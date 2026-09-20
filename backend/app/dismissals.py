"""Dismissal state: hides a Today item without deleting the underlying
signal (it is still detected and computed every request; dismissal is
purely a display preference). Persisted to a JSON file so it survives
a page reload and can be undone.
"""

import json
import threading
from pathlib import Path

_LOCK = threading.Lock()
_STORE_PATH = Path(__file__).resolve().parents[1] / "var" / "dismissals.json"


def _load() -> dict:
    if not _STORE_PATH.exists():
        return {}
    return json.loads(_STORE_PATH.read_text())


def _save(data: dict) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True))


def dismiss(entity_id: int, reason: str | None = None) -> None:
    with _LOCK:
        data = _load()
        data[str(entity_id)] = {"entity_id": entity_id, "reason": reason}
        _save(data)


def restore(entity_id: int) -> None:
    with _LOCK:
        data = _load()
        data.pop(str(entity_id), None)
        _save(data)


def get_dismissal(entity_id: int) -> dict | None:
    return _load().get(str(entity_id))


def all_dismissals() -> dict:
    return _load()


def clear_all() -> None:
    """Test-only: resets dismissal state."""
    with _LOCK:
        _save({})
