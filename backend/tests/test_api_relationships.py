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


def test_today_view_relationship_links_resolve():
    today = client.get("/api/today").json()

    checked = 0
    for signal in today["signals"]:
        response = client.get(f"/api/relationships/{signal['entity_id']}")
        assert response.status_code == 200
        assert response.json()["entity_id"] == signal["entity_id"]
        checked += 1

    assert checked > 0
