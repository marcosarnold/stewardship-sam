"""The shared Signal record every detector returns."""

from dataclasses import dataclass, field


@dataclass
class Signal:
    entity_type: str  # "constituent" or "community"
    entity_id: int
    entity_name: str
    signal_id: str  # e.g. "SIG1"
    action: str  # e.g. "THANK"
    evidence: list[str] = field(default_factory=list)
    urgency_date: str | None = None  # ISO date driving urgency, when applicable
    urgency_amount: float | None = None  # e.g. gift amount, used for provisional ordering
    channel_hint: str | None = None  # e.g. "email", or None when no allowed channel is known

    def to_dict(self) -> dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "signal_id": self.signal_id,
            "action": self.action,
            "evidence": self.evidence,
            "urgency_date": self.urgency_date,
            "urgency_amount": self.urgency_amount,
            "channel_hint": self.channel_hint,
        }
