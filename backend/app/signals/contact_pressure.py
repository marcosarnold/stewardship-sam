"""SIG5: Contact Pressure -> WAIT.

Someone with CONTACT_PRESSURE_MIN_OUTBOUND or more outbound interactions
within CONTACT_PRESSURE_WINDOW_DAYS should not receive more outreach
right now, regardless of how engaged or high-capacity they are.
"""

import pandas as pd

from app.config import CONTACT_PRESSURE_WINDOW_DAYS
from app.context import Context
from app.formatting import format_date
from app.interaction_facts import outbound_dates_by_constituent
from app.models import Signal
from app.normalize import population
from app.policy import contact_pressure_info
from app.registry import register

SIGNAL_ID = "SIG5"
ACTION = "WAIT"


def _detect(constituents: pd.DataFrame, interactions: pd.DataFrame) -> list[Signal]:
    pop = population(constituents).set_index("id", drop=False)

    scoped_interactions = interactions[interactions["constituent_id"].isin(pop.index)]
    outbound_by_id = outbound_dates_by_constituent(scoped_interactions)

    signals = []
    for constituent_id, dates in outbound_by_id.items():
        fires, count, most_recent = contact_pressure_info(dates)
        if not fires:
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
                    f"{count} outbound interactions in the last {CONTACT_PRESSURE_WINDOW_DAYS} days",
                    f"Most recent: {format_date(most_recent)}",
                ],
                urgency_date=most_recent.isoformat(),
            )
        )

    return signals


@register
def detect(context: Context) -> list[Signal]:
    return _detect(context.constituents, context.interactions)
