"""SIG2: Broken Commitment -> FOLLOW UP.

A commitment is due when an interaction's follow_up_date is on or
before AS_OF_DATE. It resolves when a later interaction with the same
constituent occurs on or after that date, or when the source data
explicitly marks it completed or cancelled. This dataset has no such
field, so only the first clause applies (see
`is_explicitly_completed_or_cancelled` for the documented hook).
"""

import pandas as pd

from app.channel_resolution import channel_note, resolve_channel
from app.config import AS_OF_DATE
from app.context import Context
from app.formatting import format_date
from app.models import Signal
from app.normalize import population
from app.registry import register
from app.staff_lookup import assigned_officer_name, officer_names

SIGNAL_ID = "SIG2"
ACTION = "FOLLOW UP"

EXPLICIT_RESOLUTION_NOTE = (
    "An explicit completed/cancelled indicator is not available in this dataset; "
    "resolution is inferred from a later interaction."
)

OUTCOME_LABELS = {
    "no_response": "No response",
    "connected": "Connected",
    "replied": "Replied",
    "meeting_booked": "Meeting booked",
    "declined": "Declined",
    "pledged": "Pledged",
    "gift_received": "Gift received",
    "information_updated": "Information updated",
}


def is_explicitly_completed_or_cancelled(interaction_row: pd.Series) -> bool:
    """Hook for an explicit completed/cancelled indicator on the commitment's
    source interaction. Always False: this dataset carries no such field.
    A future data source could populate this, e.g. by checking a
    `commitment_status` column.
    """
    return False


def compute_due_commitments(interactions: pd.DataFrame) -> list[dict]:
    """Every interaction whose follow_up_date is due by AS_OF_DATE, with
    resolution status. Follow-up dates after AS_OF_DATE are upcoming and
    are not included here.
    """
    all_interactions = interactions.copy()
    all_interactions["occurred_date"] = pd.to_datetime(all_interactions["occurred_at"]).dt.date

    due = all_interactions.dropna(subset=["follow_up_date"]).copy()
    due["follow_up_date"] = pd.to_datetime(due["follow_up_date"]).dt.date
    due = due[due["follow_up_date"] <= AS_OF_DATE]

    results = []
    for _, row in due.iterrows():
        later = all_interactions[
            (all_interactions["constituent_id"] == row["constituent_id"])
            & (all_interactions["id"] != row["id"])
            & (all_interactions["occurred_date"] >= row["follow_up_date"])
        ].sort_values("occurred_date")

        resolved_by = int(later.iloc[0]["id"]) if not later.empty else None
        resolved_at = later.iloc[0]["occurred_date"] if not later.empty else None
        explicitly_resolved = is_explicitly_completed_or_cancelled(row)

        results.append(
            {
                "constituent_id": int(row["constituent_id"]),
                "interaction_id": int(row["id"]),
                "follow_up_date": row["follow_up_date"],
                "days_overdue": (AS_OF_DATE - row["follow_up_date"]).days,
                "prior_purpose": row["purpose"],
                "prior_outcome": row["outcome"],
                "prior_interaction_type": row["interaction_type"],
                "prior_occurred_date": row["occurred_date"],
                "resolved": explicitly_resolved or resolved_by is not None,
                "resolved_by_interaction_id": resolved_by,
                "resolved_at": resolved_at,
                "explicitly_completed_or_cancelled": explicitly_resolved,
            }
        )
    return results


def _prior_outcome_evidence(row: dict) -> str:
    outcome_label = OUTCOME_LABELS.get(row["prior_outcome"], row["prior_outcome"])
    return (
        f"{outcome_label} on a {format_date(row['prior_occurred_date'])} "
        f"{row['prior_purpose']} {row['prior_interaction_type']}"
    )


def _contact_facts(constituent: pd.Series) -> dict:
    return {
        "deceased": bool(constituent["deceased"]),
        "do_not_solicit": bool(constituent["do_not_solicit"]),
        "phone_status": constituent["phone_status"],
        "email_status": constituent["email_status"],
        "outbound_dates": [],
        "has_scheduled_future_interaction": False,
    }


def _base_signal(row: dict, constituent: pd.Series, officer_name: str | None) -> Signal:
    return Signal(
        entity_type="constituent",
        entity_id=row["constituent_id"],
        entity_name=constituent["preferred_name"],
        signal_id=SIGNAL_ID,
        action=ACTION,
        evidence=[
            f"Follow-up was due {format_date(row['follow_up_date'])}",
            "No subsequent follow-up is recorded",
            _prior_outcome_evidence(row),
        ][:3],
        urgency_date=row["follow_up_date"].isoformat(),
        urgency_days=row["days_overdue"],
        assigned_officer=officer_name,
    )


def build_signal_and_channel_note(
    row: dict, constituent: pd.Series, officer_name: str | None
) -> tuple[Signal, str | None]:
    """The FOLLOW UP Signal for one unresolved due commitment, plus an
    explanatory note about any non-chosen channel (e.g. "Email status is
    inactive; phone is the allowed channel"), even when that channel
    never blocked the choice. Used by GET /api/followups, which is
    independent of the Today registry/priority queue.
    """
    decision, rejected = resolve_channel(_contact_facts(constituent), ACTION)
    notes = channel_note(decision.allowed_channel, rejected) if decision.allowed_channel else []

    signal = _base_signal(row, constituent, officer_name)
    signal.channel_hint = decision.allowed_channel
    return signal, (notes[0] if notes else None)


def _detect(constituents: pd.DataFrame, interactions: pd.DataFrame, staff: pd.DataFrame) -> list[Signal]:
    """Raw signals, no channel -- app.priority_queue resolves the channel
    centrally, like every other registered signal type.
    """
    pop = population(constituents).set_index("id", drop=False)
    names = officer_names(staff)

    due = compute_due_commitments(interactions)
    unresolved = [row for row in due if not row["resolved"] and row["constituent_id"] in pop.index]

    signals = []
    for row in unresolved:
        constituent = pop.loc[row["constituent_id"]]
        officer_name = assigned_officer_name(constituent["assigned_staff_id"], names)
        signals.append(_base_signal(row, constituent, officer_name))

    return signals


@register
def detect(context: Context) -> list[Signal]:
    return _detect(context.constituents, context.interactions, context.staff)
