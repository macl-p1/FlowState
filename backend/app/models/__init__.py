"""SQLAlchemy ORM models."""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.schemas.workflow import NodeType, PermissionLevel
from app.schemas.execution import ExecutionStatus, StepStatus
from app.models.custom_tool import CustomTool  # noqa: F401 — ensures table is registered
from app.models.genealogy import WorkflowVersionModel, WorkflowBranchModel  # noqa: F401
from app.models.quality import RunEvaluationModel, RunCorrectionModel  # noqa: F401


def gen_id() -> str:
    return str(uuid.uuid4())


class WorkflowModel(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    nodes = Column("nodes", JSON, nullable=False)  # list of node dicts
    edges = Column("edges", JSON, nullable=False)  # list of edge dicts
    wf_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("WorkflowExecutionModel", back_populates="workflow", cascade="all, delete-orphan")
    versions = relationship("WorkflowVersionModel", back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowVersionModel.version_number")


class WorkflowExecutionModel(Base):
    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True, default=gen_id)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    workflow_name = Column(String, nullable=False)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    current_node_id = Column(String, nullable=True)
    context = Column(JSON, default=dict)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)

    workflow = relationship("WorkflowModel", back_populates="executions")
    steps = relationship("StepExecutionModel", back_populates="execution", cascade="all, delete-orphan", order_by="StepExecutionModel.created_at")
    approval = relationship("ApprovalRequestModel", back_populates="execution", uselist=False, cascade="all, delete-orphan")


class StepExecutionModel(Base):
    __tablename__ = "step_executions"

    id = Column(String, primary_key=True, default=gen_id)
    execution_id = Column(String, ForeignKey("workflow_executions.id"), nullable=False)
    node_id = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    node_name = Column(String, nullable=False)
    status = Column(SQLEnum(StepStatus), default=StepStatus.PENDING)
    tool_name = Column(String, nullable=True)
    tool_inputs = Column(JSON, nullable=True)
    tool_result = Column(JSON, nullable=True)
    attempt_count = Column(Integer, default=1)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    execution = relationship("WorkflowExecutionModel", back_populates="steps")


class ApprovalRequestModel(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True, default=gen_id)
    execution_id = Column(String, ForeignKey("workflow_executions.id"), nullable=False)
    node_id = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    approver_role = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    approver_id = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    execution = relationship("WorkflowExecutionModel", back_populates="approval")
