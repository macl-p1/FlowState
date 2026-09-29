"""Workflow schema definitions — Pydantic models for the universal workflow format."""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional, Any
from enum import Enum


class NodeType(str, Enum):
    """Supported workflow node types."""
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    APPROVAL = "approval"
    WAIT = "wait"
    END = "end"


class PermissionLevel(str, Enum):
    """Tool permission levels."""
    AUTO = "AUTO"             # Execute without confirmation
    CONFIRM = "CONFIRM"       # Ask for confirmation before execution
    HUMAN_ONLY = "HUMAN_ONLY"  # Requires human to manually execute


class TriggerType(str, Enum):
    MANUAL = "manual"
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"


# --- Trigger ---

class Trigger(BaseModel):
    type: TriggerType = TriggerType.MANUAL
    schedule: Optional[str] = None  # cron expression if scheduled


# --- Nodes ---

class TriggerNode(BaseModel):
    id: str
    type: Literal["trigger"] = "trigger"
    name: str
    trigger: Trigger = Field(default_factory=Trigger)


class ActionNode(BaseModel):
    id: str
    type: Literal["action"] = "action"
    name: str
    tool: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected_outcome: Optional[str] = None
    retry_count: int = 0
    retry_delay: float = 1.0


class ConditionNode(BaseModel):
    id: str
    type: Literal["condition"] = "condition"
    name: str
    expression: str  # Python-like expression evaluated against context


class ApprovalNode(BaseModel):
    id: str
    type: Literal["approval"] = "approval"
    name: str
    reason: str
    approver_role: Optional[str] = None  # e.g. "manager", "finance_team"


class WaitNode(BaseModel):
    id: str
    type: Literal["wait"] = "wait"
    name: str
    duration_seconds: int = 60


class EndNode(BaseModel):
    id: str
    type: Literal["end"] = "end"
    name: str
    outcome: str = "completed"  # completed, failed, cancelled


# Union type for all nodes
Node = TriggerNode | ActionNode | ConditionNode | ApprovalNode | WaitNode | EndNode


# --- Edges ---

class Edge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    condition: Optional[str] = None  # "true" / "false" or expression

    model_config = {"populate_by_name": True}


# --- Workflow ---

class Workflow(BaseModel):
    """Universal workflow definition."""
    name: str
    description: str = ""
    nodes: list[dict[str, Any]]  # Raw dicts — validated on compile
    edges: list[dict[str, Any]]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("nodes")
    @classmethod
    def validate_nodes(cls, v):
        if not v:
            raise ValueError("Workflow must have at least one node")
        ids = [n.get("id") for n in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate node IDs found")
        return v

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, v, info):
        nodes = info.data.get("nodes", [])
        node_ids = {n.get("id") for n in nodes}
        for edge in v:
            from_id = edge.get("from")
            to_id = edge.get("to")
            if from_id and from_id not in node_ids:
                raise ValueError(f"Edge references unknown node: {from_id}")
            if to_id and to_id not in node_ids:
                raise ValueError(f"Edge references unknown node: {to_id}")
        return v

    @model_validator(mode="after")
    def validate_trigger_exists(self):
        node_types = [n.get("type") for n in self.nodes]
        if "trigger" not in node_types:
            raise ValueError("Workflow must have exactly one trigger node")
        trigger_count = node_types.count("trigger")
        if trigger_count > 1:
            raise ValueError("Workflow must have exactly one trigger node")
        return self


# --- Serialization helpers ---

def workflow_to_dict(workflow: Workflow) -> dict:
    """Serialize workflow to JSON-compatible dict."""
    return workflow.model_dump(by_alias=True)


def workflow_from_dict(data: dict) -> Workflow:
    """Deserialize workflow from JSON-compatible dict."""
    return Workflow.model_validate(data)
