"""Deterministic query executors for each supported Ask Sam intent
(PRD Section 12, Section 13: the LLM never computes results, only
extracts intent -- every answer here comes straight from the existing
engines).
"""

import pandas as pd

from app.config import AS_OF_DATE, MAJOR_DONOR_LIFETIME_USD
from app.context import Context
from app.graph import get_graph
from app.normalize import population, received_gifts
from app.priority_queue import evaluate_signals
from app.relationships import build_relationship
from app.signals.broken_commitment import compute_due_commitments


def _pop_row(pop: pd.DataFrame, constituent_id: int) -> dict | None:
    if constituent_id not in pop.index:
        return None
    return {"entity_id": int(constituent_id), "entity_name": pop.loc[constituent_id, "preferred_name"]}


def followups_query(context: Context) -> dict:
    """AQ1: overdue unresolved commitments and upcoming follow-ups, in
    separate groups; resolved commitments (e.g. Isaac Chen's) are
    included too, so "was it resolved?" can be answered from one call.
    """
    pop = population(context.constituents).set_index("id", drop=False)
    due = compute_due_commitments(context.interactions)

    def _row(item: dict) -> dict | None:
        base = _pop_row(pop, item["constituent_id"])
        if base is None:
            return None
        return {**base, "follow_up_date": item["follow_up_date"].isoformat()}

    overdue = [r for item in due if not item["resolved"] for r in [_row(item)] if r]
    resolved = [r for item in due if item["resolved"] for r in [_row(item)] if r]

    interactions = context.interactions.dropna(subset=["follow_up_date"]).copy()
    interactions["follow_up_date"] = pd.to_datetime(interactions["follow_up_date"]).dt.date
    upcoming_rows = interactions[interactions["follow_up_date"] > AS_OF_DATE]
    upcoming = []
    for _, row in upcoming_rows.iterrows():
        base = _pop_row(pop, row["constituent_id"])
        if base:
            upcoming.append({**base, "follow_up_date": row["follow_up_date"].isoformat()})

    return {"overdue": overdue, "resolved": resolved, "upcoming": upcoming}


def unassigned_major_donors_query(context: Context) -> list[dict]:
    """AQ2: living individuals with lifetime received giving of at least
    MAJOR_DONOR_LIFETIME_USD and no active assigned officer.
    """
    pop = population(context.constituents).set_index("id", drop=False)
    lifetime = received_gifts(context.gifts).groupby("constituent_id")["amount"].sum()
    active_staff_ids = set(context.staff[context.staff["active"] == 1]["id"])

    results = []
    for constituent_id, row in pop.iterrows():
        total = lifetime.get(constituent_id, 0.0)
        if total < MAJOR_DONOR_LIFETIME_USD:
            continue
        assigned = row["assigned_staff_id"]
        unassigned = pd.isna(assigned) or int(assigned) not in active_staff_ids
        if unassigned:
            results.append({"entity_id": int(constituent_id), "entity_name": row["preferred_name"], "lifetime_giving": float(total)})

    return sorted(results, key=lambda r: -r["lifetime_giving"])


def do_not_contact_today_query(context: Context) -> dict:
    """AQ4: WAIT items and held-back people, each with its reason."""
    shown, held_back = evaluate_signals(context)

    wait = [
        {"entity_id": s.entity_id, "entity_name": s.entity_name, "reason": s.evidence[0] if s.evidence else None}
        for s in shown
        if s.action == "WAIT"
    ]
    held = [
        {
            "entity_id": item["entity_id"],
            "entity_name": item["entity_name"],
            "reason_code": item["reason_code"],
            "reason": item["reason"],
        }
        for item in held_back
    ]
    return {"wait": wait, "held_back": held}


def resolve_person(name: str, constituents: pd.DataFrame) -> list[dict]:
    """Case-insensitive substring match against the population's
    preferred_name -- deliberately simple; ambiguity is surfaced to the
    user rather than guessed at.
    """
    pop = population(constituents)
    matches = pop[pop["preferred_name"].str.contains(name, case=False, na=False, regex=False)]
    return [{"entity_id": int(row["id"]), "entity_name": row["preferred_name"]} for _, row in matches.iterrows()]


def why_person_query(name: str, context: Context, degrees, activities, affiliations) -> dict:
    """AQ5: resolves a name to a person and returns their current
    evidence-based signals, or an ambiguous/not-found status.
    """
    matches = resolve_person(name, context.constituents)
    if len(matches) == 0:
        return {"status": "not_found", "matches": []}
    if len(matches) > 1:
        return {"status": "ambiguous", "matches": matches}

    entity_id = matches[0]["entity_id"]
    page = build_relationship(entity_id, context, degrees, activities, affiliations)
    return {
        "status": "found",
        "entity_id": entity_id,
        "entity_name": page["entity_name"],
        "recommended_action": page["recommended_action"],
        "signals": page["signals"],
    }


def cooling_communities_query(context: Context) -> list[dict]:
    """AQ3: the same SIG6 cooling list Today uses, ordered by decline
    ratio (worst first) with metrics attached, each linking to its
    Community View.
    """
    from app.community_metrics import compute_all_metrics
    from app.db import load_table
    from app.signals.community_cooling import detect as detect_cooling

    graph = get_graph()
    cooling_signals = detect_cooling(context)
    metrics = compute_all_metrics(graph, context.gifts, context.interactions, load_table("event_attendance"), context.staff)

    results = [
        {
            "community_id": s.entity_id,
            "community_name": s.entity_name,
            "action": s.action,
            "evidence": s.evidence,
            "historical_giving_rate": metrics[s.entity_id]["historical_giving_rate"],
            "recent_giving_rate": metrics[s.entity_id]["recent_giving_rate"],
            "recent_to_historical_ratio": metrics[s.entity_id]["recent_to_historical_ratio"],
        }
        for s in cooling_signals
    ]
    results.sort(key=lambda r: r["recent_to_historical_ratio"] if r["recent_to_historical_ratio"] is not None else 1.0)
    return results


def location_activity_query(city: str, activity_type: str, context: Context) -> dict:
    """AQ6: population members in `city` who belong (via the graph's
    participated_in edges) to at least one community of `activity_type`
    -- graph membership, not just a table filter, proving Sam can query
    the graph, not only tables. Communities listed are shared
    institutional context, not a claim of friendship (G5).
    """
    from app.db import load_table

    pop = population(context.constituents)
    city_matches = pop[pop["city"].str.lower() == city.lower()]
    if city_matches.empty:
        return {"status": "no_location_matches", "people": []}

    activities_table = load_table("activities")
    type_names = set(
        activities_table[activities_table["activity_type"].str.lower() == activity_type.lower()]["activity_name"]
    )
    if not type_names:
        return {"status": "no_location_matches", "people": []}

    graph = get_graph()
    people = []
    for _, row in city_matches.iterrows():
        node = f"constituent:{row['id']}"
        if node not in graph:
            continue
        spans = sorted(
            graph.nodes[target]["name"]
            for _, target, data in graph.out_edges(node, data=True)
            if data["type"] == "participated_in" and graph.nodes[target]["name"] in type_names
        )
        if spans:
            people.append({"entity_id": int(row["id"]), "entity_name": row["preferred_name"], "communities": spans})

    if not people:
        return {"status": "no_location_matches", "people": []}
    return {"status": "found", "people": people}
