"""Population and received-gift normalization (PRD Appendix A)."""

import pandas as pd

from app.config import EXCLUDED_GIFT_TYPE, POPULATION_ENTITY_TYPE, RECEIVED_GIFT_STATUS


def population(constituents: pd.DataFrame) -> pd.DataFrame:
    """Individuals who are not deceased."""
    return constituents[
        (constituents["entity_type"] == POPULATION_ENTITY_TYPE)
        & (constituents["deceased"] == 0)
    ]


def received_gifts(gifts: pd.DataFrame) -> pd.DataFrame:
    """Gifts with status = paid and gift_type != recurring_parent."""
    return gifts[
        (gifts["status"] == RECEIVED_GIFT_STATUS)
        & (gifts["gift_type"] != EXCLUDED_GIFT_TYPE)
    ]
