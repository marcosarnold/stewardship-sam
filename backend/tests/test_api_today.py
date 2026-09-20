from fastapi.testclient import TestClient

from app.config import TODAY_QUEUE_MAX_ITEMS
from app.main import app

client = TestClient(app)


def test_today_endpoint_returns_signals_json():
    response = client.get("/api/today")

    assert response.status_code == 200
    body = response.json()
    assert "signals" in body
    assert 0 < len(body["signals"]) <= TODAY_QUEUE_MAX_ITEMS


def test_today_endpoint_includes_valerie_kaur_thank_signal():
    response = client.get("/api/today")
    body = response.json()

    valerie = next(s for s in body["signals"] if s["entity_id"] == 2669)

    assert valerie["action"] == "THANK"
    assert valerie["entity_name"] == "Valerie Kaur"
    assert len(valerie["evidence"]) <= 3
    assert "No stewardship interaction is recorded since the gift" in valerie["evidence"]
    assert valerie["channel_hint"] == "email"
    assert any("do-not-call" in line.lower() for line in valerie["evidence"])


def test_today_endpoint_includes_kieran_kaur_wait_signal_and_no_thank():
    response = client.get("/api/today")
    body = response.json()

    kieran = next(s for s in body["signals"] if s["entity_id"] == 12022)

    assert kieran["action"] == "WAIT"
    assert kieran["evidence"][0] == "5 outbound interactions in the last 60 days"
    assert not any(
        s["entity_id"] == 12022 and s["action"] == "THANK" for s in body["signals"]
    )


def test_today_endpoint_includes_held_back_with_reason_counts():
    response = client.get("/api/today")
    body = response.json()

    assert "held_back" in body
    held_back = body["held_back"]
    assert "reasons" in held_back
    assert "items" in held_back
    assert len(held_back["items"]) == sum(r["count"] for r in held_back["reasons"])
    for item in held_back["items"]:
        assert item["reason_code"]
        assert item["reason"]
        assert item["entity_id"]
