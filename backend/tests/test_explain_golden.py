"""Golden-file coverage for the demo cast members whose detectors have
merged (CLAUDE.md's demo cast table). No API key is configured in this
environment, so these exercise the guaranteed-safe template path -- the
point is that the payload built from a *real* Signal renders a grounded,
compliant explanation.
"""

import pytest

from app.explain import cache as cache_module
from app.explain.service import explain
from app.explain.types import EvidencePayload
from app.explain.validation import validate
from app.signals import contact_pressure, stewardship_gap
from app.signals import broken_commitment


@pytest.fixture(autouse=True)
def clear_cache():
    cache_module.clear()
    yield
    cache_module.clear()


def _payload_for(signal):
    return EvidencePayload(
        entity_name=signal.entity_name,
        action=signal.action,
        evidence=signal.evidence,
        facts={
            k: v
            for k, v in {
                "channel_hint": signal.channel_hint,
                "assigned_officer": signal.assigned_officer,
            }.items()
            if v is not None
        },
    )


def test_valerie_kaur_thank_golden(context):
    signal = next(s for s in stewardship_gap.detect(context) if s.entity_id == 2669)

    result = explain(_payload_for(signal), client=None)

    assert result.source == "template"
    assert result.text == (
        "Sam recommends a thank-you for Valerie Kaur: $25,000 gift on Feb 4, 2026; "
        "No stewardship interaction is recorded since the gift."
    )
    assert validate(result.text, _payload_for(signal))


def test_kieran_kaur_wait_golden(context):
    signal = next(s for s in contact_pressure.detect(context) if s.entity_id == 12022)

    result = explain(_payload_for(signal), client=None)

    assert result.source == "template"
    assert result.text == (
        "Sam recommends waiting before reaching out to Kieran Kaur: "
        "5 outbound interactions in the last 60 days; Most recent: Aug 19, 2026."
    )
    assert validate(result.text, _payload_for(signal))


def test_nia_chen_follow_up_golden(context):
    signal = next(s for s in broken_commitment.detect(context) if s.entity_id == 14456)

    result = explain(_payload_for(signal), client=None)

    assert result.source == "template"
    assert result.text == (
        "Sam recommends following up with Nia Chen: Follow-up was due May 1, 2026; "
        "No subsequent follow-up is recorded; No response on a Mar 15, 2026 solicitation call."
    )
    assert validate(result.text, _payload_for(signal))
