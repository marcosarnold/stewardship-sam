from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_today_signals_include_explanation():
    response = client.get("/api/today")
    body = response.json()

    assert body["signals"], "expected at least one Today signal"
    for signal in body["signals"]:
        assert signal["explanation"]
        assert signal["explanation_source"] in ("llm", "template")
        # No API key is configured in this environment.
        assert signal["explanation_source"] == "template"


def test_relationship_signals_include_explanation():
    response = client.get("/api/relationships/2669")
    body = response.json()

    assert body["signals"], "expected at least one signal for Valerie Kaur"
    for signal in body["signals"]:
        assert signal["explanation"]
        assert "Valerie Kaur" in signal["explanation"]
