from app.explain.types import EvidencePayload
from app.explain.validation import banned_phrase, is_grounded, validate

PAYLOAD = EvidencePayload(
    entity_name="Valerie Kaur",
    action="THANK",
    evidence=[
        "$25,000 gift on Feb 4, 2026",
        "No stewardship interaction is recorded since the gift",
    ],
    facts={"channel_hint": "email"},
)


def test_grounded_text_passes():
    text = "Valerie Kaur gave $25,000 on Feb 4, 2026 and has no recorded stewardship since."
    assert is_grounded(text, PAYLOAD)
    assert validate(text, PAYLOAD)


def test_fabricated_number_is_rejected():
    text = "Valerie Kaur gave $50,000 on Feb 4, 2026."
    assert not is_grounded(text, PAYLOAD)
    assert not validate(text, PAYLOAD)


def test_fabricated_date_number_is_rejected():
    text = "Valerie Kaur gave $25,000 on Feb 9, 2026."
    assert not is_grounded(text, PAYLOAD)


def test_banned_phrase_never_thanked_is_rejected():
    text = "Valerie Kaur was never thanked for her $25,000 gift."
    assert banned_phrase(text) == "never thanked"
    assert not validate(text, PAYLOAD)


def test_banned_phrase_influential_is_rejected():
    text = "Valerie Kaur is an influential donor."
    assert banned_phrase(text) == "influential"
    assert not validate(text, PAYLOAD)


def test_banned_phrase_friends_with_is_rejected():
    text = "Valerie Kaur is friends with the dean."
    assert banned_phrase(text) == "friends with"
    assert not validate(text, PAYLOAD)


def test_wealth_inference_is_rejected():
    text = "Valerie Kaur's recent promotion suggests wealth."
    assert banned_phrase(text) == "suggests wealth"
    assert not validate(text, PAYLOAD)


def test_missing_data_described_as_missing_is_grounded():
    text = "No stewardship interaction is recorded for Valerie Kaur since her $25,000 gift."
    assert validate(text, PAYLOAD)


def test_empty_text_is_invalid():
    assert not validate("", PAYLOAD)
    assert not validate("   ", PAYLOAD)
