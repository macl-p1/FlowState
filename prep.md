# FlowState — Presentation Prep

---

## 1. The Real Problem We're Solving

### The Core Pain Point

Enterprises and teams today automate business processes using a fractured landscape of tools:

| Tool | What it does | What it doesn't do |
|------|-------------|-------------------|
| **Zapier / Make.com** | Connect apps with triggers | Can't handle complex branching, conditional logic, or human approvals |
| **n8n** | Self-hosted workflow builder | Still requires a human to draw every node manually — no AI generation |
| **AWS Step Functions** | Serverless workflow orchestration | Infrastructure-focused, developer-only, steep learning curve |
| **Temporal** | Durable execution for microservices | Designed for engineers writing code, not business users |
| **Airflow** | Data pipeline scheduling | Batch-oriented, not real-time, no natural language interface |
| **Jira / ServiceNow** | Ticketing + ITSM workflows | Rigid, IT-only, expensive, impossible to customize without admin access |

### The Real-World Problem Statement

> "A business analyst wants to automate a multi-step process — say, an invoice approval flow involving email, database checks, conditional routing, manager approval, and payment processing. Today, she has three bad options:"
>
> 1. **Learn a developer tool** — She can't write Python or configure AWS Step Functions.
> 2. **Hire a dev team** — Expensive, slow, and every process change requires a ticket and a sprint.
> 3. **Build a brittle Zapier chain** — Works for simple 2-step automations, breaks at the first condition or human gate.

**Nobody has built a system where a non-technical user describes a process in plain English, and gets a production-grade, observable, auditable, approval-gated workflow back.**

---

## 2. Our Solution

### One-Line Pitch

> **FlowState converts natural language process descriptions into executable, observable workflows with AI verification, retries, branching, and human approval gates — all through a visual interface.**

### How It Works (End-to-End Flow)

```
┌──────────────────────────────────────────────────────────────────┐
│  USER ENTERS: "Process invoices over $100K with manager approval" │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  PLANNER AGENT (Claude)                                          │
│  • Reads the natural language prompt                             │
│  • Knows all available tools from the registry                   │
│  • Generates a structured workflow JSON with nodes & edges       │
│  • Retries up to N times if JSON is invalid                      │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  VALIDATION LAYER                                                │
│  • Pydantic schema validates the JSON structure                  │
│  • Tool references are checked against the registry              │
│  • Missing required fields get default values                    │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  COMPILER (LangGraph)                                            │
│  • Converts validated JSON into a LangGraph StateGraph           │
│  • Wires trigger → actions → conditions → approvals → end        │
│  • Each node becomes an executable step                          │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  RUNNER ENGINE                                                   │
│  • Executes the graph step-by-step                               │
│  • Resolves {{template_variables}} from previous step outputs    │
│  • Calls the Tool Registry for each action node                  │
│  • Persists every step to the database                           │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌──────────────┐          ┌──────────────────┐
          │ SUCCESS PATH │          │ FAILURE / PAUSE  │
          │ → Verifier   │          │ → Retry or HITL  │
          └──────┬───────┘          └────────┬─────────┘
                 │                           │
                 ▼                           ▼
          ┌──────────────┐          ┌──────────────────┐
          │ VERIFIER     │          │ HUMAN APPROVAL   │
          │ (Claude)     │          │ Gate pauses      │
          │ Verdicts:    │          │ execution,       │
          │ SUCCESS/     │          │ waits for human  │
          │ RETRY/       │          │ decision         │
          │ ESCALATE/    │          └────────┬─────────┘
          │ FAIL         │                   │
          └──────────────┘                   ▼
                                   ┌──────────────────┐
                                   │ Resume or Cancel │
                                   │ → Continues or  │
                                   │   stops workflow │
                                   └──────────────────┘
```

### Key Capabilities

1. **Natural Language → Workflow**: No coding, no drag-and-drop. Just describe.
2. **AI-Verified Execution**: After each tool call, a verifier agent judges success/failure/retry/escalate.
3. **Human-in-the-Loop**: Built-in approval gates that pause execution and wait for human decisions.
4. **Retry & Escalation**: Failed steps can retry or escalate to a human — not silently dropped.
5. **Visual Workflow Editor**: React Flow canvas shows the full graph; users can edit any node.
6. **Observable Execution**: Every step is persisted with timestamps, inputs, outputs, and errors.
7. **30+ Tool Registry**: Email, Slack, DB, CRM, finance, HR, logistics, monitoring — pluggable.
8. **Permission Levels**: AUTO / CONFIRM / HUMAN_ONLY — controls which tools need human sign-off.
9. **Template Variables**: `{{variable_name}}` syntax passes data between steps.
10. **Conditional Branching**: `condition` nodes route flow based on expressions.

---

## 3. What Makes Us Unique vs Existing Solutions

### Comparison Matrix

| Feature | FlowState | Zapier | n8n | AWS Step Functions | Temporal | Airflow |
|---------|:----------:|:------:|:---:|:-----------------:|:--------:|:-------:|
| Natural language generation | **Yes** | No | No | No | No | No |
| Visual workflow editor | **Yes** | Limited | Yes | No | No | No |
| AI verifier per step | **Yes** | No | No | No | No | No |
| Human approval gates | **Yes** | Limited | Limited | Yes (manual) | No | No |
| Branching & conditions | **Yes** | Limited | Yes | Yes | Yes | Yes |
| Retry with escalation | **Yes** | No | Basic | Yes | Yes | Yes |
| Non-technical user | **Yes** | Yes | Partial | No | No | No |
| Self-hostable | Yes | No | Yes | Yes | Yes | Yes |
| Pluggable tool registry | **Yes** | Limited | Yes | Yes | No | Partial |
| Real-time execution console | **Yes** | Limited | Yes | Yes | No | No |
| Template variable passing | **Yes** | Yes | Yes | Yes | No | Partial |
| Observability / audit trail | **Yes** | Limited | Partial | Yes | Yes | Partial |

### Our Unique Differentiators

#### 1. AI-Native Workflow Creation
> **"Describe it, it builds."**

Nobody else lets a non-technical user type a sentence and get a fully structured workflow graph. Zapier requires you to manually chain triggers and actions. n8n requires you to drag and drop each node. We generate the entire DAG from natural language.

#### 2. AI Verifier Agent at Every Step
> **The workflow doesn't just execute — it thinks about whether each step succeeded.**

Traditional automation platforms: step fails → retry N times → give up. Our verifier agent analyzes the result and chooses: SUCCESS, RETRY, ESCALATE, or FAIL. This is workflow execution with judgment, not just plumbing.

#### 3. First-Class Human-in-the-Loop
> **Approval isn't a bolt-on — it's a node type.**

In Zapier, you add a "delay." In Step Functions, you configure a callback. In FlowState, `approval` is a first-class node type in the workflow graph. The execution pauses, surfaces to the UI, and resumes when approved.

#### 4. Universal Tool Registry with Permissions
> **One registry, one permission model, any tool.**

30+ built-in tools spanning email, Slack, databases, CRM, finance, HR, logistics, and monitoring. Each tool has a permission level (AUTO / CONFIRM / HUMAN_ONLY). Adding a new tool is one registration call. The LLM can only call what's registered — no arbitrary code execution.

#### 5. Pluggable Architecture
> **Not hardcoded to any domain, any LLM, any database.**

- LLM-agnostic: swap Claude for any Anthropic-compatible API
- Database-agnostic: SQLite for dev, PostgreSQL for prod
- Tool-agnostic: register any Python function as a tool
- Frontend-agnostic: the API is REST, any client can consume it

---

## 4. Architecture Deep-Dive

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                         │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Dashboard  │  │    Builder   │  │  Execution Console        │  │
│  │  (workflow  │  │  (React Flow │  │  (real-time step          │  │
│  │   list +    │  │  canvas +    │  │   timeline + approval     │  │
│  │   stats)    │  │   AI gen)    │  │   gates)                  │  │
│  └─────────────┘  └──────────────┘  └──────────────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Tools     │  │  Templates  │  │  History                  │  │
│  │  Explorer   │  │  Gallery    │  │  (past runs)              │  │
│  └─────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  Design: "Control Room Glass" — dark glass surfaces, phosphor cyan │
│  indicators, monospace numerics. Optimized for monitoring sessions. │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ REST API
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Python)                     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  API Layer                                                  │   │
│  │  /api/workflows — CRUD + generate + run                     │   │
│  │  /api/runs — execution details + cancel                     │   │
│  │  /api/approvals — pending + approve/reject                  │   │
│  │  /api/tools — registry listing + custom tools               │   │
│  │  /api/health — health check                                 │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │  Agent Layer                                                 │   │
│  │                                                              │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │   │
│  │  │  Planner    │  │   Compiler   │  │   Verifier       │   │   │
│  │  │  Agent      │  │   Engine     │  │   Agent          │   │   │
│  │  │             │  │              │  │                  │   │   │
│  │  │ Natural     │  │ JSON →       │  │ Post-execution   │   │   │
│  │  │ Language    │──│ LangGraph    │  │ analysis:        │   │   │
│  │  │ → Workflow  │  │ StateGraph   │  │ SUCCESS/RETRY/   │   │   │
│  │  │   JSON      │  │              │  │ ESCALATE/FAIL    │   │   │
│  │  │             │  │              │  │                  │   │   │
│  │  │ Retry loop  │  │ Node wiring  │  │ Fallback: rule-  │   │   │
│  │  │ on invalid  │  │ Conditional  │  │ based if no LLM  │   │   │
│  │  │ JSON        │  │ edges        │  │                  │   │   │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │  Engine Layer                                                │   │
│  │                                                              │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  WorkflowRunner                                         │ │   │
│  │  │  • Loads workflow from DB                               │ │   │
│  │  │  • Compiles via Compiler                                │ │   │
│  │  │  • Executes graph with LangGraph runtime                │ │   │
│  │  │  • Handles approval pauses + resumes                    │ │   │
│  │  │  • Persists steps + final state                         │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │                                                              │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Tool Registry (30+ tools)                              │ │   │
│  │  │  Categories: Communication, Data, Finance, HR,          │ │   │
│  │  │  Logistics, Monitoring, AI, Scheduling, CRM, Tasks      │ │   │
│  │  │  Permissions: AUTO / CONFIRM / HUMAN_ONLY               │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │                                                              │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Approval Service                                       │ │   │
│  │  │  • Creates approval requests                            │ │   │
│  │  │  • Approve / Reject with audit trail                    │ │   │
│  │  │  • Linked to workflow execution ID                      │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │  Data Layer                                                   │   │
│  │  SQLAlchemy ORM → SQLite (dev) / PostgreSQL (prod)           │   │
│  │  Tables: workflows, workflow_executions, step_executions,     │   │
│  │          approval_requests, custom_tools                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Lifecycle in Detail

```
Step 1: PLANNER
  Input:  "Process invoices over $100K with manager approval"
  Action: Claude receives system prompt with all registered tools
  Output: Validated Workflow JSON (nodes + edges)
  Retry:  If JSON invalid → repair prompt → retry (up to N times)

Step 2: VALIDATION
  Pydantic schema checks structure
  Tool references checked against registry
  Missing IDs auto-generated

Step 3: COMPILER
  JSON → LangGraph StateGraph
  Each node type wired differently:
    trigger  → entry point
    action   → tool execution
    condition → conditional_edges (true/false branches)
    approval → pause, no outgoing edges
    wait     → pass-through with delay
    end      → graph END

Step 4: RUNNER
  Creates execution record in DB
  Invokes LangGraph graph.ainvoke()
  Each step: resolve templates → execute tool → record result
  If approval node reached: status → WAITING_APPROVAL

Step 5: VERIFIER
  After each tool execution:
    LLM analyzes result → SUCCESS / RETRY / ESCALATE / FAIL
    Fallback: rule-based (check success flag + retryable flag)

Step 6: APPROVAL (if triggered)
  Execution pauses
  Approval request appears in UI
  Human clicks Approve/Reject
  Runner resumes from next node (or cancels)
```

### Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14 + TypeScript | React ecosystem, SSR, fast dev |
| Visual Editor | React Flow | Industry-standard node graph library |
| UI Design | Tailwind CSS + Framer Motion | Rapid styling, glassmorphism animations |
| Backend | FastAPI + Pydantic | Auto-generated docs, type safety, async |
| Workflow Engine | LangGraph | Stateful graph execution, checkpoints, persistence |
| AI | Anthropic Claude API | Best-in-class JSON generation, tool use |
| Database | SQLite / PostgreSQL | Dev simplicity → prod scalability |
| Testing | pytest + TestClient | Full backend test coverage |

---

## 5. Demo Walkthrough (3-4 minutes)

### Demo 1: Generate a Workflow from Natural Language

1. Open the Builder page
2. Type: *"Send a welcome email to new customers, then create a task for the sales team to follow up within 3 days"*
3. Click "Generate Workflow"
4. Show the resulting graph: trigger → send_email (with template variables) → create_task → end
5. Highlight the edge labels and node types

### Demo 2: Run and Observe

1. Click "Run Workflow"
2. Switch to the Console page
3. Show the execution timeline with step-by-step results
4. Show tool inputs, outputs, and the verifier's judgment

### Demo 3: Approval Gate

1. Create a workflow with an approval node (e.g., "Process payment → manager approval → complete")
2. Run it and show the workflow pausing at the approval node
3. Approve or reject and show the resume/cancel behavior

---

## 6. Counter Questions We Expect (and How to Answer Them)

### Q1: "How is this different from Zapier? Zapier already connects apps."

**A:** Zapier is a trigger-action chain — it's linear. Our system generates a full DAG (directed acyclic graph) from natural language, with conditional branching, approval gates, AI verification at every step, and a verifier agent that judges success/failure/retry. Zapier can't branch intelligently, can't pause for human decisions natively, and certainly can't analyze whether a step actually succeeded. We're not a connector — we're an **intelligent execution layer**.

---

### Q2: "n8n is open-source and has a visual editor. Why not just use that?"

**A:** n8n still requires you to manually build every node. You're drawing the workflow yourself. Our differentiator is **AI generation** — you describe the process in plain English, and the system builds the graph. Also, n8n lacks: (1) an AI verifier per step, (2) first-class approval gates as graph nodes, (3) intelligent retry/escalation logic, and (4) our pluggable tool registry with permission levels.

---

### Q3: "AWS Step Functions already does workflow orchestration with branching and retries."

**A:** Step Functions is infrastructure for developers. You write JSON state machines or CloudFormation templates. A business analyst cannot use it. Our target user is someone who thinks in processes, not code. We add: natural language generation, a visual editor, an AI verifier, and a human-friendly approval system. We're the **translation layer** between business intent and execution infrastructure.

---

### Q4: "How do you ensure the LLM generates valid workflows? What if it hallucinates?"

**A:** Three-layer defense:
1. **Planner retry loop**: If the LLM outputs invalid JSON, we send a repair prompt with the specific errors and retry (up to N times).
2. **Pydantic validation**: The JSON is validated against a strict schema before compilation.
3. **Tool registry enforcement**: The LLM can only reference tools that actually exist. If it hallucinates a tool name, validation catches it and forces a retry.

---

### Q5: "What about security? The LLM is executing tools — couldn't it do something dangerous?"

**A:** Four security layers:
1. **Closed tool registry**: The LLM can ONLY call registered tools. No arbitrary code execution.
2. **Permission levels**: Each tool has AUTO / CONFIRM / HUMAN_ONLY. Destructive tools (delete, payment, DB update) require confirmation or human approval.
3. **Sandboxed execution**: Tools are mock implementations by default. Real integrations would run in isolated environments.
4. **No eval of LLM output**: The LLM generates workflow structure, not executable code. The runner interprets the JSON and calls pre-defined functions.

---

### Q6: "LangGraph is a dependency — what if you want to switch to a different orchestration engine?"

**A:** The Compiler is the abstraction layer. Today it outputs a LangGraph StateGraph, but the interface is `compile(workflow) → CompiledWorkflow`. The Runner depends on the CompiledWorkflow interface, not LangGraph directly. Swapping the engine would mean rewriting the Compiler — the rest of the system (Planner, Verifier, Registry, Approval, DB models) stays untouched. This is intentional decoupling.

---

### Q7: "This seems like a prototype. How would this scale to production?"

**A:** Good question. Current state:
- **Database**: SQLite for dev, schema supports PostgreSQL (SQLAlchemy ORM is DB-agnostic)
- **Execution**: LangGraph with MemorySaver — swap to PostgresSaver or RedisSaver for persistent, distributed checkpoints
- **LLM calls**: Already async with proper error handling
- **Frontend**: Next.js with API routes — can be deployed to Vercel or self-hosted
- **Tool implementations**: Currently mock. Real tools would call external APIs with proper auth, timeouts, and circuit breakers

The architecture is designed to scale. The bottlenecks would be LLM latency (mitigated by caching plan results) and tool execution (mitigated by async + queue-based execution).

---

### Q8: "Why not just use LangChain Agents instead of building this custom?"

**A:** LangChain Agents are great for conversational AI — they answer questions and take actions in a chat loop. They're not designed for **structured, observable, resumable, multi-step business processes**. Our system needs:
- **DAG execution** (not a conversation loop)
- **Persistent state** across steps (not a sliding context window)
- **Approval gates** that pause and resume
- **Visual workflow representation** (the graph IS the product)
- **Observability** (every step logged with timestamps, inputs, outputs)
- **Business-level retry/escalation** (not just LLM retry)

We use LangGraph (from LangChain) as the execution engine, but the entire system above it — the Planner, Verifier, Registry, Approval — is custom because no existing agent framework addresses this use case.

---

### Q9: "How do you handle failures? What if a tool is down?"

**A:** Multi-layered:
1. **Tool-level**: Each tool implementation returns a `ToolResult` with `success`, `error`, and `retryable` flags.
2. **Verifier-level**: The verifier agent (or rule-based fallback) classifies failures as RETRY, ESCALATE, or FAIL.
3. **Runner-level**: The execution engine captures failures, updates the execution record, and surfaces errors to the UI.
4. **Resume-level**: If a workflow fails mid-execution, the persisted step records allow resuming from the last successful step (implemented in the `resume()` method).

---

### Q10: "What's the business model? Who pays for this?"

**A:** (Answer based on your actual vision — here are common angles):
- **SaaS**: Per-workflow or per-execution pricing for hosted version
- **Open-core**: Core engine open-source, enterprise features (SSO, audit logs, custom tool hosting) paid
- **Enterprise**: Self-hosted license with support, custom tool development, SLA guarantees
- **Marketplace**: Third-party tool integrations as a revenue share model

---

### Q11: "How do you handle concurrency? What if two users run the same workflow simultaneously?"

**A:** LangGraph's checkpointer (MemorySaver today, PostgresSaver in production) isolates executions by `thread_id`. Each execution gets a unique ID. The database uses proper transaction isolation. Concurrent executions don't share state — each has its own `context` dict. Tool implementations would need their own concurrency handling (rate limiting, connection pooling) depending on the external service.

---

### Q12: "What LLM do you use? Are you locked into Anthropic?"

**A:** Currently Anthropic Claude, but the architecture is LLM-agnostic:
- `PlannerAgent` and `VerifierAgent` accept an `llm_client` parameter
- The config uses `anthropic_api_key` and `anthropic_base_url`
- To swap to OpenAI: change the client initialization and adjust message formats
- The base_url override already supports compatible endpoints (e.g., local models via LiteLLM)

---

## 7. Key Metrics to Mention

| Metric | Value |
|--------|-------|
| Nodes types supported | 6 (trigger, action, condition, approval, wait, end) |
| Built-in tools | 30+ (email, Slack, DB, CRM, finance, HR, logistics, monitoring, AI, scheduling) |
| Permission levels | 3 (AUTO, CONFIRM, HUMAN_ONLY) |
| Verifier verdicts | 4 (SUCCESS, RETRY, ESCALATE, FAIL) |
| Planner retry attempts | Configurable (default: 3) |
| API endpoints | 10 (workflows, runs, approvals, tools, health) |
| Test coverage | Full backend test suite (pytest) |
| Frontend pages | 6 (Dashboard, Builder, Console, Tools, History, Landing) |
| Tech stack | 8 technologies |
| Agent pipeline steps | 5 (Plan → Validate → Compile → Run → Verify) |

---

## 8. Closing Statement (30-second version)

> "Today, business process automation is split between tools for developers and tools for non-technical users — with nothing in between. Developers use Step Functions and Temporal. Non-technical users use Zapier. Both require you to build the workflow manually.
>
> FlowState bridges this gap. A business user describes a process in plain English. Our Planner agent converts it into a structured workflow graph. Our Compiler turns it into an executable pipeline. Our Verifier judges each step's success. And our approval system ensures no critical action happens without human sign-off.
>
> We're not building a better Zapier. We're building the **operating system for AI-driven business processes** — where the AI plans, the system executes, the verifier judges, and humans stay in control."
