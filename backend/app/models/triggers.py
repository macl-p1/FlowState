"""Trigger + run-metadata models: what starts runs, and where each run came from."""

from datetime import datetime
import uuid

from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey

from app.database import Base


class TriggerModel(Base):
    """Starts a workflow automatically: on a schedule (interval/cron) or via a secret webhook URL."""
    __tablename__ = "triggers"

    id = Column(String, primary_key=True, default=lambda: f"trg_{uuid.uuid4().hex[:8]}")
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False, index=True)
    kind = Column(String, nullable=False)  # schedule | webhook
    config = Column(JSON, default=dict)    # schedule: {interval_seconds | cron, context}; webhook: {}
    token = Column(String, unique=True, nullable=True, index=True)  # webhook secret (path component)
    enabled = Column(Boolean, default=True, nullable=False)
    next_run_at = Column(DateTime, nullable=True, index=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RunMetaModel(Base):
    """Per-run provenance. Its presence marks a run as queue-managed (the worker only starts runs that have one)."""
    __tablename__ = "run_meta"

    execution_id = Column(String, ForeignKey("workflow_executions.id"), primary_key=True)
    source = Column(String, default="manual", nullable=False)  # manual | schedule | webhook | replay
    trigger_id = Column(String, nullable=True)
    replay_of = Column(String, nullable=True, index=True)
    input_context = Column(JSON, default=dict)  # the original input, kept pristine for replay
    snapshot = Column(JSON, nullable=True)      # {"nodes", "edges"} as they were when the run was queued
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
