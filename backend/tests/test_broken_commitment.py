from datetime import timedelta

import pandas as pd

from app.config import AS_OF_DATE
from app.signals import broken_commitment


def _interaction(id_, constituent_id, occurred_at, follow_up_date=None, **overrides):
    row = {
        "id": id_,
        "constituent_id": constituent_id,
        "occurred_at": f"{occurred_at}T12:00:00Z",
        "interaction_type": "call",
        "direction": "outbound",
        "purpose": "solicitation",
        "outcome": "no_response",
        "follow_up_date": follow_up_date,
        "significant": 0,
        "subject": "",
        "notes": "",
    }
    row.update(overrides)
    return row


def test_interaction_on_the_follow_up_date_resolves_it():
    follow_up_date = AS_OF_DATE - timedelta(days=30)
    commitment_date = follow_up_date - timedelta(days=45)
    interactions = pd.DataFrame(
        [
            _interaction(1, 1, commitment_date.isoformat(), follow_up_date=follow_up_date.isoformat()),
            _interaction(2, 1, follow_up_date.isoformat()),
        ]
    )

    due = broken_commitment.compute_due_commitments(interactions)

    assert len(due) == 1
    assert due[0]["resolved"] is True
    assert due[0]["resolved_by_interaction_id"] == 2


def test_interaction_the_day_before_does_not_resolve_it():
    follow_up_date = AS_OF_DATE - timedelta(days=30)
    commitment_date = follow_up_date - timedelta(days=45)
    day_before = follow_up_date - timedelta(days=1)
    interactions = pd.DataFrame(
        [
            _interaction(1, 1, commitment_date.isoformat(), follow_up_date=follow_up_date.isoformat()),
            _interaction(2, 1, day_before.isoformat()),
        ]
    )

    due = broken_commitment.compute_due_commitments(interactions)

    assert len(due) == 1
    assert due[0]["resolved"] is False
    assert due[0]["resolved_by_interaction_id"] is None


def test_follow_up_date_after_as_of_date_is_not_due():
    upcoming = AS_OF_DATE + timedelta(days=1)
    interactions = pd.DataFrame(
        [_interaction(1, 1, (upcoming - timedelta(days=10)).isoformat(), follow_up_date=upcoming.isoformat())]
    )

    due = broken_commitment.compute_due_commitments(interactions)

    assert due == []


def test_explicit_completed_or_cancelled_hook_always_reports_unavailable():
    row = pd.Series({"id": 1, "constituent_id": 1})

    assert broken_commitment.is_explicitly_completed_or_cancelled(row) is False
    assert "not available in this dataset" in broken_commitment.EXPLICIT_RESOLUTION_NOTE


def test_matches_appendix_b_40_due_39_resolved_1_unresolved(interactions):
    due = broken_commitment.compute_due_commitments(interactions)

    assert len(due) == 40
    resolved = [row for row in due if row["resolved"]]
    unresolved = [row for row in due if not row["resolved"]]
    assert len(resolved) == 39
    assert len(unresolved) == 1
    assert unresolved[0]["constituent_id"] == 14456


def test_nia_chen_surfaces_as_follow_up_with_expected_evidence(constituents, interactions, staff):
    signals = broken_commitment.detect(constituents, interactions, staff)

    assert len(signals) == 1
    nia = signals[0]
    assert nia.entity_id == 14456
    assert nia.action == "FOLLOW UP"
    assert nia.evidence == [
        "Follow-up was due May 1, 2026",
        "No subsequent follow-up is recorded",
        "No response on a Mar 15, 2026 solicitation call",
    ]
    assert nia.assigned_officer == "Morgan Ellis"
    assert nia.channel_hint == "phone"


def test_nia_chen_channel_note_explains_inactive_email(constituents, interactions, staff):
    due = broken_commitment.compute_due_commitments(interactions)
    nia_row = next(r for r in due if r["constituent_id"] == 14456)
    from app.normalize import population

    constituent = population(constituents).set_index("id", drop=False).loc[14456]

    _, note = broken_commitment.build_signal_and_channel_note(nia_row, constituent, "Morgan Ellis")

    assert note == "Email status is inactive; phone is the allowed channel"


def test_isaac_chen_does_not_surface_as_follow_up(constituents, interactions, staff):
    signals = broken_commitment.detect(constituents, interactions, staff)

    assert all(s.entity_id != 2548 for s in signals)


def test_no_evidence_says_broken_or_missed(constituents, interactions, staff):
    signals = broken_commitment.detect(constituents, interactions, staff)

    forbidden = ("broken", "missed")
    for signal in signals:
        for line in signal.evidence:
            lowered = line.lower()
            for word in forbidden:
                assert word not in lowered
