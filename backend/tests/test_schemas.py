"""Schema validation tests."""

import pytest
from pydantic import ValidationError

from app.schemas.workflow import Workflow, NodeType, PermissionLevel
from app.schemas.execution import (
    ExecutionStatus, StepStatus, WorkflowExecution, StepExecution
)
from app.schemas.tool import ToolResult


# --- Valid workflow creation ---

class TestValidWorkflows:
    def test_valid_invoice_workflow(self):
        data = {
            "name": "Invoice Processing",
            "description": "Process incoming invoices",
            "nodes": [
                {"id": "n1", "type": "trigger", "name": "Invoice Received"},
                {"id": "n2", "type": "action", "name": "Extract Data", "tool": "extract_invoice_data"},
                {"id": "n3", "type": "action", "name": "Find PO", "tool": "search_database"},
                {"id": "n4", "type": "condition", "name": "Amount Check", "expression": "amount > 100000"},
                {"id": "n5", "type": "approval", "name": "Manager Approval", "reason": "Invoice exceeds $100k"},
                {"id": "n6", "type": "action", "name": "Payment Request", "tool": "process_payment"},
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
        wf = Workflow.model_validate(data)
        assert wf.name == "Invoice Processing"
        assert len(wf.nodes) == 7
        assert len(wf.edges) == 7

    def test_valid_onboarding_workflow(self):
        data = {
            "name": "Employee Onboarding",
            "nodes": [
                {"id": "n1", "type": "trigger", "name": "Employee Added"},
                {"id": "n2", "type": "action", "name": "Request Documents", "tool": "send_email"},
                {"id": "n3", "type": "condition", "name": "Documents Complete"},
                {"id": "n4", "type": "action", "name": "Notify HR", "tool": "send_slack_message"},
                {"id": "n5", "type": "action", "name": "Notify Manager", "tool": "send_email"},
                {"id": "n6", "type": "end", "name": "Complete"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
                {"from": "n3", "to": "n4", "condition": "true"},
                {"from": "n3", "to": "n5", "condition": "false"},
                {"from": "n4", "to": "n6"},
                {"from": "n5", "to": "n6"},
            ],
        }
        wf = Workflow.model_validate(data)
        assert len(wf.nodes) == 6

    def test_simple_linear_workflow(self):
        data = {
            "name": "Simple",
            "nodes": [
                {"id": "n1", "type": "trigger", "name": "Start"},
                {"id": "n2", "type": "action", "name": "Do Thing", "tool": "send_email"},
                {"id": "n3", "type": "end", "name": "Done"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
            ],
        }
        wf = Workflow.model_validate(data)
        assert len(wf.nodes) == 3
        assert len(wf.edges) == 2


# --- Invalid workflows ---

class TestInvalidWorkflows:
    def test_missing_name(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({"nodes": [], "edges": []})
        assert "name" in str(exc.value)

    def test_missing_trigger(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "No Trigger",
                "nodes": [{"id": "n1", "type": "action", "name": "Do", "tool": "send_email"}],
                "edges": [],
            })
        assert "trigger" in str(exc.value).lower()

    def test_multiple_triggers(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "Multi Trigger",
                "nodes": [
                    {"id": "n1", "type": "trigger", "name": "Start A"},
                    {"id": "n2", "type": "trigger", "name": "Start B"},
                ],
                "edges": [],
            })
        assert "trigger" in str(exc.value).lower()

    def test_duplicate_node_ids(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "Dupes",
                "nodes": [
                    {"id": "n1", "type": "action", "name": "A", "tool": "send_email"},
                    {"id": "n1", "type": "action", "name": "B", "tool": "send_email"},
                ],
                "edges": [],
            })
        assert "duplicate" in str(exc.value).lower()

    def test_orphaned_edge_source(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "Orphan",
                "nodes": [{"id": "n1", "type": "trigger", "name": "Start"}],
                "edges": [{"from": "nonexistent", "to": "n1"}],
            })
        assert "nonexistent" in str(exc.value)

    def test_orphaned_edge_target(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "Orphan",
                "nodes": [{"id": "n1", "type": "trigger", "name": "Start"}],
                "edges": [{"from": "n1", "to": "nonexistent"}],
            })
        assert "nonexistent" in str(exc.value)

    def test_empty_nodes(self):
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({"name": "Empty", "nodes": [], "edges": []})
        assert "at least one" in str(exc.value).lower()


# --- Execution statuses ---

class TestExecutionStatuses:
    def test_all_statuses_exist(self):
        expected = {"pending", "running", "waiting_approval", "retrying", "completed", "failed", "cancelled"}
        actual = {s.value for s in ExecutionStatus}
        assert expected == actual

    def test_step_statuses_exist(self):
        expected = {"pending", "running", "completed", "failed", "waiting_approval", "skipped"}
        actual = {s.value for s in StepStatus}
        assert expected == actual


# --- ToolResult ---

class TestToolResult:
    def test_success_result(self):
        result = ToolResult(success=True, output={"id": "msg_123"})
        assert result.success is True
        assert result.output["id"] == "msg_123"
        assert result.error is None

    def test_failure_result(self):
        result = ToolResult(success=False, error="API returned 500", retryable=True)
        assert result.success is False
        assert result.error == "API returned 500"
        assert result.retryable is True

    def test_result_with_warnings(self):
        result = ToolResult(
            success=True,
            output={"amount": 500000},
            warnings=["Amount exceeds threshold"],
        )
        assert len(result.warnings) == 1
        assert "threshold" in result.warnings[0]
