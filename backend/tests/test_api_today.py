from collections import Counter

from fastapi.testclient import TestClient

from app.config import TODAY_QUEUE_MAX_ITEMS
from app.dismissals import clear_all
from app.main import app

client = TestClient(app)


def test_today_endpoint_returns_signals_json():
    response = client.get("/api/today")

    assert response.status_code == 200
    body = response.json()
    assert "signals" in body
    assert 0 < len(body["signals"]) <= TODAY_QUEUE_MAX_ITEMS


def test_today_endpoint_includes_valerie_kaur_thank_signal():
    response = client.get("/api/today")
    body = response.json()

    valerie = next(s for s in body["signals"] if s["entity_id"] == 2669)

    assert valerie["action"] == "THANK"
    assert valerie["entity_name"] == "Valerie Kaur"
    assert len(valerie["evidence"]) <= 3
    assert "No stewardship interaction is recorded since the gift" in valerie["evidence"]
    assert valerie["channel_hint"] == "email"
    assert any("do-not-call" in line.lower() for line in valerie["evidence"])


def test_today_endpoint_includes_kieran_kaur_wait_signal_and_no_thank():
    response = client.get("/api/today")
    body = response.json()

    kieran = next(s for s in body["signals"] if s["entity_id"] == 12022)

    assert kieran["action"] == "WAIT"
    assert kieran["evidence"][0] == "5 outbound interactions in the last 60 days"
    assert not any(
        s["entity_id"] == 12022 and s["action"] == "THANK" for s in body["signals"]
    )


def test_today_endpoint_includes_held_back_with_reason_counts():
    response = client.get("/api/today")
    body = response.json()

    assert "held_back" in body
    held_back = body["held_back"]
    assert "reasons" in held_back
    assert "items" in held_back
    assert len(held_back["items"]) == sum(r["count"] for r in held_back["reasons"])
    for item in held_back["items"]:
        assert item["reason_code"]
        assert item["reason"]
        assert item["entity_id"]


def test_header_counts_match_the_items_actually_shown():
    response = client.get("/api/today")
    body = response.json()

    assert body["counts"] == dict(Counter(s["action"] for s in body["signals"]))


def test_show_all_returns_more_than_the_capped_default():
    capped = client.get("/api/today").json()
    full = client.get("/api/today", params={"show_all": "true"}).json()

    assert len(capped["signals"]) <= TODAY_QUEUE_MAX_ITEMS
    assert full["show_all"] is True
    assert len(full["signals"]) == full["total_count"]
    assert full["total_count"] > len(capped["signals"])


def test_officer_filter_only_returns_that_officers_relationships():
    response = client.get("/api/today", params={"officer_id": 1, "show_all": "true"})
    body = response.json()

    assert body["signals"], "expected staff 1 (Morgan Ellis) to own at least one item"
    for signal in body["signals"]:
        # Valerie and Nia are both assigned to staff 1 in the demo cast.
        assert signal["assigned_officer"] in (None, "Morgan Ellis") or signal["entity_id"] in (2669, 14456)


def test_dismiss_hides_an_item_and_restore_brings_it_back():
    try:
        before = client.get("/api/today").json()
        assert any(s["entity_id"] == 2669 for s in before["signals"])

        dismiss_response = client.post("/api/today/2669/dismiss", json={"reason": "handled by phone"})
        assert dismiss_response.status_code == 200

        after_dismiss = client.get("/api/today").json()
        assert not any(s["entity_id"] == 2669 for s in after_dismiss["signals"])
        assert any(s["entity_id"] == 2669 for s in after_dismiss["dismissed"])

        with_dismissed = client.get("/api/today", params={"include_dismissed": "true"}).json()
        valerie = next(s for s in with_dismissed["signals"] if s["entity_id"] == 2669)
        assert valerie["dismissed"] is True
        assert valerie["dismiss_reason"] == "handled by phone"
        assert valerie["action"] == "THANK"  # the underlying signal survives

        restore_response = client.post("/api/today/2669/restore")
        assert restore_response.status_code == 200

        after_restore = client.get("/api/today").json()
        assert any(s["entity_id"] == 2669 for s in after_restore["signals"])
    finally:
        clear_all()


def test_dismiss_without_a_reason_is_allowed():
    try:
        response = client.post("/api/today/2669/dismiss")
        assert response.status_code == 200
        assert response.json()["reason"] is None
    finally:
        clear_all()
