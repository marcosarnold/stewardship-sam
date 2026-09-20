"""Builds GET /api/relationships/:id/prepare-action (issue 017).

A short brief: the recommended action, the allowed channel from the
policy engine, the officer who owns the relationship (G3), an evidence
recap, and 3-5 talking points/checklist items. Sam never sends, calls,
solicits, or changes assignments (PRD Section 16) -- this brief is
read-only input for a human, not an action Sam takes.
"""

from app.action_outcomes import latest_outcome
from app.context import Context
from app.priority_queue import evaluate_signals, merge_per_person
from app.relationships import find_constituent
from app.staff_lookup import assigned_officer_name, officer_names
from app.talking_points import build_talking_points


def build_action_brief(entity_id: int, context: Context) -> dict | None:
    constituent = find_constituent(entity_id, context.constituents)
    if constituent is None:
        return None

    names = officer_names(context.staff)
    assigned_officer = assigned_officer_name(constituent["assigned_staff_id"], names)

    shown, _held_back = evaluate_signals(context)
    person_signals = [s for s in shown if s.entity_id == entity_id]
    merged = merge_per_person(person_signals)

    if not merged:
        return {
            "entity_id": int(entity_id),
            "entity_name": constituent["preferred_name"],
            "assigned_officer": assigned_officer,
            "action": None,
            "channel_hint": None,
            "evidence": [],
            "talking_points": [],
            "last_outcome": latest_outcome(entity_id),
        }

    item = merged[0]
    talking_points = build_talking_points(item.entity_name, item.action, item.evidence, item.channel_hint)

    return {
        "entity_id": int(entity_id),
        "entity_name": constituent["preferred_name"],
        "assigned_officer": assigned_officer,
        "action": item.action,
        "channel_hint": item.channel_hint,
        "evidence": item.evidence,
        "talking_points": talking_points,
        "last_outcome": latest_outcome(entity_id),
    }
