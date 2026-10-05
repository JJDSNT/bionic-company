"""The Organizational Twin, M0: an append-only signal log and projections over it.

The log is the twin's own copy of what domains reported. It never depends on a
domain keeping its history. Projections are computed from the log on demand;
they are disposable by construction.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .contract import Signal
from .organization import Organization

LOG_FILENAME = "signals.jsonl"


class SignalLog:
    def __init__(self, directory: Path) -> None:
        self.path = directory / LOG_FILENAME

    def read(self) -> list[Signal]:
        if not self.path.is_file():
            return []
        with self.path.open(encoding="utf-8") as handle:
            return [Signal.from_dict(json.loads(line)) for line in handle if line.strip()]

    def append(self, signals: Iterable[Signal]) -> int:
        """Append the signals not already in the log; return how many were new."""

        known = {s.id for s in self.read()}
        new = []
        for signal in signals:
            if signal.id not in known:
                known.add(signal.id)
                new.append(signal)
        if new:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                for signal in sorted(new, key=lambda s: s.occurred_at):
                    handle.write(json.dumps(signal.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return len(new)


@dataclass
class Participation:
    domain: str
    capability: str
    first_signal_at: str
    last_signal_at: str
    signal_count: int = 0
    cost: dict[str, float] = field(default_factory=dict)


@dataclass
class WorkUnit:
    unit: str
    domain: str
    capabilities: list[str]
    first_signal_at: str
    last_signal_at: str
    signal_count: int


@dataclass
class InitiativeView:
    initiative: str
    work_units: list[WorkUnit]
    participations: list[Participation]
    decisions: list[Signal]
    open_gates: list[Signal]
    cost: dict[str, float]
    unpriced: dict[str, float]
    signal_count: int


def signals_of(org: Organization, signals: Iterable[Signal], initiative: str) -> list[Signal]:
    """The signals whose work unit is bound to this initiative."""

    return sorted((s for s in signals if org.initiative_for(s.domain_id, s.work_unit_ref) == initiative),
                  key=lambda s: s.occurred_at)


def initiative_view(org: Organization, signals: Iterable[Signal], initiative: str) -> InitiativeView:
    mine = signals_of(org, signals, initiative)

    by_pair: dict[tuple[str, str], Participation] = {}
    total: dict[str, float] = defaultdict(float)
    gates: dict[str, Signal] = {}
    unpriced = {"count": 0, "seconds": 0.0}
    units: dict[str, WorkUnit] = {}
    for s in mine:
        name = f"{s.domain_id}/{s.work_unit_ref}"
        unit = units.get(name)
        if unit is None:
            unit = units[name] = WorkUnit(name, s.domain_id, [], s.occurred_at, s.occurred_at, 0)
        unit.last_signal_at = s.occurred_at
        unit.signal_count += 1
        if s.capability not in unit.capabilities:
            unit.capabilities.append(s.capability)
        key = (s.domain_id, s.capability)
        p = by_pair.get(key)
        if p is None:
            p = by_pair[key] = Participation(s.domain_id, s.capability, s.occurred_at, s.occurred_at)
        p.last_signal_at = s.occurred_at
        p.signal_count += 1
        if s.cost:
            p.cost[s.cost.currency] = round(p.cost.get(s.cost.currency, 0) + s.cost.amount, 4)
            total[s.cost.currency] += s.cost.amount
        elif s.type == "cost.incurred":
            # Spend the domain measured but did not price: visible, never guessed.
            unpriced["count"] += 1
            unpriced["seconds"] += float(s.data.get("seconds") or 0)
        gate = _gate_key(s)
        if s.type == "gate.opened" and gate:
            gates[gate] = s
        elif s.type == "gate.decided" and gate:
            gates.pop(gate, None)

    return InitiativeView(
        initiative=initiative,
        work_units=sorted(units.values(), key=lambda u: u.first_signal_at),
        participations=sorted(by_pair.values(), key=lambda p: p.first_signal_at),
        decisions=[s for s in mine if s.type in ("decision.recorded", "gate.decided")],
        open_gates=sorted(gates.values(), key=lambda s: s.occurred_at),
        cost={k: round(v, 4) for k, v in total.items()},
        unpriced={"count": unpriced["count"], "seconds": round(unpriced["seconds"], 3)},
        signal_count=len(mine),
    )


def unbound(org: Organization, signals: Iterable[Signal]) -> dict[tuple[str, str], int]:
    """Work units that report signals but serve no initiative: the twin sees them, nobody claimed them."""

    counts: dict[tuple[str, str], int] = defaultdict(int)
    for s in signals:
        if org.initiative_for(s.domain_id, s.work_unit_ref) is None:
            counts[(s.domain_id, s.work_unit_ref)] += 1
    return dict(counts)


def _gate_key(signal: Signal) -> str:
    gate: Any = signal.data.get("gate")
    return f"{signal.domain_id}:{signal.work_unit_ref}:{gate}" if gate else ""
