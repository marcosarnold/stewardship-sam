"""Walks the demo narrative (PRD Section 23, Appendix C) against the
API end to end, verifying every cast member's expected action
(Appendix B). Reset first, so this also exercises the reset command.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_reset_command_restores_a_clean_state():
    client.post("/api/relationships/2669/confirm-action", json={"outcome": "dismissed", "note": "test"})
    dismissed_before = client.get("/api/today?show_all=true").json()
    assert any(s["entity_id"] == 2669 for s in dismissed_before["dismissed"])

    response = client.post("/api/demo/reset")
    assert response.status_code == 200

    after = client.get("/api/today?show_all=true").json()
    assert not any(s["entity_id"] == 2669 for s in after["dismissed"])


def test_demo_path_walks_the_full_narrative():
    client.post("/api/demo/reset")

    # 1. Open Today: Nia Chen is FOLLOW UP, the positive broken-commitment example.
    today = client.get("/api/today?show_all=true").json()
    nia = next(s for s in today["signals"] if s["entity_id"] == 14456)
    assert nia["action"] == "FOLLOW UP"
    assert nia["entity_name"] == "Nia Chen"

    # Isaac Chen is the control: no action, commitment kept.
    isaac = client.get("/api/relationships/2548").json()
    assert isaac["recommended_action"] is None
    assert len(isaac["kept_commitments"]) == 1

    # Valerie Kaur: THANK.
    valerie = next(s for s in today["signals"] if s["entity_id"] == 2669)
    assert valerie["action"] == "THANK"
    assert valerie["entity_name"] == "Valerie Kaur"

    # Kieran Kaur: WAIT.
    kieran = next(s for s in today["signals"] if s["entity_id"] == 12022)
    assert kieran["action"] == "WAIT"
    assert kieran["entity_name"] == "Kieran Kaur"

    # 2. Ask "Which communities are we losing touch with?"
    ask_response = client.post(
        "/api/ask", json={"question": "Which communities are losing engagement?"}
    ).json()
    assert ask_response["intent"] == "COOLING_COMMUNITIES"
    community_ids = {r["community_id"] for r in ask_response["results"]}
    assert "alumni-board" in community_ids

    # 3. Open Alumni Board: header, network, connectors.
    community_view = client.get("/api/community/alumni-board").json()
    assert community_view["name"] == "Alumni Board"
    assert community_view["member_count"] == 180

    graph = client.get("/api/community/alumni-board/graph").json()
    assert any(n["is_connector"] for n in graph["nodes"] if n["type"] == "person")

    connectors = client.get("/api/communities/alumni-board/connectors?limit=5").json()
    assert len(connectors["connectors"]) == 5

    # 4. Close on Today -- the queue is still coherent after the detour.
    closing_today = client.get("/api/today").json()
    assert closing_today["total_count"] > 0
