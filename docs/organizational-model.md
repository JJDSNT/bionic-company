# Bionic Company — Initial Organizational Model

> Status: working theory / architectural draft.

## Purpose

Bionic Company is an experimental environment for representing, understanding and directing an agentic organization.

Its role is not to execute the internal work of every business domain. It connects organizational intent to autonomous domain execution and turns domain results back into organizational understanding.

A useful working definition is:

> **Bionic Company knows what the organization can do, what it wants to achieve, and how well it is performing — not how each domain does its work.**

The current architectural hypothesis is:

> **Bionic Company = Agentic BizOps + Organizational Twin.**

## Agentic BizOps

BizOps is the alignment layer between strategy and operation.

It may reason about:
- purpose, strategy and objectives;
- organizational priorities;
- initiatives and desired outcomes;
- policies and constraints;
- resources and budgets;
- cross-domain coordination;
- risks and organizational performance.

It should not prescribe domain workflows, prompts, tools, models or implementation steps.

The intended flow is:

```text
Strategy
   ↓
Objectives
   ↓
Initiatives
   ↓
Outcomes + Constraints
   ↓
Autonomous Domains
   ↓
Results + Status + Cost + Risk + Metrics
   ↓
Organizational Understanding
   ↓
Strategic / Tactical Decision
```

## Organizational Twin

The Organizational Twin is the living representation of the company used for observation, reasoning and simulation.

It may represent:
- business domains and business capabilities;
- active initiatives and their relationships;
- resources;
- organizational agents;
- financial and performance state;
- risks and dependencies;
- relevant external signals;
- historical decisions and outcomes.

Agents belonging to other domains may appear in the twin for visibility, topology, status and organizational understanding. Their presence in the twin does **not** imply that Bionic Company owns or directly orchestrates their internal work.

## Current Operating Domains

The first organizational model uses three autonomous operating domains:

### KDP Studio — Editorial

Owns editorial production and its domain workflows. Bionic Company may ask for an editorial outcome; KDP Studio decides how to achieve it.

### Cine Toaster — Audiovisual

Owns audiovisual production and its domain workflows. Bionic Company may ask for an audiovisual outcome; Cine Toaster decides how to achieve it.

### Pulse — Market & Relationships

Owns relationships, communication, audiences, communities, reputation and market intelligence. It provides an important interface between the organization and its external environment.

These applications remain independently useful products. Bionic Company is not intended to absorb their internal architectures.

## Boundary Principle

Bionic Company exchanges **organizational intent and organizational results** with domains.

Typical direction from Bionic Company to a domain may include:
- objective or initiative;
- desired outcome;
- priority;
- deadline;
- policy or constraint;
- budget/resource envelope.

Typical information returned by a domain may include:
- status;
- outcome progress;
- result;
- cost;
- risk/blocker;
- forecast;
- relevant KPI or event.

Internal domain details remain domain-owned:
- task decomposition;
- agent routing;
- prompts;
- technical capabilities;
- models and providers;
- tool invocation;
- retries;
- production workflows.

**Sharing infrastructure does not imply sharing domain responsibility.**

## Strategy, Tactics and Operations

The exact boundary between strategic and tactical responsibility is intentionally not frozen yet.

Current principle:
- Bionic Company owns strategic direction.
- Bionic Company may coordinate cross-domain tactical initiatives.
- Domain-local tactical planning and operational execution belong to the domains.
- Bionic Company should not become a universal task executor.

## Business Capabilities, Not Technical Capabilities

At the organizational level, Bionic Company needs a coarse business capability map.

Examples:
- Editorial Production → KDP Studio
- Audiovisual Production → Cine Toaster
- Market Intelligence & Relationships → Pulse

It does not need to know that a domain uses a particular renderer, model, API, file format or workflow node in order to delegate an outcome.

## Finance and Organizational Performance

The organization must eventually understand its economic state and what is producing results.

Finance is therefore expected to be a transversal organizational concern, but its final model is deliberately left open.

Potential organizational concepts include:
- revenue;
- expenses;
- cash;
- budgets;
- investment;
- return;
- forecasts;
- FinOps.

Domains may retain domain-specific commercial or cost information while exposing organizationally meaningful results upward.

## Interoperability

Bionic Company and the operating domains should remain loosely coupled.

Candidate mechanisms include:
- events;
- A2A;
- APIs;
- MCP/context interfaces where appropriate.

The architectural contract matters more than the transport protocol: domains expose outcomes and organizational signals without exposing their entire internal implementation.

## What Changes from the Original AgentOS Prototype

The original prototype explored a generic sequence:

```text
Goal → Planner Agent → Action → Executor Agent
```

That prototype remains useful as an experiment, but it is no longer the intended core abstraction.

The new direction is closer to:

```text
Organizational Intent
        ↓
Agentic BizOps
        ↓
Initiatives / Outcomes / Constraints
        ↓
Autonomous Business Domains
        ↓
Organizational Signals
        ↓
Organizational Twin
        ↓
Decision / Adaptation
```

LangGraph, AG-UI, A2A, MCP, simulation and agent technologies may still be valuable. Their role should be reassessed against this organizational model rather than treated as the product definition.

## Open Questions

This draft intentionally leaves several questions unresolved:

1. What is the minimum computational model for an organization, domain, capability, initiative and outcome?
2. Where exactly should the tactical boundary sit?
3. What financial information belongs in Bionic Company versus each domain?
4. What level of agent detail should appear in the Organizational Twin?
5. Which events and KPIs are organizationally meaningful?
6. How should cross-domain initiatives be coordinated without operational micromanagement?
7. Which interoperability mechanisms should be normative versus optional?
8. How should organizational simulation and scenario planning use the twin?
9. How should human governance and approval be represented?
10. Which concepts from the original AgentOS prototype should be retained, adapted or retired?

## Near-Term Architectural Direction

Before expanding implementation, the repository should:

1. Treat this organizational model as the conceptual source of truth.
2. Reframe the README around Bionic Company rather than a generic AgentOS.
3. Preserve the existing prototype while marking its planner/executor model as exploratory.
4. Define the smallest domain-facing contracts for intent and results.
5. Prototype the Organizational Twin around the real ecosystem: KDP Studio, Cine Toaster and Pulse.
6. Let real cross-domain use cases drive subsequent abstractions.
