"""Tests for the cross-pollination engine — similarity, patterns, gaps, patches, suggestions."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import WorkflowModel
from app.genealogy.cross_pollination import (
    extract_patterns,
    compute_similarity,
    find_pattern_gaps,
    apply_patch_to_workflow,
    get_suggestions,
)


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


def _make_workflow(db, name, nodes=None, edges=None):
    wf = WorkflowModel(
        id=f"wf_{name[:8].lower().replace(' ', '_')}",
        name=name,
        nodes=nodes or [],
        edges=edges or [],
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


# ---------------------------------------------------------------------------
# Pattern Extraction
# ---------------------------------------------------------------------------

class TestPatternExtraction:

    def test_detects_retry_logic(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http", "retry_count": 3},
        ]
        info = extract_patterns(nodes, [])
        assert info["patterns"]["retry_logic"] is True
        assert "n2" in info["pattern_details"]["retry_nodes"]

    def test_detects_approval_gate(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "approval", "name": "Review", "approver_role": "manager"},
        ]
        info = extract_patterns(nodes, [])
        assert info["patterns"]["approval_gate"] is True
        assert info["patterns"]["human_escalation"] is True

    def test_detects_branching(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "condition", "name": "Check"},
            {"id": "n3", "type": "action", "name": "A"},
            {"id": "n4", "type": "action", "name": "B"},
        ]
        edges = [
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3", "condition": "true"},
            {"from": "n2", "to": "n4", "condition": "false"},
        ]
        info = extract_patterns(nodes, edges)
        assert info["patterns"]["branching"] is True

    def test_detects_wait_delay(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "wait", "name": "Delay", "duration_seconds": 5},
        ]
        info = extract_patterns(nodes, [])
        assert info["patterns"]["wait_delay"] is True

    def test_no_false_positives(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "Send", "tool": "email"},
            {"id": "n3", "type": "end", "name": "Done"},
        ]
        edges = [
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ]
        info = extract_patterns(nodes, edges)
        for pat in ["retry_logic", "error_handling", "approval_gate", "branching", "wait_delay"]:
            assert info["patterns"][pat] is False


# ---------------------------------------------------------------------------
# Similarity Scoring
# ---------------------------------------------------------------------------

class TestSimilarityScoring:

    def test_identical_workflows_score_one(self):
        info = {
            "node_types": {"trigger": 1, "action": 2},
            "tools": ["http", "email"],
            "edge_signatures": {"trigger->action": 2, "action->end": 1},
        }
        score = compute_similarity(info, info)
        assert score == 1.0

    def test_completely_different_scores_zero(self):
        a = {"node_types": {"trigger": 1}, "tools": ["http"], "edge_signatures": {"trigger->action": 1}}
        b = {"node_types": {"condition": 2}, "tools": ["db"], "edge_signatures": {"condition->action": 1}}
        score = compute_similarity(a, b)
        assert score == 0.0

    def test_partial_overlap(self):
        a = {"node_types": {"trigger": 1, "action": 2}, "tools": ["http"], "edge_signatures": {"trigger->action": 1}}
        b = {"node_types": {"trigger": 1, "action": 1}, "tools": ["email"], "edge_signatures": {"trigger->action": 1}}
        score = compute_similarity(a, b)
        assert 0 < score < 1.0


# ---------------------------------------------------------------------------
# Pattern Gaps
# ---------------------------------------------------------------------------

class TestPatternGaps:

    def test_finds_missing_retry(self):
        target = {
            "patterns": {"retry_logic": False, "error_handling": False},
            "pattern_details": {},
        }
        candidate = {
            "patterns": {"retry_logic": True, "error_handling": False},
            "pattern_details": {"retry_nodes": ["n2"]},
        }
        gaps = find_pattern_gaps(target, candidate)
        assert len(gaps) == 1
        assert gaps[0]["pattern"] == "retry_logic"

    def test_no_gap_when_both_have(self):
        target = {
            "patterns": {"approval_gate": True},
            "pattern_details": {"approval_nodes": ["n3"]},
        }
        candidate = {
            "patterns": {"approval_gate": True},
            "pattern_details": {"approval_nodes": ["n3"]},
        }
        gaps = find_pattern_gaps(target, candidate)
        assert len(gaps) == 0


# ---------------------------------------------------------------------------
# Apply Patch
# ---------------------------------------------------------------------------

class TestApplyPatch:

    def test_update_node_patch(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http"},
        ]
        patch = {"type": "update_node", "node_id": "n2", "field": "retry_count", "value": 3}
        new_nodes, _ = apply_patch_to_workflow(nodes, [], patch)
        n2 = next(n for n in new_nodes if n["id"] == "n2")
        assert n2["retry_count"] == 3

    def test_insert_between_patch(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "Send", "tool": "email"},
        ]
        edges = [{"from": "n1", "to": "n2"}]
        patch = {
            "type": "insert_between",
            "from_node_id": "n1",
            "to_node_id": "n2",
            "new_node": {"id": "n_new", "type": "approval", "name": "Gate"},
            "new_edges": [
                {"from": "n1", "to": "n_new"},
                {"from": "n_new", "to": "n2"},
            ],
        }
        new_nodes, new_edges = apply_patch_to_workflow(nodes, edges, patch)
        assert any(n["id"] == "n_new" and n["type"] == "approval" for n in new_nodes)
        assert any(e["from"] == "n_new" and e["to"] == "n2" for e in new_edges)
        assert not any(e["from"] == "n1" and e["to"] == "n2" for e in new_edges)

    def test_insert_between_with_branch_patch(self):
        nodes = [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http"},
            {"id": "n3", "type": "end", "name": "Done"},
        ]
        edges = [{"from": "n2", "to": "n3"}]
        patch = {
            "type": "insert_between_with_branch",
            "from_node_id": "n2",
            "to_node_id": "n3",
            "condition_node": {"id": "__new_condition__", "type": "condition", "name": "Check"},
            "branch_node": {"id": "__new_branch__", "type": "action", "name": "Alt", "tool": "http"},
        }
        new_nodes, new_edges = apply_patch_to_workflow(nodes, edges, patch)
        cond_node = next(n for n in new_nodes if n["type"] == "condition")
        br_node = next(n for n in new_nodes if n["type"] == "action" and n["name"] == "Alt")
        cond_id = cond_node["id"]
        # Should have edges: n2->cond, cond->n3 (true), cond->br (false)
        cond_edges = [e for e in new_edges if e.get("from") == cond_id]
        assert len(cond_edges) == 2  # true and false branches
        assert any(e.get("to") == "n3" and e.get("condition") == "true" for e in cond_edges)
        assert any(e.get("to") == br_node["id"] and e.get("condition") == "false" for e in cond_edges)


# ---------------------------------------------------------------------------
# Integration: get_suggestions
# ---------------------------------------------------------------------------

class TestGetSuggestions:

    def test_no_suggestions_with_single_workflow(self, db):
        wf = _make_workflow(db, "Only One", nodes=[
            {"id": "n1", "type": "trigger", "name": "Start"},
        ])
        suggestions = get_suggestions(db, wf.id)
        assert suggestions == []

    def test_returns_suggestions_for_similar_workflow(self, db):
        # Workflow A: simple, no retry
        wf_a = _make_workflow(db, "Customer Onboarding", nodes=[
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http"},
        ], edges=[{"from": "n1", "to": "n2"}])

        # Workflow B: similar but with retry
        _make_workflow(db, "Invoice Processor", nodes=[
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http", "retry_count": 3},
        ], edges=[{"from": "n1", "to": "n2"}])

        suggestions = get_suggestions(db, wf_a.id, top_k=5)
        assert len(suggestions) > 0
        retry_sugg = [s for s in suggestions if s["pattern"] == "retry_logic"]
        assert len(retry_sugg) == 1
        assert retry_sugg[0]["source_workflow_name"] == "Invoice Processor"
        assert retry_sugg[0]["similarity_score"] > 0.3

    def test_scores_sorted_descending(self, db):
        wf_a = _make_workflow(db, "Customer Onboarding", nodes=[
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http"},
        ])

        _make_workflow(db, "Support Router", nodes=[
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "HTTP", "tool": "http"},
        ])

        _make_workflow(db, "DB Sync Tool", nodes=[
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "action", "name": "DB", "tool": "db"},
        ])

        suggestions = get_suggestions(db, wf_a.id, top_k=5)
        scores = [s["similarity_score"] for s in suggestions]
        assert scores == sorted(scores, reverse=True)
