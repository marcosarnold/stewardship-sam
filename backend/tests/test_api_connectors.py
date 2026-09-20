from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_connectors_endpoint_returns_ranked_connectors():
    response = client.get("/api/communities/alumni-board/connectors?limit=5")

    assert response.status_code == 200
    body = response.json()
    assert len(body["connectors"]) == 5
    for c in body["connectors"]:
        assert "overlap_count" in c
        assert "degree_centrality" in c
        assert "betweenness_centrality" in c
        assert "basis" in c
        assert "policy_status" in c


def test_connectors_endpoint_404s_for_unknown_community():
    response = client.get("/api/communities/not-a-real-community/connectors")

    assert response.status_code == 404
