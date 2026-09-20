from app.action_prep import build_action_brief


def test_brief_includes_action_channel_officer_and_evidence(context):
    brief = build_action_brief(2669, context)  # Valerie Kaur

    assert brief["action"] == "THANK"
    assert brief["channel_hint"] == "email"
    assert brief["assigned_officer"]
    assert len(brief["evidence"]) > 0


def test_no_full_message_draft_only_talking_points(context):
    brief = build_action_brief(2669, context)

    assert 3 <= len(brief["talking_points"]) <= 5
    for point in brief["talking_points"]:
        assert len(point) < 400  # a bullet, not a drafted email body


def test_restricted_channel_is_never_suggested_for_wait(context):
    brief = build_action_brief(12022, context)  # Kieran Kaur, WAIT

    assert brief["action"] == "WAIT"
    assert brief["channel_hint"] is None
    assert any("no allowed channel" in p.lower() for p in brief["talking_points"])


def test_unknown_id_returns_none(context):
    assert build_action_brief(999999999, context) is None


def test_works_with_llm_unavailable_deterministic_fallback(context):
    # No OPENAI_API_KEY is configured in the test environment, so explain()
    # already falls back to its template path -- this proves the brief
    # still builds end to end rather than raising.
    brief = build_action_brief(14456, context)  # Nia Chen, FOLLOW UP
    assert brief["action"] == "FOLLOW UP"
    assert len(brief["talking_points"]) >= 3
