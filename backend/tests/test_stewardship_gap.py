from datetime import timedelta

import pandas as pd

from app.config import AS_OF_DATE, RECENT_GIFT_WINDOW_DAYS
from app.signals import stewardship_gap

FORBIDDEN_PHRASES = ("never thanked", "never contacted")


def _constituent(id_=1, **overrides):
    row = {
        "id": id_,
        "entity_type": "individual",
        "deceased": 0,
        "preferred_name": "Test Person",
        "email_status": "deliverable",
        "phone_status": "missing",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_gift_exactly_365_days_before_as_of_date_counts_as_recent():
    gift_date = AS_OF_DATE - timedelta(days=RECENT_GIFT_WINDOW_DAYS)
    constituents = _constituent()
    gifts = pd.DataFrame(
        [{"constituent_id": 1, "amount": 100, "status": "paid", "gift_type": "one_time", "gift_date": gift_date.isoformat()}]
    )
    interactions = pd.DataFrame(columns=["constituent_id", "purpose", "occurred_at"])

    signals = stewardship_gap.detect(constituents, gifts, interactions)

    assert len(signals) == 1
    assert signals[0].entity_id == 1


def test_stewardship_interaction_on_same_day_as_gift_counts_as_subsequent():
    gift_date = AS_OF_DATE - timedelta(days=30)
    constituents = _constituent()
    gifts = pd.DataFrame(
        [{"constituent_id": 1, "amount": 100, "status": "paid", "gift_type": "one_time", "gift_date": gift_date.isoformat()}]
    )
    interactions = pd.DataFrame(
        [
            {
                "constituent_id": 1,
                "purpose": "stewardship",
                "occurred_at": f"{gift_date.isoformat()}T09:00:00Z",
            }
        ]
    )

    signals = stewardship_gap.detect(constituents, gifts, interactions)

    assert signals == []


def test_gift_366_days_before_as_of_date_is_not_recent():
    gift_date = AS_OF_DATE - timedelta(days=RECENT_GIFT_WINDOW_DAYS + 1)
    constituents = _constituent()
    gifts = pd.DataFrame(
        [{"constituent_id": 1, "amount": 100, "status": "paid", "gift_type": "one_time", "gift_date": gift_date.isoformat()}]
    )
    interactions = pd.DataFrame(columns=["constituent_id", "purpose", "occurred_at"])

    signals = stewardship_gap.detect(constituents, gifts, interactions)

    assert signals == []


def test_no_evidence_text_says_a_donor_was_never_thanked(constituents, gifts, interactions):
    signals = stewardship_gap.detect(constituents, gifts, interactions)

    for signal in signals:
        for line in signal.evidence:
            lowered = line.lower()
            for phrase in FORBIDDEN_PHRASES:
                assert phrase not in lowered


def test_sig1_matches_appendix_b_count(constituents, gifts, interactions):
    signals = stewardship_gap.detect(constituents, gifts, interactions)

    assert len(signals) == 1508


def test_valerie_kaur_surfaces_as_thank_with_expected_evidence(constituents, gifts, interactions):
    signals = stewardship_gap.detect(constituents, gifts, interactions)
    by_id = {s.entity_id: s for s in signals}

    valerie = by_id[2669]

    assert valerie.action == "THANK"
    assert valerie.evidence == [
        "$25,000 gift on Feb 4, 2026",
        "No stewardship interaction is recorded since the gift",
    ]
    assert valerie.channel_hint == "email"
