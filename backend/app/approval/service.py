"""Human Approval Service — pause/resume workflow execution."""

import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session

from app.models import ApprovalRequestModel
from app.schemas.execution import ExecutionStatus
from app.schemas.workflow import PermissionLevel


class ApprovalAlreadyResolvedError(Exception):
    """Raised when trying to resolve an already-resolved approval."""

    def __init__(self, approval_id: str, current_status: str):
        self.approval_id = approval_id
        self.current_status = current_status
        super().__init__(
            f"Approval {approval_id} is already resolved (status: {current_status})"
        )


class ApprovalNotFoundError(Exception):
    """Raised when an approval request is not found."""

    def __init__(self, approval_id: str):
        super().__init__(f"Approval request not found: {approval_id}")


class ApprovalService:
    """Manages human-in-the-loop approval requests."""

    def __init__(self, db: Session):
        self.db = db

    def create_request(
        self,
        workflow_execution_id: str,
        node_id: str,
        reason: str,
        context: dict[str, Any] | None = None,
        approver_role: str | None = None,
        requested_by: str = "system",
    ) -> ApprovalRequestModel:
        """Create a new approval request."""
        approval = ApprovalRequestModel(
            id=f"approval_{uuid.uuid4().hex[:8]}",
            execution_id=workflow_execution_id,
            node_id=node_id,
            reason=reason,
            context=context or {},
            approver_role=approver_role,
            status="pending",
        )
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def get(self, approval_id: str) -> ApprovalRequestModel | None:
        """Get an approval request by ID."""
        return self.db.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.id == approval_id
        ).first()

    def list_pending(self) -> list[ApprovalRequestModel]:
        """List all pending approval requests."""
        return self.db.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.status == "pending"
        ).order_by(ApprovalRequestModel.created_at.desc()).all()

    def approve(
        self,
        approval_id: str,
        approver_id: str,
    ) -> ApprovalRequestModel:
        """Approve an approval request."""
        approval = self.get(approval_id)
        if not approval:
            raise ApprovalNotFoundError(approval_id)
        if approval.status != "pending":
            raise ApprovalAlreadyResolvedError(approval_id, approval.status)

        approval.status = "approved"
        approval.approver_id = approver_id
        approval.approved_at = datetime.utcnow()
        approval.resolved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(approval)
        self.db.expire_all()
        return approval

    def reject(
        self,
        approval_id: str,
        approver_id: str,
        reason: str | None = None,
    ) -> ApprovalRequestModel:
        """Reject an approval request."""
        approval = self.get(approval_id)
        if not approval:
            raise ApprovalNotFoundError(approval_id)
        if approval.status != "pending":
            raise ApprovalAlreadyResolvedError(approval_id, approval.status)

        approval.status = "rejected"
        approval.approver_id = approver_id
        approval.rejection_reason = reason
        approval.resolved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(approval)
        return approval
