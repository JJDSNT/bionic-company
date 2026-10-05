"""The organizational contract: what a domain reports, independent of how it works.

See docs/m0-model.md. Nothing here assumes a language, storage or transport;
this module is one implementation of the JSON envelopes the document defines.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

CONTRACT_VERSION = "0.1"

ACTOR_KINDS = {"human", "agent", "system"}

SIGNAL_TYPES = {
    "work.started",
    "decision.recorded",
    "gate.opened",
    "gate.decided",
    "version.recorded",
    "cost.incurred",
    "outcome.delivered",
    "blocker.raised",
    "blocker.cleared",
}


class ContractError(ValueError):
    """A record does not satisfy the organizational contract."""


def utc(timestamp: str) -> str:
    """Normalise an ISO 8601 timestamp to UTC, second precision, with a Z."""

    try:
        moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"Not an ISO 8601 timestamp: {timestamp!r}") from error
    if moment.tzinfo is None:
        raise ContractError(f"Timestamp without a time zone: {timestamp!r}")
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Actor:
    id: str
    kind: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ContractError("Actor id must not be empty")
        if self.kind not in ACTOR_KINDS:
            raise ContractError(f"Unknown actor kind {self.kind!r}; allowed: {sorted(ACTOR_KINDS)}")


@dataclass(frozen=True)
class Cost:
    amount: float
    currency: str
    kind: str = "compute"


@dataclass(frozen=True)
class Signal:
    """Something that already happened, reported by a domain."""

    id: str
    type: str
    occurred_at: str
    domain_id: str
    work_unit_ref: str
    actor: Actor
    capability: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    cost: Cost | None = None
    source: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in SIGNAL_TYPES:
            raise ContractError(f"Unknown signal type {self.type!r}; allowed: {sorted(SIGNAL_TYPES)}")
        for name in ("id", "domain_id", "work_unit_ref", "capability"):
            if not str(getattr(self, name)).strip():
                raise ContractError(f"Signal {name} must not be empty")
        object.__setattr__(self, "occurred_at", utc(self.occurred_at))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Signal:
        cost = raw.get("cost")
        return cls(**{**raw, "actor": Actor(**raw["actor"]), "cost": Cost(**cost) if cost else None})
