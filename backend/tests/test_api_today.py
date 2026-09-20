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
