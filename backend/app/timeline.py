"""Builds GET /api/relationships/:id/timeline (UX2, G4, G6).

Merges gifts, interactions, events attended, career changes, and
opportunities into one newest-first list. Type filters narrow the list
before pagination, so `total`/`has_more` always describe the filtered
set, not the person's full history.
"""

import pandas as pd

from app.config import TIMELINE_PAGE_SIZE
from app.formatting import format_amount, format_date

TIMELINE_TYPES = ("gift", "interaction", "event", "career_change", "opportunity")

INTERACTION_OUTCOME_LABELS = {
    "no_response": "No response",
    "connected": "Connected",
    "replied": "Replied",
    "meeting_booked": "Meeting booked",
    "declined": "Declined",
    "pledged": "Pledged",
    "gift_received": "Gift received",
    "information_updated": "Information updated",
}

OPPORTUNITY_STATUS_LABELS = {
    "identified": "Identified",
    "qualifying": "Qualifying",
    "cultivating": "Cultivating",
    "soliciting": "Soliciting",
    "committed": "Committed",
    "closed_won": "Closed, won",
    "closed_lost": "Closed, lost",
}


def _clean(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str) and value == "":
        return None
    return value


def _gift_entries(entity_id: int, gifts: pd.DataFrame) -> list[dict]:
    rows = gifts[gifts["constituent_id"] == entity_id]
    entries = []
    for _, row in rows.iterrows():
        gift_date = pd.to_datetime(row["gift_date"]).date()
        gift_type = str(row["gift_type"]).replace("_", " ")
        entries.append(
            {
                "type": "gift",
                "date": gift_date.isoformat(),
                "headline": f"{format_amount(row['amount'])} gift",
                "detail": f"{gift_type}, {row['status']}",
                "significant": None,
            }
        )
    return entries


def _interaction_entries(entity_id: int, interactions: pd.DataFrame) -> list[dict]:
    rows = interactions[interactions["constituent_id"] == entity_id]
    entries = []
    for _, row in rows.iterrows():
        occurred = pd.to_datetime(row["occurred_at"]).date()
        outcome = INTERACTION_OUTCOME_LABELS.get(row["outcome"], row["outcome"])
        headline = f"{str(row['interaction_type']).capitalize()} ({row['direction']}) — {outcome}"
        detail_parts = [_clean(row["subject"]), _clean(row["notes"])]
        entries.append(
            {
                "type": "interaction",
                "date": occurred.isoformat(),
                "headline": headline,
                "detail": " — ".join(p for p in detail_parts if p) or None,
                "significant": bool(row["significant"]),
                "follow_up_date": _clean(row["follow_up_date"]),
            }
        )
    return entries


def _event_entries(entity_id: int, attendance: pd.DataFrame, events: pd.DataFrame) -> list[dict]:
    rows = attendance[attendance["constituent_id"] == entity_id]
    if rows.empty:
        return []
    joined = rows.merge(events, left_on="event_id", right_on="id", suffixes=("", "_event"))
    entries = []
    for _, row in joined.iterrows():
        attended = pd.to_datetime(row["attended_at"]).date()
        location = ", ".join(p for p in [_clean(row["city"]), _clean(row["state"])] if p)
        detail = f"{str(row['event_type']).replace('_', ' ')}" + (f" · {location}" if location else "")
        entries.append(
            {
                "type": "event",
                "date": attended.isoformat(),
                "headline": f"Attended {row['name']}",
                "detail": detail,
                "significant": None,
            }
        )
    return entries


def _career_change_entries(entity_id: int, career_history: pd.DataFrame) -> list[dict]:
    rows = career_history[career_history["constituent_id"] == entity_id]
    entries = []
    for _, row in rows.iterrows():
        started = pd.to_datetime(row["started_at"]).date()
        job_title = _clean(row["job_title"])
        headline = f"Started as {job_title} at {row['employer']}" if job_title else f"Started at {row['employer']}"
        if bool(row["is_current"]):
            detail = "Current position"
        elif _clean(row["ended_at"]):
            detail = f"Through {format_date(pd.to_datetime(row['ended_at']).date())}"
        else:
            detail = None
        entries.append(
            {
                "type": "career_change",
                "date": started.isoformat(),
                "headline": headline,
                "detail": detail,
                "significant": None,
            }
        )
    return entries


def _opportunity_entries(entity_id: int, opportunities: pd.DataFrame) -> list[dict]:
    rows = opportunities[opportunities["constituent_id"] == entity_id]
    entries = []
    for _, row in rows.iterrows():
        date_value = next(
            (v for v in (row["closed_at"], row["response_date"], row["ask_date"], row["expected_ask_date"]) if _clean(v) is not None)
        )
        opp_date = pd.to_datetime(date_value).date()
        status_label = OPPORTUNITY_STATUS_LABELS.get(row["status"], row["status"])
        amount = next(
            (v for v in (row["accepted_amount"], row["ask_amount"], row["expected_ask_amount"]) if _clean(v) is not None),
            None,
        )
        detail = f"{format_amount(amount)} expected" if amount is not None else None
        entries.append(
            {
                "type": "opportunity",
                "date": opp_date.isoformat(),
                "headline": f"Opportunity {status_label.lower()}",
                "detail": detail,
                "significant": None,
            }
        )
    return entries


def build_timeline(
    entity_id: int,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
    events: pd.DataFrame,
    event_attendance: pd.DataFrame,
    career_history: pd.DataFrame,
    opportunities: pd.DataFrame,
    types: list[str] | None = None,
    page: int = 1,
    page_size: int = TIMELINE_PAGE_SIZE,
) -> dict:
    all_entries = {
        "gift": _gift_entries(entity_id, gifts),
        "interaction": _interaction_entries(entity_id, interactions),
        "event": _event_entries(entity_id, event_attendance, events),
        "career_change": _career_change_entries(entity_id, career_history),
        "opportunity": _opportunity_entries(entity_id, opportunities),
    }
    counts = {t: len(all_entries[t]) for t in TIMELINE_TYPES}

    selected_types = types if types else list(TIMELINE_TYPES)
    filtered = [entry for t in selected_types for entry in all_entries[t]]
    filtered.sort(key=lambda e: e["date"], reverse=True)

    total = len(filtered)
    start = (page - 1) * page_size
    page_entries = filtered[start : start + page_size]

    return {
        "entity_id": entity_id,
        "entries": page_entries,
        "counts": counts,
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_more": start + page_size < total,
    }
