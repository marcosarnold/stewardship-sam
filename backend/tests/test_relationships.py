from app.relationships import build_relationship


def test_valerie_kaur_shows_thank_with_gift_and_email_channel(context, degrees, activities):
    page = build_relationship(2669, context, degrees, activities)

    assert page["entity_name"] == "Valerie Kaur"
    assert page["recommended_action"] == "THANK"

    thank_signals = [s for s in page["signals"] if s["signal_id"] == "SIG1"]
    assert len(thank_signals) == 1
    thank = thank_signals[0]
    assert thank["policy_status"] == "shown"
    assert "$25,000 gift on Feb 4, 2026" in thank["evidence"]
    assert thank["channel_hint"] == "email"


def test_assigned_fundraiser_shown_before_recommendation(context, degrees, activities):
    page = build_relationship(2669, context, degrees, activities)
    keys = list(page.keys())

    assert keys.index("assigned_officer") < keys.index("recommended_action")


def test_kieran_kaur_shows_wait_with_count(context, degrees, activities):
    page = build_relationship(12022, context, degrees, activities)

    assert page["recommended_action"] == "WAIT"
    wait_signals = [s for s in page["signals"] if s["action"] == "WAIT"]
    assert len(wait_signals) == 1
    assert wait_signals[0]["evidence"][0] == "5 outbound interactions in the last 60 days"


def test_nia_chen_shows_follow_up(context, degrees, activities):
    page = build_relationship(14456, context, degrees, activities)

    assert page["recommended_action"] == "FOLLOW UP"
    followup_signals = [s for s in page["signals"] if s["signal_id"] == "SIG2"]
    assert len(followup_signals) == 1
    assert followup_signals[0]["assigned_officer"] == "Morgan Ellis"


def test_isaac_chen_shows_no_action_recommended_and_kept_commitment(context, degrees, activities):
    page = build_relationship(2548, context, degrees, activities)

    assert page["recommended_action"] is None
    assert len(page["kept_commitments"]) == 1
    note = page["kept_commitments"][0]
    assert note["follow_up_date"] == "2026-05-15"
    assert "kept" in note["note"].lower()

    # His suppressed THANK is still visible in the why-card, tagged held_back.
    held_back_signals = [s for s in page["signals"] if s["policy_status"] == "held_back"]
    assert any(s["action"] == "THANK" for s in held_back_signals)


def test_missing_fields_show_not_on_file(context, degrees, activities):
    page = build_relationship(12022, context, degrees, activities)

    # Kieran has no city/state/degree on file -- the API returns null,
    # "Not on file" is the frontend's rendering of a null field (G4).
    assert page["city"] is None
    assert page["state"] is None
    assert page["class_year"] is None
    assert page["degree"] is None


def test_unknown_id_returns_none(context, degrees, activities):
    page = build_relationship(999999999, context, degrees, activities)

    assert page is None


def test_organization_id_returns_none(context, degrees, activities):
    org_id = int(context.constituents[context.constituents["entity_type"] == "organization"].iloc[0]["id"])

    page = build_relationship(org_id, context, degrees, activities)

    assert page is None


def test_deceased_id_returns_none(context, degrees, activities):
    deceased_id = int(context.constituents[context.constituents["deceased"] == 1].iloc[0]["id"])

    page = build_relationship(deceased_id, context, degrees, activities)

    assert page is None


def test_no_numeric_relationship_score_in_response(context, degrees, activities):
    page = build_relationship(2669, context, degrees, activities)

    assert "score" not in page
    for signal in page["signals"]:
        assert "score" not in signal
