# Graph Report - OrchestrAI  (2026-10-01)

## Corpus Check
- 137 files · ~178,182 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .graphify-bak 1, .ini 1)

## Summary
- 1858 nodes · 3919 edges · 126 communities (83 shown, 43 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 367 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b485291b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- implementations.py
- VerifierAgent
- fetchWithAuth
- TestPlannerAgent
- package.json
- WorkflowNotFoundError
- workflows.py
- compiler.py
- api/integrations.py
- IntegrationHandler
- jobs.py
- test_jobs.py
- asyncio
- BuilderClient.tsx
- lucide-react
- ConsoleClient.tsx
- Settings
- CustomTool
- tools/integrations.py
- FlowState Application
- Workflow Builder Page
- 2. Schema Validation Tests
- history_suggestions
- compilerOptions
- design-md-planner skill
- 7. Integration / End-to-End Tests
- compute_diff
- apply_patch_to_workflow
- ToolRegistry
- api/genealogy.py
- TestApiKeyAuth
- OrchestrAI Platform
- WorkflowCompiler
- Dashboard Page
- Workflow
- ToolResult
- GenealogyService
- fixture
- test_history.py
- Tool Registry
- custom_tools.py
- TestApprovalResolution
- WorkflowModel
- workflow.py
- 1. API Endpoint Tests
- Anthropic Claude API
- WorkflowRunner Engine
- ApprovalRequestModel
- graphify skill
- extract_patterns
- OrchestrAI Backend — Comprehensive Test Cases
- Next.js Frontend
- Landing Feature Sections
- FastAPI main.py Entry Point
- ApprovalNotFoundError
- registry.py
- api/quality.py
- history/page.tsx
- graph.py
- EvolvePanel.tsx
- 5. Workflow Runner Tests
- PlannerAgent
- OrchestrAI — Run Instructions
- TestApprovalQueries
- Workflow Compiler
- Frontend Pages
- get_suggestions
- reject_request
- Navigation Sidebar
- Dark Theme UI
- TestWorkflowAPI
- 6. Approval Service Tests
- What's Built
- TestApprovalCreation
- cross_pollination.py
- 9. Security Tests
- TriggersPanel.tsx
- graph_key
- ApprovalService
- typing
- runs.py
- WorkflowRunner
- models/custom_tool.py
- VersionHistoryPanel.tsx
- 4. Tool Execution Tests
- TestToolAPI
- api.ts
- _version_to_dict
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
- main.py
- test_compiler.py
- DiffResult
- genealogy/service.py
- ExecutionStatus
- test_cross_pollination.py
- planner.py
- TestVerifierLLM
- app/layout.tsx
- TestInvalidWorkflows
- TestApprovalAPI
- TestRunAPI
- get_tool
- .list_pending

## God Nodes (most connected - your core abstractions)
1. `ToolResult` - 91 edges
2. `ExecutionStatus` - 59 edges
3. `WorkflowRunner` - 50 edges
4. `fetchWithAuth()` - 48 edges
5. `WorkflowModel` - 46 edges
6. `handleResponse()` - 46 edges
7. `ToolRegistry` - 41 edges
8. `Workflow` - 38 edges
9. `PlannerAgent` - 35 edges
10. `GenealogyService` - 33 edges

## Surprising Connections (you probably didn't know these)
- `TC-APR-014: Create Approval With Default Parameters` --references--> `ApprovalService`  [INFERRED]
  backend/test-cases.md → backend/app/approval/service.py
- `TC-RUN-009: Error Handling — Unknown Workflow` --references--> `WorkflowNotFoundError`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py
- `TC-RUN-013: Resume Non-Existent Execution` --references--> `WorkflowNotFoundError`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py
- `TC-RUN-014: Cancel Non-Existent Execution` --references--> `WorkflowNotFoundError`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py
- `TC-RUN-001: Happy Path — Simple Linear Workflow` --references--> `WorkflowRunner`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py

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

## Communities (126 total, 43 thin omitted)

### Community 0 - "implementations.py"
Cohesion: 0.04
Nodes (34): aggregate_metrics(), check_health(), classify_text(), conditional_router(), create_calendar_event(), create_invoice(), create_lead(), create_task() (+26 more)

### Community 1 - "VerifierAgent"
Cohesion: 0.15
Nodes (6): VerificationResult, VerifierAgent, TC-AGT-016: Verifier Rule-Based — Success Verdict, TC-AGT-020: Verifier LLM-Based Verification With Mock, TC-AGT-021: Verifier Falls Back to Rule-Based on LLM Error, verifier()

### Community 2 - "fetchWithAuth"
Cohesion: 0.12
Nodes (38): ConsoleClient(), FormData, STATUS_LABEL, STATUS_STYLES, TOOL_TYPE_LABELS, TOOL_TYPES, ToolsPage(), TYPE_ICONS (+30 more)

### Community 3 - "TestPlannerAgent"
Cohesion: 0.23
Nodes (3): make_mock_client(), make_mock_client_with_sequence(), TestPlannerAgent

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (38): eslintConfig, dependencies, lucide-react, next, react, react-dom, @xyflow/react, devDependencies (+30 more)

### Community 5 - "WorkflowNotFoundError"
Cohesion: 0.11
Nodes (7): RunnerError, WorkflowNotFoundError, _persist_steps(), StepExecution, WorkflowExecution, TC-E2E-010: Database Transaction Rollback on Runner Failure, TC-RUN-012: Resume From Non-Approval State Raises Error

### Community 6 - "workflows.py"
Cohesion: 0.18
Nodes (10): delete_workflow(), generate_workflow(), GenerateRequest, get_workflow(), list_workflows(), run_workflow(), RunRequest, save_workflow_direct() (+2 more)

### Community 7 - "compiler.py"
Cohesion: 0.15
Nodes (5): _make_node_executor(), execute(), _eval_node(), safe_eval(), SafeEvalError

### Community 8 - "api/integrations.py"
Cohesion: 0.12
Nodes (11): get_integration(), _get_tool_or_404(), list_integrations(), remove_integration(), set_integration(), _tool_to_response(), verify_integration(), CustomToolResponse (+3 more)

### Community 10 - "jobs.py"
Cohesion: 0.10
Nodes (16): create_trigger(), delete_trigger(), fire_webhook(), list_triggers(), _serialize(), TriggerCreate, TriggerUpdate, update_trigger() (+8 more)

### Community 11 - "test_jobs.py"
Cohesion: 0.17
Nodes (20): enqueue_run(), recover_interrupted(), RunMetaModel, _cleanup(), _create_wf(), db(), slow(), _status() (+12 more)

### Community 13 - "BuilderClient.tsx"
Cohesion: 0.10
Nodes (28): BuilderClient(), BuilderInner(), defaultEdges, defaultNodes, LabeledEdgeMemo, snap(), toBackendGraph(), toFlowGraph() (+20 more)

### Community 14 - "lucide-react"
Cohesion: 0.16
Nodes (13): nextConfig, AppLayout(), demoSteps, features, LandingPage(), RunIdSpan(), templates, AppSidebar() (+5 more)

### Community 15 - "ConsoleClient.tsx"
Cohesion: 0.12
Nodes (15): ConsoleClientProps, getNodeState(), NODE_ICONS, NodeState, nodeStateStyles, statusLabel, statusStyles, dynamic (+7 more)

### Community 17 - "CustomTool"
Cohesion: 0.14
Nodes (10): create_custom_tool(), delete_custom_tool(), get_custom_tool(), list_all_tools(), list_custom_tools(), list_custom_tools_by_type(), register_custom_tool(), _tool_to_response() (+2 more)

### Community 18 - "tools/integrations.py"
Cohesion: 0.14
Nodes (3): _mask(), _mask_credentials(), TestCredentialMasking

### Community 19 - "FlowState Application"
Cohesion: 0.15
Nodes (17): FlowState Application, FlowState Logo, Vercel Logo, Workflow Builder (Mobile), Execution Console (Mobile), Dashboard (Mobile), Run History (Mobile), Landing/Root Page (Mobile) (+9 more)

### Community 20 - "Workflow Builder Page"
Cohesion: 0.16
Nodes (19): Approval UI, Canvas Grid Background, Customer Onboarding Workflow, Fetch Customers Node, Workflow Builder Page, Console Output Log, Execution Console Page, Glassmorphism Design System (+11 more)

### Community 21 - "2. Schema Validation Tests"
Cohesion: 0.14
Nodes (15): 2. Schema Validation Tests, TC-SCH-001: Valid Invoice Processing Workflow Passes Validation, TC-SCH-002: Valid Employee Onboarding Workflow Passes Validation, TC-SCH-003: Missing Trigger Node Rejected, TC-SCH-004: Multiple Trigger Nodes Rejected, TC-SCH-005: Duplicate Node IDs Rejected, TC-SCH-006: Orphaned Edge Source Rejected, TC-SCH-007: Orphaned Edge Target Rejected (+7 more)

### Community 22 - "history_suggestions"
Cohesion: 0.23
Nodes (8): event_evidence(), _evidence_text(), _finish(), history_suggestions(), pattern_timeline(), _side(), version_outcomes(), test_runs_attributed_by_snapshot_then_by_time()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "design-md-planner skill"
Cohesion: 0.33
Nodes (12): Archival Institutional aesthetic direction, Kiln — worked DESIGN.md example, DESIGN.md template skeleton, design-md-planner README, cli.md — @google/design.md CLI reference, designmd-spec.md — DESIGN.md format spec, design-md-planner skill, DESIGN.md format specification (+4 more)

### Community 25 - "7. Integration / End-to-End Tests"
Cohesion: 0.22
Nodes (9): 7. Integration / End-to-End Tests, TC-E2E-001: Full Invoice Processing Workflow, TC-E2E-002: Full Employee Onboarding Workflow, TC-E2E-003: Full Customer Support Workflow, TC-E2E-004: Workflow With Retry on Failure, TC-E2E-005: Workflow With Multiple Condition Nodes, TC-E2E-006: Concurrent Workflow Executions, TC-E2E-007: Workflow End-to-End With Approval Rejection (+1 more)

### Community 26 - "compute_diff"
Cohesion: 0.18
Nodes (4): compute_diff(), _edge_condition_key(), _serialize(), TestComputeDiff

### Community 27 - "apply_patch_to_workflow"
Cohesion: 0.15
Nodes (7): _anchor_refs(), apply_patch_to_workflow(), ref(), _build_suggestion(), PatchError, TestApplyPatch, test_every_suggestion_patch_applies_cleanly_or_refuses()

### Community 28 - "ToolRegistry"
Cohesion: 0.05
Nodes (21): get_db_context(), ToolAlreadyRegisteredError, ToolRegistry, UnknownToolError, 8. Edge Cases & Stress Tests, TC-EDGE-001: Very Large Workflow (50+ Nodes), TC-EDGE-003: Missing Tool Handler at Runtime, TC-EDGE-004: Node Execution Timeout (+13 more)

### Community 29 - "api/genealogy.py"
Cohesion: 0.15
Nodes (11): branch_workflow(), BranchWorkflowRequest, evolve_workflow(), EvolveRequest, get_history(), get_lineage(), get_version(), restore_version() (+3 more)

### Community 31 - "OrchestrAI Platform"
Cohesion: 0.14
Nodes (12): Backend Architecture Plan, 21-Session Build Plan, Customer Complaint Workflow, Docker Compose, FlowPilot (Product Name), FlowState (Presentation Name), Graphify Knowledge Graph, Invoice Processing Workflow (+4 more)

### Community 32 - "WorkflowCompiler"
Cohesion: 0.09
Nodes (11): CompilationError, CompiledWorkflow, WorkflowCompiler, TC-AGT-009: Compiler Builds StateGraph for Linear Workflow, TC-AGT-010: Compiler Rejects Workflow Without Trigger, TC-AGT-011: Compiler Rejects Workflow With Multiple Triggers, TC-AGT-012: Compiler Handles Condition Nodes with True/False Branches, TC-AGT-013: Compiler Handles Approval Nodes (+3 more)

### Community 33 - "Dashboard Page"
Cohesion: 0.14
Nodes (14): Daily Report Generator Workflow, Dashboard KPI Cards, Dashboard Page, Run History Page, Invoice Processor Workflow, Run History Table, Run Status: Completed, Run Status: Failed (+6 more)

### Community 34 - "Workflow"
Cohesion: 0.12
Nodes (5): Workflow, workflow_from_dict(), workflow_to_dict(), TC-SCH-014: Workflow Serialization Round-Trip, TestValidWorkflows

### Community 35 - "ToolResult"
Cohesion: 0.12
Nodes (7): ToolResult, generate_content(), read_file(), update_task_status(), TestExecutionStatuses, TestToolResult, TestVerifierRuleBased

### Community 36 - "GenealogyService"
Cohesion: 0.33
Nodes (3): GenealogyService, _make_workflow(), TestGenealogyService

### Community 37 - "fixture"
Cohesion: 0.10
Nodes (10): db_engine(), db_session(), persisted_invoice_workflow(), persisted_onboarding_workflow(), registry_with_context(), runner(), sample_complaint_workflow(), sample_invoice_workflow() (+2 more)

### Community 38 - "test_history.py"
Cohesion: 0.21
Nodes (17): _cleanup(), db(), _no_llm(), _runs(), test_api_save_keeps_baseline_and_skips_noop(), test_applying_a_suggestion_is_versioned(), test_branch_records_parent_in_metadata(), test_history_evidence_uses_this_workflows_precise_target() (+9 more)

### Community 39 - "Tool Registry"
Cohesion: 0.26
Nodes (12): Tools Module (Registry + Implementations), Database Query Tool, Tools Browser, Tools Explorer Page, HTTP Request Tool, Mock Tool Implementations, Permission Levels, Rate Limiter Tool (+4 more)

### Community 40 - "custom_tools.py"
Cohesion: 0.15
Nodes (12): _build_verification_inputs(), list_categories(), _run_verification_test(), _type_icon(), _validate_config_shape(), verify_custom_tool(), ToolStatus, CustomToolCreate (+4 more)

### Community 42 - "WorkflowModel"
Cohesion: 0.05
Nodes (34): evaluate_run(), heuristic_evaluate(), _keys(), learned_corrections(), llm_evaluate(), _previous_runs(), _refine_with_llm(), _verdict() (+26 more)

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

### Community 47 - "ApprovalRequestModel"
Cohesion: 0.18
Nodes (4): ApprovalRequestModel, TC-APR-001: Create Pending Approval Request, TC-APR-009: Get Existing Approval by ID, create_pending_approval()

### Community 48 - "graphify skill"
Cohesion: 0.20
Nodes (11): OrchestrAI CLAUDE.md, add-watch.md — URL ingest and folder watch reference, exports.md — extra exports and benchmark reference, extraction-spec.md — extraction subagent prompt spec, github-and-merge.md — GitHub clone and cross-repo merge reference, hooks.md — commit hook and CLAUDE.md integration reference, query.md — query, path, explain reference, transcribe.md — video/audio transcription reference (+3 more)

### Community 49 - "extract_patterns"
Cohesion: 0.29
Nodes (4): extract_patterns(), _get_condition_node_ids(), _get_node_by_id(), TestPatternExtraction

### Community 50 - "OrchestrAI Backend — Comprehensive Test Cases"
Cohesion: 0.18
Nodes (10): 10. Performance Tests, OrchestrAI Backend — Comprehensive Test Cases, Table of Contents, TC-PERF-001: Workflow Compilation Time for Large Graphs, TC-PERF-002: Concurrent Execution Limits, TC-PERF-003: Database Query Optimization for List Runs, TC-PERF-004: Memory Usage With Many Concurrent Workflows, TC-PERF-005: LangGraph Compilation Caching (+2 more)

### Community 51 - "Next.js Frontend"
Cohesion: 0.20
Nodes (10): Deep Space Color Palette, Control Room Glass Design System, Framer Motion, Glassmorphism UI, JetBrains Mono Font, Next.js Frontend, Phosphor Cyan Accent, React Flow (+2 more)

### Community 52 - "Landing Feature Sections"
Cohesion: 0.22
Nodes (9): Conditional Branching, Landing Feature Sections, No Drag-and-Drop Design, No DSL Required Design, Workflow Execution Observability, Plain Language Workflow Definition, Retry Logic, Step-by-Step Execution Graph (+1 more)

### Community 53 - "FastAPI main.py Entry Point"
Cohesion: 0.29
Nodes (8): REST API Endpoints, Agent Layer (Planner/Compiler/Verifier), Approval Module (HITL), Engine Layer (Runner), Config.py (Settings), CORS Middleware, FastAPI Backend, FastAPI main.py Entry Point

### Community 54 - "ApprovalNotFoundError"
Cohesion: 0.22
Nodes (3): ApprovalNotFoundError, TC-APR-011: Approve Non-Existent Approval Raises Error, TC-APR-012: Reject Non-Existent Approval Raises Error

### Community 55 - "registry.py"
Cohesion: 0.23
Nodes (3): Tool, ToolCall, TestToolPermissions

### Community 56 - "api/quality.py"
Cohesion: 0.14
Nodes (11): _rate(), stats(), add_correction(), CorrectionRequest, get_evaluation(), get_quality(), record_correction(), serialize_evaluation() (+3 more)

### Community 57 - "history/page.tsx"
Cohesion: 0.24
Nodes (9): HistoryPage(), HistoryRow, STATUS_BUCKET, statusDot, statusLabel, statusStyles, toRow(), deleteRun() (+1 more)

### Community 58 - "graph.py"
Cohesion: 0.33
Nodes (7): _edge(), is_canvas_shaped(), _node(), normalize_graph(), normalize_stored_graphs(), _tool(), test_canvas_shaped_graph_is_normalized()

### Community 59 - "EvolvePanel.tsx"
Cohesion: 0.17
Nodes (18): EvolvePanel(), EvolvePanelProps, pct(), VariantCard(), PATTERN_COLORS, SuggestionCard(), SuggestionsPanel(), SuggestionsPanelProps (+10 more)

### Community 60 - "5. Workflow Runner Tests"
Cohesion: 0.12
Nodes (17): 5. Workflow Runner Tests, TC-RUN-001: Happy Path — Simple Linear Workflow, TC-RUN-002: Happy Path — Branching Workflow (Onboarding), TC-RUN-003: Approval Pause and Resume Flow, TC-RUN-004: Approval Rejection Cancels Workflow, TC-RUN-005: Cancel Running Workflow, TC-RUN-006: Context Propagation Between Nodes, TC-RUN-007: Context-Driven Branching (Amount > Threshold) (+9 more)

### Community 61 - "PlannerAgent"
Cohesion: 0.11
Nodes (17): PlannerAgent, main(), 3. Agent Tests — Planner, Compiler, Verifier, TC-AGT-001: Planner Generates Valid Invoice Workflow From Prompt, TC-AGT-002: Planner Handles Malformed LLM Output, TC-AGT-003: Planner Retry Logic — Repairs After First Failure, TC-AGT-004: Planner Exhausts Retries and Returns Error, TC-AGT-005: Planner Rejects Unknown Tool References (+9 more)

### Community 62 - "OrchestrAI — Run Instructions"
Cohesion: 0.13
Nodes (14): 1. Clone and enter the project, 2. Backend, 3. Frontend, API Endpoints, Backend, Common Issues, Default Data, Frontend (+6 more)

### Community 64 - "Workflow Compiler"
Cohesion: 0.29
Nodes (4): Branching Logic, Workflow Compiler, Pydantic Schemas, Six Node Types

### Community 65 - "Frontend Pages"
Cohesion: 0.29
Nodes (7): Dashboard, Frontend Pages, Landing Page, Run Console, Tools Explorer, Wireframes, Workflow Builder

### Community 66 - "get_suggestions"
Cohesion: 0.48
Nodes (3): get_suggestions(), _make_workflow(), TestGetSuggestions

### Community 67 - "reject_request"
Cohesion: 0.20
Nodes (5): approve_request(), ApproveRequest, list_approvals(), reject_request(), RejectRequest

### Community 68 - "Navigation Sidebar"
Cohesion: 0.33
Nodes (6): Console Navigation, Dashboard Navigation, History Navigation, Navigation Sidebar, Tools Navigation, Workflows Navigation

### Community 69 - "Dark Theme UI"
Cohesion: 0.33
Nodes (6): Dark Theme UI, Window/Frame Icon, Landing/Root Page, Landing CTA Section, Landing Page Hero Section, Live Execution Replay

### Community 71 - "6. Approval Service Tests"
Cohesion: 0.24
Nodes (10): ApprovalAlreadyResolvedError, 6. Approval Service Tests, TC-APR-002: Approve Sets All Required Fields, TC-APR-003: Reject Sets All Required Fields, TC-APR-004: Double-Approve Raises Error, TC-APR-005: Double-Reject Raises Error, TC-APR-006: Approve Already-Rejected Approval Raises Error, TC-APR-007: Reject Already-Approved Approval Raises Error (+2 more)

### Community 72 - "What's Built"
Cohesion: 0.12
Nodes (16): 1. Execution Caching / Resumability, 2. Workflow Templates Marketplace, 3. Real-time Execution Console, 4. Multi-env Deployment, 5. Observability & Analytics, Backend — Core Engine, Backend — Cross-Pollination, Backend � Evolution Engine (+8 more)

### Community 74 - "cross_pollination.py"
Cohesion: 0.12
Nodes (6): enrich_with_llm(), _finalize_suggestion(), intrinsic_suggestions(), _structural_suggestions(), _summarize_workflow(), pattern_events()

### Community 75 - "9. Security Tests"
Cohesion: 0.20
Nodes (10): 9. Security Tests, TC-SEC-002: XSS in Workflow Names and Descriptions, TC-SEC-003: Permission Escalation via Approval, TC-SEC-004: Unauthorized Cancellation of Another User's Execution, TC-SEC-005: Environment Variable Exposure, TC-SEC-006: Code Injection via Condition Expression (eval), TC-SEC-007: Oversized Payload DoS Protection, TC-SEC-008: Tool Input Schema Validation (+2 more)

### Community 77 - "TriggersPanel.tsx"
Cohesion: 0.29
Nodes (10): describe(), PRESETS, TriggersPanel(), TriggersPanelProps, createTrigger(), deleteTrigger(), listTriggers(), setTriggerEnabled() (+2 more)

### Community 79 - "ApprovalService"
Cohesion: 0.20
Nodes (4): ApprovalService, TC-APR-013: Approval Persists Across Session Close/Reopen, approval_service(), TestApprovalPersistence

### Community 83 - "typing"
Cohesion: 0.13
Nodes (5): apply_suggestion(), list_suggestions(), ApplyPatchRequest, SuggestionResponse, SuggestionsResponse

### Community 85 - "runs.py"
Cohesion: 0.13
Nodes (12): cancel_run(), delete_run(), get_run(), list_runs(), _meta(), replay_run(), ReplayRequest, _serialize_exec() (+4 more)

### Community 86 - "WorkflowRunner"
Cohesion: 0.08
Nodes (12): Worker, WorkflowRunner, test_runner_cancel_running_workflow(), test_runner_context_passed_through(), test_runner_happy_path_simple_workflow(), test_runner_multiple_runs_no_state_leakage(), test_runner_onboarding_workflow(), test_runner_pauses_at_approval() (+4 more)

### Community 88 - "VersionHistoryPanel.tsx"
Cohesion: 0.33
Nodes (8): CHANGE_TYPE_COLORS, ChangeTypeBadge(), formatTime(), VersionHistoryPanel(), branchWorkflow(), getWorkflowHistory(), restoreVersion(), saveWorkflowVersion()

### Community 89 - "4. Tool Execution Tests"
Cohesion: 0.07
Nodes (32): create_ticket(), extract_invoice_data(), process_payment(), request_human_approval(), search_database(), send_email(), send_slack_message(), update_database() (+24 more)

### Community 93 - "api.ts"
Cohesion: 0.10
Nodes (27): AnalyticsPage(), pct(), Stat(), DashboardPage(), statusLabel, statusStyles, AnalyticsStats, authHeaders() (+19 more)

### Community 116 - "main.py"
Cohesion: 0.09
Nodes (4): get_api_key(), get_db(), health(), lifespan()

### Community 119 - "test_compiler.py"
Cohesion: 0.10
Nodes (4): compiler(), TestCompilerBranching, TestCompilerEdgeCases, TestCompilerSequential

### Community 121 - "genealogy/service.py"
Cohesion: 0.21
Nodes (3): WorkflowBranchModel, WorkflowVersionModel, db()

### Community 122 - "ExecutionStatus"
Cohesion: 0.11
Nodes (10): StepExecutionModel, WorkflowExecutionModel, ExecutionStatus, StepStatus, create_execution_at_approval(), test_stats(), TestHealth, TestSaveCreatesVersion (+2 more)

### Community 123 - "test_cross_pollination.py"
Cohesion: 0.17
Nodes (5): compute_similarity(), find_pattern_gaps(), db(), TestPatternGaps, TestSimilarityScoring

### Community 124 - "planner.py"
Cohesion: 0.13
Nodes (4): PlanningError, PlanningResult, TC-EDGE-007: Empty Workflow Prompt to Planner, mock_registry()

### Community 126 - "app/layout.tsx"
Cohesion: 0.33
Nodes (3): instrumentSans, jetbrainsMono, metadata

## Knowledge Gaps
- **300 isolated node(s):** `Config`, `eslintConfig`, `nextConfig`, `name`, `version` (+295 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 819 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQLAlchemy ORM` connect `ExecutionStatus` to `workflows.py`, `custom_tools.py`, `api/integrations.py`, `WorkflowModel`, `jobs.py`, `Anthropic Claude API`, `WorkflowRunner Engine`, `typing`, `main.py`, `runs.py`, `api/quality.py`, `genealogy/service.py`, `graph.py`, `test_cross_pollination.py`, `api/genealogy.py`, `OrchestrAI Platform`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `ToolResult` connect `ToolResult` to `implementations.py`, `VerifierAgent`, `WorkflowNotFoundError`, `IntegrationHandler`, `asyncio`, `tools/integrations.py`, `WorkflowRunner`, `registry.py`, `4. Tool Execution Tests`, `ExecutionStatus`, `ToolRegistry`, `TestVerifierLLM`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `Python Requirements` connect `Anthropic Claude API` to `ExecutionStatus`, `FastAPI main.py Entry Point`, `OrchestrAI Platform`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ToolResult` (e.g. with `VerifierAgent` and `WorkflowRunner`) actually correct?**
  _`ToolResult` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ExecutionStatus` (e.g. with `_make_node_executor()` and `evaluate_run()`) actually correct?**
  _`ExecutionStatus` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `WorkflowRunner` (e.g. with `approve_request()` and `reject_request()`) actually correct?**
  _`WorkflowRunner` has 31 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `eslintConfig`, `nextConfig` to the rest of the system?**
  _300 weakly-connected nodes found - possible documentation gaps or missing edges._