"""Genealogy API routes — version history, branching, and lineage."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkflowModel
from app.genealogy.service import GenealogyService
from app.genealogy.evolve import evolve


router = APIRouter()


class SaveVersionRequest(BaseModel):
    rationale: str | None = None
    nodes: list[dict] | None = None
    edges: list[dict] | None = None


class BranchWorkflowRequest(BaseModel):
    name: str
    rationale: str | None = None
    nodes: list[dict] | None = None
    edges: list[dict] | None = None
    branch_name: str | None = None


@router.post("/workflows/{workflow_id}/versions")
async def save_version(
    workflow_id: str,
    request: SaveVersionRequest,
    db: Session = Depends(get_db),
):
    """Save a new version of a workflow with a change rationale."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    service = GenealogyService(db)

    # Use provided nodes/edges or fall back to current workflow state
    nodes = request.nodes if request.nodes is not None else workflow.nodes
    edges = request.edges if request.edges is not None else workflow.edges

    version = service.save_version(
        workflow_id=workflow_id,
        nodes=nodes,
        edges=edges,
        rationale=request.rationale,
    )

    return {
        "version_id": version.id,
        "workflow_id": version.workflow_id,
        "version_number": version.version_number,
        "change_summary": version.change_summary,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }


@router.post("/workflows/{workflow_id}/branch")
async def branch_workflow(
    workflow_id: str,
    request: BranchWorkflowRequest,
    db: Session = Depends(get_db),
):
    """Create a new workflow branched from an existing one."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    service = GenealogyService(db)

    # Use provided nodes/edges or fall back to current workflow state
    nodes = request.nodes if request.nodes is not None else workflow.nodes
    edges = request.edges if request.edges is not None else workflow.edges

    new_workflow, version, branch = service.branch_workflow(
        source_workflow_id=workflow_id,
        new_name=request.name,
        new_nodes=nodes,
        new_edges=edges,
        rationale=request.rationale,
        branch_name=request.branch_name,
    )

    return {
        "new_workflow_id": new_workflow.id,
        "new_workflow_name": new_workflow.name,
        "branch_id": branch.id,
        "version_id": version.id,
        "version_number": version.version_number,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }


@router.get("/workflows/{workflow_id}/history")
async def get_history(workflow_id: str, db: Session = Depends(get_db)):
    """Get version history for a workflow."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    service = GenealogyService(db)
    versions = service.get_history(workflow_id)
    return {"workflow_id": workflow_id, "versions": versions}


@router.get("/workflows/{workflow_id}/versions/{version_id}")
async def get_version(workflow_id: str, version_id: str, db: Session = Depends(get_db)):
    """Get a specific version's full graph."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    service = GenealogyService(db)
    version = service.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.get("/workflows/{workflow_id}/lineage")
async def get_lineage(workflow_id: str, db: Session = Depends(get_db)):
    """Get the full family tree for a workflow."""
    workflow = db.query(WorkflowModel).filter(
        WorkflowModel.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    service = GenealogyService(db)
    return service.get_lineage(workflow_id)


class EvolveRequest(BaseModel):
    trials: int = 3
    generations: int = 1
    allow_gate_removal: bool = False  # removing approval gates is opt-in
    apply: bool = False


@router.post("/workflows/{workflow_id}/evolve")
async def evolve_workflow(
    workflow_id: str,
    request: EvolveRequest,
    db: Session = Depends(get_db),
):
    """Test mutated variants in a sandbox; with apply=true, save the winner as a new version."""
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    result = await evolve(
        db, workflow, max(1, min(request.trials, 20)),
        generations=max(1, min(request.generations, 5)),
        allow_gate_removal=request.allow_gate_removal,
    )
    winner = result["winner"]
    result["applied_version_id"] = None
    if request.apply and winner:
        workflow.nodes, workflow.edges = winner["nodes"], winner["edges"]
        version = GenealogyService(db).save_version(
            workflow_id, winner["nodes"], winner["edges"],
            rationale=f"Evolved: {winner['description']} "
                      f"(sandbox success {result['baseline']:.0%} -> {winner['fitness']:.0%})",
        )
        db.commit()
        result["applied_version_id"] = version.id
    return result
