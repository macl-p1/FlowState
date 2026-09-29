"""API endpoint tests."""

import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import WorkflowModel, WorkflowExecutionModel
from app.schemas.workflow import Workflow
from app.schemas.execution import ExecutionStatus, StepStatus, StepExecution
from app.schemas.tool import ToolResult
from examples import INVOICE_PROCESSING


# ---- Test client setup ----

TEST_DB_URL = "sqlite:///:memory:"

# StaticPool ensures all connections share the same in-memory SQLite database
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables once for all API tests."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Test client with overridden database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    """Client with mocked authentication if needed."""
    return client


# ---- Health endpoint ----

class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "orchestr-ai"


# ---- Workflow endpoints ----

class TestWorkflowAPI:
    def test_generate_workflow_requires_prompt(self, client):
        response = client.post("/api/workflows/generate", json={})
        assert response.status_code == 422  # Validation error

    def test_list_workflows_empty(self, client):
        response = client.get("/api/workflows")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_workflow_not_found(self, client):
        response = client.get("/api/workflows/nonexistent")
        assert response.status_code == 404

    def test_run_workflow_not_found(self, client):
        response = client.post("/api/workflows/nonexistent/run", json={})
        assert response.status_code == 404


# ---- Run endpoints ----

class TestRunAPI:
    def test_get_run_not_found(self, client):
        response = client.get("/api/runs/nonexistent")
        assert response.status_code == 404

    def test_cancel_run_not_found(self, client):
        response = client.post("/api/runs/nonexistent/cancel")
        assert response.status_code == 404

    def test_list_runs_empty(self, client):
        response = client.get("/api/runs")
        assert response.status_code == 200
        assert response.json() == []


# ---- Approval endpoints ----

class TestApprovalAPI:
    def test_list_approvals_empty(self, client):
        response = client.get("/api/approvals")
        assert response.status_code == 200
        assert response.json() == []

    def test_approve_nonexistent(self, client):
        response = client.post("/api/approvals/nonexistent/approve", json={"approver_id": "u1"})
        assert response.status_code == 400

    def test_reject_nonexistent(self, client):
        response = client.post("/api/approvals/nonexistent/reject", json={
            "approver_id": "u1",
            "reason": "No",
        })
        assert response.status_code == 400


# ---- Tool endpoints ----

class TestToolAPI:
    def test_list_tools(self, client):
        response = client.get("/api/tools")
        assert response.status_code == 200
        tools = response.json()
        assert len(tools) > 0
        names = {t["name"] for t in tools}
        assert "send_email" in names

    def test_get_specific_tool(self, client):
        response = client.get("/api/tools/send_email")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "send_email"
        assert "description" in data

    def test_get_nonexistent_tool(self, client):
        response = client.get("/api/tools/nonexistent_tool")
        assert response.status_code == 404
