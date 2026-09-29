"""Execution schema definitions — Pydantic models for workflow runs and steps."""

from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Workflow execution lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Individual step execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"
    SKIPPED = "skipped"


class StepExecution(BaseModel):
    """Record of a single node execution."""
    id: str
    execution_id: str
    node_id: str
    node_type: str
    node_name: str
    status: StepStatus = StepStatus.PENDING
    tool_name: str | None = None
    tool_inputs: dict[str, Any] | None = None
    tool_result: Any | None = None
    attempt_count: int = 1
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


class WorkflowExecution(BaseModel):
    """Record of a full workflow run."""
    id: str
    workflow_id: str
    workflow_name: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_node_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    steps: list[StepExecution] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    error_details: dict[str, Any] | None = None
