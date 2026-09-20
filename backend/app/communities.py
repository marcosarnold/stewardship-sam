"""GET /api/communities and GET /api/communities/:id/members (UX3 data layer).

A community is an activity (PRD Appendix A, SIG6 rule); it is
*eligible* once it has at least COMMUNITY_MIN_MEMBERS population
members. Membership counts and lists exclude organizations and the
deceased (PRD Appendix A population rule), read off the cached graph's
participated_in edges so the graph is the one source of truth for who
belongs where.

An edge here is shared institutional context, not friendship (G5) --
every response that names a community should be read that way.
"""

import re

import networkx as nx

from app.config import COMMUNITY_MEMBERS_PAGE_SIZE, COMMUNITY_MIN_MEMBERS
from app.graph import activity_node

EDGE_NOTE = "An edge represents shared institutional context (for example a common activity), not a direct social relationship or friendship."


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def _activity_names(graph: nx.MultiDiGraph) -> list[str]:
    return sorted(data["name"] for _, data in graph.nodes(data=True) if data["type"] == "activity")


def _members(graph: nx.MultiDiGraph, activity_name: str) -> list[dict]:
    node = activity_node(activity_name)
    if node not in graph:
        return []
    members = []
    for constituent_node in graph.predecessors(node):
        data = graph.nodes[constituent_node]
        if data["entity_type"] != "individual" or data["deceased"]:
            continue
        members.append({"entity_id": data["entity_id"], "entity_name": data["name"]})
    return sorted(members, key=lambda m: m["entity_name"])


def list_communities(graph: nx.MultiDiGraph) -> list[dict]:
    communities = []
    for name in _activity_names(graph):
        member_count = len(_members(graph, name))
        communities.append(
            {
                "id": _slug(name),
                "name": name,
                "type": "activity",
                "member_count": member_count,
                "eligible": member_count >= COMMUNITY_MIN_MEMBERS,
            }
        )
    return communities


def find_community(graph: nx.MultiDiGraph, community_id: str) -> dict | None:
    for community in list_communities(graph):
        if community["id"] == community_id:
            return community
    return None


def get_community_members(graph: nx.MultiDiGraph, community_id: str, page: int = 1) -> dict | None:
    community = find_community(graph, community_id)
    if community is None:
        return None

    all_members = _members(graph, community["name"])
    start = (page - 1) * COMMUNITY_MEMBERS_PAGE_SIZE
    page_members = all_members[start : start + COMMUNITY_MEMBERS_PAGE_SIZE]

    return {
        "community_id": community_id,
        "community_name": community["name"],
        "members": page_members,
        "page": page,
        "page_size": COMMUNITY_MEMBERS_PAGE_SIZE,
        "total": len(all_members),
        "has_more": start + COMMUNITY_MEMBERS_PAGE_SIZE < len(all_members),
        "note": EDGE_NOTE,
    }
