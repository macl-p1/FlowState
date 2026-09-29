# Universal Workflow Agent — Claude Code Build Plan

> **Hackathon goal:** Build a universal agentic workflow automation platform where a user describes a process in natural language, the system converts it into an executable workflow, runs it through registered tools, verifies results, handles retries/branches, and pauses for human approval when needed.
>
> **Primary demo:** Generate and execute an invoice-processing workflow, pause at a human approval gate, resume after approval, then generate a completely different employee-onboarding workflow using the same engine.

---

## How to use this plan

This document is intentionally divided into **Claude Code sessions**.

**Rule:** Complete one session, run the requested tests, fix errors, and only then start the next session.

Claude Code should not attempt to build the entire application in one shot.

### Core principle

```text
Natural Language
      ↓
Planner Agent
      ↓
Validated Workflow JSON
      ↓
Workflow Graph
      ↓
Tool Execution
      ↓
Observe Result
      ↓
Verify
   ↙      ↘
Success   Failure
  ↓         ↓
Next      Retry / Escalate
  ↓
Human Approval when required
  ↓
Resume
  ↓
Complete
```

---

# Product Definition

## Product name

Working name: **FlowPilot**

Alternative names:
- AgentFlow
- AutoOps
- OrchestrAI
- FlowForge
- Runway AI

## Product promise

> **Describe a workflow. Let the agent build, execute, verify, and manage it.**

The product should feel like an **AI operating system for business workflows**, not a chatbot.

---

# Tech Stack

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Flow
- Framer Motion
- Lucide icons

## Backend

- Python
- FastAPI
- Pydantic
- LangGraph

## AI

- Anthropic Claude API
- Structured output / JSON schema validation

## Database

- PostgreSQL
- SQLAlchemy or equivalent

## Integrations

Start with a controlled mock tool layer:

- Email
- Slack
- Database
- Ticket creation
- Calendar
- Human approval

Then optionally connect real APIs/MCP tools after the core engine works.

## Development

- Docker Compose
- `.env`
- pytest
- TypeScript checks
- ESLint

---

# UI Direction — Glass Morphism

The frontend is a major part of the hackathon presentation.

## Visual concept

Create a **premium dark glassmorphism command center**.

Think:

- deep near-black background
- subtle blue/purple ambient gradients
- translucent glass panels
- backdrop blur
- thin low-opacity borders
- soft shadows
- restrained neon accents
- smooth micro-interactions
- generous whitespace
- highly legible typography

Do **not** make it look like a generic SaaS dashboard.

It should feel like a futuristic **AI operations control room**.

## Design language

### Background

Use a dark base with large blurred radial gradients.

Example conceptual layers:

```text
background
├── dark base
├── blurred blue glow
├── blurred violet glow
└── subtle grid/noise texture
```

### Glass panels

Use:

```css
background: rgba(...)
backdrop-filter: blur(...)
border: 1px solid rgba(...)
box-shadow: ...
```

Keep glass effects subtle. Avoid excessive transparency that hurts readability.

### Typography

Use a modern sans-serif.

Recommended hierarchy:

- very large display heading
- compact uppercase labels
- medium-weight section headings
- readable body text
- monospace for execution IDs, JSON, logs, and tool calls

### Accent behavior

Use accent colors semantically:

- blue = active/running
- green = completed
- amber = waiting/approval
- red = failed
- violet = AI/planning

Do not turn every element into neon.

---

# Frontend Information Architecture

Build these main views:

```text
/
├── Dashboard
│
├── /create
│   └── Natural-language workflow builder
│
├── /workflow/[id]
│   └── Visual workflow editor
│
├── /run/[id]
│   └── Live execution console
│
└── /templates
    └── Example workflows
```

---

# Session 01 — Repository and Project Foundation

## Objective

Create the initial monorepo and get frontend/backend/database running.

## Claude Code prompt

```text
You are the lead engineer for a hackathon project called FlowPilot, a Universal Workflow Agent.

Build the project incrementally. Do not implement the complete application in this session.

Architecture:

Frontend:
- Next.js
- TypeScript
- Tailwind
- shadcn/ui
- React Flow
- Framer Motion
- Lucide

Backend:
- Python
- FastAPI
- Pydantic
- LangGraph

Database:
- PostgreSQL

Create:

/frontend
/backend
/examples
/docker-compose.yml
/.env.example
/README.md

Frontend requirements:
- dark premium glassmorphism visual system
- reusable GlassPanel component
- global background ambient gradients
- typography hierarchy
- responsive layout
- clean component architecture

Backend requirements:
- FastAPI app
- /health endpoint
- environment configuration
- PostgreSQL connection
- basic API structure

Do not implement AI agents yet.

Run:
- frontend typecheck
- frontend lint
- backend tests
- backend import/startup check

At the end report:
1. files created
2. commands to run
3. tests run
4. unresolved issues
```

## Acceptance criteria

- Frontend loads.
- Backend `/health` works.
- PostgreSQL starts.
- Glassmorphism base theme exists.
- No agent logic yet.

---

# Session 02 — Design System and Glassmorphism Shell

## Objective

Build the visually impressive application shell before adding functionality.

## Claude Code prompt

```text
Implement the FlowPilot frontend design system.

Create a premium dark glassmorphism AI operations interface.

Requirements:

1. Full-screen dark background.
2. Subtle blurred ambient gradient orbs.
3. Glass panels with:
   - backdrop blur
   - low-opacity backgrounds
   - thin translucent borders
   - subtle shadows
4. Responsive layout.
5. Accessible contrast.
6. Smooth hover/focus transitions.
7. Framer Motion for restrained page and panel animations.
8. Lucide icons.
9. Avoid excessive gradients and visual clutter.

Create reusable components:

- GlassPanel
- GlassButton
- StatusBadge
- SectionLabel
- AmbientBackground
- PageHeader
- EmptyState
- LoadingState

Create application shell:

- left navigation
- top status bar
- main content region

Navigation:

Dashboard
Workflows
Runs
Templates
Tools
Settings

Dashboard hero:

"Automate the work.
Let agents run the rest."

Subtitle:

"Describe a process in plain English. FlowPilot turns it into an executable, observable workflow."

Add a prominent workflow input card with:
- large textarea
- example prompts
- Generate Workflow button

Do not connect it to the backend yet.

Focus heavily on polish.
```

## Acceptance criteria

The UI should already look presentation-ready before backend functionality exists.

---

# Session 03 — Workflow Schema

## Objective

Create the universal workflow representation.

## Claude Code prompt

```text
Implement the workflow schema in the backend.

Create strict Pydantic models for:

Workflow
Trigger
ActionNode
ConditionNode
ApprovalNode
Edge
ToolDefinition
WorkflowState
WorkflowExecution
StepExecution
ToolResult

The schema must support:

- sequential execution
- branching
- retries
- human approval
- pause/resume
- completion
- failure
- metadata
- tool inputs
- expected outcomes

Example node types:

trigger
action
condition
approval
wait
end

Do not permit arbitrary Python code in workflow definitions.

Create:
- schema validation
- serialization
- deserialization
- unit tests

Create example workflow JSON files:

examples/employee_onboarding.json
examples/invoice_processing.json
examples/customer_support.json

The examples must use the exact same universal schema.

Do not add workflow-specific engine logic.
```

---

# Session 04 — Tool Registry

## Objective

Create a safe tool system.

## Claude Code prompt

```text
Implement a generic tool registry.

Create:

Tool
ToolRegistry
ToolPermission
ToolResult

Each tool must have:

- name
- description
- input schema
- permission level
- async execute function

Implement mock tools:

send_email
send_slack_message
search_database
update_database
create_ticket
create_calendar_event
request_human_approval
wait

Permission levels:

AUTO
CONFIRM
HUMAN_ONLY

The agent may only call registered tools.

The LLM must never execute arbitrary Python or shell commands.

Add unit tests for:
- registration
- lookup
- invalid tool
- input validation
- permissions
- successful execution
- failed execution
```

---

# Session 05 — Planner Agent

## Objective

Convert natural language into validated workflow JSON.

## Claude Code prompt

```text
Implement PlannerAgent using the Anthropic Claude API.

Input:
natural-language workflow description

Output:
strict Workflow Pydantic object

Pipeline:

User prompt
  ↓
Claude
  ↓
Structured workflow
  ↓
Pydantic validation
  ↓
Tool validation
  ↓
Workflow accepted

If validation fails:
- capture validation errors
- ask Claude to repair the structured output
- retry a limited number of times
- return a useful error if still invalid

Important:

The planner must never invent tools.

It can only use tools returned by ToolRegistry.

The planner should reason about:
- workflow steps
- dependencies
- branching
- failure conditions
- approval requirements
- retry behavior

Do not expose hidden chain-of-thought in the UI or API.

Return concise planning metadata instead:
- number of nodes
- tools selected
- approval gates
- estimated workflow complexity

Add tests using mocked LLM responses.
```

---

# Session 06 — Workflow Compiler

## Objective

Convert the planner's JSON into an executable graph.

## Claude Code prompt

```text
Implement WorkflowCompiler.

Input:
validated Workflow object

Output:
executable LangGraph representation.

Support:
- sequential nodes
- conditional branches
- retry edges
- approval pauses
- completion
- failure

Do not put business-specific logic inside the compiler.

The compiler must work with any valid Workflow schema.

Add tests for:
1. sequential workflow
2. branching workflow
3. retry workflow
4. approval workflow
5. invalid graph
```

---

# Session 07 — Execution Engine

## Objective

Build the actual agent runtime.

## Claude Code prompt

```text
Implement WorkflowRunner.

Execution lifecycle:

START
 ↓
Load workflow state
 ↓
Get current node
 ↓
Execute action/tool
 ↓
Persist result
 ↓
Verify outcome
 ↓
Determine next node
 ↓
Repeat
 ↓
COMPLETE

Requirements:

- persistent execution state
- step-level execution logs
- timestamps
- tool inputs/outputs
- status
- retries
- failure handling
- pause/resume
- idempotency where practical

Execution statuses:

PENDING
RUNNING
WAITING_APPROVAL
RETRYING
COMPLETED
FAILED
CANCELLED

Create database models for:
- Workflow
- WorkflowVersion
- WorkflowExecution
- StepExecution
- ApprovalRequest

Every step must be observable.
```

---

# Session 08 — Verifier Agent

## Objective

Prevent the agent from assuming a task succeeded.

## Claude Code prompt

```text
Implement VerifierAgent.

The verifier receives:

- workflow node
- tool call
- tool result
- expected outcome

It returns:

SUCCESS
RETRY
ESCALATE
FAIL

The verifier should use structured output.

Example:

Tool:
send_email

Result:
API returned 500

Verifier:
RETRY

Another example:

Tool:
invoice_validation

Result:
invoice amount exceeds approval threshold

Verifier:
ESCALATE

Do not expose private chain-of-thought.

Return only structured verification data and a short user-facing explanation.

Add tests for success, retry, escalation, and failure.
```

---

# Session 09 — Human Approval System

## Objective

Make the agent pause safely and resume.

## Claude Code prompt

```text
Implement human-in-the-loop approval.

When a workflow reaches an approval node:

1. Persist workflow state.
2. Create ApprovalRequest.
3. Set execution status to WAITING_APPROVAL.
4. Stop execution.
5. Expose pending approval through API.
6. Allow frontend to approve or reject.
7. Resume workflow after approval.
8. Record who approved/rejected and when.

Approval UI must show:

- workflow name
- current step
- reason
- relevant data
- requested action
- approve button
- reject button

Make approval state durable across server restarts.
```

---

# Session 10 — Backend API

## Objective

Expose the engine to the frontend.

## API endpoints

```text
POST /api/workflows/generate
POST /api/workflows
GET  /api/workflows
GET  /api/workflows/{id}

POST /api/workflows/{id}/run
GET  /api/runs/{id}
POST /api/runs/{id}/cancel

GET  /api/runs/{id}/events

GET  /api/approvals
POST /api/approvals/{id}/approve
POST /api/approvals/{id}/reject

GET /api/tools
```

## Claude Code prompt

```text
Implement the API layer for FlowPilot.

Connect:
- planner
- compiler
- runner
- verifier
- tool registry
- approval system
- database

Use Pydantic request/response models.

Add:
- validation
- consistent errors
- structured logging
- CORS
- environment configuration

Do not expose secrets.

Add API tests.
```

---

# Session 11 — Workflow Builder UI

## Objective

Connect natural-language generation to the visual workflow.

## Claude Code prompt

```text
Build the workflow builder UI.

Flow:

User enters natural-language workflow
        ↓
Generate Workflow
        ↓
Backend planner
        ↓
Validated workflow
        ↓
React Flow graph

Create visual node components for:

Trigger
Action
Condition
Approval
Wait
End

Visual states:

default
selected
running
completed
waiting
failed

Glassmorphism requirements:
- translucent nodes
- subtle border glow
- status-specific accent
- smooth transitions
- clear text hierarchy

Allow users to:
- inspect node details
- view selected tool
- view inputs
- view expected outcome
- start execution

Do not make the graph visually overwhelming.
```

---

# Session 12 — Live Execution Console

## Objective

Create the strongest visual demo screen.

## Claude Code prompt

```text
Build a live execution console.

When a workflow runs, display:

LEFT:
React Flow workflow graph

RIGHT:
Execution timeline

BOTTOM:
Current agent/tool details

Timeline examples:

✓ Workflow started
✓ Invoice received
✓ Extracted invoice data
✓ Found purchase order
✓ Compared invoice
⚠ Human approval required

When a node is running:
- animate it subtly
- show spinner/status
- highlight the active path

When completed:
- show completed state

When failed:
- show error state

When waiting for approval:
- show prominent but elegant approval card

Use Server-Sent Events or WebSockets for live updates.

The UI should feel like an AI execution observability console.
```

---

# Session 13 — Demo Workflows

## Objective

Make three workflows work end-to-end.

## 1. Invoice Processing

```text
Invoice Received
      ↓
Extract Invoice
      ↓
Find Purchase Order
      ↓
Compare
      ↓
Matches?
   ↙       ↘
 YES       NO
 ↓          ↓
Approval   Human Review
 ↓
Payment Request
 ↓
Complete
```

## 2. Employee Onboarding

```text
Employee Added
      ↓
Request Documents
      ↓
Verify Documents
      ↓
Complete?
   ↙       ↘
 YES       NO
 ↓          ↓
Notify HR  Reminder
 ↓
Notify Manager
 ↓
Complete
```

## 3. Customer Complaint

```text
Complaint Received
      ↓
Identify Customer
      ↓
Find Order
      ↓
Check Delivery
      ↓
Determine Issue
      ↓
Generate Response
      ↓
Send Response
      ↓
Escalate if Required
```

## Claude Code prompt

```text
Validate the three end-to-end demo workflows.

IMPORTANT:
They must run through the same planner/compiler/runner/tool architecture.

Do not create special-case code such as:
if workflow == "invoice":
    ...

The workflow engine must remain generic.

Create deterministic mock data so the hackathon demo is reliable.

Add a demo mode that allows:
- successful execution
- intentional failure
- human approval
- retry
```

---

# Session 14 — Dashboard

## Objective

Make the product feel complete.

## Dashboard content

### Hero

```text
Automate the work.
Let agents run the rest.
```

### Metrics

```text
Active Workflows
12

Running Now
4

Completed Today
87

Awaiting Approval
3
```

### Recent Runs

Show:

- workflow name
- status
- duration
- started time
- current step

### Quick Start

Cards:

```text
Invoice Processing
Employee Onboarding
Customer Support
Create from Scratch
```

---

# Session 15 — Templates

## Objective

Allow instant demos.

Create polished workflow template cards:

- Invoice Processing
- Employee Onboarding
- Customer Complaint
- IT Helpdesk
- Procurement
- Meeting → Action Items

Each card should have:

- icon
- description
- number of steps
- tools used
- approval gates
- "Use Template"

---

# Session 16 — Tool Explorer

## Objective

Show why the system is universal.

Create a Tools page.

Example:

```text
TOOLS

Connected

● Email
  send_email
  read_email

● Slack
  send_slack_message

● Database
  search_database
  update_database

● Calendar
  create_calendar_event

AI Controls

● Human Approval
  request_human_approval
```

Show tool permissions.

---

# Session 17 — Error Handling and Reliability

## Claude Code prompt

```text
Perform a reliability pass.

Test:

- malformed LLM output
- unknown tool
- invalid tool arguments
- tool timeout
- tool failure
- verifier failure
- workflow dead end
- invalid condition
- duplicate execution
- approval rejection
- server restart while waiting
- resume after restart

The application should fail gracefully.

Never silently mark a workflow as successful.

Every failed execution must have a visible reason.
```

---

# Session 18 — Security Pass

## Claude Code prompt

```text
Perform a security review.

Check:

- API key exposure
- arbitrary code execution
- shell execution
- SQL injection
- unsafe tool parameters
- prompt injection from workflow data
- unauthorized tool execution
- approval bypass
- sensitive information in logs
- CORS configuration
- environment variable handling

Implement a tool permission boundary.

Never allow the LLM to directly execute arbitrary code.

Treat external documents, emails, and database content as untrusted input.

Document remaining security limitations clearly.
```

---

# Session 19 — Final UI Polish

## Claude Code prompt

```text
Perform a final frontend polish pass.

Do not add major functionality.

Focus on:

- glassmorphism consistency
- spacing
- typography
- responsive behavior
- loading states
- skeleton states
- empty states
- hover states
- focus states
- transitions
- error states
- accessibility
- keyboard navigation

Make the application feel like a premium AI operations product.

Avoid:
- excessive gradients
- excessive animations
- tiny text
- cluttered dashboards
- unnecessary cards
- generic template-like styling

The main demo screen should immediately communicate:

AI is planning.
AI is executing.
AI is observing.
Human approval is available.
```

---

# Session 20 — Hackathon Demo Mode

## Objective

Make the demo deterministic.

Create a Demo Mode.

### Demo sequence

```text
1. Open FlowPilot

2. Enter:
"When an invoice arrives, extract the details,
match it against the purchase order, and request
approval if the amount exceeds ₹100,000."

3. Click Generate Workflow.

4. Show generated graph.

5. Click Run.

6. Watch:
   ✓ Invoice received
   ✓ Data extracted
   ✓ PO found
   ✓ Invoice matched
   ⚠ Approval required

7. Approve.

8. Watch:
   ✓ Payment request created
   ✓ Workflow completed

9. Return to builder.

10. Enter:
"When a new employee joins, collect documents,
verify them, notify HR and remind them if anything
is missing."

11. Generate.

12. Show completely different workflow.

13. Explain:
"The engine didn't change.
Only the workflow description changed."
```

---

# Session 21 — Final README and Architecture

## Claude Code prompt

```text
Write the final README.

Include:

1. Product overview
2. Problem
3. Solution
4. Architecture
5. Agent lifecycle
6. Tool system
7. Human-in-the-loop
8. Tech stack
9. Local setup
10. Environment variables
11. Running tests
12. Demo instructions
13. Security model
14. Known limitations
15. Future roadmap

Include a clean Mermaid architecture diagram.

Do not make unsupported claims.
```

---

# Final Architecture

```text
                         USER
                           │
                           ▼
                 ┌──────────────────┐
                 │  Next.js UI      │
                 │ Glassmorphism    │
                 │ React Flow       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     FastAPI      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Planner Agent  │
                 │     Claude       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Pydantic Schema  │
                 │    Validation    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Workflow Compiler│
                 │    LangGraph     │
                 └────────┬─────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Workflow Runner  │
                └─────────┬──────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Tool Call     Verifier     Condition
             │            │            │
             ▼            │            │
        Tool Registry     │            │
             │            │            │
       ┌─────┼─────┐      │            │
       ▼     ▼     ▼      │            │
     Email Slack  DB      │            │
                           │            │
                           ▼            │
                    ┌─────────────┐    │
                    │ Retry /     │◄───┘
                    │ Escalation  │
                    └──────┬──────┘
                           │
                           ▼
                    Human Approval
                           │
                           ▼
                      Resume Run
                           │
                           ▼
                       COMPLETE
```

---

# Non-Negotiable Engineering Rules

1. **No arbitrary code execution by the LLM.**
2. **No hard-coded workflow-specific engine logic.**
3. **All workflows use the same schema.**
4. **All tools go through ToolRegistry.**
5. **All consequential actions have permissions.**
6. **Every execution step is observable.**
7. **Workflow state is persistent.**
8. **Approval can pause and resume execution.**
9. **LLM outputs are validated before execution.**
10. **Failures are explicit, never silently ignored.**
11. **Do not expose hidden chain-of-thought.**
12. **Build incrementally and test after every session.**

---

# What NOT to Build

For a hackathon, avoid spending time on:

- complex user management
- enterprise billing
- 50 integrations
- mobile apps
- complicated RBAC
- custom LLM training
- vector databases unless actually needed
- elaborate workflow marketplace
- production-scale distributed infrastructure

The judging moment is the **agent execution**, not the number of features.

---

# Hackathon Priority Order

If time becomes limited:

## Tier 1 — Must work

- Natural language input
- Workflow generation
- Workflow schema
- Tool registry
- Workflow execution
- React Flow visualization
- Human approval
- Live execution logs

## Tier 2 — Strong differentiators

- Verification agent
- Retry
- Branching
- Persistent state
- Three workflows
- Demo mode

## Tier 3 — Polish

- Templates
- Tool explorer
- Dashboard metrics
- Animations
- Real integrations
- MCP

---

# Final 3-Minute Pitch

> **"Most workflow automation platforms require humans to manually define every step. We wanted to remove that bottleneck."**
>
> **"With FlowPilot, you describe a workflow in plain English. Our planning agent converts that description into a validated workflow graph, selects tools from a controlled registry, executes each step, verifies the results, handles failures, and pauses for human approval whenever an action requires authorization."**
>
> **"Let's start with an invoice."**
>
> Generate the workflow.
>
> Run it.
>
> Let it reach the approval gate.
>
> Approve it.
>
> Show completion.
>
> Then say:
>
> **"Now I'll give it a completely different problem."**
>
> Enter employee onboarding.
>
> Generate the second workflow.
>
> **"The engine didn't change. The workflow did."**
>
> **"That's our Universal Workflow Agent."**

---

# Definition of Done

The project is ready for judging when this exact sequence works reliably:

```text
Natural language
      ↓
Workflow generated
      ↓
Workflow visually displayed
      ↓
User clicks Run
      ↓
Agent executes tools
      ↓
Execution appears live
      ↓
Agent encounters approval gate
      ↓
UI asks human
      ↓
Human approves
      ↓
Agent resumes
      ↓
Verifier confirms result
      ↓
Workflow completes
      ↓
Execution history is saved
```

**If this works beautifully, stop adding features and rehearse the demo.**
