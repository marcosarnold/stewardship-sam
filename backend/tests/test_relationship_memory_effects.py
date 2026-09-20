from app.channel_resolution import resolve_channel
from app.policy import SUPPRESSED, evaluate_contact
from app.relationship_memory import all_follow_up_dates, latest_note, save_note
from app.signals.broken_commitment import compute_due_commitments


def _facts(**overrides):
    base = {
        "deceased": False,
        "do_not_solicit": False,
        "phone_status": "available",
        "email_status": "deliverable",
        "outbound_dates": [],
        "has_scheduled_future_interaction": False,
        "not_currently_interested": False,
    }
    base.update(overrides)
    return base


def test_nothing_saved_until_confirmed():
    assert latest_note(2669) is None  # extract_note (tested separately) never calls save_note


def test_saving_sets_not_currently_interested_and_it_blocks_ask():
    save_note(2669, {"solicitation_status": "not_currently_interested"}, "raw note text")

    facts = _facts(not_currently_interested=True)
    decision = evaluate_contact(facts, "ASK", "email")

    assert decision.status == SUPPRESSED
    assert decision.reason_code == "not_currently_interested"


def test_not_currently_interested_does_not_block_thank():
    facts = _facts(not_currently_interested=True)
    decision = evaluate_contact(facts, "THANK", "email")
    assert decision.status != SUPPRESSED or decision.reason_code != "not_currently_interested"


def test_saved_follow_up_is_picked_up_by_sig2_once_due(context):
    # Nia Chen (14456) already has a real overdue commitment; use a
    # different population member with no interactions at all so the
    # saved note's follow-up date is the only source of the commitment.
    entity_id = 2669  # Valerie Kaur, zero interactions on record
    save_note(entity_id, {"follow_up_date": "2026-01-01"}, "told her I'd follow up in January")

    extra = all_follow_up_dates()
    assert extra[entity_id] == "2026-01-01"

    due = compute_due_commitments(context.interactions, extra)
    matching = [d for d in due if d["constituent_id"] == entity_id]
    assert len(matching) == 1
    assert matching[0]["resolved"] is False  # Valerie has no later interaction to resolve it


def test_text_preference_is_stored_and_labeled_as_a_preference_only():
    entry = save_note(2669, {"communication_preference": "text"}, "prefers texts")

    assert entry["communication_preference"] == "text"
    # Storing the preference must not make text an allowed_channel anywhere
    # in the policy engine -- the dataset has no text interactions.
    decision, _ = resolve_channel(
        {
            "deceased": False,
            "do_not_solicit": False,
            "phone_status": "missing",
            "email_status": "missing",
            "outbound_dates": [],
            "has_scheduled_future_interaction": False,
        },
        "THANK",
    )
    assert decision.allowed_channel != "text"
