"""BizOps, M1: intents on initiatives, their resolution and their lifecycle.

The organization's own decisions are records, like a domain's: an append-only
``decisions.jsonl`` in the organization directory, each line a signal in the
contract's envelope, reported by the ``bionic`` domain. Intents are a
projection over those decisions plus what the domains report; ``in progress``
is derived from domain signals, never declared. See docs/m1-model.md.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contract import ORGANIZATION_DOMAIN, Actor, ContractError, Signal
from .organization import Organization

DECISIONS_FILENAME = "decisions.jsonl"

# transition -> the statuses it may follow
TRANSITIONS: dict[str, set[str]] = {
    "stated": set(),
    "resolved": {"stated", "resolved", "gap"},
    "gap": {"stated", "resolved", "gap"},
    "option_chosen": {"gap"},
    "handed_off": {"resolved"},
    "fulfilled": {"handed_off", "in_progress"},
    "withdrawn": {"stated", "resolved", "gap", "handed_off", "in_progress"},
}
GAP_OPTIONS = ("wait", "external", "adapt")


@dataclass
class Intent:
    id: str
    initiative: str
    capability: str
    desired_outcome: str
    product: str = ""
    draws_on: list[dict[str, str]] = field(default_factory=list)
    priority: str = ""
    deadline: str = ""
    status: str = "stated"
    provider: str = ""
    rationale: str = ""
    options: list[str] = field(default_factory=list)
    option: str = ""
    handed_off_at: str = ""
    progress: list[Signal] = field(default_factory=list)
    history: list[Signal] = field(default_factory=list)


@dataclass
class Resolution:
    transition: str  # "resolved" or "gap"
    provider: str
    rationale: str
    options: list[str] = field(default_factory=list)


class DecisionLog:
    """The organization's own records: append-only, versioned with the organization."""

    def __init__(self, org: Organization) -> None:
        self.org = org
        self.path = org.root / DECISIONS_FILENAME

    def read(self) -> list[Signal]:
        if not self.path.is_file():
            return []
        with self.path.open(encoding="utf-8") as handle:
            return [Signal.from_dict(json.loads(line)) for line in handle if line.strip()]

    def record(self, intent_id: str, transition: str, *, actor: Actor, summary: str, capability: str,
               at: str = "", **data: Any) -> Signal:
        at = at or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        signal = Signal(
            id=f"{ORGANIZATION_DOMAIN}:{intent_id}:{transition}:{at}",
            type="decision.recorded",
            occurred_at=at,
            domain_id=ORGANIZATION_DOMAIN,
            work_unit_ref=intent_id,
            actor=actor,
            capability=capability,
            summary=summary,
            data={"intent": intent_id, "transition": transition, **data},
            source={"kind": DECISIONS_FILENAME, "ref": f"{intent_id}:{transition}"},
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(signal.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return signal


def intents(org: Organization, decisions: Iterable[Signal], signals: Iterable[Signal] = ()) -> dict[str, Intent]:
    """Every intent's current state: the organization's decisions, then the domains' signals."""

    out: dict[str, Intent] = {}
    for d in sorted(decisions, key=lambda s: s.occurred_at):
        name, transition = d.data.get("intent"), d.data.get("transition")
        if not name or not transition:
            continue
        if transition == "stated":
            out[name] = Intent(
                id=name, initiative=d.data["initiative"], capability=d.capability,
                desired_outcome=d.data.get("desired_outcome", ""), product=d.data.get("product", ""),
                draws_on=list(d.data.get("draws_on") or []), priority=d.data.get("priority", ""),
                deadline=d.data.get("deadline", ""),
            )
        intent = out.get(name)
        if intent is None:
            continue
        intent.history.append(d)
        if transition in ("resolved", "gap"):
            intent.provider = d.data.get("provider", "")
            intent.rationale = d.data.get("rationale", "")
            intent.options = list(d.data.get("options") or [])
            intent.option = ""
        if transition == "option_chosen":
            intent.option = d.data.get("option", "")
            continue
        if transition == "handed_off":
            intent.handed_off_at = d.occurred_at
        intent.status = transition

    for intent in out.values():
        if intent.status == "handed_off":
            intent.progress = _progress(org, intent, signals)
            if intent.progress:
                intent.status = "in_progress"
    return out


def _progress(org: Organization, intent: Intent, signals: Iterable[Signal]) -> list[Signal]:
    """The provider's own signals about the intent's product, after the handoff."""

    found = []
    for s in signals:
        if s.domain_id != intent.provider or s.occurred_at < intent.handed_off_at:
            continue
        product = org.product_for(s.domain_id, s.work_unit_ref)
        if product is None:
            continue
        if intent.product and product.id != intent.product:
            continue
        if not intent.product and (product.initiative != intent.initiative or s.capability != intent.capability):
            continue
        found.append(s)
    return sorted(found, key=lambda s: s.occurred_at)


def resolve(org: Organization, signals: Iterable[Signal], intent: Intent) -> Resolution:
    """Relate the need to the capabilities available. A rule, explained; a person accepts it."""

    capability = org.capabilities.get(intent.capability)
    if capability is None:
        raise ContractError(f"Unknown capability {intent.capability!r}")
    providers = org.providers(intent.capability)
    observed = sorted({s.domain_id for s in signals
                       if s.capability == intent.capability and s.domain_id != ORGANIZATION_DOMAIN
                       and org.initiative_for(s.domain_id, s.work_unit_ref) == intent.initiative})
    product = org.products.get(intent.product) if intent.product else None
    custodian = product.custodian.domain if product and product.custodian else ""

    notes = []
    if observed:
        notes.append(f"this initiative's {capability.name.lower()} so far was done by {', '.join(observed)}")

    if not providers:
        planned = [p.domain for p in org.provisions if p.capability == intent.capability and not p.until
                   and org.domains[p.domain].status == "planned"]
        external = [d for d in observed if org.domains[d].kind == "external"]
        options = [
            "wait: keep the need open and visible",
            "external: have it done outside the domains" + (f" (as before: {', '.join(external)})" if external else ""),
            "adapt: create the capability (M2)" + (f"; planned provider: {', '.join(planned)}" if planned else ""),
        ]
        rationale = f"No active domain provides {capability.name.lower()}."
        if notes:
            rationale += " Observed: " + "; ".join(notes) + "."
        return Resolution("gap", "", rationale, options)

    if custodian in providers:
        chosen, why = custodian, f"{custodian} already has custody of {product.id}"
    elif len(providers) == 1:
        chosen, why = providers[0], f"{providers[0]} is the only active provider"
    else:
        ranked = sorted(providers, key=lambda d: (d not in observed, d))
        chosen, why = ranked[0], f"{ranked[0]} chosen among {', '.join(providers)}" + (
            ", having done this initiative's work before" if ranked[0] in observed else "")
    rationale = f"{why}."
    if notes:
        rationale += " Observed: " + "; ".join(notes) + "."
    if product and custodian and custodian != chosen:
        rationale += f" Custody of {product.id} moves from {custodian} to {chosen}."
    return Resolution("resolved", chosen, rationale)


def check_transition(intent: Intent | None, transition: str) -> None:
    if transition == "stated":
        if intent is not None:
            raise ContractError(f"Intent {intent.id!r} already exists")
        return
    if intent is None:
        raise ContractError("No such intent")
    if intent.status not in TRANSITIONS[transition]:
        raise ContractError(f"Intent {intent.id} is {intent.status}; it cannot become {transition}")


def flows(org: Organization, all_intents: Iterable[Intent]) -> list[dict[str, str]]:
    """Declared flows, plus those intents create: planned while open, observed once fulfilled."""

    out = [{"source": f.source, "target": f.target, "relation": f.relation, "state": "observed", "via": ""}
           for f in org.flows]
    for intent in all_intents:
        if not intent.product or intent.status == "withdrawn":
            continue
        for source in intent.draws_on:
            out.append({"source": source["product"], "target": intent.product,
                        "relation": source.get("relation", "feeds"),
                        "state": "observed" if intent.status == "fulfilled" else "planned", "via": intent.id})
    return out


def organization_signals(path: Path) -> Iterable[Signal]:
    """The adapter for the organization's own decisions: they already are signals."""

    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        return [Signal.from_dict(json.loads(line)) for line in handle if line.strip()]
