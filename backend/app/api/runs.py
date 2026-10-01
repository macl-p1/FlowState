"""Runs API routes."""

import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkflowExecutionModel, StepExecutionModel
from app.engine.runner import WorkflowRunner, WorkflowNotFoundError
from app.tools.registry import registry


router = APIRouter()


_TERMINAL_STATUSES = frozenset({
    "completed", "failed", "cancelled",
})


def _serialize_step(step: StepExecutionModel) -> dict:
    return {
        "id": step.id,
        "node_id": step.node_id,
        "node_name": step.node_name,
        "node_type": step.node_type,
        "status": step.status.value,
        "tool_name": step.tool_name,
        "tool_inputs": step.tool_inputs,
        "tool_result": step.tool_result,
        "attempt_count": step.attempt_count,
        "error": step.error,
        "started_at": step.started_at.isoformat() if step.started_at else None,
        "completed_at": step.completed_at.isoformat() if step.completed_at else None,
    }


def _serialize_exec(exec_) -> dict:
    return {
        "id": exec_.id,
        "status": exec_.status.value,
        "current_node_id": exec_.current_node_id,
        "error_message": exec_.error_message,
        "started_at": exec_.started_at.isoformat() if exec_.started_at else None,
        "completed_at": exec_.completed_at.isoformat() if exec_.completed_at else None,
        "steps": [_serialize_step(s) for s in exec_.steps],
    }


@router.get("/runs/{run_id}/stream")
async def stream_run(run_id: str, db: Session = Depends(get_db)):
    """SSE stream of execution updates — sends steps as they appear in the DB."""
    exec_ = db.query(WorkflowExecutionModel).filter(
        WorkflowExecutionModel.id == run_id
    ).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator():
        # Immediately send current state
        yield f"event: snapshot\ndata: {json.dumps(_serialize_exec(exec_))}\n\n"

        if exec_.status.value in _TERMINAL_STATUSES:
            yield f"event: done\ndata: {{}}\n\n"
            return

        seen_step_ids: set = set(s.id for s in exec_.steps)

        try:
            while True:
                await asyncio.sleep(0.5)
                db.expire_all()

                exec_ = db.query(WorkflowExecutionModel).filter(
                    WorkflowExecutionModel.id == run_id
                ).first()
                if not exec_:
                    break

                current_status = exec_.status.value

                # Check for new steps
                current_step_ids = set(s.id for s in exec_.steps)
                new_ids = current_step_ids - seen_step_ids
                if new_ids:
                    new_steps = [s for s in exec_.steps if s.id in new_ids]
                    for step in new_steps:
                        seen_step_ids.add(step.id)
                        payload = json.dumps({
                            "type": "step",
                            "data": _serialize_step(step),
                        })
                        yield f"event: step\ndata: {payload}\n\n"

                # Check for status change
                payload = json.dumps({
                    "type": "status",
                    "data": {"status": current_status},
                })
                yield f"event: status\ndata: {payload}\n\n"

                # Send periodic full snapshot (every ~5s via the periodic status event)
                # The client can use this for live updates without full re-poll

                if current_status in _TERMINAL_STATUSES:
                    # Send final snapshot with all steps
                    final_payload = json.dumps(_serialize_exec(exec_))
                    yield f"event: snapshot\ndata: {final_payload}\n\n"
                    yield f"event: done\ndata: {{}}\n\n"
                    break
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


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
