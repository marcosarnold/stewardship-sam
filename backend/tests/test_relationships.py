from app.relationships import build_relationship


def _build(entity_id, constituents, gifts, interactions, staff, opportunities, degrees, activities):
    return build_relationship(
        entity_id, constituents, gifts, interactions, staff, opportunities, degrees, activities
    )


def test_valerie_kaur_shows_thank_with_gift_and_email_channel(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(2669, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page["entity_name"] == "Valerie Kaur"
    assert page["recommended_action"] == "THANK"

    thank_signals = [s for s in page["signals"] if s["signal_id"] == "SIG1"]
    assert len(thank_signals) == 1
    thank = thank_signals[0]
    assert thank["policy_status"] == "shown"
    assert "$25,000 gift on Feb 4, 2026" in thank["evidence"]
    assert thank["channel_hint"] == "email"


def test_assigned_fundraiser_shown_before_recommendation(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(2669, constituents, gifts, interactions, staff, opportunities, degrees, activities)
    keys = list(page.keys())

    assert keys.index("assigned_officer") < keys.index("recommended_action")


def test_kieran_kaur_shows_wait_with_count(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(12022, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page["recommended_action"] == "WAIT"
    wait_signals = [s for s in page["signals"] if s["action"] == "WAIT"]
    assert len(wait_signals) == 1
    assert wait_signals[0]["evidence"][0] == "5 outbound interactions in the last 60 days"


def test_nia_chen_shows_follow_up(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(14456, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page["recommended_action"] == "FOLLOW UP"
    followup_signals = [s for s in page["signals"] if s["signal_id"] == "SIG2"]
    assert len(followup_signals) == 1
    assert followup_signals[0]["assigned_officer"] == "Morgan Ellis"


def test_isaac_chen_shows_no_action_recommended_and_kept_commitment(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(2548, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page["recommended_action"] is None
    assert len(page["kept_commitments"]) == 1
    note = page["kept_commitments"][0]
    assert note["follow_up_date"] == "2026-05-15"
    assert "kept" in note["note"].lower()

    # His suppressed THANK is still visible in the why-card, tagged held_back.
    held_back_signals = [s for s in page["signals"] if s["policy_status"] == "held_back"]
    assert any(s["action"] == "THANK" for s in held_back_signals)


def test_missing_fields_show_not_on_file(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(12022, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    # Kieran has no city/state/degree on file -- the API returns null,
    # "Not on file" is the frontend's rendering of a null field (G4).
    assert page["city"] is None
    assert page["state"] is None
    assert page["class_year"] is None
    assert page["degree"] is None


def test_unknown_id_returns_none(constituents, gifts, interactions, staff, opportunities, degrees, activities):
    page = _build(999999999, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page is None


def test_organization_id_returns_none(constituents, gifts, interactions, staff, opportunities, degrees, activities):
    org_id = int(constituents[constituents["entity_type"] == "organization"].iloc[0]["id"])

    page = _build(org_id, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page is None


def test_deceased_id_returns_none(constituents, gifts, interactions, staff, opportunities, degrees, activities):
    deceased_id = int(constituents[constituents["deceased"] == 1].iloc[0]["id"])

    page = _build(deceased_id, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert page is None


def test_no_numeric_relationship_score_in_response(
    constituents, gifts, interactions, staff, opportunities, degrees, activities
):
    page = _build(2669, constituents, gifts, interactions, staff, opportunities, degrees, activities)

    assert "score" not in page
    for signal in page["signals"]:
        assert "score" not in signal
