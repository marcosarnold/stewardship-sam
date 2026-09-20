from app.today import build_today_queue, summarize_held_back


def test_valerie_kaur_channel_note_explains_do_not_call(constituents, gifts, interactions, staff, opportunities):
    today_items, _ = build_today_queue(constituents, gifts, interactions, staff, opportunities)
    thank_signals = [s for s in today_items if s.entity_id == 2669 and s.action == "THANK"]

    assert len(thank_signals) == 1
    valerie = thank_signals[0]
    assert valerie.channel_hint == "email"
    assert valerie.evidence[-1] == "Phone is marked do-not-call; email is the allowed channel"
    assert len(valerie.evidence) <= 3


def test_kieran_kaur_wait_signal_present_and_no_thank(constituents, gifts, interactions, staff, opportunities):
    today_items, held_back = build_today_queue(constituents, gifts, interactions, staff, opportunities)

    kieran_signals = [s for s in today_items if s.entity_id == 12022]
    assert len(kieran_signals) == 1
    assert kieran_signals[0].action == "WAIT"
    assert not any(item["entity_id"] == 12022 for item in held_back)


def test_held_back_count_plus_today_thank_count_equals_total_thank_signals(
    constituents, gifts, interactions, staff, opportunities
):
    from app.signals import stewardship_gap

    total_thank = len(stewardship_gap.detect(constituents, gifts, interactions))
    today_items, held_back = build_today_queue(constituents, gifts, interactions, staff, opportunities)

    today_thank_count = sum(1 for s in today_items if s.action == "THANK")
    thank_held_back_count = sum(1 for item in held_back if item["action"] == "THANK")
    assert today_thank_count + thank_held_back_count == total_thank


def test_valerie_kaur_also_surfaces_as_reconnect(constituents, gifts, interactions, staff, opportunities):
    """Duplicate appearance across signals is expected until issue 007 merges
    per-person (issue 004's own example)."""
    today_items, _ = build_today_queue(constituents, gifts, interactions, staff, opportunities)

    valerie_actions = {s.action for s in today_items if s.entity_id == 2669}
    assert valerie_actions == {"THANK", "RECONNECT"}


def test_summarize_held_back_groups_by_reason_code():
    held_back = [
        {"reason_code": "recent_contact", "reason": "x", "entity_id": 1, "entity_name": "A", "action": "THANK", "entity_type": "constituent"},
        {"reason_code": "recent_contact", "reason": "x", "entity_id": 2, "entity_name": "B", "action": "THANK", "entity_type": "constituent"},
        {"reason_code": "scheduled_follow_up", "reason": "y", "entity_id": 3, "entity_name": "C", "action": "THANK", "entity_type": "constituent"},
    ]

    summary = summarize_held_back(held_back)

    reasons = {r["reason_code"]: r["count"] for r in summary["reasons"]}
    assert reasons == {"recent_contact": 2, "scheduled_follow_up": 1}
    assert len(summary["items"]) == 3
