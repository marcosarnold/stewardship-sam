from app.relationship_notes import extract_note

PRD_EXAMPLE_NOTE = (
    "Sarah isn't ready to give again. She's interested in the Boston alumni event, "
    "prefers texts, and I told her I'd follow up in November."
)


def test_prd_example_note_extracts_all_four_fields():
    result = extract_note(PRD_EXAMPLE_NOTE)

    assert result["interest"] == "Boston alumni events"
    assert result["communication_preference"] == "text"
    assert result["solicitation_status"] == "not_currently_interested"
    assert result["follow_up_date"] == "2026-11-01"  # AS_OF_DATE is 2026-08-31, so November is this year


def test_missing_information_stays_null():
    result = extract_note("Had a quick chat, nothing notable.")

    assert result["interest"] is None
    assert result["communication_preference"] is None
    assert result["solicitation_status"] is None
    assert result["follow_up_date"] is None


def test_mocked_llm_client_is_used_when_valid():
    class FakeClient:
        def complete(self, system_prompt, user_prompt):
            return (
                '{"interest": "athletics", "communication_preference": "email", '
                '"solicitation_status": null, "follow_up_month": "March"}'
            )

    result = extract_note("some note", client=FakeClient())
    assert result["interest"] == "athletics"
    assert result["communication_preference"] == "email"
    assert result["follow_up_date"] == "2027-03-01"  # March already passed this AS_OF_DATE year -> next year


def test_invalid_llm_output_falls_back_to_keywords():
    class FakeClient:
        def complete(self, system_prompt, user_prompt):
            return '{"communication_preference": "carrier_pigeon"}'  # not in the allowed set

    result = extract_note(PRD_EXAMPLE_NOTE, client=FakeClient())
    assert result["communication_preference"] == "text"  # fell back to keyword extraction
