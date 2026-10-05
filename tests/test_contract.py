"""Everything the package produces satisfies the published, language-neutral contract."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from bionic import bizops, organization
from bionic.adapters import MANIFESTS, cine_toaster, kdp_studio, manual
from bionic.contract import Actor

from test_m0 import HISTORY, make_book, make_production
from test_m1 import make_org, state

CONTRACT = Path(__file__).parent.parent / "contract"
SCHEMAS = {p.name: json.loads(p.read_text("utf-8")) for p in CONTRACT.glob("*.schema.json")}
REGISTRY = Registry().with_resources(
    (name, Resource.from_contents(schema)) for name, schema in SCHEMAS.items()
).with_resources((schema["$id"], Resource.from_contents(schema)) for schema in SCHEMAS.values())


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(SCHEMAS[name], registry=REGISTRY)


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_schemas_are_valid(name):
    Draft202012Validator.check_schema(SCHEMAS[name])


def test_adapter_signals_satisfy_the_contract(tmp_path):
    book = make_book(tmp_path / "book", HISTORY)
    production = make_production(tmp_path / "film")
    (tmp_path / "manual.yaml").write_text(
        "work_unit_ref: w\ncapability: c\nsignals:\n"
        "  - {id: a, type: version.recorded, occurred_at: '2025-07-17T20:04:58Z', summary: s, evidence: e}\n",
        "utf-8")
    signals = [*kdp_studio.signals(book), *cine_toaster.signals(production), *manual.signals(tmp_path / "manual.yaml")]
    check = validator("signal.schema.json")
    for signal in signals:
        check.validate(signal.to_dict())
    assert {s.domain_id for s in signals} == {"kdp-studio", "cine-toaster", "manual"}


@pytest.mark.parametrize("domain", sorted(MANIFESTS))
def test_manifests_satisfy_the_contract(domain):
    validator("capability-manifest.schema.json").validate(MANIFESTS[domain])


def test_organization_decisions_and_envelopes_satisfy_the_contract(tmp_path):
    org = make_org(tmp_path / "org")
    state(org, "enrich", "--initiative", "story", "--capability", "editorial-production", "--product", "novel",
          "--outcome", "Enrich the novel", "--draws-on", "film:enriches", "--at", "2026-10-05T10:00:00Z")
    intent = bizops.intents(org, bizops.DecisionLog(org).read())["enrich"]
    intent.provider = "kdp-studio"

    envelope = bizops.envelope(org, intent, issued_by=Actor("bionic:author", "human"), issued_at="2026-10-05T11:00:00Z")
    validator("intent.schema.json").validate(envelope)
    assert "initiative" not in json.dumps(envelope)  # the initiative never crosses the boundary
    for decision in bizops.DecisionLog(org).read():
        validator("signal.schema.json").validate(decision.to_dict())


def test_the_example_organizations_records_satisfy_the_contract():
    root = Path(__file__).parent.parent / "examples" / "organization"
    organization.load(root)
    check = validator("signal.schema.json")
    for line in (root / "decisions.jsonl").read_text("utf-8").splitlines():
        check.validate(json.loads(line))
