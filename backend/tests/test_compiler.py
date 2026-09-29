"""Compiler tests — test WorkflowCompiler produces correct LangGraph structures."""

import pytest
from pydantic import ValidationError

from app.agents.compiler import WorkflowCompiler, CompilationError
from app.schemas.workflow import Workflow
from app.tools.registry import ToolRegistry


@pytest.fixture
def compiler():
    return WorkflowCompiler()


class TestCompilerSequential:
    def test_linear_workflow_compiles(self, compiler):
        wf = Workflow.model_validate({
            "name": "Linear",
            "nodes": [
                {"id": "n1", "type": "trigger"},
                {"id": "n2", "type": "action", "tool": "send_email"},
                {"id": "n3", "type": "end"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
            ],
        })
        result = compiler.compile(wf)
        assert result is not None
        assert "n1" in result.node_order
        assert "n2" in result.node_order
        assert "n3" in result.node_order

    def test_no_trigger_raises(self, compiler):
        """Workflow with no trigger is rejected by schema validation."""
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "No Trigger",
                "nodes": [{"id": "n1", "type": "action", "tool": "send_email"}],
                "edges": [],
            })
        assert "trigger" in str(exc.value).lower()

    def test_multiple_triggers_raises(self, compiler):
        """Workflow with multiple triggers is rejected by schema validation."""
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "Multi Trigger",
                "nodes": [
                    {"id": "n1", "type": "trigger"},
                    {"id": "n2", "type": "trigger"},
                    {"id": "n3", "type": "end"},
                ],
                "edges": [
                    {"from": "n1", "to": "n3"},
                    {"from": "n2", "to": "n3"},
                ],
            })
        assert "trigger" in str(exc.value).lower()

    def test_no_nodes_raises(self, compiler):
        """Workflow with no nodes is rejected by schema validation."""
        with pytest.raises(ValidationError) as exc:
            Workflow.model_validate({
                "name": "Empty",
                "nodes": [],
                "edges": [],
            })
        assert "node" in str(exc.value).lower()


class TestCompilerBranching:
    def test_condition_node_compiles(self, compiler):
        wf = Workflow.model_validate({
            "name": "Branch",
            "nodes": [
                {"id": "n1", "type": "trigger"},
                {"id": "n2", "type": "condition", "expression": "x > 10"},
                {"id": "n3", "type": "action", "tool": "send_email", "name": "High"},
                {"id": "n4", "type": "action", "tool": "send_email", "name": "Low"},
                {"id": "n5", "type": "end"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3", "condition": "true"},
                {"from": "n2", "to": "n4", "condition": "false"},
                {"from": "n3", "to": "n5"},
                {"from": "n4", "to": "n5"},
            ],
        })
        result = compiler.compile(wf)
        assert result is not None

    def test_approval_node_compiles(self, compiler):
        wf = Workflow.model_validate({
            "name": "Approval",
            "nodes": [
                {"id": "n1", "type": "trigger"},
                {"id": "n2", "type": "action", "tool": "extract_invoice_data"},
                {"id": "n3", "type": "approval", "reason": "Need sign-off"},
                {"id": "n4", "type": "action", "tool": "process_payment"},
                {"id": "n5", "type": "end"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
                {"from": "n3", "to": "n4"},
                {"from": "n4", "to": "n5"},
            ],
        })
        result = compiler.compile(wf)
        assert result is not None
        node = result.get_node("n3")
        assert node is not None

    def test_retry_node_compiles(self, compiler):
        wf = Workflow.model_validate({
            "name": "Retry",
            "nodes": [
                {"id": "n1", "type": "trigger"},
                {"id": "n2", "type": "action", "tool": "send_email", "retry_count": 3, "retry_delay": 2.0},
                {"id": "n3", "type": "end"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
            ],
        })
        result = compiler.compile(wf)
        assert result is not None
        node = result.get_node("n2")
        assert node["retry_count"] == 3
        assert node["retry_delay"] == 2.0


class TestCompilerEdgeCases:
    def test_single_node_trigger_only(self, compiler):
        """Workflow with just a trigger and end."""
        wf = Workflow.model_validate({
            "name": "Minimal",
            "nodes": [
                {"id": "n1", "type": "trigger", "name": "Start"},
                {"id": "n2", "type": "end", "name": "Done"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
            ],
        })
        result = compiler.compile(wf)
        assert result is not None

    def test_complex_workflow_compiles(self, compiler):
        """The full invoice processing workflow should compile."""
        from examples import INVOICE_PROCESSING
        wf = Workflow.model_validate(INVOICE_PROCESSING)
        result = compiler.compile(wf)
        assert result is not None
        assert len(result.node_order) == 7
