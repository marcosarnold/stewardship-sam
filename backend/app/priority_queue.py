"""Merges every registered signal into one prioritized Today queue (UX1).

Every signal (except WAIT and ASSIGN, which are policy-exempt: WAIT
already means "don't contact", ASSIGN is an internal, non-donor-facing
action) passes through evaluate_contact exactly once, here -- no
detector applies contact policy itself. Suppressed signals move to
held_back.

Signals are then merged per person into one queue item: an explicit
WAIT signal always wins as that person's primary action (contact-
pressure restraint overrides everything); otherwise the
highest-priority remaining signal becomes primary and the rest attach
as supporting evidence.

Ranking is a fixed, documented, deterministic ordering (PRD Section
10): a bucket per action (matching the PRD's own demo narrative
sequence -- broken promise, stewardship, restraint, then relationship
ownership), then a per-bucket urgency factor, then entity_id as a
final tie-breaker. This produces an internal sort key for ordering
only; it is never included in an API response field meant for display.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from app import signals as _signals  # noqa: F401  -- side effect: registers every detector
from app.channel_resolution import channel_note, resolve_channel
from app.context import Context
from app.dismissals import get_dismissal
from app.interaction_facts import outbound_dates_by_constituent, scheduled_future_interaction_ids
from app.models import Signal
from app.policy import ALLOWED
from app.registry import all_signals
from app.relationship_memory import not_currently_interested

# WAIT already means "don't contact"; ASSIGN is internal (issue 004).
POLICY_EXEMPT_ACTIONS = frozenset({"WAIT", "ASSIGN"})

# Bucket order, most urgent first. FOLLOW UP always leads: it is an
# explicit existing promise (SIG2 rule, PRD Section 7). WAIT comes next,
# ahead of THANK, even though far fewer people are ever in it -- contact
# -pressure restraint (SC8) must never be crowded out of the display cap
# by THANK's much larger pool, which is exactly what a naive
# type-then-dollar-amount sort would do. RECONNECT/ASSIGN rank last:
# these relationships have already gone quiet for a long time (SIG3's
# 730-day-or-ever gap), so one more day of display priority costs little.
# INVITE/ADVOCATE (SIG6, community-level) share RECONNECT's tier: same
# underlying "gone quiet" story, just at the community level.
ACTION_BUCKET = {"FOLLOW UP": 0, "WAIT": 1, "THANK": 2, "RECONNECT": 3, "INVITE": 3, "ADVOCATE": 3, "ASSIGN": 4}

RANKING_FACTOR = {
    "FOLLOW UP": "Promised follow-up is overdue",
    "THANK": "Recent gift has no recorded stewardship",
    "WAIT": "Recent contact pressure suggests restraint",
    "RECONNECT": "Relationship has gone quiet",
    "INVITE": "Community giving is cooling relative to its history",
    "ADVOCATE": "Community giving is cooling relative to its history",
    "ASSIGN": "Major donor has no assigned fundraiser",
}

# Communities have no individual contact facts (phone/email status,
# do-not-solicit, ...) -- contact policy doesn't apply at that level, so
# their signals skip evaluate_contact entirely, like WAIT and ASSIGN.
COMMUNITY_ENTITY_TYPE = "community"


@dataclass
class QueueItem:
    entity_type: str
    entity_id: int
    entity_name: str
    action: str
    evidence: list[str]
    channel_hint: str | None
    assigned_officer: str | None
    ranking_factor: str
    supporting_signals: list[dict] = field(default_factory=list)
    dismissed: bool = False
    dismiss_reason: str | None = None
    sort_key: tuple = field(default=(), repr=False, compare=False)
    assigned_staff_id: float | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "action": self.action,
            "evidence": self.evidence,
            "channel_hint": self.channel_hint,
            "assigned_officer": self.assigned_officer,
            "ranking_factor": self.ranking_factor,
            "supporting_signals": self.supporting_signals,
            "dismissed": self.dismissed,
            "dismiss_reason": self.dismiss_reason,
        }


def _secondary_rank(signal: Signal) -> float:
    """Higher = more urgent, within a signal's own action bucket."""
    if signal.action == "FOLLOW UP":
        return -(signal.urgency_days or 0)
    if signal.action == "WAIT":
        if signal.urgency_date:
            return -date.fromisoformat(signal.urgency_date).toordinal()
        return 0
    # THANK, RECONNECT, ASSIGN: dollar magnitude (relationship history).
    return -(signal.urgency_amount or 0)


def _sort_key(signal: Signal) -> tuple:
    # entity_id is an int for constituents, a string slug for communities;
    # str() keeps the tie-breaker comparable across both instead of
    # raising when a person and a community land in the same bucket/rank.
    return (ACTION_BUCKET.get(signal.action, 99), _secondary_rank(signal), str(signal.entity_id))


def _facts_for(entity_id: int, pop: pd.DataFrame, outbound_dates: dict, scheduled_ids: set) -> dict:
    row = pop.loc[entity_id]
    return {
        "deceased": bool(row["deceased"]),
        "do_not_solicit": bool(row["do_not_solicit"]),
        "phone_status": row["phone_status"],
        "email_status": row["email_status"],
        "outbound_dates": outbound_dates.get(entity_id, []),
        "has_scheduled_future_interaction": entity_id in scheduled_ids,
        "not_currently_interested": not_currently_interested(entity_id),
    }


def evaluate_signals(context: Context) -> tuple[list[Signal], list[dict]]:
    """Every registered detector's raw signals, each routed through
    evaluate_contact once. Returns (shown, held_back); WAIT and ASSIGN
    signals are always in `shown` (policy-exempt).
    """
    raw_signals = all_signals(context)

    pop = context.constituents.set_index("id", drop=False)
    outbound_dates = outbound_dates_by_constituent(context.interactions)
    scheduled_ids = scheduled_future_interaction_ids(context.interactions)

    shown: list[Signal] = []
    held_back: list[dict] = []

    for signal in raw_signals:
        if signal.action in POLICY_EXEMPT_ACTIONS or signal.entity_type == COMMUNITY_ENTITY_TYPE:
            shown.append(signal)
            continue

        facts = _facts_for(signal.entity_id, pop, outbound_dates, scheduled_ids)
        decision, rejected = resolve_channel(facts, signal.action)

        if decision.status != ALLOWED:
            held_back.append(
                {
                    "entity_type": signal.entity_type,
                    "entity_id": signal.entity_id,
                    "entity_name": signal.entity_name,
                    "action": signal.action,
                    "evidence": signal.evidence,
                    "reason_code": decision.reason_code,
                    "reason": decision.reason,
                }
            )
            continue

        signal.channel_hint = decision.allowed_channel
        signal.evidence = (signal.evidence + channel_note(decision.allowed_channel, rejected))[:3]
        shown.append(signal)

    return shown, held_back


def merge_per_person(shown: list[Signal]) -> list[QueueItem]:
    by_entity: dict[int, list[Signal]] = {}
    for signal in shown:
        by_entity.setdefault(signal.entity_id, []).append(signal)

    items = []
    for signals in by_entity.values():
        wait_signals = [s for s in signals if s.action == "WAIT"]
        primary = wait_signals[0] if wait_signals else min(signals, key=_sort_key)
        others = [s for s in signals if s is not primary]

        items.append(
            QueueItem(
                entity_type=primary.entity_type,
                entity_id=primary.entity_id,
                entity_name=primary.entity_name,
                action=primary.action,
                evidence=primary.evidence,
                channel_hint=primary.channel_hint,
                assigned_officer=primary.assigned_officer,
                ranking_factor=RANKING_FACTOR.get(primary.action, primary.action),
                supporting_signals=[{"action": s.action, "evidence": s.evidence} for s in others],
                sort_key=_sort_key(primary),
            )
        )

    return items


def build_queue(context: Context) -> tuple[list[QueueItem], list[dict]]:
    shown, held_back = evaluate_signals(context)
    items = merge_per_person(shown)

    pop = context.constituents.set_index("id", drop=False)
    for item in items:
        if item.entity_type != COMMUNITY_ENTITY_TYPE:
            item.assigned_staff_id = pop.loc[item.entity_id]["assigned_staff_id"]
        record = get_dismissal(item.entity_id)
        if record:
            item.dismissed = True
            item.dismiss_reason = record.get("reason")

    items.sort(key=lambda item: item.sort_key)
    return items, held_back


def summarize_held_back(held_back: list[dict]) -> dict:
    counts = Counter(item["reason_code"] for item in held_back)
    return {
        "reasons": [{"reason_code": code, "count": count} for code, count in counts.most_common()],
        "items": held_back,
    }


def summarize_counts(items: list[QueueItem]) -> dict[str, int]:
    return dict(Counter(item.action for item in items))
