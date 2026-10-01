"""Suggestions API routes — cross-pollination and pattern suggestions."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.models import WorkflowModel
from app.genealogy.cross_pollination import get_suggestions, apply_patch_to_workflow
from app.schemas.suggestions import ApplyPatchRequest


router = APIRouter()


@router.get("/workflows/{workflow_id}/suggestions")
async def list_suggestions(
    workflow_id: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
):
    """Get cross-pollination suggestions for a workflow."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    suggestions = get_suggestions(db, workflow_id, top_k=top_k)
    return {
        "workflow_id": workflow_id,
        "suggestions": suggestions,
    }


@router.post("/workflows/{workflow_id}/suggestions/apply")
async def apply_suggestion(
    workflow_id: str,
    request: ApplyPatchRequest,
    db: Session = Depends(get_db),
):
    """Apply a suggestion's patch to a workflow."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    patch = request.patch
    if not patch or not isinstance(patch, dict):
        raise HTTPException(status_code=400, detail="Invalid patch format")

    patch_type = patch.get("type")
    valid_types = {"update_node", "insert_between", "insert_between_with_branch", "append_node"}
    if patch_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid patch type: {patch_type}")

    try:
        new_nodes, new_edges = apply_patch_to_workflow(
            workflow.nodes or [],
            workflow.edges or [],
            patch,
        )
        workflow.nodes = new_nodes
        workflow.edges = new_edges
        db.commit()
        db.refresh(workflow)

        return {
            "id": workflow.id,
            "name": workflow.name,
            "nodes": workflow.nodes,
            "edges": workflow.edges,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to apply patch: {e}")
