# OpenJev as a Decision Intelligence Reference

> **Status:** research candidate — not an architectural dependency.
>
> **Reference:** https://huggingface.co/openjev/openjev

## Why this is relevant

BC-ARA identifies **Decision Intelligence** as a distinct responsibility in the Agentic Runtime Plane. OpenJev is a concrete example of a model optimized for typed decisions rather than free-form generation.

This makes it useful as a reference implementation for questions such as:

- Which agent should receive this task?
- Which model or tool should be selected?
- Which candidate action should be taken next?
- Is the task complete?
- Should execution continue, retry, change strategy, or escalate?
- Is a result sufficiently grounded or compliant?
- When is uncertainty high enough to invoke a stronger model or a human?

The architectural lesson is broader than OpenJev itself: agentic systems may benefit from a dedicated decision mechanism instead of using a large generative model for every micro-decision.

## What OpenJev is

According to its model card, OpenJev is a 27B open-weights decision model. At request time, the caller supplies state/context, a typed question, and labels or ordered criteria. The model returns a choice, yes/no probability, or score rather than free-form text.

For up to 52 options, it can score the alternatives in one forward pass. The implementation reads the model's first-position option scores and applies fixed calibration to produce probabilities.

The model card describes use cases including:

- routing and triage;
- judging other models;
- document/operations decisions;
- browser and desktop agent next-action selection;
- deciding whether a task is done;
- scoring ordered alternatives.

OpenJev can consume text, structured state such as DOM/JSON, and—on supported builds—screenshots.

## BC-ARA mapping

```text
Planner
   │
   ▼
Decision Intelligence
   │
   ├── deterministic rules / policy
   ├── OpenJev-like decision model
   ├── LLM reasoning
   └── human escalation
   │
   ▼
Delegation / Execution
   │
   ▼
Evaluation / Verification
```

OpenJev should therefore be treated as one possible **Decision Engine**, not as the Decision Intelligence architecture itself.

## Confidence-aware escalation

A particularly relevant pattern is:

```text
candidate decision
       ↓
decision model
       ↓
probability / confidence
       │
       ├── high confidence + low risk
       │        → execute
       │
       ├── ambiguous / low confidence
       │        → stronger reasoning / critic
       │
       ├── high risk
       │        → policy gate / human
       │
       └── prohibited
                → stop
```

Confidence alone must not define authority. Policy, risk, evidence, cost, and organizational authority may override the highest-probability action.

## Decision is not verification

OpenJev's own guidance recommends treating a `DONE` decision as an opinion and confirming completion using external evidence before stopping.

This strongly supports BC-ARA's separation:

```text
Decision Intelligence
        ≠
Evaluation / Verification
```

For example:

```text
Decision Engine
"Task is probably DONE: 0.94"
        ↓
Verifier
"Did the commit actually exist?"
"Did the tests pass?"
"Was the requested artifact produced?"
        ↓
verified completion / continue
```

This separation should remain true regardless of which decision technology is used.

## Potential ecosystem experiments

### Experiment A — Tool routing

Given an agent state and available tools, compare:

1. rules;
2. a general-purpose LLM;
3. an OpenJev-like decision model.

Measure decision quality, latency, cost, retries, and escalation rate.

### Experiment B — Model routing

Let the decision layer choose among different model classes according to task, confidence, risk, context size, and cost.

Measure whether inexpensive decisions can safely avoid unnecessary use of stronger models.

### Experiment C — Continue / retry / stop

After each execution step, ask whether the system should:

- continue;
- retry;
- change strategy;
- ask a critic;
- escalate;
- stop.

Always keep an independent completion verifier.

### Experiment D — Agent routing

Use Bionic Company's capability and agent registry as state and ask the decision layer which eligible agent should receive a task.

This could become a useful test of the future Agent Control Plane.

### Experiment E — Knowledge application

In conjunction with KnowEvolve, evaluate whether a candidate knowledge item should be:

- applied;
- ignored;
- challenged;
- escalated for reasoning.

This explores an **epistemic decision layer** without granting the decision model authority to modify knowledge or policy.

## Telemetry to capture

Experiments should preserve enough information to evaluate or later learn routing policy:

```text
decision.id
decision.type
decision.context
decision.options
decision.selected
decision.probabilities
decision.confidence
decision.engine
decision.latency
decision.cost

policy.constraints
risk.level

execution.outcome
evaluation.result
human.override
escalation.reason
```

This also provides useful data for KnowEvolve and future policy-learning research.

## Technical notes

The current OpenJev model card reports:

- 27B parameters;
- BF16 and FP8 variants;
- MLX builds for Apple Silicon;
- GGUF quantizations for llama.cpp;
- up to 52 alternatives in a single pass;
- up to 16,384 prompt tokens;
- optional image input on supported serving configurations;
- an API request/response shape compatible with the hosted Jev API.

These characteristics make local experiments possible, but infrastructure cost should be measured against simpler alternatives. A 27B decision model is not automatically cheaper or better than rules, a small classifier, a small general LLM, or a hosted decision service for every workload.

## Licensing and project relationship

OpenJev states that:

- model weights are **CC BY-NC 4.0**;
- research and other non-commercial use is permitted with attribution;
- commercial use requires a commercial licence;
- files in `helper/` and `serve/` are Apache 2.0;
- OpenJev is independent and **not affiliated with TypeSafe**;
- Jev is TypeSafe's product.

This is significant for Bionic Company's broader ambitions. OpenJev can be investigated and benchmarked, but the current model-weight licence means it should **not** silently become a commercial architectural dependency.

## Alternatives must remain open

The Decision Intelligence capability should be implementation-agnostic. Candidate implementations include:

- deterministic rules;
- policy engines;
- classical classifiers;
- small language models;
- OpenJev / Jev-like decision models;
- general-purpose reasoning models;
- contextual bandits or learned routing policies;
- human decision gates.

Hybrid approaches are expected.

## Architectural conclusion

OpenJev is useful because it validates an architectural category already identified by BC-ARA:

> **Decision Intelligence deserves to be modeled independently from planning, execution, and verification.**

The project should use OpenJev as a concrete research reference and benchmarking candidate, while keeping BC-ARA independent of it.
