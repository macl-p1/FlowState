"""Tests for the genealogy engine — version tracking, diff, branching, lineage."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import WorkflowModel, WorkflowVersionModel, WorkflowBranchModel
from app.genealogy.diff import compute_diff, DiffResult
from app.genealogy.service import GenealogyService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def _make_workflow(db, name="Test Workflow"):
    wf = WorkflowModel(id=f"wf_{name[:8].lower()}", name=name, nodes=[], edges=[])
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


# ---------------------------------------------------------------------------
# Diff engine tests
# ---------------------------------------------------------------------------

class TestComputeDiff:

    def test_added_nodes(self):
        old_nodes = [{"id": "a", "type": "trigger", "name": "Start"}]
        new_nodes = old_nodes + [{"id": "b", "type": "action", "name": "Email", "tool": "email"}]
        diff = compute_diff(old_nodes, [], new_nodes, [])
        assert len(diff.added_nodes) == 1
        assert diff.added_nodes[0]["id"] == "b"
        assert len(diff.removed_nodes) == 0
        assert len(diff.modified_nodes) == 0
        assert diff.has_changes

    def test_removed_nodes(self):
        old_nodes = [{"id": "a"}, {"id": "b"}]
        new_nodes = [{"id": "a"}]
        diff = compute_diff(old_nodes, [], new_nodes, [])
        assert len(diff.removed_nodes) == 1
        assert diff.removed_nodes[0]["id"] == "b"

    def test_modified_nodes(self):
        old_nodes = [{"id": "a", "type": "action", "tool": "email", "inputs": {"to": "x"}}]
        new_nodes = [{"id": "a", "type": "action", "tool": "email", "inputs": {"to": "y"}}]
        diff = compute_diff(old_nodes, [], new_nodes, [])
        assert len(diff.modified_nodes) == 1
        assert diff.modified_nodes[0]["id"] == "a"
        assert "inputs" in diff.modified_nodes[0]["changes"]

    def test_no_changes(self):
        nodes = [{"id": "a", "type": "trigger"}]
        diff = compute_diff(nodes, [], nodes, [])
        assert not diff.has_changes
        assert diff.summary() == "no changes"

    def test_added_edges(self):
        old_nodes = [{"id": "a"}, {"id": "b"}]
        new_nodes = old_nodes[:]
        diff = compute_diff(old_nodes, [], new_nodes, [{"from": "a", "to": "b"}])
        assert len(diff.added_edges) == 1

    def test_summary_contains_changes(self):
        old_nodes = [{"id": "a", "type": "trigger", "name": "Start"}]
        new_nodes = old_nodes + [{"id": "b", "type": "action", "name": "Email", "tool": "email"}]
        diff = compute_diff(old_nodes, [], new_nodes, [])
        s = diff.summary()
        assert "added" in s
        assert "Email" in s

    def test_to_dict_serializable(self):
        nodes = [{"id": "a"}, {"id": "b"}]
        diff = compute_diff(nodes, [], nodes + [{"id": "c"}], [])
        d = diff.to_dict()
        assert "added_nodes" in d
        assert "removed_nodes" in d
        assert "modified_nodes" in d


# ---------------------------------------------------------------------------
# Service layer tests
# ---------------------------------------------------------------------------

class TestGenealogyService:

    def test_save_initial_version(self, db):
        wf = _make_workflow(db)
        svc = GenealogyService(db)

        v = svc.save_version(wf.id, wf.nodes, wf.edges, rationale="initial")

        assert v.version_number == 1
        assert v.change_summary == "initial version"
        assert v.change_rationale == "initial"
        assert v.parent_version_id is None

    def test_save_subsequent_version_computes_diff(self, db):
        wf = _make_workflow(db)
        svc = GenealogyService(db)

        v1 = svc.save_version(wf.id, [{"id": "a", "type": "trigger"}], [], rationale="v1")
        v2 = svc.save_version(
            wf.id,
            [{"id": "a", "type": "trigger"}, {"id": "b", "type": "action"}],
            [],
            rationale="added action",
        )

        assert v2.version_number == 2
        assert v2.parent_version_id == v1.id
        assert v2.change_summary is not None
        assert "added" in v2.change_summary
        assert v2.diff_details is not None

    def test_get_history(self, db):
        wf = _make_workflow(db)
        svc = GenealogyService(db)
        svc.save_version(wf.id, [{"id": "a"}], [], rationale="v1")
        svc.save_version(wf.id, [{"id": "a"}, {"id": "b"}], [], rationale="v2")

        history = svc.get_history(wf.id)
        assert len(history) == 2
        assert history[0]["version_number"] == 2  # newest first

    def test_get_version(self, db):
        wf = _make_workflow(db)
        svc = GenealogyService(db)
        v = svc.save_version(wf.id, [{"id": "a"}], [], rationale="test")

        found = svc.get_version(v.id)
        assert found is not None
        assert found["change_rationale"] == "test"
        assert found["nodes"] == [{"id": "a"}]

    def test_branch_workflow(self, db):
        wf = _make_workflow(db, name="Original")
        svc = GenealogyService(db)
        svc.save_version(wf.id, [{"id": "a", "type": "trigger"}], [], rationale="initial")

        new_wf, new_ver, branch = svc.branch_workflow(
            wf.id, "Branched", [{"id": "a"}], [], rationale="experiment"
        )

        assert new_wf.id != wf.id
        assert new_wf.name == "Branched"
        assert new_ver.version_number == 1
        assert branch.source_workflow_id == wf.id
        assert branch.branched_workflow_id == new_wf.id

    def test_get_lineage(self, db):
        wf = _make_workflow(db)
        svc = GenealogyService(db)
        svc.save_version(wf.id, [{"id": "a"}], [], rationale="v1")
        svc.save_version(wf.id, [{"id": "a"}, {"id": "b"}], [], rationale="v2")
        svc.branch_workflow(wf.id, "Branch1", [{"id": "a"}], [], rationale="experiment")

        lineage = svc.get_lineage(wf.id)
        assert lineage["workflow_id"] == wf.id
        assert lineage["current_version"] == 2
        assert len(lineage["versions"]) == 2
        assert len(lineage["branches"]) == 1
        assert lineage["branches"][0]["branch_name"] is None or lineage["branches"][0]["target_name"] == "Branch1"
