"""Records what a fundraiser did after reviewing a "Prepare action"
brief -- Sam never sends, calls, or writes to GiveCampus data itself
(PRD Section 16); this is Sam's own local log, not the CRM.
"""

import json
import threading
from datetime import datetime
from pathlib import Path

from app.config import AS_OF_DATE

OUTCOMES = frozenset({"done", "not_now", "dismissed"})

_LOCK = threading.Lock()
_STORE_PATH = Path(__file__).resolve().parents[1] / "var" / "action_outcomes.json"


def _load() -> dict:
    if not _STORE_PATH.exists():
        return {}
    return json.loads(_STORE_PATH.read_text())


def _save(data: dict) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True))


def record_outcome(entity_id, action: str | None, outcome: str, note: str | None = None) -> dict:
    if outcome not in OUTCOMES:
        raise ValueError(f"Unknown outcome: {outcome}")

    entry = {
        "entity_id": entity_id if isinstance(entity_id, str) else int(entity_id),
        "action": action,
        "outcome": outcome,
        "note": note,
        "recorded_at": datetime.combine(AS_OF_DATE, datetime.min.time()).isoformat(),
    }
    with _LOCK:
        data = _load()
        data.setdefault(str(entity_id), []).append(entry)
        _save(data)
    return entry


def latest_outcome(entity_id) -> dict | None:
    entries = _load().get(str(entity_id))
    return entries[-1] if entries else None


def clear_all() -> None:
    """Test-only: resets the outcome log."""
    with _LOCK:
        _save({})
