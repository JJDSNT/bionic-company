from pathlib import Path

import pytest
import yaml

from bionic import bizops, organization, twin
from bionic.cli import main
from bionic.contract import Actor, ContractError, Signal


def make_org(root: Path) -> organization.Organization:
    root.mkdir(parents=True)
    (root / "organization.yaml").write_text(yaml.safe_dump({
        "organization": {"id": "test", "name": "Test"},
        "domains": [{"id": "kdp-studio", "name": "KDP Studio"}, {"id": "pulse", "name": "Pulse", "status": "planned"},
                    {"id": "manual", "name": "By hand", "kind": "external"}],
        "capabilities": [{"id": "editorial-production", "name": "Editorial production"},
                         {"id": "market-relationships", "name": "Market relationships"}],
        "provisions": [{"capability": "editorial-production", "domain": "kdp-studio"},
                       {"capability": "market-relationships", "domain": "pulse"}],
        "initiatives": [{"id": "story", "name": "Story"}],
        "products": [
            {"id": "novel", "name": "Novel", "initiative": "story",
             "custody": [{"domain": "manual", "ref": "novel-by-hand"}]},
            {"id": "film", "name": "Film", "initiative": "story"},
        ],
        "flows": [{"source": "novel", "target": "film", "relation": "adapted into"}],
    }), "utf-8")
    return organization.load(root)


def by_hand(at: str) -> Signal:
    return Signal(id=f"manual:{at}", type="version.recorded", occurred_at=at, domain_id="manual",
                  work_unit_ref="novel-by-hand", actor=Actor("manual:author", "human"),
                  capability="editorial-production", summary="Novel v1")


def run(org, *args):
    assert main(["--org", str(org.root), *args]) == 0


def state(org, *args):
    run(org, "intent", "state", *args, "--by", "author")


def test_resolution_names_the_provider_and_the_custody_change(tmp_path):
    org = make_org(tmp_path / "org")
    twin.SignalLog(org.twin_dir).append([by_hand("2025-07-17T00:00:00Z")])
    state(org, "enrich", "--initiative", "story", "--capability", "editorial-production", "--product", "novel",
          "--outcome", "Enrich the novel", "--draws-on", "film:enriches", "--at", "2026-10-05T10:00:00Z")
    intent = bizops.intents(org, bizops.DecisionLog(org).read())["enrich"]

    proposal = bizops.resolve(org, twin.SignalLog(org.twin_dir).read(), intent)
    assert (proposal.transition, proposal.provider) == ("resolved", "kdp-studio")
    assert "done by manual" in proposal.rationale
    assert "Custody of novel moves from manual to kdp-studio" in proposal.rationale


def test_a_need_nobody_provides_is_a_gap_with_options(tmp_path):
    org = make_org(tmp_path / "org")
    state(org, "launch", "--initiative", "story", "--capability", "market-relationships",
          "--outcome", "Launch", "--at", "2026-10-05T10:00:00Z")
    run(org, "intent", "resolve", "launch", "--accept", "--by", "author", "--at", "2026-10-05T10:01:00Z")
    run(org, "intent", "choose", "launch", "wait", "--by", "author", "--at", "2026-10-05T10:02:00Z")

    intent = bizops.intents(org, bizops.DecisionLog(org).read())["launch"]
    assert intent.status == "gap" and intent.option == "wait"
    assert any("planned provider: pulse" in option for option in intent.options)


def test_progress_is_derived_from_the_providers_own_signals(tmp_path):
    org = make_org(tmp_path / "org")
    at = iter(f"2026-10-05T10:0{n}:00Z" for n in range(10))
    state(org, "enrich", "--initiative", "story", "--capability", "editorial-production", "--product", "novel",
          "--outcome", "Enrich", "--draws-on", "film:enriches", "--at", next(at))
    run(org, "intent", "resolve", "enrich", "--accept", "--by", "author", "--at", next(at))
    run(org, "intent", "handoff", "enrich", "--by", "author", "--at", next(at))

    # The book moves into KDP Studio: a change of custody, recorded by the organization.
    raw = yaml.safe_load((org.root / "organization.yaml").read_text("utf-8"))
    raw["products"][0]["custody"] = [{"domain": "manual", "ref": "novel-by-hand", "until": "2026-10-05"},
                                     {"domain": "kdp-studio", "ref": "novel", "since": "2026-10-05"}]
    (org.root / "organization.yaml").write_text(yaml.safe_dump(raw), "utf-8")
    org = organization.load(org.root)

    decisions = bizops.DecisionLog(org).read()
    assert bizops.intents(org, decisions)["enrich"].status == "handed_off"
    before = Signal(id="k:0", type="version.recorded", occurred_at="2026-10-01T00:00:00Z", domain_id="kdp-studio",
                    work_unit_ref="novel", actor=Actor("kdp-studio:a", "human"),
                    capability="editorial-production", summary="Earlier")
    after = Signal(id="k:1", type="version.recorded", occurred_at="2026-10-06T00:00:00Z", domain_id="kdp-studio",
                   work_unit_ref="novel", actor=Actor("kdp-studio:reviser", "agent"),
                   capability="editorial-production", summary="Chapter 1 enriched")
    intent = bizops.intents(org, decisions, [before, after])["enrich"]
    assert intent.status == "in_progress" and [s.id for s in intent.progress] == ["k:1"]

    planned = bizops.flows(org, [intent])
    assert {"source": "film", "target": "novel", "relation": "enriches", "state": "planned",
            "via": "enrich"} in planned

    run(org, "intent", "fulfil", "enrich", "--by", "author", "--at", "2026-10-07T00:00:00Z")
    intent = bizops.intents(org, bizops.DecisionLog(org).read(), [after])["enrich"]
    assert intent.status == "fulfilled"
    assert [f["state"] for f in bizops.flows(org, [intent]) if f["via"] == "enrich"] == ["observed"]


def test_transitions_follow_the_lifecycle(tmp_path):
    org = make_org(tmp_path / "org")
    state(org, "enrich", "--initiative", "story", "--capability", "editorial-production", "--outcome", "Enrich")
    assert main(["--org", str(org.root), "intent", "fulfil", "enrich", "--by", "author"]) == 2
    assert main(["--org", str(org.root), "intent", "state", "enrich", "--initiative", "story",
                 "--capability", "editorial-production", "--outcome", "Again", "--by", "author"]) == 2
    with pytest.raises(ContractError):
        bizops.check_transition(None, "resolved")


def test_organization_decisions_reach_the_twin_but_are_not_domain_work(tmp_path, capsys):
    org = make_org(tmp_path / "org")
    state(org, "launch", "--initiative", "story", "--capability", "market-relationships", "--outcome", "Launch")
    run(org, "ingest")
    signals = twin.SignalLog(org.twin_dir).read()
    assert [s.domain_id for s in signals] == ["bionic"]
    assert twin.unbound(org, signals) == {}
    assert twin.initiative_view(org, signals, "story").signal_count == 0


KDP_MANIFEST = {"kdp-studio": {"provides": [{"capability": "editorial-production", "accepts": ["book", "text"]}]}}


def kinded(org: organization.Organization) -> organization.Organization:
    from dataclasses import replace

    products = {k: replace(p, kind={"novel": "book", "film": "film"}[k]) for k, p in org.products.items()}
    return replace(org, products=products)


def test_a_provider_that_cannot_take_the_inputs_reveals_a_missing_transformation(tmp_path):
    org = kinded(make_org(tmp_path / "org"))
    state(org, "enrich", "--initiative", "story", "--capability", "editorial-production", "--product", "novel",
          "--outcome", "Enrich", "--draws-on", "film:enriches", "--at", "2026-10-05T10:00:00Z")
    intent = bizops.intents(org, bizops.DecisionLog(org).read())["enrich"]

    proposal = bizops.resolve(org, [], intent, KDP_MANIFEST)
    assert proposal.transition == "gap" and proposal.lands_with == "kdp-studio"
    assert proposal.missing == [{"product": "film", "kind": "film", "accepted": ["book", "text"]}]
    assert "missing transformation" in proposal.rationale
    assert any(o.startswith("adapt: create a capability that turns film into book or text") for o in proposal.options)

    # Inputs the provider accepts, or a provider that declares nothing, resolve as before.
    from dataclasses import replace
    assert bizops.resolve(org, [], replace(intent, draws_on=[{"product": "novel"}]), KDP_MANIFEST).provider == "kdp-studio"
    undeclared = bizops.resolve(org, [], intent, {})
    assert undeclared.provider == "kdp-studio" and "inputs were not checked" in undeclared.rationale


def test_a_blocker_from_the_provider_after_handoff_blocks_the_intent(tmp_path):
    org = make_org(tmp_path / "org")
    state(org, "enrich", "--initiative", "story", "--capability", "editorial-production", "--product", "novel",
          "--outcome", "Enrich", "--at", "2026-10-05T10:00:00Z")
    run(org, "intent", "resolve", "enrich", "--accept", "--by", "author", "--at", "2026-10-05T10:01:00Z")
    run(org, "intent", "handoff", "enrich", "--by", "author", "--at", "2026-10-05T10:02:00Z")
    raw = yaml.safe_load((org.root / "organization.yaml").read_text("utf-8"))
    raw["products"][0]["custody"] = [{"domain": "kdp-studio", "ref": "novel"}]
    (org.root / "organization.yaml").write_text(yaml.safe_dump(raw), "utf-8")
    org = organization.load(org.root)

    def signal(n, kind):
        return Signal(id=f"k:{n}", type=kind, occurred_at=f"2026-10-06T00:0{n}:00Z", domain_id="kdp-studio",
                      work_unit_ref="novel", actor=Actor("kdp-studio:a", "agent"),
                      capability="editorial-production", summary=kind)

    decisions = bizops.DecisionLog(org).read()
    blocked = [signal(1, "version.recorded"), signal(2, "blocker.raised")]
    assert bizops.intents(org, decisions, blocked)["enrich"].status == "blocked"
    assert bizops.intents(org, decisions, [*blocked, signal(3, "blocker.cleared")])["enrich"].status == "in_progress"
    bizops.check_transition(bizops.intents(org, decisions, blocked)["enrich"], "gap")  # may be re-resolved


def test_agents_act_only_within_the_authority_envelope(tmp_path):
    org = make_org(tmp_path / "org")
    agent = ["--by", "planner", "--kind", "agent"]
    args = ["intent", "state", "launch", "--initiative", "story", "--capability", "market-relationships",
            "--outcome", "Launch"]
    assert main(["--org", str(org.root), *args, *agent]) == 2  # default envelope: agents need a grant

    raw = yaml.safe_load((org.root / "organization.yaml").read_text("utf-8"))
    raw["authority"] = [
        {"who": "human", "may": ["*"]},
        {"who": "bionic:planner", "may": ["state", "resolve"], "capabilities": ["market-relationships"],
         "note": "the planner may state and resolve market needs"},
    ]
    (org.root / "organization.yaml").write_text(yaml.safe_dump(raw), "utf-8")
    assert main(["--org", str(org.root), *args, *agent]) == 0
    assert main(["--org", str(org.root), "intent", "choose", "launch", "wait", *agent]) == 2  # not granted
    assert main(["--org", str(org.root), "intent", "state", "enrich", "--initiative", "story",
                 "--capability", "editorial-production", "--outcome", "Enrich", *agent]) == 2  # out of scope

    [stated] = bizops.DecisionLog(organization.load(org.root)).read()
    assert stated.actor == Actor("bionic:planner", "agent")
    assert stated.data["authority"] == "the planner may state and resolve market needs"


def test_initiatives_serve_declared_objectives(tmp_path, capsys):
    org = make_org(tmp_path / "org")
    raw = yaml.safe_load((org.root / "organization.yaml").read_text("utf-8"))
    raw["objectives"] = [{"id": "reach", "statement": "Reach an audience", "priority": "high"}]
    raw["initiatives"][0]["objectives"] = ["reach"]
    (org.root / "organization.yaml").write_text(yaml.safe_dump(raw), "utf-8")
    run(organization.load(org.root), "overview")
    assert "reach: Reach an audience  (high)" in capsys.readouterr().out

    raw["initiatives"][0]["objectives"] = ["nothing"]
    (org.root / "organization.yaml").write_text(yaml.safe_dump(raw), "utf-8")
    with pytest.raises(ContractError, match="unknown objective"):
        organization.load(org.root)
