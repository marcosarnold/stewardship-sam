"""explain(): the one interface Today, the Relationship View, Ask Sam
(issues 014-015), and Community View (issue 011) all call for a
grounded "why" (PRD Section 13).
"""

from app.explain import cache as cache_module
from app.explain.client import LLMClient, LLMUnavailableError, default_client
from app.explain.prompts import SYSTEM_PROMPT, build_user_prompt
from app.explain.templates import render_template
from app.explain.types import EvidencePayload, ExplanationResult
from app.explain.validation import validate

_UNSET = object()


def explain(
    payload: EvidencePayload,
    client: LLMClient | None = _UNSET,  # type: ignore[assignment]
    use_cache: bool = True,
) -> ExplanationResult:
    """Explains one signal. `client` defaults to the configured OpenAI
    client (or None if unconfigured); pass an explicit client (or None)
    to override, which is how tests inject a mock or force the template
    path.
    """
    key = cache_module.evidence_hash(payload)
    if use_cache:
        cached = cache_module.get(key)
        if cached is not None:
            return cached

    resolved_client = default_client() if client is _UNSET else client

    result = ExplanationResult(text=render_template(payload), source="template")

    if resolved_client is not None:
        try:
            raw = resolved_client.complete(SYSTEM_PROMPT, build_user_prompt(payload))
            if validate(raw, payload):
                result = ExplanationResult(text=raw.strip(), source="llm")
        except LLMUnavailableError:
            pass

    if use_cache:
        cache_module.set(key, result)
    return result
