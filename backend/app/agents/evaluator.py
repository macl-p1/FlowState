"""Silent-success detection: judge whether a COMPLETED run produced the right result."""

import json
import threading
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    WorkflowExecutionModel, WorkflowModel, StepExecutionModel, RunEvaluationModel, RunCorrectionModel,
)
from app.schemas.execution import ExecutionStatus, StepStatus

_VERDICTS = ((0.8, "ok"), (0.5, "suspect"), (0.0, "bad"))


def _verdict(score: float) -> str:
    return next(v for floor, v in _VERDICTS if score >= floor)


def _keys(step: StepExecutionModel) -> frozenset:
    out = (step.tool_result or {}).get("output")
    return frozenset(out) if isinstance(out, dict) else frozenset()


def _previous_runs(db: Session, execution: WorkflowExecutionModel, n: int = 3):
    return (
        db.query(WorkflowExecutionModel)
        .filter(
            WorkflowExecutionModel.workflow_id == execution.workflow_id,
            WorkflowExecutionModel.id != execution.id,
            WorkflowExecutionModel.status == ExecutionStatus.COMPLETED,
        )
        .order_by(WorkflowExecutionModel.started_at.desc())
        .limit(n)
        .all()
    )


def learned_corrections(db: Session, workflow_id: str) -> dict[str, list[str]]:
    """What humans flagged on this workflow before: the reasons we gave (and their notes)."""
    rows = (
        db.query(RunCorrectionModel, RunEvaluationModel)
        .outerjoin(RunEvaluationModel, RunEvaluationModel.execution_id == RunCorrectionModel.execution_id)
        .filter(RunCorrectionModel.workflow_id == workflow_id)
        .all()
    )
    return {
        "reasons": [r for _, ev in rows if ev for r in ev.reasons or []],
        "notes": [c.note for c, _ in rows if c.note],
    }


def heuristic_evaluate(db: Session, execution: WorkflowExecutionModel) -> dict[str, Any]:
    """Offline checks: empty output, tool warnings, output shape drift, identical repeat output.

    A finding humans previously flagged as wrong on this workflow counts for more.
    """
    reasons: list[str] = []
    prev_by_node: dict[str, list[StepExecutionModel]] = {}
    for run in _previous_runs(db, execution):
        for s in run.steps:
            prev_by_node.setdefault(s.node_id, []).append(s)

    for s in execution.steps:
        if s.status != StepStatus.COMPLETED or not s.tool_name:
            continue
        result = s.tool_result or {}
        if not result.get("output"):
            reasons.append(f"'{s.node_name}' reported success but returned no output")
        if result.get("warnings"):
            reasons.append(f"'{s.node_name}' succeeded with warnings: {'; '.join(result['warnings'])}")
        history = prev_by_node.get(s.node_id, [])
        if history and _keys(s) and _keys(history[0]) and _keys(s) != _keys(history[0]):
            changed = sorted(_keys(s) ^ _keys(history[0]))
            reasons.append(f"'{s.node_name}' output shape changed vs. last run (fields: {', '.join(changed)})")
        if history and s.tool_result and all(s.tool_result == h.tool_result for h in history):
            reasons.append(f"'{s.node_name}' produced identical output to its last {len(history)} run(s)")

    flagged = set(learned_corrections(db, execution.workflow_id)["reasons"])
    score = max(0.0, 1.0 - sum(0.4 if r in flagged else 0.25 for r in reasons))
    return {"score": score, "verdict": _verdict(score), "reasons": reasons, "source": "heuristic"}


def llm_evaluate(
    workflow: WorkflowModel, execution: WorkflowExecutionModel, heuristic: dict, learned: dict | None = None
) -> dict | None:
    """One Claude call judging output vs. the workflow's intent. None when no key or on any failure."""
    if not settings.anthropic_api_key:
        return None
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=settings.anthropic_api_key, base_url=settings.anthropic_base_url or None)
        steps = [
            {"step": s.node_name, "tool": s.tool_name, "inputs": s.tool_inputs, "result": s.tool_result}
            for s in execution.steps if s.tool_name
        ]
        prompt = (
            "You audit automation runs that technically succeeded. Judge whether the OUTPUT matches the workflow's "
            "intent (wrong content, duplicates, suspicious values, schema changes), not whether it errored.\n"
            f"Workflow: {workflow.name}\nIntent: {workflow.description}\n"
            f"Offline checks already found: {heuristic['reasons']}\n"
            "Problems the user previously flagged on this workflow (weigh similar issues heavily): "
            f"{json.dumps((learned or {}).get('reasons', [])[-10:] + (learned or {}).get('notes', [])[-10:])}\n"
            f"Steps: {json.dumps(steps, default=str)[:6000]}\n"
            'Reply with JSON only: {"score": 0.0-1.0, "reasons": ["short problem statements"]}. '
            "Empty reasons if the run looks right."
        )
        resp = client.messages.create(
            model=settings.anthropic_model, max_tokens=400, temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads("".join(b.text for b in resp.content if hasattr(b, "text")))
        score = min(1.0, max(0.0, float(data["score"])))
        return {"score": score, "verdict": _verdict(score), "reasons": list(data.get("reasons", [])), "source": "llm"}
    except Exception:
        return None


def _refine_with_llm(bind, execution_id: str, heuristic: dict) -> None:
    """Background: replace the heuristic evaluation with Claude's judgement when it succeeds."""
    try:
        with Session(bind) as db:
            execution = db.query(WorkflowExecutionModel).filter_by(id=execution_id).first()
            workflow = db.query(WorkflowModel).filter_by(id=execution.workflow_id).first()
            result = llm_evaluate(workflow, execution, heuristic, learned_corrections(db, execution.workflow_id))
            if result:
                row = db.query(RunEvaluationModel).filter_by(execution_id=execution_id).first()
                for k, v in result.items():
                    setattr(row, k, v)
                db.commit()
    except Exception:
        pass


def evaluate_run(db: Session, execution_id: str) -> RunEvaluationModel | None:
    """Evaluate and persist (once) a completed run. Never raises.

    Offline checks run inline; the Claude judgement (if a key is set) refines the row in a background thread.
    """
    try:
        execution = db.query(WorkflowExecutionModel).filter_by(id=execution_id).first()
        if not execution or execution.status != ExecutionStatus.COMPLETED:
            return None
        existing = db.query(RunEvaluationModel).filter_by(execution_id=execution_id).first()
        if existing:
            return existing
        result = heuristic_evaluate(db, execution)
        row = RunEvaluationModel(execution_id=execution_id, workflow_id=execution.workflow_id, **result)
        db.add(row)
        db.commit()
        if settings.anthropic_api_key:
            threading.Thread(
                target=_refine_with_llm, args=(db.get_bind(), execution_id, result), daemon=True
            ).start()
        return row
    except Exception:
        db.rollback()
        return None
