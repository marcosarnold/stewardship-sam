"""Builds GET /api/community/:id/graph (UX3 visualization data).

Selects up to COMMUNITY_GRAPH_MAX_NODES member nodes, prioritizing
connectors (issue 012) and members with attention signals (issue 011),
plus the eligible "bridge" communities those shown members also
belong to. Everyone else is summarized as a single omitted count so
the graph stays readable and fast (Section 11: a decision aid, not a
decorative homepage graph).
"""

import networkx as nx

from app.communities import find_community, list_communities, members
from app.config import COMMUNITY_GRAPH_MAX_NODES
from app.connectors import compute_connectors
from app.context import Context
from app.priority_queue import evaluate_signals


def build_community_graph(graph: nx.MultiDiGraph, community_id: str, context: Context) -> dict | None:
    community = find_community(graph, community_id)
    if community is None:
        return None

    connectors = compute_connectors(graph, community_id, context) or []
    connector_by_id = {c["entity_id"]: c for c in connectors}
    id_by_name = {c["name"]: c["id"] for c in list_communities(graph)}

    member_rows = members(graph, community["name"])
    member_ids = {m["entity_id"] for m in member_rows}

    shown, _held_back = evaluate_signals(context)
    signal_counts: dict[int, int] = {}
    for s in shown:
        if s.entity_id in member_ids:
            signal_counts[s.entity_id] = signal_counts.get(s.entity_id, 0) + 1

    def priority(m: dict) -> tuple:
        connector = connector_by_id.get(m["entity_id"])
        overlap = connector["overlap_count"] if connector else 0
        signals = signal_counts.get(m["entity_id"], 0)
        return (-overlap, -signals, m["entity_name"])

    ranked = sorted(member_rows, key=priority)
    shown_members = ranked[:COMMUNITY_GRAPH_MAX_NODES]
    omitted_count = max(0, len(ranked) - len(shown_members))

    bridge_names: set[str] = set()
    edges = []
    nodes = [{"id": community_id, "type": "community", "name": community["name"], "is_center": True}]

    for m in shown_members:
        connector = connector_by_id.get(m["entity_id"])
        is_connector = bool(connector and connector["overlap_count"] > 0)
        nodes.append(
            {
                "id": f"person:{m['entity_id']}",
                "type": "person",
                "entity_id": m["entity_id"],
                "name": m["entity_name"],
                "is_connector": is_connector,
                "signal_count": signal_counts.get(m["entity_id"], 0),
                "basis": connector["basis"] if connector else None,
                "policy_status": connector["policy_status"] if connector else None,
            }
        )
        edges.append({"source": f"person:{m['entity_id']}", "target": community_id, "type": "member_of"})

        if connector:
            for other_name in connector["communities_spanned"]:
                bridge_names.add(other_name)

    for name in sorted(bridge_names):
        nodes.append(
            {
                "id": f"bridge:{name}",
                "type": "community",
                "name": name,
                "is_center": False,
                "community_id": id_by_name.get(name),
            }
        )

    # Edges from each connector to the bridge communities they span.
    for m in shown_members:
        connector = connector_by_id.get(m["entity_id"])
        if not connector:
            continue
        for other_name in connector["communities_spanned"]:
            edges.append({"source": f"person:{m['entity_id']}", "target": f"bridge:{other_name}", "type": "member_of"})

    return {
        "id": community_id,
        "name": community["name"],
        "nodes": nodes,
        "edges": edges,
        "omitted_count": omitted_count,
        "node_cap": COMMUNITY_GRAPH_MAX_NODES,
        "wording_note": "An edge is shared institutional context, not friendship or influence.",
    }
