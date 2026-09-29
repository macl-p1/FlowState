"""Tool registry tests."""

import pytest

from app.tools.registry import (
    ToolRegistry, ToolAlreadyRegisteredError, UnknownToolError, registry
)
from app.schemas.tool import Tool, PermissionLevel


class TestToolRegistration:
    def test_register_and_retrieve(self):
        r = ToolRegistry()
        tool = Tool(
            name="test_tool",
            description="A test tool",
            permission=PermissionLevel.AUTO,
        )
        r.register(tool)
        assert r.get("test_tool") == tool

    def test_list_all_returns_defaults(self):
        r = ToolRegistry()
        tools = r.list_all()
        assert len(tools) > 0
        names = {t.name for t in tools}
        assert "send_email" in names
        assert "search_database" in names

    def test_has_returns_true_for_registered(self):
        r = ToolRegistry()
        assert r.has("send_email") is True

    def test_has_returns_false_for_unknown(self):
        r = ToolRegistry()
        assert r.has("nonexistent_tool") is False

    def test_get_returns_none_for_unknown(self):
        r = ToolRegistry()
        assert r.get("nonexistent_tool") is None

    def test_duplicate_registration_raises(self):
        r = ToolRegistry()
        tool = Tool(name="dup_tool", description="test")
        r.register(tool)
        with pytest.raises(ToolAlreadyRegisteredError) as exc:
            r.register(tool)
        assert "dup_tool" in str(exc.value)

    def test_registry_has_all_expected_tools(self):
        r = ToolRegistry()
        expected = {
            "send_email", "send_slack_message", "search_database",
            "update_database", "create_ticket", "create_calendar_event",
            "request_human_approval", "wait",
        }
        actual = {t.name for t in r.list_all()}
        assert expected.issubset(actual)


class TestToolPermissions:
    def test_auto_permission(self):
        tool = Tool(name="query", description="q", permission=PermissionLevel.AUTO)
        assert tool.permission == PermissionLevel.AUTO

    def test_confirm_permission(self):
        tool = Tool(name="update", description="u", permission=PermissionLevel.CONFIRM)
        assert tool.permission == PermissionLevel.CONFIRM

    def test_human_only_permission(self):
        tool = Tool(name="pay", description="p", permission=PermissionLevel.HUMAN_ONLY)
        assert tool.permission == PermissionLevel.HUMAN_ONLY


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_execute_send_email(self):
        r = ToolRegistry()
        result = await r.execute("send_email", {"to": "test@example.com", "subject": "Hi", "body": "Hello"})
        assert result.success is True
        assert result.output["message_id"] is not None

    @pytest.mark.asyncio
    async def test_execute_unknown_tool_raises(self):
        r = ToolRegistry()
        with pytest.raises(UnknownToolError) as exc:
            await r.execute("nonexistent", {})
        assert "nonexistent" in str(exc.value)

    @pytest.mark.asyncio
    async def test_execute_send_email_missing_to(self):
        r = ToolRegistry()
        result = await r.execute("send_email", {"subject": "Hi"})
        assert result.success is False
        assert "to" in result.error.lower() or "required" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_search_database(self):
        r = ToolRegistry()
        result = await r.execute("search_database", {"table": "purchase_orders"})
        assert result.success is True
        assert "records" in result.output

    @pytest.mark.asyncio
    async def test_execute_search_invalid_table(self):
        r = ToolRegistry()
        result = await r.execute("search_database", {"table": "nonexistent_table"})
        assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_human_approval(self):
        r = ToolRegistry()
        result = await r.execute("request_human_approval", {"reason": "Test approval"})
        assert result.success is True
        assert result.output["status"] == "pending"
        assert "approval_id" in result.output

    @pytest.mark.asyncio
    async def test_execute_wait(self):
        r = ToolRegistry()
        result = await r.execute("wait", {"seconds": 1})
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_extract_invoice(self):
        r = ToolRegistry()
        result = await r.execute("extract_invoice_data", {"document": "test.pdf"})
        assert result.success is True
        assert "vendor" in result.output
        assert "amount" in result.output

    @pytest.mark.asyncio
    async def test_execute_process_payment(self):
        r = ToolRegistry()
        result = await r.execute("process_payment", {"invoice_id": "inv_001", "amount": 45000})
        assert result.success is True
        assert "payment_id" in result.output

    @pytest.mark.asyncio
    async def test_execute_update_database(self):
        r = ToolRegistry()
        result = await r.execute("update_database", {
            "table": "invoices",
            "id": "inv_001",
            "updates": {"status": "paid"},
        })
        assert result.success is True

    @pytest.mark.asyncio
    async def test_create_ticket(self):
        r = ToolRegistry()
        result = await r.execute("create_ticket", {"title": "Test ticket", "priority": "high"})
        assert result.success is True
        assert "ticket_id" in result.output
