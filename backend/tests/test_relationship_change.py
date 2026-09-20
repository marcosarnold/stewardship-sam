from app.db import load_table
from app.signals.relationship_change import detect

_BANNED_WORDS = ("wealth", "capacity", "afford", "rich", "likelihood to give")


def test_people_with_a_recent_career_change_surface_with_neutral_evidence(context):
    import datetime

    import pandas as pd

    from app.config import AS_OF_DATE, RELATIONSHIP_CHANGE_WINDOW_DAYS

    signals = detect(context)
    assert len(signals) > 0

    career_history = load_table("career_history").copy()
    career_history["started_at"] = pd.to_datetime(career_history["started_at"]).dt.date
    window_start = AS_OF_DATE - datetime.timedelta(days=RELATIONSHIP_CHANGE_WINDOW_DAYS)
    recent_career_ids = set(
        career_history[
            (career_history["started_at"] >= window_start) & (career_history["started_at"] <= AS_OF_DATE)
        ]["constituent_id"]
    )

    with_career_change = [s for s in signals if s.entity_id in recent_career_ids]
    assert len(with_career_change) > 0
    for s in with_career_change:
        assert any(e.startswith("Started") for e in s.evidence)


def test_never_produces_ask_and_evidence_never_mentions_wealth_or_capacity(context):
    signals = detect(context)

    for s in signals:
        assert s.action != "ASK"
        for line in s.evidence:
            lowered = line.lower()
            for banned in _BANNED_WORDS:
                assert banned not in lowered


def test_invite_only_with_an_upcoming_event_otherwise_reconnect(context):
    signals = detect(context)
    actions = {s.action for s in signals}
    assert actions <= {"RECONNECT", "INVITE"}
    # This dataset has upcoming events (verified in test_relationship_change_no_upcoming_events below),
    # so every SIG4 signal should currently be INVITE.
    assert actions == {"INVITE"}


def test_reconnect_when_no_upcoming_event_exists(context):
    import pandas as pd

    from app.signals.relationship_change import _detect as raw_detect

    events = load_table("events")
    no_upcoming_events = events.copy()
    no_upcoming_events["starts_at"] = "2020-01-01T00:00:00Z"  # force every event into the past

    signals = raw_detect(
        context,
        load_table("career_history"),
        load_table("event_attendance"),
        no_upcoming_events,
        load_table("affiliations"),
    )
    assert len(signals) > 0
    assert all(s.action == "RECONNECT" for s in signals)


def test_duplicate_evidence_types_merge_into_one_signal_per_person(context):
    signals = detect(context)
    ids = [s.entity_id for s in signals]
    assert len(ids) == len(set(ids))  # one Signal per person even with multiple change types


def test_window_comes_from_config(context):
    import datetime

    from app.config import AS_OF_DATE, RELATIONSHIP_CHANGE_WINDOW_DAYS

    career_history = load_table("career_history")
    signals = detect(context)
    career_signal_ids = {s.entity_id for s in signals if any(e.startswith("Started") for e in s.evidence)}

    window_start = AS_OF_DATE - datetime.timedelta(days=RELATIONSHIP_CHANGE_WINDOW_DAYS)
    import pandas as pd

    ch = career_history.copy()
    ch["started_at"] = pd.to_datetime(ch["started_at"]).dt.date
    expected_ids = set(
        ch[(ch["started_at"] >= window_start) & (ch["started_at"] <= AS_OF_DATE)]["constituent_id"]
    )
    assert career_signal_ids <= expected_ids
