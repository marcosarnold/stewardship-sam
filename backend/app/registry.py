"""Signal registry: detectors plug in via `register`, and the priority
queue reads them all through `all_signals` without ever importing a
specific detector module. A new detector (SIG4, SIG6, ...) registers
itself and starts appearing on Today; no ranking code changes.
"""

from typing import Callable

from app.context import Context
from app.models import Signal

Detector = Callable[[Context], list[Signal]]

_DETECTORS: list[Detector] = []


def register(detector: Detector) -> Detector:
    """Use as a decorator on a module-level `detect(context)` function."""
    _DETECTORS.append(detector)
    return detector


def unregister(detector: Detector) -> None:
    if detector in _DETECTORS:
        _DETECTORS.remove(detector)


def registered_detectors() -> list[Detector]:
    return list(_DETECTORS)


def all_signals(context: Context) -> list[Signal]:
    signals: list[Signal] = []
    for detector in _DETECTORS:
        signals.extend(detector(context))
    return signals
