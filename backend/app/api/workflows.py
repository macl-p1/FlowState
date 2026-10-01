"""Workflow API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any

from app.database import get_db
from app.models import WorkflowModel
from app.schemas.workflow import Workflow
from app.schemas.execution import WorkflowExecution
from app.agents.planner import PlannerAgent, PlanningResult
from app.engine.runner import WorkflowRunner
from app.tools.registry import registry
from app.genealogy.service import GenealogyService


router = APIRouter()


class SaveWorkflowRequest(BaseModel):
    name: str
    description: str = ""
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    workflow_id: str | None = None  # If provided, update existing workflow


class GenerateRequest(BaseModel):
    prompt: str
    preview: bool = False


class RunRequest(BaseModel):
    context: dict | None = None


@router.post("/workflows/generate")
async def generate_workflow(request: GenerateRequest, db: Session = Depends(get_db)):
    """Generate a workflow from natural language.

    When preview=True, returns the generated nodes without persisting to the database.
    """
    planner = PlannerAgent(tool_registry=registry)
    result: PlanningResult = await planner.plan(request.prompt)

    if not result.success:
        detail = result.error or "Planning failed"
        if result.raw_response:
            detail += f" | Raw response: {result.raw_response[:500]}"
        raise HTTPException(status_code=422, detail=detail)

    workflow = result.workflow
    metadata = planner.get_planning_metadata(workflow)

    response_nodes = [n.model_dump() if hasattr(n, 'model_dump') else n for n in workflow.nodes]
    response_edges = [e.model_dump() if hasattr(e, 'model_dump') else e for e in workflow.edges]

    if request.preview:
        return {
            "preview": True,
            "name": workflow.name,
            "description": workflow.description,
            "nodes": response_nodes,
            "edges": response_edges,
            "metadata": metadata,
        }

    wf_model = WorkflowModel(
        id=f"wf_{uuid.uuid4().hex[:8]}",
        name=workflow.name,
        description=workflow.description,
        nodes=response_nodes,
        edges=response_edges,
        metadata=metadata,
    )
    db.add(wf_model)
    db.commit()
    db.refresh(wf_model)

    return {
        "id": wf_model.id,
        "name": wf_model.name,
        "description": wf_model.description,
        "nodes": wf_model.nodes,
        "edges": wf_model.edges,
        "metadata": metadata,
    }


@router.post("/workflows")
async def save_workflow_direct(request: SaveWorkflowRequest, db: Session = Depends(get_db)):
    """Save a workflow graph directly (no LLM re-generation).

    If workflow_id is provided, update the existing workflow and create a new version.
    Otherwise, create a new workflow.
    """
    import re

    if request.workflow_id:
        # Update existing workflow
        wf_model = db.query(WorkflowModel).filter(WorkflowModel.id == request.workflow_id).first()
        if not wf_model:
            raise HTTPException(status_code=404, detail="Workflow not found")

        wf_model.name = request.name
        wf_model.description = request.description
        wf_model.nodes = request.nodes
        wf_model.edges = request.edges
        db.commit()
        db.refresh(wf_model)
    else:
        # Create new workflow
        slug = re.sub(r'[^a-z0-9]', '_', request.name.lower())[:20]
        wf_id = f"wf_{slug}_{uuid.uuid4().hex[:6]}"

        wf_model = WorkflowModel(
            id=wf_id,
            name=request.name,
            description=request.description,
            nodes=request.nodes,
            edges=request.edges,
            metadata={"source": "builder"},
        )
        db.add(wf_model)
        db.commit()
        db.refresh(wf_model)

    # Save version with diff from previous version
    try:
        genealogy = GenealogyService(db)
        rationale = "Updated workflow" if request.workflow_id else "Initial version"
        genealogy.save_version(wf_model.id, wf_model.nodes, wf_model.edges, rationale=rationale)
    except Exception:
        pass  # Non-critical — don't fail the save if genealogy fails

    return {
        "id": wf_model.id,
        "name": wf_model.name,
        "description": wf_model.description,
        "nodes": wf_model.nodes,
        "edges": wf_model.edges,
        "metadata": wf_model.wf_metadata,
    }


@router.get("/workflows")
async def list_workflows(db: Session = Depends(get_db)):
    """List all workflows."""
    workflows = db.query(WorkflowModel).order_by(WorkflowModel.created_at.desc()).all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "created_at": w.created_at.isoformat(),
            "metadata": w.wf_metadata,
        }
        for w in workflows
    ]


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Get a specific workflow."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "nodes": wf.nodes,
        "edges": wf.edges,
        "metadata": wf.metadata,
        "created_at": wf.created_at.isoformat(),
    }


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Delete a workflow."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"deleted": workflow_id}


@router.post("/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: str, request: RunRequest, db: Session = Depends(get_db)):
    """Execute a workflow."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    runner = WorkflowRunner(db=db, tool_registry=registry)
    execution = await runner.run(workflow_id, context=request.context)

    return {
        "id": execution.id,
        "workflow_id": execution.workflow_id,
        "status": execution.status.value,
        "current_node_id": execution.current_node_id,
        "steps": [
            {
                "id": s.id,
                "node_id": s.node_id,
                "node_name": s.node_name,
                "node_type": s.node_type,
                "status": s.status.value,
                "tool_name": s.tool_name,
                "attempt_count": s.attempt_count,
                "error": s.error,
            }
            for s in execution.steps
        ],
    }
