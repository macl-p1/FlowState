"""Analytics stats endpoint."""

from datetime import datetime, timedelta

from tests.test_api import client, setup_test_db, TestingSessionLocal, WorkflowModel, WorkflowExecutionModel
from app.models import StepExecutionModel
from app.schemas.execution import ExecutionStatus, StepStatus


def test_stats(client):
    db = TestingSessionLocal()
    db.add(WorkflowModel(id="w", name="w", nodes=[], edges=[]))
    for i, st in enumerate([ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]):
        db.add(WorkflowExecutionModel(id=f"e{i}", workflow_id="w", workflow_name="w", status=st))
        t = datetime(2026, 1, 1)
        db.add(StepExecutionModel(
            execution_id=f"e{i}", node_id="n", node_type="action", node_name="n", tool_name="analytics_probe",
            status=StepStatus.FAILED if i else StepStatus.COMPLETED,
            started_at=t, completed_at=t + timedelta(seconds=2)))
    db.commit(); db.close()

    r = client.get("/api/analytics/stats")
    db = TestingSessionLocal()
    db.query(StepExecutionModel).delete(); db.query(WorkflowExecutionModel).delete(); db.query(WorkflowModel).delete()
    db.commit(); db.close()
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["total_runs"] >= 2 and d["by_status"]["failed"] >= 1
    assert {"tool": "analytics_probe", "steps": 2, "failure_rate": 0.5, "avg_seconds": 2.0} in d["tools"]
