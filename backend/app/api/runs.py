"""Runs API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkflowExecutionModel
from app.engine.runner import WorkflowRunner, WorkflowNotFoundError
from app.schemas.execution import ExecutionStatus
from app.tools.registry import registry


router = APIRouter()


@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get execution details."""
    exec_ = db.query(WorkflowExecutionModel).filter(
        WorkflowExecutionModel.id == run_id
    ).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": exec_.id,
        "workflow_id": exec_.workflow_id,
        "workflow_name": exec_.workflow_name,
        "status": exec_.status.value,
        "current_node_id": exec_.current_node_id,
        "context": exec_.context,
        "error_message": exec_.error_message,
        "started_at": exec_.started_at.isoformat() if exec_.started_at else None,
        "completed_at": exec_.completed_at.isoformat() if exec_.completed_at else None,
        "steps": [
            {
                "id": s.id,
                "node_id": s.node_id,
                "node_name": s.node_name,
                "node_type": s.node_type,
                "status": s.status.value,
                "tool_name": s.tool_name,
                "tool_inputs": s.tool_inputs,
                "tool_result": s.tool_result,
                "attempt_count": s.attempt_count,
                "error": s.error,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in exec_.steps
        ],
        "approval": (
            {
                "id": exec_.approval.id,
                "reason": exec_.approval.reason,
                "context": exec_.approval.context,
                "status": exec_.approval.status,
            }
            if exec_.approval else None
        ),
    }


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, db: Session = Depends(get_db)):
    """Cancel a running execution."""
    runner = WorkflowRunner(db=db, tool_registry=registry)
    try:
        execution = await runner.cancel(run_id)
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": execution.id,
        "status": execution.status.value,
    }


@router.get("/runs")
async def list_runs(db: Session = Depends(get_db), limit: int = 50):
    """List recent executions."""
    executions = db.query(WorkflowExecutionModel).order_by(
        WorkflowExecutionModel.started_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": e.id,
            "workflow_id": e.workflow_id,
            "workflow_name": e.workflow_name,
            "status": e.status.value,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in executions
    ]
