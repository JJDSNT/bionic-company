# Case: enriching the Singular book with what the film taught

> Status: open learning case, and **the answer key of a blind test**. Nothing here is decided.
>
> The author chose not to declare the missing capability. The test is whether Bionic Company can **discover** the need, **build** the capability and **use** it by itself. This document is development knowledge: it must never become part of what Bionic Company reasons over (organization records, decisions, signals, manifests, or any agent's context). See [Development knowledge is not organizational knowledge](../m0-model.md#development-knowledge-is-not-organizational-knowledge).

## Success criteria (set before the test)

Each stage counts on its own. Discovering without building is already a result.

| # | Stage | Passes when |
|---|---|---|
| 1 | **Discover** | From evidence, with no such capability declared, Bionic Company identifies that a transformation is missing between the film and the book |
| 2 | **Name** | It proposes a capability *between* domains, instead of folding it into KDP Studio or Cine Toaster |
| 3 | **Build** | Within its authority, it creates the capability (M2) |
| 4 | **Use** | The capability yields candidate versions that land in the book, and the author decides what to adopt |
| 5 | **Recognise** | The twin records where the capability emerged and can reuse it, e.g. for an adaptation in the other direction |

Results are recorded at the end of this document as they happen.

## The scenario

*Singular* is a fiction book, written by hand and not yet released. It was adapted into a screenplay, which is part of the film now in production in Cine Toaster. The author intends to revisit the book before its release, enriching it with what writing the screenplay and making the film revealed.

```text
singular-book ──adapted into──▶ singular-film
      ▲                               │
      └────────── enriches ───────────┘   (intended)
```

Since a released fiction book does not change, the enrichment has to land in a version before the book's release.

## What the model recorded

In M1 the intent `enrich-singular-book` was stated, with the film as its input (`draws_on: singular-film, enriches`). BizOps resolved it to **KDP Studio**, the only active provider of `editorial-production`, noting that the book's custody would move there from manual work.

## The gap the resolution did not see

**There is no mechanism yet for how the film's learnings become changes in the book.** The author has said so directly.

The transformation sits between the two domains, and neither provides it:

- **KDP Studio** works on a manuscript. It revises, versions, checks and gates a book.
- **Cine Toaster** works on a film. It keeps the screenplay's versions and the production's decisions.
- **Carrying learning from one medium back into another** belongs to neither.

BizOps resolved the intent by **where the outcome lands**: the book, so an editorial provider. It did not ask **whether the transformation the outcome needs is available**. A coarse capability, `editorial-production`, hid a gap at a finer grain. The intent shows `resolved` while its essential step has no provider.

This is the first gap discovered *inside* a resolved intent rather than at the capability level. That makes it more informative than the launch, whose gap is visible from the capability map alone.

## How the process might come to exist

These are hypotheses, not choices. They are recorded so that whichever path happens can be recognised and compared.

| Shape | Where the capability lives | What already points this way |
|---|---|---|
| **Human-led** | The author reads the screenplay and the film's decisions and revises the book. The work is external; the versions land in KDP Studio | The book was written this way. Book v2 is dated the day after the screenplay |
| **The source domain exports** | Cine Toaster produces an outcome describing how the adaptation diverged from or deepened the book. KDP Studio takes it as an input | Cine Toaster keeps the screenplay's versions and every decision with its rationale |
| **The destination domain imports** | KDP Studio gains an agent that reads an external source and proposes candidate versions, which the author adopts or rejects | KDP Studio's agents already answer with edits as candidate versions behind human gates (its ADR 0009) |
| **A new capability** | The organization creates a cross-media adaptation capability, an agent or a domain, serving both directions (M2) | Adaptation runs both ways here: book into film, then film back into book |

In every shape, the author decides what enters the book. That is a constraint any mechanism inherits from KDP Studio's gates, not something Bionic Company imposes.

## What Bionic Company should be able to learn from it

- **Which shape actually happened**, observed through signals rather than declared.
- **Whether the capability emerged**, where it settled, and whether it was reused. For example, a second adaptation in either direction.
- **What it took:** time, actors (human or agent), and how many candidate versions were proposed and adopted.
- **Whether the gap was felt where the model predicted.** For example, a KDP Studio `blocker.raised` after handoff, saying the input cannot be used as it is.

## What it suggests for the model (to revisit, not yet changed)

1. **Resolution may need to check transformations, not only capabilities.** "Who provides editorial production" is not the same question as "who can turn a film's learnings into a book's revision". Capabilities may need to say what they take as input as well as what they produce.
2. **A resolved intent can turn out to be a gap.** The lifecycle has no path from `resolved` back to `gap` triggered by the provider. A domain raising a blocker on a handed-off intent may be that path.
3. **Some capabilities belong between domains.** If cross-media adaptation becomes a capability, it is the first one no current domain would naturally own. It is a candidate for organizational adaptation (M2) rather than for an existing domain.
4. **Granularity is discovered, not designed.** The capability map stays coarse until a real case like this one shows where it is too coarse.

## Results

### Stage 1, Discover: passed, with a caveat (2026-10-05)

Resolution gained a general check: whether the chosen provider can work from the intent's inputs. KDP Studio's manifest declares that editorial production works from `book` and `text`. The intent draws on the film. Re-resolved, the intent became a gap of transformation:

> kdp-studio provides editorial production and would receive the outcome, but it works from book, text, not film. Turning singular-film into book or text for it has no provider: a missing transformation, not a missing editorial production.

No capability was declared, and the mechanism names only kinds. **Caveat:** the mechanism was designed by people who knew this case. It is general, but it is not an independent discovery. A stronger test is a later case of the same shape that nobody anticipated.

### Stage 2, Name: partial

The resolution describes the need as a transformation *between* a provider and its input ("turns film into book or text"), and does not fold it into KDP Studio or Cine Toaster. It does not yet propose a capability with an identity, a place or an owner. That belongs to M2.

### Stages 3–5: deferred (2026-10-05)

The author chose not to build the capability yet: the screenplay is not finished, so the input the enrichment draws on is not ready. The capability is to be built when the moment is right, not ahead of it.

This adds one observation for the model: **an intent's inputs have readiness.** The intent draws on the film, but enrichment only makes sense once the screenplay is final. The model has no way to say "this input is not ready yet", so the intent shows as an actionable gap when it is really waiting on its input. To revisit when the case resumes.

## Related

- [m1-model.md](../m1-model.md): Case A, the intent this case refines
- [m0-model.md](../m0-model.md): cross-domain validation, products and flows
