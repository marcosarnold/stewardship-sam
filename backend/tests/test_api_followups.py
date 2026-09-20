from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_followups_default_returns_only_nia_chen():
    response = client.get("/api/followups")

    assert response.status_code == 200
    body = response.json()
    assert len(body["commitments"]) == 1
    assert body["commitments"][0]["entity_name"] == "Nia Chen"
    assert body["commitments"][0]["action"] == "FOLLOW UP"


def test_followups_include_resolved_shows_40_including_isaac_chen():
    response = client.get("/api/followups", params={"include_resolved": "true"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["commitments"]) == 40

    isaac = next(c for c in body["commitments"] if c["entity_name"] == "Isaac Chen")
    assert isaac["resolved"] is True
    assert isaac["action"] is None
