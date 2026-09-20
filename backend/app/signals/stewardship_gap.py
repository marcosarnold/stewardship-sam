"""SIG1: Stewardship Gap -> THANK.

A recent gift with no subsequent acknowledgement/stewardship interaction
recorded. When a person has multiple recent gifts, the earliest one
establishes when continuous stewardship coverage should have started;
any stewardship touch on or after that date resolves the gap for all of
their recent gifts.
"""

from datetime import timedelta

import pandas as pd

from app.config import AS_OF_DATE, RECENT_GIFT_WINDOW_DAYS, STEWARDSHIP_PURPOSES
from app.formatting import format_amount, format_date
from app.models import Signal
from app.normalize import population, received_gifts

SIGNAL_ID = "SIG1"
ACTION = "THANK"

_WINDOW_START = AS_OF_DATE - timedelta(days=RECENT_GIFT_WINDOW_DAYS)


def _channel_hint(constituent: pd.Series) -> str | None:
    if constituent["email_status"] == "deliverable":
        return "email"
    if constituent["phone_status"] == "available":
        return "phone"
    return None


def detect(
    constituents: pd.DataFrame,
    gifts: pd.DataFrame,
    interactions: pd.DataFrame,
) -> list[Signal]:
    pop = population(constituents).set_index("id", drop=False)

    recv = received_gifts(gifts)
    recv = recv[recv["constituent_id"].isin(pop.index)].copy()
    recv["gift_date"] = pd.to_datetime(recv["gift_date"]).dt.date
    recent = recv[(recv["gift_date"] >= _WINDOW_START) & (recv["gift_date"] <= AS_OF_DATE)]
    if recent.empty:
        return []

    anchor_gifts = recent.sort_values("gift_date").groupby("constituent_id").head(1)
    anchor_gifts = anchor_gifts.set_index("constituent_id")

    steward = interactions[interactions["purpose"].isin(STEWARDSHIP_PURPOSES)].copy()
    steward["occurred_date"] = pd.to_datetime(steward["occurred_at"]).dt.date
    steward_dates: dict[int, list] = (
        steward.groupby("constituent_id")["occurred_date"].apply(list).to_dict()
    )

    signals = []
    for constituent_id, gift in anchor_gifts.iterrows():
        gift_date = gift["gift_date"]
        dates = steward_dates.get(constituent_id, [])
        if any(d >= gift_date for d in dates):
            continue

        constituent = pop.loc[constituent_id]
        signals.append(
            Signal(
                entity_type="constituent",
                entity_id=int(constituent_id),
                entity_name=constituent["preferred_name"],
                signal_id=SIGNAL_ID,
                action=ACTION,
                evidence=[
                    f"{format_amount(gift['amount'])} gift on {format_date(gift_date)}",
                    "No stewardship interaction is recorded since the gift",
                ],
                urgency_date=gift_date.isoformat(),
                urgency_amount=float(gift["amount"]),
                channel_hint=_channel_hint(constituent),
            )
        )

    return signals
