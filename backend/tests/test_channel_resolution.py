from app.channel_resolution import channel_note, resolve_channel


def _facts(**overrides):
    base = {
        "deceased": False,
        "do_not_solicit": False,
        "phone_status": "missing",
        "email_status": "inactive",
        "outbound_dates": [],
        "has_scheduled_future_interaction": False,
    }
    base.update(overrides)
    return base


def test_no_viable_channel_note_never_says_none_is_the_allowed_channel():
    decision, rejected = resolve_channel(_facts(), "THANK")

    assert decision.allowed_channel is None
    notes = channel_note(decision.allowed_channel, rejected)

    assert notes  # both channels were rejected, so there is something to say
    for note in notes:
        assert "none is the allowed channel" not in note.lower()
        assert "no channel is currently available" in note.lower()


def test_viable_channel_note_names_it():
    decision, rejected = resolve_channel(_facts(phone_status="do_not_call", email_status="deliverable"), "THANK")

    assert decision.allowed_channel == "email"
    notes = channel_note(decision.allowed_channel, rejected)

    assert notes == ["Phone is marked do-not-call; email is the allowed channel"]
