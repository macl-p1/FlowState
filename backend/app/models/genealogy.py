"""Genealogy models — workflow version history and lineage tracking."""

from sqlalchemy import (
    Column, String, Integer, Text, JSON, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.schemas.execution import ExecutionStatus


class WorkflowVersionModel(Base):
    """Snapshot of a workflow at a point in time with change tracking."""
    __tablename__ = "workflow_versions"

    id = Column(String, primary_key=True, default=lambda: f"ver_{uuid.uuid4().hex[:8]}")
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False, index=True)
    parent_version_id = Column(String, ForeignKey("workflow_versions.id"), nullable=True, index=True)
    version_number = Column(Integer, nullable=False, default=1)

    # Full graph snapshot
    nodes = Column(JSON, nullable=False)
    edges = Column(JSON, nullable=False)

    # Change tracking
    change_rationale = Column(Text, nullable=True)
    change_summary = Column(Text, nullable=True)
    diff_details = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workflow = relationship("WorkflowModel", back_populates="versions")
    parent_version = relationship("WorkflowVersionModel", remote_side=[id])
    children = relationship("WorkflowVersionModel", back_populates="parent_version")


class WorkflowBranchModel(Base):
    """Tracks when a workflow is forked from another (for lineage tree)."""
    __tablename__ = "workflow_branches"

    id = Column(String, primary_key=True, default=lambda: f"branch_{uuid.uuid4().hex[:8]}")
    source_workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False, index=True)
    source_version_id = Column(String, ForeignKey("workflow_versions.id"), nullable=True)
    branched_workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False, index=True)
    branch_name = Column(String, nullable=True)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
