"""Trigger API: schedules and webhooks that start workflows automatically."""

import secrets
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.jobs import enqueue_run, get_worker, next_fire, WorkflowInvalid
from app.models import WorkflowModel
from app.models.triggers import TriggerModel

router = APIRouter()        # behind the API key
hooks_router = APIRouter()  # public: the unguessable token in the URL is the credential

MIN_INTERVAL_SECONDS = 10
MAX_HOOK_BODY = 256 * 1024


class TriggerCreate(BaseModel):
    kind: Literal["schedule", "webhook"]
    interval_seconds: int | None = None
    cron: str | None = None  # 5 fields, UTC
    context: dict | None = None  # input passed to scheduled runs
    enabled: bool = True


class TriggerUpdate(BaseModel):
    enabled: bool


def _serialize(t: TriggerModel) -> dict:
    return {
        "id": t.id, "workflow_id": t.workflow_id, "kind": t.kind, "enabled": t.enabled,
        "config": t.config or {},
        "webhook_path": f"/api/hooks/{t.token}" if t.token else None,
        "next_run_at": t.next_run_at.isoformat() if t.next_run_at else None,
        "last_run_at": t.last_run_at.isoformat() if t.last_run_at else None,
    }


@router.post("/workflows/{workflow_id}/triggers")
def create_trigger(workflow_id: str, req: TriggerCreate, db: Session = Depends(get_db)):
    if not db.query(WorkflowModel.id).filter(WorkflowModel.id == workflow_id).first():
        raise HTTPException(status_code=404, detail="Workflow not found")

    t = TriggerModel(workflow_id=workflow_id, kind=req.kind, enabled=req.enabled, config={})
    if req.kind == "webhook":
        t.token = secrets.token_urlsafe(24)
    else:
        if bool(req.cron) == bool(req.interval_seconds):
            raise HTTPException(status_code=422, detail="Give exactly one of interval_seconds or cron")
        if req.interval_seconds is not None and req.interval_seconds < MIN_INTERVAL_SECONDS:
            raise HTTPException(status_code=422, detail=f"interval_seconds must be >= {MIN_INTERVAL_SECONDS}")
        t.config = {"cron": req.cron} if req.cron else {"interval_seconds": req.interval_seconds}
        if req.context:
            t.config["context"] = req.context
        try:
            t.next_run_at = next_fire(t.config, datetime.utcnow())
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    db.add(t)
    db.commit()
    return _serialize(t)


@router.get("/workflows/{workflow_id}/triggers")
def list_triggers(workflow_id: str, db: Session = Depends(get_db)):
    rows = db.query(TriggerModel).filter(TriggerModel.workflow_id == workflow_id).order_by(TriggerModel.created_at).all()
    return [_serialize(t) for t in rows]


@router.patch("/triggers/{trigger_id}")
def update_trigger(trigger_id: str, req: TriggerUpdate, db: Session = Depends(get_db)):
    t = db.query(TriggerModel).filter(TriggerModel.id == trigger_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trigger not found")
    t.enabled = req.enabled
    if t.kind == "schedule" and req.enabled:
        t.next_run_at = next_fire(t.config or {}, datetime.utcnow())  # no catch-up burst after being paused
    db.commit()
    return _serialize(t)


@router.delete("/triggers/{trigger_id}")
def delete_trigger(trigger_id: str, db: Session = Depends(get_db)):
    t = db.query(TriggerModel).filter(TriggerModel.id == trigger_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trigger not found")
    db.delete(t)
    db.commit()
    return {"deleted": trigger_id}


@hooks_router.post("/hooks/{token}", status_code=202)
async def fire_webhook(token: str, request: Request, db: Session = Depends(get_db)):
    """Start the workflow bound to this webhook. The JSON body becomes the run's input context."""
    t = db.query(TriggerModel).filter(
        TriggerModel.token == token, TriggerModel.kind == "webhook", TriggerModel.enabled.is_(True)
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="Unknown webhook")

    raw = await request.body()
    if len(raw) > MAX_HOOK_BODY:
        raise HTTPException(status_code=413, detail="Payload too large")
    try:
        body = await request.json() if raw else {}
    except ValueError:
        raise HTTPException(status_code=400, detail="Body must be JSON")
    context = body if isinstance(body, dict) else {"payload": body}

    try:
        run_id = enqueue_run(db, t.workflow_id, context, "webhook", trigger_id=t.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Workflow no longer exists")
    except WorkflowInvalid as e:
        raise HTTPException(status_code=400, detail=str(e))
    t.last_run_at = datetime.utcnow()
    db.commit()
    get_worker(db.get_bind()).kick()
    return {"run_id": run_id, "status": "pending"}
