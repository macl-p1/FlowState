# Graph Report - OrchestrAI  (2026-10-01)

## Corpus Check
- 134 files · ~172,835 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .graphify-bak 1, .ini 1)

## Summary
- 1781 nodes · 3640 edges · 130 communities (82 shown, 48 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 350 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c1dfcd1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- implementations.py
- ToolResult
- api.ts
- TestPlannerAgent
- package.json
- api/quality.py
- generate_workflow
- compiler.py
- api/integrations.py
- IntegrationHandler
- api/triggers.py
- enqueue_run
- asyncio
- BuilderClient.tsx
- lucide-react
- console/page.tsx
- runner.py
- CustomTool
- tools/integrations.py
- FlowState Application
- Workflow Builder Page
- ToolRegistry
- client
- compilerOptions
- design-md-planner skill
- OrchestrAI Backend — Comprehensive Test Cases
- compute_diff
- VerifierAgent
- ApprovalService
- GenealogyService
- TestApiKeyAuth
- OrchestrAI Platform
- WorkflowCompiler
- Dashboard Page
- config.py
- Worker
- test_quality.py
- conftest.py
- custom_tools.py
- Tool Registry
- approvals.py
- test_jobs.py
- WorkflowModel
- workflow.py
- 1. API Endpoint Tests
- Anthropic Claude API
- WorkflowRunner Engine
- 10. Performance Tests
- graphify skill
- schemas/suggestions.py
- get_tool
- Next.js Frontend
- Landing Feature Sections
- FastAPI main.py Entry Point
- analytics/page.tsx
- WorkflowRunner
- models/custom_tool.py
- history/page.tsx
- TestInvalidWorkflows
- VersionHistoryPanel.tsx
- 5. Workflow Runner Tests
- PlannerAgent
- OrchestrAI — Run Instructions
- .run
- Workflow Compiler
- Frontend Pages
- cross_pollination.py
- Session
- Navigation Sidebar
- Dark Theme UI
- TestWorkflowAPI
- 6. Approval Service Tests
- What's Built
- planner.py
- tool.py
- Workflow
- 9. Security Tests
- TriggersPanel.tsx
- find_pattern_gaps
- apply_patch_to_workflow
- extract_patterns
- TestCompilerSequential
- TestCompilerEdgeCases
- 2. Schema Validation Tests
- CompiledWorkflow
- auth.py
- 4. Tool Execution Tests
- ExecutionStatus
- TestToolAPI
- TestApprovalQueries
- dashboard/page.tsx
- _run_verification_test
- AGENTS.md
- postcss.config.mjs
- Backend README
- File SVG Icon (Next.js)
- Globe SVG Icon (Next.js)
- Next.js Logo SVG
- Frontend README
- Node Status: Pending
- Node Status: Queued
- Universal Workflow Automation
- TestVerifierLLM
- replay_run
- test_schemas.py
- apply_suggestion
- TestApprovalCreation
- WorkflowInvalid
- compute_similarity
- get_suggestions
- models/__init__.py
- cron_next
- app/layout.tsx
- TestApprovalResolution
- TestApprovalAPI
- TestRunAPI

## God Nodes (most connected - your core abstractions)
1. `ToolResult` - 91 edges
2. `ExecutionStatus` - 53 edges
3. `WorkflowRunner` - 50 edges
4. `fetchWithAuth()` - 47 edges
5. `handleResponse()` - 45 edges
6. `ToolRegistry` - 41 edges
7. `WorkflowModel` - 40 edges
8. `Workflow` - 36 edges
9. `PlannerAgent` - 35 edges
10. `ApprovalService` - 29 edges

## Surprising Connections (you probably didn't know these)
- `TC-RUN-002: Happy Path — Branching Workflow (Onboarding)` --references--> `WorkflowRunner`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py
- `TC-SCH-009: ExecutionStatus Enum Contains All Required States` --references--> `ExecutionStatus`  [INFERRED]
  backend/test-cases.md → backend/app/schemas/execution.py
- `TC-SCH-010: StepStatus Enum Contains All Required States` --references--> `StepStatus`  [INFERRED]
  backend/test-cases.md → backend/app/schemas/execution.py
- `TC-API-016: Get Specific Tool Details` --references--> `send_email()`  [INFERRED]
  backend/test-cases.md → backend/app/tools/implementations.py
- `TC-EDGE-014: Empty Tool Inputs` --references--> `send_email()`  [INFERRED]
  backend/test-cases.md → backend/app/tools/implementations.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Dashboard KPI Metric Set** — frontend_screenshots_desktop_dashboard_kpi_cards, workflow_kpis, run_status_completed, run_status_running, run_status_pending, run_status_failed [EXTRACTED 0.95]
- **Agent Pipeline (Plan-Validate-Compile-Run-Verify)** — planner_agent, pydantic_schemas, compiler, runner_engine, verifier_agent [EXTRACTED 1.00]
- **Backend App Module Structure** — main_py, config_py, database_py, app_api, app_agents, app_engine, app_approval, app_tools [EXTRACTED 1.00]
- **Backend Tech Stack** — fastapi_backend, langgraph_engine, anthropic_claude, sqlalchemy_orm [EXTRACTED 1.00]
- **Customer Onboarding Demo Flow** — fetch_customers_node, parse_results_node, store_output_node, http_request_tool, transform_tool, database_query_tool [EXTRACTED 1.00]
- **Data Layer** — sqlalchemy_orm, sqlite_db, postgresql_db [EXTRACTED 1.00]
- **Demo Workflows** — invoice_workflow, onboarding_workflow, complaint_workflow [EXTRACTED 1.00]
- **design-md-planner skill system** — claude_skills_design_md_planner_skill_design_md_planner, claude_skills_design_md_planner_readme_design_md_planner, claude_skills_design_md_planner_assets_design_template_design_md_template, claude_skills_design_md_planner_assets_design_example_kiln_design_system, claude_skills_design_md_planner_references_anti_slop_anti_slop_catalog, claude_skills_design_md_planner_references_cli_design_md_cli, claude_skills_design_md_planner_references_color_craft_color_craft, claude_skills_design_md_planner_references_designmd_spec_design_md_format_spec, claude_skills_design_md_planner_references_style_directions_style_directions, claude_skills_design_md_planner_references_typography_typography_guide [EXTRACTED 1.00]
- **Docker Services** — docker_compose, postgresql_db, fastapi_backend, nextjs_frontend [EXTRACTED 1.00]
- **Execution Lifecycle (Load-Execute-Verify-Determine)** — runner_engine, tool_registry, verifier_agent, approval_system [EXTRACTED 1.00]
- **FlowState Application Across Devices** — frontend_screenshots_desktop_builder_page, frontend_screenshots_desktop_console_page, frontend_screenshots_desktop_dashboard_page, frontend_screenshots_desktop_history_page, frontend_screenshots_desktop_tools_page, frontend_screenshots_mobile_builder_page, frontend_screenshots_mobile_console_page, frontend_screenshots_mobile_dashboard_page, frontend_screenshots_mobile_history_page, frontend_screenshots_mobile_tools_page, frontend_screenshots_tablet_builder_page, frontend_screenshots_tablet_console_page, frontend_screenshots_tablet_dashboard_page, frontend_screenshots_tablet_history_page, frontend_screenshots_tablet_tools_page [EXTRACTED 1.00]
- **Frontend Tech Stack** — nextjs_frontend, react_flow, tailwind_css, framer_motion [EXTRACTED 1.00]
- **graphify skill system** — claude_skills_graphify_skill_graphify, claude_skills_graphify_references_add_watch_add_watch, claude_skills_graphify_references_exports_exports_benchmark, claude_skills_graphify_references_extraction_spec_extraction_spec, claude_skills_graphify_references_github_and_merge_github_merge, claude_skills_graphify_references_hooks_hooks, claude_skills_graphify_references_query_query_path_explain, claude_skills_graphify_references_transcribe_transcribe, claude_skills_graphify_references_update_update_cluster_only [EXTRACTED 1.00]
- **Landing Page Complete Structure** — landing_hero, landing_feature_sections, landing_cta, landing_footer [EXTRACTED 1.00]
- **Application Navigation System** — dashboard_nav, workflows_nav, console_nav, tools_nav, history_nav [EXTRACTED 1.00]
- **Workflow Node Types** — six_node_types [EXTRACTED 1.00]
- **Kiln design system concept cluster** — kiln_design_system, claude_skills_design_md_planner_assets_design_example_kiln_design_system, warm_analog_aesthetic, archival_institutional_aesthetic, ai_design_slop, oklch_color_space, google_design_md_linter, design_md_format_spec [INFERRED 0.90]

## Communities (130 total, 48 thin omitted)

### Community 0 - "implementations.py"
Cohesion: 0.04
Nodes (34): aggregate_metrics(), check_health(), classify_text(), conditional_router(), create_calendar_event(), create_invoice(), create_lead(), create_task() (+26 more)

### Community 1 - "ToolResult"
Cohesion: 0.13
Nodes (8): ToolResult, export_csv(), fan_in(), get_employee_info(), validate_invoice(), TC-TOOL-017: validate_invoice — Detects Large Amounts, TestToolResult, TestVerifierRuleBased

### Community 2 - "api.ts"
Cohesion: 0.07
Nodes (64): ConsoleClient(), ConsoleClientProps, getNodeState(), NODE_ICONS, NodeState, nodeStateStyles, statusLabel, statusStyles (+56 more)

### Community 3 - "TestPlannerAgent"
Cohesion: 0.23
Nodes (3): make_mock_client(), make_mock_client_with_sequence(), TestPlannerAgent

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (39): eslintConfig, dependencies, lucide-react, next, react, react-dom, @xyflow/react, devDependencies (+31 more)

### Community 5 - "api/quality.py"
Cohesion: 0.13
Nodes (10): _rate(), stats(), add_correction(), CorrectionRequest, get_evaluation(), get_quality(), serialize_evaluation(), workflow_quality() (+2 more)

### Community 6 - "generate_workflow"
Cohesion: 0.15
Nodes (10): delete_workflow(), generate_workflow(), GenerateRequest, get_workflow(), list_workflows(), run_workflow(), RunRequest, save_workflow_direct() (+2 more)

### Community 7 - "compiler.py"
Cohesion: 0.13
Nodes (6): _make_node_executor(), execute(), StepExecution, _eval_node(), safe_eval(), SafeEvalError

### Community 8 - "api/integrations.py"
Cohesion: 0.11
Nodes (11): get_integration(), _get_tool_or_404(), list_integrations(), remove_integration(), set_integration(), _tool_to_response(), verify_integration(), CustomToolResponse (+3 more)

### Community 10 - "api/triggers.py"
Cohesion: 0.19
Nodes (9): create_trigger(), delete_trigger(), list_triggers(), _serialize(), TriggerCreate, TriggerUpdate, update_trigger(), next_fire() (+1 more)

### Community 11 - "enqueue_run"
Cohesion: 0.24
Nodes (12): enqueue_run(), recover_interrupted(), slow(), _status(), test_cancel_while_queued_is_never_started(), test_concurrency_cap_and_cancel(), test_enqueue_rejects_unrunnable_workflow(), test_queued_run_executes_with_provenance() (+4 more)

### Community 13 - "BuilderClient.tsx"
Cohesion: 0.11
Nodes (24): BuilderClient(), BuilderInner(), defaultEdges, defaultNodes, LabeledEdgeMemo, snap(), toBackendGraph(), toFlowGraph() (+16 more)

### Community 14 - "lucide-react"
Cohesion: 0.12
Nodes (20): nextConfig, AppLayout(), demoSteps, features, LandingPage(), RunIdSpan(), templates, AppSidebar() (+12 more)

### Community 15 - "console/page.tsx"
Cohesion: 0.50
Nodes (3): dynamic, Page(), PageProps

### Community 16 - "runner.py"
Cohesion: 0.11
Nodes (5): get_db(), get_db_context(), get_worker(), health(), lifespan()

### Community 17 - "CustomTool"
Cohesion: 0.17
Nodes (9): create_custom_tool(), delete_custom_tool(), get_custom_tool(), list_all_tools(), list_custom_tools(), list_custom_tools_by_type(), register_custom_tool(), _tool_to_response() (+1 more)

### Community 18 - "tools/integrations.py"
Cohesion: 0.14
Nodes (3): _mask(), _mask_credentials(), TestCredentialMasking

### Community 19 - "FlowState Application"
Cohesion: 0.15
Nodes (17): FlowState Application, FlowState Logo, Vercel Logo, Workflow Builder (Mobile), Execution Console (Mobile), Dashboard (Mobile), Run History (Mobile), Landing/Root Page (Mobile) (+9 more)

### Community 20 - "Workflow Builder Page"
Cohesion: 0.16
Nodes (19): Approval UI, Canvas Grid Background, Customer Onboarding Workflow, Fetch Customers Node, Workflow Builder Page, Console Output Log, Execution Console Page, Glassmorphism Design System (+11 more)

### Community 21 - "ToolRegistry"
Cohesion: 0.05
Nodes (20): ToolAlreadyRegisteredError, ToolRegistry, UnknownToolError, 8. Edge Cases & Stress Tests, TC-EDGE-001: Very Large Workflow (50+ Nodes), TC-EDGE-003: Missing Tool Handler at Runtime, TC-EDGE-004: Node Execution Timeout, TC-EDGE-005: Malformed Context Data (+12 more)

### Community 22 - "client"
Cohesion: 0.25
Nodes (4): auth_client(), client(), override_get_db(), setup_test_db()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "design-md-planner skill"
Cohesion: 0.33
Nodes (12): Archival Institutional aesthetic direction, Kiln — worked DESIGN.md example, DESIGN.md template skeleton, design-md-planner README, cli.md — @google/design.md CLI reference, designmd-spec.md — DESIGN.md format spec, design-md-planner skill, DESIGN.md format specification (+4 more)

### Community 25 - "OrchestrAI Backend — Comprehensive Test Cases"
Cohesion: 0.17
Nodes (11): 7. Integration / End-to-End Tests, OrchestrAI Backend — Comprehensive Test Cases, Table of Contents, TC-E2E-001: Full Invoice Processing Workflow, TC-E2E-002: Full Employee Onboarding Workflow, TC-E2E-003: Full Customer Support Workflow, TC-E2E-004: Workflow With Retry on Failure, TC-E2E-005: Workflow With Multiple Condition Nodes (+3 more)

### Community 26 - "compute_diff"
Cohesion: 0.11
Nodes (5): compute_diff(), DiffResult, _edge_condition_key(), _serialize(), TestComputeDiff

### Community 27 - "VerifierAgent"
Cohesion: 0.15
Nodes (6): VerificationResult, VerifierAgent, TC-AGT-016: Verifier Rule-Based — Success Verdict, TC-AGT-020: Verifier LLM-Based Verification With Mock, TC-AGT-021: Verifier Falls Back to Rule-Based on LLM Error, verifier()

### Community 28 - "ApprovalService"
Cohesion: 0.10
Nodes (9): ApprovalService, ApprovalRequestModel, TC-APR-001: Create Pending Approval Request, TC-APR-009: Get Existing Approval by ID, TC-APR-013: Approval Persists Across Session Close/Reopen, TC-APR-014: Create Approval With Default Parameters, create_pending_approval(), approval_service() (+1 more)

### Community 29 - "GenealogyService"
Cohesion: 0.09
Nodes (12): branch_workflow(), BranchWorkflowRequest, evolve_workflow(), EvolveRequest, get_history(), get_lineage(), get_version(), save_version() (+4 more)

### Community 31 - "OrchestrAI Platform"
Cohesion: 0.14
Nodes (12): Backend Architecture Plan, 21-Session Build Plan, Customer Complaint Workflow, Docker Compose, FlowPilot (Product Name), FlowState (Presentation Name), Graphify Knowledge Graph, Invoice Processing Workflow (+4 more)

### Community 32 - "WorkflowCompiler"
Cohesion: 0.10
Nodes (11): CompilationError, WorkflowCompiler, TC-AGT-010: Compiler Rejects Workflow Without Trigger, TC-AGT-011: Compiler Rejects Workflow With Multiple Triggers, TC-AGT-012: Compiler Handles Condition Nodes with True/False Branches, TC-AGT-013: Compiler Handles Approval Nodes, TC-AGT-014: Compiler Handles Retry Configuration on Nodes, TC-AGT-015: Compiler Minimal Workflow (Trigger + End Only) (+3 more)

### Community 33 - "Dashboard Page"
Cohesion: 0.14
Nodes (14): Daily Report Generator Workflow, Dashboard KPI Cards, Dashboard Page, Run History Page, Invoice Processor Workflow, Run History Table, Run Status: Completed, Run Status: Failed (+6 more)

### Community 34 - "config.py"
Cohesion: 0.18
Nodes (3): Config, Settings, main()

### Community 36 - "test_quality.py"
Cohesion: 0.39
Nodes (8): evaluate_run(), _cleanup(), _seed(), test_clean_run_is_ok(), test_delete_run_and_analytics_workflows(), test_flagged_issue_weighs_more_next_time(), test_heuristics_flag_empty_drift_and_warnings(), test_override_rate_insight_and_reject_correction()

### Community 37 - "conftest.py"
Cohesion: 0.12
Nodes (10): db_engine(), db_session(), persisted_invoice_workflow(), persisted_onboarding_workflow(), registry_with_context(), runner(), sample_complaint_workflow(), sample_invoice_workflow() (+2 more)

### Community 38 - "custom_tools.py"
Cohesion: 0.23
Nodes (8): list_categories(), _type_icon(), verify_custom_tool(), CustomToolCreate, CustomToolUpdate, ToolCategory, ToolVerifyRequest, ToolVerifyResponse

### Community 39 - "Tool Registry"
Cohesion: 0.26
Nodes (12): Tools Module (Registry + Implementations), Database Query Tool, Tools Browser, Tools Explorer Page, HTTP Request Tool, Mock Tool Implementations, Permission Levels, Rate Limiter Tool (+4 more)

### Community 40 - "approvals.py"
Cohesion: 0.20
Nodes (6): approve_request(), ApproveRequest, list_approvals(), reject_request(), RejectRequest, record_correction()

### Community 41 - "test_jobs.py"
Cohesion: 0.31
Nodes (8): RunMetaModel, _cleanup(), _create_wf(), db(), test_replay_uses_original_definition_unless_latest(), test_trigger_validation(), test_webhook_trigger_end_to_end(), _wait_done()

### Community 42 - "WorkflowModel"
Cohesion: 0.08
Nodes (17): apply_ops(), candidate_ops(), evolve(), score(), fitness(), _remove_node(), _sandbox_db(), SandboxRegistry (+9 more)

### Community 43 - "workflow.py"
Cohesion: 0.19
Nodes (11): ActionNode, ApprovalNode, ConditionNode, Edge, EndNode, NodeType, PermissionLevel, Trigger (+3 more)

### Community 44 - "1. API Endpoint Tests"
Cohesion: 0.12
Nodes (17): 1. API Endpoint Tests, TC-API-001: Health Check Returns Service Status, TC-API-002: Generate Workflow From Natural Language Prompt, TC-API-003: List Workflows — Empty State, TC-API-004: List Workflows — Multiple Workflows Sorted by Recency, TC-API-005: Get Specific Workflow, TC-API-006: Run Workflow — Happy Path, TC-API-007: Run Workflow — Not Found (+9 more)

### Community 45 - "Anthropic Claude API"
Cohesion: 0.18
Nodes (9): Anthropic Claude API, Python Requirements, Backend Tests, LangGraph (from LangChain), LangGraph Engine, Natural Language Interface, Planner Agent, pytest Test Suite (+1 more)

### Community 46 - "WorkflowRunner Engine"
Cohesion: 0.22
Nodes (10): API Route Handlers, Approval System (HITL), Human-in-the-Loop, Step-Level Observability, Retry Mechanism, WorkflowRunner Engine, Step Persistence, Template Variable Substitution (+2 more)

### Community 47 - "10. Performance Tests"
Cohesion: 0.17
Nodes (10): 10. Performance Tests, TC-APR-008: List Pending Returns Only Pending, TC-PERF-001: Workflow Compilation Time for Large Graphs, TC-PERF-002: Concurrent Execution Limits, TC-PERF-003: Database Query Optimization for List Runs, TC-PERF-004: Memory Usage With Many Concurrent Workflows, TC-PERF-005: LangGraph Compilation Caching, TC-PERF-006: API Response Time Under Load (+2 more)

### Community 48 - "graphify skill"
Cohesion: 0.20
Nodes (11): OrchestrAI CLAUDE.md, add-watch.md — URL ingest and folder watch reference, exports.md — extra exports and benchmark reference, extraction-spec.md — extraction subagent prompt spec, github-and-merge.md — GitHub clone and cross-repo merge reference, hooks.md — commit hook and CLAUDE.md integration reference, query.md — query, path, explain reference, transcribe.md — video/audio transcription reference (+3 more)

### Community 49 - "schemas/suggestions.py"
Cohesion: 0.28
Nodes (3): ApplyPatchRequest, SuggestionResponse, SuggestionsResponse

### Community 51 - "Next.js Frontend"
Cohesion: 0.20
Nodes (10): Deep Space Color Palette, Control Room Glass Design System, Framer Motion, Glassmorphism UI, JetBrains Mono Font, Next.js Frontend, Phosphor Cyan Accent, React Flow (+2 more)

### Community 52 - "Landing Feature Sections"
Cohesion: 0.22
Nodes (9): Conditional Branching, Landing Feature Sections, No Drag-and-Drop Design, No DSL Required Design, Workflow Execution Observability, Plain Language Workflow Definition, Retry Logic, Step-by-Step Execution Graph (+1 more)

### Community 53 - "FastAPI main.py Entry Point"
Cohesion: 0.29
Nodes (8): REST API Endpoints, Agent Layer (Planner/Compiler/Verifier), Approval Module (HITL), Engine Layer (Runner), Config.py (Settings), CORS Middleware, FastAPI Backend, FastAPI main.py Entry Point

### Community 54 - "analytics/page.tsx"
Cohesion: 0.53
Nodes (5): AnalyticsPage(), pct(), Stat(), AnalyticsStats, getAnalyticsStats()

### Community 55 - "WorkflowRunner"
Cohesion: 0.14
Nodes (13): WorkflowRunner, TC-RUN-001: Happy Path — Simple Linear Workflow, TC-RUN-003: Approval Pause and Resume Flow, test_runner_cancel_running_workflow(), test_runner_context_passed_through(), test_runner_happy_path_simple_workflow(), test_runner_multiple_runs_no_state_leakage(), test_runner_onboarding_workflow() (+5 more)

### Community 56 - "models/custom_tool.py"
Cohesion: 0.22
Nodes (3): update_custom_tool(), ToolStatus, ToolType

### Community 57 - "history/page.tsx"
Cohesion: 0.24
Nodes (10): HistoryPage(), HistoryRow, STATUS_BUCKET, statusDot, statusLabel, statusStyles, toRow(), deleteRun() (+2 more)

### Community 59 - "VersionHistoryPanel.tsx"
Cohesion: 0.16
Nodes (19): EvolvePanelProps, PATTERN_COLORS, SuggestionCard(), SuggestionsPanel(), SuggestionsPanelProps, CHANGE_TYPE_COLORS, ChangeTypeBadge(), formatTime() (+11 more)

### Community 60 - "5. Workflow Runner Tests"
Cohesion: 0.12
Nodes (19): RunnerError, WorkflowNotFoundError, 5. Workflow Runner Tests, TC-E2E-010: Database Transaction Rollback on Runner Failure, TC-RUN-002: Happy Path — Branching Workflow (Onboarding), TC-RUN-004: Approval Rejection Cancels Workflow, TC-RUN-005: Cancel Running Workflow, TC-RUN-006: Context Propagation Between Nodes (+11 more)

### Community 61 - "PlannerAgent"
Cohesion: 0.13
Nodes (16): PlannerAgent, 3. Agent Tests — Planner, Compiler, Verifier, TC-AGT-001: Planner Generates Valid Invoice Workflow From Prompt, TC-AGT-002: Planner Handles Malformed LLM Output, TC-AGT-003: Planner Retry Logic — Repairs After First Failure, TC-AGT-004: Planner Exhausts Retries and Returns Error, TC-AGT-005: Planner Rejects Unknown Tool References, TC-AGT-006: Planner Metadata Extraction (+8 more)

### Community 62 - "OrchestrAI — Run Instructions"
Cohesion: 0.13
Nodes (14): 1. Clone and enter the project, 2. Backend, 3. Frontend, API Endpoints, Backend, Common Issues, Default Data, Frontend (+6 more)

### Community 64 - "Workflow Compiler"
Cohesion: 0.29
Nodes (4): Branching Logic, Workflow Compiler, Pydantic Schemas, Six Node Types

### Community 65 - "Frontend Pages"
Cohesion: 0.29
Nodes (7): Dashboard, Frontend Pages, Landing Page, Run Console, Tools Explorer, Wireframes, Workflow Builder

### Community 66 - "cross_pollination.py"
Cohesion: 0.22
Nodes (4): enrich_with_llm(), _get_condition_node_ids(), _get_node_by_id(), _summarize_workflow()

### Community 67 - "Session"
Cohesion: 0.19
Nodes (9): delete_run(), get_run(), list_runs(), _meta(), _serialize_exec(), _serialize_step(), stream_run(), event_generator() (+1 more)

### Community 68 - "Navigation Sidebar"
Cohesion: 0.33
Nodes (6): Console Navigation, Dashboard Navigation, History Navigation, Navigation Sidebar, Tools Navigation, Workflows Navigation

### Community 69 - "Dark Theme UI"
Cohesion: 0.33
Nodes (6): Dark Theme UI, Window/Frame Icon, Landing/Root Page, Landing CTA Section, Landing Page Hero Section, Live Execution Replay

### Community 71 - "6. Approval Service Tests"
Cohesion: 0.14
Nodes (12): ApprovalAlreadyResolvedError, ApprovalNotFoundError, 6. Approval Service Tests, TC-APR-002: Approve Sets All Required Fields, TC-APR-003: Reject Sets All Required Fields, TC-APR-004: Double-Approve Raises Error, TC-APR-005: Double-Reject Raises Error, TC-APR-006: Approve Already-Rejected Approval Raises Error (+4 more)

### Community 72 - "What's Built"
Cohesion: 0.12
Nodes (15): 1. Execution Caching / Resumability, 2. Workflow Templates Marketplace, 3. Real-time Execution Console, 4. Multi-env Deployment, 5. Observability & Analytics, Backend — Core Engine, Backend — Cross-Pollination, Backend � Evolution Engine (+7 more)

### Community 73 - "planner.py"
Cohesion: 0.13
Nodes (4): PlanningError, PlanningResult, TC-EDGE-007: Empty Workflow Prompt to Planner, mock_registry()

### Community 74 - "tool.py"
Cohesion: 0.26
Nodes (3): Tool, ToolCall, TestToolPermissions

### Community 75 - "Workflow"
Cohesion: 0.12
Nodes (5): Workflow, workflow_from_dict(), workflow_to_dict(), TC-SCH-014: Workflow Serialization Round-Trip, TestValidWorkflows

### Community 76 - "9. Security Tests"
Cohesion: 0.20
Nodes (10): 9. Security Tests, TC-SEC-002: XSS in Workflow Names and Descriptions, TC-SEC-003: Permission Escalation via Approval, TC-SEC-004: Unauthorized Cancellation of Another User's Execution, TC-SEC-005: Environment Variable Exposure, TC-SEC-006: Code Injection via Condition Expression (eval), TC-SEC-007: Oversized Payload DoS Protection, TC-SEC-008: Tool Input Schema Validation (+2 more)

### Community 77 - "TriggersPanel.tsx"
Cohesion: 0.29
Nodes (10): describe(), PRESETS, TriggersPanel(), TriggersPanelProps, createTrigger(), deleteTrigger(), listTriggers(), setTriggerEnabled() (+2 more)

### Community 78 - "find_pattern_gaps"
Cohesion: 0.24
Nodes (4): _build_suggestion(), _finalize_suggestion(), find_pattern_gaps(), TestPatternGaps

### Community 79 - "apply_patch_to_workflow"
Cohesion: 0.32
Nodes (4): apply_patch_to_workflow(), _find_first_by_type(), _find_node(), TestApplyPatch

### Community 86 - "2. Schema Validation Tests"
Cohesion: 0.14
Nodes (15): 2. Schema Validation Tests, TC-SCH-001: Valid Invoice Processing Workflow Passes Validation, TC-SCH-002: Valid Employee Onboarding Workflow Passes Validation, TC-SCH-003: Missing Trigger Node Rejected, TC-SCH-004: Multiple Trigger Nodes Rejected, TC-SCH-005: Duplicate Node IDs Rejected, TC-SCH-006: Orphaned Edge Source Rejected, TC-SCH-007: Orphaned Edge Target Rejected (+7 more)

### Community 89 - "4. Tool Execution Tests"
Cohesion: 0.07
Nodes (30): create_ticket(), extract_invoice_data(), process_payment(), request_human_approval(), search_database(), send_email(), send_slack_message(), update_database() (+22 more)

### Community 90 - "ExecutionStatus"
Cohesion: 0.13
Nodes (13): heuristic_evaluate(), _keys(), learned_corrections(), llm_evaluate(), _previous_runs(), _refine_with_llm(), _verdict(), StepExecutionModel (+5 more)

### Community 93 - "dashboard/page.tsx"
Cohesion: 0.31
Nodes (8): DashboardPage(), statusLabel, statusStyles, deleteWorkflow(), listWorkflows(), runWorkflow(), WorkflowDetail, WorkflowListItem

### Community 94 - "_run_verification_test"
Cohesion: 0.38
Nodes (3): _build_verification_inputs(), _run_verification_test(), _validate_config_shape()

### Community 117 - "replay_run"
Cohesion: 0.29
Nodes (3): cancel_run(), replay_run(), ReplayRequest

### Community 123 - "get_suggestions"
Cohesion: 0.48
Nodes (3): get_suggestions(), _make_workflow(), TestGetSuggestions

### Community 124 - "models/__init__.py"
Cohesion: 0.10
Nodes (7): _version_to_dict(), WorkflowBranchModel, WorkflowVersionModel, db(), db(), Database.py (SQLAlchemy), SQLAlchemy ORM

### Community 125 - "cron_next"
Cohesion: 0.33
Nodes (4): _cron_field(), cron_next(), parse_cron(), test_cron_next()

### Community 126 - "app/layout.tsx"
Cohesion: 0.33
Nodes (3): instrumentSans, jetbrainsMono, metadata

## Knowledge Gaps
- **298 isolated node(s):** `Config`, `eslintConfig`, `nextConfig`, `name`, `version` (+293 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 790 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQLAlchemy ORM` connect `models/__init__.py` to `api/quality.py`, `custom_tools.py`, `conftest.py`, `approvals.py`, `api/integrations.py`, `WorkflowModel`, `api/triggers.py`, `Anthropic Claude API`, `WorkflowRunner Engine`, `runner.py`, `ExecutionStatus`, `OrchestrAI Platform`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `ToolResult` connect `ToolResult` to `implementations.py`, `conftest.py`, `IntegrationHandler`, `tool.py`, `WorkflowModel`, `asyncio`, `runner.py`, `tools/integrations.py`, `TestVerifierLLM`, `ToolRegistry`, `test_schemas.py`, `WorkflowRunner`, `4. Tool Execution Tests`, `VerifierAgent`, `.run`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `Python Requirements` connect `Anthropic Claude API` to `models/__init__.py`, `FastAPI main.py Entry Point`, `OrchestrAI Platform`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ToolResult` (e.g. with `VerifierAgent` and `WorkflowRunner`) actually correct?**
  _`ToolResult` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `ExecutionStatus` (e.g. with `_make_node_executor()` and `evaluate_run()`) actually correct?**
  _`ExecutionStatus` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `WorkflowRunner` (e.g. with `approve_request()` and `reject_request()`) actually correct?**
  _`WorkflowRunner` has 31 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `eslintConfig`, `nextConfig` to the rest of the system?**
  _298 weakly-connected nodes found - possible documentation gaps or missing edges._