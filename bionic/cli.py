"""bionic — observe an organization (M0).

    bionic ingest              read every source, append new signals to the twin
    bionic initiative <id>     what the twin knows about one initiative
    bionic overview            initiatives, capability gaps, unclaimed work

The organization directory is ``--org`` or ``$BIONIC_ORG`` (default: current directory).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import organization, twin
from .adapters import ADAPTERS
from .contract import ContractError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bionic", description=__doc__.split("\n")[0])
    parser.add_argument("--org", type=Path, default=Path(os.environ.get("BIONIC_ORG", ".")))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest")
    show = commands.add_parser("initiative")
    show.add_argument("id")
    commands.add_parser("overview")
    args = parser.parse_args(argv)

    try:
        org = organization.load(args.org.expanduser())
        return {"ingest": ingest, "initiative": initiative, "overview": overview}[args.command](org, args)
    except ContractError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


def ingest(org: organization.Organization, args: argparse.Namespace) -> int:
    log = twin.SignalLog(org.twin_dir)
    for source in org.sources:
        adapter = ADAPTERS.get(source.domain)
        if adapter is None:
            print(f"  skip   {source.domain:14} no adapter yet  ({source.path})")
            continue
        found = list(adapter(source.path))
        added = log.append(found)
        print(f"  read   {source.domain:14} {len(found):4} signals, {added:4} new  ({source.path})")
    return 0


def initiative(org: organization.Organization, args: argparse.Namespace) -> int:
    item = org.initiatives.get(args.id)
    if item is None:
        raise ContractError(f"No initiative {args.id!r}; known: {sorted(org.initiatives)}")
    view = twin.initiative_view(org, twin.SignalLog(org.twin_dir).read(), item.id)

    print(f"{item.name}  [{item.status}]")
    if item.intent:
        print(f"  {item.intent}")
    print(f"\n{view.signal_count} signals")

    print("\nParticipation")
    for p in view.participations:
        cost = ", ".join(f"{v:.2f} {k}" for k, v in p.cost.items()) or "no cost recorded"
        print(f"  {p.domain:14} {p.capability:26} {p.first_signal_at[:10]} → {p.last_signal_at[:10]}"
              f"  {p.signal_count:4} signals  {cost}")
    if not view.participations:
        print("  none yet")

    print("\nDecisions (latest 15)")
    for s in view.decisions[-15:]:
        print(f"  {s.occurred_at[:16]}  {s.actor.kind:6} {s.actor.id:34} {s.summary[:90]}")

    print("\nOpen gates")
    for s in view.open_gates:
        print(f"  {s.occurred_at[:16]}  {s.summary}")
    if not view.open_gates:
        print("  none")

    print("\nCost: " + (", ".join(f"{v:.2f} {k}" for k, v in view.cost.items()) or "none recorded"))
    return 0


def overview(org: organization.Organization, args: argparse.Namespace) -> int:
    signals = twin.SignalLog(org.twin_dir).read()
    print(f"{org.name}: {len(signals)} signals in the twin\n")
    print("Initiatives")
    for item in org.initiatives.values():
        count = len(twin.signals_of(org, signals, item.id))
        print(f"  {item.id:24} {item.status:8} {count:4} signals")
    print("\nCapabilities")
    for cap in org.capabilities.values():
        providers = org.providers(cap.id)
        print(f"  {cap.id:26} {', '.join(providers) if providers else 'GAP — no provider'}")
    loose = twin.unbound(org, signals)
    if loose:
        print("\nWork units reporting signals but bound to no initiative")
        for (domain, ref), count in sorted(loose.items()):
            print(f"  {domain:14} {ref:24} {count:4} signals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
