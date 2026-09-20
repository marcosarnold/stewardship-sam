"""Summarizes raw interaction rows into the plain facts `evaluate_contact` needs."""

import pandas as pd

from app.config import AS_OF_DATE


def outbound_dates_by_constituent(interactions: pd.DataFrame) -> dict[int, list]:
    outbound = interactions[interactions["direction"] == "outbound"].copy()
    outbound["occurred_date"] = pd.to_datetime(outbound["occurred_at"]).dt.date
    return outbound.groupby("constituent_id")["occurred_date"].apply(list).to_dict()


def scheduled_future_interaction_ids(interactions: pd.DataFrame) -> set[int]:
    with_follow_up = interactions.dropna(subset=["follow_up_date"]).copy()
    with_follow_up["follow_up_date"] = pd.to_datetime(with_follow_up["follow_up_date"]).dt.date
    future = with_follow_up[with_follow_up["follow_up_date"] > AS_OF_DATE]
    return set(future["constituent_id"])
