"""Verifier Agent — evaluates tool results against expected outcomes."""

from typing import Any
from anthropic import Anthropic

from app.config import settings
from app.schemas.tool import ToolResult


SYSTEM_PROMPT = """You are a workflow result verifier. Given a tool call and its result,
determine if the outcome matches expectations.

Respond with ONLY one of these verdicts:
- SUCCESS: The result matches the expected outcome
- RETRY: The result is unsatisfactory but retrying may help (transient errors)
- ESCALATE: The result indicates a business rule violation requiring human review
- FAIL: The result is a permanent failure that cannot be recovered

Also provide:
- confidence: 0.0 to 1.0
- user_message: short plain-English explanation for the user

Respond in this exact JSON format:
{"verdict": "SUCCESS|RETRY|ESCALATE|FAIL", "confidence": 0.95, "user_message": "..."}"""


class VerificationResult:
    def __init__(self, verdict: str, confidence: float, user_message: str):
        self.verdict = verdict
        self.confidence = confidence
        self.user_message = user_message


class VerifierAgent:
    """Evaluates tool execution results against expected outcomes."""

    def __init__(self, llm_client: Anthropic | None = None):
        self.client = llm_client or Anthropic(
            api_key=settings.anthropic_api_key,
            base_url=settings.anthropic_base_url or None,
        )
        self.model = settings.anthropic_model

    async def verify(
        self,
        tool_name: str,
        tool_result: ToolResult,
        expected_outcome: str | None = None,
    ) -> VerificationResult:
        """
        Verify if a tool result meets expectations.

        Falls back to rule-based verification if LLM is not available.
        """
        # If no API key, use rule-based verification
        if not settings.anthropic_api_key:
            return self._rule_based_verify(tool_name, tool_result, expected_outcome)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                temperature=0.0,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": json.dumps({
                        "tool": tool_name,
                        "result": tool_result.model_dump(),
                        "expected_outcome": expected_outcome or "Operation completed successfully",
                    }),
                }],
            )

            import json as json_module

            # Extract text, skipping thinking blocks
            text_content = ""
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    text_content += block.text

            data = json_module.loads(text_content.strip())
            return VerificationResult(
                verdict=data["verdict"],
                confidence=data["confidence"],
                user_message=data["user_message"],
            )
        except Exception:
            return self._rule_based_verify(tool_name, tool_result, expected_outcome)

    def _rule_based_verify(
        self,
        tool_name: str,
        tool_result: ToolResult,
        expected_outcome: str | None,
    ) -> VerificationResult:
        """Fallback rule-based verification when LLM is unavailable."""
        if tool_result.success:
            if tool_result.warnings:
                return VerificationResult(
                    verdict="ESCALATE",
                    confidence=0.9,
                    user_message=f"Operation succeeded but has warnings: {'; '.join(tool_result.warnings)}",
                )
            return VerificationResult(
                verdict="SUCCESS",
                confidence=0.95,
                user_message=f"{tool_name} completed successfully.",
            )
        else:
            if tool_result.retryable:
                return VerificationResult(
                    verdict="RETRY",
                    confidence=0.8,
                    user_message=f"{tool_name} failed with retryable error: {tool_result.error}",
                )
            return VerificationResult(
                verdict="FAIL",
                confidence=0.9,
                user_message=f"{tool_name} failed permanently: {tool_result.error}",
            )
