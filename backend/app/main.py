"""FastAPI app exposing the Today queue."""

from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.action_outcomes import record_outcome
from app.action_prep import build_action_brief
from app.ask_sam import ask
from app.demo_reset import reset_demo_state
from app.relationship_notes import extract_note
from app.relationship_memory import latest_note, save_note
from app.communities import find_community, get_community_members, list_communities
from app.community_metrics import compute_all_metrics
from app.community_graph_view import build_community_graph
from app.community_view import build_community_view
from app.connectors import top_connectors
from app.config import TODAY_QUEUE_MAX_ITEMS
from app.context import build_context
from app.db import load_table
from app.dismissals import dismiss, restore
from app.explain import explain
from app.explain.from_signal import payload_from_signal_dict
from app.followups import build_followups
from app.graph import get_graph
from app.priority_queue import build_queue, summarize_counts, summarize_held_back
from app.relationships import build_relationship, find_constituent
from app.signals.community_cooling import detect as detect_community_cooling
from app.timeline import TIMELINE_TYPES, build_timeline


@asynccontextmanager
async def _lifespan(app: FastAPI):
    get_graph()  # built once at startup and cached (issue 009), not on first request
    yield


app = FastAPI(title="Stewardship Sam API", lifespan=_lifespan)

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
def dismiss_today_item(entity_id: str, body: DismissRequest = DismissRequest()):
    # entity_id is an int for a constituent, a community slug (e.g.
    # "alumni-board") for a community -- dismissals.py keys by str either way.
    dismiss(entity_id, body.reason)
    return {"entity_id": entity_id, "dismissed": True, "reason": body.reason}


@app.post("/api/today/{entity_id}/restore")
def restore_today_item(entity_id: str):
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
    affiliations = load_table("affiliations")

    relationship = build_relationship(entity_id, context, degrees, activities, affiliations)
    if relationship is None:
        raise HTTPException(
            status_code=404,
            detail=f"No relationship record for id {entity_id}: unknown, not an individual, or deceased.",
        )

    relationship["signals"] = [_with_explanation(s) for s in relationship["signals"]]
    return relationship


@app.get("/api/relationships/{entity_id}/timeline")
def get_relationship_timeline(entity_id: int, types: str | None = None, page: int = 1):
    constituents = load_table("constituents")
    if find_constituent(entity_id, constituents) is None:
        raise HTTPException(
            status_code=404,
            detail=f"No relationship record for id {entity_id}: unknown, not an individual, or deceased.",
        )

    requested_types = None
    if types is not None:
        requested_types = [t for t in types.split(",") if t in TIMELINE_TYPES]

    return build_timeline(
        entity_id,
        gifts=load_table("gifts"),
        interactions=load_table("interactions"),
        events=load_table("events"),
        event_attendance=load_table("event_attendance"),
        career_history=load_table("career_history"),
        opportunities=load_table("opportunities"),
        types=requested_types,
        page=page,
    )


@app.get("/api/communities")
def get_communities():
    return {"communities": list_communities(get_graph())}


@app.get("/api/communities/{community_id}/members")
def get_communities_members(community_id: str, page: int = 1):
    result = get_community_members(get_graph(), community_id, page)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No community with id {community_id}.")
    return result


@app.get("/api/communities/metrics")
def get_all_communities_metrics():
    """All 79 communities' metrics in one call, so the sortable table on
    the Communities page doesn't fire 79 separate requests.
    """
    return compute_all_metrics(
        get_graph(),
        gifts=load_table("gifts"),
        interactions=load_table("interactions"),
        event_attendance=load_table("event_attendance"),
        staff=load_table("staff"),
    )


@app.get("/api/communities/{community_id}/metrics")
def get_communities_metrics(community_id: str):
    graph = get_graph()
    if find_community(graph, community_id) is None:
        raise HTTPException(status_code=404, detail=f"No community with id {community_id}.")

    all_metrics = compute_all_metrics(
        graph,
        gifts=load_table("gifts"),
        interactions=load_table("interactions"),
        event_attendance=load_table("event_attendance"),
        staff=load_table("staff"),
    )
    return all_metrics[community_id]


@app.get("/api/community/{community_id}")
def get_community_view(community_id: str):
    graph = get_graph()
    context = build_context()
    cooling_signals = detect_community_cooling(context)

    view = build_community_view(graph, community_id, context, load_table("event_attendance"), cooling_signals)
    if view is None:
        raise HTTPException(status_code=404, detail=f"No community with id {community_id}.")
    return view


@app.get("/api/communities/{community_id}/connectors")
def get_communities_connectors(community_id: str, limit: int = 10):
    """Potential connectors from observed membership overlap (PRD Section
    8). Overlap is shared institutional context, not friendship or
    influence (G5): it never implies a direct social relationship.
    """
    connectors = top_connectors(get_graph(), community_id, build_context(), limit)
    if connectors is None:
        raise HTTPException(status_code=404, detail=f"No community with id {community_id}.")
    return {"community_id": community_id, "connectors": connectors}


@app.get("/api/community/{community_id}/graph")
def get_community_graph(community_id: str):
    result = build_community_graph(get_graph(), community_id, build_context())
    if result is None:
        raise HTTPException(status_code=404, detail=f"No community with id {community_id}.")
    return result


class AskRequest(BaseModel):
    question: str


@app.post("/api/ask")
def post_ask(body: AskRequest):
    context = build_context()
    degrees = load_table("degrees")
    activities = load_table("activities")
    affiliations = load_table("affiliations")
    return ask(body.question, context, degrees, activities, affiliations)


@app.get("/api/relationships/{entity_id}/prepare-action")
def get_prepare_action(entity_id: int):
    brief = build_action_brief(entity_id, build_context())
    if brief is None:
        raise HTTPException(
            status_code=404,
            detail=f"No relationship record for id {entity_id}: unknown, not an individual, or deceased.",
        )
    return brief


class ConfirmActionRequest(BaseModel):
    action: str | None = None
    outcome: str  # "done" | "not_now" | "dismissed"
    note: str | None = None


@app.post("/api/relationships/{entity_id}/confirm-action")
def post_confirm_action(entity_id: int, body: ConfirmActionRequest):
    """Records what the fundraiser did -- Sam never sends, calls, or
    writes to GiveCampus data itself (Section 16). A "dismissed" outcome
    also dismisses the Today item, reusing issue 007's dismissal store,
    so Today reflects the outcome.
    """
    try:
        entry = record_outcome(entity_id, body.action, body.outcome, body.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if body.outcome == "dismissed":
        dismiss(entity_id, body.note)

    return entry


class ExtractNoteRequest(BaseModel):
    note: str


@app.post("/api/relationships/{entity_id}/notes/extract")
def post_extract_note(entity_id: int, body: ExtractNoteRequest):
    """Preview only -- extraction never saves anything (Section 16); the
    fundraiser reviews and edits via POST .../notes before it's kept.
    """
    return extract_note(body.note)


class SaveNoteRequest(BaseModel):
    interest: str | None = None
    communication_preference: str | None = None
    solicitation_status: str | None = None
    follow_up_date: str | None = None
    raw_note: str = ""


@app.post("/api/relationships/{entity_id}/notes")
def post_save_note(entity_id: int, body: SaveNoteRequest):
    """Saves fundraiser-confirmed (possibly edited) structured memory.
    Has real effects: not_currently_interested blocks ASK in the policy
    engine, and a saved follow-up date is picked up by SIG2 once due.
    """
    return save_note(entity_id, body.model_dump(), body.raw_note)


@app.get("/api/relationships/{entity_id}/notes/latest")
def get_latest_note(entity_id: int):
    note = latest_note(entity_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"No saved note for id {entity_id}.")
    return note


@app.post("/api/demo/reset")
def post_demo_reset():
    """Returns the app to a deterministic demo state (issue 019)."""
    return reset_demo_state()
