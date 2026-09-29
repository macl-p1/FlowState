# OrchestrAI — Plan & Vision

## The Core Idea

OrchestrAI (product name: **FlowPilot**) is an AI-native workflow automation platform.
Users describe business processes in plain English, and the system converts them into
executable, observable workflow graphs — then runs them through a controlled tool registry
with human-in-the-loop approval gates.

It is **not** a chatbot. It is **not** an RAG wrapper. It is a workflow engine where
an LLM acts as the planner, not the executor.

---

## How It Works

```
Natural Language Prompt
        │
        ▼
  ┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
  │  PLANNER    │────▶│  COMPILER    │────▶│  WORKFLOW RUNNER │
  │  (LLM)      │     │  (Validator) │     │  (Executor)      │
  └─────────────┘     └──────────────┘     └──────────────────┘
        │                     │                       │
        │  1. Converts prompt  │  2. Validates graph   │  3. Executes node
        │     into a graph of  │     structure, checks │     by node through
        │     nodes (trigger,  │     for cycles,       │     the tool registry
        │     action, condition,│     missing edges    │
        │     approval, end)   │                       │
        │                      │                       │
        │   Nodes reference    │                       │
        │   only registered    │                       │
        │   tools — no         │                       │
        │   arbitrary code     │                       │
        ▼                      ▼                       ▼
  ┌─────────────────────────────────────────────────────────┐
  │                   TOOL REGISTRY                         │
  │  Whitelist of 45 executable tools. The LLM can ONLY     │
  │  call tools from this list. No shell exec, no imports,  │
  │  no arbitrary code. Every tool has a permission level:  │
  │  AUTO (runs silently) / CONFIRM (asks before running)  │
  │  / HUMAN_ONLY (requires a human to trigger it).         │
  └─────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────┐
  │                    APPROVAL GATE                        │
  │  When a node hits a condition like "amount > $100k",    │
  │  the workflow PAUSES. A human sees the request, reviews  │
  │  the context, and clicks Approve or Reject.             │
  │  On Approve → runner resumes from the next node.        │
  │  On Reject  → execution is cancelled.                   │
  └─────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────┐
  │                   STEP PERSISTENCE                      │
  │  Every node execution is recorded with:                 │
  │  - started_at, completed_at timestamps                  │
  │  - tool inputs and outputs                              │
  │  - attempt count (for retries)                          │
  │  - error messages (for failures)                        │
  │  This gives full observability into every run.           │
  └─────────────────────────────────────────────────────────┘
```

### Step by step

1. **Describe** — User types a natural language prompt: *"When an invoice arrives, extract the details, validate it, and request manager approval if the amount exceeds $100k. If approved, process the payment."*

2. **Plan** — The Planner agent (powered by an LLM, with the tool registry as context) converts the prompt into a structured workflow graph: nodes (trigger, action, condition, approval, end) connected by edges.

3. **Compile** — The Compiler validates the graph: checks for cycles, orphaned nodes, missing trigger, duplicate IDs. Returns a compiled, executable workflow.

4. **Run** — The WorkflowRunner executes the graph node by node:
   - **Action nodes** resolve template variables, execute the corresponding tool from the registry, record the step.
   - **Condition nodes** evaluate expressions against the execution context and follow the matching branch.
   - **Approval nodes** pause execution, create an approval request in the database, and wait for a human decision.
   - **End nodes** mark the execution as completed.

5. **Verify** — After each tool execution, the Verifier agent checks the result: did it succeed? Should it retry? Should it escalate?

6. **Approve** — A human reviews the approval request with full context (the data, the reason, the workflow state) and decides. Approve resumes execution. Reject cancels it.

7. **Observe** — Every step is persisted. Users can view the full execution timeline, drill into individual steps, see inputs/outputs, timestamps, and errors.

---

## What Makes It Novel

### 1. Tool Registry as the Security Boundary

Most "AI automation" platforms let the LLM call arbitrary APIs or execute code. OrchestrAI is
**security-first by design**: the LLM can only call tools from a registered, validated whitelist.
No shell access, no arbitrary imports, no hidden side effects. This is the same principle as
function calling with a controlled schema — but applied to the entire workflow layer.

### 2. Human-in-the-Loop as a First-Class Node Type

Approval isn't bolted on as an afterthought. It is a **node type** (`approval`) in the workflow
graph, placed by the planner at exactly the right point. The runner knows how to pause, the API
exposes pending approvals, and the frontend renders an approve/reject UI — all wired together
as a single, coherent pattern.

### 3. The Same Engine Runs Everything

Invoice processing, employee onboarding, customer complaints — all run through the same
`WorkflowRunner`. The engine doesn't know about invoices or employees; it just knows about
nodes, edges, tools, and approvals. This universality means adding a new workflow type is
just a new prompt, not new infrastructure.

### 4. Full Step-Level Observability

Every execution step is recorded with:
- Timestamps (started, completed)
- Tool inputs and raw outputs
- Attempt count (for retried steps)
- Error messages (for failed steps)
- Node ID, node type, node name

This isn't just logging — it's structured, queryable, and displayed in the UI as a live
execution timeline. Users can see exactly where a workflow stopped, why, and what to do.

### 5. Natural Language as the Primary Interface

No drag-and-drop builder required (though one could be added later). Users describe what they
want in plain English. The LLM does the structural work of turning prose into a graph. This
lowers the barrier to entry dramatically while keeping the output structured and executable.

### 6. Retry, Verify, Escalate — Built In

Every tool execution goes through a verification step. If a tool fails:
- **Retryable** → the runner retries up to `retry_count` times with `retry_delay`.
- **Non-retryable** → the workflow fails with a clear error message.
- **Verifier says ESCALATE** → the workflow pauses for human review.

This makes workflows resilient without the user having to code error handling.

---

## Architecture at a Glance

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Landing │     │  Create  │     │ Workflow │     │   Run    │
│  Page    │     │  Page    │     │  Detail  │     │ Console  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     └────────────────┴────────────────┴────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   FastAPI API    │
              │  /api/workflows  │──▶ POST /generate  (NL → workflow)
              │  /api/workflows  │──▶ GET  /          (list)
              │  /api/workflows  │──▶ POST /{id}/run  (execute)
              │  /api/runs       │──▶ GET  /{id}      (poll status)
              │  /api/approvals  │──▶ GET /           (queue)
              │  /api/tools      │──▶ GET /           (registry)
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Workflow Engine  │
              │  Planner         │  LLM converts NL → graph
              │  Compiler        │  Validates structure
              │  Runner          │  Executes node by node
              │  Verifier        │  Checks tool results
              │  ApprovalService │  Human-in-the-loop
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Tool Registry   │
              │  45 registered   │
              │  tools (mock)    │
              │  AUTO/CONFIRM/   │
              │  HUMAN_ONLY      │
              └──────────────────┘
```

## Frontend Pages

| Page | Route | Purpose |
|------|-------|---------|
| Landing | `/` | Marketing page, CTA to get started |
| Dashboard | `/` (app) | Overview cards, recent activity, quick actions |
| Create | `/create` | Natural language prompt → generate workflow |
| Workflows | `/workflows` | List all saved workflows |
| Workflow Detail | `/workflows/[id]` | Visual graph, run button, run history |
| Run Console | `/run/[id]` | Live execution timeline, approve/reject |
| Approvals | `/approvals` | Approval queue across all workflows |
| Runs | `/runs` | Historical execution log, filterable |
| Tools | `/tools` | Browse the tool registry |

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + LangGraph + Pydantic v2
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **AI**: Claude (planner + verifier agents)
- **Database**: SQLite (dev), PostgreSQL (production via Docker)

## Current State

- 94/94 backend tests passing
- 45 tools registered (11 original + 34 new)
- Full CRUD for workflows, executions, approvals
- Runner supports: sequential execution, condition branching, approval pause/resume, retries, cancellation
- Frontend being rebuilt from scratch
