"""Manual signals: work observed outside any autonomous domain.

A YAML file of signals, written by a person: what happened, when, and what it
evidences. It is how the twin sees work done by hand, by a vendor, or before a
domain existed. Every entry carries its own id, so editing the file and
re-ingesting never duplicates what the twin already has.

    work_unit_ref: singular-book
    capability: editorial-production
    signals:
      - id: book-v1
        type: version.recorded
        occurred_at: 2025-07-17T20:04:58Z
        actor: {id: jaime, kind: human}
        summary: Book, version 1 (ODT, PDF)
        evidence: ~/confyui/singular/livro/singular/Singular_versao1.pdf
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import yaml

from ..contract import Actor, ContractError, Signal

DOMAIN = "manual"


def signals(path: Path) -> Iterator[Signal]:
    if not path.is_file():
        raise ContractError(f"No manual signal file: {path}")
    raw = yaml.safe_load(path.read_text("utf-8")) or {}
    domain = str(raw.get("domain", DOMAIN))
    for entry in raw.get("signals") or []:
        actor = entry.get("actor") or {}
        yield Signal(
            id=f"{domain}:{entry.get('work_unit_ref', raw.get('work_unit_ref'))}:{entry['id']}",
            type=entry["type"],
            occurred_at=str(entry["occurred_at"]).replace(" ", "T"),
            domain_id=domain,
            work_unit_ref=entry.get("work_unit_ref", raw.get("work_unit_ref", "")),
            actor=Actor(id=f"{domain}:{actor.get('id', 'unknown')}", kind=actor.get("kind", "human")),
            capability=entry.get("capability", raw.get("capability", "")),
            summary=entry.get("summary", ""),
            data={k: v for k, v in entry.items()
                  if k not in ("id", "type", "occurred_at", "actor", "summary", "capability", "work_unit_ref")},
            source={"kind": "manual", "ref": f"{path.name}#{entry['id']}"},
        )
