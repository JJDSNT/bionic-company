# Backlog

Everything pending, in one place. Each item links to where it is discussed. Last updated 2026-10-05.

## Waiting on the author

| Item | Why it waits | Where |
|---|---|---|
| **Objectives**: which objectives the initiatives serve | More complex than a sentence per initiative; to be worked on later. Until then none are declared, and the overview says so | [m1-model.md](m1-model.md), open question 5 |
| **Launch of Singular**: choose among wait, external work, or adapt (M2) | The intent `launch-singular` is a gap; the choice is the author's | [m1-model.md](m1-model.md#gaps) |
| **Blind test, stages 3–5**: build, use and recognise the film-to-book capability | The screenplay is not finished, so the input is not ready | [cases/singular-book-enrichment.md](cases/singular-book-enrichment.md) |

## Next foundations (no dependency on the domains)

| Item | What it is | Where |
|---|---|---|
| **Input readiness** | An intent's inputs can be not ready yet, e.g. a screenplay still in progress. Today the intent shows as an actionable gap when it is really waiting | [cases/singular-book-enrichment.md](cases/singular-book-enrichment.md#stages-35-deferred-2026-10-05) |
| **M2 — Adapt, conceptual design** | What Bionic Company may create, change or retire by itself (agents, capabilities) within the authority envelope, and what it must propose for approval. Includes naming a discovered capability: identity, place, owner (blind test stage 2) | [organizational-model.md](organizational-model.md#organizational-adaptation-and-self-evolution) |
| **Release semantics** | Releases are modelled (`outcome.delivered` carrying a version) and products declare `after_release`, but nothing yet flags a change to a released `frozen` version | [m0-model.md](m0-model.md#product) |
| **Authority envelope, extended** | Today: intent actions by actor or kind, scoped by initiative and capability. Still missing: budgets, limits (e.g. number of agents), and M2's actions | [m1-model.md](m1-model.md#direction-and-authority) |
| **M3 — Learn & Simulate** | Not started | [organizational-model.md](organizational-model.md#organizational-twin) |

## Open design questions

| Question | Where |
|---|---|
| Is `accepts` by kind fine-grained enough for resolution? | [m1-model.md](m1-model.md#open-questions), 0 |
| Intent granularity: one per desired outcome, breakdown left to the domain? | [m1-model.md](m1-model.md#open-questions), 1 |
| Can an intent draw on a product from another initiative? | [m1-model.md](m1-model.md#open-questions), 4 |
| Where the twin's log lives: a file (current default) or a database | [m0-model.md](m0-model.md#open-decisions), 1 |
| Adapters inside Bionic Company (current) or published by each domain | [m0-model.md](m0-model.md#open-decisions), 2 |
| Does `outcome.delivered` need a human confirmation, or can it be inferred? | [m0-model.md](m0-model.md#open-decisions), 4 |
| Can flows ever be inferred, or must they always be declared? | [m0-model.md](m0-model.md#open-decisions), 6 |
| When intellectual property becomes an entity rather than a name the initiative carries | [m0-model.md](m0-model.md#intellectual-property-named-not-modelled) |
| Multi-tenancy: is a platform such as Brix one organization, or host to many? | [m0-model.md](m0-model.md#future-compatibility) |

## Outside Bionic Company

Bionic Company only observes these. Each is noted in one line, to recognise it when it changes.

| Item | Effect on Bionic Company |
|---|---|
| The Singular book moves into KDP Studio | Its custody changes, and the enrichment intent can be handed off for real |
| Pulse exists only as a README | `market-relationships` stays a gap; Pulse is its planned provider |
| Singular's production declares no `generation_rates` | Its 138 billed jobs (5.11 h) show as unpriced spend |
| Cine Toaster's FinOps reports spend it cannot attribute to any job | Bionic Company sees only the production's own records, so that spend is invisible to it |
| Actors of commits made by hand in a KDP Studio book are identified by the git e-mail | The twin's local log holds e-mail addresses; consider names instead |
