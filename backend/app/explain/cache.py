"""In-memory cache keyed by a hash of the evidence payload, so repeat
requests for the same signal don't re-call the LLM."""

import hashlib
import json

from app.explain.types import EvidencePayload, ExplanationResult

_cache: dict[str, ExplanationResult] = {}


def evidence_hash(payload: EvidencePayload) -> str:
    canonical = json.dumps(
        {
            "entity_name": payload.entity_name,
            "action": payload.action,
            "evidence": payload.evidence,
            "facts": payload.facts,
            "untrusted_notes": payload.untrusted_notes,
        },
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def get(key: str) -> ExplanationResult | None:
    return _cache.get(key)


def set(key: str, result: ExplanationResult) -> None:
    _cache[key] = result


def clear() -> None:
    _cache.clear()
