"""Approvals API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.approval.service import ApprovalService
from app.engine.runner import WorkflowRunner
from app.tools.registry import registry


router = APIRouter()


class ApproveRequest(BaseModel):
    approver_id: str


class RejectRequest(BaseModel):
    approver_id: str
    reason: str | None = None


@router.get("/approvals")
async def list_approvals(db: Session = Depends(get_db)):
    """List all pending approvals."""
    service = ApprovalService(db)
    approvals = service.list_pending()
    return [
        {
            "id": a.id,
            "execution_id": a.execution_id,
            "node_id": a.node_id,
            "reason": a.reason,
            "context": a.context,
            "approver_role": a.approver_role,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        }
        for a in approvals
    ]


@router.post("/approvals/{approval_id}/approve")
async def approve_request(approval_id: str, request: ApproveRequest, db: Session = Depends(get_db)):
    """Approve an approval request and resume the workflow."""
    service = ApprovalService(db)
    try:
        approval = service.approve(approval_id, approver_id=request.approver_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Resume the workflow
    runner = WorkflowRunner(db=db, tool_registry=registry)
    try:
        execution = await runner.resume(approval.execution_id)
        return {
            "id": approval.id,
            "status": approval.status,
            "execution": {
                "id": execution.id,
                "status": execution.status.value,
                "steps": [
                    {
                        "node_id": s.node_id,
                        "node_name": s.node_name,
                        "status": s.status.value,
                    }
                    for s in execution.steps
                ],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resume: {e}")


@router.post("/approvals/{approval_id}/reject")
async def reject_request(approval_id: str, request: RejectRequest, db: Session = Depends(get_db)):
    """Reject an approval request and cancel the workflow."""
    service = ApprovalService(db)
    try:
        approval = service.reject(
            approval_id,
            approver_id=request.approver_id,
            reason=request.reason,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Cancel the workflow execution
    runner = WorkflowRunner(db=db, tool_registry=registry)
    try:
        await runner.cancel(approval.execution_id)
    except Exception:
        pass  # Best effort cancel

    return {
        "id": approval.id,
        "status": approval.status,
        "rejection_reason": approval.rejection_reason,
    }
