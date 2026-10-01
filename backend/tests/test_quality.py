"""Silent-success detection: heuristics, correction tracking, override-rate insight."""

from datetime import datetime, timedelta

from tests.test_api import client, setup_test_db, TestingSessionLocal  # noqa: F401
from app.agents.evaluator import evaluate_run
from app.models import (
    WorkflowModel, WorkflowExecutionModel, StepExecutionModel,
    RunEvaluationModel, RunCorrectionModel,
)
from app.schemas.execution import ExecutionStatus, StepStatus


def _seed(db, wf="qwf", n=0, output=None, warnings=None):
    """Add a COMPLETED run with one http step. Returns the execution id."""
    if not db.query(WorkflowModel).filter_by(id=wf).first():
        db.add(WorkflowModel(id=wf, name=wf, description="sync customers", nodes=[], edges=[]))
    eid = f"{wf}_run{n}"
    db.add(WorkflowExecutionModel(id=eid, workflow_id=wf, workflow_name=wf, status=ExecutionStatus.COMPLETED,
                                  started_at=datetime(2026, 1, 1) + timedelta(minutes=n)))
    db.add(StepExecutionModel(
        execution_id=eid, node_id="n1", node_type="action", node_name="fetch", tool_name="http",
        status=StepStatus.COMPLETED,
        tool_result={"success": True, "output": output, "warnings": warnings or []},
    ))
    db.commit()
    return eid


def _cleanup(db):
    for m in (RunCorrectionModel, RunEvaluationModel, StepExecutionModel, WorkflowExecutionModel, WorkflowModel):
        db.query(m).delete()
    db.commit()
    db.close()


def test_heuristics_flag_empty_drift_and_warnings():
    db = TestingSessionLocal()
    try:
        _seed(db, n=0, output={"id": 1, "email": "a"})
        # same workflow, later run: output shape drifted and a warning appeared
        eid = _seed(db, n=1, output={"id": 1, "mail": "a"}, warnings=["deprecated field"])
        ev = evaluate_run(db, eid)
        text = " ".join(ev.reasons)
        assert "shape changed" in text and "warnings" in text
        assert ev.verdict in ("suspect", "bad") and ev.source == "heuristic"

        empty = evaluate_run(db, _seed(db, n=2, output={}))
        assert any("no output" in r for r in empty.reasons)

        # fail-soft: unknown run does not raise
        assert evaluate_run(db, "nope") is None
    finally:
        _cleanup(db)


def test_clean_run_is_ok():
    db = TestingSessionLocal()
    try:
        ev = evaluate_run(db, _seed(db, output={"id": 1}))
        assert ev.verdict == "ok" and ev.reasons == []
    finally:
        _cleanup(db)


def test_override_rate_insight_and_reject_correction(client):
    db = TestingSessionLocal()
    try:
        ids = [_seed(db, n=i, output={"id": i}) for i in range(6)]
        for i in ids[:2]:  # 2 of 6 flagged -> 33%
            r = client.post(f"/api/runs/{i}/correction", json={"kind": "wrong_result", "note": "bad data"})
            assert r.status_code == 200
        q = client.get("/api/workflows/qwf/quality").json()
        assert q["runs"] == 6 and q["corrected"] == 2 and q["override_rate"] == 0.3333
        assert "2 of 6" in q["insight"]

        assert client.post("/api/runs/missing/correction", json={}).status_code == 404

        # below the minimum run count there is no insight
        db.query(RunCorrectionModel).delete(); db.commit()
        client.post(f"/api/runs/{ids[0]}/correction", json={})
        for i in ids[1:]:
            db.query(StepExecutionModel).filter_by(execution_id=i).delete()
            db.query(WorkflowExecutionModel).filter_by(id=i).delete()
        db.commit()
        assert client.get("/api/workflows/qwf/quality").json()["insight"] is None

        # GET /runs/{id} exists and carries quality
        evaluate_run(db, ids[0])
        run = client.get(f"/api/runs/{ids[0]}").json()
        assert run["quality"]["verdict"] == "ok"
    finally:
        _cleanup(db)


def test_flagged_issue_weighs_more_next_time():
    db = TestingSessionLocal()
    try:
        _seed(db, n=0, output={})                       # run 0: empty output, will be flagged
        ev0 = evaluate_run(db, "qwf_run0")
        db.add(RunCorrectionModel(execution_id="qwf_run0", workflow_id="qwf", kind="wrong_result"))
        db.commit()
        ev1 = evaluate_run(db, _seed(db, n=1, output={}))  # same issue again
        # empty output costs 0.25 first time, 0.4 once humans flagged it; run 1 also repeats run 0 exactly (0.25)
        assert ev0.score == 0.75 and abs(ev1.score - 0.35) < 1e-9
    finally:
        _cleanup(db)


def test_delete_run_and_analytics_workflows(client):
    db = TestingSessionLocal()
    try:
        a, b = _seed(db, n=0, output={"id": 1}), _seed(db, n=1, output={"id": 2})
        evaluate_run(db, a)
        client.post(f"/api/runs/{a}/correction", json={})
        wfs = {w["id"]: w for w in client.get("/api/analytics/stats").json()["workflows"]}
        assert wfs["qwf"]["corrected"] == 1 and wfs["qwf"]["runs"] == 2

        assert client.delete(f"/api/runs/{a}").status_code == 200
        assert client.delete(f"/api/runs/{a}").status_code == 404
        assert client.get(f"/api/runs/{b}").status_code == 200
        assert db.query(RunCorrectionModel).filter_by(execution_id=a).count() == 0
    finally:
        _cleanup(db)
