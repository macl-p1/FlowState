"""Runner / execution engine tests."""

import pytest
import uuid

from app.engine.runner import WorkflowRunner, WorkflowNotFoundError, RunnerError
from app.approval.service import ApprovalService, ApprovalNotFoundError
from app.schemas.execution import ExecutionStatus, StepStatus
from app.schemas.tool import ToolResult


@pytest.mark.asyncio
async def test_runner_happy_path_simple_workflow(db_session, persisted_invoice_workflow):
    """Complete a simple workflow end-to-end (or pause for approval)."""
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_invoice_workflow.id)

    # The invoice workflow has an approval node, so it may pause for approval
    assert execution.status in (ExecutionStatus.COMPLETED, ExecutionStatus.WAITING_APPROVAL)
    assert len(execution.steps) > 0
    assert len(execution.steps) > 0
    # Steps can be completed or waiting approval (workflow pauses at approval)
    for step in execution.steps:
        assert step.status in (StepStatus.COMPLETED, StepStatus.WAITING_APPROVAL, StepStatus.FAILED), (
            f"Unexpected step status for {step.node_name}: {step.status}"
        )


@pytest.mark.asyncio
async def test_runner_unknown_workflow_raises(db_session):
    runner = WorkflowRunner(db=db_session)
    with pytest.raises(WorkflowNotFoundError):
        await runner.run("nonexistent_wf_id")


@pytest.mark.asyncio
async def test_runner_steps_have_observability(db_session, persisted_invoice_workflow):
    """Every step should have timestamps, inputs, outputs."""
    from app.schemas.execution import StepStatus
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_invoice_workflow.id)

    for step in execution.steps:
        assert step.started_at is not None
        # Steps that are still waiting for approval won't have completed_at yet
        if step.status != StepStatus.WAITING_APPROVAL:
            assert step.completed_at is not None
        assert step.node_id is not None
        assert step.node_type is not None
        assert step.attempt_count >= 1


@pytest.mark.asyncio
async def test_runner_pauses_at_approval(db_session, persisted_invoice_workflow):
    """Workflow with approval node should pause and wait."""
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_invoice_workflow.id)

    # The invoice workflow has an approval node, so it should pause
    assert execution.status == ExecutionStatus.WAITING_APPROVAL
    assert execution.current_node_id is not None

    # Check that an approval request was created
    service = ApprovalService(db_session)
    pending = service.list_pending()
    assert len(pending) > 0
    approval = pending[0]
    assert approval.execution_id == execution.id


@pytest.mark.asyncio
async def test_runner_resumes_after_approval(db_session, persisted_invoice_workflow):
    """After approving, workflow should complete."""
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_invoice_workflow.id)

    assert execution.status == ExecutionStatus.WAITING_APPROVAL

    # Approve
    service = ApprovalService(db_session)
    pending = service.list_pending()
    approval = pending[0]
    service.approve(approval.id, approver_id="test_user")

    # Resume
    resumed = await runner.resume(execution.id)
    assert resumed.status == ExecutionStatus.COMPLETED


@pytest.mark.asyncio
async def test_runner_rejects_and_cancels(db_session, persisted_invoice_workflow):
    """Rejecting an approval and cancelling the workflow."""
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_invoice_workflow.id)

    assert execution.status == ExecutionStatus.WAITING_APPROVAL

    # Reject
    service = ApprovalService(db_session)
    pending = service.list_pending()
    approval = pending[0]
    service.reject(approval.id, approver_id="test_user", reason="Too expensive")

    # Cancel the execution after rejection
    cancelled = await runner.cancel(execution.id)
    assert cancelled.status == ExecutionStatus.CANCELLED


@pytest.mark.asyncio
async def test_runner_cancel_running_workflow(db_session, persisted_invoice_workflow):
    """Cancel a running workflow."""
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_invoice_workflow.id)

    if execution.status in (ExecutionStatus.RUNNING, ExecutionStatus.WAITING_APPROVAL):
        cancelled = await runner.cancel(execution.id)
        assert cancelled.status == ExecutionStatus.CANCELLED


@pytest.mark.asyncio
async def test_runner_onboarding_workflow(db_session, persisted_onboarding_workflow):
    """Employee onboarding workflow runs to completion."""
    runner = WorkflowRunner(db=db_session)
    execution = await runner.run(persisted_onboarding_workflow.id)

    # Onboarding should complete (no approval gate)
    assert execution.status == ExecutionStatus.COMPLETED
    assert len(execution.steps) >= 4


@pytest.mark.asyncio
async def test_runner_multiple_runs_no_state_leakage(db_session, persisted_invoice_workflow):
    """Running the same workflow multiple times should produce independent executions."""
    runner = WorkflowRunner(db=db_session)

    exec1 = await runner.run(persisted_invoice_workflow.id)
    exec2 = await runner.run(persisted_invoice_workflow.id)

    assert exec1.id != exec2.id
    assert exec1.workflow_id == exec2.workflow_id
    # Both should have their own steps
    assert len(exec1.steps) > 0
    assert len(exec2.steps) > 0


@pytest.mark.asyncio
async def test_runner_context_passed_through(db_session, persisted_invoice_workflow):
    """Context variables should be available to condition nodes."""
    runner = WorkflowRunner(db=db_session)

    # Provide context that makes amount > 100000
    context = {"amount": 500000, "vendor": "TestCorp"}
    execution = await runner.run(persisted_invoice_workflow.id, context=context)

    # Should hit approval (amount > 100000)
    assert execution.status == ExecutionStatus.WAITING_APPROVAL
    assert execution.current_node_id is not None


# Fix import issue
from app.models import WorkflowExecutionModel
