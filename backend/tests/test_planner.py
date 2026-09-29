"""Planner agent tests — mock-based tests without calling real Claude API."""

import json
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.agents.planner import PlannerAgent, PlanningResult, PlanningError
from app.tools.registry import ToolRegistry
from app.schemas.workflow import Workflow


INVOICE_RESPONSE = json.dumps({
    "name": "Invoice Processing",
    "description": "Process invoices with approval",
    "nodes": [
        {"id": "n1", "type": "trigger", "name": "Invoice Received"},
        {"id": "n2", "type": "action", "name": "Extract Data", "tool": "extract_invoice_data"},
        {"id": "n3", "type": "action", "name": "Find PO", "tool": "search_database"},
        {"id": "n4", "type": "condition", "name": "Amount Check", "expression": "amount > 100000"},
        {"id": "n5", "type": "approval", "name": "Manager Approval", "reason": "Exceeds threshold"},
        {"id": "n6", "type": "action", "name": "Process Payment", "tool": "process_payment"},
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
})

ONBOARDING_RESPONSE = json.dumps({
    "name": "Employee Onboarding",
    "description": "Onboard new employees",
    "nodes": [
        {"id": "n1", "type": "trigger", "name": "Employee Added"},
        {"id": "n2", "type": "action", "name": "Request Docs", "tool": "send_email"},
        {"id": "n3", "type": "condition", "name": "Docs Complete"},
        {"id": "n4", "type": "action", "name": "Notify HR", "tool": "send_slack_message"},
        {"id": "n5", "type": "action", "name": "Remind", "tool": "send_email"},
        {"id": "n6", "type": "action", "name": "Notify Manager", "tool": "send_email"},
        {"id": "n7", "type": "end", "name": "Done"},
    ],
    "edges": [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "n3"},
        {"from": "n3", "to": "n4", "condition": "true"},
        {"from": "n3", "to": "n5", "condition": "false"},
        {"from": "n4", "to": "n6"},
        {"from": "n5", "to": "n6"},
        {"from": "n6", "to": "n7"},
    ],
})

MALFORMED_RESPONSE = "Here is a workflow... sorry I cannot provide JSON."
INVALID_TOOL_RESPONSE = json.dumps({
    "name": "Bad",
    "nodes": [{"id": "n1", "type": "action", "tool": "teleport", "name": "Teleport"}],
    "edges": [],
})


def make_mock_client(response_text: str):
    """Create a mock Anthropic client that returns a fixed response.

    Note: Anthropic SDK's messages.create() is synchronous, not async.
    """
    client = MagicMock()
    response = MagicMock()
    # .text must be a real string, not another MagicMock
    response.content = [MagicMock()]
    response.content[0].text = response_text
    client.messages.create = MagicMock(return_value=response)
    return client


def make_mock_client_with_sequence(responses: list[str]):
    """Create a mock client that returns responses in sequence."""
    client = MagicMock()
    call_count = [0]

    def create(*args, **kwargs):
        idx = min(call_count[0], len(responses) - 1)
        call_count[0] += 1
        response = MagicMock()
        response.content = [MagicMock()]
        response.content[0].text = responses[idx]
        return response

    client.messages.create = MagicMock(side_effect=create)
    return client


@pytest.fixture
def mock_registry():
    return ToolRegistry()


class TestPlannerAgent:
    @pytest.mark.asyncio
    async def test_planner_generates_invoice_workflow(self, mock_registry):
        client = make_mock_client(INVOICE_RESPONSE)
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Process invoices with approval for amounts over $100k")

        assert result.success is True
        assert result.workflow is not None
        assert result.workflow.name == "Invoice Processing"
        assert len(result.workflow.nodes) == 7

    @pytest.mark.asyncio
    async def test_planner_generates_onboarding_workflow(self, mock_registry):
        client = make_mock_client(ONBOARDING_RESPONSE)
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Onboard a new employee")

        assert result.success is True
        assert result.workflow.name == "Employee Onboarding"
        assert len(result.workflow.nodes) == 7

    @pytest.mark.asyncio
    async def test_planner_rejects_unknown_tools(self, mock_registry):
        client = make_mock_client(INVALID_TOOL_RESPONSE)
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Use teleport to ship")

        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_planner_repairs_malformed_output(self, mock_registry):
        client = make_mock_client_with_sequence([MALFORMED_RESPONSE, INVOICE_RESPONSE])
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Process an invoice")

        assert result.success is True
        assert client.messages.create.call_count == 2

    @pytest.mark.asyncio
    async def test_planner_exhausts_retries(self, mock_registry):
        client = make_mock_client_with_sequence([MALFORMED_RESPONSE] * 5)
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Process an invoice")

        assert result.success is False
        assert "validation" in result.error.lower() or "failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_planner_metadata_extraction(self, mock_registry):
        client = make_mock_client(INVOICE_RESPONSE)
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Process invoices")

        assert result.success is True
        meta = planner.get_planning_metadata(result.workflow)
        assert meta["node_count"] == 7
        assert "extract_invoice_data" in meta["tools_used"]
        assert meta["approval_gates"] == 1
        assert meta["has_branching"] is True

    @pytest.mark.asyncio
    async def test_planner_no_api_key_graceful_failure(self, mock_registry, monkeypatch):
        """Without an API key, planner should still return a valid result via fallback."""
        monkeypatch.setattr("app.agents.planner.settings.anthropic_api_key", "")
        planner = PlannerAgent(tool_registry=mock_registry)
        # Should not crash — it will try to call Anthropic and fail
        result = await planner.plan("Do something")
        # Either success or a proper error, never a crash
        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "error")

    @pytest.mark.asyncio
    async def test_planner_linear_workflow(self, mock_registry):
        linear_response = json.dumps({
            "name": "Send Report",
            "description": "Generate and send a report",
            "nodes": [
                {"id": "n1", "type": "trigger", "name": "Schedule Trigger"},
                {"id": "n2", "type": "action", "name": "Generate Report", "tool": "search_database"},
                {"id": "n3", "type": "action", "name": "Send Report", "tool": "send_email"},
                {"id": "n4", "type": "end", "name": "Done"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
                {"from": "n3", "to": "n4"},
            ],
        })
        client = make_mock_client(linear_response)
        planner = PlannerAgent(tool_registry=mock_registry, llm_client=client)
        result = await planner.plan("Generate a report and email it")

        assert result.success is True
        assert len(result.workflow.nodes) == 4
        node_types = [n.get("type") for n in result.workflow.nodes]
        assert "trigger" in node_types
        assert "end" in node_types
