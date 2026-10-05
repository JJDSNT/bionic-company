"""Cine Toaster adapter: read a production directory, emit organizational signals.

Read-only. Sources:

- each scene's ``history.jsonl``: every committed decision, append-only and
  never truncated (Cine Toaster ADR 0021);
- each scene's ``state.json`` ``gates``: when a gate was opened, which the
  history does not record;
- the provider job records a production keeps beside its takes
  (``<take>.job.json``): what each generation was billed in seconds. They
  are the production's own cost records, whoever ran the job. The price per
  hour is the production's declared ``generation_rates``; without one the
  signal carries the seconds and no amount, rather than guessing a price.

Cine Toaster's machine-wide spend ledger and job database are not read: they
are runtime state, and reconciling them with the provider's billing is Cine
Toaster's own FinOps concern (``docs/finops.md``: reconcile, do not duplicate).
The ``events.jsonl`` cache is ignored: it is disposable by design (ADR 0006).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ..contract import CONTRACT_VERSION, Actor, ContractError, Cost, Signal

DOMAIN = "cine-toaster"
CAPABILITY = "audiovisual-production"

MANIFEST = {
    "domain": {"id": DOMAIN, "name": "Cine Toaster"},
    "contract_version": CONTRACT_VERSION,
    "provides": [{"capability": CAPABILITY, "outcomes": ["scene", "sequence", "film", "trailer"]}],
    "work_unit": {"kind": "production", "ref_field": "project.yaml id"},
    "signals": ["work.started", "decision.recorded", "gate.opened", "gate.decided", "version.recorded",
                "cost.incurred"],
}

# Cine Toaster decision kind -> signal type
KINDS = {
    "assembly.imported": "version.recorded",
    "assembly.recorded": "version.recorded",
    "assembly.reviewed": "decision.recorded",
    "assembly.restored": "decision.recorded",
    "gate.decided": "gate.decided",
    "workflow.started": "work.started",
}


def production_id(root: Path) -> str:
    path = root / "project.yaml"
    if not path.is_file():
        raise ContractError(f"Not a Cine Toaster production (no project.yaml): {root}")
    identity = (yaml.safe_load(path.read_text("utf-8")) or {}).get("id")
    if not identity:
        raise ContractError(f"project.yaml has no id: {path}")
    return str(identity)


def signals(root: Path) -> Iterator[Signal]:
    production = production_id(root)
    project = yaml.safe_load((root / "project.yaml").read_text("utf-8")) or {}
    scenes = root / str((project.get("paths") or {}).get("scenes", "scenes"))
    for scene in sorted(p for p in scenes.iterdir() if p.is_dir()) if scenes.is_dir() else []:
        yield from _from_history(scene, production)
        yield from _from_gates(scene, production)
    yield from _from_job_records(root, production, project.get("generation_rates") or {})


def _scene_id(scene: Path) -> str:
    state = scene / "state.json"
    if state.is_file():
        identity = json.loads(state.read_text("utf-8")).get("scene_id")
        if identity:
            return str(identity)
    return scene.name


def _from_history(scene: Path, production: str) -> Iterator[Signal]:
    path = scene / "history.jsonl"
    if not path.is_file():
        return
    scene_id = _scene_id(scene)
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            entry = json.loads(line)
            kind = str(entry.get("kind", ""))
            when, assumed = _when(str(entry.get("decided_at", "")))
            data = {k: v for k, v in entry.items() if k not in ("actor", "decided_at", "kind")}
            data.update(domain_event=kind, scene=scene_id)
            if assumed:
                data["timestamp_assumed_local"] = True
            yield Signal(
                id=f"{DOMAIN}:{production}:{scene_id}:{entry.get('command_id') or _digest(entry)}:{kind}",
                type=KINDS.get(kind, "decision.recorded"),
                occurred_at=when,
                domain_id=DOMAIN,
                work_unit_ref=production,
                actor=_actor(entry.get("actor")),
                capability=CAPABILITY,
                summary=_summary(scene_id, kind, entry),
                data=data,
                source={"kind": "history.jsonl", "ref": f"{path.relative_to(scene.parent.parent)}#L{line_number}"},
            )


def _from_gates(scene: Path, production: str) -> Iterator[Signal]:
    path = scene / "state.json"
    if not path.is_file():
        return
    scene_id = _scene_id(scene)
    for gate_id, gate in (json.loads(path.read_text("utf-8")).get("gates") or {}).items():
        if not gate.get("requested_at"):
            continue
        when, assumed = _when(str(gate["requested_at"]))
        data = {"gate": gate_id, "kind": gate.get("kind", ""), "subject": gate.get("subject", ""), "scene": scene_id}
        if assumed:
            data["timestamp_assumed_local"] = True
        yield Signal(
            id=f"{DOMAIN}:{production}:{scene_id}:gate-opened:{gate_id}",
            type="gate.opened",
            occurred_at=when,
            domain_id=DOMAIN,
            work_unit_ref=production,
            actor=_actor(gate.get("requested_by")),
            capability=CAPABILITY,
            summary=f"{scene_id}: gate {gate.get('kind', gate_id)} opened for {gate.get('subject') or 'the scene'}",
            data=data,
            source={"kind": "state.json", "ref": f"{path.relative_to(scene.parent.parent)}#gates.{gate_id}"},
        )


def _from_job_records(root: Path, production: str, rates: dict[str, Any]) -> Iterator[Signal]:
    seen: set[str] = set()
    # Archived takes included: they were paid for. A copy of a record (same job id) counts once.
    for path in sorted(root.rglob("*.job.json")):
        try:
            record = json.loads(path.read_text("utf-8"))
        except (OSError, ValueError):
            continue
        job, endpoint = record.get("id"), record.get("endpoint")
        if not job or not endpoint or job in seen:
            continue
        seen.add(job)
        seconds = (float(record.get("delayTime") or 0) + float(record.get("executionTime") or 0)) / 1000
        what = path.relative_to(root).as_posix().removesuffix(".job.json")
        rate = rates.get(endpoint)
        cost = Cost(amount=round(seconds * float(rate) / 3600, 4), currency="USD", kind="compute") \
            if rate is not None else None
        finished = record.get("finished_at")
        when = finished or datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(timespec="seconds")
        priced = f"US$ {cost.amount:.4f}" if cost else "no declared rate"
        yield Signal(
            id=f"{DOMAIN}:{production}:job:{job}",
            type="cost.incurred",
            occurred_at=_when(when)[0],
            domain_id=DOMAIN,
            work_unit_ref=production,
            actor=Actor(id=f"{DOMAIN}:provider", kind="system"),
            capability=CAPABILITY,
            summary=f"{what}: {seconds:.1f} s billed ({priced})",
            data={"remote": job, "endpoint": endpoint, "seconds": round(seconds, 3), "status": record.get("status", ""),
                  "rate_usd_per_hour": rate, "at_source": "recorded" if finished else "file_time"},
            cost=cost,
            source={"kind": "job.json", "ref": f"{what}.job.json"},
        )


def _summary(scene: str, kind: str, entry: dict[str, Any]) -> str:
    subject = entry.get("assembly_id") or entry.get("take_id") or entry.get("gate") or entry.get("workflow") or ""
    verdict = entry.get("verdict") or entry.get("outcome") or ""
    text = f"{scene}: {kind.replace('.', ' ')}" + (f" {subject}" if subject else "") + (f" ({verdict})" if verdict else "")
    rationale = str(entry.get("rationale") or "").strip()
    return f"{text} — {rationale}" if rationale else text


def _actor(raw: Any) -> Actor:
    raw = raw or {}
    return Actor(id=f"{DOMAIN}:{raw.get('id') or 'unknown'}", kind=raw.get("kind") or "system")


def _when(text: str) -> tuple[str, bool]:
    """A timestamp with a zone. Records imported from before Cine Toaster have none;
    they were written on this machine, so its local zone is assumed, and the signal says so."""

    moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        return moment.astimezone().isoformat(), True
    return moment.isoformat(), False


def _digest(entry: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
