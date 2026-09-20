"""Builds the Today queue: applies the contact policy to raw signals.

Suppressed THANK signals move to a "held back" list with reasons
instead of appearing on Today (G1, G2). WAIT signals (SIG5) are added
to Today directly; contact pressure already is the reason they surface.
"""

from collections import Counter

import pandas as pd

from app.interaction_facts import outbound_dates_by_constituent, scheduled_future_interaction_ids
from app.models import Signal
from app.normalize import population
from app.policy import ALLOWED, evaluate_contact
from app.signals import contact_pressure, stewardship_gap

# Phone is the more personal channel for a thank-you; fall back to email
# when it is unavailable or restricted (PRD Section 7, SIG1 example).
CHANNEL_PREFERENCE = ("phone", "email")

CHANNEL_SPECIFIC_REASONS = frozenset(
    {"do_not_call", "phone_unavailable", "do_not_email", "email_unavailable", "text_unsupported"}
)
RESTRICTION_REASON_CODES = frozenset({"do_not_call", "do_not_email"})

_CHANNEL_RESTRICTION_LABEL = {
    "do_not_call": "Phone is marked do-not-call",
    "do_not_email": "Email is marked do-not-email",
}


def _constituent_facts(row: pd.Series, outbound_dates: dict, scheduled_ids: set) -> dict:
    return {
        "deceased": bool(row["deceased"]),
        "do_not_solicit": bool(row["do_not_solicit"]),
        "phone_status": row["phone_status"],
        "email_status": row["email_status"],
        "outbound_dates": outbound_dates.get(row["id"], []),
        "has_scheduled_future_interaction": row["id"] in scheduled_ids,
    }


def _resolve_channel(facts: dict, action: str):
    """Try channels in preference order. Returns (decision, rejected_restrictions)."""
    rejected = []
    for channel in CHANNEL_PREFERENCE:
        decision = evaluate_contact(facts, action, channel)
        if decision.status == ALLOWED:
            return decision, rejected
        if decision.reason_code not in CHANNEL_SPECIFIC_REASONS:
            # A non-channel suppression (recent contact, pressure, ...)
            # applies no matter which channel we would have used.
            return decision, rejected
        if decision.reason_code in RESTRICTION_REASON_CODES:
            rejected.append((channel, decision))
    return evaluate_contact(facts, action, None), rejected


def _apply_channel_note(signal: Signal, allowed_channel: str, rejected: list) -> None:
    for _, rejection in rejected:
        label = _CHANNEL_RESTRICTION_LABEL.get(rejection.reason_code)
        if label:
            signal.evidence.append(f"{label}; {allowed_channel} is the allowed channel")
    signal.evidence = signal.evidence[:3]


def build_today_queue(
    constituents: pd.DataFrame, gifts: pd.DataFrame, interactions: pd.DataFrame
) -> tuple[list[Signal], list[dict]]:
    outbound_dates = outbound_dates_by_constituent(interactions)
    scheduled_ids = scheduled_future_interaction_ids(interactions)
    pop = population(constituents).set_index("id", drop=False)

    thank_signals = stewardship_gap.detect(constituents, gifts, interactions)
    wait_signals = contact_pressure.detect(constituents, interactions)

    today_items: list[Signal] = []
    held_back: list[dict] = []

    for signal in thank_signals:
        row = pop.loc[signal.entity_id]
        facts = _constituent_facts(row, outbound_dates, scheduled_ids)
        decision, rejected = _resolve_channel(facts, signal.action)

        if decision.status != ALLOWED:
            held_back.append(
                {
                    "entity_type": signal.entity_type,
                    "entity_id": signal.entity_id,
                    "entity_name": signal.entity_name,
                    "action": signal.action,
                    "reason_code": decision.reason_code,
                    "reason": decision.reason,
                }
            )
            continue

        _apply_channel_note(signal, decision.allowed_channel, rejected)
        signal.channel_hint = decision.allowed_channel
        today_items.append(signal)

    today_items.extend(wait_signals)

    return today_items, held_back


def summarize_held_back(held_back: list[dict]) -> dict:
    counts = Counter(item["reason_code"] for item in held_back)
    return {
        "reasons": [{"reason_code": code, "count": count} for code, count in counts.most_common()],
        "items": held_back,
    }
