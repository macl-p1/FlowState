"""Genealogy service — workflow version tracking, branching, and lineage."""

from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session

from app.models import WorkflowModel, WorkflowVersionModel, WorkflowBranchModel
from app.models.genealogy import WorkflowBranchModel as BranchModel
from app.genealogy.diff import compute_diff, graph_key


class GenealogyService:
    """Manages workflow version history and lineage tree."""

    def __init__(self, db: Session):
        self.db = db

    def save_version(
        self,
        workflow_id: str,
        nodes: list[dict],
        edges: list[dict],
        rationale: str | None = None,
    ) -> WorkflowVersionModel:
        """
        Save a new version of a workflow.

        Computes diff from the previous version and stores a change summary.
        If this is the first save, creates version 1 with no diff.
        """
        workflow = self.db.query(WorkflowModel).filter(
            WorkflowModel.id == workflow_id
        ).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Determine version number and parent
        existing_versions = (
            self.db.query(WorkflowVersionModel)
            .filter(WorkflowVersionModel.workflow_id == workflow_id)
            .order_by(WorkflowVersionModel.version_number.desc())
            .all()
        )

        # Nothing changed (layout aside): keep the latest version instead of adding a "no changes" one.
        if existing_versions and graph_key(existing_versions[0].nodes, existing_versions[0].edges) == graph_key(nodes, edges):
            latest = existing_versions[0]
            if rationale and not latest.change_rationale:
                latest.change_rationale = rationale
                self.db.commit()
            return latest

        version_number = (existing_versions[0].version_number + 1) if existing_versions else 1
        parent_version_id = existing_versions[0].id if existing_versions else None

        # Compute diff from previous version
        diff_details = None
        change_summary = "initial version"
        if parent_version_id:
            parent = existing_versions[0]
            diff = compute_diff(parent.nodes, parent.edges, nodes, edges)
            diff_details = diff.to_dict()
            change_summary = diff.summary()

        version = WorkflowVersionModel(
            workflow_id=workflow_id,
            parent_version_id=parent_version_id,
            version_number=version_number,
            nodes=nodes,
            edges=edges,
            change_rationale=rationale,
            change_summary=change_summary,
            diff_details=diff_details,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def ensure_baseline(self, workflow_id: str) -> None:
        """Before the first tracked change, snapshot the current state so history keeps the 'before'."""
        has_version = self.db.query(WorkflowVersionModel.id).filter(
            WorkflowVersionModel.workflow_id == workflow_id
        ).first()
        if has_version:
            return
        workflow = self.db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
        if workflow:
            self.save_version(workflow_id, workflow.nodes or [], workflow.edges or [],
                              rationale="Baseline (state before first tracked change)")

    def restore_version(self, workflow_id: str, version_id: str, rationale: str | None = None) -> WorkflowVersionModel:
        """Make an old version current again, recorded as a new version (history is never rewritten)."""
        old = self.db.query(WorkflowVersionModel).filter(
            WorkflowVersionModel.id == version_id, WorkflowVersionModel.workflow_id == workflow_id
        ).first()
        if not old:
            raise ValueError(f"Version {version_id} not found for workflow {workflow_id}")
        workflow = self.db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
        workflow.nodes, workflow.edges = old.nodes, old.edges
        self.db.commit()
        note = f"Restored v{old.version_number}" + (f": {rationale}" if rationale else "")
        return self.save_version(workflow_id, old.nodes, old.edges, rationale=note)

    def branch_workflow(
        self,
        source_workflow_id: str,
        new_name: str,
        new_nodes: list[dict],
        new_edges: list[dict],
        rationale: str | None = None,
        branch_name: str | None = None,
    ) -> tuple[WorkflowModel, WorkflowVersionModel, WorkflowBranchModel]:
        """
        Create a new workflow branched from an existing one.

        The new workflow gets its own ID but carries a lineage link back to the source.
        An initial version is saved for the new workflow.
        """
        import uuid

        source = self.db.query(WorkflowModel).filter(
            WorkflowModel.id == source_workflow_id
        ).first()
        if not source:
            raise ValueError(f"Source workflow {source_workflow_id} not found")

        # Get the latest version of the source workflow to link as branch point
        source_version = (
            self.db.query(WorkflowVersionModel)
            .filter(WorkflowVersionModel.workflow_id == source_workflow_id)
            .order_by(WorkflowVersionModel.version_number.desc())
            .first()
        )

        # Create new workflow
        new_workflow = WorkflowModel(
            id=f"wf_{uuid.uuid4().hex[:8]}",
            name=new_name,
            description=source.description,
            nodes=new_nodes,
            edges=new_edges,
            wf_metadata={
                "source": "builder",
                "branched_from": source_workflow_id,
            },
        )
        self.db.add(new_workflow)

        # Create initial version for the new workflow
        version = WorkflowVersionModel(
            workflow_id=new_workflow.id,
            version_number=1,
            nodes=new_nodes,
            edges=new_edges,
            change_rationale=f"Branched from '{source.name}'. {rationale or ''}".strip(),
            change_summary="branched from parent workflow",
        )

        # Create branch record
        branch = WorkflowBranchModel(
            source_workflow_id=source_workflow_id,
            source_version_id=source_version.id if source_version else None,
            branched_workflow_id=new_workflow.id,
            branch_name=branch_name,
            rationale=rationale,
        )

        self.db.add(new_workflow)
        self.db.add(version)
        self.db.add(branch)
        self.db.commit()
        self.db.refresh(new_workflow)
        self.db.refresh(version)
        self.db.refresh(branch)

        return new_workflow, version, branch

    def get_history(self, workflow_id: str) -> list[dict]:
        """Return ordered list of all versions for a workflow."""
        versions = (
            self.db.query(WorkflowVersionModel)
            .filter(WorkflowVersionModel.workflow_id == workflow_id)
            .order_by(WorkflowVersionModel.version_number.desc())
            .all()
        )
        return [_version_to_dict(v) for v in versions]

    def get_version(self, version_id: str) -> dict | None:
        """Get a specific version by ID."""
        version = self.db.query(WorkflowVersionModel).filter(
            WorkflowVersionModel.id == version_id
        ).first()
        return _version_to_dict(version) if version else None

    def get_lineage(self, workflow_id: str) -> dict:
        """
        Build a family tree for a workflow.

        Returns:
        {
            "workflow_id": "...",
            "workflow_name": "...",
            "current_version": N,
            "versions": [...],
            "branches": [
                {"branch_id": "...", "target_workflow_id": "...", "target_name": "...", "at_version": N, "created_at": "..."}
            ],
            "ancestry": [list of ancestor workflows via branch links]
        }
        """
        workflow = self.db.query(WorkflowModel).filter(
            WorkflowModel.id == workflow_id
        ).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Versions
        versions = (
            self.db.query(WorkflowVersionModel)
            .filter(WorkflowVersionModel.workflow_id == workflow_id)
            .order_by(WorkflowVersionModel.version_number.asc())
            .all()
        )

        # Branches that originated from this workflow
        outgoing_branches = (
            self.db.query(WorkflowBranchModel)
            .filter(WorkflowBranchModel.source_workflow_id == workflow_id)
            .all()
        )

        # Branches that point TO this workflow (it was branched from another)
        incoming_branch = (
            self.db.query(WorkflowBranchModel)
            .filter(WorkflowBranchModel.branched_workflow_id == workflow_id)
            .first()
        )

        # Ancestry chain
        ancestry = []
        current = incoming_branch
        while current:
            source_wf = self.db.query(WorkflowModel).filter(
                WorkflowModel.id == current.source_workflow_id
            ).first()
            if source_wf:
                ancestry.append({
                    "workflow_id": source_wf.id,
                    "workflow_name": source_wf.name,
                    "branched_at_version": current.source_version_id,
                    "branch_rationale": current.rationale,
                    "created_at": current.created_at.isoformat() if current.created_at else None,
                })
            # Check if source was itself branched (go further up)
            parent_branch = (
                self.db.query(WorkflowBranchModel)
                .filter(WorkflowBranchModel.branched_workflow_id == current.source_workflow_id)
                .first()
            )
            current = parent_branch

        return {
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "current_version": versions[-1].version_number if versions else 0,
            "versions": [_version_to_dict(v) for v in versions],
            "branches": [
                {
                    "branch_id": b.id,
                    "target_workflow_id": b.branched_workflow_id,
                    "target_name": self.db.query(WorkflowModel).filter(
                        WorkflowModel.id == b.branched_workflow_id
                    ).first().name if self.db.query(WorkflowModel).filter(
                        WorkflowModel.id == b.branched_workflow_id
                    ).first() else "unknown",
                    "branch_name": b.branch_name,
                    "rationale": b.rationale,
                    "at_version": b.source_version_id,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                }
                for b in outgoing_branches
            ],
            "ancestry": ancestry,
        }


def _version_to_dict(version: WorkflowVersionModel) -> dict:
    """Convert a version ORM model to a response dict."""
    return {
        "id": version.id,
        "workflow_id": version.workflow_id,
        "parent_version_id": version.parent_version_id,
        "version_number": version.version_number,
        "nodes": version.nodes,
        "edges": version.edges,
        "change_rationale": version.change_rationale,
        "change_summary": version.change_summary,
        "diff_details": version.diff_details,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }
