"""Picks the allowed contact channel for a proposed action (G1, G2).

Shared by every detector that needs to recommend a channel: tries each
channel in CHANNEL_PREFERENCE, and reports any other channel's
restriction as supporting evidence even when it wasn't the blocker
(e.g. "email is inactive" is worth surfacing even when phone already
succeeded as the first choice).
"""

from app.policy import ALLOWED, ContactDecision, evaluate_contact

# Phone is the more personal channel for a thank-you or follow-up; fall
# back to email when it is unavailable or restricted (PRD Section 7).
CHANNEL_PREFERENCE = ("phone", "email")

CHANNEL_SPECIFIC_REASONS = frozenset(
    {"do_not_call", "phone_unavailable", "do_not_email", "email_unavailable", "text_unsupported"}
)


def resolve_channel(facts: dict, action: str) -> tuple[ContactDecision, list[tuple[str, ContactDecision]]]:
    """Returns (decision, other_channel_notes).

    `decision` is the best available channel's ContactDecision (or the
    base, channel-less decision when no channel is viable). Any
    non-channel-specific suppression/wait (recent contact, contact
    pressure, do-not-solicit, deceased, ...) short-circuits immediately
    since it applies no matter which channel would have been used.
    `other_channel_notes` lists every channel that was NOT chosen along
    with why it isn't viable, for evidence text -- even channels that
    were never "in the way" of the chosen one.
    """
    results = {channel: evaluate_contact(facts, action, channel) for channel in CHANNEL_PREFERENCE}

    for decision in results.values():
        if decision.status != ALLOWED and decision.reason_code not in CHANNEL_SPECIFIC_REASONS:
            return decision, []

    chosen = next((results[c] for c in CHANNEL_PREFERENCE if results[c].status == ALLOWED), None)

    if chosen is None:
        base = evaluate_contact(facts, action, None)
        notes = [(c, d) for c, d in results.items() if d.status != ALLOWED]
        return base, notes

    notes = [(c, d) for c, d in results.items() if c != chosen.allowed_channel and d.status != ALLOWED]
    return chosen, notes


def channel_note(allowed_channel: str | None, rejected: list[tuple[str, ContactDecision]]) -> list[str]:
    """Evidence lines explaining why a non-chosen channel wasn't used."""
    lines = []
    for _, rejection in rejected:
        reason_text = rejection.reason.rstrip(".") if rejection.reason else "Not viable"
        if allowed_channel:
            lines.append(f"{reason_text}; {allowed_channel} is the allowed channel")
        else:
            lines.append(f"{reason_text}; no channel is currently available")
    return lines
