from fastapi.testclient import TestClient

from app.dismissals import clear_all
from app.main import app

client = TestClient(app)


def test_community_view_endpoint():
    response = client.get("/api/community/alumni-board")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alumni Board"
    assert body["member_count"] == 180


def test_community_view_endpoint_404s_for_unknown_id():
    response = client.get("/api/community/not-a-real-community")

    assert response.status_code == 404


def test_today_includes_community_items_distinct_from_people():
    response = client.get("/api/today?show_all=true")

    body = response.json()
    community_items = [s for s in body["signals"] if s["entity_type"] == "community"]
    assert len(community_items) > 0
    for item in community_items:
        assert item["action"] != "RE-ENGAGE"


def test_dismiss_and_restore_a_community_item():
    clear_all()
    try:
        response = client.post("/api/today/alumni-board/dismiss", json={"reason": "test"})
        assert response.status_code == 200

        today = client.get("/api/today?show_all=true").json()
        assert not any(s["entity_id"] == "alumni-board" for s in today["signals"])
        assert any(s["entity_id"] == "alumni-board" for s in today["dismissed"])

        client.post("/api/today/alumni-board/restore")
        today = client.get("/api/today?show_all=true").json()
        assert any(s["entity_id"] == "alumni-board" for s in today["signals"])
    finally:
        clear_all()
