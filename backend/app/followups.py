"""Builds the GET /api/followups response (SIG2).

Lists every due commitment regardless of population (Appendix B's count
of 40 includes a handful of organizations; SC1/SC3's actionable FOLLOW
UP recommendation still only applies to the individual population, same
as every other signal).
"""

import pandas as pd

from app.normalize import population
from app.signals.broken_commitment import (
    EXPLICIT_RESOLUTION_NOTE,
    build_signal_and_channel_note,
    compute_due_commitments,
)
from app.staff_lookup import assigned_officer_name, officer_names


def build_followups(
    constituents: pd.DataFrame,
    interactions: pd.DataFrame,
    staff: pd.DataFrame,
    include_resolved: bool,
) -> dict:
    all_constituents = constituents.set_index("id", drop=False)
    pop_ids = set(population(constituents)["id"])
    names = officer_names(staff)

    due = compute_due_commitments(interactions)
    if not include_resolved:
        due = [row for row in due if not row["resolved"]]

    rows = []
    for row in due:
        constituent = all_constituents.loc[row["constituent_id"]]
        is_population = row["constituent_id"] in pop_ids
        officer_name = assigned_officer_name(constituent["assigned_staff_id"], names)

        entry = {
            "entity_type": constituent["entity_type"],
            "entity_id": row["constituent_id"],
            "entity_name": constituent["preferred_name"],
            "interaction_id": row["interaction_id"],
            "follow_up_date": row["follow_up_date"].isoformat(),
            "days_overdue": row["days_overdue"],
            "prior_purpose": row["prior_purpose"],
            "prior_outcome": row["prior_outcome"],
            "prior_interaction_type": row["prior_interaction_type"],
            "prior_occurred_date": row["prior_occurred_date"].isoformat(),
            "resolved": row["resolved"],
            "resolved_by_interaction_id": row["resolved_by_interaction_id"],
            "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] else None,
            "explicitly_completed_or_cancelled": row["explicitly_completed_or_cancelled"],
            "assigned_officer": officer_name,
            "action": None,
            "evidence": [],
            "channel_hint": None,
            "channel_note": None,
        }

        if not row["resolved"] and is_population:
            signal, note = build_signal_and_channel_note(row, constituent, officer_name)
            entry["action"] = signal.action
            entry["evidence"] = signal.evidence
            entry["channel_hint"] = signal.channel_hint
            entry["channel_note"] = note

        rows.append(entry)

    return {"commitments": rows, "explicit_resolution_note": EXPLICIT_RESOLUTION_NOTE}
