"""Verifier agent tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.agents.verifier import VerifierAgent, VerificationResult
from app.schemas.tool import ToolResult


@pytest.fixture
def verifier():
    return VerifierAgent()


class TestVerifierRuleBased:
    """Test the rule-based fallback verifier (no LLM needed)."""

    def test_success_result(self, verifier):
        result = verifier._rule_based_verify(
            "send_email",
            ToolResult(success=True, output={"message_id": "msg_123"}),
            "Email sent successfully",
        )
        assert result.verdict == "SUCCESS"
        assert result.confidence > 0

    def test_retryable_failure(self, verifier):
        result = verifier._rule_based_verify(
            "send_email",
            ToolResult(success=False, error="API returned 503", retryable=True),
            "Email sent successfully",
        )
        assert result.verdict == "RETRY"

    def test_non_retryable_failure(self, verifier):
        result = verifier._rule_based_verify(
            "search_database",
            ToolResult(success=False, error="Authentication failed", retryable=False),
            "Records found",
        )
        assert result.verdict == "FAIL"

    def test_success_with_warnings_escalates(self, verifier):
        result = verifier._rule_based_verify(
            "validate_invoice",
            ToolResult(
                success=True,
                output={"amount": 500000},
                warnings=["Amount exceeds approval threshold"],
            ),
            "Invoice is under $100,000",
        )
        assert result.verdict == "ESCALATE"

    def test_user_message_provided(self, verifier):
        result = verifier._rule_based_verify(
            "send_email",
            ToolResult(success=False, error="Connection timeout", retryable=True),
            "Email sent",
        )
        assert len(result.user_message) > 0
        assert "send_email" in result.user_message or "timeout" in result.user_message.lower()


class TestVerifierLLM:
    """Test LLM-based verifier with mocked responses."""

    @pytest.mark.asyncio
    async def test_llm_verify_success(self, verifier, monkeypatch):
        client = MagicMock()
        response = MagicMock()
        response.content = [MagicMock(text='{"verdict": "SUCCESS", "confidence": 0.95, "user_message": "OK"}')]
        client.messages.create = AsyncMock(return_value=response)
        monkeypatch.setattr(verifier, "client", client)

        result = await verifier.verify(
            "send_email",
            ToolResult(success=True),
            "Email sent",
        )
        assert result.verdict == "SUCCESS"

    @pytest.mark.asyncio
    async def test_llm_verify_falls_back_on_error(self, verifier, monkeypatch):
        """If LLM call fails, should fall back to rule-based."""
        client = MagicMock()
        client.messages.create = AsyncMock(side_effect=Exception("API error"))
        monkeypatch.setattr(verifier, "client", client)
        monkeypatch.setattr("app.agents.verifier.settings.anthropic_api_key", "fake-key")

        result = await verifier.verify(
            "send_email",
            ToolResult(success=True),
            "Email sent",
        )
        # Should fall back to rule-based and return SUCCESS
        assert result.verdict == "SUCCESS"
