"""Quality API: run evaluations, human corrections, per-workflow override insight."""

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkflowExecutionModel, RunEvaluationModel, RunCorrectionModel
from app.schemas.execution import ExecutionStatus

router = APIRouter()

MIN_RUNS, MIN_RATE = 5, 0.2  # ponytail: fixed thresholds; make per-workflow if noisy


class CorrectionRequest(BaseModel):
    kind: str = "wrong_result"  # overridden | wrong_result
    note: str | None = None
    created_by: str | None = None


def serialize_evaluation(e: RunEvaluationModel | None) -> dict | None:
    if not e:
        return None
    return {"score": e.score, "verdict": e.verdict, "reasons": e.reasons or [], "source": e.source}


def record_correction(db: Session, execution_id: str, kind: str, note: str | None = None,
                      created_by: str | None = None) -> RunCorrectionModel:
    ex = db.query(WorkflowExecutionModel).filter_by(id=execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Run not found")
    row = RunCorrectionModel(execution_id=execution_id, workflow_id=ex.workflow_id,
                             kind=kind, note=note, created_by=created_by)
    db.add(row)
    db.commit()
    return row


def workflow_quality(db: Session, workflow_id: str) -> dict:
    runs = db.query(WorkflowExecutionModel).filter(
        WorkflowExecutionModel.workflow_id == workflow_id,
        WorkflowExecutionModel.status == ExecutionStatus.COMPLETED,
    ).count()
    corrected = {c.execution_id for c in db.query(RunCorrectionModel).filter_by(workflow_id=workflow_id)}
    evals = db.query(RunEvaluationModel).filter_by(workflow_id=workflow_id).all()
    rate = len(corrected) / runs if runs else 0.0
    top = [r for r, _ in Counter(
        r for e in evals if e.execution_id in corrected for r in e.reasons or []
    ).most_common(3)]
    insight = None
    if runs >= MIN_RUNS and rate >= MIN_RATE:
        insight = (f"Succeeding technically, but you flagged {len(corrected)} of {runs} runs "
                   f"({rate:.0%}) as wrong." + (f" Most common issue: {top[0]}" if top else ""))
    return {
        "runs": runs, "corrected": len(corrected), "override_rate": round(rate, 4),
        "avg_score": round(sum(e.score for e in evals) / len(evals), 3) if evals else None,
        "top_reasons": top, "insight": insight,
    }


@router.post("/runs/{run_id}/correction")
def add_correction(run_id: str, req: CorrectionRequest, db: Session = Depends(get_db)):
    row = record_correction(db, run_id, req.kind, req.note, req.created_by)
    return {"id": row.id, "execution_id": run_id, "kind": row.kind}


@router.get("/runs/{run_id}/evaluation")
def get_evaluation(run_id: str, db: Session = Depends(get_db)):
    return serialize_evaluation(db.query(RunEvaluationModel).filter_by(execution_id=run_id).first())


@router.get("/workflows/{workflow_id}/quality")
def get_quality(workflow_id: str, db: Session = Depends(get_db)):
    return workflow_quality(db, workflow_id)
