from app.followups import build_followups


def test_default_excludes_resolved(constituents, interactions, staff):
    result = build_followups(constituents, interactions, staff, include_resolved=False)

    assert len(result["commitments"]) == 1
    assert result["commitments"][0]["entity_id"] == 14456
    assert result["commitments"][0]["resolved"] is False


def test_include_resolved_lists_all_40(constituents, interactions, staff):
    result = build_followups(constituents, interactions, staff, include_resolved=True)

    assert len(result["commitments"]) == 40
    resolved = [c for c in result["commitments"] if c["resolved"]]
    assert len(resolved) == 39


def test_isaac_chen_shown_resolved_by_may_15_meeting(constituents, interactions, staff):
    result = build_followups(constituents, interactions, staff, include_resolved=True)

    isaac = next(c for c in result["commitments"] if c["entity_id"] == 2548)

    assert isaac["resolved"] is True
    assert isaac["follow_up_date"] == "2026-05-15"
    assert isaac["resolved_at"] == "2026-05-15"
    assert isaac["action"] is None
    assert isaac["evidence"] == []


def test_isaac_chens_upcoming_follow_up_is_not_listed_as_due(constituents, interactions, staff):
    result = build_followups(constituents, interactions, staff, include_resolved=True)

    isaac_entries = [c for c in result["commitments"] if c["entity_id"] == 2548]

    assert all(c["follow_up_date"] != "2026-12-01" for c in isaac_entries)


def test_nia_chen_entry_has_officer_and_channel(constituents, interactions, staff):
    result = build_followups(constituents, interactions, staff, include_resolved=False)

    nia = result["commitments"][0]

    assert nia["assigned_officer"] == "Morgan Ellis"
    assert nia["channel_hint"] == "phone"
    assert nia["channel_note"] == "Email status is inactive; phone is the allowed channel"


def test_explicit_resolution_note_present(constituents, interactions, staff):
    result = build_followups(constituents, interactions, staff, include_resolved=True)

    assert "not available in this dataset" in result["explicit_resolution_note"]
