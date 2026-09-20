"""FastAPI app exposing the Today queue."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import TODAY_QUEUE_MAX_ITEMS
from app.db import load_table
from app.followups import build_followups
from app.today import build_today_queue, summarize_held_back

app = FastAPI(title="Stewardship Sam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/today")
def get_today():
    constituents = load_table("constituents")
    gifts = load_table("gifts")
    interactions = load_table("interactions")
    staff = load_table("staff")
    opportunities = load_table("opportunities")

    today_items, held_back = build_today_queue(
        constituents, gifts, interactions, staff, opportunities
    )
    # Provisional ordering only (real ranking is issues/007-priority-queue-and-dismissal.md).
    # Bucket by action first so no signal type is entirely crowded out of the
    # display cap by another type's larger dollar figures -- ASSIGN/RECONNECT
    # rank by lifetime giving, which otherwise dwarfs THANK's single-gift
    # amounts and would bury it. WAIT surfaces first for restraint (SC8),
    # then THANK (issue 001), then RECONNECT/ASSIGN (issue 004).
    _ACTION_PRIORITY = {"WAIT": 0, "THANK": 1, "RECONNECT": 2, "ASSIGN": 3}
    today_items.sort(
        key=lambda s: (_ACTION_PRIORITY.get(s.action, 99), -(s.urgency_amount or 0))
    )

    return {
        "signals": [s.to_dict() for s in today_items[:TODAY_QUEUE_MAX_ITEMS]],
        "held_back": summarize_held_back(held_back),
    }


@app.get("/api/followups")
def get_followups(include_resolved: bool = False):
    constituents = load_table("constituents")
    interactions = load_table("interactions")
    staff = load_table("staff")

    return build_followups(constituents, interactions, staff, include_resolved)
