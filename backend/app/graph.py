"""Builds the institutional relationship graph (PRD Section 6) with
NetworkX.

Node types: Constituent, Activity, Affiliation, Major, Class Year,
Event, Employer, Fund, Campaign. Edge types: participated_in,
affiliated_with, studied, graduated_in, attended, works_at,
donated_to, donated_via.

A MultiDiGraph is used, not a plain Graph, so two source rows between
the same pair of nodes (e.g. two gifts to the same fund) become two
distinct edges -- node and edge counts must match the source CSV row
counts (issue 009's first acceptance criterion), which a deduping
Graph would silently violate.

An edge is an observed institutional relationship or shared context,
not a direct social relationship between two constituents (PRD
Section 6, G5): Sam never infers friendship or influence from it.
"""

import networkx as nx
import pandas as pd

from app.db import load_table


def activity_node(name: str) -> str:
    return f"activity:{name}"


def _affiliation_node(value: str) -> str:
    return f"affiliation:{value}"


def _major_node(name: str) -> str:
    return f"major:{name}"


def _class_year_node(year: int) -> str:
    return f"class_year:{year}"


def _employer_node(name: str) -> str:
    return f"employer:{name}"


def _constituent_node(entity_id: int) -> str:
    return f"constituent:{entity_id}"


def _event_node(entity_id: int) -> str:
    return f"event:{entity_id}"


def _fund_node(entity_id: int) -> str:
    return f"fund:{entity_id}"


def _campaign_node(entity_id: int) -> str:
    return f"campaign:{entity_id}"


def build_graph() -> nx.MultiDiGraph:
    constituents = load_table("constituents")
    activities = load_table("activities")
    affiliations = load_table("affiliations")
    degrees = load_table("degrees")
    events = load_table("events")
    event_attendance = load_table("event_attendance")
    career_history = load_table("career_history")
    funds = load_table("funds")
    campaigns = load_table("campaigns")
    gifts = load_table("gifts")
    gift_allocations = load_table("gift_allocations")

    graph = nx.MultiDiGraph()

    for _, row in constituents.iterrows():
        graph.add_node(
            _constituent_node(row["id"]),
            type="constituent",
            entity_id=int(row["id"]),
            name=row["preferred_name"],
            entity_type=row["entity_type"],
            deceased=bool(row["deceased"]),
            assigned_staff_id=row["assigned_staff_id"],
        )

    for name in activities["activity_name"].unique():
        graph.add_node(activity_node(name), type="activity", name=name)
    for _, row in activities.iterrows():
        graph.add_edge(
            _constituent_node(row["constituent_id"]),
            activity_node(row["activity_name"]),
            type="participated_in",
        )

    for value in affiliations["raw_affiliation_value"].unique():
        graph.add_node(_affiliation_node(value), type="affiliation", name=value)
    for _, row in affiliations.iterrows():
        graph.add_edge(
            _constituent_node(row["constituent_id"]),
            _affiliation_node(row["raw_affiliation_value"]),
            type="affiliated_with",
        )

    degrees_with_major = degrees.dropna(subset=["major"])
    for major in degrees_with_major["major"].unique():
        graph.add_node(_major_node(major), type="major", name=major)
    for _, row in degrees_with_major.iterrows():
        graph.add_edge(_constituent_node(row["constituent_id"]), _major_node(row["major"]), type="studied")

    degrees_with_class_year = degrees.dropna(subset=["class_year"])
    for year in degrees_with_class_year["class_year"].unique():
        graph.add_node(_class_year_node(int(year)), type="class_year", name=int(year))
    for _, row in degrees_with_class_year.iterrows():
        graph.add_edge(
            _constituent_node(row["constituent_id"]),
            _class_year_node(int(row["class_year"])),
            type="graduated_in",
        )

    for _, row in events.iterrows():
        graph.add_node(_event_node(row["id"]), type="event", entity_id=int(row["id"]), name=row["name"])
    for _, row in event_attendance.iterrows():
        graph.add_edge(_constituent_node(row["constituent_id"]), _event_node(row["event_id"]), type="attended")

    for employer in career_history["employer"].unique():
        graph.add_node(_employer_node(employer), type="employer", name=employer)
    for _, row in career_history.iterrows():
        graph.add_edge(_constituent_node(row["constituent_id"]), _employer_node(row["employer"]), type="works_at")

    for _, row in funds.iterrows():
        graph.add_node(_fund_node(row["id"]), type="fund", entity_id=int(row["id"]), name=row["name"])
    for _, row in campaigns.iterrows():
        graph.add_node(_campaign_node(row["id"]), type="campaign", entity_id=int(row["id"]), name=row["name"])

    gifts_by_id = gifts.set_index("id")
    for _, row in gift_allocations.iterrows():
        if pd.isna(row["fund_id"]):
            continue
        constituent_id = gifts_by_id.loc[row["gift_id"], "constituent_id"]
        # fund_id is float64 here (the column is nullable), while the fund
        # nodes above were keyed by the funds table's int id -- cast, or
        # this silently creates a duplicate, attribute-less "fund:17.0" node.
        graph.add_edge(_constituent_node(constituent_id), _fund_node(int(row["fund_id"])), type="donated_to")

    gifts_with_campaign = gifts.dropna(subset=["campaign_id"])
    for _, row in gifts_with_campaign.iterrows():
        graph.add_edge(
            _constituent_node(row["constituent_id"]), _campaign_node(int(row["campaign_id"])), type="donated_via"
        )

    return graph


_GRAPH_CACHE: nx.MultiDiGraph | None = None


def get_graph(force_rebuild: bool = False) -> nx.MultiDiGraph:
    """The cached graph, built once per process (issue 009: "build once
    at startup and cache it"). `force_rebuild` exists for tests only.
    """
    global _GRAPH_CACHE
    if _GRAPH_CACHE is None or force_rebuild:
        _GRAPH_CACHE = build_graph()
    return _GRAPH_CACHE


def edge_count_by_type(graph: nx.MultiDiGraph) -> dict[str, int]:
    counts: dict[str, int] = {}
    for _, _, data in graph.edges(data=True):
        edge_type = data["type"]
        counts[edge_type] = counts.get(edge_type, 0) + 1
    return counts


def node_count_by_type(graph: nx.MultiDiGraph) -> dict[str, int]:
    counts: dict[str, int] = {}
    for _, data in graph.nodes(data=True):
        node_type = data["type"]
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts
