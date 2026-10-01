# OrchestrAI — Feature Plan

## What's Built

### Backend — Core Engine
- [x] FastAPI app with CORS, lifespan, API key auth
- [x] SQLAlchemy ORM (Workflow, Execution, ExecutionStep, Approval, WorkflowVersion, Branch models)
- [x] **Planner** — LLM-based workflow generation from natural language prompts
- [x] **Compiler** — validates and compiles workflow graphs (trigger, action, condition, approval, wait, end nodes)
- [x] **Runner** — executes compiled workflows step-by-step with retry, branching, approvals
- [x] **Verifier** — rule-based + optional LLM verification of step results
- [x] **Tool Registry** — 8 built-in tools (http, email, db, delay, transform, webhook, extract_invoice, process_payment, update_db, create_ticket)
- [x] **Approval System** — human-in-the-loop with approve/reject/cancel
- [x] **Custom Tools CRUD** — create, read, update, delete, verify, register
- [x] **Integrations** — HTTP, database, AWS S3, email SMTP, Slack with credential masking

### Backend — Genealogy
- [x] Version snapshots with diff computation (added/removed/modified nodes & edges)
- [x] Branch workflow — create named branches from any version
- [x] Lineage tracking — ancestry graph across branches
- [x] Version history per workflow

### Backend — Cross-Pollination
- [x] Pattern extraction — 8 patterns (retry, error_handling, approval_gate, human_escalation, branching, input_validation, wait_delay, fallback_path)
- [x] Weighted Jaccard similarity scoring (node types 0.30, edge signatures 0.30, tools 0.40)
- [x] Pattern gap detection — find what similar workflows have that this one doesn't
- [x] Structured apply-patch engine (update_node, insert_between, insert_between_with_branch, append_node)
- [x] LLM enrichment via Claude for richer suggestions
- [x] API endpoints: GET suggestions, POST apply suggestion

### Backend � Evolution Engine
- [x] Sandbox fitness (mock-only tools, in-memory DB): success rate without approval gates or failures
- [x] Mutations: cross-pollination patches + retry bumps
- [x] `POST /workflows/{id}/evolve` � scores variants; `apply=true` saves winner as a version with rationale
- [ ] Multi-generation loop / crossover (single generation today)

### Frontend
- [x] Next.js app with glassmorphism UI
- [x] Dashboard — workflow list
- [x] **Builder** — React Flow canvas with:
  - [x] AI prompt-to-workflow generation
  - [x] Node palette (6 tool types)
  - [x] Node configuration panel
  - [x] Auto-save before run
  - [x] Execution result overlay with step-by-step status
- [x] Version History Panel — browse and load past versions
- [x] Suggestions Panel — cross-pollination suggestions grouped by source workflow
- [x] Execution Console — run detail view
- [x] Templates & Tools Explorer

### Tests — 146/146 passing
- [x] 16 cross-pollination tests (patterns, similarity, gaps, patches, suggestions integration)
- [x] 12 genealogy tests (diff, versions, branching, lineage)
- [x] 10 integration tests (credential masking, dispatch, execution)
- [x] 8 planner tests
- [x] 9 compiler tests
- [x] 9 runner tests
- [x] 11 schema tests
- [x] 12 tool tests
- [x] 7 verifier tests
- [x] 11 API tests
- [x] 9 approval tests

## What Needs to Be Built

### 1. Execution Caching / Resumability
Cache step outputs so a failed workflow re-runs only from the failure point.
- [ ] ExecutionStep cache table (input_hash → output, status)
- [ ] Runner check: skip steps where input hasn't changed since last successful run
- [ ] `--from-step` flag on run endpoint
- [ ] Cache invalidation when workflow definition changes

### 2. Workflow Templates Marketplace
Turn the cross-pollination engine into a browsable template library.
- [ ] Template model (published, community vs private)
- [ ] Template CRUD API
- [ ] Browse/search templates page in frontend
- [ ] One-click import from template to new workflow

### 3. Real-time Execution Console
Live streaming of workflow runs with node-by-node status.
- [ ] Server-Sent Events or WebSocket endpoint for run progress
- [ ] Streaming step updates from runner to frontend
- [ ] Live node highlighting on the builder canvas during execution

### 4. Multi-env Deployment
Dev/staging/prod promotion with approval gates between environments.
- [ ] Environment model (dev, staging, prod with connection configs)
- [ ] Promotion workflow with approval gate
- [ ] Deployment history per environment
- [ ] Rollback to previous version

### 5. Observability & Analytics
Execution metrics, failure rate dashboards, pattern heatmaps.
- [x] Execution metrics aggregation (per tool; per node not yet)
- [x] Dashboard stats endpoint (`GET /api/analytics/stats`)
- [ ] Frontend analytics page (charts, heatmaps, trends)
- [ ] Alerting rules (e.g., failure rate > threshold)
