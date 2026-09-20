from app.signals import neglected_relationship


def test_matches_appendix_b_116_candidates_101_assign_15_reconnect(
    constituents, gifts, interactions, staff, opportunities
):
    today_items, held_back = neglected_relationship.detect(
        constituents, gifts, interactions, staff, opportunities
    )

    all_items = today_items + [
        item for item in held_back  # RECONNECT candidates suppressed by contact policy, if any
    ]
    assign_count = sum(1 for s in today_items if s.action == "ASSIGN")
    reconnect_count = sum(1 for s in today_items if s.action == "RECONNECT") + len(held_back)

    assert assign_count == 101
    assert reconnect_count == 15
    assert assign_count + reconnect_count == 116


def test_assign_states_no_fundraiser_assigned(constituents, gifts, interactions, staff, opportunities):
    today_items, _ = neglected_relationship.detect(constituents, gifts, interactions, staff, opportunities)

    assign_items = [s for s in today_items if s.action == "ASSIGN"]
    assert assign_items
    for signal in assign_items:
        assert signal.assigned_officer is None
        assert "No fundraiser is assigned" in signal.evidence


def test_reconnect_names_assigned_officer(constituents, gifts, interactions, staff, opportunities):
    today_items, held_back = neglected_relationship.detect(
        constituents, gifts, interactions, staff, opportunities
    )

    reconnect_items = [s for s in today_items if s.action == "RECONNECT"]
    assert reconnect_items or held_back
    for signal in reconnect_items:
        assert signal.assigned_officer is not None
        assert any(signal.assigned_officer in line for line in signal.evidence)


def test_signal_never_returns_ask(constituents, gifts, interactions, staff, opportunities):
    today_items, held_back = neglected_relationship.detect(
        constituents, gifts, interactions, staff, opportunities
    )

    assert all(s.action != "ASK" for s in today_items)
    assert all(item["action"] != "ASK" for item in held_back)


def test_no_interaction_ever_says_no_interaction_is_recorded(
    constituents, gifts, interactions, staff, opportunities
):
    today_items, _ = neglected_relationship.detect(constituents, gifts, interactions, staff, opportunities)

    micah = next(s for s in today_items if s.entity_id == 42)
    assert "No interaction is recorded" in micah.evidence
    assert not any("never" in line.lower() for line in micah.evidence)


def test_will_khan_reconnect_with_stale_interaction_date_and_opportunity_count(
    constituents, gifts, interactions, staff, opportunities
):
    today_items, _ = neglected_relationship.detect(constituents, gifts, interactions, staff, opportunities)

    will = next(s for s in today_items if s.entity_id == 14876)
    assert will.action == "RECONNECT"
    assert will.assigned_officer == "Morgan Ellis"
    assert "$16,200 lifetime giving" in will.evidence
    assert "Last interaction recorded Jun 25, 2024" in will.evidence
    assert "1 related opportunity" in will.evidence


def test_do_not_solicit_still_gets_assign_with_policy_note(
    constituents, gifts, interactions, staff, opportunities
):
    today_items, _ = neglected_relationship.detect(constituents, gifts, interactions, staff, opportunities)

    micah = next(s for s in today_items if s.entity_id == 42)
    assert micah.action == "ASSIGN"
    assert any("do-not-solicit" in line.lower() for line in micah.evidence)


def test_thresholds_come_from_config():
    import inspect

    source = inspect.getsource(neglected_relationship)
    assert "10000" not in source
    assert "730" not in source
