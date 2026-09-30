"""Schemas for integration config management."""

from pydantic import BaseModel, Field
from typing import Any, Optional


class IntegrationConfigUpdate(BaseModel):
    """Set or update integration config for a tool."""
    integration_config: Optional[dict[str, Any]] = Field(
        default=None,
        description="Integration config dict. Pass null to remove (revert to mock).",
    )


class IntegrationTestRequest(BaseModel):
    """Request to test a real integration connection."""
    test_inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional test inputs to pass to the integration handler.",
    )


class IntegrationTestResponse(BaseModel):
    """Result of testing an integration connection."""
    success: bool
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    message: str
    elapsed_seconds: float
