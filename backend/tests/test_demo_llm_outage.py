"""With the LLM disabled (no OPENAI_API_KEY, or the client raising),
the entire demo path must still work via deterministic template
fallbacks (issue 019). The test environment already has no API key
configured, so this is the default path every other test already
exercises -- this test makes that guarantee explicit and walks the
full narrative under it.
"""

from fastapi.testclient import TestClient

from app.explain import client as explain_client_module
from app.main import app

client = TestClient(app)


def test_default_client_is_none_in_this_environment():
    # Confirms the assumption every other test in this suite relies on:
    # explain() and Ask Sam's intent extraction are exercising their
    # template/keyword fallbacks, not a real LLM call.
    assert explain_client_module.default_client() is None


def test_demo_path_works_end_to_end_with_llm_unavailable():
    client.post("/api/demo/reset")

    today = client.get("/api/today").json()
    assert today["signals"]
    for signal in today["signals"][:3]:
        assert signal["explanation_source"] == "template"
        assert signal["explanation"]

    relationship = client.get("/api/relationships/2669").json()
    assert relationship["signals"]
    assert relationship["signals"][0]["explanation_source"] == "template"

    ask_response = client.post("/api/ask", json={"question": "Why did Valerie Kaur surface?"}).json()
    assert ask_response["intent"] == "WHY_PERSON"
    assert ask_response["answer"]

    brief = client.get("/api/relationships/2669/prepare-action").json()
    assert 3 <= len(brief["talking_points"]) <= 5

    extracted = client.post(
        "/api/relationships/2669/notes/extract",
        json={"note": "She's interested in the Boston alumni event, prefers texts, follow up in November."},
    ).json()
    assert extracted["communication_preference"] == "text"

    community = client.get("/api/community/alumni-board").json()
    assert community["recommended_action"] in ("RECONNECT", "INVITE", "ADVOCATE")
