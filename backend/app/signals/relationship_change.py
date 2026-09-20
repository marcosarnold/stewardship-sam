"""SIG4: Relationship Change -> RECONNECT / INVITE.

A change is recent when it falls within RELATIONSHIP_CHANGE_WINDOW_DAYS
of AS_OF_DATE: a new career_history role, event attendance, a changed
affiliation, or a new opportunity. A new gift alone is deliberately
excluded as a trigger -- that is SIG1's job (THANK), and counting it
here too would duplicate the same fact as two separate recommendations.

Affiliations only carry a start_year (no exact date), so "recent" for
that type is approximated as starting in AS_OF_DATE's calendar year --
a documented, coarser reading than the day-level precision available
for the other three types.

Evidence is a neutral fact ("Started as ... at ... in June"), never a
reason tied to wealth, capacity, or likelihood to give (G6). This
signal never recommends ASK.
"""

from datetime import timedelta

import pandas as pd

from app.config import AS_OF_DATE, RELATIONSHIP_CHANGE_WINDOW_DAYS
from app.context import Context
from app.db import load_table
from app.models import Signal
from app.normalize import population
from app.registry import register

SIGNAL_ID = "SIG4"
RECONNECT = "RECONNECT"
INVITE = "INVITE"

_WINDOW_START = AS_OF_DATE - timedelta(days=RELATIONSHIP_CHANGE_WINDOW_DAYS)


def _month_name(value) -> str:
    return value.strftime("%B")


def _career_evidence(pop_ids: set, career_history: pd.DataFrame) -> dict[int, str]:
    rows = career_history[career_history["constituent_id"].isin(pop_ids)].copy()
    rows["started_at"] = pd.to_datetime(rows["started_at"]).dt.date
    recent = rows[(rows["started_at"] >= _WINDOW_START) & (rows["started_at"] <= AS_OF_DATE)]

    evidence: dict[int, str] = {}
    for _, row in recent.sort_values("started_at").iterrows():
        job_title = row["job_title"] if isinstance(row["job_title"], str) and row["job_title"] else None
        month = _month_name(row["started_at"])
        headline = f"Started as {job_title} at {row['employer']} in {month}" if job_title else f"Started at {row['employer']} in {month}"
        evidence[int(row["constituent_id"])] = headline
    return evidence


def _event_evidence(pop_ids: set, event_attendance: pd.DataFrame, events: pd.DataFrame) -> dict[int, str]:
    rows = event_attendance[event_attendance["constituent_id"].isin(pop_ids)].copy()
    rows["attended_at"] = pd.to_datetime(rows["attended_at"]).dt.date
    recent = rows[(rows["attended_at"] >= _WINDOW_START) & (rows["attended_at"] <= AS_OF_DATE)]
    joined = recent.merge(events, left_on="event_id", right_on="id", suffixes=("", "_event"))

    evidence: dict[int, str] = {}
    for _, row in joined.sort_values("attended_at").iterrows():
        month = _month_name(row["attended_at"])
        evidence[int(row["constituent_id"])] = f"Attended {row['name']} in {month}"
    return evidence


def _affiliation_evidence(pop_ids: set, affiliations: pd.DataFrame) -> dict[int, str]:
    rows = affiliations[affiliations["constituent_id"].isin(pop_ids)]
    recent = rows[rows["start_year"] == AS_OF_DATE.year]

    evidence: dict[int, str] = {}
    for _, row in recent.iterrows():
        evidence[int(row["constituent_id"])] = f"New affiliation: {row['raw_affiliation_value']} ({AS_OF_DATE.year})"
    return evidence


def _opportunity_evidence(pop_ids: set, opportunities: pd.DataFrame) -> dict[int, str]:
    if "expected_ask_date" not in opportunities.columns:
        return {}
    rows = opportunities[opportunities["constituent_id"].isin(pop_ids)].copy()
    rows["expected_ask_date"] = pd.to_datetime(rows["expected_ask_date"]).dt.date
    recent = rows[(rows["expected_ask_date"] >= _WINDOW_START) & (rows["expected_ask_date"] <= AS_OF_DATE)]

    evidence: dict[int, str] = {}
    for _, row in recent.sort_values("expected_ask_date").iterrows():
        month = _month_name(row["expected_ask_date"])
        evidence[int(row["constituent_id"])] = f"New fundraising opportunity opened in {month}"
    return evidence


def _has_upcoming_event(events: pd.DataFrame) -> bool:
    starts = pd.to_datetime(events["starts_at"]).dt.date
    return bool((starts > AS_OF_DATE).any())


def _detect(context: Context, career_history: pd.DataFrame, event_attendance: pd.DataFrame, events: pd.DataFrame, affiliations: pd.DataFrame) -> list[Signal]:
    pop = population(context.constituents).set_index("id", drop=False)
    pop_ids = set(pop.index)

    by_type = [
        _career_evidence(pop_ids, career_history),
        _event_evidence(pop_ids, event_attendance, events),
        _affiliation_evidence(pop_ids, affiliations),
        _opportunity_evidence(pop_ids, context.opportunities),
    ]

    changed_ids = set().union(*(d.keys() for d in by_type))
    if not changed_ids:
        return []

    upcoming_event = _has_upcoming_event(events)
    action = INVITE if upcoming_event else RECONNECT

    signals = []
    for constituent_id in changed_ids:
        constituent = pop.loc[constituent_id]
        evidence = [d[constituent_id] for d in by_type if constituent_id in d][:3]
        signals.append(
            Signal(
                entity_type="constituent",
                entity_id=int(constituent_id),
                entity_name=constituent["preferred_name"],
                signal_id=SIGNAL_ID,
                action=action,
                evidence=evidence,
            )
        )
    return signals


@register
def detect(context: Context) -> list[Signal]:
    return _detect(
        context,
        load_table("career_history"),
        load_table("event_attendance"),
        load_table("events"),
        load_table("affiliations"),
    )
