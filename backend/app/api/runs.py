"""Runs API routes."""

import asyncio
import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.jobs import enqueue_run, get_worker, WorkflowInvalid
from app.models.triggers import RunMetaModel
from app.models import WorkflowModel, WorkflowExecutionModel, StepExecutionModel, RunEvaluationModel, RunCorrectionModel
from app.api.quality import serialize_evaluation
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
    """SSE stream of execution progress.

    Unnamed messages (EventSource.onmessage): {"type": "step", "data": step} per finished step and
    {"type": "status", "data": {"status", "current_node_id"}} whenever status or the running node changes.
    Named events: "snapshot" (full state) and "done".
    """
    exists = db.query(WorkflowExecutionModel.id).filter(WorkflowExecutionModel.id == run_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Run not found")
    bind = db.get_bind()

    def msg(kind: str, data: dict) -> str:
        return f"data: {json.dumps({'type': kind, 'data': data})}\n\n"

    async def event_generator():
        # The request-scoped session is closed before the body streams, so use our own.
        with Session(bind) as sdb:
            def load():
                sdb.expire_all()
                return sdb.query(WorkflowExecutionModel).filter(WorkflowExecutionModel.id == run_id).first()

            current = load()
            yield f"event: snapshot\ndata: {json.dumps(_serialize_exec(current))}\n\n"
            if current.status.value in _TERMINAL_STATUSES:
                yield "event: done\ndata: {}\n\n"
                return

            wf = sdb.query(WorkflowModel).filter(WorkflowModel.id == current.workflow_id).first()
            node_names = {n.get("id"): n.get("name") for n in (wf.nodes if wf else [])}
            seen_step_ids: set = {s.id for s in current.steps}
            last_status = None
            try:
                while True:
                    await asyncio.sleep(0.25)
                    current = load()
                    if not current:
                        break

                    for step in current.steps:
                        if step.id not in seen_step_ids:
                            seen_step_ids.add(step.id)
                            yield msg("step", _serialize_step(step))

                    state = (current.status.value, current.current_node_id)
                    if state != last_status:
                        last_status = state
                        yield msg("status", {"status": state[0], "current_node_id": state[1],
                                             "current_node_name": node_names.get(state[1])})

                    if current.status.value in _TERMINAL_STATUSES:
                        yield f"event: snapshot\ndata: {json.dumps(_serialize_exec(current))}\n\n"
                        yield "event: done\ndata: {}\n\n"
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


@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: Session = Depends(get_db)):
    exec_ = db.query(WorkflowExecutionModel).filter(WorkflowExecutionModel.id == run_id).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="Run not found")
    quality = db.query(RunEvaluationModel).filter_by(execution_id=run_id).first()
    return {
        **_serialize_exec(exec_),
        "workflow_id": exec_.workflow_id,
        "workflow_name": exec_.workflow_name,
        "quality": serialize_evaluation(quality),
        **_meta(db, run_id),
    }


def _meta(db: Session, run_id: str) -> dict:
    m = db.get(RunMetaModel, run_id)
    return {"source": m.source if m else "manual", "replay_of": m.replay_of if m else None,
            "trigger_id": m.trigger_id if m else None}


class ReplayRequest(BaseModel):
    latest: bool = False  # False: replay against the workflow definition as it was when the run was queued


@router.post("/runs/{run_id}/replay")
async def replay_run(run_id: str, req: ReplayRequest, db: Session = Depends(get_db)):
    """Run it again with the same input (and, by default, the same workflow definition)."""
    ex = db.query(WorkflowExecutionModel).filter(WorkflowExecutionModel.id == run_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Run not found")
    meta = db.get(RunMetaModel, run_id)
    context = (meta.input_context if meta else ex.context) or {}
    snapshot = None if (req.latest or not meta) else meta.snapshot
    try:
        new_id = enqueue_run(db, ex.workflow_id, context, "replay", replay_of=run_id, snapshot=snapshot)
    except LookupError:
        raise HTTPException(status_code=404, detail="Workflow no longer exists")
    except WorkflowInvalid as e:
        raise HTTPException(status_code=400, detail=str(e))
    get_worker(db.get_bind()).kick()
    return {"id": new_id, "replay_of": run_id, "status": "pending"}


@router.delete("/runs/{run_id}")
async def delete_run(run_id: str, db: Session = Depends(get_db)):
    exec_ = db.query(WorkflowExecutionModel).filter(WorkflowExecutionModel.id == run_id).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="Run not found")
    # quality rows have no ORM cascade
    db.query(RunEvaluationModel).filter_by(execution_id=run_id).delete()
    db.query(RunCorrectionModel).filter_by(execution_id=run_id).delete()
    db.delete(exec_)
    db.commit()
    return {"deleted": run_id}


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, db: Session = Depends(get_db)):
    """Cancel a running execution."""
    if get_worker(db.get_bind()).cancel(run_id):  # in flight: stop the task; the worker records CANCELLED
        return {"id": run_id, "status": "cancelled"}
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

    metas = {m.execution_id: m for m in db.query(RunMetaModel).filter(
        RunMetaModel.execution_id.in_([e.id for e in executions])).all()}
    return [
        {
            "source": metas[e.id].source if e.id in metas else "manual",
            "replay_of": metas[e.id].replay_of if e.id in metas else None,
            "id": e.id,
            "workflow_id": e.workflow_id,
            "workflow_name": e.workflow_name,
            "status": e.status.value,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in executions
    ]
