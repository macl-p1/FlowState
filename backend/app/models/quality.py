"""Quality models — run evaluations and human corrections."""

from datetime import datetime
import uuid

from sqlalchemy import Column, String, Float, Text, JSON, DateTime, ForeignKey

from app.database import Base


class RunEvaluationModel(Base):
    """AI/heuristic judgement of whether a completed run produced the right result."""
    __tablename__ = "run_evaluations"

    id = Column(String, primary_key=True, default=lambda: f"eval_{uuid.uuid4().hex[:8]}")
    execution_id = Column(String, ForeignKey("workflow_executions.id"), nullable=False, unique=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)  # ok | suspect | bad
    reasons = Column(JSON, default=list)
    source = Column(String, default="heuristic")  # llm | heuristic
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RunCorrectionModel(Base):
    """A human saying 'this run's output was wrong / I had to fix it'."""
    __tablename__ = "run_corrections"

    id = Column(String, primary_key=True, default=lambda: f"corr_{uuid.uuid4().hex[:8]}")
    execution_id = Column(String, ForeignKey("workflow_executions.id"), nullable=False, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False, index=True)
    kind = Column(String, nullable=False)  # overridden | wrong_result | approval_rejected
    note = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
