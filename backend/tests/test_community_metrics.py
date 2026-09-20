import time
from datetime import date, timedelta

import networkx as nx
import pandas as pd
import pytest

from app.communities import find_community, list_communities
from app.community_metrics import compute_all_metrics, compute_community_metrics
from app.config import AS_OF_DATE
from app.graph import activity_node, build_graph, get_graph


def _synthetic_graph(members: list[dict]) -> nx.MultiDiGraph:
    """members: [{"id": int, "assigned_staff_id": int | None}, ...],
    all in the "Test Club" activity.
    """
    graph = nx.MultiDiGraph()
    graph.add_node(activity_node("Test Club"), type="activity", name="Test Club")
    for m in members:
        node = f"constituent:{m['id']}"
        graph.add_node(
            node,
            type="constituent",
            entity_id=m["id"],
            name=f"Person {m['id']}",
            entity_type="individual",
            deceased=False,
            assigned_staff_id=m["assigned_staff_id"],
        )
        graph.add_edge(node, activity_node("Test Club"), type="participated_in")
    return graph


@pytest.fixture
def synthetic():
    # 4 members: 1001 gave long ago only, 1002 gave recently and is
    # stewarded, 1003 gave recently with no stewardship, 1004 never gave.
    members = [
        {"id": 1001, "assigned_staff_id": 1},
        {"id": 1002, "assigned_staff_id": 1},
        {"id": 1003, "assigned_staff_id": None},
        {"id": 1004, "assigned_staff_id": None},
    ]
    graph = _synthetic_graph(members)

    gifts = pd.DataFrame(
        [
            {"constituent_id": 1001, "gift_date": "2020-01-01", "status": "paid", "gift_type": "one_time"},
            {"constituent_id": 1002, "gift_date": (AS_OF_DATE.isoformat()), "status": "paid", "gift_type": "one_time"},
            {"constituent_id": 1003, "gift_date": (AS_OF_DATE.isoformat()), "status": "paid", "gift_type": "one_time"},
            # Outside the recent window by one day -- boundary check.
            {
                "constituent_id": 1001,
                "gift_date": (AS_OF_DATE - timedelta(days=366)).isoformat(),
                "status": "paid",
                "gift_type": "one_time",
            },
        ]
    )

    interactions = pd.DataFrame(
        [
            {
                "constituent_id": 1002,
                "occurred_at": AS_OF_DATE.isoformat() + "T00:00:00Z",
                "purpose": "stewardship",
            },
            {
                "constituent_id": 1001,
                "occurred_at": (AS_OF_DATE - timedelta(days=730)).isoformat() + "T00:00:00Z",
                "purpose": "solicitation",
            },
            # One day outside the recent-engagement window -- boundary check.
            {
                "constituent_id": 1004,
                "occurred_at": (AS_OF_DATE - timedelta(days=731)).isoformat() + "T00:00:00Z",
                "purpose": "solicitation",
            },
        ]
    )

    event_attendance = pd.DataFrame(
        [
            {
                "constituent_id": 1001,
                "attended_at": (AS_OF_DATE - timedelta(days=800)).isoformat() + "T00:00:00Z",
            },
            {
                "constituent_id": 1002,
                "attended_at": AS_OF_DATE.isoformat() + "T00:00:00Z",
            },
        ]
    )

    staff = pd.DataFrame([{"id": 1, "display_name": "Officer One", "active": 1}])

    return graph, gifts, interactions, event_attendance, staff


def test_definitions_on_a_synthetic_dataset(synthetic):
    graph, gifts, interactions, event_attendance, staff = synthetic

    metrics = compute_community_metrics(graph, "Test Club", gifts, interactions, event_attendance, staff)

    assert metrics["member_count"] == 4
    # 1001, 1002, 1003 ever gave -> 3/4.
    assert metrics["historical_giving_rate"] == 0.75
    # 1002, 1003 gave within the window -> 2/4. 1001's 366-day-old gift is
    # outside RECENT_GIVING_WINDOW_DAYS=365, the boundary case.
    assert metrics["recent_giving_rate"] == 0.5
    assert metrics["recent_to_historical_ratio"] == round(0.5 / 0.75, 4)
    # Only 1002's interaction (on AS_OF_DATE) is within the 730-day window;
    # 1001's is exactly 730 days back (included); 1004's is 731 (excluded).
    assert metrics["recent_interaction_rate"] == 0.5
    # 1001 and 1002 ever attended -> 2/4.
    assert metrics["historical_event_participation"] == 0.5
    # Only 1002's attendance is within the recent-engagement window.
    assert metrics["recent_event_participation"] == 0.25
    # Of the 2 recent donors (1002, 1003), only 1002 has a stewardship
    # interaction on/after their gift date -> 1/2.
    assert metrics["stewardship_coverage"] == 0.5
    # Only 1001 and 1002 have an active assigned officer -> 2/4.
    assert metrics["assignment_coverage"] == 0.5


def test_alumni_board_matches_appendix_b(context, event_attendance, staff):
    graph = build_graph()
    metrics = compute_community_metrics(graph, "Alumni Board", context.gifts, context.interactions, event_attendance, staff)

    assert round(metrics["historical_giving_rate"] * 100, 1) == pytest.approx(58.9, abs=0.5)
    assert round(metrics["recent_giving_rate"] * 100, 1) == pytest.approx(8.9, abs=0.5)
    assert round(metrics["recent_interaction_rate"] * 100, 1) == pytest.approx(20.6, abs=0.5)


def test_event_data_caveat_is_present(synthetic):
    graph, gifts, interactions, event_attendance, staff = synthetic
    metrics = compute_community_metrics(graph, "Test Club", gifts, interactions, event_attendance, staff)

    assert "September 2025" in metrics["event_data_caveat"]
    assert "June 2026" in metrics["event_data_caveat"]


def test_all_79_communities_compute_under_5_seconds_and_are_cached(context, event_attendance, staff):
    graph = get_graph()

    started = time.monotonic()
    first = compute_all_metrics(graph, context.gifts, context.interactions, event_attendance, staff, force_rebuild=True)
    elapsed = time.monotonic() - started
    assert elapsed < 5

    communities = list_communities(graph)
    assert len(first) == len(communities)

    second = compute_all_metrics(graph, context.gifts, context.interactions, event_attendance, staff)
    assert first is second
