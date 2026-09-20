from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_endpoint_follow_ups():
    response = client.post("/api/ask", json={"question": "Who have we promised to follow up with?"})

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "FOLLOW_UPS"
    assert any(r["entity_id"] == 14456 for r in body["results"]["overdue"])


def test_ask_endpoint_why_person():
    response = client.post("/api/ask", json={"question": "Why did Valerie Kaur surface?"})

    body = response.json()
    assert body["intent"] == "WHY_PERSON"
    assert body["results"]["entity_name"] == "Valerie Kaur"


def test_ask_endpoint_unsupported_question():
    response = client.post("/api/ask", json={"question": "What time is it?"})

    body = response.json()
    assert body["intent"] is None
    assert body["examples"] is not None
