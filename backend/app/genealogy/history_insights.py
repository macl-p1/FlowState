"""History-backed suggestions: learn from how workflows actually evolved.

For every workflow we walk its version timeline and record when a pattern (retry, approval gate, ...)
was adopted or dropped, together with the author's rationale. Runs are attributed to the version that
was live when they ran, so each event gets before/after outcome evidence. A run counts as a success
only if it completed AND nobody flagged it as wrong AND the quality check did not judge it "bad".

Suggestions:
- from other workflows: a similar workflow adopted pattern P (and runs improved) -> suggest P here
- from this workflow's own past: it dropped P and runs got worse -> suggest restoring P
"""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.genealogy.cross_pollination import (
    PATTERN_LABELS, _build_suggestion, compute_similarity, extract_patterns,
)
from app.genealogy.diff import graph_key
from app.models import (
    WorkflowModel, WorkflowVersionModel, WorkflowExecutionModel, RunCorrectionModel, RunEvaluationModel,
)
from app.models.triggers import RunMetaModel
from app.schemas.execution import ExecutionStatus

MIN_RUNS = 3        # runs needed on each side of a change before we claim it helped or hurt
MIN_DELTA = 0.10    # success-rate change that counts as a real difference
MIN_SIMILARITY = 0.15


def pattern_timeline(db: Session, workflow_id: str) -> list[dict[str, Any]]:
    versions = (
        db.query(WorkflowVersionModel)
        .filter(WorkflowVersionModel.workflow_id == workflow_id)
        .order_by(WorkflowVersionModel.version_number)
        .all()
    )
    return [
        {
            "version_id": v.id, "number": v.version_number, "created_at": v.created_at,
            "rationale": v.change_rationale, "key": graph_key(v.nodes or [], v.edges or []),
            "info": extract_patterns(v.nodes or [], v.edges or []),
        }
        for v in versions
    ]


def pattern_events(timeline: list[dict]) -> list[dict[str, Any]]:
    """Pattern flips between consecutive versions."""
    events = []
    for prev, cur in zip(timeline, timeline[1:]):
        for p, now in cur["info"]["patterns"].items():
            was = prev["info"]["patterns"].get(p, False)
            if now != was:
                events.append({
                    "pattern": p, "kind": "adopted" if now else "dropped",
                    "index": timeline.index(cur), "version_number": cur["number"],
                    "rationale": cur["rationale"],
                })
    return events


def version_outcomes(db: Session, workflow_id: str, timeline: list[dict]) -> dict[int, list[bool]]:
    """Success/failure of finished runs, keyed by the timeline index of the version they ran on."""
    if not timeline:
        return {}
    runs = (
        db.query(WorkflowExecutionModel)
        .filter(
            WorkflowExecutionModel.workflow_id == workflow_id,
            WorkflowExecutionModel.status.in_((ExecutionStatus.COMPLETED, ExecutionStatus.FAILED)),
        )
        .all()
    )
    ids = [r.id for r in runs]
    corrected = {c.execution_id for c in db.query(RunCorrectionModel.execution_id)
                 .filter(RunCorrectionModel.execution_id.in_(ids))}
    bad = {e.execution_id for e in db.query(RunEvaluationModel.execution_id)
           .filter(RunEvaluationModel.execution_id.in_(ids), RunEvaluationModel.verdict == "bad")}
    snapshots = {m.execution_id: m.snapshot for m in db.query(RunMetaModel)
                 .filter(RunMetaModel.execution_id.in_(ids))}
    by_key = {v["key"]: i for i, v in enumerate(timeline)}

    out: dict[int, list[bool]] = {}
    for r in runs:
        snap = snapshots.get(r.id)
        idx = by_key.get(graph_key(snap["nodes"], snap["edges"])) if snap else None
        if idx is None and r.started_at:  # no snapshot (older runs): the version live at the time
            live = [i for i, v in enumerate(timeline) if v["created_at"] and v["created_at"] <= r.started_at]
            idx = live[-1] if live else None
        if idx is None:
            continue
        ok = r.status == ExecutionStatus.COMPLETED and r.id not in corrected and r.id not in bad
        out.setdefault(idx, []).append(ok)
    return out


def _side(outcomes: dict[int, list[bool]], indexes) -> dict[str, Any]:
    results = [ok for i in indexes for ok in outcomes.get(i, [])]
    return {"runs": len(results), "rate": round(sum(results) / len(results), 3) if results else None}


def event_evidence(event: dict, timeline: list[dict], outcomes: dict[int, list[bool]]) -> dict[str, Any]:
    """Compare runs on versions before the change with runs from the change up to the next flip of that pattern."""
    i = event["index"]
    end = next(
        (j for j in range(i + 1, len(timeline))
         if timeline[j]["info"]["patterns"].get(event["pattern"]) != timeline[i]["info"]["patterns"].get(event["pattern"])),
        len(timeline),
    )
    start = max(
        (j for j in range(i - 1, -1, -1)
         if timeline[j]["info"]["patterns"].get(event["pattern"]) == timeline[i]["info"]["patterns"].get(event["pattern"])),
        default=-1,
    ) + 1
    before, after = _side(outcomes, range(start, i)), _side(outcomes, range(i, end))
    if before["runs"] < MIN_RUNS or after["runs"] < MIN_RUNS:
        verdict = "unknown"
    else:
        delta = after["rate"] - before["rate"]
        verdict = "improved" if delta >= MIN_DELTA else "worse" if delta <= -MIN_DELTA else "neutral"
    return {"before": before, "after": after, "verdict": verdict}


def _evidence_text(e: dict, owner: str, kind: str) -> str:
    v = e["version_number"]
    why = f" ('{e['rationale']}')" if e.get("rationale") else ""
    s = f"{owner} {kind} this in v{v}{why}"
    b, a = e["evidence"]["before"], e["evidence"]["after"]
    if e["evidence"]["verdict"] != "unknown":
        s += f"; success went {b['rate']:.0%} -> {a['rate']:.0%} ({b['runs']} -> {a['runs']} runs)"
    return s


def history_suggestions(db: Session, workflow_id: str) -> list[dict[str, Any]]:
    """Evidence-carrying suggestions mined from version histories (this workflow's and similar ones')."""
    target = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not target:
        return []
    target_info = extract_patterns(target.nodes or [], target.edges or [])
    lacking = {p for p, has in target_info["patterns"].items() if not has}
    out: list[dict[str, Any]] = []

    # 1) Similar workflows that adopted a pattern this one lacks.
    for wf in db.query(WorkflowModel).filter(WorkflowModel.id != workflow_id).all():
        info = extract_patterns(wf.nodes or [], wf.edges or [])
        score = compute_similarity(target_info, info)
        if score < MIN_SIMILARITY:
            continue
        timeline = pattern_timeline(db, wf.id)
        outcomes = version_outcomes(db, wf.id, timeline)
        for e in pattern_events(timeline):
            if e["kind"] != "adopted" or e["pattern"] not in lacking or not info["patterns"].get(e["pattern"]):
                continue  # only patterns we lack and they still use
            e["evidence"] = event_evidence(e, timeline, outcomes)
            if e["evidence"]["verdict"] in ("worse", "neutral"):
                continue  # history says it did not help there
            base = _build_suggestion(e["pattern"], info["pattern_details"])
            if base:
                out.append(_finish(base, workflow_id, wf, score, e, "history",
                                   _evidence_text(e, f"'{wf.name}'", "adopted")))

    # 2) This workflow's own past: patterns it dropped after which results got worse.
    timeline = pattern_timeline(db, workflow_id)
    outcomes = version_outcomes(db, workflow_id, timeline)
    for e in pattern_events(timeline):
        if e["kind"] != "dropped" or e["pattern"] not in lacking:
            continue
        e["evidence"] = event_evidence(e, timeline, outcomes)
        if e["evidence"]["verdict"] != "worse":
            continue  # dropping it was fine (or we can't tell): don't nag
        base = _build_suggestion(e["pattern"], timeline[e["index"] - 1]["info"]["pattern_details"])
        if base:
            base["suggestion"] = f"Restore it: {base['suggestion']}"
            out.append(_finish(base, workflow_id, target, 1.0, e, "self_history",
                               _evidence_text(e, "This workflow", "dropped")))

    # strongest evidence first, one suggestion per pattern
    rank = {"improved": 0, "worse": 0, "unknown": 1}
    out.sort(key=lambda s: (rank.get(s["evidence"]["verdict"], 2), -s["evidence"]["delta"], -s["similarity_score"]))
    seen, unique = set(), []
    for s in out:
        if s["pattern"] not in seen:
            seen.add(s["pattern"])
            unique.append(s)
    return unique


def _finish(base: dict, workflow_id: str, source: WorkflowModel, score: float, e: dict, origin: str, text: str) -> dict:
    import uuid
    b, a = e["evidence"]["before"], e["evidence"]["after"]
    delta = abs(a["rate"] - b["rate"]) if a["rate"] is not None and b["rate"] is not None else 0.0
    return {
        "id": f"sugg_{uuid.uuid4().hex[:8]}",
        "workflow_id": workflow_id,
        "source_workflow_id": source.id,
        "source_workflow_name": source.name,
        "similarity_score": score,
        "pattern": base["pattern"],
        "pattern_label": base.get("pattern_label", PATTERN_LABELS.get(base["pattern"], base["pattern"])),
        "description": base["description"],
        "suggestion": base["suggestion"],
        "target_node_id": base.get("target_node_id"),
        "actionable": True,
        "apply_patch": base.get("apply_patch", {}),
        "origin": origin,
        "evidence": {**e["evidence"], "delta": round(delta, 3), "version_number": e["version_number"],
                     "rationale": e.get("rationale"), "text": text},
    }
