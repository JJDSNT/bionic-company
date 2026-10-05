import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from bionic import organization, twin
from bionic.adapters import kdp_studio
from bionic.cli import main
from bionic.contract import Actor, ContractError, Signal

HUMAN = {"id": "jaime", "kind": "human"}
AGENT = {"id": "reviser", "kind": "agent"}


def make_book(root: Path, history: list[dict], *, git: bool = True) -> Path:
    root.mkdir(parents=True)
    (root / "book.yaml").write_text("schema: 1\nid: test-book\n", "utf-8")
    (root / "state.json").write_text(json.dumps({"revision": len(history), "gates": {}, "history": history}), "utf-8")
    if git:
        env = ["-c", "user.name=Author", "-c", "user.email=author@example.org"]
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", *env, "add", "book.yaml"], cwd=root, check=True)
        subprocess.run(["git", *env, "commit", "-q", "-m", "Start the book"], cwd=root, check=True)
        subprocess.run(["git", *env, "add", "state.json"], cwd=root, check=True)
        subprocess.run(["git", *env, "commit", "-q", "-m", "Open gate\n\nActor: jaime (human)"], cwd=root, check=True)
    return root


HISTORY = [
    {"at": "2026-10-01T10:00:00Z", "event": "gate_opened", "gate": "chapter-1", "actor": HUMAN},
    {"at": "2026-10-01T11:00:00Z", "event": "version_proposed", "version": "v1", "section": "01", "actor": AGENT},
    {"at": "2026-10-01T12:00:00Z", "event": "version_adopted", "version": "v1", "section": "01",
     "actor": HUMAN, "rationale": "reads better"},
    {"at": "2026-10-02T09:00:00Z", "event": "gate_opened", "gate": "chapter-2", "actor": HUMAN},
    {"at": "2026-10-02T10:00:00Z", "event": "gate_decided", "gate": "chapter-1", "decision": "approved",
     "actor": HUMAN, "rationale": ""},
]


def make_org(root: Path, book: Path) -> organization.Organization:
    root.mkdir(parents=True, exist_ok=True)
    (root / "organization.yaml").write_text(yaml.safe_dump({
        "organization": {"id": "test", "name": "Test org"},
        "domains": [{"id": "kdp-studio", "name": "KDP Studio"}, {"id": "pulse", "name": "Pulse", "status": "planned"}],
        "capabilities": [{"id": "editorial-production", "name": "Editorial"},
                         {"id": "market-relationships", "name": "Market"}],
        "provisions": [{"capability": "editorial-production", "domain": "kdp-studio"}],
        "initiatives": [{"id": "the-book", "name": "The Book"}],
        "products": [{"id": "book", "name": "The Book", "initiative": "the-book",
                      "custody": [{"domain": "kdp-studio", "ref": "test-book"}]}],
        "sources": [{"domain": "kdp-studio", "path": str(book)}],
    }), "utf-8")
    return organization.load(root)


def test_kdp_history_becomes_signals(tmp_path):
    book = make_book(tmp_path / "book", HISTORY)
    signals = list(kdp_studio.signals(book))

    types = [s.type for s in signals]
    assert types == ["gate.opened", "version.recorded", "decision.recorded", "gate.opened", "gate.decided",
                     "decision.recorded"]
    adopted = signals[2]
    assert adopted.actor == Actor("kdp-studio:jaime", "human")
    assert adopted.summary == "Version v1 of 01 adopted — reads better"
    assert adopted.source == {"kind": "state.json", "ref": "history[2]"}
    assert all(s.work_unit_ref == "test-book" and s.capability == "editorial-production" for s in signals)


def test_commits_made_by_kdp_studio_are_not_counted_twice(tmp_path):
    book = make_book(tmp_path / "book", HISTORY)
    from_git = [s for s in kdp_studio.signals(book) if s.source["kind"] == "git"]
    assert [s.summary for s in from_git] == ["Start the book"]
    assert from_git[0].actor.id == "kdp-studio:author@example.org"


def test_signal_ids_are_stable_across_reads(tmp_path):
    book = make_book(tmp_path / "book", HISTORY)
    assert [s.id for s in kdp_studio.signals(book)] == [s.id for s in kdp_studio.signals(book)]


def test_log_is_idempotent_and_keeps_history(tmp_path):
    book = make_book(tmp_path / "book", HISTORY)
    log = twin.SignalLog(tmp_path / "twin")
    assert log.append(kdp_studio.signals(book)) == 6
    assert log.append(kdp_studio.signals(book)) == 0

    # The domain loses its records; the twin still has them.
    (book / "state.json").unlink()
    assert log.append(kdp_studio.signals(book)) == 0
    assert len(log.read()) == 6


def test_initiative_view_reconstructs_the_path(tmp_path):
    book = make_book(tmp_path / "book", HISTORY)
    org = make_org(tmp_path / "org", book)
    log = twin.SignalLog(org.twin_dir)
    log.append(kdp_studio.signals(book))

    view = twin.initiative_view(org, log.read(), "the-book")
    assert view.signal_count == 6
    [p] = view.participations
    assert (p.domain, p.capability, p.signal_count) == ("kdp-studio", "editorial-production", 6)
    assert [g.data["gate"] for g in view.open_gates] == ["chapter-2"]
    assert view.cost == {}


def test_capability_without_provider_is_a_gap(tmp_path):
    org = make_org(tmp_path / "org", tmp_path / "book")
    assert [c.id for c in org.gaps()] == ["market-relationships"]


def test_unbound_work_units_are_visible(tmp_path):
    book = make_book(tmp_path / "book", HISTORY, git=False)
    org = make_org(tmp_path / "org", book)
    stray = Signal(id="x:1", type="decision.recorded", occurred_at="2026-10-01T00:00:00Z", domain_id="kdp-studio",
                   work_unit_ref="other-book", actor=Actor("kdp-studio:x", "human"),
                   capability="editorial-production", summary="s")
    assert twin.unbound(org, [stray]) == {("kdp-studio", "other-book"): 1}


def test_contract_rejects_unknown_types_and_naive_timestamps():
    base = dict(id="a", occurred_at="2026-10-01T00:00:00Z", domain_id="d", work_unit_ref="w",
                actor=Actor("d:x", "human"), capability="c", summary="s")
    with pytest.raises(ContractError):
        Signal(type="thing.happened", **base)
    with pytest.raises(ContractError):
        Signal(type="work.started", **{**base, "occurred_at": "2026-10-01T00:00:00"})
    assert Signal(type="work.started", **{**base, "occurred_at": "2026-10-01T00:00:00-03:00"}).occurred_at \
        == "2026-10-01T03:00:00Z"


def test_cli_end_to_end(tmp_path, capsys):
    book = make_book(tmp_path / "book", HISTORY)
    org = make_org(tmp_path / "org", book)
    assert main(["--org", str(org.root), "ingest"]) == 0
    assert main(["--org", str(org.root), "initiative", "the-book"]) == 0
    assert main(["--org", str(org.root), "overview"]) == 0
    out = capsys.readouterr().out
    assert "6 signals, " in out and "GAP — no provider" in out and "chapter-2" in out


def make_production(root: Path) -> Path:
    scene = root / "scenes" / "010-opening"
    scene.mkdir(parents=True)
    (root / "project.yaml").write_text("schema_version: 1\nid: film\npaths: {scenes: scenes}\n", "utf-8")
    (scene / "history.jsonl").write_text("\n".join(json.dumps(e) for e in [
        {"kind": "assembly.imported", "assembly_id": "v1", "command_id": "import-v1", "decided_at": "2026-09-18T08:24:00",
         "actor": {"id": "migration", "kind": "system"}, "rationale": "Imported."},
        {"kind": "gate.decided", "gate": "gate_1", "outcome": "approved", "command_id": "c2",
         "decided_at": "2026-09-20T10:00:00+00:00", "actor": HUMAN, "rationale": ""},
    ]) + "\n", "utf-8")
    (scene / "state.json").write_text(json.dumps({"scene_id": "010", "gates": {
        "gate_1": {"kind": "approve_picture", "subject": "c01", "state": "approved",
                   "requested_at": "2026-09-19T10:00:00+00:00", "requested_by": {"id": "workflow", "kind": "system"}},
        "gate_2": {"kind": "approve_picture", "subject": "c02", "state": "waiting",
                   "requested_at": "2026-09-21T10:00:00+00:00", "requested_by": {"id": "workflow", "kind": "system"}},
    }}), "utf-8")

    work = scene / "work"
    work.mkdir()
    record = {"id": "job-1", "endpoint": "ep", "status": "COMPLETED", "delayTime": 1000, "executionTime": 359000,
              "finished_at": "2026-09-22T10:00:00+00:00"}
    (work / "c01.mp4.job.json").write_text(json.dumps(record), "utf-8")
    (root / "archive").mkdir()
    (root / "archive" / "c01-copy.mp4.job.json").write_text(json.dumps(record), "utf-8")  # same job: once
    (work / "c02.mp4.job.json").write_text(json.dumps({**record, "id": "job-2", "endpoint": "unpriced"}), "utf-8")
    with (root / "project.yaml").open("a", encoding="utf-8") as handle:
        handle.write("generation_rates: {ep: 2.0}\n")
    return root


def test_cine_production_becomes_signals(tmp_path):
    from bionic.adapters import cine_toaster

    production = make_production(tmp_path / "film")
    signals = {s.type: s for s in cine_toaster.signals(production)}
    found = [s.type for s in cine_toaster.signals(production)]

    assert sorted(found) == sorted(["version.recorded", "gate.decided", "gate.opened", "gate.opened",
                                    "cost.incurred", "cost.incurred"])
    assert signals["version.recorded"].data["timestamp_assumed_local"] is True
    assert signals["version.recorded"].data["scene"] == "010"
    costs = {s.data["remote"]: s for s in cine_toaster.signals(production) if s.type == "cost.incurred"}
    assert costs["job-1"].cost.amount == 0.2  # 360 s at US$ 2.00/h, declared by the production
    assert costs["job-2"].cost is None and costs["job-2"].data["seconds"] == 360.0
    assert all(s.work_unit_ref == "film" for s in signals.values())


def test_cine_open_gates_and_cost_reach_the_initiative(tmp_path):
    from bionic.adapters import cine_toaster

    production = make_production(tmp_path / "film")
    org = replace(make_org(tmp_path / "org", tmp_path / "book"),
                  domains={"cine-toaster": organization.Domain("cine-toaster", "Cine Toaster")},
                  products={"film": organization.Product("film", "Film", "the-book",
                                                         custody=({"domain": "cine-toaster", "ref": "film"},))})
    signals = list(cine_toaster.signals(production))

    view = twin.initiative_view(org, signals, "the-book")
    assert [g.data["gate"] for g in view.open_gates] == ["gate_2"]
    assert view.cost == {"USD": 0.2}
    assert view.unpriced == {"count": 1, "seconds": 360.0}



def test_custody_moves_and_the_product_stays_the_same(tmp_path):
    from bionic.adapters import manual

    org_root = tmp_path / "org"
    (org_root / "manual").mkdir(parents=True)
    (org_root / "manual" / "work.yaml").write_text(yaml.safe_dump({
        "work_unit_ref": "the-novel", "capability": "editorial-production",
        "signals": [{"id": "v1", "type": "version.recorded", "occurred_at": "2025-07-17T20:00:00Z",
                     "actor": {"id": "author", "kind": "human"}, "summary": "Novel v1", "evidence": "novel.pdf"}],
    }), "utf-8")
    (org_root / "organization.yaml").write_text(yaml.safe_dump({
        "organization": {"id": "test", "name": "Test"},
        "domains": [{"id": "manual", "name": "By hand", "kind": "external"},
                    {"id": "kdp-studio", "name": "KDP Studio"}],
        "initiatives": [{"id": "story", "name": "Story"}],
        "products": [
            {"id": "novel", "name": "Novel", "initiative": "story", "custody": [
                {"domain": "manual", "ref": "the-novel", "until": "2026-01-01"},
                {"domain": "kdp-studio", "ref": "novel-in-kdp", "since": "2026-01-01"}]},
            {"id": "film", "name": "Film", "initiative": "story"},
        ],
        "flows": [{"source": "novel", "target": "film", "relation": "adapted into"}],
        "sources": [{"domain": "manual", "path": "manual/work.yaml"}],
    }), "utf-8")
    org = organization.load(org_root)
    later = Signal(id="k:1", type="version.recorded", occurred_at="2026-02-01T00:00:00Z", domain_id="kdp-studio",
                   work_unit_ref="novel-in-kdp", actor=Actor("kdp-studio:author", "human"),
                   capability="editorial-production", summary="Novel v2")
    signals = [*manual.signals(org.sources[0].path), later]

    view = twin.initiative_view(org, signals, "story")
    novel, film = view.products
    assert novel.product == "novel" and novel.custodian == "kdp-studio"
    assert [t.domain for t in novel.stretches] == ["manual", "kdp-studio"]
    assert film.stretches == [] and novel.releases == []
    assert signals[0].data["evidence"] == "novel.pdf"


def test_products_must_be_consistent(tmp_path):
    book = make_book(tmp_path / "book", HISTORY, git=False)
    org = make_org(tmp_path / "org", book)
    path = org.root / "organization.yaml"
    good = yaml.safe_load(path.read_text("utf-8"))

    for change, message in [
        ({"flows": [{"source": "book", "target": "nowhere", "relation": "feeds"}]}, "unknown product"),
        ({"products": good["products"] + [{"id": "copy", "name": "C", "initiative": "the-book",
                                            "custody": [{"domain": "kdp-studio", "ref": "test-book"}]}]},
         "is claimed by"),
        ({"products": [{**good["products"][0], "custody": [{"domain": "kdp-studio", "ref": "a"},
                                                           {"domain": "kdp-studio", "ref": "b"}]}]},
         "more than one current custodian"),
    ]:
        path.write_text(yaml.safe_dump({**good, **change}), "utf-8")
        with pytest.raises(ContractError, match=message):
            organization.load(org.root)
