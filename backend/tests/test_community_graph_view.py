import time

from app.community_graph_view import build_community_graph
from app.config import COMMUNITY_GRAPH_MAX_NODES
from app.graph import get_graph


def test_alumni_board_graph_renders_under_2_seconds(context):
    graph = get_graph()
    started = time.monotonic()
    result = build_community_graph(graph, "alumni-board", context)
    elapsed = time.monotonic() - started

    assert elapsed < 2
    assert result["name"] == "Alumni Board"


def test_node_cap_and_omitted_count(context):
    graph = get_graph()
    result = build_community_graph(graph, "alumni-board", context)

    person_nodes = [n for n in result["nodes"] if n["type"] == "person"]
    assert len(person_nodes) <= COMMUNITY_GRAPH_MAX_NODES
    assert result["omitted_count"] == 180 - len(person_nodes)


def test_connectors_are_flagged_with_basis(context):
    graph = get_graph()
    result = build_community_graph(graph, "alumni-board", context)

    connectors = [n for n in result["nodes"] if n["type"] == "person" and n["is_connector"]]
    assert len(connectors) > 0
    for c in connectors:
        assert c["basis"]


def test_bridge_communities_link_to_their_own_community_id(context):
    graph = get_graph()
    result = build_community_graph(graph, "alumni-board", context)

    bridges = [n for n in result["nodes"] if n["type"] == "community" and not n["is_center"]]
    assert len(bridges) > 0
    for b in bridges:
        assert b["community_id"] is not None


def test_unknown_community_returns_none(context):
    graph = get_graph()
    assert build_community_graph(graph, "not-a-real-community", context) is None
