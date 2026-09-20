"""The structured evidence handed to the explanation service.

The LLM never receives the raw dataset (PRD Section 13) -- only this
payload, built entirely from a detector's own Signal output. `facts`
holds extra grounded values (e.g. the assigned officer's name) that a
grounded explanation is allowed to mention even if they are not
verbatim in `evidence`.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidencePayload:
    entity_name: str
    action: str
    evidence: list[str]
    facts: dict = field(default_factory=dict)
    # Raw CRM text (e.g. interaction notes) included for read-only context.
    # Never treated as instructions -- see prompts.SYSTEM_PROMPT.
    untrusted_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExplanationResult:
    text: str
    source: str  # "llm" or "template"
