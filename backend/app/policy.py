"""Contact policy engine (PRD SIG5, G1, G2).

`evaluate_contact` is a pure function: every interaction-derived fact it
needs is pre-summarized by the caller into the `constituent` mapping, so
this module never touches pandas, the database, or the clock.

Expected `constituent` keys:
    deceased: bool
    do_not_solicit: bool
    phone_status: str   ("available", "do_not_call", "inactive", "missing")
    email_status: str   ("deliverable", "do_not_email", "inactive", "missing")
    outbound_dates: list[date]       -- every outbound interaction date, any purpose
    has_scheduled_future_interaction: bool -- a follow-up already booked after AS_OF_DATE
    not_currently_interested: bool  -- from a confirmed post-call note (issue 018); optional, defaults False
"""

from dataclasses import dataclass
from datetime import date, timedelta

from app.config import (
    AS_OF_DATE,
    CONTACT_PRESSURE_MIN_OUTBOUND,
    CONTACT_PRESSURE_WINDOW_DAYS,
    RECENT_CONTACT_SUPPRESSION_DAYS,
)

SOLICITING_ACTIONS = frozenset({"ASK"})
SUPPRESSIBLE_ACTIONS = frozenset({"THANK", "RECONNECT", "INVITE", "ASK"})

ALLOWED = "allowed"
SUPPRESSED = "suppressed"
WAIT = "wait"


@dataclass(frozen=True)
class ContactDecision:
    status: str  # ALLOWED | SUPPRESSED | WAIT
    reason_code: str | None
    reason: str | None
    allowed_channel: str | None


def _pressure_window_dates(outbound_dates: list[date]) -> list[date]:
    window_start = AS_OF_DATE - timedelta(days=CONTACT_PRESSURE_WINDOW_DAYS)
    return [d for d in outbound_dates if window_start <= d <= AS_OF_DATE]


def contact_pressure_info(outbound_dates: list[date]) -> tuple[bool, int, date | None]:
    """Whether SIG5 contact pressure fires, the count, and the most recent date."""
    window_dates = _pressure_window_dates(outbound_dates)
    fires = len(window_dates) >= CONTACT_PRESSURE_MIN_OUTBOUND
    most_recent = max(window_dates) if window_dates else None
    return fires, len(window_dates), most_recent


def _channel_decision(channel: str, constituent: dict) -> ContactDecision | None:
    """None means the channel is viable; otherwise the suppression to return."""
    if channel == "phone":
        status = constituent["phone_status"]
        if status == "do_not_call":
            return ContactDecision(SUPPRESSED, "do_not_call", "Phone is marked do-not-call.", None)
        if status != "available":
            return ContactDecision(
                SUPPRESSED, "phone_unavailable", f"Phone status is {status}.", None
            )
        return None
    if channel == "email":
        status = constituent["email_status"]
        if status == "do_not_email":
            return ContactDecision(SUPPRESSED, "do_not_email", "Email is marked do-not-email.", None)
        if status != "deliverable":
            return ContactDecision(
                SUPPRESSED, "email_unavailable", f"Email status is {status}.", None
            )
        return None
    if channel == "text":
        return ContactDecision(
            SUPPRESSED, "text_unsupported", "Text is not supported; no phone numbers are on file.", None
        )
    return ContactDecision(SUPPRESSED, "unknown_channel", f"Unknown channel: {channel}.", None)


def evaluate_contact(
    constituent: dict, proposed_action: str, proposed_channel: str | None
) -> ContactDecision:
    if constituent.get("deceased"):
        return ContactDecision(SUPPRESSED, "deceased", "Constituent is recorded as deceased.", None)

    if constituent.get("do_not_solicit") and proposed_action in SOLICITING_ACTIONS:
        return ContactDecision(
            SUPPRESSED, "do_not_solicit", "Constituent has a do-not-solicit restriction.", None
        )

    if constituent.get("not_currently_interested") and proposed_action in SOLICITING_ACTIONS:
        return ContactDecision(
            SUPPRESSED,
            "not_currently_interested",
            "A post-call note recorded that the constituent is not currently interested.",
            None,
        )

    if proposed_channel is not None:
        blocked = _channel_decision(proposed_channel, constituent)
        if blocked is not None:
            return blocked

    outbound_dates = constituent.get("outbound_dates", [])
    fires, count, most_recent = contact_pressure_info(outbound_dates)
    if fires:
        reason = (
            f"{count} outbound interactions in the last {CONTACT_PRESSURE_WINDOW_DAYS} days"
            f" (most recent {most_recent.isoformat()})."
        )
        return ContactDecision(WAIT, "contact_pressure", reason, None)

    if constituent.get("has_scheduled_future_interaction"):
        return ContactDecision(
            WAIT, "scheduled_follow_up", "Another interaction is already scheduled.", None
        )

    if proposed_action in SUPPRESSIBLE_ACTIONS:
        suppression_start = AS_OF_DATE - timedelta(days=RECENT_CONTACT_SUPPRESSION_DAYS)
        recent_outbound = [d for d in outbound_dates if suppression_start <= d <= AS_OF_DATE]
        if recent_outbound:
            most_recent_contact = max(recent_outbound)
            return ContactDecision(
                SUPPRESSED,
                "recent_contact",
                f"An outbound interaction occurred on {most_recent_contact.isoformat()},"
                f" within the last {RECENT_CONTACT_SUPPRESSION_DAYS} days.",
                None,
            )

    return ContactDecision(ALLOWED, None, None, proposed_channel)
