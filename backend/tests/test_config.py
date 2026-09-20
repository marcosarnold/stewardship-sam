from datetime import date

from app import config


def test_as_of_date_is_frozen_and_not_the_system_clock():
    assert config.AS_OF_DATE == date(2026, 8, 31)
    assert isinstance(config.AS_OF_DATE, date)


def test_appendix_a_constants_are_present():
    assert config.RECENT_GIFT_WINDOW_DAYS == 365
    assert config.STEWARDSHIP_PURPOSES == ("acknowledgement", "stewardship")
    assert config.RECEIVED_GIFT_STATUS == "paid"
    assert config.EXCLUDED_GIFT_TYPE == "recurring_parent"
    assert config.POPULATION_ENTITY_TYPE == "individual"
    assert config.TODAY_QUEUE_MAX_ITEMS == 15
