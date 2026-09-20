import time

import networkx as nx
import pandas as pd
import pytest

from app.connectors import compute_connectors, top_connectors
from app.context import Context
from app.graph import activity_node, get_graph


def _person_node(graph, entity_id, name, **facts):
    base = {
        "type": "constituent",
        "entity_id": entity_id,
        "name": name,
        "entity_type": "individual",
        "deceased": False,
        "do_not_solicit": False,
        "phone_status": "available",
        "email_status": "deliverable",
        "assigned_staff_id": None,
    }
    base.update(facts)
    graph.add_node(f"constituent:{entity_id}", **base)


@pytest.fixture
def small_graph():
    """A: alice, bob, carol, dave, eve. Communities: X (alice, bob, carol),
    Y (bob, carol, dave), Z (carol only). Carol spans all three -- the
    known highest-overlap, highest-centrality connector.
    """
    graph = nx.MultiDiGraph()
    people = {
        1: "Alice", 2: "Bob", 3: "Carol", 4: "Dave", 5: "Eve",
    }
    for pid, name in people.items():
        _person_node(graph, pid, name)
    # Eve is restricted (deceased won't apply here -- use do_not_solicit
    # would only matter for ASK; instead give her a WAIT-triggering
    # contact-pressure situation isn't modeled here, so mark her
    # do-not-solicit as a stand-in restricted case isn't checked by
    # RECONNECT's suppressible set -- use do_not_call + inactive email
    # instead so she reads as suppressed).
    graph.nodes["constituent:5"]["phone_status"] = "do_not_call"
    graph.nodes["constituent:5"]["email_status"] = "inactive"

    for name in ("X", "Y", "Z"):
        graph.add_node(activity_node(name), type="activity", name=name)

    for pid in (1, 2, 3):
        graph.add_edge(f"constituent:{pid}", activity_node("X"), type="participated_in")
    for pid in (2, 3, 4):
        graph.add_edge(f"constituent:{pid}", activity_node("Y"), type="participated_in")
    graph.add_edge("constituent:3", activity_node("Z"), type="participated_in")

    return graph


@pytest.fixture
def small_context():
    constituents = pd.DataFrame(
        [
            {"id": i, "deceased": False, "do_not_solicit": False, "phone_status": "available", "email_status": "deliverable"}
            for i in (1, 2, 3, 4)
        ]
        + [{"id": 5, "deceased": False, "do_not_solicit": False, "phone_status": "do_not_call", "email_status": "inactive"}]
    )
    interactions = pd.DataFrame(columns=["constituent_id", "direction", "occurred_at", "follow_up_date"])
    staff = pd.DataFrame(columns=["id", "display_name", "active"])
    opportunities = pd.DataFrame(columns=["constituent_id"])
    gifts = pd.DataFrame(columns=["constituent_id", "amount", "status", "gift_type", "gift_date"])
    return Context(constituents=constituents, gifts=gifts, interactions=interactions, staff=staff, opportunities=opportunities)


def test_known_centrality_on_a_hand_built_graph(small_graph, small_context):
    connectors = compute_connectors(small_graph, "x-community-does-not-exist", small_context)
    assert connectors is None  # sanity: unknown id returns None, not a crash

    # Patch find_community indirectly by using the real "X" via list_communities'
    # eligibility gate -- X only has 3 members, below any real threshold, so
    # call compute_connectors against a monkey-patched community lookup instead.
    from app import connectors as module

    original_find = module.find_community
    original_list = module.list_communities
    module.find_community = lambda graph, cid: {"id": "x", "name": "X", "eligible": True, "member_count": 3, "type": "activity"}
    module.list_communities = lambda graph: [
        {"id": "x", "name": "X", "eligible": True, "member_count": 3, "type": "activity"},
        {"id": "y", "name": "Y", "eligible": True, "member_count": 3, "type": "activity"},
        {"id": "z", "name": "Z", "eligible": True, "member_count": 1, "type": "activity"},
    ]
    try:
        result = module.compute_connectors(small_graph, "x", small_context, force_rebuild=True)
    finally:
        module.find_community = original_find
        module.list_communities = original_list

    by_id = {c["entity_id"]: c for c in result}
    # Carol (3) is in X, Y, and Z -- overlap of 2 others, highest centrality.
    assert by_id[3]["overlap_count"] == 2
    assert by_id[3]["communities_spanned"] == ["Y", "Z"]
    assert by_id[3]["betweenness_centrality"] >= by_id[1]["betweenness_centrality"]
    # Alice (1) is only in X -- no overlap.
    assert by_id[1]["overlap_count"] == 0
    assert by_id[1]["basis"] == "Belongs to no other eligible community."
    assert "Spans 2 relevant institutional communities: Y, Z" == by_id[3]["basis"]


def test_no_influence_or_friendship_language_anywhere(context, event_attendance):
    connectors = top_connectors(get_graph(), "alumni-board", context, limit=20)
    text = " ".join(c["basis"] + " " + (c["policy_reason"] or "") for c in connectors).lower()
    for banned in ("influential", "influence", "friend"):
        assert banned not in text


def test_each_connector_has_a_policy_status(context):
    connectors = top_connectors(get_graph(), "alumni-board", context, limit=50)
    for c in connectors:
        assert c["policy_status"] in ("allowed", "suppressed", "restricted")


def test_alumni_board_results_are_deterministic(context):
    first = top_connectors(get_graph(), "alumni-board", context, limit=10)
    second = top_connectors(get_graph(), "alumni-board", context, limit=10)
    assert first == second


def test_unknown_community_returns_none(context):
    assert top_connectors(get_graph(), "not-a-real-community", context) is None


def test_cold_analysis_under_5_seconds_and_cached(context):
    from app import connectors as module

    module._CACHE.clear()
    started = time.monotonic()
    first = compute_connectors(get_graph(), "alumni-board", context, force_rebuild=True)
    elapsed = time.monotonic() - started
    assert elapsed < 5

    second = compute_connectors(get_graph(), "alumni-board", context)
    assert first is second
