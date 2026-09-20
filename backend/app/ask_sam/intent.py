"""Extracts one of a fixed set of intents from a natural-language
question (PRD Section 12, AQ1/AQ2/AQ3/AQ4/AQ5/AQ6).

The LLM sees only the question and this module's schema/examples --
never the dataset (PRD Section 13). It must return strict JSON; any
other output, or no configured client, falls back to a deterministic
keyword match against the four exact example phrasings. An
unrecognized question returns None either way -- Sam never guesses.
"""

import json
import re

from app.explain.client import LLMClient, LLMUnavailableError, default_client

INTENT_FOLLOW_UPS = "FOLLOW_UPS"  # AQ1
INTENT_UNASSIGNED_MAJOR_DONORS = "UNASSIGNED_MAJOR_DONORS"  # AQ2
INTENT_COOLING_COMMUNITIES = "COOLING_COMMUNITIES"  # AQ3
INTENT_DO_NOT_CONTACT_TODAY = "DO_NOT_CONTACT_TODAY"  # AQ4
INTENT_WHY_PERSON = "WHY_PERSON"  # AQ5
INTENT_LOCATION_ACTIVITY = "LOCATION_ACTIVITY"  # AQ6

SUPPORTED_INTENTS = frozenset(
    {
        INTENT_FOLLOW_UPS,
        INTENT_UNASSIGNED_MAJOR_DONORS,
        INTENT_COOLING_COMMUNITIES,
        INTENT_DO_NOT_CONTACT_TODAY,
        INTENT_WHY_PERSON,
        INTENT_LOCATION_ACTIVITY,
    }
)

EXAMPLES = [
    "Who have we promised to follow up with?",
    "Show major donors without an assigned officer.",
    "Which communities are losing engagement?",
    "Who shouldn't I contact today?",
    "Why did Valerie surface?",
    "Show Boston alumni connected to athletics.",
]

SYSTEM_PROMPT = f"""You classify a fundraiser's question into one of these intents and return strict JSON, nothing else.

Intents:
- {INTENT_FOLLOW_UPS}: asking who they promised to follow up with.
- {INTENT_UNASSIGNED_MAJOR_DONORS}: asking for major donors with no assigned officer.
- {INTENT_COOLING_COMMUNITIES}: asking which communities are losing engagement or cooling.
- {INTENT_DO_NOT_CONTACT_TODAY}: asking who not to contact today.
- {INTENT_WHY_PERSON}: asking why a specific named person surfaced. Include a "name" field with just their name.
- {INTENT_LOCATION_ACTIVITY}: asking for people in a city connected to an activity type (e.g. athletics). Include "city", "state", and "activity_type" fields.

If the question doesn't match any of these, return {{"intent": null}}.

Output JSON only, e.g. {{"intent": "{INTENT_WHY_PERSON}", "name": "Valerie"}} or {{"intent": "{INTENT_FOLLOW_UPS}"}}."""


def _normalize(question: str) -> str:
    return re.sub(r"[^\w\s]", "", question).strip().lower()


def _keyword_fallback(question: str) -> dict | None:
    normalized = _normalize(question)

    why_match = re.match(r"why did (.+?) surface$", normalized)
    if why_match:
        return {"intent": INTENT_WHY_PERSON, "name": why_match.group(1).strip()}

    if "promised" in normalized and "follow up" in normalized:
        return {"intent": INTENT_FOLLOW_UPS}

    if "major donor" in normalized and ("assigned officer" in normalized or "without an assigned" in normalized):
        return {"intent": INTENT_UNASSIGNED_MAJOR_DONORS}

    if "contact today" in normalized and ("shouldnt" in normalized or "should not" in normalized):
        return {"intent": INTENT_DO_NOT_CONTACT_TODAY}

    if "communit" in normalized and ("losing engagement" in normalized or "cooling" in normalized):
        return {"intent": INTENT_COOLING_COMMUNITIES}

    location_match = re.match(r"show (.+?) alumni connected to (.+)$", normalized)
    if location_match:
        return {
            "intent": INTENT_LOCATION_ACTIVITY,
            "city": location_match.group(1).strip(),
            "activity_type": location_match.group(2).strip(),
        }

    return None


def _valid(parsed: dict) -> bool:
    if not isinstance(parsed, dict) or parsed.get("intent") not in SUPPORTED_INTENTS:
        return False
    if parsed["intent"] == INTENT_WHY_PERSON and not parsed.get("name"):
        return False
    if parsed["intent"] == INTENT_LOCATION_ACTIVITY and not (parsed.get("city") and parsed.get("activity_type")):
        return False
    return True


_UNSET = object()


def extract_intent(question: str, client: LLMClient | None = _UNSET) -> dict | None:  # type: ignore[assignment]
    resolved_client = default_client() if client is _UNSET else client

    if resolved_client is not None:
        try:
            raw = resolved_client.complete(SYSTEM_PROMPT, question)
            parsed = json.loads(raw)
            if _valid(parsed):
                return parsed
        except (LLMUnavailableError, json.JSONDecodeError, TypeError, ValueError):
            pass

    return _keyword_fallback(question)
