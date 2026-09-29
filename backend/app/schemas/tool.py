"""Tool schema definitions — Pydantic models for tool registry."""

from typing import Any
from pydantic import BaseModel, Field

from app.schemas.workflow import PermissionLevel


class Tool(BaseModel):
    """Definition of a registered tool."""
    name: str
    description: str
    input_schema: dict[str, Any] = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {},
            "required": [],
        }
    )
    permission: PermissionLevel = PermissionLevel.AUTO
    timeout_seconds: int = 30
    retryable: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """A request to execute a tool."""
    tool_name: str
    inputs: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Result from tool execution."""
    success: bool
    output: dict[str, Any] | None = None
    error: str | None = None
    retryable: bool = False
    warnings: list[str] = Field(default_factory=list)
