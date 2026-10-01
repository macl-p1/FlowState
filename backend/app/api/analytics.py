"""Analytics: execution metrics aggregated per workflow and per tool."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkflowExecutionModel as E, StepExecutionModel as S
from app.schemas.execution import ExecutionStatus, StepStatus

router = APIRouter()


def _rate(failed: int, total: int) -> float:
    return round(failed / total, 4) if total else 0.0


@router.get("/analytics/stats")
def stats(db: Session = Depends(get_db)):
    runs = db.query(E.status, func.count()).group_by(E.status).all()
    by_status = {s.value: n for s, n in runs}
    total = sum(by_status.values())

    agg = {}  # tool -> [steps, failed, total_seconds, timed_steps]
    rows = db.query(S.tool_name, S.status, S.started_at, S.completed_at).filter(S.tool_name.isnot(None))
    # ponytail: row scan in Python for DB portability; move to SQL aggregates if step volume gets large
    for tool, status, t0, t1 in rows:
        a = agg.setdefault(tool, [0, 0, 0.0, 0])
        a[0] += 1
        a[1] += status == StepStatus.FAILED
        if t0 and t1:
            a[2] += (t1 - t0).total_seconds()
            a[3] += 1
    return {
        "total_runs": total,
        "by_status": by_status,
        "failure_rate": _rate(by_status.get(ExecutionStatus.FAILED.value, 0), total),
        "tools": [
            {"tool": t, "steps": n, "failure_rate": _rate(f, n),
             "avg_seconds": round(sec / k, 3) if k else None}
            for t, (n, f, sec, k) in agg.items()
        ],
    }
