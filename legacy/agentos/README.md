# AgentOS prototype (legacy)

The project's first experiment: a planner agent proposes a digital-transformation plan, the first action is extracted, and an executor agent describes how to carry it out (LangChain, LangGraph, Ollama, AG-UI over FastAPI).

```text
Goal → Planner Agent → First Action → Executor Agent
```

It is preserved as history. Bionic Company moved the abstraction upward, from a generic planner/executor to an organization that observes and directs autonomous domains (see the repository README). Nothing in `bionic/` depends on this code.

To run it, from this directory:

```bash
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Ollama model and URL
python main.py                # planner → executor in the terminal
uvicorn app.api:app           # the same graph over AG-UI
```
