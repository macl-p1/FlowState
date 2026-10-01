# Graph Report - OrchestrAI  (2026-10-01)

## Corpus Check
- 120 files · ~162,586 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .graphify-bak 1, .ini 1)

## Summary
- 1557 nodes · 2920 edges · 119 communities (67 shown, 52 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 299 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a2c5ead4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- implementations.py
- cross_pollination.py
- api.ts
- package.json
- WorkflowNotFoundError
- conftest.py
- compiler.py
- api/integrations.py
- IntegrationHandler
- WorkflowRunner
- Workflow
- asyncio
- BuilderClient.tsx
- lucide-react
- ConsoleClient.tsx
- test_genealogy.py
- CustomTool
- tools/integrations.py
- FlowState Application
- Workflow Builder Page
- planner.py
- ToolResult
- compilerOptions
- design-md-planner skill
- workflows.py
- compute_diff
- VerifierAgent
- custom_tools.py
- api/genealogy.py
- TestApiKeyAuth
- OrchestrAI Platform
- TestPlannerAgent
- Dashboard Page
- GenealogyService
- WorkflowCompiler
- find_pattern_gaps
- ToolRegistry
- VersionHistoryPanel.tsx
- Tool Registry
- extract_patterns
- runs.py
- _version_to_dict
- workflow.py
- 1. API Endpoint Tests
- Anthropic Claude API
- WorkflowRunner Engine
- models/custom_tool.py
- graphify skill
- CompiledWorkflow
- TestExecutionStatuses
- Next.js Frontend
- Landing Feature Sections
- FastAPI main.py Entry Point
- PlannerAgent
- 7. Integration / End-to-End Tests
- client
- TestCompilerSequential
- TestInvalidWorkflows
- SuggestionsPanel.tsx
- 5. Workflow Runner Tests
- _run_verification_test
- OrchestrAI — Run Instructions
- compute_similarity
- Workflow Compiler
- Frontend Pages
- get_suggestions
- DiffResult
- Navigation Sidebar
- Dark Theme UI
- TestWorkflowAPI
- 6. Approval Service Tests
- What Needs to Be Built
- TestApprovalAPI
- TestRunAPI
- TestToolAPI
- TestApprovalQueries
- TestVerifierLLM
- 8. Edge Cases & Stress Tests
- 4. Tool Execution Tests
- TestCompilerEdgeCases
- enrich_with_llm
- OrchestrAI Backend — Comprehensive Test Cases
- apply_suggestion
- 9. Security Tests
- search_database
- typing
- app/layout.tsx
- stats
- create_pending_approval
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
- TestApprovalCreation
- TestHealth
- db

## God Nodes (most connected - your core abstractions)
1. `ToolResult` - 91 edges
2. `WorkflowRunner` - 42 edges
3. `ToolRegistry` - 39 edges
4. `PlannerAgent` - 35 edges
5. `fetchWithAuth()` - 35 edges
6. `Workflow` - 34 edges
7. `handleResponse()` - 33 edges
8. `ExecutionStatus` - 32 edges
9. `ApprovalService` - 29 edges
10. `3. Agent Tests — Planner, Compiler, Verifier` - 25 edges

## Surprising Connections (you probably didn't know these)
- `TC-APR-013: Approval Persists Across Session Close/Reopen` --references--> `ApprovalService`  [INFERRED]
  backend/test-cases.md → backend/app/approval/service.py
- `TC-APR-014: Create Approval With Default Parameters` --references--> `ApprovalService`  [INFERRED]
  backend/test-cases.md → backend/app/approval/service.py
- `TC-RUN-009: Error Handling — Unknown Workflow` --references--> `WorkflowNotFoundError`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py
- `TC-RUN-013: Resume Non-Existent Execution` --references--> `WorkflowNotFoundError`  [INFERRED]
  backend/test-cases.md → backend/app/engine/runner.py
- `TC-RUN-014: Cancel Non-Existent Execution` --references--> `WorkflowNotFoundError`  [INFERRED]
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

## Communities (119 total, 52 thin omitted)

### Community 0 - "implementations.py"
Cohesion: 0.05
Nodes (30): aggregate_metrics(), check_health(), classify_text(), conditional_router(), create_invoice(), create_lead(), create_task(), delay() (+22 more)

### Community 1 - "cross_pollination.py"
Cohesion: 0.23
Nodes (4): apply_patch_to_workflow(), _find_first_by_type(), _find_node(), TestApplyPatch

### Community 2 - "api.ts"
Cohesion: 0.09
Nodes (48): DashboardPage(), statusLabel, statusStyles, FormData, STATUS_LABEL, STATUS_STYLES, TOOL_TYPE_LABELS, TOOL_TYPES (+40 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (38): eslintConfig, dependencies, lucide-react, next, react, react-dom, @xyflow/react, devDependencies (+30 more)

### Community 5 - "WorkflowNotFoundError"
Cohesion: 0.14
Nodes (6): RunnerError, WorkflowNotFoundError, _persist_steps(), WorkflowExecution, TC-E2E-010: Database Transaction Rollback on Runner Failure, TC-RUN-012: Resume From Non-Approval State Raises Error

### Community 6 - "conftest.py"
Cohesion: 0.10
Nodes (12): ApprovalRequestModel, StepExecutionModel, WorkflowExecutionModel, WorkflowModel, ExecutionStatus, StepStatus, PermissionLevel, create_execution_at_approval() (+4 more)

### Community 7 - "compiler.py"
Cohesion: 0.15
Nodes (6): _make_node_executor(), execute(), StepExecution, _eval_node(), safe_eval(), SafeEvalError

### Community 8 - "api/integrations.py"
Cohesion: 0.11
Nodes (11): get_integration(), _get_tool_or_404(), list_integrations(), remove_integration(), set_integration(), _tool_to_response(), verify_integration(), CustomToolResponse (+3 more)

### Community 10 - "WorkflowRunner"
Cohesion: 0.07
Nodes (22): approve_request(), ApproveRequest, list_approvals(), reject_request(), RejectRequest, ApprovalService, WorkflowRunner, TC-APR-001: Create Pending Approval Request (+14 more)

### Community 11 - "Workflow"
Cohesion: 0.07
Nodes (11): Workflow, db_engine(), db_session(), persisted_invoice_workflow(), registry_with_context(), runner(), sample_complaint_workflow(), sample_invoice_workflow() (+3 more)

### Community 13 - "BuilderClient.tsx"
Cohesion: 0.11
Nodes (21): BuilderClient(), BuilderInner(), defaultEdges, defaultNodes, LabeledEdgeMemo, snap(), tools, BuilderLoading() (+13 more)

### Community 14 - "lucide-react"
Cohesion: 0.11
Nodes (18): nextConfig, initialRuns, statusDot, statusLabel, statusStyles, AppLayout(), demoSteps, features (+10 more)

### Community 15 - "ConsoleClient.tsx"
Cohesion: 0.12
Nodes (21): ConsoleClient(), ConsoleClientProps, getNodeState(), NODE_ICONS, NodeState, nodeStateStyles, statusLabel, statusStyles (+13 more)

### Community 16 - "test_genealogy.py"
Cohesion: 0.17
Nodes (3): WorkflowBranchModel, WorkflowVersionModel, db()

### Community 17 - "CustomTool"
Cohesion: 0.17
Nodes (9): create_custom_tool(), delete_custom_tool(), get_custom_tool(), list_all_tools(), list_custom_tools(), list_custom_tools_by_type(), register_custom_tool(), _tool_to_response() (+1 more)

### Community 18 - "tools/integrations.py"
Cohesion: 0.15
Nodes (3): _mask(), _mask_credentials(), TestCredentialMasking

### Community 19 - "FlowState Application"
Cohesion: 0.15
Nodes (17): FlowState Application, FlowState Logo, Vercel Logo, Workflow Builder (Mobile), Execution Console (Mobile), Dashboard (Mobile), Run History (Mobile), Landing/Root Page (Mobile) (+9 more)

### Community 20 - "Workflow Builder Page"
Cohesion: 0.16
Nodes (19): Approval UI, Canvas Grid Background, Customer Onboarding Workflow, Fetch Customers Node, Workflow Builder Page, Console Output Log, Execution Console Page, Glassmorphism Design System (+11 more)

### Community 21 - "planner.py"
Cohesion: 0.10
Nodes (5): PlanningError, PlanningResult, main(), TC-EDGE-007: Empty Workflow Prompt to Planner, mock_registry()

### Community 22 - "ToolResult"
Cohesion: 0.12
Nodes (8): ToolResult, delete_file(), fan_in(), generate_shipping_label(), list_available_slots(), send_sms(), TestToolResult, TestVerifierRuleBased

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "design-md-planner skill"
Cohesion: 0.33
Nodes (12): Archival Institutional aesthetic direction, Kiln — worked DESIGN.md example, DESIGN.md template skeleton, design-md-planner README, cli.md — @google/design.md CLI reference, designmd-spec.md — DESIGN.md format spec, design-md-planner skill, DESIGN.md format specification (+4 more)

### Community 25 - "workflows.py"
Cohesion: 0.06
Nodes (16): get_api_key(), get_tool(), list_tools(), delete_workflow(), generate_workflow(), GenerateRequest, get_workflow(), list_workflows() (+8 more)

### Community 26 - "compute_diff"
Cohesion: 0.18
Nodes (4): compute_diff(), _edge_condition_key(), _serialize(), TestComputeDiff

### Community 27 - "VerifierAgent"
Cohesion: 0.14
Nodes (6): VerificationResult, VerifierAgent, TC-AGT-016: Verifier Rule-Based — Success Verdict, TC-AGT-020: Verifier LLM-Based Verification With Mock, TC-AGT-021: Verifier Falls Back to Rule-Based on LLM Error, verifier()

### Community 28 - "custom_tools.py"
Cohesion: 0.23
Nodes (8): list_categories(), _type_icon(), verify_custom_tool(), CustomToolCreate, CustomToolUpdate, ToolCategory, ToolVerifyRequest, ToolVerifyResponse

### Community 29 - "api/genealogy.py"
Cohesion: 0.18
Nodes (7): branch_workflow(), BranchWorkflowRequest, get_history(), get_lineage(), get_version(), save_version(), SaveVersionRequest

### Community 31 - "OrchestrAI Platform"
Cohesion: 0.14
Nodes (12): Backend Architecture Plan, 21-Session Build Plan, Customer Complaint Workflow, Docker Compose, FlowPilot (Product Name), FlowState (Presentation Name), Graphify Knowledge Graph, Invoice Processing Workflow (+4 more)

### Community 32 - "TestPlannerAgent"
Cohesion: 0.23
Nodes (3): make_mock_client(), make_mock_client_with_sequence(), TestPlannerAgent

### Community 33 - "Dashboard Page"
Cohesion: 0.14
Nodes (14): Daily Report Generator Workflow, Dashboard KPI Cards, Dashboard Page, Run History Page, Invoice Processor Workflow, Run History Table, Run Status: Completed, Run Status: Failed (+6 more)

### Community 34 - "GenealogyService"
Cohesion: 0.33
Nodes (3): GenealogyService, _make_workflow(), TestGenealogyService

### Community 35 - "WorkflowCompiler"
Cohesion: 0.11
Nodes (11): CompilationError, WorkflowCompiler, TC-AGT-010: Compiler Rejects Workflow Without Trigger, TC-AGT-011: Compiler Rejects Workflow With Multiple Triggers, TC-AGT-012: Compiler Handles Condition Nodes with True/False Branches, TC-AGT-013: Compiler Handles Approval Nodes, TC-AGT-014: Compiler Handles Retry Configuration on Nodes, TC-AGT-015: Compiler Minimal Workflow (Trigger + End Only) (+3 more)

### Community 36 - "find_pattern_gaps"
Cohesion: 0.24
Nodes (4): _build_suggestion(), _finalize_suggestion(), find_pattern_gaps(), TestPatternGaps

### Community 37 - "ToolRegistry"
Cohesion: 0.06
Nodes (11): get_db_context(), Tool, ToolCall, ToolAlreadyRegisteredError, ToolRegistry, UnknownToolError, TC-EDGE-003: Missing Tool Handler at Runtime, TC-TOOL-011: Unknown Tool Execution Raises Error (+3 more)

### Community 38 - "VersionHistoryPanel.tsx"
Cohesion: 0.27
Nodes (11): CHANGE_TYPE_COLORS, ChangeTypeBadge(), formatTime(), VersionHistoryPanel(), VersionHistoryPanelProps, VersionItemData, BackendEdge, BackendNode (+3 more)

### Community 39 - "Tool Registry"
Cohesion: 0.26
Nodes (12): Tools Module (Registry + Implementations), Database Query Tool, Tools Browser, Tools Explorer Page, HTTP Request Tool, Mock Tool Implementations, Permission Levels, Rate Limiter Tool (+4 more)

### Community 40 - "extract_patterns"
Cohesion: 0.29
Nodes (4): extract_patterns(), _get_condition_node_ids(), _get_node_by_id(), TestPatternExtraction

### Community 41 - "runs.py"
Cohesion: 0.15
Nodes (7): cancel_run(), list_runs(), _serialize_exec(), _serialize_step(), stream_run(), event_generator(), get_db()

### Community 43 - "workflow.py"
Cohesion: 0.07
Nodes (28): ActionNode, ApprovalNode, ConditionNode, Edge, EndNode, NodeType, Trigger, TriggerNode (+20 more)

### Community 44 - "1. API Endpoint Tests"
Cohesion: 0.12
Nodes (17): 1. API Endpoint Tests, TC-API-001: Health Check Returns Service Status, TC-API-002: Generate Workflow From Natural Language Prompt, TC-API-003: List Workflows — Empty State, TC-API-004: List Workflows — Multiple Workflows Sorted by Recency, TC-API-005: Get Specific Workflow, TC-API-006: Run Workflow — Happy Path, TC-API-007: Run Workflow — Not Found (+9 more)

### Community 45 - "Anthropic Claude API"
Cohesion: 0.18
Nodes (9): Anthropic Claude API, Python Requirements, Backend Tests, LangGraph (from LangChain), LangGraph Engine, Natural Language Interface, Planner Agent, pytest Test Suite (+1 more)

### Community 46 - "WorkflowRunner Engine"
Cohesion: 0.22
Nodes (10): API Route Handlers, Approval System (HITL), Human-in-the-Loop, Step-Level Observability, Retry Mechanism, WorkflowRunner Engine, Step Persistence, Template Variable Substitution (+2 more)

### Community 47 - "models/custom_tool.py"
Cohesion: 0.22
Nodes (3): update_custom_tool(), ToolStatus, ToolType

### Community 48 - "graphify skill"
Cohesion: 0.20
Nodes (11): OrchestrAI CLAUDE.md, add-watch.md — URL ingest and folder watch reference, exports.md — extra exports and benchmark reference, extraction-spec.md — extraction subagent prompt spec, github-and-merge.md — GitHub clone and cross-repo merge reference, hooks.md — commit hook and CLAUDE.md integration reference, query.md — query, path, explain reference, transcribe.md — video/audio transcription reference (+3 more)

### Community 51 - "Next.js Frontend"
Cohesion: 0.20
Nodes (10): Deep Space Color Palette, Control Room Glass Design System, Framer Motion, Glassmorphism UI, JetBrains Mono Font, Next.js Frontend, Phosphor Cyan Accent, React Flow (+2 more)

### Community 52 - "Landing Feature Sections"
Cohesion: 0.22
Nodes (9): Conditional Branching, Landing Feature Sections, No Drag-and-Drop Design, No DSL Required Design, Workflow Execution Observability, Plain Language Workflow Definition, Retry Logic, Step-by-Step Execution Graph (+1 more)

### Community 53 - "FastAPI main.py Entry Point"
Cohesion: 0.29
Nodes (8): REST API Endpoints, Agent Layer (Planner/Compiler/Verifier), Approval Module (HITL), Engine Layer (Runner), Config.py (Settings), CORS Middleware, FastAPI Backend, FastAPI main.py Entry Point

### Community 54 - "PlannerAgent"
Cohesion: 0.13
Nodes (16): PlannerAgent, 3. Agent Tests — Planner, Compiler, Verifier, TC-AGT-001: Planner Generates Valid Invoice Workflow From Prompt, TC-AGT-002: Planner Handles Malformed LLM Output, TC-AGT-003: Planner Retry Logic — Repairs After First Failure, TC-AGT-004: Planner Exhausts Retries and Returns Error, TC-AGT-005: Planner Rejects Unknown Tool References, TC-AGT-006: Planner Metadata Extraction (+8 more)

### Community 55 - "7. Integration / End-to-End Tests"
Cohesion: 0.25
Nodes (8): 7. Integration / End-to-End Tests, TC-E2E-002: Full Employee Onboarding Workflow, TC-E2E-003: Full Customer Support Workflow, TC-E2E-004: Workflow With Retry on Failure, TC-E2E-005: Workflow With Multiple Condition Nodes, TC-E2E-006: Concurrent Workflow Executions, TC-E2E-007: Workflow End-to-End With Approval Rejection, TC-E2E-009: Workflow With Wait Node in Sequence

### Community 56 - "client"
Cohesion: 0.25
Nodes (4): auth_client(), client(), override_get_db(), setup_test_db()

### Community 59 - "SuggestionsPanel.tsx"
Cohesion: 0.36
Nodes (7): PATTERN_COLORS, SuggestionCard(), SuggestionsPanel(), SuggestionsPanelProps, applySuggestion(), getWorkflowSuggestions(), SuggestionItem

### Community 60 - "5. Workflow Runner Tests"
Cohesion: 0.12
Nodes (16): 5. Workflow Runner Tests, TC-RUN-001: Happy Path — Simple Linear Workflow, TC-RUN-002: Happy Path — Branching Workflow (Onboarding), TC-RUN-004: Approval Rejection Cancels Workflow, TC-RUN-005: Cancel Running Workflow, TC-RUN-006: Context Propagation Between Nodes, TC-RUN-007: Context-Driven Branching (Amount > Threshold), TC-RUN-008: Multiple Runs Without State Leakage (+8 more)

### Community 61 - "_run_verification_test"
Cohesion: 0.38
Nodes (3): _build_verification_inputs(), _run_verification_test(), _validate_config_shape()

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

### Community 68 - "Navigation Sidebar"
Cohesion: 0.33
Nodes (6): Console Navigation, Dashboard Navigation, History Navigation, Navigation Sidebar, Tools Navigation, Workflows Navigation

### Community 69 - "Dark Theme UI"
Cohesion: 0.33
Nodes (6): Dark Theme UI, Window/Frame Icon, Landing/Root Page, Landing CTA Section, Landing Page Hero Section, Live Execution Replay

### Community 71 - "6. Approval Service Tests"
Cohesion: 0.06
Nodes (26): ApprovalAlreadyResolvedError, ApprovalNotFoundError, 10. Performance Tests, 6. Approval Service Tests, TC-APR-002: Approve Sets All Required Fields, TC-APR-003: Reject Sets All Required Fields, TC-APR-004: Double-Approve Raises Error, TC-APR-005: Double-Reject Raises Error (+18 more)

### Community 72 - "What Needs to Be Built"
Cohesion: 0.14
Nodes (13): 1. Execution Caching / Resumability, 2. Workflow Templates Marketplace, 3. Real-time Execution Console, 4. Multi-env Deployment, 5. Observability & Analytics, Backend — Core Engine, Backend — Cross-Pollination, Backend — Genealogy (+5 more)

### Community 79 - "8. Edge Cases & Stress Tests"
Cohesion: 0.15
Nodes (13): 8. Edge Cases & Stress Tests, TC-EDGE-001: Very Large Workflow (50+ Nodes), TC-EDGE-004: Node Execution Timeout, TC-EDGE-005: Malformed Context Data, TC-EDGE-006: Database Connection Loss During Execution, TC-EDGE-008: Workflow With Only Trigger and End (No Intermediate Nodes), TC-EDGE-009: Unicode and Special Characters in Workflow Names and Inputs, TC-EDGE-010: Condition Node With Malformed Expression (+5 more)

### Community 83 - "4. Tool Execution Tests"
Cohesion: 0.11
Nodes (16): create_calendar_event(), request_human_approval(), send_email(), send_slack_message(), validate_invoice(), 4. Tool Execution Tests, TC-TOOL-001: send_email — Successful Send, TC-TOOL-002: send_email — Missing Required Field (+8 more)

### Community 88 - "9. Security Tests"
Cohesion: 0.20
Nodes (10): 9. Security Tests, TC-SEC-002: XSS in Workflow Names and Descriptions, TC-SEC-003: Permission Escalation via Approval, TC-SEC-004: Unauthorized Cancellation of Another User's Execution, TC-SEC-005: Environment Variable Exposure, TC-SEC-006: Code Injection via Condition Expression (eval), TC-SEC-007: Oversized Payload DoS Protection, TC-SEC-008: Tool Input Schema Validation (+2 more)

### Community 89 - "search_database"
Cohesion: 0.10
Nodes (18): create_ticket(), extract_invoice_data(), process_payment(), search_database(), update_database(), Appendix: Test Data Reference, Built-in Mock Data, Example Workflow Definitions (+10 more)

### Community 90 - "typing"
Cohesion: 0.22
Nodes (3): ApplyPatchRequest, SuggestionResponse, SuggestionsResponse

### Community 91 - "app/layout.tsx"
Cohesion: 0.33
Nodes (3): instrumentSans, jetbrainsMono, metadata

## Knowledge Gaps
- **292 isolated node(s):** `Config`, `eslintConfig`, `nextConfig`, `name`, `version` (+287 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 725 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQLAlchemy ORM` connect `conftest.py` to `api/integrations.py`, `runs.py`, `WorkflowRunner`, `Anthropic Claude API`, `WorkflowRunner Engine`, `test_genealogy.py`, `workflows.py`, `typing`, `custom_tools.py`, `api/genealogy.py`, `OrchestrAI Platform`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Why does `ToolResult` connect `ToolResult` to `implementations.py`, `ToolRegistry`, `WorkflowNotFoundError`, `conftest.py`, `IntegrationHandler`, `WorkflowRunner`, `asyncio`, `TestVerifierLLM`, `tools/integrations.py`, `4. Tool Execution Tests`, `search_database`, `VerifierAgent`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `Python Requirements` connect `Anthropic Claude API` to `FastAPI main.py Entry Point`, `conftest.py`, `OrchestrAI Platform`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ToolResult` (e.g. with `VerifierAgent` and `WorkflowRunner`) actually correct?**
  _`ToolResult` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `WorkflowRunner` (e.g. with `approve_request()` and `reject_request()`) actually correct?**
  _`WorkflowRunner` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ToolRegistry` (e.g. with `CustomTool` and `Tool`) actually correct?**
  _`ToolRegistry` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PlannerAgent` (e.g. with `Workflow` and `generate_workflow()`) actually correct?**
  _`PlannerAgent` has 14 INFERRED edges - model-reasoned connections that need verification._