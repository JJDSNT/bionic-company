"""Organizational records: what Bionic Company itself authors.

Domains, capabilities, provisions, initiatives, products and their custody
live in one human-readable file,
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


AFTER_RELEASE = {"frozen", "editions"}


@dataclass(frozen=True)
class Custody:
    """A period during which a domain works on a product, under its own reference for it."""

    domain: str
    ref: str
    since: str = ""
    until: str = ""


@dataclass(frozen=True)
class Product:
    """What the organization makes and releases: a book, a film.

    Its identity is the organization's, not a domain's: custody moves between
    domains (a book written by hand, then in KDP Studio) and the product stays
    the same. It evolves in versions; a release freezes a version. ``frozen``:
    nothing released changes (fiction). ``editions``: a later edition may revise
    it (a technical book).
    """

    id: str
    name: str
    initiative: str
    kind: str = ""
    after_release: str = "frozen"
    custody: tuple[Custody, ...] = ()

    def __post_init__(self) -> None:
        if self.after_release not in AFTER_RELEASE:
            raise ContractError(f"Unknown after_release {self.after_release!r}; allowed: {sorted(AFTER_RELEASE)}")
        object.__setattr__(self, "custody", tuple(c if isinstance(c, Custody) else Custody(**c)
                                                  for c in self.custody))

    @property
    def custodian(self) -> Custody | None:
        """Who works on it now."""

        return next((c for c in self.custody if not c.until), None)


@dataclass(frozen=True)
class Flow:
    """One product feeding another: a film adapting a book, a film enriching it.

    Domains do not know each other, so no domain can report this; the
    organization records it.
    """

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
    products: dict[str, Product] = field(default_factory=dict)
    flows: list[Flow] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)

    @property
    def twin_dir(self) -> Path:
        return self.root / "twin"

    def product_for(self, domain: str, ref: str) -> Product | None:
        """The product a domain's own reference stands for, in any period of custody."""

        for product in self.products.values():
            if any(c.domain == domain and c.ref == ref for c in product.custody):
                return product
        return None

    def initiative_for(self, domain: str, ref: str) -> str | None:
        product = self.product_for(domain, ref)
        return product.initiative if product else None

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
        products=_by_id(raw.get("products"), Product, "product"),
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
    claimed: dict[tuple[str, str], str] = {}
    for product in org.products.values():
        if product.initiative not in org.initiatives:
            raise ContractError(f"Product {product.id!r} names unknown initiative {product.initiative!r}")
        if sum(1 for c in product.custody if not c.until) > 1:
            raise ContractError(f"Product {product.id!r} has more than one current custodian")
        for c in product.custody:
            if c.domain not in org.domains:
                raise ContractError(f"Product {product.id!r} names unknown domain {c.domain!r}")
            other = claimed.setdefault((c.domain, c.ref), product.id)
            if other != product.id:
                raise ContractError(f"{c.domain} reference {c.ref!r} is claimed by {other!r} and {product.id!r}")
    for f in org.flows:
        for end in (f.source, f.target):
            if end not in org.products:
                raise ContractError(f"Flow names unknown product {end!r}")
    for s in org.sources:
        if s.domain not in org.domains:
            raise ContractError(f"Source names unknown domain {s.domain!r}")
