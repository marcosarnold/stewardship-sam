"""Builds GET /api/community/:id (UX3 header, why, explore members).

Wording note (PRD Section 3 caveat, G5): a cooling association is
descriptive, not causal -- Sam never claims to know why a community's
giving slowed, only that historical and recent giving diverge.
"""

from collections import Counter

import networkx as nx
import pandas as pd

from app.communities import find_community, members
from app.community_metrics import compute_all_metrics
from app.context import Context
from app.priority_queue import evaluate_signals

WORDING_NOTE = "This association is descriptive, not causal: Sam observes that recent giving has diverged from historical giving, not why."


def build_community_view(
    graph: nx.MultiDiGraph,
    community_id: str,
    context: Context,
    event_attendance: pd.DataFrame,
    cooling_signals: list,
) -> dict | None:
    community = find_community(graph, community_id)
    if community is None:
        return None

    all_metrics = compute_all_metrics(graph, context.gifts, context.interactions, event_attendance, context.staff)
    metrics = all_metrics[community_id]

    cooling = next((s for s in cooling_signals if s.entity_id == community_id), None)
    recommended_action = cooling.action if cooling else None
    why_surfaced = cooling.evidence if cooling else []

    member_rows = members(graph, community["name"])
    member_ids = {m["entity_id"] for m in member_rows}

    shown, _held_back = evaluate_signals(context)
    signal_counts = Counter(s.entity_id for s in shown if s.entity_id in member_ids)

    explore_members = sorted(
        (
            {"entity_id": m["entity_id"], "entity_name": m["entity_name"], "signal_count": signal_counts.get(m["entity_id"], 0)}
            for m in member_rows
        ),
        key=lambda m: (-m["signal_count"], m["entity_name"]),
    )

    return {
        "id": community_id,
        "name": community["name"],
        "member_count": metrics["member_count"],
        "historical_giving_rate": metrics["historical_giving_rate"],
        "recent_giving_rate": metrics["recent_giving_rate"],
        "recent_interaction_rate": metrics["recent_interaction_rate"],
        "recommended_action": recommended_action,
        "why_surfaced": why_surfaced,
        "explore_members": explore_members,
        "wording_note": WORDING_NOTE,
    }
