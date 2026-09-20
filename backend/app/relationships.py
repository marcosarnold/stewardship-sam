"""Builds the GET /api/relationships/:id response (UX2).

The page renders whatever signals currently exist for this person
through the shared Signal record: THANK/WAIT/ASSIGN/RECONNECT (merged
into Today by issue 004) plus FOLLOW UP (issue 003, not yet merged into
Today itself -- see issues/007). Held-back signals still appear, tagged
with their policy status, so the "why" card is never silently empty.
"""

import pandas as pd

from app.formatting import format_date
from app.signals import broken_commitment
from app.staff_lookup import assigned_officer_name, officer_names
from app.today import build_today_queue

# Priority for picking one headline "recommended action" when a person
# currently has more than one signal (expected until issue 007 merges
# per-person). WAIT signals restraint; FOLLOW UP is an explicit existing
# promise; both outrank routine stewardship/ownership actions.
ACTION_PRIORITY = {"WAIT": 0, "FOLLOW UP": 1, "THANK": 2, "RECONNECT": 3, "ASSIGN": 4}


def _clean(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str) and value == "":
        return None
    return value


def find_constituent(entity_id: int, constituents: pd.DataFrame):
    """The constituent row, or None if the id is unknown, not an
    individual, or deceased -- all of which are a not-found state here.
    """
    matches = constituents[constituents["id"] == entity_id]
    if matches.empty:
        return None
    row = matches.iloc[0]
    if row["entity_type"] != "individual" or bool(row["deceased"]):
        return None
    return row


def _degree_info(entity_id: int, degrees: pd.DataFrame) -> dict:
    rows = degrees[(degrees["constituent_id"] == entity_id) & degrees["class_year"].notna()]
    if rows.empty:
        return {"class_year": None, "degree": None}
    first = rows.sort_values("class_year").iloc[0]
    label_parts = [p for p in [_clean(first["degree_type"]), _clean(first["major"])] if p]
    return {
        "class_year": int(first["class_year"]),
        "degree": ", ".join(label_parts) if label_parts else None,
    }


def _activities(entity_id: int, activities: pd.DataFrame) -> list[str]:
    rows = activities[activities["constituent_id"] == entity_id]
    return sorted(set(rows["activity_name"].tolist()))


def _kept_commitments(entity_id: int, interactions: pd.DataFrame) -> list[dict]:
    due = broken_commitment.compute_due_commitments(interactions)
    resolved = [row for row in due if row["constituent_id"] == entity_id and row["resolved"]]

    by_id = interactions.set_index("id")
    notes = []
    for row in resolved:
        resolved_type = None
        if row["resolved_by_interaction_id"] is not None:
            resolved_type = by_id.loc[row["resolved_by_interaction_id"], "interaction_type"]

        note = f"Follow-up promised {format_date(row['follow_up_date'])} was kept"
        if resolved_type and row["resolved_at"]:
            note += f" — a {resolved_type} occurred on {format_date(row['resolved_at'])}."
        else:
            note += "."

        notes.append(
            {
                "follow_up_date": row["follow_up_date"].isoformat(),
                "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] else None,
                "note": note,
            }
        )
    return notes


def _recommended_action(signals: list) -> str | None:
    if not signals:
        return None
    return min(signals, key=lambda s: ACTION_PRIORITY.get(s.action, 99)).action


def build_relationship(
    entity_id: int,
    constituents: pd.DataFrame,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
    staff: pd.DataFrame,
    opportunities: pd.DataFrame,
    degrees: pd.DataFrame,
    activities: pd.DataFrame,
) -> dict | None:
    constituent = find_constituent(entity_id, constituents)
    if constituent is None:
        return None

    names = officer_names(staff)
    assigned_officer = assigned_officer_name(constituent["assigned_staff_id"], names)

    today_items, held_back = build_today_queue(constituents, gifts, interactions, staff, opportunities)
    person_signals = [s for s in today_items if s.entity_id == entity_id]
    person_held_back = [item for item in held_back if item["entity_id"] == entity_id]

    follow_up_signals = [
        s for s in broken_commitment.detect(constituents, interactions, staff) if s.entity_id == entity_id
    ]
    person_signals += follow_up_signals

    why = [dict(s.to_dict(), policy_status="shown") for s in person_signals]
    why += [
        {
            "entity_type": item["entity_type"],
            "entity_id": item["entity_id"],
            "entity_name": item["entity_name"],
            "action": item["action"],
            "evidence": item.get("evidence", []),
            "policy_status": "held_back",
            "policy_reason_code": item["reason_code"],
            "policy_reason": item["reason"],
        }
        for item in person_held_back
    ]

    degree_info = _degree_info(entity_id, degrees)

    return {
        "entity_id": int(entity_id),
        "entity_name": constituent["preferred_name"],
        "class_year": degree_info["class_year"],
        "degree": degree_info["degree"],
        "activities": _activities(entity_id, activities),
        "city": _clean(constituent["city"]),
        "state": _clean(constituent["state"]),
        "assigned_officer": assigned_officer,
        "recommended_action": _recommended_action(person_signals),
        "signals": why,
        "kept_commitments": _kept_commitments(entity_id, interactions),
    }
