from datetime import timedelta

import pandas as pd

from app.config import AS_OF_DATE
from app.context import Context
from app.dismissals import clear_all, dismiss
from app.models import Signal
from app.priority_queue import build_queue, merge_per_person
from app.registry import register, unregister


def test_dummy_detector_changes_the_queue_without_touching_ranking_code(context):
    target_id = int(
        context.constituents[
            (context.constituents["entity_type"] == "individual") & (context.constituents["deceased"] == 0)
        ].iloc[0]["id"]
    )

    def dummy_detector(ctx):
        row = ctx.constituents[ctx.constituents["id"] == target_id].iloc[0]
        return [
            Signal(
                entity_type="constituent",
                entity_id=target_id,
                entity_name=row["preferred_name"],
                signal_id="SIGX",
                action="THANK",
                evidence=["dummy evidence marker"],
            )
        ]

    register(dummy_detector)
    try:
        items, _ = build_queue(context)
    finally:
        unregister(dummy_detector)

    all_evidence = [
        line
        for item in items
        if item.entity_id == target_id
        for line in item.evidence + [e for s in item.supporting_signals for e in s["evidence"]]
    ]
    assert "dummy evidence marker" in all_evidence


def test_valerie_kaur_appears_once_thank_primary_reconnect_supporting(context):
    items, _ = build_queue(context)

    valerie_items = [i for i in items if i.entity_id == 2669]
    assert len(valerie_items) == 1
    assert valerie_items[0].action == "THANK"
    assert any(s["action"] == "RECONNECT" for s in valerie_items[0].supporting_signals)


def test_kieran_kaur_appears_once_as_wait_with_no_other_actions(context):
    items, _ = build_queue(context)

    kieran_items = [i for i in items if i.entity_id == 12022]
    assert len(kieran_items) == 1
    assert kieran_items[0].action == "WAIT"
    assert all(s["action"] != kieran_items[0].action for s in kieran_items[0].supporting_signals)


def test_nia_chen_follow_up_ranks_above_every_thank_assign_reconnect(context):
    items, _ = build_queue(context)

    nia_index = next(i for i, item in enumerate(items) if item.entity_id == 14456)
    assert items[nia_index].action == "FOLLOW UP"

    for i, item in enumerate(items):
        if item.action in ("THANK", "ASSIGN", "RECONNECT"):
            assert nia_index < i


def test_suppressed_signal_from_any_detector_goes_to_held_back():
    constituents = pd.DataFrame(
        [
            {
                "id": 555555,
                "entity_type": "individual",
                "deceased": 0,
                "preferred_name": "Suppressed Person",
                "email_status": "deliverable",
                "phone_status": "available",
                "do_not_solicit": 0,
                "assigned_staff_id": None,
                "city": None,
                "state": None,
            }
        ]
    )
    recent_date = AS_OF_DATE - timedelta(days=1)
    interactions = pd.DataFrame(
        [
            {
                "id": 1,
                "constituent_id": 555555,
                "occurred_at": f"{recent_date.isoformat()}T00:00:00Z",
                "direction": "outbound",
                "purpose": "cultivation",
                "follow_up_date": None,
            }
        ]
    )
    empty_gifts = pd.DataFrame(columns=["constituent_id", "amount", "status", "gift_type", "gift_date"])
    empty_staff = pd.DataFrame(columns=["id", "display_name", "active"])
    empty_opportunities = pd.DataFrame(columns=["constituent_id"])

    def fake_detector(ctx):
        return [
            Signal(
                entity_type="constituent",
                entity_id=555555,
                entity_name="Suppressed Person",
                signal_id="SIGX",
                action="THANK",
                evidence=["test evidence"],
            )
        ]

    register(fake_detector)
    try:
        ctx = Context(
            constituents=constituents,
            gifts=empty_gifts,
            interactions=interactions,
            staff=empty_staff,
            opportunities=empty_opportunities,
        )
        items, held_back = build_queue(ctx)
    finally:
        unregister(fake_detector)

    assert not any(i.entity_id == 555555 for i in items)
    assert any(h["entity_id"] == 555555 and h["reason_code"] == "recent_contact" for h in held_back)


def test_dismissal_hides_survives_reload_and_can_be_restored_without_deleting_signal(context):
    dismiss(2669, reason="already stewarded by phone")
    try:
        items, _ = build_queue(context)
        valerie = next(i for i in items if i.entity_id == 2669)
        assert valerie.dismissed is True
        assert valerie.dismiss_reason == "already stewarded by phone"
        assert valerie.action == "THANK"  # the underlying signal is still there

        # A second, independent computation ("reload") sees the same state.
        items_again, _ = build_queue(context)
        valerie_again = next(i for i in items_again if i.entity_id == 2669)
        assert valerie_again.dismissed is True
    finally:
        clear_all()

    items_after_restore, _ = build_queue(context)
    valerie_restored = next(i for i in items_after_restore if i.entity_id == 2669)
    assert valerie_restored.dismissed is False


def test_queue_item_serialization_has_no_score_field(context):
    items, _ = build_queue(context)

    for item in items[:30]:
        payload = item.to_dict()
        assert "score" not in payload
        assert "sort_key" not in payload


def test_ranking_is_deterministic_with_entity_id_as_tiebreaker():
    higher_id = Signal(
        entity_type="constituent",
        entity_id=20,
        entity_name="B",
        signal_id="SIGX",
        action="THANK",
        evidence=[],
        urgency_amount=100.0,
    )
    lower_id = Signal(
        entity_type="constituent",
        entity_id=10,
        entity_name="A",
        signal_id="SIGX",
        action="THANK",
        evidence=[],
        urgency_amount=100.0,
    )

    for _ in range(3):
        items = merge_per_person([higher_id, lower_id])
        items.sort(key=lambda i: i.sort_key)
        assert [i.entity_id for i in items] == [10, 20]
