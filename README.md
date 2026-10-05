# Bionic Company

**An experimental environment for representing, understanding and directing an agentic organization.**

Bionic Company is evolving from the original **AgentOS** experiment into an organizational layer that connects strategy with autonomous business domains.

The current working hypothesis is:

> **Bionic Company = Agentic BizOps + Organizational Twin + Organizational Adaptation.**

It should know what the organization can do, what it wants to achieve, what is happening across its domains, and how well it is performing — **without needing to know how each domain performs its internal work**.

> This repository is currently being reoriented. The existing planner/executor implementation is preserved as an early prototype and should not be read as the final architecture.

## The organizational model

```text
                         BIONIC COMPANY
              BizOps + Twin + Adaptation
                              │
              Strategy / Objectives / State
                              │
             Outcomes / Constraints / Signals
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
          KDP Studio      Cine Toaster       Pulse
           Editorial       Audiovisual      Market &
                                          Relationships
```

The three operating domains remain autonomous applications. Bionic Company coordinates at the organizational level rather than absorbing their internal agents and workflows.

### KDP Studio

Editorial production. Bionic Company may request an editorial outcome; KDP Studio owns how that outcome is produced.

### Cine Toaster

Audiovisual production. Bionic Company may request an audiovisual outcome; Cine Toaster owns its production workflow.

### Pulse

Market intelligence, audiences, relationships, communication, communities and reputation. Pulse represents an important interface between the organization and its external environment.

## Agentic BizOps

BizOps is the bridge between strategy and operation.

Bionic Company may work with:
- strategy and objectives;
- initiatives and desired outcomes;
- priorities;
- policies and constraints;
- resources and budgets;
- cross-domain coordination;
- risks;
- organizational performance.

It should not prescribe prompts, tools, models, task graphs or production steps inside a domain.

```text
Strategy
   ↓
Objectives
   ↓
Initiatives
   ↓
Outcomes + Constraints
   ↓
Domain Execution
   ↓
Results + Cost + Risk + Metrics
   ↓
Organizational Understanding
   ↺
```

## Organizational Twin

The Organizational Twin is intended to become a living representation of the company.

It may show domains, business capabilities, initiatives, resources, agents, dependencies, financial/performance state and relevant external signals.

Agents from KDP Studio, Cine Toaster and Pulse may be visible in the twin for organizational understanding. Visibility does **not** imply that Bionic Company directly controls their operational work.

## Organizational Adaptation

Bionic Company is intended to be more than a static set of predefined agents. The organization should be able to identify capability gaps, adapt its agentic workforce and sustain the platform that enables it.

Two mechanisms are currently distinguished:

- **Meta-Agent / Agent Workforce** — concerned with creating, configuring, evaluating, adapting and retiring organizational agents when new capabilities are needed.
- **Development / DevOps / SRE** — concerned with maintaining and evolving the Bionic Company platform itself: code, releases, infrastructure, observability, reliability and incidents.

These are related but different forms of evolution. The Meta-Agent changes the organization's agentic capacity; Dev/DevOps/SRE sustain the technical system on which that capacity runs.

Operating domains may have their **own** equivalent mechanisms. For example, a Cine Toaster SRE agent belongs to Cine Toaster and understands its infrastructure and production environment. Bionic Company may observe organizational signals such as reliability, cost or capability gaps without micromanaging how the domain responds.

> **Self-maintaining domains; self-evolving organization.**

This adaptation is expected to be governed. Agent creation or removal does not imply unrestricted autonomous self-modification; human approval, policies, security and cost constraints may apply.

## Architectural boundary

Bionic Company deals primarily in **organizational intent and organizational results**.

A domain may receive an objective, desired outcome, priority, deadline, policy or resource envelope. It may return status, progress, results, cost, risks, forecasts and relevant KPIs.

Task decomposition, agent routing, prompts, tools, providers and production workflows remain inside the domain.

> **Sharing infrastructure does not imply sharing domain responsibility.**

## Technology

The original AgentOS prototype explored:
- LangChain;
- LangGraph;
- Ollama;
- FastAPI;
- AG-UI;
- MCP;
- A2A;
- digital twins;
- simulation.

These technologies remain candidates, but they are now subordinate to the organizational architecture. The product is not defined by a specific agent framework or protocol.

## Current prototype

The code currently implements an early experimental flow:

```text
Goal → Planner Agent → First Action → Executor Agent
```

The planner creates a digital-transformation plan and the executor describes how an action could be performed. This code is being kept as historical/prototyping material while the new architecture is defined.

Current implementation areas include:

```text
agents/
  planner_agent.py
  executor_agent.py

langgraph/
  digital_plan_graph.py

app/
  api.py
  agui/

main.py
```

Do not interpret this flow as the target operating model of Bionic Company.

## Architectural draft

The first working theory is documented in:

**[docs/organizational-model.md](docs/organizational-model.md)**

It describes:
- Agentic BizOps;
- the Organizational Twin;
- organizational adaptation and the Agent Workforce;
- Meta-Agent, Development, DevOps and SRE responsibilities;
- recursive domain autonomy;
- autonomous business domains;
- the strategy-to-operation boundary;
- coarse business capabilities;
- finance and organizational performance as an open design area;
- interoperability;
- open architectural questions.

## Near-term direction

The immediate goal is not to add more agents. It is to establish the smallest useful organizational model and validate it against real cross-domain scenarios involving KDP Studio, Cine Toaster and Pulse.

Likely next steps are:
1. define minimal organizational entities and contracts;
2. model the three real domains in the twin;
3. define intent/result exchanges between Bionic Company and domains;
4. revisit the planner/executor prototype against those contracts;
5. model organizational capability gaps and governed adaptation;
6. let real organizational use cases drive additional capabilities.

## Status

**Early architectural reorientation / working theory.**

The project intentionally keeps several questions open, including finance, tactical boundaries, organizational KPIs, agent visibility, event contracts and simulation.

## Author

Jaime José Dias da Silva Neto
