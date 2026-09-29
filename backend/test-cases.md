# OrchestrAI Backend — Comprehensive Test Cases

> **Scope**: Universal Workflow Agent Platform  
> **Framework**: pytest + FastAPI TestClient + AsyncMock  
> **Database**: SQLite (in-memory for tests)  
> **Coverage Target**: 100% of happy paths, critical error paths, and real-world business scenarios

---

## Table of Contents

1. [API Endpoint Tests](#1-api-endpoint-tests)
2. [Schema Validation Tests](#2-schema-validation-tests)
3. [Agent Tests — Planner, Compiler, Verifier](#3-agent-tests--planner-compiler-verifier)
4. [Tool Execution Tests](#4-tool-execution-tests)
5. [Workflow Runner Tests](#5-workflow-runner-tests)
6. [Approval Service Tests](#6-approval-service-tests)
7. [Integration / End-to-End Tests](#7-integration--end-to-end-tests)
8. [Edge Cases & Stress Tests](#8-edge-cases--stress-tests)
9. [Security Tests](#9-security-tests)
10. [Performance Tests](#10-performance-tests)

---

## 1. API Endpoint Tests

### TC-API-001: Health Check Returns Service Status

- **Priority**: High
- **Preconditions**: Server is running; no authentication required
- **Test Steps**:
  1. Send `GET /api/health`
- **Expected Result**:
  - Status code: `200`
  - Response body: `{"status": "healthy", "service": "orchestr-ai", "version": "0.1.0"}`
  - Response time < 100ms
- **Edge Cases**:
  - Verify the endpoint is accessible without authentication headers
  - Verify the `service` field matches the application name
  - Verify the `version` field follows semver format

---

### TC-API-002: Generate Workflow From Natural Language Prompt

- **Priority**: High
- **Preconditions**: Valid `ANTHROPIC_API_KEY` configured or mocked LLM client
- **Test Steps**:
  1. Send `POST /api/workflows/generate` with body `{"prompt": "When an invoice arrives, extract the details and match it against a purchase order, then process payment if approved"}`
  2. Capture the response
  3. Verify the returned workflow ID
- **Expected Result**:
  - Status code: `200`
  - Response contains `id` (prefixed with `wf_`), `name`, `description`, `nodes`, `edges`, `metadata`
  - Workflow has exactly one trigger node and one end node
  - All node IDs are unique
  - All edge references point to existing nodes
  - `metadata` contains `node_count`, `tools_used`, `has_branching`, `complexity`
- **Edge Cases**:
  - Empty prompt body → `422` validation error
  - Extremely long prompt (>10,000 characters) → should not crash, may time out
  - Prompt referencing a tool that does not exist (e.g., "use quantum_tool") → planner should return `422` after retries
  - Prompt in a non-English language (e.g., Japanese, Arabic) → should still produce valid JSON
  - Prompt with special characters (emoji, unicode, code snippets)

---

### TC-API-003: List Workflows — Empty State

- **Priority**: Medium
- **Preconditions**: No workflows have been created
- **Test Steps**:
  1. Send `GET /api/workflows`
- **Expected Result**:
  - Status code: `200`
  - Response body: `[]`
  - Response time < 200ms
- **Edge Cases**:
  - Verify the endpoint returns an empty array, not `null` or `{}`
  - Verify CORS headers are present

---

### TC-API-004: List Workflows — Multiple Workflows Sorted by Recency

- **Priority**: Medium
- **Preconditions**: At least 3 workflows exist in the database, created at different times
- **Test Steps**:
  1. Create workflow A, wait 1 second, create workflow B, wait 1 second, create workflow C
  2. Send `GET /api/workflows`
- **Expected Result**:
  - Status code: `200`
  - Array length: 3
  - Workflows ordered by `created_at` descending (C, B, A)
  - Each entry has `id`, `name`, `description`, `created_at`, `metadata`
- **Edge Cases**:
  - Workflows with identical timestamps → stable sort order
  - Very large number of workflows (100+) → response time acceptable
  - Deleted workflows should not appear

---

### TC-API-005: Get Specific Workflow

- **Priority**: High
- **Preconditions**: A workflow with ID `wf_abc12345` exists
- **Test Steps**:
  1. Send `GET /api/workflows/wf_abc12345`
- **Expected Result**:
  - Status code: `200`
  - Response body contains full workflow definition including nodes, edges, metadata, and `created_at`
- **Edge Cases**:
  - Request with a non-existent ID → `404 Not Found`
  - Request with an ID that looks valid but does not exist → `404 Not Found`
  - Request with SQL injection payload in ID (`"wf_'; DROP TABLE workflows;--"`) → `404 Not Found` (no crash)
  - Request with extremely long ID (10,000 characters) → `404 Not Found`

---

### TC-API-006: Run Workflow — Happy Path

- **Priority**: High
- **Preconditions**: A workflow `wf_abc12345` exists (e.g., the invoice processing workflow)
- **Test Steps**:
  1. Send `POST /api/workflows/wf_abc12345/run` with optional context `{"amount": 50000}`
  2. Capture the execution ID and initial status
- **Expected Result**:
  - Status code: `200`
  - Response contains `id` (execution ID), `workflow_id`, `status`, `steps`
  - Each step has `id`, `node_id`, `node_name`, `node_type`, `status`, `attempt_count`
  - Workflow either completes or pauses for approval depending on the workflow definition
- **Edge Cases**:
  - Run with `null` context → should use empty context
  - Run with deeply nested context (5+ levels) → should work
  - Run the same workflow concurrently → each run should have a unique execution ID
  - Run a workflow that has already been run before → should create a new independent execution

---

### TC-API-007: Run Workflow — Not Found

- **Priority**: Medium
- **Preconditions**: No workflow with ID `wf_nonexistent` exists
- **Test Steps**:
  1. Send `POST /api/workflows/wf_nonexistent/run`
- **Expected Result**:
  - Status code: `404 Not Found`
  - Response body: `{"detail": "Workflow not found"}`

---

### TC-API-008: Get Execution Details

- **Priority**: Medium
- **Preconditions**: An execution with ID `exec_xyz` exists (completed, failed, or running)
- **Test Steps**:
  1. Send `GET /api/runs/exec_xyz`
- **Expected Result**:
  - Status code: `200`
  - Response contains full execution record: `id`, `workflow_id`, `workflow_name`, `status`, `context`, `steps` (with timestamps, tool results, errors), `approval` (if present), `started_at`, `completed_at`
- **Edge Cases**:
  - Execution with no steps yet (just created) → `steps: []`
  - Execution with failed step → step contains `error` field
  - Execution with approval pending → `approval` object present

---

### TC-API-009: Get Execution — Not Found

- **Priority**: Low
- **Preconditions**: No execution with the given ID exists
- **Test Steps**:
  1. Send `GET /api/runs/exec_nonexistent`
- **Expected Result**:
  - Status code: `404 Not Found`

---

### TC-API-010: List Executions

- **Priority**: Medium
- **Preconditions**: Multiple executions exist (some completed, some failed, some pending approval)
- **Test Steps**:
  1. Send `GET /api/runs?limit=10`
- **Expected Result**:
  - Status code: `200`
  - Returns executions ordered by `started_at` descending
  - Default limit of 50 is applied when no query parameter provided
  - Each entry has `id`, `workflow_id`, `workflow_name`, `status`, `started_at`, `completed_at`
- **Edge Cases**:
  - No executions exist → returns `[]`
  - More than 50 executions exist → only first 50 returned
  - Custom `limit` parameter → respected (e.g., `?limit=5`)

---

### TC-API-011: Cancel Running Execution

- **Priority**: High
- **Preconditions**: An execution `exec_xyz` is in `RUNNING` or `WAITING_APPROVAL` status
- **Test Steps**:
  1. Send `POST /api/runs/exec_xyz/cancel`
  2. Verify the execution status is now `CANCELLED`
- **Expected Result**:
  - Status code: `200`
  - Response body: `{"id": "exec_xyz", "status": "cancelled"}`
  - `completed_at` is set to current timestamp
- **Edge Cases**:
  - Cancel an already completed execution → `400 Bad Request` (or handled gracefully)
  - Cancel an already cancelled execution → handled gracefully
  - Cancel a non-existent execution → `404 Not Found`
  - Cancel an execution twice → second cancel should not error catastrophically

---

### TC-API-012: List Pending Approvals

- **Priority**: High
- **Preconditions**: At least one execution is in `WAITING_APPROVAL` status
- **Test Steps**:
  1. Send `GET /api/approvals`
- **Expected Result**:
  - Status code: `200`
  - Returns array of pending approval objects with `id`, `execution_id`, `node_id`, `reason`, `context`, `approver_role`, `status`, `created_at`
- **Edge Cases**:
  - No pending approvals → returns `[]`
  - Mix of pending and resolved approvals → only pending returned

---

### TC-API-013: Approve an Approval Request

- **Priority**: High
- **Preconditions**: An approval request with ID `approval_xyz` is in `pending` status
- **Test Steps**:
  1. Send `POST /api/approvals/approval_xyz/approve` with body `{"approver_id": "user_123"}`
  2. Verify the approval is now `approved`
  3. Verify the associated workflow execution has resumed
- **Expected Result**:
  - Status code: `200`
  - Approval status changes to `approved`
  - `approver_id` is set
  - `approved_at` and `resolved_at` timestamps are set
  - Workflow execution continues past the approval node
- **Edge Cases**:
  - Approve with empty `approver_id` → may be accepted (validation depends on implementation)
  - Approve a non-existent approval → `400 Bad Request`
  - Approve an already resolved approval → `400 Bad Request` with "already resolved" message

---

### TC-API-014: Reject an Approval Request

- **Priority**: High
- **Preconditions**: An approval request with ID `approval_xyz` is in `pending` status
- **Test Steps**:
  1. Send `POST /api/approvals/approval_xyz/reject` with body `{"approver_id": "user_123", "reason": "Budget exceeded"}`
  2. Verify the approval is now `rejected`
  3. Verify the associated workflow execution is `CANCELLED`
- **Expected Result**:
  - Status code: `200`
  - Approval status: `rejected`
  - `rejection_reason` is stored
  - Workflow execution status becomes `CANCELLED`
- **Edge Cases**:
  - Reject without a reason (null) → should work, `rejection_reason` is `null`
  - Reject with an extremely long reason (10,000 characters) → should store it
  - Reject a non-existent approval → `400 Bad Request`
  - Reject an already approved approval → `400 Bad Request`

---

### TC-API-015: List All Registered Tools

- **Priority**: Medium
- **Preconditions**: Tool registry is initialized with default tools
- **Test Steps**:
  1. Send `GET /api/tools`
- **Expected Result**:
  - Status code: `200`
  - Returns array of tool objects, each with `name`, `description`, `permission`, `timeout_seconds`, `retryable`, `input_schema`
  - Contains all 11 default tools (send_email, send_slack_message, search_database, update_database, create_ticket, create_calendar_event, request_human_approval, wait, extract_invoice_data, validate_invoice, process_payment)
- **Edge Cases**:
  - Verify `permission` values are valid enum strings (AUTO, CONFIRM, HUMAN_ONLY)
  - Verify `input_schema` follows JSON Schema format

---

### TC-API-016: Get Specific Tool Details

- **Priority**: Low
- **Preconditions**: Tool `send_email` is registered
- **Test Steps**:
  1. Send `GET /api/tools/send_email`
- **Expected Result**:
  - Status code: `200`
  - Response contains tool definition with required fields
- **Edge Cases**:
  - Request for non-existent tool → `404 Not Found`
  - Request with case variation (`Send_Email`, `SEND_EMAIL`) → `404 Not Found` (case-sensitive)

---

## 2. Schema Validation Tests

### TC-SCH-001: Valid Invoice Processing Workflow Passes Validation

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow dict matching the invoice processing pattern (trigger → action → action → condition → approval → action → end)
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - No `ValidationError` raised
  - `workflow.name` is "Invoice Processing"
  - `len(workflow.nodes)` == 7
  - `len(workflow.edges)` == 7
  - Node types: trigger, action, action, condition, approval, action, end
- **Edge Cases**:
  - Add optional fields (`expected_outcome`, `retry_count`, `retry_delay`) → should still validate
  - Add `metadata` to the workflow → should validate

---

### TC-SCH-002: Valid Employee Onboarding Workflow Passes Validation

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow dict for employee onboarding (trigger → email → condition → slack/email → email → end)
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - No `ValidationError` raised
  - 6 nodes, 7 edges
  - Condition node has `true` and `false` branches
- **Edge Cases**:
  - Both branches of the condition converge to the same node → should validate

---

### TC-SCH-003: Missing Trigger Node Rejected

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow with nodes `[action, action, end]` — no trigger
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - `ValidationError` raised
  - Error message contains "trigger"

---

### TC-SCH-004: Multiple Trigger Nodes Rejected

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow with two trigger nodes
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - `ValidationError` raised
  - Error message mentions exactly one trigger required

---

### TC-SCH-005: Duplicate Node IDs Rejected

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow with nodes having the same `id` value (e.g., two nodes with `id: "n1"`)
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - `ValidationError` raised
  - Error message contains "duplicate"

---

### TC-SCH-006: Orphaned Edge Source Rejected

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow where an edge's `from` references a node ID that does not exist
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - `ValidationError` raised
  - Error message names the unknown node ID

---

### TC-SCH-007: Orphaned Edge Target Rejected

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow where an edge's `to` references a node ID that does not exist
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - `ValidationError` raised
  - Error message names the unknown node ID

---

### TC-SCH-008: Empty Nodes List Rejected

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Construct a workflow with `nodes: []`
  2. Call `Workflow.model_validate(data)`
- **Expected Result**:
  - `ValidationError` raised
  - Error message mentions "at least one node"

---

### TC-SCH-009: ExecutionStatus Enum Contains All Required States

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Enumerate all `ExecutionStatus` values
- **Expected Result**:
  - Set equals `{"pending", "running", "waiting_approval", "retrying", "completed", "failed", "cancelled"}`

---

### TC-SCH-010: StepStatus Enum Contains All Required States

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Enumerate all `StepStatus` values
- **Expected Result**:
  - Set equals `{"pending", "running", "completed", "failed", "waiting_approval", "skipped"}`

---

### TC-SCH-011: ToolResult — Success With Output

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Create `ToolResult(success=True, output={"id": "msg_123"})`
- **Expected Result**:
  - `success` is `True`
  - `output["id"]` == `"msg_123"`
  - `error` is `None`
  - `warnings` is an empty list

---

### TC-SCH-012: ToolResult — Failure With Retryable Flag

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Create `ToolResult(success=False, error="Connection timeout", retryable=True)`
- **Expected Result**:
  - `success` is `False`
  - `error` == `"Connection timeout"`
  - `retryable` is `True`

---

### TC-SCH-013: ToolResult — Success With Warnings Escalates

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Create `ToolResult(success=True, output={}, warnings=["Threshold exceeded"])`
- **Expected Result**:
  - `success` is `True`
  - `warnings` list has one entry
  - This result should cause the verifier to return `ESCALATE` verdict

---

### TC-SCH-014: Workflow Serialization Round-Trip

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Create a valid `Workflow` object
  2. Serialize with `workflow_to_dict()`
  3. Deserialize with `workflow_from_dict()`
  4. Compare the original and deserialized workflows
- **Expected Result**:
  - Both workflows are equal
  - All fields are preserved

---

### TC-SCH-015: Edge Model With Alias "from"

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Create `Edge(from="n1", to="n2", condition="true")` using the alias
  2. Verify `edge.from_` == `"n1"` and `edge.to` == `"n2"`
  3. Serialize and verify the output uses `"from"` as the key
- **Expected Result**:
  - Alias works correctly for both input and output
  - `model_dump(by_alias=True)` produces `{"from": "n1", "to": "n2", "condition": "true"}`

---

## 3. Agent Tests — Planner, Compiler, Verifier

### TC-AGT-001: Planner Generates Valid Invoice Workflow From Prompt

- **Priority**: High
- **Preconditions**: Mocked Anthropic client returning valid invoice workflow JSON; tool registry is initialized
- **Test Steps**:
  1. Create `PlannerAgent` with mock LLM client returning invoice processing workflow JSON
  2. Call `planner.plan("Process invoices with approval for amounts over $100k")`
  3. Verify the result
- **Expected Result**:
  - `result.success` is `True`
  - `result.workflow.name` == `"Invoice Processing"`
  - `len(result.workflow.nodes)` == 7
  - All action nodes reference valid tools from the registry
  - Exactly one trigger and one end node
  - No duplicate node IDs
- **Edge Cases**:
  - LLM returns JSON wrapped in code fences (```json ... ```) → planner extracts correctly
  - LLM returns raw JSON without code fences → planner extracts correctly
  - LLM returns extra text before/after JSON → planner finds the JSON object
  - LLM returns a workflow with all 11 tools referenced → all validated successfully

---

### TC-AGT-002: Planner Handles Malformed LLM Output

- **Priority**: High
- **Preconditions**: Mocked LLM client that returns non-JSON text
- **Test Steps**:
  1. Create `PlannerAgent` with mock client returning `"Here is a workflow... sorry I cannot provide JSON."`
  2. Set `max_retries=3`
  3. Call `planner.plan("Process an invoice")`
- **Expected Result**:
  - After retries, `result.success` is `False`
  - `result.error` is not `None`
  - `result.raw_response` contains the last LLM response
  - A `PlanningError` could be raised (depending on implementation)

---

### TC-AGT-003: Planner Retry Logic — Repairs After First Failure

- **Priority**: High
- **Preconditions**: Mocked LLM client that returns malformed JSON on first call, valid JSON on second
- **Test Steps**:
  1. Create mock client with sequence: `[MALFORMED_RESPONSE, VALID_INVOICE_JSON]`
  2. Create `PlannerAgent` with this client
  3. Call `planner.plan("Process an invoice")`
- **Expected Result**:
  - `result.success` is `True`
  - `client.messages.create.call_count` == 2
  - Second call uses the repair prompt with error details
  - The conversation history includes the previous failed attempt

---

### TC-AGT-004: Planner Exhausts Retries and Returns Error

- **Priority**: Medium
- **Preconditions**: Mocked LLM client that always returns invalid output
- **Test Steps**:
  1. Create mock client returning malformed JSON for all calls
  2. Create `PlannerAgent` with `max_retries=2`
  3. Call `planner.plan("Process an invoice")`
- **Expected Result**:
  - `result.success` is `False`
  - `result.error` mentions "Failed to generate valid workflow after 2 retries"
  - `result.raw_response` contains the last response

---

### TC-AGT-005: Planner Rejects Unknown Tool References

- **Priority**: High
- **Preconditions**: Mocked LLM client returning a workflow with an action node using `"tool": "quantum_teleport"`
- **Test Steps**:
  1. Create `PlannerAgent` with mock client
  2. Call `planner.plan("Use quantum teleport to ship")`
- **Expected Result**:
  - `result.success` is `False`
  - Error message mentions the unknown tool name
  - Lists available tools in the error

---

### TC-AGT-006: Planner Metadata Extraction

- **Priority**: Medium
- **Preconditions**: Mocked LLM client returning invoice workflow JSON
- **Test Steps**:
  1. Create `PlannerAgent`, call `plan()`, get valid workflow
  2. Call `planner.get_planning_metadata(workflow)`
- **Expected Result**:
  - `metadata["node_count"]` == 7
  - `metadata["tools_used"]` contains `"extract_invoice_data"`, `"search_database"`, `"process_payment"`
  - `metadata["approval_gates"]` == 1
  - `metadata["has_branching"]` is `True`
  - `metadata["has_retry"]` is `False` (no retry_count > 0)
  - `metadata["complexity"]` is `"high"` (7 nodes > 8? No, 7 > 4 but not > 8, so "medium")
  - Wait, 7 > 4 = "medium" if we check: high > 8, medium > 4, else low. So 7 nodes → medium

---

### TC-AGT-007: Planner Handles Empty API Key Gracefully

- **Priority**: Medium
- **Preconditions**: `ANTHROPIC_API_KEY` is empty string
- **Test Steps**:
  1. Monkeypatch `settings.anthropic_api_key` to `""`
  2. Create `PlannerAgent`
  3. Call `planner.plan("Do something")`
- **Expected Result**:
  - Does not crash with `AttributeError` or `TypeError`
  - Returns a `PlanningResult` with either `success=True` (unlikely without API) or `success=False` with an error
  - `result` has `.success` and `.error` attributes

---

### TC-AGT-008: Planner Generates Linear Workflow

- **Priority**: Medium
- **Preconditions**: Mocked LLM client returning a simple 4-node linear workflow
- **Test Steps**:
  1. Create `PlannerAgent` with mock client returning linear workflow JSON
  2. Call `planner.plan("Generate a report and email it")`
- **Expected Result**:
  - `result.success` is `True`
  - `len(result.workflow.nodes)` == 4
  - Node types include exactly one `trigger` and one `end`
  - No condition or approval nodes

---

### TC-AGT-009: Compiler Builds StateGraph for Linear Workflow

- **Priority**: High
- **Preconditions**: Valid 3-node linear workflow (trigger → action → end)
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Call `compiler.compile(workflow)`
  3. Inspect the compiled result
- **Expected Result**:
  - Returns `CompiledWorkflow` instance
  - `node_order` contains all node IDs in sequence
  - `get_compiled()` returns a compiled LangGraph StateGraph
  - Entry point is the trigger node
  - End node connects to `END`

---

### TC-AGT-010: Compiler Rejects Workflow Without Trigger

- **Priority**: High
- **Preconditions**: Workflow with no trigger node
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Call `compiler.compile(workflow_without_trigger)`
- **Expected Result**:
  - Raises `CompilationError`
  - Error message contains "trigger"

---

### TC-AGT-011: Compiler Rejects Workflow With Multiple Triggers

- **Priority**: Medium
- **Preconditions**: Workflow with two trigger nodes
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Call `compiler.compile(workflow_with_two_triggers)`
- **Expected Result**:
  - Raises `CompilationError`
  - Error message contains "multiple triggers"

---

### TC-AGT-012: Compiler Handles Condition Nodes with True/False Branches

- **Priority**: High
- **Preconditions**: Workflow with a condition node having `condition="true"` and `condition="false"` edges
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Compile the branching workflow
- **Expected Result**:
  - Compilation succeeds
  - Condition node has `add_conditional_edges` applied
  - The routing maps `"true"` and `"false"` to the correct target nodes

---

### TC-AGT-013: Compiler Handles Approval Nodes

- **Priority**: High
- **Preconditions**: Workflow with an approval node
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Compile a workflow containing an approval node
- **Expected Result**:
  - Compilation succeeds
  - Approval node is present in the compiled graph
  - Approval node's executor will set `status` to `WAITING_APPROVAL`

---

### TC-AGT-014: Compiler Handles Retry Configuration on Nodes

- **Priority**: Low
- **Preconditions**: Workflow where an action node has `retry_count: 3` and `retry_delay: 2.0`
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Compile the workflow
  3. Retrieve the node definition
- **Expected Result**:
  - Node is compiled successfully
  - `retry_count` == 3 is preserved in the node definition
  - `retry_delay` == 2.0 is preserved

---

### TC-AGT-015: Compiler Minimal Workflow (Trigger + End Only)

- **Priority**: Low
- **Preconditions**: Workflow with only trigger and end nodes connected by one edge
- **Test Steps**:
  1. Create `WorkflowCompiler`
  2. Compile the minimal workflow
- **Expected Result**:
  - Compilation succeeds
  - `node_order` has 2 entries

---

### TC-AGT-016: Verifier Rule-Based — Success Verdict

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Create `VerifierAgent`
  2. Call `verifier._rule_based_verify("send_email", ToolResult(success=True, output={"id": "msg_123"}), "Email sent")`
- **Expected Result**:
  - `result.verdict` == `"SUCCESS"`
  - `result.confidence` == 0.95
  - `result.user_message` contains the tool name

---

### TC-AGT-017: Verifier Rule-Based — Retryable Failure

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Call `verifier._rule_based_verify("send_email", ToolResult(success=False, error="503 Service Unavailable", retryable=True), "Email sent")`
- **Expected Result**:
  - `result.verdict` == `"RETRY"`
  - `result.confidence` == 0.8

---

### TC-AGT-018: Verifier Rule-Based — Non-Retryable Failure

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Call `verifier._rule_based_verify("search_database", ToolResult(success=False, error="Auth failed", retryable=False), "Records found")`
- **Expected Result**:
  - `result.verdict` == `"FAIL"`
  - `result.confidence` == 0.9

---

### TC-AGT-019: Verifier Rule-Based — Warnings Cause Escalation

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Call `verifier._rule_based_verify("validate_invoice", ToolResult(success=True, output={"valid": True}, warnings=["Amount exceeds $100k"]), "Invoice valid")`
- **Expected Result**:
  - `result.verdict` == `"ESCALATE"`
  - `result.confidence` == 0.9
  - `result.user_message` mentions the warning

---

### TC-AGT-020: Verifier LLM-Based Verification With Mock

- **Priority**: Medium
- **Preconditions**: Mocked Anthropic client returning a verification JSON response
- **Test Steps**:
  1. Create `VerifierAgent` with mock client
  2. Monkeypatch `settings.anthropic_api_key` to `"fake-key"`
  3. Call `verifier.verify("send_email", ToolResult(success=True), "Email sent")`
- **Expected Result**:
  - LLM is called with the correct system prompt
  - Response is parsed correctly
  - Returns `VerificationResult` with verdict, confidence, and user_message from the LLM

---

### TC-AGT-021: Verifier Falls Back to Rule-Based on LLM Error

- **Priority**: Medium
- **Preconditions**: Mocked LLM client that raises an exception
- **Test Steps**:
  1. Create `VerifierAgent` with mock client that raises `Exception("API error")`
  2. Monkeypatch `settings.anthropic_api_key` to `"fake-key"`
  3. Call `verifier.verify("send_email", ToolResult(success=True), "Email sent")`
- **Expected Result**:
  - No exception propagates to the caller
  - Falls back to rule-based verification
  - Returns `VerificationResult(verdict="SUCCESS", ...)`

---

### TC-AGT-022: Planner Handles JSON in Code Fences

- **Priority**: Medium
- **Preconditions**: Mocked LLM client returning JSON wrapped in triple backticks
- **Test Steps**:
  1. Create `PlannerAgent` with mock client returning ```` ```json\n{...}\n``` ``
  2. Call `planner.plan("...")`
- **Expected Result**:
  - `result.success` is `True`
  - JSON is correctly extracted from within the code fences

---

### TC-AGT-023: Planner Handles JSON Embedded in Narrative Text

- **Priority**: Medium
- **Preconditions**: Mocked LLM client returning prose with JSON embedded (e.g., "Here's the workflow:\n{...}\nLet me know if you need changes.")
- **Test Steps**:
  1. Create `PlannerAgent` with mock client
  2. Call `planner.plan("...")`
- **Expected Result**:
  - `result.success` is `True`
  - JSON extracted from between first `{` and last `}`

---

### TC-AGT-024: Planner Adds Missing IDs to Nodes

- **Priority**: Low
- **Preconditions**: Mocked LLM client returning a workflow where some nodes lack `id` fields
- **Test Steps**:
  1. Create `PlannerAgent` with mock client
  2. Call `planner.plan("...")`
- **Expected Result**:
  - `result.success` is `True`
  - All nodes in `result.workflow.nodes` have non-empty `id` fields
  - Missing IDs are filled with pattern `n1`, `n2`, etc.

---

## 4. Tool Execution Tests

### TC-TOOL-001: send_email — Successful Send

- **Priority**: High
- **Preconditions**: Tool registry initialized; mock email store is available
- **Test Steps**:
  1. Execute `send_email` with `{"to": "user@example.com", "subject": "Hello", "body": "World"}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["message_id"]` matches pattern `msg_\d{4}`
  - `result.output["to"]` == `"user@example.com"`
  - Email is stored in `MOCK_EMAILS`
- **Edge Cases**:
  - Unicode in subject/body (e.g., Japanese, emoji) → stored correctly
  - Very long body (10,000 characters) → stored correctly
  - Multiple recipients as comma-separated string → stored as a single `to` value

---

### TC-TOOL-002: send_email — Missing Required Field

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `send_email` with `{"subject": "No recipient"}`
- **Expected Result**:
  - `result.success` is `False`
  - `result.error` mentions "to" or "required"
  - `result.retryable` is `False`
  - No email is added to `MOCK_EMAILS`

---

### TC-TOOL-003: search_database — Valid Table Query

- **Priority**: High
- **Preconditions**: Tool registry initialized; `purchase_orders` table has seed data
- **Test Steps**:
  1. Execute `search_database` with `{"table": "purchase_orders"}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["records"]` is a list of records
  - `result.output["count"]` matches `len(records)`
  - Records include seed data (Acme Corp, Globex Inc)
- **Edge Cases**:
  - Query with additional `query` parameter → should not crash
  - Query with empty table name → `result.success` is `False`

---

### TC-TOOL-004: search_database — Invalid Table Name

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `search_database` with `{"table": "nonexistent_table"}`
- **Expected Result**:
  - `result.success` is `False`
  - `result.error` lists available tables
  - `result.retryable` is `False`

---

### TC-TOOL-005: request_human_approval — Creates Approval Record

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `request_human_approval` with `{"reason": "Large invoice needs review", "context": {"amount": 250000}, "approver_role": "finance_team"}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["status"]` == `"pending"`
  - `result.output["approval_id"]` matches pattern `approval_\d{4}`
  - Approval record is created in `MOCK_APPROVALS`

---

### TC-TOOL-006: wait — Waits Specified Duration

- **Priority**: Low
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `wait` with `{"seconds": 2}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["waited_seconds"]` == 2 (capped at 5)
- **Edge Cases**:
  - `seconds: 0` → waits 0 seconds (or 1 due to min)
  - `seconds: 100` → capped at 5 seconds
  - Negative seconds → behavior depends on implementation

---

### TC-TOOL-007: extract_invoice_data — Returns Mock Invoice

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `extract_invoice_data` with `{"document": "inv_2024_001.pdf"}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["vendor"]` == `"Acme Corp"`
  - `result.output["amount"]` == `45000`
  - `result.output["invoice_number"]` == `"INV-2024-001"`
  - `result.output["line_items"]` is a non-empty list

---

### TC-TOOL-008: process_payment — Processes Mock Payment

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `process_payment` with `{"invoice_id": "inv_001", "amount": 45000}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["payment_id"]` matches pattern `pay_\d{4}`
  - `result.output["status"]` == `"processed"`
  - `result.output["amount"]` == `45000`

---

### TC-TOOL-009: update_database — Updates Existing Record

- **Priority**: Medium
- **Preconditions**: Tool registry initialized; `invoices` table has seed data
- **Test Steps**:
  1. Execute `update_database` with `{"table": "invoices", "id": "inv_001", "updates": {"status": "paid"}}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["updated"]` is `True`
  - The record in `MOCK_DB_RECORDS["invoices"]` is updated
- **Edge Cases**:
  - Update non-existent record → `result.success` is `False`
  - Update non-existent table → `result.success` is `False`

---

### TC-TOOL-010: create_ticket — Creates Support Ticket

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `create_ticket` with `{"title": "Server down", "priority": "critical", "assignee": "oncall_team"}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["ticket_id"]` matches pattern `ticket_\d{4}`
  - Ticket is stored in `MOCK_TICKETS`
  - Ticket has correct title, priority, assignee

---

### TC-TOOL-011: Unknown Tool Execution Raises Error

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `registry.execute("nonexistent_tool", {})`
- **Expected Result**:
  - Raises `UnknownToolError`
  - Error message contains the tool name and lists available tools

---

### TC-TOOL-012: send_slack_message — Successful Send

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `send_slack_message` with `{"channel": "#engineering", "message": "Deployment complete"}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["message_id"]` matches pattern `slack_\d{4}`
  - Message is stored in `MOCK_SLACK_MESSAGES`

---

### TC-TOOL-013: send_slack_message — Missing Channel

- **Priority**: Low
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `send_slack_message` with `{"message": "Hello"}`
- **Expected Result**:
  - `result.success` is `False`
  - `result.error` mentions "channel"

---

### TC-TOOL-014: Permission Levels — AUTO Executes Without Confirmation

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Verify `send_email` has `permission == PermissionLevel.AUTO`
  2. Execute the tool
- **Expected Result**:
  - Tool executes immediately without any confirmation step
  - Permission is correctly registered

---

### TC-TOOL-015: Permission Levels — CONFIRM Requires Human Confirmation

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Verify `process_payment` has `permission == PermissionLevel.CONFIRM`
  2. Verify `update_database` has `permission == PermissionLevel.CONFIRM`
- **Expected Result**:
  - These tools are registered with `CONFIRM` permission level
  - In a real system, they would require human confirmation before execution

---

### TC-TOOL-016: Permission Levels — HUMAN_ONLY Cannot Be Auto-Executed

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Verify `request_human_approval` has `permission == PermissionLevel.HUMAN_ONLY`
- **Expected Result**:
  - Tool is registered with `HUMAN_ONLY` permission
  - In the workflow runner, this tool pauses execution for human intervention

---

### TC-TOOL-017: validate_invoice — Detects Large Amounts

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `validate_invoice` with `{"amount": 150000, "purchase_order_id": "po_001"}`
  2. Execute `validate_invoice` with `{"amount": 50000, "purchase_order_id": "po_001"}`
- **Expected Result**:
  - Amount 150,000: `result.success` is `True`, `result.warnings` contains threshold message
  - Amount 50,000: `result.success` is `True`, `result.warnings` is empty

---

### TC-TOOL-018: create_calendar_event — Creates Event

- **Priority**: Low
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `create_calendar_event` with `{"title": "Board Meeting", "date": "2024-12-01", "attendees": ["ceo", "cfo"]}`
- **Expected Result**:
  - `result.success` is `True`
  - `result.output["event_id"]` matches pattern `evt_\d{4}`
  - Event is stored in `MOCK_CALENDAR_EVENTS`

---

## 5. Workflow Runner Tests

### TC-RUN-001: Happy Path — Simple Linear Workflow

- **Priority**: High
- **Preconditions**: A simple 3-node workflow (trigger → action → end) is persisted in DB
- **Test Steps**:
  1. Create `WorkflowRunner` with DB session
  2. Call `runner.run(workflow_id)`
  3. Examine the returned execution
- **Expected Result**:
  - `execution.status` == `ExecutionStatus.COMPLETED`
  - `len(execution.steps)` == 3 (one for each node)
  - All steps have `status == StepStatus.COMPLETED`
  - Steps are ordered by execution sequence
  - Each step has non-null `started_at` and `completed_at`

---

### TC-RUN-002: Happy Path — Branching Workflow (Onboarding)

- **Priority**: High
- **Preconditions**: Employee onboarding workflow is persisted (has condition node)
- **Test Steps**:
  1. Create `WorkflowRunner`
  2. Call `runner.run(onboarding_workflow_id)`
  3. Examine the execution
- **Expected Result**:
  - `execution.status` == `ExecutionStatus.COMPLETED` (onboarding has no approval gate)
  - `len(execution.steps)` >= 4
  - Condition node result determines the branch taken
  - At least one of the branch paths is exercised

---

### TC-RUN-003: Approval Pause and Resume Flow

- **Priority**: High
- **Preconditions**: Invoice processing workflow is persisted; it has an approval node
- **Test Steps**:
  1. Create `WorkflowRunner`, run the invoice workflow
  2. Verify execution pauses at `WAITING_APPROVAL`
  3. Use `ApprovalService` to approve the pending approval
  4. Call `runner.resume(execution_id)`
  5. Verify the resumed execution
- **Expected Result**:
  - After initial run: `execution.status` == `WAITING_APPROVAL`
  - At least one pending approval exists linked to the execution
  - After resume: `resumed.status` == `COMPLETED`
  - Steps from before approval are preserved
  - Steps after approval are added

---

### TC-RUN-004: Approval Rejection Cancels Workflow

- **Priority**: High
- **Preconditions**: Invoice processing workflow persisted
- **Test Steps**:
  1. Run the invoice workflow
  2. Reject the approval with reason `"Amount exceeds quarterly budget"`
  3. Query the execution directly from DB
- **Expected Result**:
  - Initial run: status is `WAITING_APPROVAL`
  - After rejection: execution status is `CANCELLED`
  - `rejection_reason` is stored in the approval record

---

### TC-RUN-005: Cancel Running Workflow

- **Priority**: High
- **Preconditions**: A workflow is currently running
- **Test Steps**:
  1. Run a workflow
  2. If status is `RUNNING` or `WAITING_APPROVAL`, call `runner.cancel(execution_id)`
  3. Examine the cancelled execution
- **Expected Result**:
  - `cancelled.status` == `ExecutionStatus.CANCELLED`
  - `cancelled.completed_at` is set
  - Steps that were already created remain in the database

---

### TC-RUN-006: Context Propagation Between Nodes

- **Priority**: High
- **Preconditions**: Invoice processing workflow persisted
- **Test Steps**:
  1. Run the workflow with context `{"amount": 500000, "vendor": "MegaCorp", "custom_field": "test_value"}`
  2. After execution, examine the execution context
- **Expected Result**:
  - Context values provided at start are available to all nodes
  - Tool outputs (e.g., extracted invoice data) are added to context
  - Condition expressions can reference context keys (e.g., `amount > 100000` evaluates based on context)

---

### TC-RUN-007: Context-Driven Branching (Amount > Threshold)

- **Priority**: High
- **Preconditions**: Invoice processing workflow persisted
- **Test Steps**:
  1. Run with `context = {"amount": 500000}` (above threshold)
  2. Run again with `context = {"amount": 5000}` (below threshold)
- **Expected Result**:
  - High amount run: pauses at `WAITING_APPROVAL` (condition evaluates to `true`)
  - Low amount run: proceeds past condition to payment directly (condition evaluates to `false`)
  - Both runs complete or pause as expected

---

### TC-RUN-008: Multiple Runs Without State Leakage

- **Priority**: High
- **Preconditions**: A workflow is persisted
- **Test Steps**:
  1. Run the workflow → execution A
  2. Run the same workflow again → execution B
  3. Compare executions A and B
- **Expected Result**:
  - `exec_a.id` != `exec_b.id`
  - Both executions have their own independent step records
  - Steps from A do not appear in B and vice versa
  - Context from A does not leak into B

---

### TC-RUN-009: Error Handling — Unknown Workflow

- **Priority**: High
- **Preconditions**: None
- **Test Steps**:
  1. Call `runner.run("nonexistent_workflow_id")`
- **Expected Result**:
  - Raises `WorkflowNotFoundError`
  - Error message includes the workflow ID

---

### TC-RUN-010: Step Observability — Timestamps and Attempt Counts

- **Priority**: Medium
- **Preconditions**: Any workflow is persisted
- **Test Steps**:
  1. Run a workflow
  2. Examine every step in the execution
- **Expected Result**:
  - Every step has non-null `started_at` (datetime)
  - Every step has non-null `completed_at` (datetime)
  - `started_at` <= `completed_at` for each step
  - `attempt_count` >= 1 for each step
  - Each step has `node_id`, `node_type`, `node_name`

---

### TC-RUN-011: Template Variable Substitution in Tool Inputs

- **Priority**: Medium
- **Preconditions**: A workflow where an action node has inputs with template variables like `"{{vendor_name}}"`
- **Test Steps**:
  1. Ensure context contains `vendor_name: "Acme Corp"`
  2. Run the workflow
  3. Examine the step's `tool_inputs`
- **Expected Result**:
  - Template variables are resolved: `{{vendor_name}}` → `"Acme Corp"`
  - Non-template values are passed through unchanged
  - If a template variable is not in context, it remains unresolved or is handled gracefully

---

### TC-RUN-012: Resume From Non-Approval State Raises Error

- **Priority**: Medium
- **Preconditions**: An execution in `COMPLETED` status
- **Test Steps**:
  1. Call `runner.resume(completed_execution_id)`
- **Expected Result**:
  - Raises `RunnerError`
  - Error message indicates the execution cannot be resumed in its current state

---

### TC-RUN-013: Resume Non-Existent Execution

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Call `runner.resume("nonexistent_exec_id")`
- **Expected Result**:
  - Raises `WorkflowNotFoundError`

---

### TC-RUN-014: Cancel Non-Existent Execution

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Call `runner.cancel("nonexistent_exec_id")`
- **Expected Result**:
  - Raises `WorkflowNotFoundError`

---

### TC-RUN-015: Action Node Without Tool Field Fails Gracefully

- **Priority**: Medium
- **Preconditions**: A workflow where an action node has no `tool` field
- **Test Steps**:
  1. Compile and run this workflow
- **Expected Result**:
  - The node execution fails with a clear error
  - Step status is `FAILED`
  - Step `error` field contains "Action node missing 'tool' field"
  - Workflow execution status becomes `FAILED`

---

### TC-RUN-016: Condition Node Eval Error Defaults to True Branch

- **Priority**: Medium
- **Preconditions**: A workflow with a condition node whose expression references a context variable that doesn't exist
- **Test Steps**:
  1. Run workflow with context missing the variable used in the expression
  2. The condition expression throws an exception on eval
- **Expected Result**:
  - Condition node defaults to `"true"` branch on eval error
  - Workflow continues without crashing
  - Step status for condition node is `COMPLETED`

---

### TC-RUN-017: Wait Node Completes Without Actual Delay

- **Priority**: Low
- **Preconditions**: A workflow with a wait node
- **Test Steps**:
  1. Run a workflow containing a wait node
  2. Verify the wait node's step
- **Expected Result**:
  - Wait node step has `status == StepStatus.COMPLETED`
  - Duration is capped at 5 seconds (per implementation)

---

## 6. Approval Service Tests

### TC-APR-001: Create Pending Approval Request

- **Priority**: High
- **Preconditions**: `ApprovalService` with active DB session
- **Test Steps**:
  1. Call `service.create_request("exec_001", "n3", "Amount exceeds threshold", {"amount": 500000}, "manager")`
- **Expected Result**:
  - Returns `ApprovalRequestModel` instance
  - `approval.id` starts with `"approval_"`
  - `approval.status` == `"pending"`
  - `approval.execution_id` == `"exec_001"`
  - `approval.node_id` == `"n3"`
  - `approval.reason` == `"Amount exceeds threshold"`
  - `approval.context` == `{"amount": 500000}`
  - `approval.approver_role` == `"manager"`
  - `approval.created_at` is set

---

### TC-APR-002: Approve Sets All Required Fields

- **Priority**: High
- **Preconditions**: A pending approval request exists
- **Test Steps**:
  1. Call `service.approve(approval_id, approver_id="user_123")`
  2. Examine the returned approval
- **Expected Result**:
  - `approval.status` == `"approved"`
  - `approval.approver_id` == `"user_123"`
  - `approval.approved_at` is not `None`
  - `approval.resolved_at` is not `None`

---

### TC-APR-003: Reject Sets All Required Fields

- **Priority**: High
- **Preconditions**: A pending approval request exists
- **Test Steps**:
  1. Call `service.reject(approval_id, approver_id="user_456", reason="Budget not available")`
- **Expected Result**:
  - `approval.status` == `"rejected"`
  - `approval.approver_id` == `"user_456"`
  - `approval.rejection_reason` == `"Budget not available"`
  - `approval.resolved_at` is not `None`

---

### TC-APR-004: Double-Approve Raises Error

- **Priority**: High
- **Preconditions**: An approval has already been approved
- **Test Steps**:
  1. Approve the approval once
  2. Attempt to approve the same approval again with a different approver
- **Expected Result**:
  - Raises `ApprovalAlreadyResolvedError`
  - Error message contains the approval ID and current status

---

### TC-APR-005: Double-Reject Raises Error

- **Priority**: High
- **Preconditions**: An approval has already been rejected
- **Test Steps**:
  1. Reject the approval once
  2. Attempt to reject the same approval again
- **Expected Result**:
  - Raises `ApprovalAlreadyResolvedError`

---

### TC-APR-006: Approve Already-Rejected Approval Raises Error

- **Priority**: Medium
- **Preconditions**: An approval has been rejected
- **Test Steps**:
  1. Reject an approval
  2. Attempt to approve it
- **Expected Result**:
  - Raises `ApprovalAlreadyResolvedError`

---

### TC-APR-007: Reject Already-Approved Approval Raises Error

- **Priority**: Medium
- **Preconditions**: An approval has been approved
- **Test Steps**:
  1. Approve an approval
  2. Attempt to reject it
- **Expected Result**:
  - Raises `ApprovalAlreadyResolvedError`

---

### TC-APR-008: List Pending Returns Only Pending

- **Priority**: Medium
- **Preconditions**: A mix of pending, approved, and rejected approval requests exist
- **Test Steps**:
  1. Create 4 approvals
  2. Approve 1, reject 1
  3. Call `service.list_pending()`
- **Expected Result**:
  - Returns exactly 2 approvals (the pending ones)
  - Returned approvals are ordered by `created_at` descending

---

### TC-APR-009: Get Existing Approval by ID

- **Priority**: Low
- **Preconditions**: An approval exists in the database
- **Test Steps**:
  1. Call `service.get(approval_id)`
- **Expected Result**:
  - Returns the `ApprovalRequestModel` with matching ID
  - All fields match the created approval

---

### TC-APR-010: Get Non-Existent Approval Returns None

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Call `service.get("approval_nonexistent")`
- **Expected Result**:
  - Returns `None`

---

### TC-APR-011: Approve Non-Existent Approval Raises Error

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Call `service.approve("approval_nonexistent", "user_1")`
- **Expected Result**:
  - Raises `ApprovalNotFoundError`

---

### TC-APR-012: Reject Non-Existent Approval Raises Error

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Call `service.reject("approval_nonexistent", "user_1", "Reason")`
- **Expected Result**:
  - Raises `ApprovalNotFoundError`

---

### TC-APR-013: Approval Persists Across Session Close/Reopen

- **Priority**: Medium
- **Preconditions**: SQLite in-memory database
- **Test Steps**:
  1. Create an approval in a session
  2. Close the session
  3. Open a new session with a new `ApprovalService`
  4. Retrieve the approval by ID
- **Expected Result**:
  - Approval is found in the new session
  - All fields (reason, context, approver_role) are preserved
  - Note: This tests within the same in-memory DB engine. For true persistence, use a file-based DB.

---

### TC-APR-014: Create Approval With Default Parameters

- **Priority**: Low
- **Preconditions**: `ApprovalService` with active session
- **Test Steps**:
  1. Call `service.create_request("exec_001", "n1", "Review needed")` without optional params
- **Expected Result**:
  - Approval is created
  - `approver_role` is `None`
  - `context` is `{}`
  - `requested_by` defaults to `"system"`

---

## 7. Integration / End-to-End Tests

### TC-E2E-001: Full Invoice Processing Workflow

- **Priority**: High
- **Preconditions**: Invoice processing workflow definition is loaded and persisted
- **Test Steps**:
  1. Create a database session and persist the invoice processing workflow
  2. Create `WorkflowRunner` with the session
  3. Run the workflow with context `{"amount": 250000, "vendor": "Acme Corp"}`
  4. Verify execution pauses at the approval node
  5. Use `ApprovalService` to approve the request
  6. Resume the workflow
  7. Verify the final execution status
- **Expected Result**:
  - Initial run completes up to the approval node (status: `WAITING_APPROVAL`)
  - Steps: trigger → extract_invoice_data → search_database → condition (true branch) → approval node
  - After approval and resume: payment step executes, end node reached
  - Final status: `COMPLETED`
  - All steps have appropriate statuses
  - Extracted invoice data is available in context for downstream nodes
- **Edge Cases**:
  - If `amount` in context is below threshold → condition evaluates false, skips approval, proceeds directly to payment

---

### TC-E2E-002: Full Employee Onboarding Workflow

- **Priority**: High
- **Preconditions**: Employee onboarding workflow persisted
- **Test Steps**:
  1. Persist the onboarding workflow
  2. Run it without special context
  3. Verify all steps execute
- **Expected Result**:
  - Status: `COMPLETED` (no approval gate)
  - All 6+ steps execute
  - Email is sent to new employee
  - Condition node evaluates (documents verified or not)
  - Appropriate branch is taken (HR notification vs. reminder)
  - Manager is notified in both paths

---

### TC-E2E-003: Full Customer Support Workflow

- **Priority**: High
- **Preconditions**: Customer support workflow persisted
- **Test Steps**:
  1. Persist the customer support workflow
  2. Run the workflow
  3. Verify the complaint handling flow
- **Expected Result**:
  - Customer is identified via database search
  - Order is found
  - Delivery status is checked
  - Support ticket is created
  - Condition evaluates escalation need
  - Either response email is sent OR ticket is escalated
  - Final status: `COMPLETED`

---

### TC-E2E-004: Workflow With Retry on Failure

- **Priority**: Medium
- **Preconditions**: A workflow where an action node has `retry_count: 3`
- **Test Steps**:
  1. Create a workflow with a tool that fails transiently
  2. Run the workflow
  3. Observe the retry behavior
- **Expected Result**:
  - The retry configuration is preserved in the compiled workflow
  - Note: The current implementation stores `retry_count` but does not implement automatic retry logic in the runner — this test documents the expected behavior when retry logic is added
  - If a tool returns `retryable=True`, the system should attempt the tool again up to `retry_count` times

---

### TC-E2E-005: Workflow With Multiple Condition Nodes

- **Priority**: Medium
- **Preconditions**: A workflow with 2+ condition nodes in sequence
- **Test Steps**:
  1. Create a workflow: trigger → condition1 → action_a/action_b → condition2 → action_c/action_d → end
  2. Run with various context combinations
  3. Verify all 4 possible paths are reachable
- **Expected Result**:
  - Both condition nodes evaluate independently
  - Each condition routes to the correct branch
  - Final state reflects the combined results of both conditions

---

### TC-E2E-006: Concurrent Workflow Executions

- **Priority**: Medium
- **Preconditions**: A workflow is persisted; multiple async tasks can be spawned
- **Test Steps**:
  1. Start 3 workflow executions concurrently (using `asyncio.gather`)
  2. Wait for all to complete
  3. Verify each execution
- **Expected Result**:
  - All 3 executions complete independently
  - Each has a unique execution ID
  - Steps from one execution do not appear in another
  - Mock data (emails, tickets) from all runs are accumulated correctly
  - No race conditions or database deadlocks

---

### TC-E2E-007: Workflow End-to-End With Approval Rejection

- **Priority**: High
- **Preconditions**: Invoice processing workflow persisted
- **Test Steps**:
  1. Run the invoice workflow
  2. When it pauses at approval, reject with reason `"Invoice fraudulent"`
  3. Verify the workflow is cancelled
  4. Verify no payment was processed
- **Expected Result**:
  - Workflow runs through extraction and search steps
  - Pauses at approval node
  - After rejection: status is `CANCELLED`
  - Steps up to and including the approval node are recorded
  - No payment step was executed

---

### TC-E2E-008: Workflow Context Accumulation Across Nodes

- **Priority**: High
- **Preconditions**: Invoice processing workflow persisted
- **Test Steps**:
  1. Run with initial context `{"run_id": "test_001"}`
  2. After completion, examine `execution.context`
- **Expected Result**:
  - Initial context key `run_id` is preserved
  - Tool outputs from `extract_invoice_data` are added (vendor, amount, invoice_number)
  - Tool outputs from `search_database` are added (records, count)
  - Context grows as nodes execute

---

### TC-E2E-009: Workflow With Wait Node in Sequence

- **Priority**: Low
- **Preconditions**: A workflow: trigger → action → wait(2s) → action → end
- **Test Steps**:
  1. Run the workflow
  2. Measure total execution time
- **Expected Result**:
  - Workflow completes with `COMPLETED` status
  - Wait node step is present in steps list
  - Wait node has `status == COMPLETED`
  - Total time includes the wait duration (capped at 5s)

---

### TC-E2E-010: Database Transaction Rollback on Runner Failure

- **Priority**: High
- **Preconditions**: A workflow that will fail during execution (e.g., with an invalid tool)
- **Test Steps**:
  1. Run a workflow where an action node references a tool that throws an exception
  2. Catch the `RunnerError`
  3. Verify database state
- **Expected Result**:
  - `RunnerError` is raised
  - Execution record exists with `status == FAILED`
  - `error_message` is set
  - Steps created before the failure are persisted
  - The failed step has `status == FAILED` and an error message

---

## 8. Edge Cases & Stress Tests

### TC-EDGE-001: Very Large Workflow (50+ Nodes)

- **Priority**: Medium
- **Preconditions**: A workflow definition with 50+ nodes is constructed
- **Test Steps**:
  1. Create a workflow with 60 nodes (trigger → 58 actions → end)
  2. Compile the workflow
  3. Run the workflow
- **Expected Result**:
  - Compilation succeeds
  - `node_order` contains all 60 node IDs
  - Execution completes without memory errors
  - All 60 steps are recorded
  - Compilation and execution complete within reasonable time (< 10s)

---

### TC-EDGE-002: Circular Dependency Detection

- **Priority**: Medium
- **Preconditions**: A workflow definition where edges form a cycle (e.g., n1 → n2 → n3 → n1)
- **Test Steps**:
  1. Construct a workflow with a circular edge pattern
  2. Try to compile and run it
- **Expected Result**:
  - **Current behavior**: LangGraph may enter an infinite loop or hang
  - **Expected improvement**: The system should detect cycles and raise a `CompilationError`
  - Test documents the current limitation

---

### TC-EDGE-003: Missing Tool Handler at Runtime

- **Priority**: High
- **Preconditions**: A workflow persisted with a node referencing a tool that exists in the registry at compile time
- **Test Steps**:
  1. Remove a tool from the registry after the workflow is compiled
  2. Run the workflow
- **Expected Result**:
  - The tool execution raises `UnknownToolError`
  - The step is marked as `FAILED`
  - The error is captured in the step's `error` field
  - Workflow does not crash the server

---

### TC-EDGE-004: Node Execution Timeout

- **Priority**: Medium
- **Preconditions**: A tool implementation that takes longer than the configured timeout
- **Test Steps**:
  1. Configure `default_tool_timeout` to a low value (e.g., 1 second)
  2. Execute a tool that takes longer
- **Expected Result**:
  - Tool execution is terminated after timeout
  - `ToolResult.success` is `False`
  - Error message indicates a timeout
  - Workflow continues or fails gracefully

---

### TC-EDGE-005: Malformed Context Data

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Run a workflow with context containing:
     - `None` values
     - Circular references (if possible)
     - Very deeply nested objects (10+ levels)
     - Non-serializable objects (e.g., datetime objects)
- **Expected Result**:
  - Context with `None` values → handled gracefully
  - Deeply nested objects → serialized correctly in DB
  - Non-serializable values → cause a controlled error, not a crash
  - Workflow execution is resilient to context quality issues

---

### TC-EDGE-006: Database Connection Loss During Execution

- **Priority**: Medium
- **Preconditions**: A running workflow execution
- **Test Steps**:
  1. Start a workflow execution
  2. Simulate DB connection failure (close the session mid-execution)
  3. Attempt to continue or recover
- **Expected Result**:
  - A controlled error is raised (not an unhandled exception)
  - Partial execution state is preserved where possible
  - The system does not crash the server process

---

### TC-EDGE-007: Empty Workflow Prompt to Planner

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Call `planner.plan("")` with an empty string
  2. Call `planner.plan("   ")` with whitespace only
- **Expected Result**:
  - Empty string → planner sends it to LLM, LLM may return invalid JSON → planner returns `PlanningResult` with `success=False`
  - Whitespace only → same behavior
  - No unhandled exception

---

### TC-EDGE-008: Workflow With Only Trigger and End (No Intermediate Nodes)

- **Priority**: Low
- **Preconditions**: A workflow with trigger and end connected directly
- **Test Steps**:
  1. Compile and run a 2-node workflow
- **Expected Result**:
  - Compilation succeeds
  - Execution completes
  - `status` == `COMPLETED`
  - 2 steps are recorded (trigger + end)

---

### TC-EDGE-009: Unicode and Special Characters in Workflow Names and Inputs

- **Priority**: Medium
- **Preconditions**: None
- **Test Steps**:
  1. Create a workflow with:
     - Name: `"处理发票 🧾 — Process Invoices"`
     - Node names with emoji, Chinese characters, RTL text
     - Tool inputs with special characters: SQL-like strings, HTML, null bytes
  2. Persist and run the workflow
- **Expected Result**:
  - Workflow is persisted correctly (UTF-8 encoding)
  - Workflow runs without encoding errors
  - Special characters in inputs are passed to tools correctly
  - Database stores all characters correctly

---

### TC-EDGE-010: Condition Node With Malformed Expression

- **Priority**: Medium
- **Preconditions**: A workflow where a condition node has an invalid Python expression
- **Test Steps**:
  1. Create a workflow with `expression: "amount >>> 100000"` (invalid Python)
  2. Run the workflow
- **Expected Result**:
  - `eval()` raises a `SyntaxError` or similar
  - Condition node catches the exception
  - Defaults to `"true"` branch (per implementation)
  - Workflow continues without crashing

---

### TC-EDGE-011: Workflow With Disconnected Nodes

- **Priority**: Low
- **Preconditions**: A workflow where some nodes are not connected to any edge
- **Test Steps**:
  1. Create a workflow with 5 nodes but only 3 edges (2 nodes orphaned)
  2. Compile the workflow
  3. Run it
- **Expected Result**:
  - Compilation succeeds (orphaned nodes are simply not connected)
  - Only connected nodes are executed
  - Orphaned nodes are never reached
  - Workflow completes through the connected path

---

### TC-EDGE-012: Approval Timeout Scenario

- **Priority**: Medium
- **Preconditions**: An approval request exists with a configured timeout (48 hours)
- **Test Steps**:
  1. Create an approval request
  2. Simulate time passing beyond the approval timeout
  3. Check the approval status
- **Expected Result**:
  - **Current behavior**: No automatic timeout enforcement is implemented
  - **Expected improvement**: After 48 hours, the approval should auto-reject or auto-escalate
  - Test documents the current limitation

---

### TC-EDGE-013: Extremely Long Context Values

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Run a workflow with context containing a 100,000-character string value
  2. Verify the execution
- **Expected Result**:
  - Context is stored in the database
  - No truncation or encoding errors
  - Template substitution works with long values

---

### TC-EDGE-014: Empty Tool Inputs

- **Priority**: Low
- **Preconditions**: A workflow where an action node has `inputs: {}` or no inputs defined
- **Test Steps**:
  1. Create a workflow where `send_email` is called with empty inputs
  2. Run the workflow
- **Expected Result**:
  - Tool executes (or fails gracefully if required fields are missing)
  - `send_email` with empty inputs → fails with "Missing required field: 'to'"

---

### TC-EDGE-015: Workflow Execution ID Collision

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Create many workflow executions rapidly (100+)
  2. Verify all execution IDs are unique
- **Expected Result**:
  - All execution IDs are unique
  - No collisions in the ID space (`exec_` + 8 hex chars)
  - With 100 executions, collision probability is negligible

---

## 9. Security Tests

### TC-SEC-001: SQL Injection in Tool Inputs

- **Priority**: High
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Execute `search_database` with `{"table": "purchase_orders; DROP TABLE workflows; --"}`
  2. Execute `update_database` with `{"table": "invoices", "id": "inv_001; DROP TABLE workflows; --", "updates": {}}`
  3. Verify the workflows table still exists
- **Expected Result**:
  - Tool returns `success=False` for invalid table names
  - No SQL injection occurs (parameterized queries or table name validation)
  - The workflows table is intact
  - Application does not crash

---

### TC-SEC-002: XSS in Workflow Names and Descriptions

- **Priority**: Medium
- **Preconditions**: FastAPI test client
- **Test Steps**:
  1. Create a workflow with name: `"<script>alert('XSS')</script>"`
  2. Create a workflow with description containing HTML tags and JavaScript
  3. Retrieve the workflow via API
  4. Check the response
- **Expected Result**:
  - Workflow is persisted with the raw name/description
  - FastAPI's JSON serialization escapes HTML in the response
  - No script execution occurs when viewing the API response
  - Note: This is a backend test — frontend should also sanitize

---

### TC-SEC-003: Permission Escalation via Approval

- **Priority**: High
- **Preconditions**: An approval request exists with `approver_role: "finance_team"`
- **Test Steps**:
  1. Attempt to approve the approval as a user who is NOT in the finance_team role
  2. Attempt to approve as a user with a different role
- **Expected Result**:
  - **Current behavior**: The API accepts any `approver_id` without role validation
  - **Expected improvement**: The system should validate that the approver belongs to the required `approver_role`
  - Test documents the current limitation

---

### TC-SEC-004: Unauthorized Cancellation of Another User's Execution

- **Priority**: High
- **Preconditions**: Two executions exist, belonging to different users
- **Test Steps**:
  1. Try to cancel execution B using execution A's credentials
  2. Try to cancel with no authentication
- **Expected Result**:
  - **Current behavior**: No authentication/authorization middleware exists
  - **Expected improvement**: Only the workflow owner or an admin should be able to cancel
  - Test documents the current limitation

---

### TC-SEC-005: Environment Variable Exposure

- **Priority**: Medium
- **Preconditions**: API server is running
- **Test Steps**:
  1. Check that `/api/health` and other endpoints do not expose `ANTHROPIC_API_KEY`
  2. Check that error messages do not leak API keys
  3. Check that the `/api/tools` endpoint does not expose internal configuration
- **Expected Result**:
  - No API keys, database URLs, or secrets appear in any API response
  - Error messages are generic and don't expose internals
  - Configuration values like `planner_temperature` are not exposed

---

### TC-SEC-006: Code Injection via Condition Expression (eval)

- **Priority**: High
- **Preconditions**: A workflow with a condition node
- **Test Steps**:
  1. Create a workflow with `expression: "__import__('os').system('rm -rf /')"`
  2. Run the workflow
  3. Verify system integrity
- **Expected Result**:
  - The `eval()` call in the compiler uses `{"__builtins__": {}}` as globals
  - `__import__` is not available → raises `NameError`
  - Condition defaults to `"true"` branch
  - System is not compromised
  - **Recommendation**: Replace `eval()` with a safe expression parser (e.g., `simpleeval` or AST-based evaluation)

---

### TC-SEC-007: Oversized Payload DoS Protection

- **Priority**: Medium
- **Preconditions**: API server is running
- **Test Steps**:
  1. Send a request with a 50MB JSON payload to `/api/workflows/generate`
  2. Send a request with deeply nested JSON (1000 levels deep)
- **Expected Result**:
  - Server returns `413 Payload Too Large` or handles it gracefully
  - Server does not crash or hang
  - Memory usage remains bounded

---

### TC-SEC-008: Tool Input Schema Validation

- **Priority**: Medium
- **Preconditions**: Tool registry initialized
- **Test Steps**:
  1. Attempt to execute tools with inputs containing unexpected types
  2. Attempt to inject Python objects via tool inputs
- **Expected Result**:
  - Inputs are validated against the tool's `input_schema`
  - Type mismatches are handled gracefully
  - No code injection via tool inputs

---

### TC-SEC-009: Workflow Name Length Limit

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Create a workflow with a 10,000-character name
  2. Persist and retrieve it
- **Expected Result**:
  - Name is stored correctly
  - Database column can accommodate the length (TEXT type)
  - API response includes the full name

---

### TC-SEC-010: No Sensitive Data in Mock Tool Outputs

- **Priority**: Low
- **Preconditions**: None
- **Test Steps**:
  1. Run all tools and verify no real credentials, API keys, or PII appear in mock outputs
- **Expected Result**:
  - Mock data uses fictional values
  - No real email addresses, phone numbers, or credit card numbers in seed data

---

## 10. Performance Tests

### TC-PERF-001: Workflow Compilation Time for Large Graphs

- **Priority**: Medium
- **Preconditions**: A workflow with 50 nodes
- **Test Steps**:
  1. Measure time to compile the workflow
  2. Measure time to compile 10 times
- **Expected Result**:
  - Single compilation: < 500ms
  - 10 compilations: < 5s total
  - Memory usage is stable (no leaks)

---

### TC-PERF-002: Concurrent Execution Limits

- **Priority**: Medium
- **Preconditions**: A simple workflow persisted
- **Test Steps**:
  1. Run 20 workflow executions concurrently using `asyncio.gather`
  2. Measure completion time and resource usage
- **Expected Result**:
  - All 20 executions complete successfully
  - No deadlocks or database contention errors
  - Total time is reasonable (parallel execution should be faster than sequential)
  - Memory usage does not grow linearly with concurrent executions

---

### TC-PERF-003: Database Query Optimization for List Runs

- **Priority**: Low
- **Preconditions**: 1,000 execution records in the database
- **Test Steps**:
  1. Send `GET /api/runs?limit=50`
  2. Measure response time
- **Expected Result**:
  - Response time < 500ms
  - Query uses the index on `started_at` for ordering
  - Only 50 records are fetched (LIMIT clause works)

---

### TC-PERF-004: Memory Usage With Many Concurrent Workflows

- **Priority**: Medium
- **Preconditions**: A simple workflow persisted
- **Test Steps**:
  1. Run 50 workflow executions concurrently
  2. Monitor memory usage before, during, and after
  3. Verify memory is released after executions complete
- **Expected Result**:
  - Memory usage peaks during execution but returns to baseline after
  - No memory leaks from accumulated step records or context data
  - `MemorySaver` checkpointer does not accumulate unbounded state

---

### TC-PERF-005: LangGraph Compilation Caching

- **Priority**: Low
- **Preconditions**: A workflow persisted
- **Test Steps**:
  1. Compile the same workflow 5 times
  2. Measure if there is any caching benefit
- **Expected Result**:
  - Compilation is fast (< 100ms per call)
  - No significant performance degradation on repeated compilations
  - Consider implementing a compilation cache for frequently-run workflows

---

### TC-PERF-006: API Response Time Under Load

- **Priority**: Medium
- **Preconditions**: API server running; 100 workflows in DB
- **Test Steps**:
  1. Send 100 sequential `GET /api/workflows` requests
  2. Send 100 sequential `GET /api/tools` requests
  3. Measure p95 response time
- **Expected Result**:
  - `GET /api/health`: < 50ms per request
  - `GET /api/tools`: < 100ms per request (tool list is small)
  - `GET /api/workflows` with 100 items: < 300ms per request
  - No timeout errors

---

### TC-PERF-007: Large Context Propagation Performance

- **Priority**: Low
- **Preconditions**: A workflow with many action nodes
- **Test Steps**:
  1. Run the workflow with a context containing 100 key-value pairs
  2. Measure execution time
- **Expected Result**:
  - Execution time is proportional to node count, not context size
  - Context serialization/deserialization does not become a bottleneck
  - Template substitution (if used) handles large context efficiently

---

### TC-PERF-008: Approval Service List Performance

- **Priority**: Low
- **Preconditions**: 500 approval records in the database (mix of pending and resolved)
- **Test Steps**:
  1. Call `service.list_pending()`
  2. Measure query time
- **Expected Result**:
  - Query returns only pending approvals quickly
  - Filter by `status == "pending"` is efficient
  - Response time < 200ms

---

## Appendix: Test Data Reference

### Built-in Mock Data

The following mock data is pre-seeded in the tool implementations:

**MOCK_DB_RECORDS**:
- `purchase_orders`: 2 records (Acme Corp $45k, Globex Inc $120k)
- `invoices`: 2 records (Acme Corp INV-2024-001 $45k, Globex Inc INV-2024-002 $120k)
- `employees`: 2 records (Alice - docs verified, Bob - docs not verified)

**Tool Defaults**:
- `send_email`: requires `to`, optional `subject`/`body`
- `search_database`: requires `table`, optional `query`
- `update_database`: requires `table`, `id`, optional `updates`
- `process_payment`: requires `invoice_id`, `amount`
- `create_ticket`: requires `title`, optional `priority`/`assignee`
- `extract_invoice_data`: requires `document`, returns fixed mock data
- `wait`: requires `seconds`, capped at 5s

### Example Workflow Definitions

Three example workflows are provided in `examples/__init__.py`:
1. `INVOICE_PROCESSING` — 7 nodes, includes approval gate
2. `EMPLOYEE_ONBOARDING` — 7 nodes, includes condition branching
3. `CUSTOMER_SUPPORT` — 9 nodes, includes escalation logic

### Key Implementation Notes for Test Authors

1. **eval() usage in conditions**: The compiler uses `eval(expression, {"__builtins__": {}}, context)` for condition evaluation. This is a security consideration (see TC-SEC-006).

2. **No retry loop implemented**: The `retry_count` and `retry_delay` fields on action nodes are stored but not currently used by the runner. The verifier provides `RETRY` verdicts but the runner does not act on them.

3. **Approval timeout is configurable but not enforced**: `approval_timeout_hours` is set to 48 in config, but no background job enforces it.

4. **No authentication/authorization**: The API has no auth middleware. All endpoints are publicly accessible.

5. **SQLite in production config**: The default `DATABASE_URL` uses SQLite. For production, a PostgreSQL URL should be configured.

6. **MemorySaver checkpointer**: LangGraph uses in-memory checkpoints. State is lost on server restart.

7. **Context template substitution**: The compiler replaces `{{key}}` patterns in tool inputs with values from the execution context.

8. **Condition default branch**: When `eval()` fails, the condition defaults to the `"true"` branch.
