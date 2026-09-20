"""SIG6: Community Cooling -> RECONNECT / INVITE / ADVOCATE.

Frozen rule (PRD Appendix A): among eligible communities (>=
COMMUNITY_MIN_MEMBERS population members), a community is cooling when
its historical giving rate is at or above the median across eligible
communities AND its recent-to-historical giving ratio is at or below
the 25th percentile across eligible communities. Action defaults to
RECONNECT; INVITE when an upcoming event exists; ADVOCATE waits for
connector analysis (issues/012), so it never fires yet.

The dataset has no event-to-activity link, so "an upcoming event
exists" is read institution-wide (any event with starts_at after
AS_OF_DATE) rather than per-community -- a documented, pragmatic
reading given the data (G4: show the data's real limits, don't invent
a link the schema doesn't have).

Wording note (PRD Section 3 caveat): cooling is a descriptive
association between historical and recent giving, not a causal claim
about why a community's engagement changed.
"""

import pandas as pd

from app.communities import list_communities
from app.community_metrics import compute_all_metrics
from app.config import AS_OF_DATE
from app.context import Context
from app.db import load_table
from app.graph import get_graph
from app.models import Signal
from app.registry import register

SIGNAL_ID = "SIG6"


def _pct(rate: float) -> str:
    return f"{round(rate * 100)}%"


def _has_upcoming_event(events: pd.DataFrame) -> bool:
    starts = pd.to_datetime(events["starts_at"]).dt.date
    return bool((starts > AS_OF_DATE).any())


def _detect(context: Context, events: pd.DataFrame, event_attendance: pd.DataFrame) -> list[Signal]:
    graph = get_graph()
    communities = [c for c in list_communities(graph) if c["eligible"]]
    if not communities:
        return []

    metrics = compute_all_metrics(graph, context.gifts, context.interactions, event_attendance, context.staff)

    historical_rates = pd.Series([metrics[c["id"]]["historical_giving_rate"] for c in communities])
    ratios = pd.Series([metrics[c["id"]]["recent_to_historical_ratio"] or 0.0 for c in communities])
    median_historical = historical_rates.median()
    ratio_25th = ratios.quantile(0.25)

    upcoming_event = _has_upcoming_event(events)

    signals = []
    for community in communities:
        m = metrics[community["id"]]
        ratio = m["recent_to_historical_ratio"] or 0.0
        if m["historical_giving_rate"] < median_historical or ratio > ratio_25th:
            continue

        action = "INVITE" if upcoming_event else "RECONNECT"
        signals.append(
            Signal(
                entity_type="community",
                entity_id=community["id"],
                entity_name=community["name"],
                signal_id=SIGNAL_ID,
                action=action,
                evidence=[
                    f"{_pct(m['historical_giving_rate'])} ever gave -> {_pct(m['recent_giving_rate'])} gave in the past year",
                    f"{_pct(m['recent_interaction_rate'])} had an interaction in the last two years",
                ],
                urgency_amount=float(m["member_count"]),
            )
        )
    return signals


@register
def detect(context: Context) -> list[Signal]:
    return _detect(context, load_table("events"), load_table("event_attendance"))
