from app.signals import neglected_relationship


def test_matches_appendix_b_116_candidates_101_assign_15_reconnect(context):
    signals = neglected_relationship.detect(context)

    assign_count = sum(1 for s in signals if s.action == "ASSIGN")
    reconnect_count = sum(1 for s in signals if s.action == "RECONNECT")

    assert assign_count == 101
    assert reconnect_count == 15
    assert len(signals) == 116


def test_assign_states_no_fundraiser_assigned(context):
    signals = neglected_relationship.detect(context)

    assign_items = [s for s in signals if s.action == "ASSIGN"]
    assert assign_items
    for signal in assign_items:
        assert signal.assigned_officer is None
        assert "No fundraiser is assigned" in signal.evidence


def test_reconnect_names_assigned_officer(context):
    signals = neglected_relationship.detect(context)

    reconnect_items = [s for s in signals if s.action == "RECONNECT"]
    assert reconnect_items
    for signal in reconnect_items:
        assert signal.assigned_officer is not None
        assert any(signal.assigned_officer in line for line in signal.evidence)


def test_signal_never_returns_ask(context):
    signals = neglected_relationship.detect(context)

    assert all(s.action != "ASK" for s in signals)


def test_no_interaction_ever_says_no_interaction_is_recorded(context):
    signals = neglected_relationship.detect(context)

    micah = next(s for s in signals if s.entity_id == 42)
    assert "No interaction is recorded" in micah.evidence
    assert not any("never" in line.lower() for line in micah.evidence)


def test_will_khan_reconnect_with_stale_interaction_date_and_opportunity_count(context):
    signals = neglected_relationship.detect(context)

    will = next(s for s in signals if s.entity_id == 14876)
    assert will.action == "RECONNECT"
    assert will.assigned_officer == "Morgan Ellis"
    assert "$16,200 lifetime giving" in will.evidence
    assert "Last interaction recorded Jun 25, 2024" in will.evidence
    assert "1 related opportunity" in will.evidence


def test_do_not_solicit_still_gets_assign_signal(context):
    signals = neglected_relationship.detect(context)

    micah = next(s for s in signals if s.entity_id == 42)
    assert micah.action == "ASSIGN"
    assert any("do-not-solicit" in line.lower() for line in micah.evidence)


def test_thresholds_come_from_config():
    import inspect

    source = inspect.getsource(neglected_relationship)
    assert "10000" not in source
    assert "730" not in source
