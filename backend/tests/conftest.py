"""Shared pytest fixtures for all tests."""

import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.tools.registry import ToolRegistry, registry as default_registry
from app.models import WorkflowModel, WorkflowExecutionModel, StepExecutionModel
from app.schemas.workflow import Workflow, NodeType, PermissionLevel
from app.schemas.execution import ExecutionStatus, StepStatus
from app.schemas.tool import ToolResult
from app.agents.planner import PlannerAgent
from app.agents.compiler import WorkflowCompiler
from app.engine.runner import WorkflowRunner
from app.approval.service import ApprovalService
from examples import INVOICE_PROCESSING, EMPLOYEE_ONBOARDING, CUSTOMER_SUPPORT


# ---- Database fixtures ----

@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLite in-memory database engine for the test session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create a fresh database session for each test, wrapping in a transaction
    that is rolled back at the end so committed data from one test never leaks
    into the next."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---- Tool registry fixture ----

@pytest.fixture
def tool_registry():
    """Fresh tool registry with all default tools."""
    return ToolRegistry()


@pytest.fixture
def registry_with_context(monkeypatch):
    """Registry with seeded mock data."""
    return default_registry


# ---- Workflow fixtures ----

@pytest.fixture
def sample_invoice_workflow():
    """Invoice processing workflow for reuse."""
    return Workflow.model_validate(INVOICE_PROCESSING)


@pytest.fixture
def sample_onboarding_workflow():
    """Employee onboarding workflow for reuse."""
    return Workflow.model_validate(EMPLOYEE_ONBOARDING)


@pytest.fixture
def sample_complaint_workflow():
    """Customer complaint workflow for reuse."""
    return Workflow.model_validate(CUSTOMER_SUPPORT)


@pytest.fixture
def persisted_invoice_workflow(db_session, sample_invoice_workflow):
    """Invoice workflow persisted in the database."""
    wf_model = WorkflowModel(
        id=f"wf_{uuid.uuid4().hex[:8]}",
        name=sample_invoice_workflow.name,
        description=sample_invoice_workflow.description,
        nodes=sample_invoice_workflow.nodes,
        edges=sample_invoice_workflow.edges,
        metadata={},
    )
    db_session.add(wf_model)
    db_session.commit()
    db_session.refresh(wf_model)
    return wf_model


@pytest.fixture
def persisted_onboarding_workflow(db_session, sample_onboarding_workflow):
    """Onboarding workflow persisted in the database."""
    wf_model = WorkflowModel(
        id=f"wf_{uuid.uuid4().hex[:8]}",
        name=sample_onboarding_workflow.name,
        description=sample_onboarding_workflow.description,
        nodes=sample_onboarding_workflow.nodes,
        edges=sample_onboarding_workflow.edges,
        metadata={},
    )
    db_session.add(wf_model)
    db_session.commit()
    db_session.refresh(wf_model)
    return wf_model


# ---- Runner fixture ----

@pytest.fixture
def runner(db_session, tool_registry):
    """WorkflowRunner with database and tool registry."""
    return WorkflowRunner(db=db_session, tool_registry=tool_registry)


# ---- Mock data helpers ----

def create_pending_approval(db_session, execution_id: str = None, node_id: str = "n3") -> any:
    """Create a pending approval request in the database."""
    from app.models import ApprovalRequestModel
    approval = ApprovalRequestModel(
        id=f"approval_{uuid.uuid4().hex[:8]}",
        execution_id=execution_id or f"exec_{uuid.uuid4().hex[:8]}",
        node_id=node_id,
        reason="Test approval required",
        context={"amount": 500000},
        approver_role="manager",
        status="pending",
    )
    db_session.add(approval)
    db_session.commit()
    db_session.refresh(approval)
    return approval


def create_execution_at_approval(db_session, workflow_model, tool_registry) -> tuple:
    """Helper: create a workflow execution that's paused at the approval node."""
    from app.schemas.workflow import Workflow
    workflow = Workflow.model_validate({
        "name": workflow_model.name,
        "description": workflow_model.description,
        "nodes": workflow_model.nodes,
        "edges": workflow_model.edges,
    })

    # Find approval node index
    approval_idx = None
    for i, node in enumerate(workflow.nodes):
        if node.get("type") == "approval":
            approval_idx = i
            break

    if approval_idx is None:
        raise ValueError("Workflow has no approval node")

    # Create execution and steps up to approval node
    exec_model = WorkflowExecutionModel(
        id=f"exec_{uuid.uuid4().hex[:8]}",
        workflow_id=workflow_model.id,
        workflow_name=workflow_model.name,
        status=ExecutionStatus.WAITING_APPROVAL,
        current_node_id=workflow.nodes[approval_idx]["id"],
        context={"amount": 500000},
        started_at=None,
    )
    db_session.add(exec_model)

    # Create step records for nodes before approval
    for i in range(approval_idx):
        node = workflow.nodes[i]
        step = StepExecutionModel(
            id=f"step_{uuid.uuid4().hex[:8]}",
            execution_id=exec_model.id,
            node_id=node["id"],
            node_type=node["type"],
            node_name=node.get("name", node["id"]),
            status=StepStatus.COMPLETED,
            tool_name=node.get("tool"),
            tool_inputs=node.get("inputs", {}),
            tool_result={"success": True, "output": {}},
            attempt_count=1,
            started_at=None,
            completed_at=None,
        )
        db_session.add(step)

    db_session.commit()
    db_session.refresh(exec_model)
    return workflow_model, exec_model


# ---- Workflow prompts for tests ----

INVOICE_PROMPT = (
    "When an invoice arrives, extract the details, match it against the purchase order, "
    "compare the amounts, and request approval from the manager if the amount exceeds "
    "$100,000. If approved, process the payment."
)

ONBOARDING_PROMPT = (
    "When a new employee joins, collect their documents, verify them, notify HR, "
    "and if anything is missing, send a reminder to the employee."
)

COMPLAINT_PROMPT = (
    "When a customer complaint arrives, identify the customer, find their order, "
    "check delivery status, determine the issue, generate a response, and send it."
)
