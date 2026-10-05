"""bionic — observe and direct an organization (M0, M1).

    bionic ingest                  read every source, append new signals to the twin
    bionic initiative <id>         what the twin knows about one initiative
    bionic overview                initiatives, capability gaps, open intents, unclaimed work

    bionic intent state <id> ...   state a need on an initiative
    bionic intent resolve <id>     BizOps proposes a provider or a gap; --accept records it
    bionic intent choose <id> <option>       for a gap: wait, external or adapt
    bionic intent handoff|fulfil|withdraw <id>
    bionic intents                 every intent and its status

The organization directory is ``--org`` or ``$BIONIC_ORG`` (default: current directory).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import bizops, organization, twin
from .adapters import ADAPTERS
from .contract import Actor, ContractError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bionic", description=__doc__.split("\n")[0])
    parser.add_argument("--org", type=Path, default=Path(os.environ.get("BIONIC_ORG", ".")))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest")
    show = commands.add_parser("initiative")
    show.add_argument("id")
    commands.add_parser("overview")
    commands.add_parser("intents")

    intent_parser = commands.add_parser("intent")
    steps = intent_parser.add_subparsers(dest="step", required=True)
    stated = steps.add_parser("state")
    stated.add_argument("id")
    stated.add_argument("--initiative", required=True)
    stated.add_argument("--capability", required=True)
    stated.add_argument("--outcome", required=True, help="the desired outcome, in the organization's words")
    stated.add_argument("--product", default="", help="the product the outcome lands in, if it exists")
    stated.add_argument("--draws-on", action="append", default=[], metavar="PRODUCT[:RELATION]")
    stated.add_argument("--priority", default="")
    stated.add_argument("--deadline", default="")
    resolve_parser = steps.add_parser("resolve")
    resolve_parser.add_argument("id")
    resolve_parser.add_argument("--accept", action="store_true", help="record the proposal as the decision")
    choose = steps.add_parser("choose")
    choose.add_argument("id")
    choose.add_argument("option", choices=bizops.GAP_OPTIONS)
    for name in ("handoff", "fulfil", "withdraw"):
        steps.add_parser(name).add_argument("id")
    for step in (stated, resolve_parser, choose, *(steps.choices[n] for n in ("handoff", "fulfil", "withdraw"))):
        step.add_argument("--by", default=os.environ.get("USER", "unknown"), help="who decides (a person)")
        step.add_argument("--note", default="")
        step.add_argument("--at", default="", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        org = organization.load(args.org.expanduser())
        return {"ingest": ingest, "initiative": initiative, "overview": overview,
                "intents": list_intents, "intent": intent}[args.command](org, args)
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
    decisions = bizops.DecisionLog(org)
    found = decisions.read()
    print(f"  read   {'bionic':14} {len(found):4} signals, {log.append(found):4} new  ({decisions.path.name})")
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

    print("\nProducts")
    for v in view.products:
        released = ", ".join(r.data.get("version", "?") for r in v.releases) or "not released"
        print(f"  {v.product:24} {v.name:28} {released:14} now with: {v.custodian or 'nobody'}")
        for t in v.stretches:
            print(f"      {t.first_signal_at[:10]} → {t.last_signal_at[:10]}  {t.domain:14} {t.signal_count:4} signals")
    signals = twin.SignalLog(org.twin_dir).read()
    mine = [i for i in bizops.intents(org, bizops.DecisionLog(org).read(), signals).values()
            if i.initiative == item.id]
    ours = {p.id for p in org.products.values() if p.initiative == item.id}
    flows = [f for f in bizops.flows(org, mine) if f["source"] in ours or f["target"] in ours]
    if flows:
        print("\nFlows")
        for f in flows:
            via = f"   (intent {f['via']})" if f["via"] else ""
            print(f"  {f['source']} —{f['relation']}→ {f['target']}  [{f['state']}]{via}")

    print("\nIntents")
    for i in mine:
        _print_intent(i)
    if not mine:
        print("  none")

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

    print("\nCost: " + (", ".join(f"{v:.2f} {k}" for k, v in view.cost.items()) or "none priced"))
    if view.unpriced["count"]:
        print(f"  plus {view.unpriced['count']} billed jobs the domain did not price"
              f" ({view.unpriced['seconds'] / 3600:.2f} h)")
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
    open_intents = [i for i in bizops.intents(org, bizops.DecisionLog(org).read(), signals).values()
                    if i.status not in ("fulfilled", "withdrawn")]
    print("\nOpen intents")
    for i in open_intents:
        print(f"  {i.id:28} {i.initiative:20} {i.status:12} {i.provider or ('GAP' if i.status == 'gap' else '')}")
    if not open_intents:
        print("  none")
    external = [d.id for d in org.domains.values() if d.kind == "external"]
    if external:
        print(f"\nWork observed outside autonomous domains: {', '.join(external)}")
    loose = twin.unbound(org, signals)
    if loose:
        print("\nDomain work reporting signals but claimed by no product")
        for (domain, ref), count in sorted(loose.items()):
            print(f"  {domain:14} {ref:24} {count:4} signals")
    return 0


def list_intents(org: organization.Organization, args: argparse.Namespace) -> int:
    signals = twin.SignalLog(org.twin_dir).read()
    for i in bizops.intents(org, bizops.DecisionLog(org).read(), signals).values():
        print(f"{i.initiative} ·", end="")
        _print_intent(i)
    return 0


def _print_intent(i: bizops.Intent) -> None:
    target = f" → {i.product}" if i.product else ""
    print(f"  {i.id}  [{i.status}]  {i.capability}{target}")
    print(f"      {i.desired_outcome}")
    if i.draws_on:
        print("      draws on: " + ", ".join(f"{d['product']} ({d.get('relation', 'feeds')})" for d in i.draws_on))
    if i.status == "gap":
        print(f"      {i.rationale}")
        for option in i.options:
            mark = "→" if option.startswith(i.option + ":") and i.option else " "
            print(f"      {mark} {option}")
    elif i.provider:
        print(f"      provider: {i.provider} — {i.rationale}")
    if i.progress:
        print(f"      progress: {len(i.progress)} signals from {i.provider}, latest {i.progress[-1].occurred_at[:10]}:"
              f" {i.progress[-1].summary[:70]}")


def intent(org: organization.Organization, args: argparse.Namespace) -> int:
    decisions = bizops.DecisionLog(org)
    signals = twin.SignalLog(org.twin_dir).read()
    known = bizops.intents(org, decisions.read(), signals)
    current = known.get(args.id)
    actor = Actor(id=f"bionic:{args.by}", kind="human")
    common = {"actor": actor, "at": args.at}
    note = {"note": args.note} if args.note else {}

    if args.step == "state":
        bizops.check_transition(current, "stated")
        if args.initiative not in org.initiatives:
            raise ContractError(f"Unknown initiative {args.initiative!r}")
        if args.capability not in org.capabilities:
            raise ContractError(f"Unknown capability {args.capability!r}")
        draws_on = []
        for item in args.draws_on:
            product, _, relation = item.partition(":")
            if product not in org.products:
                raise ContractError(f"Unknown product {product!r}")
            draws_on.append({"product": product, "relation": relation or "feeds"})
        if args.product and args.product not in org.products:
            raise ContractError(f"Unknown product {args.product!r}")
        decisions.record(args.id, "stated", capability=args.capability, summary=f"Intent stated: {args.outcome}",
                         initiative=args.initiative, desired_outcome=args.outcome, product=args.product,
                         draws_on=draws_on, priority=args.priority, deadline=args.deadline, **common, **note)
        print(f"stated {args.id}")
        return 0

    if current is None:
        raise ContractError(f"No intent {args.id!r}")

    if args.step == "resolve":
        proposal = bizops.resolve(org, signals, current)
        print(f"BizOps proposes: {proposal.transition}" + (f" → {proposal.provider}" if proposal.provider else ""))
        print(f"  {proposal.rationale}")
        for option in proposal.options:
            print(f"  · {option}")
        if not args.accept:
            print("\n(not recorded; run again with --accept to decide)")
            return 0
        bizops.check_transition(current, proposal.transition)
        decisions.record(args.id, proposal.transition, capability=current.capability,
                         summary=f"Intent {proposal.transition}" + (f" → {proposal.provider}" if proposal.provider
                                                                   else ": no provider"),
                         initiative=current.initiative, provider=proposal.provider, rationale=proposal.rationale,
                         options=proposal.options, proposed_by="bizops-rule", **common, **note)
        print(f"recorded: {proposal.transition}")
        return 0

    transition = {"choose": "option_chosen", "handoff": "handed_off", "fulfil": "fulfilled",
                  "withdraw": "withdrawn"}[args.step]
    bizops.check_transition(current, transition)
    extra = {"option": args.option} if args.step == "choose" else {}
    if args.step == "handoff":
        extra = {"provider": current.provider, "desired_outcome": current.desired_outcome,
                 "product": current.product}
    decisions.record(args.id, transition, capability=current.capability,
                     summary=f"Intent {transition.replace('_', ' ')}" + (f": {args.option}" if extra.get("option") else ""),
                     initiative=current.initiative, **extra, **common, **note)
    print(f"recorded: {transition}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
