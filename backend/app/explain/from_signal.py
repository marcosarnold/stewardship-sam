"""Builds an EvidencePayload from a serialized Signal (or relationship
"why" entry) dict, for wiring explain() into the API layer."""

from app.explain.types import EvidencePayload

_FACT_KEYS = ("channel_hint", "assigned_officer", "urgency_amount", "urgency_days")


def payload_from_signal_dict(signal: dict) -> EvidencePayload:
    facts = {key: signal[key] for key in _FACT_KEYS if signal.get(key) is not None}
    return EvidencePayload(
        entity_name=signal["entity_name"],
        action=signal["action"],
        evidence=signal.get("evidence", []),
        facts=facts,
    )
