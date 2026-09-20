"""Builds the Today queue: applies the contact policy to raw signals.

Suppressed THANK signals move to a "held back" list with reasons
instead of appearing on Today (G1, G2). WAIT signals (SIG5) are added
to Today directly; contact pressure already is the reason they surface.
"""

from collections import Counter

import pandas as pd

from app.channel_resolution import channel_note, resolve_channel
from app.interaction_facts import outbound_dates_by_constituent, scheduled_future_interaction_ids
from app.models import Signal
from app.normalize import population
from app.policy import ALLOWED
from app.signals import contact_pressure, neglected_relationship, stewardship_gap


def _constituent_facts(row: pd.Series, outbound_dates: dict, scheduled_ids: set) -> dict:
    return {
        "deceased": bool(row["deceased"]),
        "do_not_solicit": bool(row["do_not_solicit"]),
        "phone_status": row["phone_status"],
        "email_status": row["email_status"],
        "outbound_dates": outbound_dates.get(row["id"], []),
        "has_scheduled_future_interaction": row["id"] in scheduled_ids,
    }


def _apply_channel_note(signal: Signal, allowed_channel: str, rejected: list) -> None:
    signal.evidence.extend(channel_note(allowed_channel, rejected))
    signal.evidence = signal.evidence[:3]


def build_today_queue(
    constituents: pd.DataFrame,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
    staff: pd.DataFrame,
    opportunities: pd.DataFrame,
) -> tuple[list[Signal], list[dict]]:
    outbound_dates = outbound_dates_by_constituent(interactions)
    scheduled_ids = scheduled_future_interaction_ids(interactions)
    pop = population(constituents).set_index("id", drop=False)

    thank_signals = stewardship_gap.detect(constituents, gifts, interactions)
    wait_signals = contact_pressure.detect(constituents, interactions)
    neglected_items, neglected_held_back = neglected_relationship.detect(
        constituents, gifts, interactions, staff, opportunities
    )

    today_items: list[Signal] = []
    held_back: list[dict] = list(neglected_held_back)

    for signal in thank_signals:
        row = pop.loc[signal.entity_id]
        facts = _constituent_facts(row, outbound_dates, scheduled_ids)
        decision, rejected = resolve_channel(facts, signal.action)

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
    today_items.extend(neglected_items)

    return today_items, held_back


def summarize_held_back(held_back: list[dict]) -> dict:
    counts = Counter(item["reason_code"] for item in held_back)
    return {
        "reasons": [{"reason_code": code, "count": count} for code, count in counts.most_common()],
        "items": held_back,
    }
