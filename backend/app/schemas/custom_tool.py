"""Schemas for custom tools."""

from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime
from app.schemas.tool import Tool


class CustomToolCreate(BaseModel):
    name: str
    description: str
    tool_type: str = "custom"
    input_schema: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    config: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)


class CustomToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tool_type: str | None = None
    input_schema: dict[str, Any] | None = None
    config: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    status: str | None = None


class CustomToolResponse(BaseModel):
    id: str
    name: str
    description: str
    tool_type: str
    status: str
    input_schema: dict[str, Any]
    config: dict[str, Any]
    output_schema: dict[str, Any]
    last_test_result: dict[str, Any] | None
    verified_at: datetime | None
    verified_by: str | None
    created_at: datetime
    updated_at: datetime


class ToolVerifyRequest(BaseModel):
    """Request to verify a custom tool — runs a test execution."""
    test_inputs: dict[str, Any] = Field(default_factory=dict)


class ToolVerifyResponse(BaseModel):
    success: bool
    output: dict[str, Any] | None
    error: str | None
    message: str


class ToolCategory(BaseModel):
    type: str
    label: str
    icon: str
    description: str
    count: int
