"""Deterministic fallback explanations.

Used whenever the LLM is unavailable, unconfigured, slow, or returns
invalid output. Built entirely by echoing the evidence payload, so it
is grounded and G4/G5/G6-safe by construction.
"""

from app.explain.types import EvidencePayload

_ACTION_LEAD = {
    "THANK": "Sam recommends a thank-you for",
    "FOLLOW UP": "Sam recommends following up with",
    "RECONNECT": "Sam recommends reconnecting with",
    "ASSIGN": "Sam recommends assigning a fundraiser to",
    "WAIT": "Sam recommends waiting before reaching out to",
}


def render_template(payload: EvidencePayload) -> str:
    lead = _ACTION_LEAD.get(payload.action, f"Sam surfaced {payload.action} for")
    if not payload.evidence:
        return f"{lead} {payload.entity_name}."
    evidence_text = "; ".join(payload.evidence)
    return f"{lead} {payload.entity_name}: {evidence_text}."
