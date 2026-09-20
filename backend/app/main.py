"""FastAPI app exposing the Today queue."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import TODAY_QUEUE_MAX_ITEMS
from app.db import load_table
from app.signals import stewardship_gap

app = FastAPI(title="Stewardship Sam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_today_queue() -> list[dict]:
    constituents = load_table("constituents")
    gifts = load_table("gifts")
    interactions = load_table("interactions")

    signals = stewardship_gap.detect(constituents, gifts, interactions)
    signals.sort(key=lambda s: s.urgency_amount or 0, reverse=True)
    return [s.to_dict() for s in signals[:TODAY_QUEUE_MAX_ITEMS]]


@app.get("/api/today")
def get_today():
    return {"signals": build_today_queue()}
