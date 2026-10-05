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

from .contract import ORGANIZATION_DOMAIN, Signal
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
class Stretch:
    """An observed period of one domain working on a product."""

    domain: str
    first_signal_at: str
    last_signal_at: str
    signal_count: int = 0


@dataclass
class ProductView:
    product: str
    name: str
    custodian: str
    stretches: list[Stretch]
    releases: list[Signal]


@dataclass
class InitiativeView:
    initiative: str
    products: list[ProductView]
    participations: list[Participation]
    decisions: list[Signal]
    open_gates: list[Signal]
    cost: dict[str, float]
    unpriced: dict[str, float]
    signal_count: int


def signals_of(org: Organization, signals: Iterable[Signal], initiative: str) -> list[Signal]:
    """The signals about products of this initiative."""

    return sorted((s for s in signals if org.initiative_for(s.domain_id, s.work_unit_ref) == initiative
                   and s.domain_id != ORGANIZATION_DOMAIN),
                  key=lambda s: s.occurred_at)


def initiative_view(org: Organization, signals: Iterable[Signal], initiative: str) -> InitiativeView:
    mine = signals_of(org, signals, initiative)

    by_pair: dict[tuple[str, str], Participation] = {}
    total: dict[str, float] = defaultdict(float)
    gates: dict[str, Signal] = {}
    unpriced = {"count": 0, "seconds": 0.0}
    products: dict[str, ProductView] = {
        p.id: ProductView(p.id, p.name, p.custodian.domain if p.custodian else "", [], [])
        for p in org.products.values() if p.initiative == initiative
    }
    for s in mine:
        view = products[org.product_for(s.domain_id, s.work_unit_ref).id]
        last = view.stretches[-1] if view.stretches else None
        if last is None or last.domain != s.domain_id:
            last = Stretch(s.domain_id, s.occurred_at, s.occurred_at)
            view.stretches.append(last)
        last.last_signal_at = s.occurred_at
        last.signal_count += 1
        if s.type == "outcome.delivered":
            view.releases.append(s)
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
        products=sorted(products.values(), key=lambda v: v.stretches[0].first_signal_at if v.stretches else "~"),
        participations=sorted(by_pair.values(), key=lambda p: p.first_signal_at),
        decisions=[s for s in mine if s.type in ("decision.recorded", "gate.decided")],
        open_gates=sorted(gates.values(), key=lambda s: s.occurred_at),
        cost={k: round(v, 4) for k, v in total.items()},
        unpriced={"count": unpriced["count"], "seconds": round(unpriced["seconds"], 3)},
        signal_count=len(mine),
    )


def unbound(org: Organization, signals: Iterable[Signal]) -> dict[tuple[str, str], int]:
    """Domain work that reports signals but is no product of the organization: seen, not claimed."""

    counts: dict[tuple[str, str], int] = defaultdict(int)
    for s in signals:
        if s.domain_id != ORGANIZATION_DOMAIN and org.initiative_for(s.domain_id, s.work_unit_ref) is None:
            counts[(s.domain_id, s.work_unit_ref)] += 1
    return dict(counts)


def _gate_key(signal: Signal) -> str:
    gate: Any = signal.data.get("gate")
    return f"{signal.domain_id}:{signal.work_unit_ref}:{gate}" if gate else ""
