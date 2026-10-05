# Bionic Company

**An experimental architecture for building adaptive, agentic organizations.**

Bionic Company explores how an organization can combine human direction, autonomous AI agents, business capabilities, organizational digital twins and adaptive operating models into a system that can **understand itself, align strategy with execution, reorganize its workforce and learn from what happens**.

The project started as **AgentOS**, an experiment in planning and executing digital-transformation actions with AI agents. That original direction is not discarded: it has evolved into a broader question.

> **What would it take to make a bionic organization computationally observable, steerable, adaptive and eventually simulatable?**

The current working hypothesis combines three concerns:

> **Agentic BizOps + Organizational Digital Twin + Organizational Adaptation**

This is a working architecture, not a claim that the final model is already known.

## Why this project exists

Traditional software usually models applications and workflows. Agentic systems make it possible to experiment with something larger: the organization itself as a dynamic system.

Bionic Company investigates an organization in which:

- humans provide strategic direction, priorities, policies, budgets and constraints;
- initiatives move through the organization without belonging permanently to a department or software domain;
- autonomous domains expose business capabilities and decide how their internal work is performed;
- agentic workforces can be composed, reorganized and retired according to changing needs;
- organizational signals keep a digital representation synchronized with real activity;
- observed flows and outcomes can later support scenario simulation and decision-making.

The goal is not to build a universal autonomous company in one step. The repository is intended to evolve through small, testable implementations.

## Core principles

### Strategy governs; autonomy operates

Human governance is primarily concerned with **direction and boundaries**: strategy, objectives, priorities, budgets, risk tolerance, policies and other constraints.

Within that authority envelope, the organization may autonomously decide how to organize work, including how many agents are useful, how teams are composed, how work is distributed and when capacity should be reassigned or retired.

Human gates may exist where strategy, policy, risk or another explicit constraint requires them; they are not assumed for every internal agent decision.

### Initiatives do not belong to domains

An initiative represents something the organization is pursuing. It is not structurally owned by a particular application or domain.

As its state and direction change, different capabilities may become relevant:

```text
Initiative + Current State + Direction
                  │
                  ▼
                BizOps
                  │
                  ▼
        Capability required now
                  │
                  ▼
         Capability resolution
                  │
                  ▼
        Domain / Agent / Resource
                  │
                  ▼
           Result + Signals
                  │
                  ▼
        Updated Initiative State
```

Domains can evolve, capabilities can move, and new resources can appear without requiring the initiative itself to be redesigned.

### Domains remain autonomous

Bionic Company operates at the organizational level. It should not become a universal task executor.

A domain may receive an organizational outcome, priority, deadline, policy or resource constraint. The domain decides how to achieve that outcome using its own agents, workflows, models and tools.

> **Bionic Company defines direction and desired outcomes; domains determine their internal execution.**

## Agentic BizOps

BizOps connects organizational intent with execution without absorbing operational workflows.

Its concerns may include:

- strategy and objectives;
- initiatives and desired outcomes;
- priorities and policies;
- resource and budget constraints;
- capability resolution;
- cross-domain coordination;
- organizational risks and performance.

Conceptually:

```text
Strategy / Direction
        ↓
     Initiative
        ↓
      BizOps
        ↓
Capabilities & Resources
        ↓
 Autonomous Execution
        ↓
Results / Cost / Risk / Signals
        ↓
Organizational Understanding
        ↺
```

## Organizational Digital Twin

The Organizational Digital Twin is intended to become a living model of the organization rather than merely an organizational chart or dashboard.

It has two primary purposes.

### Observe and map

The twin should represent the organization's **current state, flows, processes, capabilities, agents, resources and temporary relationships**.

A relationship such as an initiative currently working with an audiovisual domain describes what is happening at that moment. It does not mean that the initiative permanently belongs to that domain.

Over time, the twin can accumulate organizational memory about how work and value actually flow.

### Simulate

The same representation may later support **what-if analysis**.

The organization could compare possible directions using observed information about time, cost, capacity, dependencies, risks and outcomes:

```text
Current State
     │
     ├── Scenario A → possible consequences
     ├── Scenario B → possible consequences
     └── Scenario C → possible consequences
                         │
                         ▼
                      Decision
                         │
                         ▼
                   Real execution
                         │
                         ▼
                       Signals
                         │
                         └──→ Twin learns / updates
```

Simulation is decision support, not certainty about the future. Real execution provides evidence that can progressively improve the model.

## Organizational adaptation

A bionic organization should not require a permanently predefined workforce.

A **Meta-Agent / Agent Workforce** capability may identify missing capacity and create, configure, specialize, compose, reassign or retire organizational agents as needs change.

Bionic Company also has technical needs of its own. Development, DevOps, SRE, FinOps and other specializations may emerge to maintain, evolve, observe and optimize the organizational platform itself.

The same principle can exist recursively inside autonomous domains: a domain may maintain its own agents responsible for development, reliability or adaptation.

> **Self-maintaining domains; self-evolving organization.**

The architecture intentionally does not attempt to enumerate every future organizational specialization in advance. New capabilities should emerge from real needs.

## Validation environment

The first validation environment is deliberately concrete.

Bionic Company is currently being explored alongside three autonomous agentic domains:

- **KDP Studio** — editorial production;
- **Cine Toaster** — audiovisual production;
- **Pulse** — market intelligence, relationships, communication, community and reputation.

Two real initiatives provide initial scenarios:

- **Singular** — a creative initiative that can move between editorial, audiovisual and market-facing activity;
- **A Era dos Agentes** — an editorial initiative that can also require other organizational capabilities as it evolves.

These projects are **not the architecture of Bionic Company**. They are its current validation environment.

The intended concepts should be able to generalize to other organizations, domains, initiatives and operating scenarios. The architecture should therefore avoid hard-coding assumptions that only make sense for this ecosystem.

## A first validation path

The project will initially favor a small vertical slice over a complete organizational ontology.

A useful progression is:

```text
M0 — Observe
Represent enough organizational state to see real initiatives,
domains, capabilities, agents and activity.

M1 — Direct
Receive organizational direction and allow BizOps to relate
an initiative's current needs to available capabilities.

M2 — Adapt
Allow the organization to reorganize its agentic workforce
within its authority and constraints.

M3 — Learn & Simulate
Use observed flows, costs, outcomes and signals to improve
organizational understanding and explore alternative scenarios.
```

Concepts should enter the implementation when they are needed to validate the next hypothesis, rather than because they might eventually be useful.

## From AgentOS to Bionic Company

The original prototype implemented a simple experimental flow:

```text
Goal → Planner Agent → First Action → Executor Agent
```

That experiment remains useful history. It demonstrated an initial form of agentic planning and execution, but it coupled organizational reasoning too closely to a generic planner/executor workflow.

The emerging model moves the abstraction upward:

```text
Human Direction / Organizational Context
                  ↓
                BizOps
                  ↓
              Initiative
                  ↓
        Dynamic Capability Use
                  ↓
         Autonomous Execution
                  ↓
               Signals
                  ↓
      Organizational Digital Twin
                  ↓
       Understanding / Simulation
                  ↓
       Decision / Adaptation
```

The original prototype is preserved in [`legacy/agentos/`](legacy/agentos/). Nothing in the current implementation depends on it.

## Technology

The project has experimented with or is considering technologies such as:

- LangChain and LangGraph;
- Ollama and other model providers;
- FastAPI;
- AG-UI;
- MCP;
- A2A;
- event-driven integration;
- digital-twin and simulation techniques.

No framework or protocol defines the project. Technology choices should follow the organizational model and the hypotheses being tested.

## Architecture notes

| Document | What it holds |
|---|---|
| [docs/organizational-model.md](docs/organizational-model.md) | The working theory: boundaries, principles, open questions |
| [docs/m0-model.md](docs/m0-model.md) | M0 — Observe: entities, the contract, the twin, cross-domain validation |
| [docs/m1-model.md](docs/m1-model.md) | M1 — Direct: intents, resolution, handoff, fulfilment |
| [docs/cases/](docs/cases/) | Learning cases: real situations the model does not yet handle well |
| [contract/](contract/) | The organizational contract as language-neutral JSON Schema |

The README intentionally stays focused on what the project is, why it exists and how the current validation environment relates to the broader idea.

## Status

**Experimental / early architectural validation.**

| Stage | State |
|---|---|
| M0 — Observe | Implemented. The twin observes KDP Studio and Cine Toaster through read-only adapters, plus work done outside any domain, and reconstructs *A Era dos Agentes* and *Singular* |
| M1 — Direct | Implemented: objectives, an authority envelope, intents, resolution that checks a provider's inputs. *Singular*'s two needs are both gaps: enriching the book lacks a film-to-book transformation; the launch lacks a provider |
| M2 — Adapt | Not started |
| M3 — Learn & Simulate | Not started |

```bash
uv sync
uv run bionic --org examples/organization ingest        # read the domains' records into the twin
uv run bionic --org examples/organization overview      # initiatives, capability gaps, open intents
uv run bionic --org examples/organization initiative singular
uv run pytest
```

`examples/organization/` holds this ecosystem's data. Another organization writes its own and runs the same code.

Bionic Company is not presented as a finished reference architecture. Its purpose is to turn ideas about bionic organizations into executable experiments, learn from real initiatives and progressively discover which abstractions are actually useful.

## Author

Jaime José Dias da Silva Neto
