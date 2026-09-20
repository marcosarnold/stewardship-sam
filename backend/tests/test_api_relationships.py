from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_relationship_endpoint_returns_valerie():
    response = client.get("/api/relationships/2669")

    assert response.status_code == 200
    body = response.json()
    assert body["entity_name"] == "Valerie Kaur"
    assert body["recommended_action"] == "THANK"


def test_relationship_endpoint_404s_for_unknown_id():
    response = client.get("/api/relationships/999999999")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_relationship_endpoint_404s_for_deceased_id():
    from app.db import load_table

    constituents = load_table("constituents")
    deceased_id = int(constituents[constituents["deceased"] == 1].iloc[0]["id"])

    response = client.get(f"/api/relationships/{deceased_id}")

    assert response.status_code == 404


def test_timeline_endpoint_returns_valeries_gift_newest_first():
    response = client.get("/api/relationships/2669/timeline")

    assert response.status_code == 200
    body = response.json()
    assert body["entries"][0]["type"] == "gift"
    assert body["entries"][0]["date"] == "2026-02-04"
    assert body["counts"]["interaction"] == 0


def test_timeline_endpoint_404s_for_unknown_id():
    response = client.get("/api/relationships/999999999/timeline")

    assert response.status_code == 404


def test_timeline_endpoint_type_filter():
    response = client.get("/api/relationships/2548/timeline?types=gift")

    body = response.json()
    assert all(e["type"] == "gift" for e in body["entries"])


def test_timeline_endpoint_pages():
    page_one = client.get("/api/relationships/2548/timeline?page=1").json()
    page_two = client.get("/api/relationships/2548/timeline?page=2").json()

    assert page_one["entries"] != page_two["entries"]


def test_today_view_relationship_links_resolve():
    today = client.get("/api/today").json()

    checked = 0
    for signal in today["signals"]:
        response = client.get(f"/api/relationships/{signal['entity_id']}")
        assert response.status_code == 200
        assert response.json()["entity_id"] == signal["entity_id"]
        checked += 1

    assert checked > 0
