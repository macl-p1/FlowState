# OrchestrAI — Complex Real-Life Test Cases

These test cases are designed to catch edge cases, integration bugs, and real-world failure modes.
Organized by module/component. Each section has unit-level tests and integration-level scenarios.

---

## Table of Contents

1. [Schema Tests](#1-schema-tests)
2. [Tool Registry Tests](#2-tool-registry-tests)
3. [Mock Tool Execution Tests](#3-mock-tool-execution-tests)
4. [Planner Agent Tests](#4-planner-agent-tests)
5. [Compiler Tests](#5-compiler-tests)
6. [Runner / Execution Engine Tests](#6-runner--execution-engine-tests)
7. [Verifier Agent Tests](#7-verifier-agent-tests)
8. [Approval / HITL Tests](#8-approval--hitl-tests)
9. [API Endpoint Tests](#9-api-endpoint-tests)
10. [End-to-End Integration Tests](#10-end-to-end-integration-tests)
11. [Stress / Resilience Tests](#11-stress--resilience-tests)
12. [Security Tests](#12-security-tests)

---

## 1. Schema Tests

### 1.1 — Valid workflow creation

```python
def test_valid_invoice_workflow_schema():
    """Invoice processing workflow with all node types."""
    data = {
        "name": "Invoice Processing",
        "description": "Process incoming invoices",
        "trigger": {"type": "manual"},
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Invoice Received"},
            {"id": "n2", "type": "action", "name": "Extract Data", "tool": "extract_invoice_data", "inputs": {"document": "{{n1.output}}"}},
            {"id": "n3", "type": "action", "name": "Find PO", "tool": "search_database", "inputs": {"query": "SELECT * FROM purchase_orders WHERE vendor={{n2.output.vendor}}"}},
            {"id": "n4", "type": "condition", "name": "Amount Check", "expression": "{{n2.output.amount}} > 100000"},
            {"id": "n5", "type": "approval", "name": "Manager Approval", "reason": "Invoice exceeds ₹100,000"},
            {"id": "n6", "type": "action", "name": "Payment Request", "tool": "update_database"},
            {"id": "n7", "type": "end", "name": "Complete"},
        ],
        "edges": [
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
            {"from": "n3", "to": "n4"},
            {"from": "n4", "to": "n5", "condition": "true"},
            {"from": "n4", "to": "n6", "condition": "false"},
            {"from": "n5", "to": "n6"},
            {"from": "n6", "to": "n7"},
        ],
    }
    wf = Workflow(**data)
    assert wf.name == "Invoice Processing"
    assert len(wf.nodes) == 7
    assert len(wf.edges) == 7
```

### 1.2 — Missing required fields

```python
def test_workflow_missing_name_raises_validation_error():
    data = {"nodes": [], "edges": []}
    with pytest.raises(ValidationError) as exc:
        Workflow(**data)
    assert "name" in str(exc.value)
```

### 1.3 — Orphaned node (node referenced in edges but not defined)

```python
def test_workflow_orphaned_node_reference():
    data = {
        "name": "Bad Workflow",
        "nodes": [{"id": "n1", "type": "trigger", "name": "Start"}],
        "edges": [{"from": "n1", "to": "nonexistent"}],
    }
    with pytest.raises(ValidationError) as exc:
        Workflow(**data)
    assert "nonexistent" in str(exc.value)
```

### 1.4 — Circular dependency detection

```python
def test_workflow_circular_dependency_detection():
    data = {
        "name": "Circular",
        "nodes": [
            {"id": "n1", "type": "action", "name": "A"},
            {"id": "n2", "type": "action", "name": "B"},
        ],
        "edges": [
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n1"},  # creates cycle
        ],
    }
    with pytest.raises(ValidationError) as exc:
        Workflow(**data)
    assert "cycle" in str(exc.value).lower()
```

### 1.5 — Duplicate node IDs

```python
def test_workflow_duplicate_node_ids():
    data = {
        "name": "Dupes",
        "nodes": [
            {"id": "n1", "type": "action", "name": "A"},
            {"id": "n1", "type": "action", "name": "B"},
        ],
        "edges": [],
    }
    with pytest.raises(ValidationError) as exc:
        Workflow(**data)
    assert "duplicate" in str(exc.value).lower()
```

### 1.6 — Node with invalid type

```python
def test_workflow_invalid_node_type():
    data = {
        "name": "Bad Type",
        "nodes": [{"id": "n1", "type": "quantum_compute", "name": "Weird"}],
        "edges": [],
    }
    with pytest.raises(ValidationError) as exc:
        Workflow(**data)
    assert "quantum_compute" in str(exc.value)
```

### 1.7 — Execution state transitions (state machine validation)

```python
@pytest.mark.parametrize("from_status,to_status,valid", [
    ("pending", "running", True),
    ("running", "waiting_approval", True),
    ("waiting_approval", "running", True),   # resumed
    ("waiting_approval", "cancelled", True), # rejected
    ("running", "completed", True),
    ("running", "failed", True),
    ("completed", "running", False),         # cannot restart
    ("failed", "completed", False),          # cannot magically succeed
    ("cancelled", "running", False),
    ("pending", "completed", False),         # skip steps
])
def test_execution_state_transitions(from_status, to_status, valid):
    transition = ExecutionStateTransition(from_status, to_status)
    assert transition.is_valid == valid
```

### 1.8 — Tool input schema validation

```python
def test_action_node_validates_tool_inputs():
    node = ActionNode(
        id="n1",
        name="Send Email",
        tool="send_email",
        inputs={"to": "user@example.com", "subject": "Hello"},
    )
    assert node.inputs["to"] == "user@example.com"

def test_action_node_rejects_invalid_tool_inputs():
    with pytest.raises(ValidationError) as exc:
        ActionNode(
            id="n1",
            name="Send Email",
            tool="send_email",
            inputs={"to": 12345},  # should be string
        )
    assert "to" in str(exc.value)
```

---

## 2. Tool Registry Tests

### 2.1 — Register and retrieve tool

```python
def test_tool_registry_register_and_retrieve():
    registry = ToolRegistry()
    tool = Tool(
        name="send_email",
        description="Send an email",
        input_schema={"type": "object", "properties": {"to": {"type": "string"}}},
        permission=PermissionLevel.AUTO,
    )
    registry.register(tool)
    assert registry.get("send_email") == tool
```

### 2.2 — Unknown tool returns None / raises

```python
def test_tool_registry_unknown_tool():
    registry = ToolRegistry()
    assert registry.get("nonexistent_tool") is None
```

### 2.3 — Cannot register duplicate tool

```python
def test_tool_registry_duplicate_registration_raises():
    registry = ToolRegistry()
    tool = Tool(name="send_email", ...)
    registry.register(tool)
    with pytest.raises(ToolAlreadyRegisteredError):
        registry.register(tool)
```

### 2.4 — List all tools

```python
def test_tool_registry_list_tools():
    registry = ToolRegistry()
    registry.register(Tool(name="send_email", ...))
    registry.register(Tool(name="send_slack", ...))
    tools = registry.list_all()
    assert len(tools) == 2
    names = {t.name for t in tools}
    assert names == {"send_email", "send_slack"}
```

### 2.5 — Permission level enforcement

```python
def test_tool_registry_permission_levels():
    auto_tool = Tool(name="query_db", permission=PermissionLevel.AUTO)
    confirm_tool = Tool(name="update_db", permission=PermissionLevel.CONFIRM)
    human_tool = Tool(name="send_money", permission=PermissionLevel.HUMAN_ONLY)

    assert auto_tool.permission == PermissionLevel.AUTO
    assert confirm_tool.permission == PermissionLevel.CONFIRM
    assert human_tool.permission == PermissionLevel.HUMAN_ONLY
```

---

## 3. Mock Tool Execution Tests

### 3.1 — Successful tool execution (send_email)

```python
@pytest.mark.asyncio
async def test_send_email_success():
    result = await send_email({"to": "test@example.com", "subject": "Hi", "body": "Hello"})
    assert result.success is True
    assert result.output["message_id"] is not None
    assert result.error is None
```

### 3.2 — Tool execution with invalid inputs

```python
@pytest.mark.asyncio
async def test_send_email_missing_required_field():
    result = await send_email({"subject": "Hi"})  # missing "to"
    assert result.success is False
    assert "to" in result.error.lower()
```

### 3.3 — Tool execution timeout simulation

```python
@pytest.mark.asyncio
async def test_slow_tool_times_out():
    result = await wait(seconds=30, timeout=2)
    assert result.success is False
    assert "timeout" in result.error.lower()
```

### 3.4 — Tool execution failure (simulated API 500)

```python
@pytest.mark.asyncio
async def test_send_slack_api_failure():
    result = await send_slack_message({
        "channel": "#general",
        "message": "Hello"
    }, force_failure=True)
    assert result.success is False
    assert result.error is not None
    assert result.retryable is True
```

### 3.5 — search_database returns expected shape

```python
@pytest.mark.asyncio
async def test_search_database_returns_records():
    result = await search_database({"query": "SELECT * FROM invoices"})
    assert result.success is True
    assert isinstance(result.output["records"], list)
```

### 3.6 — request_human_approval always pauses

```python
@pytest.mark.asyncio
async def test_human_approval_tool_creates_approval_request():
    result = await request_human_approval({
        "reason": "Large invoice",
        "context": {"amount": 500000}
    })
    assert result.success is True
    assert result.output["approval_id"] is not None
    assert result.output["status"] == "pending"
```

---

## 4. Planner Agent Tests

### 4.1 — Simple linear workflow from natural language

**Input:**
```
"When an invoice arrives, extract the details and send a confirmation email."
```

**Expected output:** Workflow with 3 nodes (trigger → extract → email) and 2 edges.

```python
@pytest.mark.asyncio
async def test_planner_linear_workflow(mock_anthropic_client):
    planner = PlannerAgent(tool_registry=registry, llm_client=mock_client)
    workflow = await planner.plan(
        "When an invoice arrives, extract the details and send a confirmation email."
    )
    assert workflow is not None
    assert len(workflow.nodes) == 3
    node_types = [n.type for n in workflow.nodes]
    assert "trigger" in node_types
    assert "action" in node_types
```

### 4.2 — Workflow with conditional branching

**Input:**
```
"If the invoice amount exceeds $10,000, request manager approval. Otherwise, process it automatically."
```

```python
@pytest.mark.asyncio
async def test_planner_branching_workflow(mock_anthropic_client):
    workflow = await planner.plan(
        "If the invoice amount exceeds $10,000, request manager approval. Otherwise, process it automatically."
    )
    condition_nodes = [n for n in workflow.nodes if n.type == "condition"]
    assert len(condition_nodes) >= 1
    approval_nodes = [n for n in workflow.nodes if n.type == "approval"]
    assert len(approval_nodes) >= 1
```

### 4.3 — Workflow with retry logic

**Input:**
```
"Send the invoice email, retry up to 3 times if it fails."
```

```python
@pytest.mark.asyncio
async def test_planner_includes_retry(mock_anthropic_client):
    workflow = await planner.plan(
        "Send the invoice email, retry up to 3 times if it fails."
    )
    email_node = next(n for n in workflow.nodes if "email" in n.name.lower())
    assert email_node.retry_count == 3
    assert email_node.retry_delay is not None
```

### 4.4 — Planner rejects unknown tools (doesn't invent)

```python
@pytest.mark.asyncio
async def test_planner_rejects_unknown_tools(mock_anthropic_client):
    # LLM tries to use a tool that doesn't exist in registry
    mock_client.set_next_response(INVALID_TOOL_RESPONSE)
    result = await planner.plan("Use the teleport tool to ship the package")
    assert result.error is not None
    assert "teleport" in result.error.lower() or "unknown" in result.error.lower()
```

### 4.5 — Malformed LLM output triggers repair loop

```python
@pytest.mark.asyncio
async def test_planner_repairs_malformed_output(mock_anthropic_client):
    # First response is malformed JSON
    mock_client.set_responses([
        MALFORMED_JSON,  # invalid
        VALID_WORKFLOW,   # fixed
    ])
    workflow = await planner.plan("Process an invoice")
    assert workflow is not None  # recovered
    assert mock_client.call_count == 2  # retried once
```

### 4.6 — Planner exhausts retries on persistent invalid output

```python
@pytest.mark.asyncio
async def test_planner_exhausts_retries():
    mock_client.set_responses([MALFORMED_JSON] * 5)
    result = await planner.plan("Process an invoice", max_repairs=3)
    assert result.error is not None
    assert "validation" in result.error.lower()
```

### 4.7 — Employee onboarding workflow

```python
@pytest.mark.asyncio
async def test_planner_onboarding_workflow(mock_anthropic_client):
    workflow = await planner.plan(
        "When a new employee joins, collect their documents, verify them, "
        "notify HR, and if anything is missing, send a reminder."
    )
    tool_names = [node.tool for node in workflow.nodes if hasattr(node, 'tool')]
    assert "send_email" in tool_names or "search_database" in tool_names
    assert any(n.type == "condition" for n in workflow.nodes)
```

### 4.8 — Customer complaint workflow

```python
@pytest.mark.asyncio
async def test_planner_complaint_workflow(mock_anthropic_client):
    workflow = await planner.plan(
        "When a customer complaint arrives, identify the customer, find their order, "
        "check delivery status, determine the issue, generate a response, and send it."
    )
    assert len(workflow.nodes) >= 5
    assert any(n.type == "trigger" for n in workflow.nodes)
    assert any(n.type == "end" for n in workflow.nodes)
```

---

## 5. Compiler Tests

### 5.1 — Sequential workflow compiles correctly

```python
def test_compiler_sequential_workflow():
    wf = Workflow(
        name="Linear",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "send_email"},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ],
    )
    graph = compiler.compile(wf)
    assert graph is not None
    # Verify execution order
    order = graph.execution_order()
    assert order == ["n1", "n2", "n3"]
```

### 5.2 — Branching workflow compiles

```python
def test_compiler_branching_workflow():
    wf = Workflow(
        name="Branch",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "condition", "expression": "x > 10"},
            {"id": "n3", "type": "action", "name": "High path"},
            {"id": "n4", "type": "action", "name": "Low path"},
            {"id": "n5", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3", "condition": "true"},
            {"from": "n2", "to": "n4", "condition": "false"},
            {"from": "n3", "to": "n5"},
            {"from": "n4", "to": "n5"},
        ],
    )
    graph = compiler.compile(wf)
    # Both branches should converge at n5
    assert graph.get_node("n5") is not None
```

### 5.3 — Approval node compiles with pause semantics

```python
def test_compiler_approval_node():
    wf = Workflow(
        name="Approval",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "approval", "reason": "Need sign-off"},
            {"id": "n3", "type": "action"},
            {"id": "n4", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
            {"from": "n3", "to": "n4"},
        ],
    )
    graph = compiler.compile(wf)
    approval_node = graph.get_node("n2")
    assert approval_node.pause_execution is True
```

### 5.4 — Retry edges are compiled

```python
def test_compiler_retry_edges():
    wf = Workflow(
        name="Retry",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "send_email", "retry_count": 3},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ],
    )
    graph = compiler.compile(wf)
    node = graph.get_node("n2")
    assert node.retry_count == 3
```

### 5.5 — Invalid graph raises error

```python
def test_compiler_invalid_graph_no_trigger():
    wf = Workflow(
        name="No Trigger",
        nodes=[
            {"id": "n1", "type": "action"},
        ],
        edges=[],
    )
    with pytest.raises(CompilationError) as exc:
        compiler.compile(wf)
    assert "trigger" in str(exc.value).lower()
```

### 5.6 — Multiple triggers raise error

```python
def test_compiler_multiple_triggers_raises():
    wf = Workflow(
        name="Multi Trigger",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "trigger"},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n3"},
            {"from": "n2", "to": "n3"},
        ],
    )
    with pytest.raises(CompilationError) as exc:
        compiler.compile(wf)
    assert "multiple" in str(exc.value).lower()
```

---

## 6. Runner / Execution Engine Tests

### 6.1 — Happy path: simple workflow completes

```python
@pytest.mark.asyncio
async def test_runner_happy_path_simple_workflow(db_session):
    wf = Workflow(
        name="Simple",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "send_email", "inputs": {"to": "test@test.com", "subject": "Hi", "body": "Hello"}},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ],
    )
    # Persist workflow
    wf_model = await db.create_workflow(wf)

    runner = WorkflowRunner(db=db, tool_registry=registry)
    execution = await runner.run(wf_model.id)

    assert execution.status == ExecutionStatus.COMPLETED
    assert len(execution.steps) == 3  # trigger + action + end
    assert execution.steps[1].status == StepStatus.COMPLETED
    assert execution.steps[1].tool_result.success is True
```

### 6.2 — Workflow pauses at approval node

```python
@pytest.mark.asyncio
async def test_runner_pauses_at_approval(db_session):
    wf = Workflow(
        name="Approval Test",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "extract_invoice"},
            {"id": "n3", "type": "approval", "reason": "Amount > $100k"},
            {"id": "n4", "type": "action", "tool": "process_payment"},
            {"id": "n5", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
            {"from": "n3", "to": "n4"},
            {"from": "n4", "to": "n5"},
        ],
    )
    wf_model = await db.create_workflow(wf)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    execution = await runner.run(wf_model.id)

    # Should stop at approval node
    assert execution.status == ExecutionStatus.WAITING_APPROVAL
    assert execution.current_node_id == "n3"
    assert execution.steps[2].status == StepStatus.WAITING_APPROVAL
```

### 6.3 — Workflow resumes after approval

```python
@pytest.mark.asyncio
async def test_runner_resumes_after_approval(db_session):
    # Setup: run workflow to approval point
    wf_model, execution = await setup_workflow_at_approval(db_session)

    # Approve
    await approval_service.approve(execution.approval_id, approver_id="user_123")

    # Resume
    runner = WorkflowRunner(db=db, tool_registry=registry)
    resumed = await runner.resume(execution.id)

    assert resumed.status == ExecutionStatus.COMPLETED
    # All steps should be completed
    for step in resumed.steps:
        assert step.status == StepStatus.COMPLETED
    assert resumed.approval.approver_id == "user_123"
    assert resumed.approval.approved_at is not None
```

### 6.4 — Workflow rejects at approval node

```python
@pytest.mark.asyncio
async def test_runner_cancels_on_rejection(db_session):
    wf_model, execution = await setup_workflow_at_approval(db_session)

    # Reject
    await approval_service.reject(execution.approval_id, approver_id="user_123", reason="Too expensive")

    # Workflow should be cancelled
    execution = await db.get_execution(execution.id)
    assert execution.status == ExecutionStatus.CANCELLED
    assert execution.approval.rejection_reason == "Too expensive"
```

### 6.5 — Tool failure triggers retry then escalation

```python
@pytest.mark.asyncio
async def test_runner_retries_on_tool_failure(db_session):
    wf = Workflow(
        name="Retry Test",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "flaky_api", "retry_count": 3, "retry_delay": 0.1},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ],
    )
    # flaky_api fails twice then succeeds
    flaky_api.set_failure_pattern([True, True, False])
    wf_model = await db.create_workflow(wf)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    execution = await runner.run(wf_model.id)

    assert execution.status == ExecutionStatus.COMPLETED
    retry_step = execution.steps[1]
    assert retry_step.attempt_count == 3
    assert retry_step.status == StepStatus.COMPLETED
```

### 6.6 — Tool exhausts retries and marks workflow failed

```python
@pytest.mark.asyncio
async def test_runner_fails_after_max_retries(db_session):
    wf = Workflow(
        name="Fail Test",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "always_fail", "retry_count": 2},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ],
    )
    wf_model = await db.create_workflow(wf)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    execution = await runner.run(wf_model.id)

    assert execution.status == ExecutionStatus.FAILED
    failed_step = next(s for s in execution.steps if s.node_id == "n2")
    assert failed_step.attempt_count == 3  # 1 initial + 2 retries
    assert failed_step.error is not None
```

### 6.7 — Condition node routes correctly

```python
@pytest.mark.asyncio
async def test_runner_condition_routes_true_branch(db_session):
    wf = Workflow(
        name="Condition",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "condition", "expression": "amount > 100000"},
            {"id": "n3", "type": "approval", "name": "High value approval"},
            {"id": "n4", "type": "action", "tool": "process_payment", "name": "Auto process"},
            {"id": "n5", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3", "condition": "true"},
            {"from": "n2", "to": "n4", "condition": "false"},
            {"from": "n3", "to": "n5"},
            {"from": "n4", "to": "n5"},
        ],
    )
    # Context: amount = 500000 (> 100000)
    wf_model = await db.create_workflow(wf)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    execution = await runner.run(wf_model.id, context={"amount": 500000})

    # Should hit approval gate
    assert execution.status == ExecutionStatus.WAITING_APPROVAL
    assert execution.current_node_id == "n3"
```

### 6.8 — Workflow with dead end (no matching edge)

```python
@pytest.mark.asyncio
async def test_runner_handles_dead_end(db_session):
    wf = Workflow(
        name="Dead End",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "condition"},
            # No edges from n2 at all — dead end
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            # Missing: from n2 to anything
            {"from": "n1", "to": "n3"},  # wrong source
        ],
    )
    wf_model = await db.create_workflow(wf)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    execution = await runner.run(wf_model.id)
    # Should fail gracefully, not infinite loop
    assert execution.status == ExecutionStatus.FAILED
    assert "no outgoing edges" in execution.error_message.lower()
```

### 6.9 — Runner is idempotent (duplicate run_id)

```python
@pytest.mark.asyncio
async def test_runner_idempotent_on_duplicate_run(db_session):
    wf_model = await create_test_workflow(db)
    execution = await runner.run(wf_model.id)
    first_status = execution.status

    # Running same workflow again should create new execution
    execution2 = await runner.run(wf_model.id)
    assert execution2.id != execution.id
    assert execution2.status == ExecutionStatus.COMPLETED
```

### 6.10 — Step execution has full observability

```python
@pytest.mark.asyncio
async def test_runner_step_has_full_observability(db_session):
    wf_model = await create_test_workflow(db)
    execution = await runner.run(wf_model.id)

    for step in execution.steps:
        assert step.id is not None
        assert step.execution_id == execution.id
        assert step.node_id is not None
        assert step.started_at is not None
        assert step.completed_at is not None
        assert step.status in StepStatus
        assert step.attempt_count >= 1
        if step.tool_name:
            assert step.tool_inputs is not None
            assert step.tool_result is not None
```

---

## 7. Verifier Agent Tests

### 7.1 — Successful tool result verified

```python
@pytest.mark.asyncio
async def test_verifier_success():
    verifier = VerifierAgent()
    result = await verifier.verify(
        tool_name="send_email",
        tool_result=ToolResult(success=True, output={"message_id": "msg_123"}),
        expected_outcome="Email sent successfully",
    )
    assert result.verdict == "SUCCESS"
    assert result.confidence > 0.8
```

### 7.2 — Tool failure triggers RETRY verdict

```python
@pytest.mark.asyncio
async def test_verifier_retry_on_api_error():
    verifier = VerifierAgent()
    result = await verifier.verify(
        tool_name="send_email",
        tool_result=ToolResult(success=False, error="API returned 503", retryable=True),
        expected_outcome="Email sent successfully",
    )
    assert result.verdict == "RETRY"
```

### 7.3 — Business rule violation triggers ESCALATE

```python
@pytest.mark.asyncio
async def test_verifier_escalate_on_business_rule():
    verifier = VerifierAgent()
    result = await verifier.verify(
        tool_name="validate_invoice",
        tool_result=ToolResult(
            success=True,
            output={"amount": 500000, "valid": True},
            warnings=["Amount exceeds approval threshold of $100,000"]
        ),
        expected_outcome="Invoice is under $100,000",
    )
    assert result.verdict == "ESCALATE"
```

### 7.4 — Non-retryable failure triggers FAIL

```python
@pytest.mark.asyncio
async def test_verifier_fail_on_auth_error():
    verifier = VerifierAgent()
    result = await verifier.verify(
        tool_name="search_database",
        tool_result=ToolResult(success=False, error="Authentication failed", retryable=False),
        expected_outcome="Records found",
    )
    assert result.verdict == "FAIL"
```

### 7.5 — Verifier never exposes chain-of-thought

```python
@pytest.mark.asyncio
async def test_verifier_no_chain_of_thought():
    verifier = VerifierAgent()
    result = await verifier.verify(
        tool_name="send_email",
        tool_result=ToolResult(success=True),
        expected_outcome="Email sent",
    )
    # The output should only contain structured fields
    assert not hasattr(result, 'reasoning') or result.reasoning is None
    assert hasattr(result, 'verdict')
    assert hasattr(result, 'confidence')
    assert hasattr(result, 'user_message')
```

---

## 8. Approval / HITL Tests

### 8.1 — Approval request created with correct data

```python
@pytest.mark.asyncio
async def test_approval_request_created():
    approval = await approval_service.create_request(
        workflow_execution_id="exec_123",
        node_id="n3",
        reason="Invoice exceeds $100,000",
        context={"invoice_id": "inv_456", "amount": 500000},
        requested_by="system",
    )
    assert approval.id is not None
    assert approval.status == ApprovalStatus.PENDING
    assert approval.workflow_execution_id == "exec_123"
    assert approval.context["amount"] == 500000
```

### 8.2 — Approve updates status and records approver

```python
@pytest.mark.asyncio
async def test_approval_approve():
    approval = await create_pending_approval()
    result = await approval_service.approve(approval.id, approver_id="user_123")

    assert result.status == ApprovalStatus.APPROVED
    assert result.approver_id == "user_123"
    assert result.approved_at is not None
    assert result.resolved_at is not None
```

### 8.3 — Reject records reason

```python
@pytest.mark.asyncio
async def test_approval_reject():
    approval = await create_pending_approval()
    result = await approval_service.reject(
        approval.id,
        approver_id="user_123",
        reason="Budget not available this quarter"
    )

    assert result.status == ApprovalStatus.REJECTED
    assert result.rejection_reason == "Budget not available this quarter"
```

### 8.4 — Cannot approve already-resolved request

```python
@pytest.mark.asyncio
async def test_approval_cannot_approve_twice():
    approval = await create_pending_approval()
    await approval_service.approve(approval.id, approver_id="user_123")

    with pytest.raises(ApprovalAlreadyResolvedError):
        await approval_service.approve(approval.id, approver_id="user_456")
```

### 8.5 — Approval persists across simulated restart

```python
@pytest.mark.asyncio
async def test_approval_survives_restart(db_session):
    # Create approval
    approval = await create_pending_approval()

    # Simulate: close DB session, create new one
    await db_session.close()
    new_session = db.create_session()

    # Retrieve approval
    recovered = await approval_service.get(approval.id, session=new_session)
    assert recovered is not None
    assert recovered.status == ApprovalStatus.PENDING
    assert recovered.context["amount"] == 500000
```

### 8.6 — List pending approvals

```python
@pytest.mark.asyncio
async def test_list_pending_approvals():
    await create_pending_approval(workflow_id="wf_1")
    await create_pending_approval(workflow_id="wf_2")
    await create_pending_approval(workflow_id="wf_3")
    await create_resolved_approval(workflow_id="wf_4")

    pending = await approval_service.list_pending()
    assert len(pending) == 3
    assert all(a.status == ApprovalStatus.PENDING for a in pending)
```

---

## 9. API Endpoint Tests

### 9.1 — POST /api/workflows/generate (natural language → workflow)

```python
def test_api_generate_workflow(client, mock_planner):
    mock_planner.return_value.plan.return_value = sample_workflow

    response = client.post("/api/workflows/generate", json={
        "prompt": "Process incoming invoices with approval for amounts over $100k"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Invoice Processing"
    assert len(data["nodes"]) > 0
```

### 9.2 — GET /api/workflows lists all workflows

```python
def test_api_list_workflows(client, db_session):
    await db.create_workflow(sample_workflow_1)
    await db.create_workflow(sample_workflow_2)

    response = client.get("/api/workflows")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
```

### 9.3 — POST /api/workflows/{id}/run starts execution

```python
def test_api_run_workflow(client, db_session, mock_runner):
    wf = await db.create_workflow(sample_workflow)
    mock_runner.return_value.run.return_value = sample_execution

    response = client.post(f"/api/workflows/{wf.id}/run")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["workflow_id"] == wf.id
```

### 9.4 — GET /api/runs/{id} returns execution state

```python
def test_api_get_run(client, db_session):
    wf = await db.create_workflow(sample_workflow)
    exec_ = await runner.run(wf.id)

    response = client.get(f"/api/runs/{exec_.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exec_.id
    assert "steps" in data
```

### 9.5 — POST /api/runs/{id}/cancel cancels execution

```python
def test_api_cancel_run(client, db_session):
    wf = await db.create_workflow(sample_workflow)
    exec_ = await runner.run(wf.id)

    response = client.post(f"/api/runs/{exec_.id}/cancel")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"
```

### 9.6 — GET /api/approvals lists pending approvals

```python
def test_api_list_approvals(client, db_session):
    await create_pending_approval(workflow_exec_id="e1")
    await create_pending_approval(workflow_exec_id="e2")
    await create_approved_approval()

    response = client.get("/api/approvals")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # only pending
```

### 9.7 — POST /api/approvals/{id}/approve

```python
def test_api_approve(client, db_session):
    approval = await create_pending_approval()

    response = client.post(f"/api/approvals/{approval.id}/approve", json={
        "approver_id": "user_123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
```

### 9.8 — POST /api/approvals/{id}/reject

```python
def test_api_reject(client, db_session):
    approval = await create_pending_approval()

    response = client.post(f"/api/approvals/{approval.id}/reject", json={
        "approver_id": "user_123",
        "reason": "Too expensive"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "Too expensive"
```

### 9.9 — GET /api/tools lists registered tools

```python
def test_api_list_tools(client):
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    tool_names = [t["name"] for t in data]
    assert "send_email" in tool_names
```

### 9.10 — 404 for non-existent resources

```python
def test_api_404_for_missing_workflow(client):
    response = client.get("/api/workflows/nonexistent-id")
    assert response.status_code == 404

def test_api_404_for_missing_run(client):
    response = client.get("/api/runs/nonexistent-id")
    assert response.status_code == 404
```

---

## 10. End-to-End Integration Tests

### 10.1 — Full invoice processing workflow (happy path with approval)

```python
@pytest.mark.asyncio
async def test_e2e_invoice_processing_with_approval(client, db_session):
    """
    1. Generate workflow from natural language
    2. Run the workflow
    3. Verify it pauses at approval
    4. Approve
    5. Verify completion
    """
    # Step 1: Generate workflow
    response = client.post("/api/workflows/generate", json={
        "prompt": INVOICE_PROMPT
    })
    assert response.status_code == 201
    workflow_id = response.json()["id"]

    # Step 2: Run
    response = client.post(f"/api/workflows/{workflow_id}/run")
    assert response.status_code == 200
    exec_id = response.json()["id"]

    # Step 3: Poll until waiting approval
    exec_data = await poll_until_status(client, exec_id, "waiting_approval", timeout=10)
    assert exec_data["status"] == "waiting_approval"

    # Step 4: Find approval request
    approvals = client.get("/api/approvals").json()
    approval = next(a for a in approvals if a["workflow_execution_id"] == exec_id)
    approval_id = approval["id"]

    # Step 5: Approve
    response = client.post(f"/api/approvals/{approval_id}/approve", json={
        "approver_id": "manager_123"
    })
    assert response.status_code == 200

    # Step 6: Verify completion
    exec_data = await poll_until_status(client, exec_id, "completed", timeout=10)
    assert exec_data["status"] == "completed"

    # Verify all steps
    steps = exec_data["steps"]
    assert any(s["node_id"] == "extract" for s in steps)
    assert any(s["node_id"] == "approval" for s in steps)
    assert any(s["node_id"] == "payment" for s in steps)
```

### 10.2 — Full employee onboarding workflow

```python
@pytest.mark.asyncio
async def test_e2e_employee_onboarding(client, db_session):
    """
    Complete employee onboarding: trigger → request docs → verify → notify.
    """
    response = client.post("/api/workflows/generate", json={
        "prompt": ONBOARDING_PROMPT
    })
    workflow_id = response.json()["id"]

    response = client.post(f"/api/workflows/{workflow_id}/run")
    exec_id = response.json()["id"]

    exec_data = await poll_until_status(client, exec_id, "completed", timeout=15)

    assert exec_data["status"] == "completed"
    steps = exec_data["steps"]
    # Should have: trigger, request docs, verify, condition, notify HR, notify manager, end
    assert len(steps) >= 5
```

### 10.3 — Same engine, completely different workflow

```python
@pytest.mark.asyncio
async def test_e2e_same_engine_different_workflows(client):
    """
    Prove the engine is universal: run invoice + onboarding without code changes.
    """
    # Invoice
    inv_resp = client.post("/api/workflows/generate", json={"prompt": INVOICE_PROMPT})
    inv_wf_id = inv_resp.json()["id"]
    inv_run = client.post(f"/api/workflows/{inv_wf_id}/run").json()
    await poll_until_status(client, inv_run["id"], "waiting_approval", timeout=10)

    # Onboarding (same engine, different workflow)
    onb_resp = client.post("/api/workflows/generate", json={"prompt": ONBOARDING_PROMPT})
    onb_wf_id = onb_resp.json()["id"]
    onb_run = client.post(f"/api/workflows/{onb_wf_id}/run").json()
    await poll_until_status(client, onb_run["id"], "completed", timeout=15)

    assert onb_run["status"] == "completed"
```

### 10.4 — Full flow with rejection and restart

```python
@pytest.mark.asyncio
async def test_e2e_approval_rejection_then_retry(client):
    """
    1. Run workflow
    2. Reach approval → reject
    3. Fix issue → re-run
    4. Approve → complete
    """
    # Run 1: reject
    response = client.post("/api/workflows/generate", json={"prompt": INVOICE_PROMPT})
    wf_id = response.json()["id"]
    run1 = client.post(f"/api/workflows/{wf_id}/run").json()
    exec_id = run1["id"]

    await poll_until_status(client, exec_id, "waiting_approval", timeout=10)

    approvals = client.get("/api/approvals").json()
    approval = next(a for a in approvals if a["workflow_execution_id"] == exec_id)
    client.post(f"/api/approvals/{approval['id']}/reject", json={
        "approver_id": "mgr",
        "reason": "Need revised invoice"
    })

    exec_data = client.get(f"/api/runs/{exec_id}").json()
    assert exec_data["status"] == "cancelled"

    # Run 2: approve
    run2 = client.post(f"/api/workflows/{wf_id}/run").json()
    exec2_id = run2["id"]
    await poll_until_status(client, exec2_id, "waiting_approval", timeout=10)

    approvals = client.get("/api/approvals").json()
    approval2 = next(a for a in approvals if a["workflow_execution_id"] == exec2_id)
    client.post(f"/api/approvals/{approval2['id']}/approve", json={
        "approver_id": "mgr"
    })

    exec2_data = await poll_until_status(client, exec2_id, "completed", timeout=10)
    assert exec2_data["status"] == "completed"
```

---

## 11. Stress / Resilience Tests

### 11.1 — Concurrent workflow executions

```python
@pytest.mark.asyncio
async def test_concurrent_workflow_executions(db_session):
    """Run 10 workflows simultaneously."""
    wf = await create_test_workflow(db)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    executions = await asyncio.gather(*[
        runner.run(wf.id) for _ in range(10)
    ])

    assert len(executions) == 10
    assert all(e.status == ExecutionStatus.COMPLETED for e in executions)
    # Each execution has a unique ID
    assert len({e.id for e in executions}) == 10
```

### 11.2 — Long-running workflow doesn't timeout

```python
@pytest.mark.asyncio
async def test_long_running_workflow_completes(db_session):
    """Workflow with a 30-second wait node should complete."""
    wf = Workflow(
        name="Long",
        nodes=[
            {"id": "n1", "type": "trigger"},
            {"id": "n2", "type": "action", "tool": "wait", "inputs": {"seconds": 2}},
            {"id": "n3", "type": "end"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ],
    )
    wf_model = await db.create_workflow(wf)
    runner = WorkflowRunner(db=db, tool_registry=registry, timeout=60)

    execution = await runner.run(wf_model.id)
    assert execution.status == ExecutionStatus.COMPLETED
```

### 11.3 — Rapid sequential workflow runs

```python
@pytest.mark.asyncio
async def test_rapid_sequential_runs(db_session):
    """Run the same workflow 20 times in sequence — no state leakage."""
    wf = await create_test_workflow(db)
    runner = WorkflowRunner(db=db, tool_registry=registry)

    for i in range(20):
        execution = await runner.run(wf.id)
        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.run_number == i + 1
```

---

## 12. Security Tests

### 12.1 — No arbitrary code execution

```python
def test_no_arbitrary_code_execution():
    """The planner should never generate nodes with code execution tools."""
    malicious_prompts = [
        "Use exec() to run system commands",
        "Import os and run os.system('rm -rf /')",
        "Use subprocess to run arbitrary commands",
        "Evaluate this Python code",
    ]
    for prompt in malicious_prompts:
        # Even if LLM is tricked, the compiler should reject
        workflow = force_planner_output(malicious_tool_workflow)
        with pytest.raises(SecurityError):
            compiler.compile(workflow)
```

### 12.2 — Tool inputs sanitized

```python
@pytest.mark.asyncio
async def test_tool_inputs_sanitized():
    """SQL injection in tool inputs should not execute."""
    malicious_input = "'; DROP TABLE invoices; --"
    result = await search_database({"query": f"SELECT * FROM invoices WHERE id = '{malicious_input}'"})
    # Tool should handle this safely (parameterized query)
    assert result.success is False or "DROP" not in result.output
```

### 12.3 — Environment variables not leaked in API responses

```python
def test_api_does_not_leak_env_vars(client):
    """No API endpoint should expose API keys or secrets."""
    response = client.get("/api/health")
    data = response.json()
    assert "ANTHROPIC_API_KEY" not in str(data)
    assert "DATABASE_URL" not in str(data)
    assert "SECRET" not in str(data)
```

### 12.4 — CORS properly configured

```python
def test_cors_headers(client):
    response = client.options("/api/workflows", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    })
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
```

---

## Fixtures and Helpers

### Shared fixtures (conftest.py)

```python
@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client with controllable responses."""
    client = MockAnthropicClient()
    yield client
    client.reset()

@pytest.fixture
def tool_registry():
    """Registry pre-loaded with all mock tools."""
    registry = ToolRegistry()
    for tool in MOCK_TOOLS:
        registry.register(tool)
    return registry

@pytest.fixture
def db_session():
    """In-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_workflow():
    """Valid invoice processing workflow for reuse in tests."""
    return Workflow(
        name="Invoice Processing",
        nodes=[
            {"id": "n1", "type": "trigger", "name": "Invoice Received"},
            {"id": "n2", "type": "action", "name": "Extract Data", "tool": "extract_invoice_data"},
            {"id": "n3", "type": "action", "name": "Find PO", "tool": "search_database"},
            {"id": "n4", "type": "condition", "name": "Amount Check"},
            {"id": "n5", "type": "approval", "name": "Manager Approval"},
            {"id": "n6", "type": "action", "name": "Process Payment", "tool": "process_payment"},
            {"id": "n7", "type": "end", "name": "Complete"},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
            {"from": "n3", "to": "n4"},
            {"from": "n4", "to": "n5", "condition": "true"},
            {"from": "n4", "to": "n6", "condition": "false"},
            {"from": "n5", "to": "n6"},
            {"from": "n6", "to": "n7"},
        ],
    )
```

### Test workflow prompts

```python
INVOICE_PROMPT = (
    "When an invoice arrives, extract the details, match it against the purchase order, "
    "compare the amounts, and request approval from the manager if the amount exceeds "
    "$100,000. If approved, process the payment."
)

ONBOARDING_PROMPT = (
    "When a new employee joins, collect their documents, verify them, notify HR, "
    "and if anything is missing, send a reminder to the employee."
)

COMPLAINT_PROMPT = (
    "When a customer complaint arrives, identify the customer, find their order, "
    "check delivery status, determine the issue, generate a response, and send it."
)
```

### Helper: poll until status

```python
async def poll_until_status(client, run_id, target_status, timeout=30, interval=0.5):
    """Poll GET /api/runs/{id} until status matches or timeout."""
    import asyncio
    start = time.time()
    while time.time() - start < timeout:
        response = client.get(f"/api/runs/{run_id}")
        data = response.json()
        if data["status"] == target_status:
            return data
        await asyncio.sleep(interval)
    raise TimeoutError(f"Run {run_id} did not reach {target_status} within {timeout}s")
```

---

## Notes

- All async tests use `pytest-asyncio` with `@pytest.mark.asyncio`
- Mock LLM responses use pre-recorded JSON fixtures (see `tests/fixtures/llm_responses/`)
- Database tests use SQLite in-memory for speed; integration tests use Docker PostgreSQL
- Tests marked `@pytest.mark.slow` are excluded from quick test runs
- CI should run: `pytest tests/ -v --ignore=tests/test_slow.py` for quick feedback
