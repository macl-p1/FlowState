# OrchestrAI — AI Workflow Automation Platform

A universal agentic workflow automation platform where users describe processes in natural language, and the system converts them into executable, observable workflows.

## What This Is

**OrchestrAI** (working product name: **FlowPilot**) lets users:
- Describe business processes in natural language
- Auto-generate executable workflow graphs
- Run workflows through a controlled tool registry
- Verify results with an AI verifier agent
- Handle retries, branching, and failures
- Pause for human approval when needed

## Current State

- Backend: Full FastAPI + LangGraph engine with schema, tools, planner, compiler, runner, verifier, and approval system
- Frontend: Next.js glassmorphism UI with dashboard, workflow builder, execution console, templates, and tools explorer
- Tests: Comprehensive test suite covering schemas, tools, planner, compiler, runner, verifier, approvals, and API endpoints
- Documentation: Detailed test cases file (`testcases.md`) with 60+ test scenarios

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
D:\claude_code\OrchestrAI\
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry
│   │   ├── config.py            # Settings
│   │   ├── database.py          # SQLAlchemy
│   │   ├── schemas/             # Pydantic models
│   │   ├── models/              # ORM models
│   │   ├── tools/               # Tool registry + implementations
│   │   ├── agents/              # Planner, Compiler, Verifier
│   │   ├── engine/              # WorkflowRunner
│   │   ├── approval/            # Human-in-the-loop
│   │   └── api/                 # REST endpoints
│   ├── tests/                   # pytest suite
│   ├── examples/                # Demo workflow JSON
│   └── requirements.txt
├── frontend/
│   ├── src/app/                 # Next.js pages
│   ├── src/components/ui/       # Glassmorphism components
│   ├── src/lib/                 # API client
│   └── package.json
├── docker-compose.yml
├── README.md
└── testcases.md                 # 60+ test scenarios
```

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
