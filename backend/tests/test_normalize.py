import pandas as pd

from app.normalize import population, received_gifts


def test_population_keeps_only_non_deceased_individuals():
    constituents = pd.DataFrame(
        [
            {"id": 1, "entity_type": "individual", "deceased": 0},
            {"id": 2, "entity_type": "individual", "deceased": 1},
            {"id": 3, "entity_type": "organization", "deceased": 0},
        ]
    )

    result = population(constituents)

    assert list(result["id"]) == [1]


def test_received_gifts_keeps_only_paid_non_recurring_parent_gifts():
    gifts = pd.DataFrame(
        [
            {"id": 1, "status": "paid", "gift_type": "one_time"},
            {"id": 2, "status": "pledged", "gift_type": "one_time"},
            {"id": 3, "status": "paid", "gift_type": "recurring_parent"},
            {"id": 4, "status": "paid", "gift_type": "installment"},
        ]
    )

    result = received_gifts(gifts)

    assert sorted(result["id"]) == [1, 4]
