# M1 — Direct

> Status: implemented. Both of Singular's needs currently resolve to gaps; handoff and fulfilment are tested but not yet exercised on real data. Builds on [m0-model.md](m0-model.md).

## Purpose

M0 made the organization observable. M1 makes it **steerable**: the organization states what an initiative needs next, and BizOps relates that need to the capabilities available, without prescribing how any domain works.

The hypothesis M1 tests is:

> **Direction can be expressed as intents on an initiative. BizOps can resolve each intent to a provider, or to an explicit gap, and the twin can follow the intent to its fulfilment through ordinary domain signals.**

## The first two cases

Both come from *Singular*, and they test opposite outcomes of resolution.

| | Case A — Enrich the book | Case B — Launch |
|---|---|---|
| Direction | Revisit the book with what the screenplay and the film taught, before its release | Bring Singular to its audience |
| Capability | `editorial-production` | `market-relationships` |
| Product | `singular-book`, its next unreleased version | `singular-book`, `singular-film` |
| Draws on | `singular-film`, including its screenplay | the book, the film |
| Resolution | **A provider exists**: KDP Studio | **Gap**: no provider |
| What it tests | Resolution, handoff, fulfilment through signals; a change of custody (the book moves from manual work into KDP Studio); a planned flow that becomes an observed one | What the organization does with a need it cannot serve |

Case A closes the loop the organizational model describes: creative learning from audiovisual work flows back into editorial work.

```text
singular-book ──adapted into──▶ singular-film
      ▲                               │
      └──── enriches ─────────────────┘
            planned in M1, observed once fulfilled.
            The book's custody moves from manual work to KDP Studio; it stays the same product.
```

> **Case A hides a gap.** It resolves to KDP Studio because the book lands there, but no domain yet provides the step in the middle: turning the film's learnings into changes in the book. This is recorded as a learning case in [cases/singular-book-enrichment.md](cases/singular-book-enrichment.md).

Because Singular is fiction, a released version never changes. The enrichment must therefore land in a version **before** the book's release, and it can, since the book is not released yet.

## Intent

An intent is a need the organization states for an initiative. It says **what** and **why**, never **how**.

| Field | Notes |
|---|---|
| `id` | |
| `initiative` | |
| `capability` | The business capability the need calls for |
| `product` | The product the outcome lands in, if it is an existing one |
| `desired_outcome` | In the organization's words |
| `draws_on` | Products whose results the outcome should build on. These are planned flows |
| `priority`, `deadline` | Optional |
| `constraints` | Optional: budget, policy, quality bar |
| `stated_by` | Actor: who gave the direction |
| `status` | See the lifecycle below |

`draws_on` is how a planned flow is written. When the intent is fulfilled, each planned flow becomes an observed flow into the product.

An intent never targets a released, `frozen` version. It targets the next version, or a new product.

Every decision about an intent is a signal in the contract's envelope, reported by the `bionic` domain and appended to `decisions.jsonl` in the organization directory. That file is the organization's own record, versioned with it. The twin ingests it like any domain's. **Bionic Company reports its decisions through the same contract it asks of the domains**, so they share one history.

## Lifecycle

```text
stated ──▶ resolved ──▶ handed off ──▶ in progress ──▶ fulfilled
   │           │                              │
   │           └──▶ gap ◀──── re-resolve ─── blocked   (the provider raised a blocker)
   │                 └──▶ (wait · external work · adapt in M2)
   └──▶ withdrawn            (any state but fulfilled may become withdrawn)
```

| Status | Meaning | Recorded by |
|---|---|---|
| `stated` | The need exists | A human, or later an agent within its authority |
| `resolved` | A provider was chosen, with its rationale | BizOps |
| `gap` | No provider exists. The resolution names the options | BizOps |
| `handed off` | The provider received the desired outcome and constraints | BizOps |
| `in progress` | The product's current custodian reports signals | The twin, derived |
| `blocked` | The provider raised a blocker after the handoff and has not cleared it | The twin, derived |
| `fulfilled` | The desired outcome was delivered | A human, in M1 |
| `withdrawn` | The organization no longer wants it | A human |

`in progress` and `blocked` are **derived**, never declared. If the domain is working on it, or cannot go on, the twin sees it. A blocked intent may be resolved again, and may then turn out to be a gap. This is how a domain reveals, after the handoff, that a resolution was wrong.

## Resolution

Resolution is BizOps' first real decision.

1. **Find the declared providers** of the capability, from the provisions.
2. **Read the twin.** It shows who actually provided this capability before, especially for this initiative. Provision is not participation (M0 finding).
3. **Decide:**
   - one provider → choose it;
   - several → choose one, and record why;
   - none → `gap`, naming the options: wait, external work, or adapt (M2).
4. **Record the decision** with actor and rationale, as a signal.

Case A: KDP Studio is the only declared provider, but Singular's editorial work so far was done by hand. Choosing KDP Studio means the book moves into it, which is a change of custody. This is the first decision where M0's observation changes an M1 choice.

In M1, BizOps can be a deterministic rule plus a human confirming. An agent is not needed until resolution involves real judgement, such as several providers, cost or capacity. This follows the principle that concepts enter when a hypothesis needs them.

### Can the provider work from the inputs?

Resolution asks two questions, not one: **who provides the capability**, and **whether that provider can work from what the intent draws on**.

A domain's capability manifest declares what each capability `accepts` as input, for example `book` and `text`. Each product has a `kind`. If an input's kind is not among what the chosen provider accepts, the intent is not resolved. It is a **gap of transformation**: the provider would receive the outcome (`lands_with`), but nothing turns the input into something it can use.

A provider that declares no `accepts` is not read as accepting anything. Its inputs are reported as unchecked.

This is a general mechanism. It names the kinds on both sides and nothing else. It was prompted by a learning case, but it does not encode that case's answer.

## Handoff

Today no domain accepts intents through an interface. M1 does not require one.

- **What crosses the boundary:** the desired outcome, the constraints, and references to the inputs (`draws_on`), each located by the domain that holds it now. This is the intent envelope (`contract/intent.schema.json`). `bionic intent envelope <id>` shows it, and the handoff records it.
- **What does not cross:** the initiative's internals, other domains' details, or how to do the work.
- **How it crosses, in M1:** by hand. A person carries the intent to the domain, for example by migrating the Singular book into KDP Studio with the desired outcome as the book's intention. Bionic Company records the handoff and the book's new custody.
- **Later:** a domain may accept intents directly, over any transport. The envelope does not change.

Domains still never need to know initiatives exist. KDP Studio receives a book and a purpose. Bionic Company knows that book serves Singular.

## Fulfilment

- The new custody maps KDP Studio's reference to `singular-book`, so its signals reach the product and the intent.
- The intent is `fulfilled` when the enriched version is accepted, by a human in M1. It is not the book's release, which is a separate, later outcome.
- Each `draws_on` entry becomes an observed flow. For Case A: `singular-film —enriches→ singular-book`.

## Gaps

Case B is resolved as a gap. M1 only has to make it explicit and actionable:

| Option | Meaning |
|---|---|
| **Wait** | The intent stays open. The twin shows an unmet need with its age and priority |
| **External work** | Someone does it by hand or a vendor does. It is observed through manual signals, like the original book |
| **Adapt** | The organization creates the capability. This is M2: Pulse, or an agent workforce for it |

Choosing among these is a human decision in M1. That choice is exactly what the M2 authority envelope will later bound.

## Direction and authority

Two foundations sit above intents.

**Objectives.** People set the direction: what the organization wants, with a priority and a horizon. Initiatives declare which objectives they serve. The overview shows objectives → initiatives → open intents, and flags initiatives that serve none. BizOps does not set objectives.

**The authority envelope.** It states who may take which intent actions (`state`, `resolve`, `choose`, `handoff`, `fulfil`, `withdraw`), on which initiatives and capabilities. `who` is an actor id or a kind (`human`, `agent`). Every decision records the grant that allowed it. An action outside the envelope is refused.

```yaml
authority:
  - {who: human, may: ["*"]}
  - {who: bionic:planner, may: [state, resolve], capabilities: [market-relationships],
     note: the planner may state and resolve market needs}
```

Without a declared envelope, **people may decide anything and agents nothing**. Granting an agent authority is therefore always an explicit act. This is the first concrete form of "strategy governs; autonomy operates". Budgets, limits on agent count, and the actions of M2 (creating, changing and retiring agents and capabilities) extend the same envelope later.

## Out of scope

- Domains receiving intents through an interface
- An agent acting as BizOps
- Priorities across initiatives, and capacity planning
- Enforcing constraints: budget, policy (M2's authority envelope)
- Creating capabilities to close gaps (M2)

## Done when

1. Case A and Case B are stated as intents on Singular.
2. Case A resolves to KDP Studio and Case B to a gap, each with a recorded rationale.
3. Case A's handoff moves `singular-book` into KDP Studio's custody, and the twin shows the intent `in progress` from KDP Studio's own signals, with no manual status change.
4. When Case A is fulfilled, the planned flow from the film appears as an observed flow into the book.
5. Case B stays visible as an open gap with its options.
6. Every organizational decision (stated, resolved, handed off, fulfilled) is in the twin's history, next to the domains' decisions.

## Where it stands

Both cases are stated in `examples/organization/decisions.jsonl`, and both are currently gaps:

```text
enrich-singular-book  [gap]  editorial-production → singular-book
    lands with: kdp-studio, once its inputs are transformed
    kdp-studio provides editorial production and would receive the outcome, but it works from book, text,
    not film. Turning singular-film into book or text for it has no provider: a missing transformation,
    not a missing editorial production.
      wait · external: transform outside the domains, hand kdp-studio the result · adapt: create it (M2)

launch-singular  [gap]  market-relationships
    No active domain provides market intelligence & relationships.
      wait · external · adapt (M2); planned provider: pulse
```

The first case was resolved to KDP Studio until resolution learned to check inputs. Its history keeps both decisions. No objectives are declared yet, and the authority envelope is the default.

```bash
uv run bionic --org examples/organization intents
uv run bionic --org examples/organization overview                                 # direction, gaps, authority
uv run bionic --org examples/organization intent choose launch-singular wait --by <person>
```

## Open questions

0. ~~Does resolution need to check transformations, not only capabilities?~~ Yes: resolution now checks declared inputs ([learning case](cases/singular-book-enrichment.md)). Still open: whether `accepts` by kind is fine-grained enough.

1. **Intent granularity.** Is "enrich the book" one intent, or several, such as structure, characters and new scenes? M1 suggests one per desired outcome, and leaves the breakdown to the domain.
2. ~~Does the book stay one work unit after migration?~~ Resolved: it is one product, and the migration is a change of custody.
3. ~~Who may state an intent?~~ Whoever the authority envelope grants; by default people only.
5. **What objectives does this organization have?** None is declared yet. They are set by people, not inferred.
4. **Can an intent draw on a product from another initiative?** For example, *A Era dos Agentes* using material from Singular.
