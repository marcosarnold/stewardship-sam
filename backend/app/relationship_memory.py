"""Confirmed structured relationship memory (PRD Section 15). Nothing
here is written until the fundraiser reviews and confirms the
extracted fields (Section 16, HITL) -- see POST /api/relationships/:id/notes.

Saved memory has real effects: `not_currently_interested` blocks ASK
in the policy engine (app.policy), and a saved follow-up date is
picked up by SIG2 (app.signals.broken_commitment) once due.
"""

import json
import threading
from datetime import datetime
from pathlib import Path

from app.config import AS_OF_DATE

_LOCK = threading.Lock()
_STORE_PATH = Path(__file__).resolve().parents[1] / "var" / "relationship_memory.json"


def _load() -> dict:
    if not _STORE_PATH.exists():
        return {}
    return json.loads(_STORE_PATH.read_text())


def _save(data: dict) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True))


def save_note(entity_id: int, fields: dict, raw_note: str) -> dict:
    entry = {
        "interest": fields.get("interest"),
        "communication_preference": fields.get("communication_preference"),
        "solicitation_status": fields.get("solicitation_status"),
        "follow_up_date": fields.get("follow_up_date"),
        "raw_note": raw_note,
        "recorded_at": datetime.combine(AS_OF_DATE, datetime.min.time()).isoformat(),
    }
    with _LOCK:
        data = _load()
        data.setdefault(str(entity_id), []).append(entry)
        _save(data)
    return entry


def latest_note(entity_id) -> dict | None:
    entries = _load().get(str(entity_id))
    return entries[-1] if entries else None


def not_currently_interested(entity_id) -> bool:
    note = latest_note(entity_id)
    return bool(note and note.get("solicitation_status") == "not_currently_interested")


def all_follow_up_dates() -> dict[int, str]:
    """The latest saved follow_up_date per person, for SIG2 to fold in
    alongside real interaction follow-up dates.
    """
    result = {}
    for key, entries in _load().items():
        follow_up_date = entries[-1].get("follow_up_date")
        if follow_up_date:
            result[int(key)] = follow_up_date
    return result


def clear_all() -> None:
    """Test-only: resets the relationship memory store."""
    with _LOCK:
        _save({})
