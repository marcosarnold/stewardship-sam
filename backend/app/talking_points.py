"""Builds 3-5 talking points/checklist items for a "Prepare action"
brief -- never a full message draft (PRD Section 20 non-goal). Uses
the grounded explanation service when available, with a fully
deterministic fallback so this works with the LLM unavailable.
"""

from app.explain import EvidencePayload, explain

_MIN_POINTS = 3
_MAX_POINTS = 5


def _channel_point(channel_hint: str | None) -> str:
    if channel_hint:
        return f"Reach out by {channel_hint}."
    return "No allowed channel is currently available -- do not attempt contact."


def build_talking_points(entity_name: str, action: str, evidence: list[str], channel_hint: str | None) -> list[str]:
    points: list[str] = []

    explanation = explain(EvidencePayload(entity_name=entity_name, action=action, evidence=evidence))
    points.append(explanation.text)
    points.append(_channel_point(channel_hint))
    for line in evidence:
        if line not in points:
            points.append(line)

    deduped: list[str] = []
    for p in points:
        if p not in deduped:
            deduped.append(p)

    while len(deduped) < _MIN_POINTS:
        deduped.append("Confirm current contact details before reaching out.")

    return deduped[:_MAX_POINTS]
