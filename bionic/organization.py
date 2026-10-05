"""Organizational records: what Bionic Company itself authors.

Domains, capabilities, provisions, initiatives and the bindings between
initiatives and domain work units live in one human-readable file,
``organization.yaml``, in the organization directory. They are records, not
signals: the organization declares them; domains never do.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .contract import ContractError

FILENAME = "organization.yaml"


DOMAIN_KINDS = {"autonomous", "external"}


@dataclass(frozen=True)
class Domain:
    """Who does work. ``autonomous``: a domain behind the contract. ``external``: work
    the organization does or buys outside its domains (by hand, a freelancer, a
    vendor); it is observed through manual signals, never directed."""

    id: str
    name: str
    status: str = "active"
    kind: str = "autonomous"

    def __post_init__(self) -> None:
        if self.kind not in DOMAIN_KINDS:
            raise ContractError(f"Unknown domain kind {self.kind!r}; allowed: {sorted(DOMAIN_KINDS)}")


@dataclass(frozen=True)
class Capability:
    id: str
    name: str
    description: str = ""


@dataclass(frozen=True)
class Provision:
    capability: str
    domain: str
    since: str = ""
    until: str = ""


@dataclass(frozen=True)
class Initiative:
    id: str
    name: str
    intent: str = ""
    status: str = "active"


@dataclass(frozen=True)
class Binding:
    """An initiative served, for a period, by one of a domain's work units."""

    initiative: str
    domain: str
    work_unit_ref: str
    since: str = ""
    until: str = ""


@dataclass(frozen=True)
class Flow:
    """One work unit feeding another within an initiative: a book a film adapts.

    Domains do not know each other, so no domain can report this; the
    organization records it. Work units are written ``<domain>/<work_unit_ref>``.
    """

    initiative: str
    source: str
    target: str
    relation: str
    note: str = ""


@dataclass(frozen=True)
class Source:
    """Where an adapter reads a domain's work unit. Not part of the contract."""

    domain: str
    path: Path


@dataclass(frozen=True)
class Organization:
    root: Path
    id: str
    name: str
    domains: dict[str, Domain] = field(default_factory=dict)
    capabilities: dict[str, Capability] = field(default_factory=dict)
    provisions: list[Provision] = field(default_factory=list)
    initiatives: dict[str, Initiative] = field(default_factory=dict)
    bindings: list[Binding] = field(default_factory=list)
    flows: list[Flow] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)

    @property
    def twin_dir(self) -> Path:
        return self.root / "twin"

    def initiative_for(self, domain: str, work_unit_ref: str) -> str | None:
        """The initiative a domain's work unit currently serves, if any."""

        for binding in self.bindings:
            if binding.domain == domain and binding.work_unit_ref == work_unit_ref and not binding.until:
                return binding.initiative
        return None

    def providers(self, capability: str) -> list[str]:
        return [p.domain for p in self.provisions if p.capability == capability and not p.until]

    def gaps(self) -> list[Capability]:
        """Capabilities the organization names but nobody currently provides."""

        return [c for c in self.capabilities.values() if not self.providers(c.id)]


def _by_id(items: list[dict[str, Any]], kind: type, what: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for raw in items or []:
        item = kind(**raw)
        if item.id in out:
            raise ContractError(f"Duplicate {what} id {item.id!r}")
        out[item.id] = item
    return out


def load(root: Path) -> Organization:
    path = root / FILENAME
    if not path.is_file():
        raise ContractError(f"No {FILENAME} in {root}")
    raw = yaml.safe_load(path.read_text("utf-8")) or {}
    org = raw.get("organization") or {}
    organization = Organization(
        root=root,
        id=org.get("id", ""),
        name=org.get("name", ""),
        domains=_by_id(raw.get("domains"), Domain, "domain"),
        capabilities=_by_id(raw.get("capabilities"), Capability, "capability"),
        provisions=[Provision(**p) for p in raw.get("provisions") or []],
        initiatives=_by_id(raw.get("initiatives"), Initiative, "initiative"),
        bindings=[Binding(**b) for b in raw.get("bindings") or []],
        flows=[Flow(**f) for f in raw.get("flows") or []],
        sources=[Source(domain=s["domain"], path=root / Path(s["path"]).expanduser())
                 for s in raw.get("sources") or []],
    )
    _check_references(organization)
    return organization


def _check_references(org: Organization) -> None:
    if not org.id:
        raise ContractError("organization.id is required")
    for p in org.provisions:
        if p.capability not in org.capabilities:
            raise ContractError(f"Provision names unknown capability {p.capability!r}")
        if p.domain not in org.domains:
            raise ContractError(f"Provision names unknown domain {p.domain!r}")
    for b in org.bindings:
        if b.initiative not in org.initiatives:
            raise ContractError(f"Binding names unknown initiative {b.initiative!r}")
        if b.domain not in org.domains:
            raise ContractError(f"Binding names unknown domain {b.domain!r}")
    bound = {f"{b.domain}/{b.work_unit_ref}" for b in org.bindings}
    for f in org.flows:
        if f.initiative not in org.initiatives:
            raise ContractError(f"Flow names unknown initiative {f.initiative!r}")
        for unit in (f.source, f.target):
            if unit not in bound:
                raise ContractError(f"Flow names work unit {unit!r}, which no binding declares")
    for s in org.sources:
        if s.domain not in org.domains:
            raise ContractError(f"Source names unknown domain {s.domain!r}")
