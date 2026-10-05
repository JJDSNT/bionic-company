# M0 — Minimal Organizational Model and Contract

> Status: proposal. Derived from [organizational-model.md](organizational-model.md) and from what KDP Studio and Cine Toaster already record today.

## Purpose

M0 is **Observe**: represent enough organizational state to see real initiatives, domains, capabilities, agents and activity.

The hypothesis M0 tests is:

> **From domain signals alone, the Organizational Twin can reconstruct the real path an initiative took — which capabilities it used, which domains participated, when, at what cost, and with what result — without knowing how any domain works internally.**

M0 is validated against two real initiatives, **Singular** and **A Era dos Agentes**.

M0 does not direct, adapt or simulate. It only observes. But the contract it defines must not block M1–M3.

## Three levels

The ecosystem stays coherent through a shared contract, not a shared technology stack.

| Level | Owned by | Binding? | Contents |
|---|---|---|---|
| **1. Organizational contract** | Bionic Company | Required for every participating domain | Capability manifest, signal envelope, intent envelope, actor |
| **2. Recommended patterns** | The ecosystem | Optional | Durable records as truth, gates as records, explicit actor, append-only history |
| **3. Domain internals** | Each domain | Free | Language, storage, agents, workflows, models, tools, UI |

The contract is described in JSON Schema and is transport-neutral: a domain may deliver it over HTTP, events, MCP, files or a manual entry. It assumes no particular language, framework or storage.

## Entities

### Organization

The organization the twin represents.

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `name` | |

Every other entity belongs to exactly one organization. M0 has one organization, but the model never assumes there is only one (see [Future compatibility](#future-compatibility)).

### Domain

An autonomous operating domain.

| Field | Notes |
|---|---|
| `id` | e.g. `kdp-studio`, `cine-toaster`, `pulse` |
| `name` | |
| `status` | `active` · `planned` · `retired` |
| `kind` | `autonomous` (behind the contract) · `external` (work done by hand, by a vendor, or before a domain existed; observed through manual signals, never directed) |

### Capability

A **business** capability, not a technical one.

| Field | Notes |
|---|---|
| `id` | e.g. `editorial-production`, `audiovisual-production`, `market-relationships` |
| `name` | |
| `description` | What the organization can achieve with it |

A capability exists independently of who provides it.

### Provision

A domain's declaration that it provides a capability.

| Field | Notes |
|---|---|
| `capability_id` | |
| `domain_id` | |
| `since` / `until` | Providers can change over time |

A capability with no current provision is a **capability gap**. M0 records gaps; it does not resolve them.

### Initiative

Something the organization is pursuing. It has no owning domain.

| Field | Notes |
|---|---|
| `id` | e.g. `singular`, `a-era-dos-agentes` |
| `name` | |
| `intent` | What it is for, in the organization's words |
| `status` | `active` · `paused` · `done` · `abandoned` |

### Product

What the organization makes and releases: a book, a film. A campaign or a service could be one too.

| Field | Notes |
|---|---|
| `id` | The organization's identifier, e.g. `singular-book`, `singular-film` |
| `name` | |
| `initiative` | The initiative it serves |
| `kind` | e.g. `book`, `film` |
| `after_release` | `frozen`: a released version never changes (fiction). `editions`: a later edition may revise it (a technical book) |
| `custody` | Which domain works on it, under the domain's own reference, and when |

**A product's identity belongs to the organization, not to a domain.** When the Singular book moves from work done by hand into KDP Studio, custody changes and the product stays the same, with one continuous history.

**A product evolves in versions, and a release freezes a version.** The release is the moment a domain's work becomes an organizational asset. In the contract it is `outcome.delivered`, carrying the version. Whether anything may change after a release is a policy of the product (`after_release`), not a rule of the domain.

**Domains do not need to know initiatives or products exist.** KDP Studio keeps producing a book under its own id. Bionic Company knows that id is, for now, the custody of `a-era-dos-agentes-book`.

A component is not a product. Singular's screenplay is part of the film, not something the organization releases on its own.

### Custody

| Field | Notes |
|---|---|
| `domain` | |
| `ref` | The domain's own identifier for the work: a KDP `book.yaml` id, a Cine `project.yaml` id |
| `since` / `until` | A product has at most one current custodian |

A signal's `work_unit_ref` is the domain's own reference. The twin maps it to a product through custody.

### Flow

One product feeding another, for example a book adapted into a film.

| Field | Notes |
|---|---|
| `source` / `target` | Products |
| `relation` | Free text, read from source to target: `adapted into`, `enriches`, `promotes` |

Domains do not know each other, so no domain can report a flow. **The organization records it.** Flows join products, never custodies, so a change of custody breaks no flow.

### Intellectual property (named, not modelled)

Singular's book and film are two products on the same intellectual content: the story and its world. That content outlives any initiative and may give rise to more products later. It is not an entity yet. For now the initiative groups the products. It becomes one when a question needs it, such as rights, reputation across products, or a new product years later.

### Participation (derived)

A period during which a domain participated in an initiative through a capability.

| Field | Notes |
|---|---|
| `initiative_id`, `domain_id`, `capability_id` | |
| `first_signal_at` / `last_signal_at` | |
| `signal_count`, `cost` | Aggregates |

Participation is **derived from signals and custody**, never declared by hand. It is the "temporary relationship" in the organizational model.

### Actor

Who did something.

| Field | Notes |
|---|---|
| `id` | Scoped to its domain: `kdp-studio:jaime`, `cine-toaster:reviser` |
| `kind` | `human` · `agent` · `system` |
| `domain_id` | The domain that vouches for this actor |

KDP Studio and Cine Toaster both already use `human | agent | system`. The contract adopts that vocabulary.

Actor identity is federated: each domain vouches for its own actors. M0 does not attempt a global identity.

### Signal

Something that already happened, reported by a domain. This is the core of M0.

See [Signal envelope](#signal-envelope).

## The contract

### Capability manifest

Domain to organization. Published once and updated when it changes.

```json
{
  "domain": { "id": "cine-toaster", "name": "Cine Toaster" },
  "contract_version": "0.1",
  "provides": [
    { "capability": "audiovisual-production",
      "outcomes": ["scene", "sequence", "film", "trailer"] }
  ],
  "work_unit": { "kind": "production", "ref_field": "project.id" },
  "signals": ["work.started", "decision.recorded", "gate.opened", "gate.decided",
              "version.recorded", "cost.incurred", "outcome.delivered", "blocker.raised"]
}
```

The manifest says **what** the domain can achieve, not how.

### Signal envelope

Domain to organization.

```json
{
  "id": "cine-toaster:evt_3f9a1c02b7d84e11",
  "type": "gate.decided",
  "occurred_at": "2026-10-03T14:12:09Z",
  "domain_id": "cine-toaster",
  "work_unit_ref": "singular",
  "actor": { "id": "cine-toaster:jaime", "kind": "human" },
  "capability": "audiovisual-production",
  "summary": "Scene 030 cut v7 approved",
  "data": { "decision": "approve", "subject": "scene/030/v7" },
  "cost": null,
  "source": { "kind": "history.jsonl", "ref": "scenes/030-.../history.jsonl#L42" }
}
```

Rules:

- **`id` is globally unique and stable.** Re-ingesting the same signal is a no-op. Adapters can therefore re-read a source safely.
- **`type` comes from a small organizational vocabulary**, listed below. Domain-specific detail goes in `data`, which the twin stores but does not interpret.
- **`work_unit_ref`, not a product or initiative id.** It is the domain's own reference. The twin resolves the product, and through it the initiative, by custody.
- **`cost`**, when present, is `{ "amount": 1.84, "currency": "USD", "kind": "compute" }`.
- **`source`** points back to the domain's own record, so any organizational fact can be traced to its origin.

Initial signal vocabulary:

| Type | Meaning |
|---|---|
| `work.started` | A domain began work on something, or began serving a capability |
| `decision.recorded` | A domain decision with actor and reason |
| `gate.opened` / `gate.decided` | A human or policy gate opened or decided |
| `version.recorded` | A new version of a deliverable exists |
| `cost.incurred` | Money or resources spent |
| `outcome.delivered` | A result the organization can use |
| `blocker.raised` / `blocker.cleared` | Something prevents progress |

The vocabulary grows only when an initiative needs a fact the existing types cannot express.

### Intent envelope

Organization to domain. **Defined in M0, not sent until M1.** It is defined now only to keep it symmetrical with signals.

```json
{
  "id": "bionic:int_…",
  "initiative_id": "singular",
  "capability": "market-relationships",
  "desired_outcome": "Launch campaign for the Singular trailer",
  "priority": "high",
  "deadline": "2026-12-01",
  "constraints": { "budget": { "amount": 200, "currency": "USD" } },
  "actor": { "id": "bionic:jaime", "kind": "human" }
}
```

## The twin in M0

The twin is an **append-only signal log owned by Bionic Company**, plus projections derived from it.

```text
Domain records ──adapter──▶ Signals ──▶ Twin signal log (append-only, idempotent)
                                              │
                                              ├── Initiative timeline
                                              ├── Participations
                                              ├── Cost per initiative / domain / capability
                                              ├── Open gates and blockers
                                              └── Capability gaps
```

- The twin keeps its own copy of every signal. It never depends on a domain retaining history.
- Projections are disposable and rebuilt from the log. This applies the "records as truth" pattern to Bionic Company itself.
- Products and their custody, flows, initiatives, capabilities and provisions are organizational records that Bionic Company authors. They are versioned, but they are not signals.

## First implementations

M0 adapters are **read-only**. They read what domains already record and emit signals. No domain changes are required.

### KDP Studio

| Domain source | Signal |
|---|---|
| `book.yaml` identity | `work_unit_ref` |
| `state.json` gates (open) | `gate.opened` |
| `state.json` gates (decided, with rationale) | `gate.decided` |
| `state.json` decisions, e.g. a version adopted or rejected | `decision.recorded`, `version.recorded` |
| git commits with `Actor:` trailer | `decision.recorded` (actor, reason) |
| `kdp check` passing for an edition | `outcome.delivered` (candidate) |

KDP Studio records no cost today. Its signals carry `cost: null`.

### Cine Toaster

| Domain source | Signal |
|---|---|
| `project.yaml` id | `work_unit_ref` |
| `history.jsonl` per scene (append-only, ADR 0021) | `decision.recorded`, `gate.opened`, `gate.decided` |
| `versions/` + `VERSIONS.md` records | `version.recorded` |
| `<take>.job.json` provider job records, priced by the production's `generation_rates` | `cost.incurred` |
| `workflow.started` / `workflow.done` events | `work.started`, `outcome.delivered` (candidate) |

Cost comes from the production's own job records, not from Cine Toaster's machine-wide spend ledger. Reconciling the ledger, the production's records and the provider's billing is Cine Toaster's FinOps concern (its `docs/finops.md`: reconcile, do not duplicate). Bionic Company consumes the production's record. A job without a declared rate becomes a signal with its billed seconds and no amount. The twin shows it as unpriced spend instead of guessing a price.

Records imported from before Cine Toaster carry timestamps without a time zone. The adapter assumes the machine's local zone and marks the signal with `timestamp_assumed_local`.

Prefer the durable `history.jsonl` over `events.jsonl`. The latter is a disposable cache by design (ADR 0006).

The MCP server (`production_status`, `read_budget`) is a valid alternative transport for snapshots, but snapshots cannot reconstruct history. Durable records are the primary source.

### Pulse

Pulse has no implementation yet. In M0:

- `market-relationships` is a capability with **no provision**: a recorded capability gap.
- Pulse is a domain with status `planned`.
- Market-facing activity that happens anyway, such as a manual post or a press contact, may be entered as **manual signals** with `domain_id: "manual"` and a human actor.

This is deliberate. It shows the twin representing a need the organization has but cannot yet serve.

## Authority envelope (sketch, not used in M0)

M2 depends on representing the authority envelope. Its likely shape already exists across the ecosystem:

| Precedent | Element |
|---|---|
| Cine Toaster `spend.py`: a limit, checked before a job, refusing with `budget_exceeded` | **Budget limits** checked before action |
| Pulse README: `autonomous` · `supervised` · `approval_required` per action type | **Autonomy per action class** |
| KDP Studio and Cine Toaster: actor and reason on every decision | **Mandatory audit** |

A first shape:

```yaml
authority:
  scope: organization            # or a domain, initiative or capability
  budget:
    limit: { amount: 500, currency: USD, period: month }
  autonomy:
    agent.create: autonomous
    agent.retire: autonomous
    agent.count_above_limit: approval_required
    capability.new_provider: supervised
  limits:
    max_active_agents: 20
  audit: required                # every action emits a signal with actor and reason
```

Not implemented in M0. Recorded here so the signal contract already carries what an envelope will need: actor, cost and decision.

## Future compatibility

Some organizations may adopt Bionic Company later with a very different stack, Brix for example: TypeScript, a relational database, multi-tenant. Their current models do **not** constrain this design. The following choices only keep doors open:

1. **No storage assumption.** Signals are the interface. A domain backed by a database emits the same envelope as one backed by files.
2. **Organization is an entity, not a global.** A multi-tenant platform may later be one organization, or host many. M0 does not decide which, but nothing assumes a single organization.
3. **Federated actors.** Each domain vouches for its own actors. No global identity provider is required.
4. **Neutral schema.** JSON Schema, any transport. No Python, LangGraph or MCP dependency in the contract.

## Out of scope for M0

- Sending intent to domains (M1)
- Capability resolution beyond recording provisions and gaps (M1)
- Agent workforce management, the Meta-Agent and enforcing the authority envelope (M2)
- Simulation (M3)
- Real-time delivery. Periodic re-reading by adapters is enough.
- A user interface beyond what is needed to inspect projections

## Done when

M0 is complete when, for **Singular** and **A Era dos Agentes**, the twin can answer from its own log:

1. Which capabilities did this initiative use, through which domains, and over what periods?
2. What were the key decisions, by whom, and why, each traceable to its source record?
3. What did it cost, by domain and capability, where cost is recorded?
4. What is open now: gates, blockers, versions awaiting a decision?
5. Which needed capabilities have no provider?

And: rebuilding all projections from the log gives the same answers.

## Cross-domain validation: Singular

Before M1, the model was checked against the one initiative that already crosses domains. *Singular* is a book written by hand in 2025, not yet released and not yet in KDP Studio. It was adapted into a film whose screenplay was written in September 2026, and the film moved into Cine Toaster in October 2026.

```text
singular-book   Singular (book)   not released   now with: manual
    2025-07-16 → 2026-09-16  manual            4 signals
singular-film   Singular (film)   not released   now with: cine-toaster
    2026-09-15 → 2026-09-15  manual            1 signal   (the screenplay)
    2026-09-17 → 2026-10-04  cine-toaster    172 signals

singular-book —adapted into→ singular-film
```

What held:

- **One initiative, several products, several providers.** The signal contract did not change.
- **Initiatives do not belong to domains.** Singular's identity is untouched by which domain is working on it.

What had to be added:

- **External domains.** Work happens outside the autonomous domains: by hand, before a domain existed, or by a vendor. Without a place for it, the twin would show Singular starting in September 2026 instead of July 2025.
- **Manual signals.** A human-written file of signals, each citing its evidence. It is another adapter, not a special case.
- **Products with custody.** A first version modelled work units as `<domain>/<ref>`, so a product's identity depended on who worked on it, and moving the book into KDP Studio would have made it a different thing. Products now have the organization's identity, and custody moves. This is the same principle as initiatives, one level down.
- **Flows between products.** "The film adapts the book" is the most important fact about Singular's path, and no domain can report it.

What it showed:

- **Product, component, version, release.** The book and the film are products. The screenplay is a component of the film. Products evolve in versions, and a release freezes a version, at least for fiction.
- **Provision is not participation.** KDP Studio is the declared provider of editorial production. Singular's editorial work was done elsewhere. The twin keeps both facts: who is *expected* to provide a capability, and who *actually* did. This distinction is the input M1's capability resolution needs.
- **Timing is not causation.** Book v2 is dated the day after the screenplay. The twin shows the timing; whether the film fed back into the book is a flow only the organization can declare. Flows are declared, never inferred, for now.
- **A domain may report work from before its custody.** Cine Toaster's migration recorded SINGULAR's earlier versions as imported history, so its signals start before the custody date. The twin keeps when work happened and who reports it as separate facts.
- **The next needs are already known.** The book is to be enriched with what the film taught, before its release. The launch requires `market-relationships`, which has no provider. These are M1's two cases.

## Running it

The `bionic/` package implements the contract, the organizational records, the twin log and the adapters (KDP Studio, Cine Toaster, manual signals). The legacy AgentOS prototype is untouched.

```bash
uv sync
uv run bionic --org examples/organization ingest                  # read sources, append new signals
uv run bionic --org examples/organization overview                # initiatives, gaps, unclaimed work
uv run bionic --org examples/organization initiative a-era-dos-agentes
uv run pytest
```

`examples/organization/organization.yaml` is this ecosystem's data. Another organization writes its own and runs the same code. The twin log, `twin/signals.jsonl`, is local and not versioned.

## Open decisions

1. **Where the twin's log lives.** A JSONL file in an organization directory, consistent with the domains, or a database. A file is the M0 default.
2. **Adapter location.** Inside Bionic Company, reading domain files, or published by each domain. Inside Bionic for M0, to require no domain changes.
3. **Signal id derivation** for sources without ids, such as git commits and `state.json` entries.
4. **Whether `outcome.delivered` needs a human confirmation** or can be inferred, for example from `kdp check` passing.
5. ~~How Singular's pre-Cine-Toaster history is represented.~~ Resolved: Cine Toaster's migration recorded it as imported versions, and the book and screenplay before it are manual signals.
6. **Whether flows can ever be inferred**, for example from a production keeping its source book in `story/book`, or must always be declared.
7. **When intellectual property becomes an entity** rather than a name the initiative carries.
