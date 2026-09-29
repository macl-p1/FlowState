"""Approval / HITL service tests."""

import pytest

from app.approval.service import (
    ApprovalService, ApprovalAlreadyResolvedError, ApprovalNotFoundError
)
from app.schemas.execution import ExecutionStatus


@pytest.fixture
def approval_service(db_session):
    return ApprovalService(db_session)


class TestApprovalCreation:
    def test_create_pending_approval(self, approval_service):
        approval = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Amount exceeds threshold",
            context={"amount": 500000},
        )
        assert approval.id is not None
        assert approval.status == "pending"
        assert approval.reason == "Amount exceeds threshold"
        assert approval.context["amount"] == 500000

    def test_create_with_approver_role(self, approval_service):
        approval = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Needs sign-off",
            approver_role="manager",
        )
        assert approval.approver_role == "manager"


class TestApprovalResolution:
    def test_approve_sets_fields(self, approval_service):
        approval = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Test",
        )
        resolved = approval_service.approve(approval.id, approver_id="user_123")

        assert resolved.status == "approved"
        assert resolved.approver_id == "user_123"
        assert resolved.approved_at is not None
        assert resolved.resolved_at is not None

    def test_reject_sets_fields(self, approval_service):
        approval = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Test",
        )
        resolved = approval_service.reject(
            approval.id,
            approver_id="user_456",
            reason="Budget not available",
        )
        assert resolved.status == "rejected"
        assert resolved.approver_id == "user_456"
        assert resolved.rejection_reason == "Budget not available"

    def test_approve_twice_raises(self, approval_service):
        approval = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Test",
        )
        approval_service.approve(approval.id, approver_id="user_1")

        with pytest.raises(ApprovalAlreadyResolvedError) as exc:
            approval_service.approve(approval.id, approver_id="user_2")
        assert "already resolved" in str(exc.value).lower()

    def test_reject_twice_raises(self, approval_service):
        approval = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Test",
        )
        approval_service.reject(approval.id, approver_id="user_1", reason="No")

        with pytest.raises(ApprovalAlreadyResolvedError):
            approval_service.reject(approval.id, approver_id="user_2", reason="Also no")


class TestApprovalQueries:
    def test_list_pending_returns_only_pending(self, approval_service, db_session):
        from app.models import ApprovalRequestModel

        # Create mix of pending and resolved
        a1 = approval_service.create_request("e1", "n1", "Pending 1")
        a2 = approval_service.create_request("e2", "n2", "Pending 2")
        a3 = approval_service.create_request("e3", "n3", "To be approved")
        a4 = approval_service.create_request("e4", "n4", "To be rejected")

        # Resolve a3 and a4
        approval_service.approve(a3.id, approver_id="u1")
        approval_service.reject(a4.id, approver_id="u2", reason="Nope")

        pending = approval_service.list_pending()
        assert len(pending) == 2
        pending_ids = {a.id for a in pending}
        assert a1.id in pending_ids
        assert a2.id in pending_ids

    def test_get_existing_approval(self, approval_service):
        created = approval_service.create_request(
            workflow_execution_id="exec_001",
            node_id="n3",
            reason="Test",
        )
        fetched = approval_service.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.reason == "Test"

    def test_get_nonexistent_returns_none(self, approval_service):
        result = approval_service.get("nonexistent_id")
        assert result is None


class TestApprovalPersistence:
    def test_approval_survives_session_close(self, db_engine):
        """Create approval, close session, reopen, verify data persists."""
        from app.models import ApprovalRequestModel

        # Session 1: create and commit
        Session1 = sessionmaker(bind=db_engine)
        s1 = Session1()
        approval = ApprovalRequestModel(
            id=f"approval_{uuid.uuid4().hex[:8]}",
            execution_id="exec_001",
            node_id="n3",
            reason="Persistence test",
            context={"amount": 75000},
            status="pending",
        )
        s1.add(approval)
        s1.commit()
        approval_id = approval.id
        s1.close()

        # Session 2: read back
        Session2 = sessionmaker(bind=db_engine)
        s2 = Session2()
        try:
            service = ApprovalService(s2)
            recovered = service.get(approval_id)
            assert recovered is not None
            assert recovered.reason == "Persistence test"
            assert recovered.context["amount"] == 75000
        finally:
            s2.close()


# Fix import
import uuid
from sqlalchemy.orm import sessionmaker


# Fix import
import uuid
