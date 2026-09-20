from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_returns_alumni_board_rates():
    response = client.get("/api/communities/alumni-board/metrics")

    assert response.status_code == 200
    body = response.json()
    assert round(body["historical_giving_rate"] * 100, 1) == 58.9
    assert round(body["recent_giving_rate"] * 100, 1) == 8.9
    assert round(body["recent_interaction_rate"] * 100, 1) == 20.6
    assert "event_data_caveat" in body


def test_bulk_metrics_endpoint_returns_all_79():
    response = client.get("/api/communities/metrics")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 79
    assert round(body["alumni-board"]["recent_giving_rate"] * 100, 1) == 8.9


def test_metrics_endpoint_404s_for_unknown_community():
    response = client.get("/api/communities/not-a-real-community/metrics")

    assert response.status_code == 404
