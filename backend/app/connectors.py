"""Connector analysis (PRD Section 8, G1, G5): potential connectors for
a community from observed membership overlap.

For a target community's members, this builds the person<->eligible-
community bipartite subgraph restricted to those members and whatever
other eligible communities they also belong to, then reports, per
member: how many *other* eligible communities they span, their degree
centrality and betweenness centrality within the person-person
projection of that subgraph, and which communities they span (for the
basis text).

Centrality is computed on the projection restricted to this
community's members, not the whole institution -- a person-to-person
graph across all ~9,000 members of all 79 eligible communities would
be far too large to run betweenness centrality on within the 5-second
budget. This is a documented MVP simplification, not the frozen SIG6
data model.

Overlap is shared institutional context, not friendship or influence
(G5): a connector's basis text says "Spans N relevant institutional
communities: A, B, C", never that a person is "influential" or
"friends with" anyone.
"""

import networkx as nx
import pandas as pd

from app.channel_resolution import resolve_channel
from app.communities import find_community, list_communities, members
from app.context import Context
from app.interaction_facts import outbound_dates_by_constituent, scheduled_future_interaction_ids

RESTRICTED_REASON_CODES = frozenset({"deceased", "do_not_solicit"})

_CACHE: dict[str, list[dict]] = {}


def _policy_status(entity_id: int, pop: pd.DataFrame, outbound_dates: dict, scheduled_ids: set) -> tuple[str, str | None]:
    row = pop.loc[entity_id]
    facts = {
        "deceased": bool(row["deceased"]),
        "do_not_solicit": bool(row["do_not_solicit"]),
        "phone_status": row["phone_status"],
        "email_status": row["email_status"],
        "outbound_dates": outbound_dates.get(entity_id, []),
        "has_scheduled_future_interaction": entity_id in scheduled_ids,
    }
    # RECONNECT is the community-cooling default action (SIG6); used here
    # only to get a representative policy read, not a specific recommendation.
    decision, _rejected = resolve_channel(facts, "RECONNECT")
    if decision.reason_code in RESTRICTED_REASON_CODES:
        return "restricted", decision.reason
    if decision.status != "allowed":
        return "suppressed", decision.reason
    return "allowed", None


def _member_communities(graph: nx.MultiDiGraph, entity_id: int, eligible_names: set[str]) -> list[str]:
    node = f"constituent:{entity_id}"
    names = []
    for _, target, data in graph.out_edges(node, data=True):
        if data["type"] != "participated_in":
            continue
        name = graph.nodes[target]["name"]
        if name in eligible_names:
            names.append(name)
    return sorted(names)


def _basis_text(other_communities: list[str]) -> str:
    if not other_communities:
        return "Belongs to no other eligible community."
    return f"Spans {len(other_communities)} relevant institutional communities: {', '.join(other_communities)}"


def compute_connectors(graph: nx.MultiDiGraph, community_id: str, context: Context, force_rebuild: bool = False) -> list[dict] | None:
    if not force_rebuild and community_id in _CACHE:
        return _CACHE[community_id]

    community = find_community(graph, community_id)
    if community is None:
        return None

    eligible_names = {c["name"] for c in list_communities(graph) if c["eligible"]}
    member_rows = members(graph, community["name"])
    member_ids = [m["entity_id"] for m in member_rows]
    names_by_id = {m["entity_id"]: m["entity_name"] for m in member_rows}

    bipartite = nx.Graph()
    person_nodes = [("person", pid) for pid in member_ids]
    bipartite.add_nodes_from(person_nodes, bipartite=0)
    member_communities: dict[int, list[str]] = {}
    for pid in member_ids:
        spans = _member_communities(graph, pid, eligible_names)
        member_communities[pid] = spans
        for name in spans:
            bipartite.add_node(("community", name), bipartite=1)
            bipartite.add_edge(("person", pid), ("community", name))

    if len(person_nodes) > 1:
        projected = nx.bipartite.projected_graph(bipartite, person_nodes)
    else:
        projected = nx.Graph()
        projected.add_nodes_from(person_nodes)

    degree_centrality = nx.degree_centrality(projected) if len(projected) > 1 else {n: 0.0 for n in projected}
    betweenness = nx.betweenness_centrality(projected) if len(projected) > 2 else {n: 0.0 for n in projected}

    pop = context.constituents.set_index("id", drop=False)
    outbound_dates = outbound_dates_by_constituent(context.interactions)
    scheduled_ids = scheduled_future_interaction_ids(context.interactions)

    connectors = []
    for pid in member_ids:
        node = ("person", pid)
        spans = member_communities[pid]
        other_communities = [c for c in spans if c != community["name"]]
        status, reason = _policy_status(pid, pop, outbound_dates, scheduled_ids)
        connectors.append(
            {
                "entity_id": pid,
                "entity_name": names_by_id[pid],
                "overlap_count": len(other_communities),
                "degree_centrality": round(degree_centrality.get(node, 0.0), 4),
                "betweenness_centrality": round(betweenness.get(node, 0.0), 4),
                "communities_spanned": other_communities,
                "basis": _basis_text(other_communities),
                "policy_status": status,
                "policy_reason": reason,
            }
        )

    connectors.sort(
        key=lambda c: (-c["overlap_count"], -c["betweenness_centrality"], -c["degree_centrality"], c["entity_name"])
    )

    _CACHE[community_id] = connectors
    return connectors


def top_connectors(graph: nx.MultiDiGraph, community_id: str, context: Context, limit: int = 10) -> list[dict] | None:
    connectors = compute_connectors(graph, community_id, context)
    if connectors is None:
        return None
    return connectors[:limit]
