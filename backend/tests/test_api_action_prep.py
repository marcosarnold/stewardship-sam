import hashlib

from fastapi.testclient import TestClient

from app.db import DB_PATH
from app.main import app

client = TestClient(app)


def _db_hash() -> str:
    return hashlib.sha256(DB_PATH.read_bytes()).hexdigest()


def test_prepare_action_endpoint():
    response = client.get("/api/relationships/2669/prepare-action")

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "THANK"
    assert body["channel_hint"] == "email"
    assert 3 <= len(body["talking_points"]) <= 5


def test_prepare_action_endpoint_404s_for_unknown_id():
    response = client.get("/api/relationships/999999999/prepare-action")
    assert response.status_code == 404


def test_confirm_action_records_outcome_with_timestamp():
    response = client.post(
        "/api/relationships/2669/confirm-action",
        json={"action": "THANK", "outcome": "done", "note": "Called and thanked her"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "done"
    assert body["note"] == "Called and thanked her"
    assert body["recorded_at"]

    brief = client.get("/api/relationships/2669/prepare-action").json()
    assert brief["last_outcome"]["outcome"] == "done"


def test_dismissed_outcome_updates_today():
    entity_id = 14456  # Nia Chen, FOLLOW UP -- appears on Today

    before = client.get("/api/today?show_all=true").json()
    assert any(s["entity_id"] == entity_id for s in before["signals"])

    client.post(f"/api/relationships/{entity_id}/confirm-action", json={"outcome": "dismissed", "note": "handled"})

    after = client.get("/api/today?show_all=true").json()
    assert not any(s["entity_id"] == entity_id for s in after["signals"])
    assert any(s["entity_id"] == entity_id for s in after["dismissed"])


def test_confirm_action_rejects_unknown_outcome():
    response = client.post("/api/relationships/2669/confirm-action", json={"outcome": "sent_an_email"})
    assert response.status_code == 400


def test_no_outbound_side_effects_the_source_database_is_never_modified():
    """Sam never sends, calls, solicits, or writes to GiveCampus data
    (Section 16) -- confirming an action must never touch the CRM's own
    database file, only Sam's own outcome log.
    """
    before = _db_hash()

    client.get("/api/relationships/2669/prepare-action")
    client.post("/api/relationships/2669/confirm-action", json={"action": "THANK", "outcome": "done"})
    client.post("/api/relationships/2669/confirm-action", json={"outcome": "not_now"})

    after = _db_hash()
    assert before == after
