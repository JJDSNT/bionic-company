"""KDP Studio adapter: read a book directory, emit organizational signals.

Read-only. Sources, in order of authority:

- ``state.json`` ``history``: every gate, version, plan and edit decision KDP
  Studio made, with its actor. Append-only in KDP Studio, never truncated.
- git commits *without* an ``Actor:`` trailer: work the author did outside KDP
  Studio. Commits *with* the trailer are KDP Studio's own and are already
  covered by ``state.json``, so they are skipped to avoid counting twice.

KDP Studio records no cost, so its signals carry none.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from ..contract import CONTRACT_VERSION, Actor, ContractError, Signal

DOMAIN = "kdp-studio"
CAPABILITY = "editorial-production"

MANIFEST = {
    "domain": {"id": DOMAIN, "name": "KDP Studio"},
    "contract_version": CONTRACT_VERSION,
    "provides": [{"capability": CAPABILITY, "outcomes": ["book", "edition", "translation"]}],
    "work_unit": {"kind": "book", "ref_field": "book.yaml id"},
    "signals": ["decision.recorded", "gate.opened", "gate.decided", "version.recorded"],
}

# KDP Studio history event -> (signal type, summary template)
EVENTS: dict[str, tuple[str, str]] = {
    "gate_opened": ("gate.opened", "Gate {gate} opened"),
    "gate_decided": ("gate.decided", "Gate {gate}: {decision}"),
    "version_proposed": ("version.recorded", "Version {version} of {section} proposed"),
    "version_adopted": ("decision.recorded", "Version {version} of {section} adopted"),
    "version_rejected": ("decision.recorded", "Version {version} of {section} rejected"),
    "section_edited": ("decision.recorded", "Section {section} ({language}) edited"),
    "plan_proposed": ("version.recorded", "Plan {plan} proposed"),
    "plan_adopted": ("decision.recorded", "Plan {plan} adopted"),
}

_FIELD = re.compile(r"\{(\w+)\}")


def book_id(root: Path) -> str:
    path = root / "book.yaml"
    if not path.is_file():
        raise ContractError(f"Not a KDP Studio book (no book.yaml): {root}")
    identity = (yaml.safe_load(path.read_text("utf-8")) or {}).get("id")
    if not identity:
        raise ContractError(f"book.yaml has no id: {path}")
    return str(identity)


def signals(root: Path) -> Iterator[Signal]:
    book = book_id(root)
    yield from _from_state(root, book)
    yield from _from_git(root, book)


def _from_state(root: Path, book: str) -> Iterator[Signal]:
    path = root / "state.json"
    if not path.is_file():
        return
    history = json.loads(path.read_text("utf-8")).get("history") or []
    for index, entry in enumerate(history):
        event = str(entry.get("event", ""))
        kind, template = EVENTS.get(event, ("decision.recorded", event.replace("_", " ") or "event"))
        actor = entry.get("actor") or {}
        data = {k: v for k, v in entry.items() if k not in ("at", "actor")}
        data["domain_event"] = data.pop("event", event)
        reason = entry.get("rationale") or entry.get("reason") or ""
        summary = _FIELD.sub(lambda m: str(entry.get(m.group(1), "?")), template)
        yield Signal(
            id=f"{DOMAIN}:{book}:h:{_digest(entry)}",
            type=kind,
            occurred_at=entry["at"],
            domain_id=DOMAIN,
            work_unit_ref=book,
            actor=Actor(id=f"{DOMAIN}:{actor.get('id', 'unknown')}", kind=actor.get("kind", "system")),
            capability=CAPABILITY,
            summary=f"{summary} — {reason}" if reason else summary,
            data=data,
            source={"kind": "state.json", "ref": f"history[{index}]"},
        )


def _from_git(root: Path, book: str) -> Iterator[Signal]:
    if not (root / ".git").exists():
        return
    separator = "\x1f"
    run = subprocess.run(
        ["git", "log", "--reverse", f"--format=%H{separator}%aI{separator}%an{separator}%ae{separator}%s{separator}%b\x1e"],
        cwd=root, capture_output=True, text=True,
    )
    if run.returncode != 0:
        return
    for record in run.stdout.split("\x1e"):
        if not record.strip():
            continue
        sha, when, name, email, subject, body = record.strip("\n").split(separator, 5)
        if re.search(r"^Actor: ", body, re.MULTILINE):
            continue
        yield Signal(
            id=f"{DOMAIN}:{book}:git:{sha}",
            type="decision.recorded",
            occurred_at=when,
            domain_id=DOMAIN,
            work_unit_ref=book,
            actor=Actor(id=f"{DOMAIN}:{email or name}", kind="human"),
            capability=CAPABILITY,
            summary=subject,
            data={"commit": sha, "author": name, "body": body.strip()},
            source={"kind": "git", "ref": sha},
        )


def _digest(entry: dict[str, Any]) -> str:
    canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:16]
