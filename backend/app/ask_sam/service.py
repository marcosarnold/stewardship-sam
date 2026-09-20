"""ask(): the one entry point for Ask Sam person-level (issue 014) and
community/graph-level (issue 015) queries.

Pipeline (PRD Section 12/13): extract_intent (LLM + keyword fallback,
never sees the dataset) -> a strict enum -> a deterministic executor
that calls the existing engines -> an answer grounded entirely in the
executor's own result, never free-form LLM prose about the data.
"""

from app.ask_sam.executor import (
    cooling_communities_query,
    do_not_contact_today_query,
    followups_query,
    location_activity_query,
    unassigned_major_donors_query,
    why_person_query,
)
from app.ask_sam.intent import (
    EXAMPLES,
    INTENT_COOLING_COMMUNITIES,
    INTENT_DO_NOT_CONTACT_TODAY,
    INTENT_FOLLOW_UPS,
    INTENT_LOCATION_ACTIVITY,
    INTENT_UNASSIGNED_MAJOR_DONORS,
    INTENT_WHY_PERSON,
    extract_intent,
)
from app.context import Context

UNSUPPORTED_ANSWER = "I can't answer that yet. Try one of: " + " / ".join(EXAMPLES)

_UNSET = object()


def _followups_answer(results: dict) -> str:
    return (
        f"{len(results['overdue'])} overdue and unresolved, {len(results['upcoming'])} upcoming "
        f"(and {len(results['resolved'])} already resolved)."
    )


def _unassigned_answer(results: list[dict]) -> str:
    return f"{len(results)} major donor{'s' if len(results) != 1 else ''} have no assigned officer."


def _do_not_contact_answer(results: dict) -> str:
    return f"{len(results['wait'])} in WAIT, {len(results['held_back'])} held back today."


def _cooling_answer(results: list[dict]) -> str:
    return f"{len(results)} communities are cooling, worst decline first."


def _location_activity_answer(city: str, activity_type: str, results: dict) -> str:
    if results["status"] == "no_location_matches":
        return f'No constituents found in "{city}" connected to {activity_type}.'
    return f"{len(results['people'])} people in {city} connected to {activity_type} communities."


def _why_person_answer(name: str, results: dict) -> str:
    if results["status"] == "not_found":
        return f'I can\'t find anyone named "{name}".'
    if results["status"] == "ambiguous":
        names = ", ".join(m["entity_name"] for m in results["matches"])
        return f'Multiple people match "{name}": {names}. Which one did you mean?'
    if not results["signals"]:
        return f"{results['entity_name']} has no current signal."
    lead = results["signals"][0]
    evidence = "; ".join(lead["evidence"]) if lead.get("evidence") else lead["action"]
    return f"{results['entity_name']} surfaced as {lead['action']}: {evidence}"


def ask(question: str, context: Context, degrees, activities, affiliations, client=_UNSET) -> dict:
    intent = extract_intent(question) if client is _UNSET else extract_intent(question, client)
    if intent is None:
        return {"intent": None, "answer": UNSUPPORTED_ANSWER, "examples": EXAMPLES, "results": None}

    kind = intent["intent"]

    if kind == INTENT_FOLLOW_UPS:
        results = followups_query(context)
        answer = _followups_answer(results)
    elif kind == INTENT_UNASSIGNED_MAJOR_DONORS:
        results = unassigned_major_donors_query(context)
        answer = _unassigned_answer(results)
    elif kind == INTENT_DO_NOT_CONTACT_TODAY:
        results = do_not_contact_today_query(context)
        answer = _do_not_contact_answer(results)
    elif kind == INTENT_WHY_PERSON:
        name = intent.get("name", "")
        results = why_person_query(name, context, degrees, activities, affiliations)
        answer = _why_person_answer(name, results)
    elif kind == INTENT_COOLING_COMMUNITIES:
        results = cooling_communities_query(context)
        answer = _cooling_answer(results)
    elif kind == INTENT_LOCATION_ACTIVITY:
        city = intent.get("city", "")
        activity_type = intent.get("activity_type", "")
        results = location_activity_query(city, activity_type, context)
        answer = _location_activity_answer(city, activity_type, results)
    else:
        return {"intent": None, "answer": UNSUPPORTED_ANSWER, "examples": EXAMPLES, "results": None}

    return {"intent": kind, "answer": answer, "results": results, "examples": None}
