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
