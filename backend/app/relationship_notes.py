"""Extracts structured relationship memory from a post-call note (PRD
Section 15): interest, communication preference, solicitation status,
and a follow-up date. Strict output shape; any field not mentioned in
the note stays null -- Sam never guesses (G4). Nothing here is saved;
see app.relationship_memory for the confirm-then-save step (Section 16).
"""

import json
import re
from datetime import date

from app.config import AS_OF_DATE
from app.explain.client import LLMClient, LLMUnavailableError, default_client

COMMUNICATION_PREFERENCES = frozenset({"phone", "email", "text"})
SOLICITATION_STATUSES = frozenset({"not_currently_interested"})

_MONTHS = {
    name: i
    for i, name in enumerate(
        [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ],
        start=1,
    )
}

SYSTEM_PROMPT = (
    "Extract structured relationship memory from a fundraiser's post-call note. "
    "Return strict JSON with keys: interest (string or null), "
    "communication_preference (one of phone/email/text, or null), "
    "solicitation_status (one of not_currently_interested, or null), "
    "follow_up_month (the full month name mentioned for a follow-up, or null). "
    "Leave a field null if the note does not mention it -- never guess."
)


def _keyword_extract(note: str) -> dict:
    """Deterministic fallback, tuned for the PRD's example note and
    similarly-phrased ones. An LLM (when configured) handles the general
    case; this covers "works with the LLM unavailable."
    """
    lowered = note.lower()

    interest = None
    match = re.search(r"interested in (?:the )?([A-Za-z0-9' ]+?)(?:,| and|\.|$)", note, re.IGNORECASE)
    if match:
        phrase = match.group(1).strip()
        interest = phrase if phrase.lower().endswith("s") else f"{phrase}s"

    comm_pref = None
    if "prefer" in lowered:
        if "text" in lowered:
            comm_pref = "text"
        elif "email" in lowered:
            comm_pref = "email"
        elif "phone" in lowered or "call" in lowered:
            comm_pref = "phone"

    solicitation_status = None
    if any(
        phrase in lowered
        for phrase in ("isn't ready to give", "isnt ready to give", "not currently interested", "not ready to give")
    ):
        solicitation_status = "not_currently_interested"

    follow_up_month = next((name for name in _MONTHS if name in lowered), None)

    return {
        "interest": interest,
        "communication_preference": comm_pref,
        "solicitation_status": solicitation_status,
        "follow_up_month": follow_up_month,
    }


def _month_to_date(month_name: str | None) -> str | None:
    if not month_name:
        return None
    month_num = _MONTHS[month_name.lower()]
    year = AS_OF_DATE.year if month_num >= AS_OF_DATE.month else AS_OF_DATE.year + 1
    return date(year, month_num, 1).isoformat()


def _valid(parsed: dict) -> bool:
    if not isinstance(parsed, dict):
        return False
    if parsed.get("communication_preference") not in (None, *COMMUNICATION_PREFERENCES):
        return False
    if parsed.get("solicitation_status") not in (None, *SOLICITATION_STATUSES):
        return False
    return True


_UNSET = object()


def extract_note(note: str, client: LLMClient | None = _UNSET) -> dict:  # type: ignore[assignment]
    resolved_client = default_client() if client is _UNSET else client

    parsed = None
    if resolved_client is not None:
        try:
            raw = resolved_client.complete(SYSTEM_PROMPT, note)
            candidate = json.loads(raw)
            if _valid(candidate):
                parsed = candidate
        except (LLMUnavailableError, json.JSONDecodeError, TypeError, ValueError):
            pass

    if parsed is None:
        parsed = _keyword_extract(note)

    return {
        "interest": parsed.get("interest"),
        "communication_preference": parsed.get("communication_preference"),
        "solicitation_status": parsed.get("solicitation_status"),
        "follow_up_date": _month_to_date(parsed.get("follow_up_month")),
    }
