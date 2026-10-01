"""Real-time execution: node-start hook, non-blocking start, live SSE stream."""

import json
import time

import pytest

from tests.test_api import client, setup_test_db, TestingSessionLocal  # noqa: F401
from app.genealogy.evolve import _sandbox_db, SandboxRegistry
from app.engine.runner import WorkflowRunner
from app.models import WorkflowModel, WorkflowExecutionModel, StepExecutionModel
from examples import INVOICE_PROCESSING

# trigger -> 1s delay -> delay -> end: slow enough to observe while running
SLOW = {
    "name": "slow",
    "nodes": [
        {"id": "a", "type": "trigger", "name": "Go", "trigger": {"type": "manual"}},
        {"id": "b", "type": "action", "name": "Wait 1", "tool": "delay", "inputs": {"seconds": 1}},
        {"id": "c", "type": "action", "name": "Wait 2", "tool": "delay", "inputs": {"seconds": 1}},
        {"id": "d", "type": "end", "name": "Done", "outcome": "ok"},
    ],
    "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}],
}


@pytest.mark.asyncio
async def test_runner_reports_each_node_as_it_starts():
    db = _sandbox_db()
    db.add(WorkflowModel(id="w", name="w", description="", nodes=INVOICE_PROCESSING["nodes"],
                         edges=INVOICE_PROCESSING["edges"]))
    db.commit()
    started, created = [], []
    runner = WorkflowRunner(db, tool_registry=SandboxRegistry(), evaluate=False)
    await runner.run("w", on_created=lambda e: created.append(e.id), on_node_start=started.append)
    assert started[:3] == ["n1", "n2", "n3"]            # nodes announced in execution order
    assert len(created) == 1                             # run id handed out exactly once, before finishing
    run = db.query(WorkflowExecutionModel).filter_by(id=created[0]).one()
    assert run.current_node_id                           # the running node is persisted for stream readers


def _start_slow(client):
    wid = client.post("/api/workflows", json={**SLOW, "description": ""}).json()["id"]
    t0 = time.time()
    r = client.post(f"/api/workflows/{wid}/run/start", json={})
    assert r.status_code == 200, r.text
    return wid, r.json()["id"], time.time() - t0


def _cleanup():
    db = TestingSessionLocal()
    for m in (StepExecutionModel, WorkflowExecutionModel):
        db.query(m).delete()
    db.query(WorkflowModel).delete()
    db.commit()
    db.close()


def test_start_returns_immediately_and_stream_is_live(client):
    try:
        wid, run_id, elapsed = _start_slow(client)
        assert elapsed < 1.5, "start must not wait for the 2s run to finish"

        msgs, named = [], []
        with client.stream("GET", f"/api/runs/{run_id}/stream") as r:
            event = None
            for line in r.iter_lines():
                if line.startswith("event:"):
                    event = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data = json.loads(line.split(":", 1)[1])
                    (named if event else msgs).append((event, data))
                    if event == "done":
                        break
                elif line == "":
                    event = None

        kinds = [m["type"] for _, m in msgs]
        assert "step" in kinds and "status" in kinds             # default messages -> EventSource.onmessage
        assert any(m["type"] == "status" and m["data"]["current_node_id"] in ("b", "c") for _, m in msgs)
        assert named[-1][0] == "done"
        final = [d for e, d in named if e == "snapshot"][-1]
        assert final["status"] == "completed" and len(final["steps"]) == 4
    finally:
        time.sleep(0.1)
        _cleanup()


def test_start_unknown_workflow_404(client):
    assert client.post("/api/workflows/nope/run/start", json={}).status_code == 404
