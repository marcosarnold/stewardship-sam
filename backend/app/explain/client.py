"""The LLM client interface. Tests inject a fake; production code goes
through OpenAIClient (PRD section 14). Every failure mode -- missing
key, missing package, network error, timeout, API error -- raises
LLMUnavailableError so the caller always has one thing to catch.
"""

import os
from typing import Protocol

from app import env  # noqa: F401  -- side effect: loads backend/.env


class LLMUnavailableError(Exception):
    """The LLM could not be reached, is unconfigured, or timed out."""


class LLMClient(Protocol):
    def complete(self, system_prompt: str, user_prompt: str) -> str: ...


class OpenAIClient:
    def __init__(self, model: str = "gpt-4o-mini", timeout_seconds: float = 5.0):
        self.model = model
        self.timeout_seconds = timeout_seconds

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise LLMUnavailableError("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMUnavailableError("openai package is not installed") from exc

        try:
            client = OpenAI(api_key=api_key, timeout=self.timeout_seconds)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # network error, timeout, API error, ...
            raise LLMUnavailableError(str(exc)) from exc


def default_client() -> LLMClient | None:
    """None when unconfigured, so explain() never attempts a network call
    without an API key -- the template path is the only path."""
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    return OpenAIClient()
