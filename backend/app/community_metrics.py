"""SIG6 input metrics per community (PRD Appendix A, Section 7).

Every metric below is a share of a community's population members
(individual, not deceased -- the same population used for membership
itself). Numerator and denominator are documented per metric and
computed only here; nothing hard-codes a percentage.

| Metric | Numerator | Denominator |
| --- | --- | --- |
| historical_giving_rate | members with >=1 received gift ever | member_count |
| recent_giving_rate | members with a received gift within RECENT_GIVING_WINDOW_DAYS of AS_OF_DATE | member_count |
| recent_to_historical_ratio | recent_giving_rate | historical_giving_rate (None when historical_giving_rate is 0) |
| recent_interaction_rate | members with any interaction within RECENT_ENGAGEMENT_WINDOW_DAYS | member_count |
| historical_event_participation | members who ever attended an event (event data covers Sep 2025-Jun 2026 only) | member_count |
| recent_event_participation | members who attended an event within RECENT_ENGAGEMENT_WINDOW_DAYS | member_count |
| stewardship_coverage | recent donors (received gift within RECENT_GIVING_WINDOW_DAYS) with a stewardship interaction on/after that gift | recent donors |
| assignment_coverage | members with an active assigned officer | member_count |

Event data caveat (G4): events only cover September 2025 to June 2026,
so both event metrics are limited to that window, not "ever" in the
same sense as gifts or interactions.
"""

from datetime import timedelta

import networkx as nx
import pandas as pd

from app.communities import list_communities, members
from app.config import AS_OF_DATE, RECENT_ENGAGEMENT_WINDOW_DAYS, RECENT_GIVING_WINDOW_DAYS, STEWARDSHIP_PURPOSES
from app.normalize import received_gifts
from app.staff_lookup import officer_names

EVENT_DATA_CAVEAT = "Event data covers September 2025 to June 2026 only; event participation metrics are limited to that window."

_RECENT_GIFT_START = AS_OF_DATE - timedelta(days=RECENT_GIVING_WINDOW_DAYS)
_RECENT_ENGAGEMENT_START = AS_OF_DATE - timedelta(days=RECENT_ENGAGEMENT_WINDOW_DAYS)


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def compute_community_metrics(
    graph: nx.MultiDiGraph,
    community_name: str,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
    event_attendance: pd.DataFrame,
    staff: pd.DataFrame,
) -> dict:
    member_rows = members(graph, community_name)
    member_ids = {m["entity_id"] for m in member_rows}
    member_count = len(member_ids)

    recv = received_gifts(gifts)
    recv = recv[recv["constituent_id"].isin(member_ids)].copy()
    recv["gift_date"] = pd.to_datetime(recv["gift_date"]).dt.date
    ever_gave = set(recv["constituent_id"])
    recent_gave = set(recv[(recv["gift_date"] >= _RECENT_GIFT_START) & (recv["gift_date"] <= AS_OF_DATE)]["constituent_id"])

    member_interactions = interactions[interactions["constituent_id"].isin(member_ids)].copy()
    member_interactions["occurred_date"] = pd.to_datetime(member_interactions["occurred_at"]).dt.date
    recent_interaction = set(
        member_interactions[
            (member_interactions["occurred_date"] >= _RECENT_ENGAGEMENT_START)
            & (member_interactions["occurred_date"] <= AS_OF_DATE)
        ]["constituent_id"]
    )

    member_attendance = event_attendance[event_attendance["constituent_id"].isin(member_ids)].copy()
    member_attendance["attended_date"] = pd.to_datetime(member_attendance["attended_at"]).dt.date
    ever_attended = set(member_attendance["constituent_id"])
    recent_attended = set(
        member_attendance[
            (member_attendance["attended_date"] >= _RECENT_ENGAGEMENT_START)
            & (member_attendance["attended_date"] <= AS_OF_DATE)
        ]["constituent_id"]
    )

    steward = interactions[interactions["purpose"].isin(STEWARDSHIP_PURPOSES)].copy()
    steward["occurred_date"] = pd.to_datetime(steward["occurred_at"]).dt.date
    steward_dates: dict[int, list] = steward.groupby("constituent_id")["occurred_date"].apply(list).to_dict()

    recent_donor_gift_date = recv[recv["constituent_id"].isin(recent_gave)].sort_values("gift_date").groupby(
        "constituent_id"
    ).head(1).set_index("constituent_id")["gift_date"]
    stewarded_recent_donors = sum(
        1
        for constituent_id, gift_date in recent_donor_gift_date.items()
        if any(d >= gift_date for d in steward_dates.get(constituent_id, []))
    )

    names = officer_names(staff)
    assigned = 0
    for m in member_rows:
        staff_id = graph.nodes[f"constituent:{m['entity_id']}"]["assigned_staff_id"]
        if not pd.isna(staff_id) and int(staff_id) in names:
            assigned += 1

    historical_giving_rate = _rate(len(ever_gave), member_count)
    recent_giving_rate = _rate(len(recent_gave), member_count)

    return {
        "member_count": member_count,
        "historical_giving_rate": historical_giving_rate,
        "recent_giving_rate": recent_giving_rate,
        "recent_to_historical_ratio": (
            round(recent_giving_rate / historical_giving_rate, 4) if historical_giving_rate else None
        ),
        "recent_interaction_rate": _rate(len(recent_interaction), member_count),
        "historical_event_participation": _rate(len(ever_attended), member_count),
        "recent_event_participation": _rate(len(recent_attended), member_count),
        "stewardship_coverage": _rate(stewarded_recent_donors, len(recent_gave)),
        "assignment_coverage": _rate(assigned, member_count),
        "event_data_caveat": EVENT_DATA_CAVEAT,
    }


_METRICS_CACHE: dict[str, dict] | None = None


def compute_all_metrics(
    graph: nx.MultiDiGraph,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
    event_attendance: pd.DataFrame,
    staff: pd.DataFrame,
    force_rebuild: bool = False,
) -> dict[str, dict]:
    """Metrics for every community, keyed by community id, cached after
    the first computation (issue 010: "compute in under 5 seconds and
    are cached").
    """
    global _METRICS_CACHE
    if _METRICS_CACHE is not None and not force_rebuild:
        return _METRICS_CACHE

    result = {}
    for community in list_communities(graph):
        result[community["id"]] = compute_community_metrics(
            graph, community["name"], gifts, interactions, event_attendance, staff
        )
    _METRICS_CACHE = result
    return result
