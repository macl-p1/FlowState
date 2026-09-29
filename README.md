# OrchestrAI

**Describe a process in plain English. Let the agent build, execute, verify, and manage it.**

OrchestrAI is a Universal Workflow Agent platform. It converts natural language descriptions into executable, observable workflows with verification, retries, branching, and human approval gates.

## Architecture

```
User (Natural Language)
        │
        ▼
┌──────────────┐     ┌──────────────┐
│   Next.js    │────▶│   FastAPI    │
│  Glassmorphism│    │  Pydantic    │
│  React Flow  │     │  LangGraph   │
└──────────────┘     └──────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Planner  │  │ Compiler │  │  Runner  │
        │  Agent    │  │  Engine  │  │  Engine  │
        │  (Claude)│  │(LangGraph)│  │ (State)  │
        └──────────┘  └──────────┘  └────┬─────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                        ┌──────────┐ ┌──────────┐ ┌──────────┐
                        │   Tools  │ │ Verifier │ │Approval  │
                        │Registry  │ │ Agent    │ │   HITL   │
                        └──────────┘ └──────────┘ └──────────┘
```

### Agent Lifecycle

```
Natural Language → Planner Agent (Claude) → Validated Workflow JSON
    → Pydantic Validation → Compiler (LangGraph) → Execution Engine
    → Tool Execution → Verifier Agent
        ↙ Success         Failure
        ↓                  ↓
    Next Step         Retry / Escalate
                            ↓
                      Human Approval
                            ↓
                         Resume → Complete
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| Visual Workflow | React Flow |
| Backend | Python, FastAPI, Pydantic |
| Workflow Engine | LangGraph |
| AI | Anthropic Claude API |
| Database | SQLite / PostgreSQL |
| Testing | pytest, TestClient |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL)

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Run with Docker

```bash
# Start all services
docker compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/workflows/generate` | POST | Generate workflow from natural language |
| `/api/workflows` | GET | List all workflows |
| `/api/workflows/{id}` | GET | Get workflow details |
| `/api/workflows/{id}/run` | POST | Execute a workflow |
| `/api/runs/{id}` | GET | Get execution details |
| `/api/runs/{id}/cancel` | POST | Cancel execution |
| `/api/approvals` | GET | List pending approvals |
| `/api/approvals/{id}/approve` | POST | Approve and resume |
| `/api/approvals/{id}/reject` | POST | Reject and cancel |
| `/api/tools` | GET | List registered tools |

## Demo Workflows

### Invoice Processing
1. Invoice received → 2. Extract data → 3. Find PO → 4. Amount check → 5. Approval (if >$100K) → 6. Process payment → 7. Complete

### Employee Onboarding
1. Employee added → 2. Request documents → 3. Check completeness → 4. Notify HR / Send reminder → 5. Notify manager → 6. Complete

### Customer Complaint
1. Complaint received → 2. Identify customer → 3. Find order → 4. Check delivery → 5. Create ticket → 6. Check escalation → 7. Send response / Escalate → 8. Complete

## Engineering Rules

1. No arbitrary code execution by the LLM
2. No hard-coded workflow-specific engine logic
3. All workflows use the same universal schema
4. All tools go through ToolRegistry
5. All consequential actions have permissions
6. Every execution step is observable
7. Workflow state is persistent
8. Approval can pause and resume execution
9. LLM outputs are validated before execution
10. Failures are explicit, never silently ignored

## License

MIT
