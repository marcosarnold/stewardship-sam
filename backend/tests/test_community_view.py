from app.community_view import build_community_view
from app.db import load_table
from app.graph import get_graph
from app.signals.community_cooling import detect


def test_alumni_board_view(context, event_attendance):
    graph = get_graph()
    cooling_signals = detect(context)

    view = build_community_view(graph, "alumni-board", context, event_attendance, cooling_signals)

    assert view["name"] == "Alumni Board"
    assert view["member_count"] == 180
    assert view["recommended_action"] in ("RECONNECT", "INVITE", "ADVOCATE")
    assert view["why_surfaced"]
    assert "descriptive, not causal" in view["wording_note"]


def test_explore_members_have_signal_counts_and_are_sorted(context, event_attendance):
    graph = get_graph()
    cooling_signals = detect(context)

    view = build_community_view(graph, "alumni-board", context, event_attendance, cooling_signals)

    assert len(view["explore_members"]) == 180
    counts = [m["signal_count"] for m in view["explore_members"]]
    assert counts == sorted(counts, reverse=True)
    for m in view["explore_members"]:
        assert "entity_id" in m and "entity_name" in m


def test_unknown_community_returns_none(context, event_attendance):
    graph = get_graph()
    view = build_community_view(graph, "not-a-real-community", context, event_attendance, [])

    assert view is None
