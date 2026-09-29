# OrchestrAI Backend — Architecture & Implementation Plan

**Version:** 0.1.0  
**Last Updated:** 2026-09-25  
**Purpose:** AI-driven workflow orchestration platform for finance and enterprise operations  

---

## 1. Project Overview

OrchestrAI is a backend platform that converts natural language descriptions into executable, auditable workflow automations. It is designed primarily for finance-domain workflows (invoice processing, payment approvals, employee onboarding, customer support escalation) but built as a universal engine.

### Core Value Proposition
- **Natural Language to Automation:** Users describe a workflow in plain English; an AI agent (Claude) generates a structured, validated workflow graph.
- **Human-in-the-Loop:** Critical decision points (approvals, thresholds) pause execution and surface to human operators.
- **Observable Execution:** Every step is recorded with timestamps, inputs, outputs, and status — enabling full audit trails.
- **Extensible Tools:** New capabilities are registered as tools in a controlled registry; the LLM can only invoke registered tools.

### Current State
- Fully functional MVP with 3 example workflows
- 11 registered mock tools
- LangGraph-based execution engine
- SQLite persistence with SQLAlchemy ORM
- 8 pytest test files covering planner, compiler, runner, tools, verifier, approval, API, and schemas

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                    (Port 3000, CORS-enabled)                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/REST (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                           │
│                    D:\claude_code\OrchestrAI\backend\app\main.py │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ /health      │  │ /workflows   │  │ /approvals            │  │
│  │ GET          │  │ GET/POST     │  │ GET/POST/{id}/approve │  │
│  └──────────────┘  │ POST /run    │  │ POST/{id}/reject      │  │
│                     └──────────────┘  └───────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                              │
│  │ /runs        │  │ /tools       │                              │
│  │ GET/{id}     │  │ GET          │                              │
│  │ POST/{id}/cancel│ │ GET/{name}  │                              │
│  │ GET          │  │              │                              │
│  └──────────────┘  └──────────────┘                              │
│        │                  │                                        │
│        ▼                  ▼                                        │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    API Route Handlers                         │ │
│  │  app/api/workflows.py | runs.py | approvals.py | tools.py    │ │
│  └──────────────┬──────────────┬──────────────┬─────────────────┘ │
│                 │              │              │                     │
└─────────────────┼──────────────┼──────────────┼───────────────────┘
                  │              │              │
         ┌────────▼──────┐  ┌───▼──────┐  ┌───▼──────────┐
         │  PlannerAgent │  │ Runner  │  │ ApprovalSvc  │
         │  (planner.py) │  │ (runner)│  │ (service.py) │
         └───────┬───────┘  └────┬────┘  └──────┬───────┘
                 │               │               │
         ┌───────▼───────┐  ┌────▼──────────────▼───────┐
         │  Compiler     │  │  ToolRegistry            │
         │  (compiler.py)│  │  (registry.py)           │
         └───────┬───────┘  └────┬──────────────────────┘
                 │               │
         ┌───────▼───────────────▼───────┐
         │   LangGraph StateGraph        │
         │   (Execution Engine)           │
         └───────────────┬───────────────┘
                         │ executes tools
                         ▼
         ┌───────────────────────────────┐
         │  Tool Implementations         │
         │  (implementations.py)         │
         │  send_email, search_database, │
         │  process_payment, etc.        │
         └───────────────┬───────────────┘
                         │ persists
                         ▼
         ┌───────────────────────────────┐
         │  SQLAlchemy ORM               │
         │  (models/__init__.py)         │
         │                               │
         │  WorkflowModel                │
         │  WorkflowExecutionModel       │
         │  StepExecutionModel           │
         │  ApprovalRequestModel         │
         └───────────────┬───────────────┘
                         │ via engine
                         ▼
         ┌───────────────────────────────┐
         │  SQLite Database              │
         │  (orchestr_ai.db)             │
         └───────────────────────────────┘
```

### Data Flow Summary

```
User Prompt
    │
    ▼
[PlannerAgent] ──► Claude API ──► JSON Workflow Definition
    │                                          │
    │         validate (Pydantic + tool refs)   │
    │                                          │
    ▼                                          ▼
[Persist] ◄── WorkflowModel ──► Database
    │
    │  POST /workflows/{id}/run
    ▼
[WorkflowRunner]
    │
    ├─► Load workflow from DB
    ├─► Parse into Workflow schema
    ├─► [Compiler] ──► LangGraph StateGraph
    │                         │
    │                 ainvoke(initial_state)
    │                         │
    │         ┌───────────────┼───────────────┐
    │         ▼               ▼               ▼
    │    [trigger]      [action]       [condition]
    │         │               │               │
    │         │          ToolRegistry.execute()
    │         │               │
    │         │          ToolResult
    │         │               │
    │         │          [Verifier] ──► SUCCESS/RETRY/ESCALATE/FAIL
    │         │               │
    │         │          store result in context
    │         │               │
    │         │          [approval?] ──► WAITING_APPROVAL
    │         │               │
    │         ▼               ▼               ▼
    │    [wait]        [end] ────────► Execution Complete
    │
    ▼
[Persist Execution + Steps] ──► Database
    │
    ▼
API Response with execution details
```

---

## 3. Module Breakdown

### 3.1 `app/main.py` — Application Entry Point

**Path:** `D:\claude_code\OrchestrAI\backend\app\main.py`

The FastAPI application factory with lifespan management.

**Key elements:**
- `lifespan()` — async context manager that creates DB tables on startup via `Base.metadata.create_all()`
- `health_router` — standalone health check at `/api/health`
- CORS middleware configured from `settings.cors_origins` (comma-separated)
- Five feature routers mounted at `/api` prefix: workflows, runs, approvals, tools

**Design note:** Tables are created at startup via raw SQLAlchemy rather than Alembic migrations. This is acceptable for MVP but should transition to migrations for production.

---

### 3.2 `app/config.py` — Configuration

**Path:** `D:\claude_code\OrchestrAI\backend\app\config.py`

Pydantic Settings-based configuration loaded from environment variables.

| Setting | Default | Purpose |
|---------|---------|---------|
| `app_name` | "OrchestrAI" | Application name |
| `api_prefix` | "/api" | URL prefix for all routes |
| `cors_origins` | "http://localhost:3000" | Comma-separated allowed origins |
| `database_url` | "sqlite:///./orchestr_ai.db" | SQLAlchemy database URL |
| `anthropic_api_key` | "" | Claude API key |
| `anthropic_model` | "claude-sonnet-4-20250514" | LLM model identifier |
| `planner_max_retries` | 3 | Max retries for plan generation |
| `planner_temperature` | 0.0 | Deterministic planning |
| `default_tool_timeout` | 30 | Seconds per tool execution |
| `max_retry_attempts` | 3 | Retry limit for failed tools |
| `retry_backoff_base` | 1.0 | Base for exponential backoff |
| `approval_timeout_hours` | 48 | Auto-escalation timeout |

---

### 3.3 `app/database.py` — Database Layer

**Path:** `D:\claude_code\OrchestrAI\backend\app\database.py`

SQLAlchemy setup with two session providers:

- **`engine`** — `create_engine()` with `check_same_thread=False` for SQLite threading
- **`SessionLocal`** — sessionmaker factory (no autocommit, no autoflush)
- **`Base`** — declarative base class
- **`get_db()`** — FastAPI dependency that yields a session and closes it
- **`get_db_context()`** — Context manager for non-FastAPI usage (runner, approval service)

**Design pattern:** Dependency injection via FastAPI's `Depends()`.

---

### 3.4 `app/schemas/` — Pydantic Models

Three schema files defining the data contracts:

#### `workflow.py` — Workflow Definition Schema
- **`NodeType`** enum: trigger, action, condition, approval, wait, end
- **`PermissionLevel`** enum: AUTO, CONFIRM, HUMAN_ONLY
- **`TriggerType`** enum: MANUAL, WEBHOOK, SCHEDULE
- **Node models:** `TriggerNode`, `ActionNode`, `ConditionNode`, `ApprovalNode`, `WaitNode`, `EndNode`
- **`Edge`** model — connects nodes with optional condition ("true"/"false")
- **`Workflow`** — top-level model with validators for:
  - At least one node
  - No duplicate node IDs
  - All edge references resolve to existing nodes
  - Exactly one trigger node
- **`workflow_to_dict()` / `workflow_from_dict()`** — serialization helpers

#### `execution.py` — Execution State Schema
- **`ExecutionStatus`** enum: pending, running, waiting_approval, retrying, completed, failed, cancelled
- **`StepStatus`** enum: pending, running, completed, failed, waiting_approval, skipped
- **`StepExecution`** — records a single node execution (id, node_id, tool_name, inputs, result, timestamps, error)
- **`WorkflowExecution`** — full execution record (id, workflow_id, status, context, steps list, error info)

#### `tool.py` — Tool Schema
- **`Tool`** — tool definition (name, description, input_schema JSON, permission, timeout, retryable, metadata)
- **`ToolCall`** — request to execute a tool (tool_name + inputs)
- **`ToolResult`** — result from execution (success, output dict, error, retryable, warnings)

---

### 3.5 `app/models/` — SQLAlchemy ORM

**Path:** `D:\claude_code\OrchestrAI\backend\app\models\__init__.py`

Four ORM models with relationships:

| Model | Table | Key Fields | Relationships |
|-------|-------|------------|---------------|
| `WorkflowModel` | `workflows` | id, name, description, nodes (JSON), edges (JSON), wf_metadata (JSON), timestamps | One-to-many → `WorkflowExecutionModel` |
| `WorkflowExecutionModel` | `workflow_executions` | id, workflow_id (FK), workflow_name, status (enum), current_node_id, context (JSON), error info, timestamps | Many-to-one ← `WorkflowModel`; One-to-many → `StepExecutionModel`; One-to-one → `ApprovalRequestModel` |
| `StepExecutionModel` | `step_executions` | id, execution_id (FK), node_id, node_type, node_name, status (enum), tool_name, tool_inputs (JSON), tool_result (JSON), attempt_count, error, timestamps | Many-to-one ← `WorkflowExecutionModel` |
| `ApprovalRequestModel` | `approval_requests` | id, execution_id (FK), node_id, reason, context (JSON), approver_role, status (string), approver_id, timestamps | Many-to-one ← `WorkflowExecutionModel` |

**UUID generation:** All IDs use `gen_id()` which calls `str(uuid.uuid4())`. The workflow ID prefix is `wf_`, execution is `exec_`, step is auto-generated, approval is `approval_`.

**Cascade deletes:** Executions cascade-delete their steps and approval. Workflows cascade-delete their executions.

---

### 3.6 `app/agents/` — AI Agents

Three specialized agents form the planning-to-execution pipeline:

#### `planner.py` — PlannerAgent

**Purpose:** Converts natural language prompts into validated `Workflow` objects.

**Pipeline:**
1. Formats available tool list into the system prompt
2. Sends prompt to Claude API with structured JSON schema instructions
3. Extracts JSON from response (handles code fences and raw JSON)
4. Validates tool references exist in the registry
5. Validates with Pydantic `Workflow` schema
6. Retries up to `max_retries` with repair prompts on failure

**Key classes:**
- `PlanningError` — exception when planning exhausts retries
- `PlanningResult` — result wrapper with `success`, `workflow`, `error`, `raw_response`
- `PlannerAgent` — main class with `plan(prompt)` and `get_planning_metadata(workflow)`

**Metadata extraction:** Returns node count, node types, tools used, approval gate count, branching flag, retry flag, and complexity rating.

#### `compiler.py` — WorkflowCompiler

**Purpose:** Converts a validated `Workflow` into an executable LangGraph `StateGraph`.

**Process:**
1. Validates trigger node count (exactly one)
2. Builds node lookup and edge maps
3. Creates `StateGraph(dict)` — state is a plain dict
4. For each node, creates an async executor function via `_make_node_executor()`
5. Sets entry point to the trigger node
6. Adds edges:
   - End nodes → `END`
   - Condition nodes → conditional edges based on `condition_result`
   - Sequential nodes → first non-conditional outgoing edge
7. Wraps in `CompiledWorkflow` with lazy compilation (`MemorySaver` checkpointer)

**Node executor behavior:**
- **trigger:** Pass-through, marks step COMPLETED
- **action:** Resolves `{{context_key}}` templates in inputs, executes tool via registry, stores result in context
- **condition:** Evaluates Python expression against context with `eval()`, sets `condition_result` to "true" or "false"
- **approval:** Special handling for `request_human_approval` tool — sets WAITING_APPROVAL status and creates `pending_approval` state
- **wait:** Sleeps (capped at 5 seconds for testing)
- **end:** Marks execution as COMPLETED

**Security note:** The `eval()` in condition nodes has `__builtins__` restricted to `{}`, but this is still a potential risk. Consider a safer expression evaluator.

#### `verifier.py` — VerifierAgent

**Purpose:** Evaluates tool execution results against expected outcomes.

**Verdicts:** SUCCESS, RETRY, ESCALATE, FAIL

**Dual-mode:**
1. **LLM mode:** Sends tool result to Claude with system prompt for nuanced judgment
2. **Rule-based fallback:** If no API key or LLM call fails:
   - Success + no warnings → SUCCESS
   - Success + warnings → ESCALATE
   - Failure + retryable → RETRY
   - Failure + non-retryable → FAIL

---

### 3.7 `app/engine/` — Execution Engine

#### `runner.py` — WorkflowRunner

**Purpose:** The execution orchestrator that manages the full workflow lifecycle.

**Key methods:**
- **`run(workflow_id, context)`** — Full execution:
  1. Loads workflow from DB
  2. Parses into `Workflow` schema
  3. Compiles via `WorkflowCompiler`
  4. Creates `WorkflowExecutionModel` record
  5. Invokes LangGraph with initial state
  6. Handles approval gate creation
  7. Returns `WorkflowExecution` Pydantic model

- **`resume(execution_id)`** — Resume after approval:
  1. Validates execution is in WAITING_APPROVAL
  2. Recompiles the workflow
  3. Reconstructs state from existing steps
  4. Starts from the node after the approval node
  5. Invokes the graph to completion

- **`cancel(execution_id)`** — Sets status to CANCELLED

- **`_to_pydantic()`** — Converts ORM models to Pydantic schemas

**Custom exceptions:** `WorkflowNotFoundError`, `RunnerError`

---

### 3.8 `app/tools/` — Tool System

#### `registry.py` — ToolRegistry

**Purpose:** Central, controlled registry of all executable tools.

**Design principles:**
- The LLM can ONLY invoke tools from this registry
- Registration is explicit — no dynamic discovery
- Duplicate registration raises `ToolAlreadyRegisteredError`
- Unknown tool execution raises `UnknownToolError`
- Singleton pattern: `registry = ToolRegistry()`

**11 registered tools:**
| Tool | Permission | Description |
|------|-----------|-------------|
| `send_email` | AUTO | Send email to recipient |
| `send_slack_message` | AUTO | Send Slack message to channel |
| `search_database` | AUTO | Query a database table |
| `update_database` | CONFIRM | Update a database record |
| `create_ticket` | AUTO | Create a support ticket |
| `create_calendar_event` | AUTO | Create a calendar event |
| `request_human_approval` | HUMAN_ONLY | Pause and request approval |
| `wait` | AUTO | Sleep for duration |
| `extract_invoice_data` | AUTO | Extract structured data from invoice |
| `validate_invoice` | AUTO | Validate invoice against rules |
| `process_payment` | CONFIRM | Process a payment |

#### `implementations.py` — Mock Tool Implementations

**Purpose:** In-memory mock implementations for development/testing.

All tools are async functions that accept `inputs: dict` and return `ToolResult`. They operate on in-memory data structures (`MOCK_EMAILS`, `MOCK_SLACK_MESSAGES`, `MOCK_DB_RECORDS`, etc.).

**Note:** These are mocks. A production system would replace these with real integrations (email APIs, database connections, payment processors, etc.).

---

### 3.9 `app/approval/` — Human-in-the-Loop

#### `service.py` — ApprovalService

**Purpose:** Manages the approval request lifecycle.

**Key methods:**
- `create_request()` — Creates pending approval with execution_id, node_id, reason, context, approver_role
- `get()` — Fetches by ID
- `list_pending()` — Lists all pending approvals
- `approve()` — Sets status to "approved", records approver_id and timestamps
- `reject()` — Sets status to "rejected", records approver_id, rejection_reason, timestamps

**Custom exceptions:** `ApprovalAlreadyResolvedError`, `ApprovalNotFoundError`

---

### 3.10 `app/api/` — REST API Routes

Four routers with the following endpoints:

#### Workflows (`/api/workflows`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/workflows/generate` | Generate workflow from natural language prompt |
| GET | `/workflows` | List all workflows |
| GET | `/workflows/{id}` | Get specific workflow |
| POST | `/workflows/{id}/run` | Execute a workflow |

#### Runs (`/api/runs`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/runs` | List recent executions (limit=50) |
| GET | `/runs/{id}` | Get execution details with all steps |
| POST | `/runs/{id}/cancel` | Cancel a running execution |

#### Approvals (`/api/approvals`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/approvals` | List all pending approvals |
| POST | `/approvals/{id}/approve` | Approve and resume workflow |
| POST | `/approvals/{id}/reject` | Reject and cancel workflow |

#### Tools (`/api/tools`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/tools` | List all registered tools |
| GET | `/tools/{name}` | Get specific tool details |

**Health:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

All routes use `get_db` dependency injection for database sessions.

---

## 4. Data Flow: Prompt to Execution

### Phase 1: Planning
```
User sends prompt → POST /api/workflows/generate
    │
    ▼
PlannerAgent.plan(prompt)
    │
    ├─► Fetches available tools from registry
    ├─► Builds system prompt with tool list + examples
    ├─► Calls Claude API (messages.create)
    │
    ├─► Extracts JSON from response
    ├─► Validates tool references
    ├─► Validates Pydantic schema
    │
    ├─► [RETRY LOOP if validation fails]
    │
    ▼
PlanningResult(workflow)
    │
    ▼
Persist as WorkflowModel (nodes as JSON, edges as JSON)
    │
    ▼
Return workflow ID + metadata to client
```

### Phase 2: Execution
```
User triggers → POST /api/workflows/{id}/run
    │
    ▼
WorkflowRunner.run(workflow_id, context)
    │
    ├─► Load WorkflowModel from DB
    ├─► Parse into Workflow Pydantic model
    ├─► WorkflowCompiler.compile(workflow)
    │       │
    │       ├─► Validate trigger node
    │       ├─► Build StateGraph
    │       ├─► Create node executors
    │       └─► Wire edges
    │
    ├─► Create WorkflowExecutionModel (status=RUNNING)
    │
    ▼
LangGraph.ainvoke(initial_state)
    │
    │   For each node:
    │   ├─► trigger: mark COMPLETED, proceed
    │   ├─► action: resolve templates, execute tool, store result in context
    │   │            [if request_human_approval → WAITING_APPROVAL]
    │   ├─► condition: eval(expression, context) → set condition_result
    │   ├─► wait: sleep
    │   └─► end: set status=COMPLETED
    │
    ▼
Update WorkflowExecutionModel with final state
    │
    ├─► If WAITING_APPROVAL → create ApprovalRequestModel
    │
    ▼
Return WorkflowExecution with all steps
```

### Phase 3: Approval & Resume
```
Human approves → POST /api/approvals/{id}/approve
    │
    ▼
ApprovalService.approve(id, approver_id)
    │
    ▼
WorkflowRunner.resume(execution_id)
    │
    ├─► Validate execution is WAITING_APPROVAL
    ├─► Recompile workflow
    ├─► Reconstruct state from existing steps
    ├─► Find next node after approval
    │
    ▼
LangGraph.ainvoke(resumed_state)
    │
    ▼
Complete remaining nodes → COMPLETED
```

---

## 5. Database Schema

```
┌─────────────────────────────┐
│        workflows            │
├─────────────────────────────┤
│ id                  STRING  │ PK
│ name                STRING  │ NOT NULL
│ description         TEXT    │ NULLABLE
│ nodes               JSON    │ NOT NULL (list of node dicts)
│ edges               JSON    │ NOT NULL (list of edge dicts)
│ wf_metadata         JSON    │ DEFAULT {}
│ created_at          DATETIME│ DEFAULT now()
│ updated_at          DATETIME│ DEFAULT now() ON UPDATE
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌──────────────────────────────────┐
│     workflow_executions          │
├──────────────────────────────────┤
│ id                     STRING   │ PK
│ workflow_id            STRING   │ FK → workflows.id
│ workflow_name          STRING   │ NOT NULL
│ status                 ENUM     │ DEFAULT pending
│ current_node_id        STRING   │ NULLABLE
│ context                JSON     │ DEFAULT {}
│ started_at             DATETIME │ NULLABLE
│ completed_at           DATETIME │ NULLABLE
│ error_message          TEXT     │ NULLABLE
│ error_details          JSON     │ NULLABLE
└──────────┬───────────────────────┘
           │ 1:N
           ▼
┌─────────────────────────────┐
│      step_executions        │
├─────────────────────────────┤
│ id                  STRING  │ PK
│ execution_id        STRING  │ FK → workflow_executions.id
│ node_id             STRING  │ NOT NULL
│ node_type           STRING  │ NOT NULL
│ node_name           STRING  │ NOT NULL
│ status              ENUM    │ DEFAULT pending
│ tool_name           STRING  │ NULLABLE
│ tool_inputs         JSON     │ NULLABLE
│ tool_result         JSON     │ NULLABLE
│ attempt_count       INTEGER │ DEFAULT 1
│ error               TEXT     │ NULLABLE
│ started_at          DATETIME │ NULLABLE
│ completed_at        DATETIME │ NULLABLE
│ created_at          DATETIME │ DEFAULT now()
└─────────────────────────────┘
           ▲ 1:1 (CASCADE)
           │
┌─────────────────────────────┐
│     approval_requests       │
├─────────────────────────────┤
│ id                  STRING  │ PK
│ execution_id        STRING  │ FK → workflow_executions.id
│ node_id             STRING  │ NOT NULL
│ reason              TEXT     │ NOT NULL
│ context             JSON     │ DEFAULT {}
│ approver_role       STRING  │ NULLABLE
│ status              STRING   │ DEFAULT "pending"
│ approver_id         STRING  │ NULLABLE
│ approved_at         DATETIME │ NULLABLE
│ rejection_reason    TEXT     │ NULLABLE
│ resolved_at         DATETIME │ NULLABLE
│ created_at          DATETIME │ DEFAULT now()
└─────────────────────────────┘
```

---

## 6. Key Design Patterns

### 6.1 Dependency Injection
- FastAPI's `Depends(get_db)` injects database sessions into route handlers
- `get_db()` yields a session and guarantees cleanup via `try/finally`
- `get_db_context()` provides the same for non-FastAPI consumers (runner, approval service)

### 6.2 Repository Pattern (Lightweight)
- ORM models are queried directly in API routes and the runner
- No separate repository layer yet — direct SQLAlchemy queries serve this role
- Would benefit from a formal repository layer as the domain grows

### 6.3 Singleton Pattern
- `ToolRegistry` uses a module-level singleton: `registry = ToolRegistry()`
- All imports reference this single instance
- This ensures consistent tool state across the application

### 6.4 Strategy Pattern
- Tools are registered strategies — each tool name maps to an async function
- `TOOL_IMPLEMENTATIONS` dict is the strategy registry
- The registry validates tool references before allowing execution

### 6.5 Retry with Repair Pattern
- `PlannerAgent.plan()` implements a retry loop with repair prompts
- On validation failure, the error details are fed back to Claude for correction
- Max retries configurable via `planner_max_retries` setting

### 6.6 State Machine
- `ExecutionStatus` and `StepStatus` enums define clear state transitions
- Runner transitions executions through: PENDING → RUNNING → (COMPLETED | FAILED | WAITING_APPROVAL | CANCELLED)
- Approval service transitions: pending → approved | rejected

### 6.7 Context Manager Pattern
- `get_db_context()` wraps session lifecycle for use outside FastAPI
- Used by `ApprovalService` when it needs a session without HTTP request context

---

## 7. API Reference

### Base URL
```
http://localhost:8000/api
```

### Health
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "service": "orchestr-ai",
  "version": "0.1.0"
}
```

### Workflows

**Generate Workflow**
```
POST /workflows/generate
Content-Type: application/json

{
  "prompt": "When an invoice arrives, extract the details..."
}
```
Response (201):
```json
{
  "id": "wf_abc12345",
  "name": "Invoice Processing",
  "description": "...",
  "nodes": [...],
  "edges": [...],
  "metadata": {
    "node_count": 7,
    "tools_used": ["extract_invoice_data"],
    "approval_gates": 1,
    "has_branching": true,
    "complexity": "medium"
  }
}
```
Errors: 422 if planning fails

**List Workflows**
```
GET /workflows
```
Response (200):
```json
[
  {
    "id": "wf_abc12345",
    "name": "Invoice Processing",
    "description": "...",
    "created_at": "2026-09-25T...",
    "metadata": {...}
  }
]
```

**Get Workflow**
```
GET /workflows/{workflow_id}
```
Response (200): Full workflow definition with nodes and edges  
Errors: 404 if not found

**Run Workflow**
```
POST /workflows/{workflow_id}/run
Content-Type: application/json

{
  "context": {"amount": 500000, "vendor": "TestCorp"}
}
```
Response (200):
```json
{
  "id": "exec_xyz789",
  "workflow_id": "wf_abc12345",
  "status": "waiting_approval",
  "current_node_id": "n5",
  "steps": [
    {
      "id": "...",
      "node_id": "n2",
      "node_name": "Extract Invoice Data",
      "node_type": "action",
      "status": "completed",
      "tool_name": "extract_invoice_data",
      "attempt_count": 1,
      "error": null
    }
  ]
}
```
Errors: 404 if workflow not found

### Runs

**Get Run**
```
GET /runs/{run_id}
```
Response (200): Full execution with all steps, context, error info, and approval status

**List Runs**
```
GET /runs?limit=50
```
Response (200): Array of execution summaries

**Cancel Run**
```
POST /runs/{run_id}/cancel
```
Response (200):
```json
{
  "id": "exec_xyz789",
  "status": "cancelled"
}
```

### Approvals

**List Pending Approvals**
```
GET /approvals
```
Response (200):
```json
[
  {
    "id": "approval_123",
    "execution_id": "exec_xyz",
    "node_id": "n5",
    "reason": "Invoice exceeds threshold",
    "context": {"amount": 500000},
    "approver_role": "manager",
    "status": "pending",
    "created_at": "..."
  }
]
```

**Approve**
```
POST /approvals/{approval_id}/approve
Content-Type: application/json

{
  "approver_id": "user_123"
}
```
Response (200): Approval record + resumed execution status

**Reject**
```
POST /approvals/{approval_id}/reject
Content-Type: application/json

{
  "approver_id": "user_123",
  "reason": "Too expensive"
}
```
Response (200):
```json
{
  "id": "approval_123",
  "status": "rejected",
  "rejection_reason": "Too expensive"
}
```

### Tools

**List Tools**
```
GET /tools
```
Response (200):
```json
[
  {
    "name": "send_email",
    "description": "Send an email to a recipient",
    "permission": "AUTO",
    "timeout_seconds": 30,
    "retryable": true,
    "input_schema": {...}
  }
]
```

**Get Tool**
```
GET /tools/{tool_name}
```
Response (200): Single tool definition  
Errors: 404 if not found

---

## 8. Configuration

### Environment Variables
Set in `.env` file (loaded via `python-dotenv`):

```env
# Required for LLM-based planning
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=sqlite:///./orchestr_ai.db

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000
```

### All Configurable Settings (via `app/config.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | "" | Required for AI planning and verification |
| `DATABASE_URL` | `sqlite:///./orchestr_ai.db` | SQLAlchemy database URL |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Claude model for planning/verification |
| `PLANNER_MAX_RETRIES` | 3 | Retry attempts for plan generation |
| `PLANNER_TEMPERATURE` | 0.0 | Planning determinism |
| `DEFAULT_TOOL_TIMEOUT` | 30 | Tool execution timeout (seconds) |
| `MAX_RETRY_ATTEMPTS` | 3 | Tool retry limit |
| `RETRY_BACKOFF_BASE` | 1.0 | Exponential backoff base |
| `APPROVAL_TIMEOUT_HOURS` | 48 | Approval auto-escalation (not yet implemented) |

### Database Configuration
- SQLite for development (file-based, zero config)
- Supports any SQLAlchemy-compatible URL (PostgreSQL, MySQL) via `DATABASE_URL`
- Thread-safe for SQLite via `check_same_thread=False`

---

## 9. Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "python -c 'from app.database import engine; from app.models import Base; Base.metadata.create_all(engine)' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

**Observations:**
- Creates tables at container startup (acceptable for simple deployments)
- Installs `gcc` and `libpq-dev` for PostgreSQL support, though currently uses SQLite
- Single-stage build (no multi-stage optimization)

### Direct Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production Recommendations
1. Replace SQLite with PostgreSQL
2. Add Alembic for migration management
3. Add a reverse proxy (nginx) for TLS termination
4. Add authentication/authorization middleware
5. Use multi-worker uvicorn with proper async handling
6. Add structured logging (structlog or similar)
7. Add health check with database connectivity check
8. Container orchestration (Docker Compose or Kubernetes)

---

## 10. Testing Strategy

### Test Framework
- **pytest** with **pytest-asyncio** for async test support
- Configuration in `pytest.ini`: `asyncio_mode = auto`

### Test Files

| File | Tests | Coverage Area |
|------|-------|---------------|
| `test_planner.py` | 8 | Planner agent: generation, repair, retries, metadata extraction, no-API-key fallback |
| `test_compiler.py` | 7 | Compiler: linear, branching, approval nodes, trigger validation, edge cases |
| `test_runner.py` | 9 | Runner: happy path, unknown workflow, approval pause/resume, rejection, cancel, multiple runs, context |
| `test_tools.py` | 14 | Registry: registration, permissions, tool execution, error cases |
| `test_verifier.py` | 7 | Verifier: rule-based verdicts, LLM mode with mocks, fallback |
| `test_approval.py` | 10 | Approval service: creation, approve/reject, double-resolve, queries, persistence |
| `test_api.py` | 11 | API endpoints: health, workflow CRUD, runs, approvals, tools |
| `test_schemas.py` | 11 | Schema validation: valid workflows, invalid inputs, status enums, ToolResult |

**Total: ~66 test cases**

### Testing Approach
- **Mock-based LLM tests:** Planner and Verifier tests use `unittest.mock` to mock Claude API calls
- **In-memory SQLite:** All DB tests use `sqlite:///:memory:` with session-scoped engine
- **Fixture reuse:** `conftest.py` provides reusable fixtures for DB sessions, tool registries, sample workflows
- **No integration tests with real API:** All LLM interactions are mocked

### Gaps in Coverage
- No tests for concurrent execution
- No tests for tool timeout handling
- No tests for the `eval()` in condition nodes (security concern)
- No load/performance tests
- No end-to-end tests with real database
- No authentication/authorization tests (not yet implemented)

---

## 11. Known Issues & TODOs

### Critical Issues

1. **`eval()` in condition nodes** (`compiler.py`, line 167)
   - Condition expressions are evaluated with Python's `eval()`
   - Even with `__builtins__` restricted to `{}`, this is a code injection risk
   - **Fix:** Replace with a safe expression parser (e.g., `simpleeval`, `asteval`, or a custom DSL)

2. **Table creation at startup** (`main.py`, line 25)
   - `Base.metadata.create_all()` runs on every startup
   - No migration tracking — schema changes are manual
   - **Fix:** Add Alembic for proper migration management

3. **No authentication/authorization**
   - All endpoints are public
   - No user identity, role checking, or API key validation
   - **Fix:** Add OAuth2/JWT middleware

### Moderate Issues

4. **In-memory mock tools** (`implementations.py`)
   - All tools are mocks with no real integrations
   - Data is lost between restarts
   - **Fix:** Abstract tool implementations behind interfaces; provide real implementations

5. **No tool timeout enforcement**
   - `default_tool_timeout` is configured but never enforced in `registry.execute()`
   - Long-running tools could hang execution
   - **Fix:** Wrap tool execution with `asyncio.wait_for()`

6. **No retry logic in runner**
   - `retry_count` and `retry_delay` are defined in `ActionNode` schema
   - But the runner/compiler never implements retry loops
   - **Fix:** Add retry logic in `_make_node_executor` for action nodes

7. **Context substitution is simplistic** (`compiler.py`, lines 95-102)
   - Only handles `{{key}}` pattern with exact key matches
   - No nested access (e.g., `{{data.amount}}`)
   - No default values or type coercion

8. **No approval timeout/escalation**
   - `approval_timeout_hours` is configured but never checked
   - Pending approvals could sit forever
   - **Fix:** Add a background task or cron job to check and escalate stale approvals

### Minor Issues

9. **Duplicate `uuid` import** in `compiler.py` (lines 4 and 13)

10. **Module-level imports in tests** (`test_runner.py`, line 155; `test_approval.py`, line 165)
    - Imports placed at the bottom of files to avoid circular imports
    - Should be refactored to proper import structure

11. **`to` parameter shadowing** (`workflows.py`, schema `Edge` model uses `from_`/`to`)
    - The `from` field is Python reserved word, handled correctly with alias
    - But serialization/deserialization is fragile

12. **No request validation beyond Pydantic**
    - `GenerateRequest` only requires `prompt` string
    - No length limits, sanitization, or rate limiting

13. **Missing `exceptions.py` module**
    - Listed in requirements but file doesn't exist
    - Custom exceptions are defined inline in individual modules

---

## 12. Future Roadmap

### Phase 2: Production Readiness
- [ ] Add Alembic migrations
- [ ] Implement authentication (OAuth2/JWT)
- [ ] Add request rate limiting
- [ ] Replace `eval()` with safe expression parser
- [ ] Enforce tool timeouts with `asyncio.wait_for()`
- [ ] Implement retry logic in runner
- [ ] Add structured logging (JSON logs)
- [ ] Add OpenAPI/Swagger documentation enhancements

### Phase 3: Enhanced AI Capabilities
- [ ] Streaming responses for plan generation
- [ ] Multi-turn conversation for workflow refinement
- [ ] Workflow suggestion from historical patterns
- [ ] Natural language execution status queries
- [ ] LLM-based condition expression generation
- [ ] Anomaly detection in execution patterns

### Phase 4: Scale & Observability
- [ ] Switch to PostgreSQL with connection pooling
- [ ] Add Redis for caching and pub/sub
- [ ] Implement workflow versioning
- [ ] Add execution replay capability
- [ ] Webhook notifications for execution events
- [ ] Dashboard with real-time execution visualization
- [ ] Multi-tenant support with tenant isolation

### Phase 5: Extensibility
- [ ] Plugin system for custom tools
- [ ] Workflow templates marketplace
- [ ] Integration connectors (Slack, email, databases, APIs)
- [ ] Visual workflow editor (frontend)
- [ ] Workflow import/export (JSON/YAML)
- [ ] A/B testing for workflow variants
- [ ] Cost tracking per workflow execution

### Phase 6: Enterprise Features
- [ ] Role-based access control (RBAC)
- [ ] Audit log with immutable records
- [ ] Compliance reporting (SOX, GDPR)
- [ ] SLA monitoring and alerting
- [ ] Multi-region deployment support
- [ ] SSO integration (SAML, Okta)

---

## Appendix: File Structure

```
D:\claude_code\OrchestrAI\backend\
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── Dockerfile                    # Container definition
├── README.md                     # Quick-start guide
├── pytest.ini                    # pytest configuration
├── requirements.txt              # Python dependencies
├── orchestr_ai.db                # SQLite database (development)
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory
│   ├── config.py                 # Pydantic Settings
│   ├── database.py               # SQLAlchemy engine & sessions
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py            # PlannerAgent (NL → Workflow)
│   │   ├── compiler.py           # WorkflowCompiler (Workflow → LangGraph)
│   │   └── verifier.py           # VerifierAgent (result evaluation)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── workflows.py          # /workflows endpoints
│   │   ├── runs.py               # /runs endpoints
│   │   ├── approvals.py          # /approvals endpoints
│   │   └── tools.py              # /tools endpoints
│   ├── approval/
│   │   ├── __init__.py
│   │   └── service.py            # ApprovalService (HITL)
│   ├── engine/
│   │   ├── __init__.py
│   │   └── runner.py             # WorkflowRunner (execution engine)
│   ├── models/
│   │   ├── __init__.py           # SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── workflow.py           # Workflow definition schema
│   │   ├── execution.py          # Execution state schema
│   │   └── tool.py               # Tool schema
│   └── tools/
│       ├── __init__.py
│       ├── registry.py           # ToolRegistry (tool management)
│       └── implementations.py    # Mock tool implementations
├── examples/
│   └── __init__.py               # Example workflow definitions
└── tests/
    ├── __init__.py
    ├── conftest.py               # Shared pytest fixtures
    ├── test_planner.py           # 8 tests
    ├── test_compiler.py          # 7 tests
    ├── test_runner.py            # 9 tests
    ├── test_tools.py             # 14 tests
    ├── test_verifier.py          # 7 tests
    ├── test_approval.py          # 10 tests
    ├── test_api.py               # 11 tests
    └── test_schemas.py           # 11 tests
```

---

*End of Architecture Document*
