import json
import subprocess
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
        "bindings": [{"initiative": "the-book", "domain": "kdp-studio", "work_unit_ref": "test-book"}],
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
