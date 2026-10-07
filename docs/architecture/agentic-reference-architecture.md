# Bionic Company Agentic Reference Architecture (BC-ARA)

> **Status:** exploratory reference architecture.
>
> BC-ARA is a technology-agnostic model for designing, operating, governing, evaluating, observing, and continuously improving agentic organizations. It is a reference model, not a requirement that every domain use the same runtime or framework.

## Why BC-ARA exists

A collection of capable agents is not, by itself, a complete agentic architecture. BC-ARA makes the responsibilities around those agents explicit:

- Who turns organizational intent into plans?
- Who decides which agent, model, tool, skill, or knowledge should be used?
- How is uncertainty represented and when is work escalated?
- Who executes?
- Who criticizes, verifies, or judges results?
- How are cost, quality, latency, risk, and decisions observed?
- How are agents created, configured, authorized, versioned, and retired?
- What does the organization learn from execution?
- How does learned knowledge influence later behavior?
- How does the Organizational Digital Twin remain connected to real execution?

The architecture should outlive individual model providers, orchestration frameworks, protocols, and implementation fashions.

## Architectural position

```text
                    HUMAN / ORGANIZATION
          strategy · objectives · constraints · policy
                              │
                              ▼
                    BIONIC COMPANY / BIZOPS
                              │
                              ▼
                AGENTIC REFERENCE ARCHITECTURE
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
   CONTROL PLANE        RUNTIME PLANE       LEARNING PLANE
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
               Autonomous agentic domains
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    Cine Toaster          KDP Studio             Pulse
```

Domains remain autonomous. BC-ARA does not require current or future domains to share an internal implementation.

## 1. Agentic Control Plane

The control plane manages the agentic workforce and its authority envelope.

Responsibilities include:

- agent registry and identity;
- roles and capability descriptions;
- agent lifecycle;
- skills and tool entitlements;
- model availability and constraints;
- permissions and authority;
- policies and governance;
- workforce composition;
- creation, specialization, reassignment, and retirement;
- versions and configuration;
- FinOps and resource constraints;
- observability and audit;
- performance and quality history.

The **Agent HR** concept belongs here. It is more than a directory or UI: it is a human-facing view over the agent control plane.

The **Meta-Agent / Agent Workforce** capability also interacts with this plane when proposing or performing workforce adaptation.

## 2. Agentic Runtime Plane

The runtime plane is where intent becomes decisions and execution.

```text
Intent / Desired Outcome
          ↓
       Planning
          ↓
 Decision Intelligence
          ↓
 Delegation / Routing
          ↓
       Execution
          ↓
 Evaluation / Verification
          ↓
        Outcome
```

### Planning

Answers:

> What should be done?

Planning may include decomposition, sequencing, dependency reasoning, resource awareness, and capability selection.

### Decision Intelligence

Makes intermediate operational decisions such as:

```text
Which agent?       Which model?
Which tool?        Which skill?
Which knowledge?

Execute directly?  Delegate?
Ask a critic?      Escalate?
Request a human?

Continue?          Retry?
Change strategy?   Stop?
```

A decision may carry:

```text
confidence · uncertainty · risk · cost
evidence · policy constraints · expected utility
```

A general pattern is confidence- or uncertainty-aware routing:

```text
decision
   ↓
confidence / risk / policy
   ├── sufficient → execute
   ├── uncertain  → reason / consult / escalate
   └── prohibited → stop / request authority
```

BC-ARA defines the capability rather than prescribing a specific implementation.

### Execution

Workers and specialists perform domain work through tools, APIs, MCP servers, local capabilities, other agents, or domain-specific infrastructure.

### Evaluation and verification

Answers:

> Did the result satisfy the relevant criteria?

Evaluation may include deterministic tests, domain validators, model judges, critics, human review, quality gates, and outcome metrics.

Evaluation is distinct from execution even when implemented by the same model.

## Agent roles are responsibilities, not necessarily processes

```text
Planner
"What should we do?"

Router / Decision Layer
"Who or what should decide or act next?"

Worker
"Do the work."

Critic
"What may be wrong, weak, or missing?"

Judge / Evaluator
"Does the result meet the criteria?"

Learning Observer
"What can be learned from what happened?"

Knowledge Steward
"What should become governed knowledge,
for whom, and with what lifecycle?"
```

These do **not** imply seven permanently running agents. One model may perform multiple roles, deterministic software may perform some, and high-risk situations may deliberately separate them.

## 3. Learning Plane

The learning plane turns execution into durable improvement. **KnowEvolve** is the current project exploring this capability.

```text
Execution
    ↓
Experience
    ↓
Evaluation / Reflection
    ↓
Learning Candidate
    ↓
Evidence
    ↓
Validation
    ↓
Knowledge
    ↓
┌────────────┬────────────┬────────────────┐
│   Agent    │   Domain   │  Organization  │
│ Knowledge  │ Knowledge  │   Knowledge    │
└────────────┴────────────┴────────────────┘
    ↓
Future Behavior
    ↺
```

The Learning Observer and Knowledge Steward are different responsibilities:

- **Learning Observer / Critic:** observes executions and identifies candidate lessons.
- **Knowledge Steward:** governs evidence, duplication, contradiction, validation, promotion, rescoping, supersession, and deprecation.

Knowledge becoming valid is also distinct from knowledge gaining authority to change behavior.

## Cross-cutting concerns

### Observability

The organization should be able to reconstruct not only what agents did, but why important decisions were made.

Candidate signals include traces, plans, delegations, model/tool/skill selection, confidence, uncertainty, retrieved/applied knowledge, evaluation outcomes, latency, cost, failures, retries, human interventions, and policy decisions.

### FinOps

Cost is part of agentic decision-making, not merely accounting after execution. FinOps may inform model routing, resource selection, worker lifecycle, budget enforcement, cost/quality trade-offs, cold-start versus idle capacity, and initiative/domain attribution.

### Governance and security

Governance includes identity, permissions, authority envelopes, policy, risk, audit, secrets/tool access, human approval where required, and separation of knowledge from behavioral authority.

### Events and interoperability

Event-driven integration is a natural fit because organizational capabilities should remain loosely coupled.

Conceptual namespaces may include:

```text
intent.*       plan.*         decision.*
delegation.*   execution.*    evaluation.*
agent.*        knowledge.*    policy.*
cost.*         twin.*
```

These are not current API commitments.

## Organizational Digital Twin

The twin is not another agent-runtime component. It is a representation of organizational state and behavior informed by signals from the architecture.

```text
Control Plane ──┐
Runtime Plane ──┼──→ Organizational Digital Twin
Learning Plane ─┤             │
BizOps ─────────┘             ↓
                      observe / map / simulate
                              │
                              ↓
                     organizational decision
                              │
                              └────→ execution
```

The twin should progressively model actual flows, capabilities, temporary relationships, costs, dependencies, outcomes, and learned organizational behavior. Simulation remains decision support rather than prediction certainty.

## Relationship to BizOps

**BizOps** connects organizational direction, initiatives, capabilities, resources, risks, and outcomes.

**BC-ARA** describes the agentic machinery through which reasoning, decisions, execution, evaluation, governance, and learning can occur.

```text
Strategy
   ↓
BizOps
   ↓
Desired capability / outcome
   ↓
BC-ARA runtime + control + learning
   ↓
Autonomous domain
   ↓
Result + signals
   ↓
BizOps + Digital Twin
```

## Current ecosystem mapping

This table is an architectural audit, not a maturity claim.

| BC-ARA capability | Current direction | Status |
|---|---|---|
| Organizational direction | Bionic Company / BizOps | Defined and under validation |
| Initiatives & capability resolution | Bionic Company M0/M1 | Initial implementation exists |
| Agent workforce adaptation | Meta-Agent / Agent Workforce | Concept defined; M2 not started |
| Agent registry / HR | Agent HR concept | Conceptual |
| Planning / orchestration | Domain-specific + legacy AgentOS lessons | Partial / distributed |
| Decision Intelligence | Confidence, uncertainty, routing, escalation | **Newly explicit capability** |
| Execution | Autonomous domains and specialist agents | Existing direction |
| Evaluation / verification | Domain validators, critics, quality gates | Partial; common model needed |
| Observability | Analytics, traces, operational signals | Partial / distributed |
| FinOps | FinOps capabilities and domain cost concerns | Defined direction |
| Knowledge evolution | KnowEvolve | Separate project; early research |
| Organizational knowledge | KnowEvolve + Bionic Company | Conceptual |
| Digital Twin — observe/map | Bionic Company | M0 implemented |
| Digital Twin — simulation | Bionic Company | M3 not started |
| Governance / authority | Bionic Company authority envelope | Initial implementation exists |

## Architectural gaps worth investigating

### Decision Intelligence

Planning and execution already exist conceptually, but confidence-aware routing, escalation, stopping, retrying, model selection, and tool selection should become explicit concerns.

### Evaluation model

Domains naturally evaluate their own work, but BC-ARA needs a clear model relating critic, judge, deterministic validator, human review, and organizational quality signals.

### Agent Control Plane

Agent HR, Meta-Agent, permissions, configuration, versions, skills, model access, performance, and lifecycle should converge into a coherent control-plane model.

### Cross-plane observability

A trace should eventually connect:

```text
organizational intent
 → plan
 → decision
 → delegation
 → execution
 → evaluation
 → cost
 → learning
 → knowledge application
 → outcome
```

### Learning-to-twin feedback

KnowEvolve and the Organizational Digital Twin should complement rather than duplicate each other:

- the twin asks **how the organization behaves and what may happen**;
- KnowEvolve asks **what the organization has learned and how strongly it knows it**.

Their future feedback loop needs explicit design.

## How to use BC-ARA

When encountering a new agent architecture, paper, product, or implementation pattern, ask:

1. Which BC-ARA responsibility does this represent?
2. Do we already have that responsibility explicitly modeled?
3. Is it implemented in the correct plane?
4. Is it reusable organizational infrastructure or a domain-specific concern?
5. Does it expose a missing decision, evaluation, governance, observability, or learning mechanism?
6. Should BC-ARA change, or is this merely one implementation of an existing capability?

This makes BC-ARA a living architectural audit tool rather than a static diagram.

## Technology independence

BC-ARA does not prescribe LangGraph, AG-UI, MCP, A2A, a particular model provider, memory system, or database.

> **Frameworks implement the architecture. They do not define it.**

## Evolution

BC-ARA should evolve from evidence produced by the Bionic Company validation environment. It is intentionally a **reference hypothesis**. New patterns should be tested against Cine Toaster, KDP Studio, Pulse, KnowEvolve, and future domains before being treated as universal organizational requirements.
