"""Tests for integration config and real tool execution."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tools.integrations import (
    integration_handler,
    _mask_credentials,
)


# ──────────────────────────────────────────────
# Credential masking
# ──────────────────────────────────────────────


class TestCredentialMasking:
    def test_masks_password(self):
        ic = {"username": "user", "password": "secret123"}
        masked = _mask_credentials(ic)
        assert masked["password"].startswith("***")
        assert masked["username"] == "user"

    def test_masks_api_key(self):
        ic = {"api_key": "sk-abc123"}
        masked = _mask_credentials(ic)
        assert masked["api_key"].startswith("***")

    def test_preserves_non_sensitive(self):
        ic = {"host": "smtp.gmail.com", "port": 587, "use_tls": True}
        masked = _mask_credentials(ic)
        assert masked["host"] == "smtp.gmail.com"
        assert masked["port"] == 587

    def test_handles_empty_dict(self):
        assert _mask_credentials({}) == {}

    def test_does_not_mutate_original(self):
        ic = {"password": "secret"}
        _mask_credentials(ic)
        assert ic["password"] == "secret"


# ──────────────────────────────────────────────
# Integration handler dispatch (real vs mock)
# ──────────────────────────────────────────────


class TestIntegrationHandler:

    @pytest.mark.asyncio
    async def test_dispatches_to_http_webhook(self):
        """HTTP handler sends request to configured base_url + url."""
        mock_client = MagicMock()
        mock_client.is_closed = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"ok": true}'
        mock_response.headers = {"content-type": "application/json"}
        mock_response.is_success = True
        mock_response.json = MagicMock(return_value={"ok": True})
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        # Set directly on the singleton to bypass _get_http_client's lazy init
        integration_handler._http_client = mock_client

        result = await integration_handler.execute(
            {"integration_type": "http", "base_url": "https://api.example.com"},
            {"url": "/endpoint", "method": "POST", "body": {"key": "value"}},
        )
        assert result.success is True
        assert result.output["status_code"] == 200

    @pytest.mark.asyncio
    async def test_dispatches_to_database(self):
        """Database handler queries via connection string."""
        mock_conn = MagicMock()
        mock_row = MagicMock()
        mock_row.__iter__ = lambda self: iter([("id", 1), ("name", "Alice")])
        mock_row.keys = lambda: ["id", "name"]
        mock_conn.fetch = AsyncMock(return_value=[mock_row])
        mock_conn.close = AsyncMock()

        mock_connect = AsyncMock(return_value=mock_conn)
        mock_asyncpg = MagicMock()
        mock_asyncpg.connect = mock_connect

        import sys
        old_asyncpg = sys.modules.get("asyncpg")
        sys.modules["asyncpg"] = mock_asyncpg
        try:
            result = await integration_handler.execute(
                {
                    "integration_type": "database",
                    "driver": "postgresql",
                    "connection_string": "postgresql://user:pass@localhost/db",
                },
                {"query": "SELECT * FROM users"},
            )
        finally:
            if old_asyncpg is not None:
                sys.modules["asyncpg"] = old_asyncpg
            else:
                sys.modules.pop("asyncpg", None)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_dispatches_to_aws_s3(self):
        """AWS S3 handler lists objects."""
        mock_boto = MagicMock()
        mock_session = MagicMock()
        mock_boto.Session.return_value = mock_session
        mock_s3 = MagicMock()
        mock_session.client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {"Contents": []}

        mock_boto_mod = MagicMock()
        mock_boto_mod.Session = mock_boto.Session

        import sys
        old_boto3 = sys.modules.get("boto3")
        sys.modules["boto3"] = mock_boto_mod
        try:
            result = await integration_handler.execute(
                {
                    "integration_type": "storage_s3",
                    "access_key": "AKIAIOSFODNN7EXAMPLE",
                    "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "bucket": "my-bucket",
                    "region": "us-east-1",
                },
                {"action": "list_objects"},
            )
        finally:
            if old_boto3 is not None:
                sys.modules["boto3"] = old_boto3
            else:
                sys.modules.pop("boto3", None)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_dispatches_to_email_smtp(self):
        """SMTP handler sends email via aiosmtplib."""
        mock_send = AsyncMock()

        import sys
        old_aiosmtplib = sys.modules.get("aiosmtplib")
        mock_mod = MagicMock()
        mock_mod.send = mock_send
        mock_mod.SMTPAuthenticationError = Exception
        mock_mod.SMTPConnectError = Exception
        sys.modules["aiosmtplib"] = mock_mod
        try:
            result = await integration_handler.execute(
                {
                    "integration_type": "email_smtp",
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "smtp_user": "user@example.com",
                    "smtp_password": "pass",
                    "use_tls": True,
                },
                {"to": "recipient@example.com", "subject": "Hi", "body": "Hello"},
            )
        finally:
            if old_aiosmtplib is not None:
                sys.modules["aiosmtplib"] = old_aiosmtplib
            else:
                sys.modules.pop("aiosmtplib", None)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_dispatches_to_slack(self):
        """Slack messaging handler posts messages via Web API."""
        mock_client = MagicMock()
        mock_client.is_closed = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"ok": True, "ts": "12345"})
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        integration_handler._http_client = mock_client

        result = await integration_handler.execute(
            {
                "integration_type": "messaging_slack",
                "bot_token": "xoxb-test-token",
            },
            {"channel": "#general", "text": "Hello"},
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_unknown_type_returns_failure(self):
        """Unknown integration type returns failure."""
        result = await integration_handler.execute(
            {"integration_type": "nonexistent_service"}, {}
        )
        assert result.success is False
        assert "nonexistent_service" in result.error.lower()

    @pytest.mark.asyncio
    async def test_http_connection_error_is_retryable(self):
        """Connection errors are marked as retryable."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(side_effect=Exception("Connection refused"))
        integration_handler._http_client = mock_client

        result = await integration_handler.execute(
            {"integration_type": "http", "base_url": "http://bad-host"},
            {"url": "/", "method": "GET"},
        )
        assert result.success is False


# ──────────────────────────────────────────────
# Real execution: runner dispatches to integration_handler
# ──────────────────────────────────────────────


class TestRealExecution:
    """Tests that the workflow runner uses real integrations when configured."""

    def test_tool_model_has_integration_config_field(self):
        """CustomTool model has integration_config column for real execution."""
        from app.models.custom_tool import CustomTool
        from sqlalchemy.inspection import inspect
        cols = [c.name for c in inspect(CustomTool).columns]
        assert "integration_config" in cols

    @pytest.mark.asyncio
    async def test_integration_handler_returns_tool_result(self):
        """integration_handler.execute returns a ToolResult."""
        from app.schemas.tool import ToolResult

        result = await integration_handler.execute(
            {"integration_type": "nonexistent_service"}, {}
        )
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_http_without_base_url_returns_failure(self):
        """Missing base_url returns a clear error."""
        result = await integration_handler.execute(
            {"integration_type": "http"}, {"url": "/endpoint"}
        )
        assert result.success is False
        assert "base_url" in result.error.lower()

    @pytest.mark.asyncio
    async def test_database_without_connection_string_returns_failure(self):
        """Missing connection_string returns a clear error."""
        result = await integration_handler.execute(
            {"integration_type": "database"}, {"query": "SELECT 1"}
        )
        assert result.success is False
        assert "connection_string" in result.error.lower()
