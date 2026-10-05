# M1 — Direct

> Status: proposal. Builds on [m0-model.md](m0-model.md).

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
      └──── enriched by ──────────────┘
            planned in M1, observed once fulfilled.
            The book's custody moves from manual work to KDP Studio; it stays the same product.
```

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

Intents are organizational records, kept beside `organization.yaml`. Every change of status is also a signal in the twin, with `domain_id: bionic`. The organization's own decisions are therefore part of the same history as the domains'.

## Lifecycle

```text
stated ──▶ resolved ──▶ handed off ──▶ in progress ──▶ fulfilled
   │           │                                          
   │           └──▶ gap ──▶ (wait · external work · adapt in M2)
   └──▶ withdrawn            (any state may become withdrawn)
```

| Status | Meaning | Recorded by |
|---|---|---|
| `stated` | The need exists | A human, or later an agent within its authority |
| `resolved` | A provider was chosen, with its rationale | BizOps |
| `gap` | No provider exists. The resolution names the options | BizOps |
| `handed off` | The provider received the desired outcome and constraints | BizOps |
| `in progress` | The product's current custodian reports signals | The twin, derived |
| `fulfilled` | The desired outcome was delivered | A human, in M1 |
| `withdrawn` | The organization no longer wants it | A human |

`in progress` is **derived**, never declared. If the domain is working on it, the twin sees it.

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

## Handoff

Today no domain accepts intents through an interface. M1 does not require one.

- **What crosses the boundary:** the desired outcome, the constraints, and references to the inputs (`draws_on`). This is the intent envelope from M0.
- **What does not cross:** the initiative's internals, other domains' details, or how to do the work.
- **How it crosses, in M1:** by hand. A person carries the intent to the domain, for example by migrating the Singular book into KDP Studio with the desired outcome as the book's intention. Bionic Company records the handoff and the book's new custody.
- **Later:** a domain may accept intents directly, over any transport. The envelope does not change.

Domains still never need to know initiatives exist. KDP Studio receives a book and a purpose. Bionic Company knows that book serves Singular.

## Fulfilment

- The new custody maps KDP Studio's reference to `singular-book`, so its signals reach the product and the intent.
- The intent is `fulfilled` when the enriched version is accepted, by a human in M1. It is not the book's release, which is a separate, later outcome.
- Each `draws_on` entry becomes an observed flow. For Case A: `singular-film —enriched→ singular-book`.

## Gaps

Case B is resolved as a gap. M1 only has to make it explicit and actionable:

| Option | Meaning |
|---|---|
| **Wait** | The intent stays open. The twin shows an unmet need with its age and priority |
| **External work** | Someone does it by hand or a vendor does. It is observed through manual signals, like the original book |
| **Adapt** | The organization creates the capability. This is M2: Pulse, or an agent workforce for it |

Choosing among these is a human decision in M1. That choice is exactly what the M2 authority envelope will later bound.

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

## Open questions

1. **Intent granularity.** Is "enrich the book" one intent, or several, such as structure, characters and new scenes? M1 suggests one per desired outcome, and leaves the breakdown to the domain.
2. ~~Does the book stay one work unit after migration?~~ Resolved: it is one product, and the migration is a change of custody.
3. **Who may state an intent?** Only humans in M1. Later, an agent within its authority. This is the first concrete use of the authority envelope.
4. **Can an intent draw on a product from another initiative?** For example, *A Era dos Agentes* using material from Singular.
