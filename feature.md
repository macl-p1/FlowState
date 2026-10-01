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

### Backend � Triggers, Durable Runs & Replay
- [x] Schedule triggers (interval or 5-field cron, UTC) and webhook triggers (secret URL, JSON body becomes run input)
- [x] Durable run queue: runs are PENDING rows, a worker starts them (max_concurrent_runs, run_timeout_seconds)
- [x] Cancel actually stops in-flight runs; queued runs can be cancelled before they start
- [x] Restart recovery: runs left mid-flight are failed and replayable; queued runs survive
- [x] Replay a run with the same input and the same workflow definition (snapshot), or against the latest
- [x] Builder Triggers panel, Console Replay button and source badges
- [ ] Multi-process workers (needs a row-level claim on PENDING runs)
- [ ] Replay from a failed step (see Execution Caching)
- [ ] Webhook rate limiting / signature verification

### Backend � Silent-Success Detection
- [x] Run evaluator: offline heuristics (empty output, warnings, shape drift, identical repeats) + optional Claude judgement
- [x] Auto-evaluates completed runs (fail-soft; off in evolve sandbox)
- [x] Human corrections (POST /runs/{id}/correction, approval rejections) and override-rate insight (GET /workflows/{id}/quality)
- [x] Console: quality score, reasons, Flag as wrong, override banner
- [x] Per-workflow override rates on Analytics page
- [x] Learns from corrections: flagged issues weigh more next time and are fed to Claude as examples
- [x] Claude judgement runs in a background thread; offline checks stay inline
- [ ] Judging things that need outside data (e.g. recipient tone) - needs an external data source

### Backend � Evolution Engine
- [x] Sandbox fitness (mock-only tools, in-memory DB): success rate without approval gates or failures
- [x] Mutations: cross-pollination patches + retry bumps
- [x] `POST /workflows/{id}/evolve` � scores variants; `apply=true` saves winner as a version with rationale
- [x] Multi-generation loop with crossover (union of survivors' ops) and mutation, parsimony penalty
- [x] Approval-gate removal mutation (opt-in via allow_gate_removal; flagged in results)
- [ ] Sandbox uses mock tools only; real tool behavior is not simulated

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
- [x] Server-Sent Events endpoint for run progress (GET /runs/{id}/stream; fixed: used a closed DB session and named events the client never received)
- [x] Streaming step updates from runner to frontend (POST /workflows/{id}/run/start returns the run id immediately; runner reports each node as it starts)
- [x] Live node highlighting on the builder canvas during execution (running / done / failed / waiting rings); Console shows the running node

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
