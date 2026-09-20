"""FastAPI app exposing the Today queue."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import TODAY_QUEUE_MAX_ITEMS
from app.db import load_table
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

    today_items, held_back = build_today_queue(constituents, gifts, interactions)
    # Provisional ordering only (real ranking is issues/007-priority-queue-and-dismissal.md).
    # WAIT signals surface first so contact-pressure restraint (SC8) isn't
    # crowded out by the much larger THANK pool under the display cap;
    # THANK is then ordered by gift amount, per issue 001.
    today_items.sort(key=lambda s: (s.action != "WAIT", -(s.urgency_amount or 0)))

    return {
        "signals": [s.to_dict() for s in today_items[:TODAY_QUEUE_MAX_ITEMS]],
        "held_back": summarize_held_back(held_back),
    }
