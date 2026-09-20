from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_communities_endpoint_lists_79_eligible():
    response = client.get("/api/communities")

    assert response.status_code == 200
    communities = response.json()["communities"]
    eligible = [c for c in communities if c["eligible"]]
    assert len(eligible) == 79


def test_members_endpoint_paginates_and_ids_resolve_in_relationship_view():
    response = client.get("/api/communities/alumni-board/members")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 180
    assert len(body["members"]) == 50

    member = body["members"][0]
    relationship = client.get(f"/api/relationships/{member['entity_id']}")
    assert relationship.status_code == 200
    assert relationship.json()["entity_id"] == member["entity_id"]


def test_members_endpoint_404s_for_unknown_community():
    response = client.get("/api/communities/not-a-real-community/members")

    assert response.status_code == 404
