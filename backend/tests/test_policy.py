from datetime import timedelta

from app.config import (
    AS_OF_DATE,
    CONTACT_PRESSURE_MIN_OUTBOUND,
    CONTACT_PRESSURE_WINDOW_DAYS,
    RECENT_CONTACT_SUPPRESSION_DAYS,
)
from app.policy import ALLOWED, SUPPRESSED, WAIT, evaluate_contact


def _constituent(**overrides):
    base = {
        "deceased": False,
        "do_not_solicit": False,
        "phone_status": "available",
        "email_status": "deliverable",
        "outbound_dates": [],
        "has_scheduled_future_interaction": False,
    }
    base.update(overrides)
    return base


def test_deceased_blocks_any_outreach():
    decision = evaluate_contact(_constituent(deceased=True), "THANK", "email")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "deceased"
    assert decision.reason


def test_do_not_solicit_blocks_ask():
    decision = evaluate_contact(_constituent(do_not_solicit=True), "ASK", "email")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "do_not_solicit"


def test_do_not_solicit_does_not_block_thank():
    decision = evaluate_contact(_constituent(do_not_solicit=True), "THANK", "email")

    assert decision.status == ALLOWED


def test_do_not_call_blocks_phone_channel():
    decision = evaluate_contact(_constituent(phone_status="do_not_call"), "THANK", "phone")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "do_not_call"


def test_inactive_email_blocks_email_channel():
    decision = evaluate_contact(_constituent(email_status="inactive"), "THANK", "email")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "email_unavailable"


def test_missing_email_blocks_email_channel():
    decision = evaluate_contact(_constituent(email_status="missing"), "THANK", "email")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "email_unavailable"


def test_text_channel_is_always_unsupported():
    decision = evaluate_contact(_constituent(), "THANK", "text")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "text_unsupported"


def test_recent_contact_within_14_days_suppresses_thank():
    recent_date = AS_OF_DATE - timedelta(days=RECENT_CONTACT_SUPPRESSION_DAYS)
    decision = evaluate_contact(_constituent(outbound_dates=[recent_date]), "THANK", "email")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "recent_contact"


def test_contact_15_days_ago_does_not_suppress_thank():
    older_date = AS_OF_DATE - timedelta(days=RECENT_CONTACT_SUPPRESSION_DAYS + 1)
    decision = evaluate_contact(_constituent(outbound_dates=[older_date]), "THANK", "email")

    assert decision.status == ALLOWED


def test_overdue_follow_up_is_exempt_from_14_day_suppression():
    recent_date = AS_OF_DATE - timedelta(days=1)
    decision = evaluate_contact(_constituent(outbound_dates=[recent_date]), "FOLLOW UP", "email")

    assert decision.status == ALLOWED


def test_exactly_3_outbound_in_exactly_60_days_triggers_wait():
    boundary_date = AS_OF_DATE - timedelta(days=CONTACT_PRESSURE_WINDOW_DAYS)
    dates = [boundary_date] * CONTACT_PRESSURE_MIN_OUTBOUND
    decision = evaluate_contact(_constituent(outbound_dates=dates), "THANK", "email")

    assert decision.status == WAIT
    assert decision.reason_code == "contact_pressure"


def test_only_2_outbound_in_60_days_does_not_trigger_wait():
    boundary_date = AS_OF_DATE - timedelta(days=CONTACT_PRESSURE_WINDOW_DAYS)
    decision = evaluate_contact(_constituent(outbound_dates=[boundary_date, boundary_date]), "THANK", "email")

    assert decision.status == ALLOWED


def test_contact_61_days_ago_is_outside_the_pressure_window():
    outside_date = AS_OF_DATE - timedelta(days=CONTACT_PRESSURE_WINDOW_DAYS + 1)
    dates = [outside_date] * CONTACT_PRESSURE_MIN_OUTBOUND
    decision = evaluate_contact(_constituent(outbound_dates=dates), "THANK", "email")

    assert decision.status == ALLOWED


def test_every_suppressed_or_wait_decision_has_a_reason_code_and_text():
    scenarios = [
        evaluate_contact(_constituent(deceased=True), "THANK", "email"),
        evaluate_contact(_constituent(do_not_solicit=True), "ASK", "email"),
        evaluate_contact(_constituent(phone_status="do_not_call"), "THANK", "phone"),
        evaluate_contact(_constituent(email_status="missing"), "THANK", "email"),
        evaluate_contact(_constituent(), "THANK", "text"),
        evaluate_contact(
            _constituent(outbound_dates=[AS_OF_DATE - timedelta(days=1)]), "THANK", "email"
        ),
        evaluate_contact(
            _constituent(outbound_dates=[AS_OF_DATE] * CONTACT_PRESSURE_MIN_OUTBOUND),
            "THANK",
            "email",
        ),
        evaluate_contact(_constituent(has_scheduled_future_interaction=True), "THANK", "email"),
    ]

    for decision in scenarios:
        assert decision.status in (SUPPRESSED, WAIT)
        assert decision.reason_code
        assert decision.reason
