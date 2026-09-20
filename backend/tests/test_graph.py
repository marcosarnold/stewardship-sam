import time

from app.db import load_table
from app.graph import build_graph, edge_count_by_type, node_count_by_type


def test_node_counts_match_source_tables():
    graph = build_graph()
    counts = node_count_by_type(graph)

    assert counts["constituent"] == len(load_table("constituents"))
    assert counts["event"] == len(load_table("events"))
    assert counts["fund"] == len(load_table("funds"))
    assert counts["campaign"] == len(load_table("campaigns"))

    activities = load_table("activities")
    assert counts["activity"] == activities["activity_name"].nunique()

    affiliations = load_table("affiliations")
    assert counts["affiliation"] == affiliations["raw_affiliation_value"].nunique()

    degrees = load_table("degrees")
    assert counts["major"] == degrees["major"].dropna().nunique()
    assert counts["class_year"] == degrees["class_year"].dropna().nunique()

    career_history = load_table("career_history")
    assert counts["employer"] == career_history["employer"].nunique()


def test_edge_counts_match_source_row_counts():
    graph = build_graph()
    counts = edge_count_by_type(graph)

    assert counts["participated_in"] == len(load_table("activities"))
    assert counts["affiliated_with"] == len(load_table("affiliations"))
    assert counts["attended"] == len(load_table("event_attendance"))
    assert counts["works_at"] == len(load_table("career_history"))
    # One gift_allocations row has no fund_id -- no edge is fabricated for it.
    assert counts["donated_to"] == load_table("gift_allocations")["fund_id"].notna().sum()

    degrees = load_table("degrees")
    assert counts["studied"] == degrees["major"].notna().sum()
    assert counts["graduated_in"] == degrees["class_year"].notna().sum()

    gifts = load_table("gifts")
    assert counts["donated_via"] == gifts["campaign_id"].notna().sum()


def test_graph_builds_cold_in_under_30_seconds():
    started = time.monotonic()
    build_graph()
    assert time.monotonic() - started < 30


def test_get_graph_caches_between_calls():
    from app.graph import get_graph

    first = get_graph(force_rebuild=True)
    second = get_graph()

    assert first is second
