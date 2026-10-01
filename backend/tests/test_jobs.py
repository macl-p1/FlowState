"""Triggers, durable queue, worker (concurrency/timeout/cancel), replay and restart recovery."""

import time
from datetime import datetime, timedelta

import pytest

from tests.test_api import client, setup_test_db, test_engine, TestingSessionLocal  # noqa: F401
from app.config import settings
from app.engine.jobs import Worker, cron_next, enqueue_run, recover_interrupted, WorkflowInvalid
from app.models import (
    WorkflowModel, WorkflowExecutionModel, StepExecutionModel, RunEvaluationModel, RunCorrectionModel,
)
from app.models.triggers import TriggerModel, RunMetaModel
from app.schemas.execution import ExecutionStatus

QUICK = {
    "nodes": [
        {"id": "a", "type": "trigger", "name": "Go", "trigger": {"type": "manual"}},
        {"id": "b", "type": "end", "name": "Done", "outcome": "ok"},
    ],
    "edges": [{"from": "a", "to": "b"}],
}


def slow(seconds: int) -> dict:
    return {
        "nodes": [
            {"id": "a", "type": "trigger", "name": "Go", "trigger": {"type": "manual"}},
            {"id": "w", "type": "action", "name": "Wait", "tool": "delay", "inputs": {"seconds": seconds}},
            {"id": "b", "type": "end", "name": "Done", "outcome": "ok"},
        ],
        "edges": [{"from": "a", "to": "w"}, {"from": "w", "to": "b"}],
    }


def _cleanup():
    db = TestingSessionLocal()
    for m in (RunCorrectionModel, RunEvaluationModel, RunMetaModel, TriggerModel,
              StepExecutionModel, WorkflowExecutionModel, WorkflowModel):
        db.query(m).delete()
    db.commit()
    db.close()


@pytest.fixture
def db():
    s = TestingSessionLocal()
    yield s
    s.close()
    _cleanup()


def _wf(db, graph, wid="jwf"):
    db.add(WorkflowModel(id=wid, name=wid, description="", nodes=graph["nodes"], edges=graph["edges"]))
    db.commit()
    return wid


def _status(eid):
    s = TestingSessionLocal()
    try:
        s.expire_all()
        return s.get(WorkflowExecutionModel, eid)
    finally:
        s.close()


# ── cron ──

def test_cron_next():
    assert cron_next("*/15 * * * *", datetime(2026, 1, 1, 10, 7)) == datetime(2026, 1, 1, 10, 15)
    assert cron_next("0 9 * * 1", datetime(2026, 1, 1)) == datetime(2026, 1, 5, 9, 0)     # next Monday 09:00
    assert cron_next("0 0 13 * 5", datetime(2026, 1, 1)) == datetime(2026, 1, 2, 0, 0)    # dom OR dow: Friday the 2nd
    assert cron_next("0 0 * * 7", datetime(2026, 1, 1)) == datetime(2026, 1, 4, 0, 0)     # 7 == Sunday
    for bad in ("* * * *", "61 * * * *", "a b c d e"):
        with pytest.raises(ValueError):
            cron_next(bad, datetime(2026, 1, 1))


# ── queue + worker ──

@pytest.mark.asyncio
async def test_queued_run_executes_with_provenance(db):
    wid = _wf(db, QUICK)
    eid = enqueue_run(db, wid, {"order": 7}, "webhook", trigger_id="trg_x")
    assert _status(eid).status == ExecutionStatus.PENDING          # durable row exists before any worker runs

    w = Worker(test_engine)
    await w.tick()
    await w.drain()
    run = _status(eid)
    assert run.status == ExecutionStatus.COMPLETED
    meta = db.get(RunMetaModel, eid)
    assert (meta.source, meta.trigger_id, meta.input_context) == ("webhook", "trg_x", {"order": 7})


def test_enqueue_rejects_unrunnable_workflow(db):
    wid = _wf(db, {"nodes": QUICK["nodes"], "edges": [{"from": "a", "to": "ghost"}]})
    with pytest.raises(WorkflowInvalid):
        enqueue_run(db, wid)
    with pytest.raises(LookupError):
        enqueue_run(db, "missing")


@pytest.mark.asyncio
async def test_concurrency_cap_and_cancel(db, monkeypatch):
    monkeypatch.setattr(settings, "max_concurrent_runs", 1)
    wid = _wf(db, slow(5))
    first, second = enqueue_run(db, wid), enqueue_run(db, wid)

    w = Worker(test_engine)
    await w.tick()
    assert list(w.active) == [first]                                  # only one slot, FIFO
    assert _status(second).status == ExecutionStatus.PENDING

    t0 = time.time()
    assert w.cancel(first)
    await w.drain()
    assert _status(first).status == ExecutionStatus.CANCELLED
    assert time.time() - t0 < 2                                       # cancelled, not waited out (delay is 5s)

    await w.tick()                                                    # slot freed -> next queued run starts
    assert list(w.active) == [second]
    w.cancel(second)
    await w.drain()


@pytest.mark.asyncio
async def test_run_timeout(db, monkeypatch):
    monkeypatch.setattr(settings, "run_timeout_seconds", 0.5)
    eid = enqueue_run(db, _wf(db, slow(3)))
    w = Worker(test_engine)
    await w.tick()
    await w.drain()
    run = _status(eid)
    assert run.status == ExecutionStatus.FAILED and "Timed out" in run.error_message


@pytest.mark.asyncio
async def test_cancel_while_queued_is_never_started(db):
    eid = enqueue_run(db, _wf(db, QUICK))
    run = db.get(WorkflowExecutionModel, eid)
    run.status = ExecutionStatus.CANCELLED
    db.commit()
    w = Worker(test_engine)
    await w.tick()
    assert not w.active


@pytest.mark.asyncio
async def test_schedule_trigger_fires_once_then_waits(db):
    wid = _wf(db, QUICK)
    db.add(TriggerModel(id="trg_s", workflow_id=wid, kind="schedule", config={"interval_seconds": 3600, "context": {"k": 1}},
                        next_run_at=datetime.utcnow() - timedelta(minutes=5)))
    db.commit()
    w = Worker(test_engine)
    await w.tick()
    await w.drain()
    await w.tick()                                                    # not due again for an hour
    await w.drain()

    db.expire_all()
    metas = db.query(RunMetaModel).filter_by(trigger_id="trg_s").all()
    assert len(metas) == 1 and metas[0].source == "schedule" and metas[0].input_context == {"k": 1}
    t = db.get(TriggerModel, "trg_s")
    assert t.last_run_at and t.next_run_at > datetime.utcnow() + timedelta(minutes=50)
    assert _status(metas[0].execution_id).status == ExecutionStatus.COMPLETED


def test_recover_interrupted_fails_midflight_but_keeps_queue(db):
    wid = _wf(db, QUICK)
    db.add(WorkflowExecutionModel(id="exec_mid", workflow_id=wid, workflow_name=wid, status=ExecutionStatus.RUNNING))
    db.add(WorkflowExecutionModel(id="exec_wait", workflow_id=wid, workflow_name=wid, status=ExecutionStatus.WAITING_APPROVAL))
    db.commit()
    queued = enqueue_run(db, wid)

    assert recover_interrupted(test_engine) == 1
    assert _status("exec_mid").status == ExecutionStatus.FAILED
    assert "restart" in _status("exec_mid").error_message
    assert _status("exec_wait").status == ExecutionStatus.WAITING_APPROVAL
    assert _status(queued).status == ExecutionStatus.PENDING          # queued work survives the restart


# ── API: webhook, triggers, replay ──



def _wait_done(client, run_id, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        r = client.get(f"/api/runs/{run_id}").json()
        if r["status"] in ("completed", "failed", "cancelled"):
            return r
        time.sleep(0.1)
    raise AssertionError(f"run {run_id} did not finish")


def _create_wf(client, graph, name="apiwf"):
    return client.post("/api/workflows", json={"name": name, "description": "", **graph}).json()["id"]


def test_webhook_trigger_end_to_end(client):
    try:
        wid = _create_wf(client, QUICK)
        t = client.post(f"/api/workflows/{wid}/triggers", json={"kind": "webhook"}).json()
        path = t["webhook_path"]
        assert path.startswith("/api/hooks/") and len(path) > 30        # unguessable

        r = client.post(path, json={"invoice": 42})
        assert r.status_code == 202
        run_id = r.json()["run_id"]
        run = _wait_done(client, run_id)
        assert run["status"] == "completed" and run["source"] == "webhook"
        db = TestingSessionLocal()
        assert db.get(RunMetaModel, run_id).input_context == {"invoice": 42}
        db.close()

        assert client.post("/api/hooks/not-a-token", json={}).status_code == 404
        assert client.post(path, content="{bad json", headers={"content-type": "application/json"}).status_code == 400

        client.patch(f"/api/triggers/{t['id']}", json={"enabled": False})
        assert client.post(path, json={}).status_code == 404            # disabled
        assert client.delete(f"/api/triggers/{t['id']}").status_code == 200
    finally:
        time.sleep(0.2)
        _cleanup()


def test_trigger_validation(client):
    try:
        wid = _create_wf(client, QUICK)
        url = f"/api/workflows/{wid}/triggers"
        assert client.post(url, json={"kind": "schedule"}).status_code == 422                                  # nothing given
        assert client.post(url, json={"kind": "schedule", "interval_seconds": 5}).status_code == 422          # too frequent
        assert client.post(url, json={"kind": "schedule", "cron": "bad"}).status_code == 422
        assert client.post(url, json={"kind": "schedule", "cron": "* * * * *", "interval_seconds": 60}).status_code == 422
        ok = client.post(url, json={"kind": "schedule", "cron": "*/5 * * * *"})
        assert ok.status_code == 200 and ok.json()["next_run_at"]
        assert client.post("/api/workflows/nope/triggers", json={"kind": "webhook"}).status_code == 404
        assert len(client.get(url).json()) == 1
    finally:
        _cleanup()


def test_replay_uses_original_definition_unless_latest(client):
    try:
        wid = _create_wf(client, QUICK)
        first = client.post(f"/api/workflows/{wid}/run/start", json={"context": {"n": 1}}).json()["id"]
        assert len(_wait_done(client, first)["steps"]) == 2

        # edit the workflow afterwards: one more step in the middle
        longer = {"nodes": QUICK["nodes"][:1] + [{"id": "m", "type": "action", "name": "Mid", "tool": "delay", "inputs": {"seconds": 0}}]
                  + QUICK["nodes"][1:], "edges": [{"from": "a", "to": "m"}, {"from": "m", "to": "b"}]}
        client.post("/api/workflows", json={"name": "apiwf", "description": "", **longer, "workflow_id": wid})

        same = client.post(f"/api/runs/{first}/replay", json={}).json()
        latest = client.post(f"/api/runs/{first}/replay", json={"latest": True}).json()
        assert same["replay_of"] == first

        r_same, r_latest = _wait_done(client, same["id"]), _wait_done(client, latest["id"])
        assert len(r_same["steps"]) == 2 and r_same["source"] == "replay" and r_same["replay_of"] == first
        assert len(r_latest["steps"]) == 3
        db = TestingSessionLocal()
        assert db.get(RunMetaModel, same["id"]).input_context == {"n": 1}  # same input
        db.close()

        assert client.post("/api/runs/nope/replay", json={}).status_code == 404
    finally:
        time.sleep(0.2)
        _cleanup()
