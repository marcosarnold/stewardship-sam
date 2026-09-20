from app.explain.templates import render_template
from app.explain.types import EvidencePayload


def test_thank_template_grounded():
    payload = EvidencePayload(
        entity_name="Valerie Kaur",
        action="THANK",
        evidence=[
            "$25,000 gift on Feb 4, 2026",
            "No stewardship interaction is recorded since the gift",
        ],
    )

    text = render_template(payload)

    assert "Valerie Kaur" in text
    assert "$25,000 gift on Feb 4, 2026" in text
    assert "No stewardship interaction is recorded since the gift" in text


def test_wait_template_uses_wait_lead():
    payload = EvidencePayload(
        entity_name="Kieran Kaur",
        action="WAIT",
        evidence=["5 outbound interactions in the last 60 days"],
    )

    text = render_template(payload)

    assert text.startswith("Sam recommends waiting before reaching out to Kieran Kaur")


def test_no_evidence_still_produces_a_sentence():
    payload = EvidencePayload(entity_name="Isaac Chen", action="ASSIGN", evidence=[])

    text = render_template(payload)

    assert "Isaac Chen" in text
    assert text.endswith(".")


def test_unknown_action_has_a_generic_lead():
    payload = EvidencePayload(entity_name="Someone", action="MYSTERY", evidence=["a fact"])

    text = render_template(payload)

    assert "MYSTERY" in text
    assert "Someone" in text
