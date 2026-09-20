"""FastAPI app exposing the Today queue."""

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import TODAY_QUEUE_MAX_ITEMS
from app.context import build_context
from app.db import load_table
from app.dismissals import dismiss, restore
from app.explain import explain
from app.explain.from_signal import payload_from_signal_dict
from app.followups import build_followups
from app.priority_queue import build_queue, summarize_counts, summarize_held_back
from app.relationships import build_relationship

app = FastAPI(title="Stewardship Sam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _with_explanation(signal: dict) -> dict:
    result = explain(payload_from_signal_dict(signal))
    return {**signal, "explanation": result.text, "explanation_source": result.source}


@app.get("/api/today")
def get_today(
    officer_id: int | None = None,
    include_dismissed: bool = False,
    show_all: bool = False,
):
    context = build_context()
    items, held_back = build_queue(context)

    if officer_id is not None:
        items = [i for i in items if not pd.isna(i.assigned_staff_id) and int(i.assigned_staff_id) == officer_id]

    shown = items if include_dismissed else [i for i in items if not i.dismissed]
    dismissed = [i for i in items if i.dismissed]

    visible = shown if show_all else shown[:TODAY_QUEUE_MAX_ITEMS]
    # Explanations are only computed for what's actually rendered, so cost
    # and latency never scale with the full (potentially 1000+ item) queue.
    signals = [_with_explanation(i.to_dict()) for i in visible]

    return {
        "signals": signals,
        "total_count": len(shown),
        "dismissed": [i.to_dict() for i in dismissed],
        # Counts always describe `signals` itself, so the header never
        # claims a total the visible cards don't back up.
        "counts": summarize_counts(visible),
        "cap": TODAY_QUEUE_MAX_ITEMS,
        "show_all": show_all,
        "held_back": summarize_held_back(held_back),
    }


class DismissRequest(BaseModel):
    reason: str | None = None


@app.post("/api/today/{entity_id}/dismiss")
def dismiss_today_item(entity_id: int, body: DismissRequest = DismissRequest()):
    dismiss(entity_id, body.reason)
    return {"entity_id": entity_id, "dismissed": True, "reason": body.reason}


@app.post("/api/today/{entity_id}/restore")
def restore_today_item(entity_id: int):
    restore(entity_id)
    return {"entity_id": entity_id, "dismissed": False}


@app.get("/api/followups")
def get_followups(include_resolved: bool = False):
    constituents = load_table("constituents")
    interactions = load_table("interactions")
    staff = load_table("staff")

    return build_followups(constituents, interactions, staff, include_resolved)


@app.get("/api/relationships/{entity_id}")
def get_relationship(entity_id: int):
    context = build_context()
    degrees = load_table("degrees")
    activities = load_table("activities")

    relationship = build_relationship(entity_id, context, degrees, activities)
    if relationship is None:
        raise HTTPException(
            status_code=404,
            detail=f"No relationship record for id {entity_id}: unknown, not an individual, or deceased.",
        )

    relationship["signals"] = [_with_explanation(s) for s in relationship["signals"]]
    return relationship
