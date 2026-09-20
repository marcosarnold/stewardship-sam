"""SIG3: Neglected Relationship -> ASSIGN / RECONNECT.

A major donor (lifetime received giving >= MAJOR_DONOR_LIFETIME_USD)
with no recorded interaction within LONG_INTERACTION_GAP_DAYS (or
ever). ASSIGN when unassigned or assigned to an inactive staff member
(treated as unassigned); RECONNECT when assigned to an active officer.
This signal never returns ASK (G1, G3).

Returns raw signals only -- contact policy (channel, suppression) is
applied centrally by app.priority_queue, which also treats ASSIGN as
an internal action that is never hidden by contact restrictions.
"""

from datetime import timedelta

import pandas as pd

from app.config import AS_OF_DATE, LONG_INTERACTION_GAP_DAYS, MAJOR_DONOR_LIFETIME_USD
from app.context import Context
from app.formatting import format_amount, format_date
from app.models import Signal
from app.normalize import population, received_gifts
from app.registry import register
from app.staff_lookup import assigned_officer_name, officer_names

SIGNAL_ID = "SIG3"
ASSIGN = "ASSIGN"
RECONNECT = "RECONNECT"

_GAP_CUTOFF = AS_OF_DATE - timedelta(days=LONG_INTERACTION_GAP_DAYS)


def _lifetime_giving(gifts: pd.DataFrame, pop_ids: set) -> pd.Series:
    recv = received_gifts(gifts)
    recv = recv[recv["constituent_id"].isin(pop_ids)]
    return recv.groupby("constituent_id")["amount"].sum()


def _last_interaction_dates(interactions: pd.DataFrame, pop_ids: set) -> dict:
    scoped = interactions[interactions["constituent_id"].isin(pop_ids)].copy()
    scoped["occurred_date"] = pd.to_datetime(scoped["occurred_at"]).dt.date
    return scoped.groupby("constituent_id")["occurred_date"].max().to_dict()


def _opportunity_counts(opportunities: pd.DataFrame) -> dict:
    return opportunities.groupby("constituent_id").size().to_dict()


def _base_evidence(lifetime_amount: float, last_date, action: str, officer_name: str | None, opp_count: int) -> list[str]:
    return [
        f"{format_amount(lifetime_amount)} lifetime giving",
        f"Last interaction recorded {format_date(last_date)}" if last_date else "No interaction is recorded",
        f"Assigned to {officer_name}" if action == RECONNECT else "No fundraiser is assigned",
        f"{opp_count} related opportunit{'y' if opp_count == 1 else 'ies'}",
    ]


def _detect(
    constituents: pd.DataFrame,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
    staff: pd.DataFrame,
    opportunities: pd.DataFrame,
) -> list[Signal]:
    pop = population(constituents).set_index("id", drop=False)
    names = officer_names(staff)
    active_staff_ids = set(staff[staff["active"] == 1]["id"])

    lifetime = _lifetime_giving(gifts, set(pop.index))
    major_donor_ids = lifetime[lifetime >= MAJOR_DONOR_LIFETIME_USD].index

    last_interaction = _last_interaction_dates(interactions, set(pop.index))
    opp_counts = _opportunity_counts(opportunities)

    signals: list[Signal] = []

    for constituent_id in major_donor_ids:
        last_date = last_interaction.get(constituent_id)
        if last_date is not None and last_date >= _GAP_CUTOFF:
            continue

        constituent = pop.loc[constituent_id]
        assigned_staff_id = constituent["assigned_staff_id"]
        is_assigned = not pd.isna(assigned_staff_id) and int(assigned_staff_id) in active_staff_ids
        action = RECONNECT if is_assigned else ASSIGN
        officer_name = assigned_officer_name(assigned_staff_id, names) if is_assigned else None
        opp_count = opp_counts.get(constituent_id, 0)
        lifetime_amount = float(lifetime[constituent_id])

        evidence = _base_evidence(lifetime_amount, last_date, action, officer_name, opp_count)
        if constituent["do_not_solicit"]:
            evidence.append("Do-not-solicit is on file (G1).")

        signals.append(
            Signal(
                entity_type="constituent",
                entity_id=int(constituent_id),
                entity_name=constituent["preferred_name"],
                signal_id=SIGNAL_ID,
                action=action,
                evidence=evidence,
                urgency_amount=lifetime_amount,
                assigned_officer=officer_name,
            )
        )

    return signals


@register
def detect(context: Context) -> list[Signal]:
    return _detect(
        context.constituents,
        context.gifts,
        context.interactions,
        context.staff,
        context.opportunities,
    )
