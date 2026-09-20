"""Validates an LLM explanation before it is trusted (G4, G5, G6).

Every number in the text must be traceable to the evidence payload, and
none of the banned phrasings from Appendix A's language rules may
appear. Anything that fails either check is rejected and the caller
falls back to the deterministic template.
"""

import re

from app.explain.types import EvidencePayload

BANNED_PHRASES = (
    "never thanked",
    "was never contacted",
    "never contacted",
    "influential",
    "friends with",
    "wealthy",
    "capacity to give",
    "can afford",
    "suggests wealth",
    "indicates wealth",
    "financial capacity",
)

_NUMBER_RE = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def _numbers(text: str) -> set[str]:
    return {token.strip("$,%") for token in _NUMBER_RE.findall(text)}


def _grounded_text(payload: EvidencePayload) -> str:
    parts = [payload.entity_name, payload.action, *payload.evidence]
    parts += [str(value) for value in payload.facts.values()]
    return " ".join(parts)


def banned_phrase(text: str) -> str | None:
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            return phrase
    return None


def is_grounded(text: str, payload: EvidencePayload) -> bool:
    grounded_numbers = _numbers(_grounded_text(payload))
    return all(number in grounded_numbers for number in _numbers(text))


def validate(text: str, payload: EvidencePayload) -> bool:
    if not text or not text.strip():
        return False
    if banned_phrase(text):
        return False
    if not is_grounded(text, payload):
        return False
    return True
