from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PRD_EXAMPLE_NOTE = (
    "Sarah isn't ready to give again. She's interested in the Boston alumni event, "
    "prefers texts, and I told her I'd follow up in November."
)


def test_extract_endpoint_does_not_save_anything():
    response = client.post("/api/relationships/2669/notes/extract", json={"note": PRD_EXAMPLE_NOTE})

    assert response.status_code == 200
    body = response.json()
    assert body["interest"] == "Boston alumni events"

    latest = client.get("/api/relationships/2669/notes/latest")
    assert latest.status_code == 404  # extraction alone never saves


def test_save_endpoint_persists_confirmed_fields():
    extracted = client.post("/api/relationships/2669/notes/extract", json={"note": PRD_EXAMPLE_NOTE}).json()

    saved = client.post(
        "/api/relationships/2669/notes",
        json={**extracted, "raw_note": PRD_EXAMPLE_NOTE},
    )
    assert saved.status_code == 200

    latest = client.get("/api/relationships/2669/notes/latest").json()
    assert latest["solicitation_status"] == "not_currently_interested"
    assert latest["follow_up_date"] == "2026-11-01"


def test_not_currently_interested_blocks_ask_end_to_end():
    client.post(
        "/api/relationships/2669/notes",
        json={"solicitation_status": "not_currently_interested", "raw_note": "not interested right now"},
    )

    from app.priority_queue import _facts_for
    from app.context import build_context

    context = build_context()
    pop = context.constituents.set_index("id", drop=False)
    facts = _facts_for(2669, pop, {}, set())
    assert facts["not_currently_interested"] is True
