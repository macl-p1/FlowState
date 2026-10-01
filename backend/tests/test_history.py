"""Version history correctness + history-backed suggestions."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from tests.test_api import client, setup_test_db, TestingSessionLocal  # noqa: F401
from app.genealogy.cross_pollination import get_suggestions
from app.genealogy.diff import compute_diff
from app.genealogy.history_insights import pattern_timeline, version_outcomes
from app.genealogy.service import GenealogyService
from app.models import (
    WorkflowModel, WorkflowVersionModel, WorkflowBranchModel, WorkflowExecutionModel, StepExecutionModel,
    RunCorrectionModel, RunEvaluationModel,
)
from app.models.triggers import RunMetaModel, TriggerModel
from app.schemas.execution import ExecutionStatus

BASE = {
    "nodes": [
        {"id": "t", "type": "trigger", "name": "Start", "trigger": {"type": "manual"}},
        {"id": "a", "type": "action", "name": "Call API", "tool": "http", "inputs": {"url": "https://x"}},
        {"id": "e", "type": "end", "name": "Done", "outcome": "ok"},
    ],
    "edges": [{"from": "t", "to": "a"}, {"from": "a", "to": "e"}],
}
WITH_RETRY = {"nodes": [BASE["nodes"][0], {**BASE["nodes"][1], "retry_count": 3}, BASE["nodes"][2]], "edges": BASE["edges"]}
T0 = datetime(2026, 1, 1)


def _cleanup():
    db = TestingSessionLocal()
    for m in (RunCorrectionModel, RunEvaluationModel, RunMetaModel, TriggerModel, StepExecutionModel,
              WorkflowExecutionModel, WorkflowBranchModel, WorkflowVersionModel, WorkflowModel):
        db.query(m).delete()
    db.commit()
    db.close()


@pytest.fixture
def db():
    s = TestingSessionLocal()
    yield s
    s.close()
    _cleanup()


def _workflow(db, wid, current, versions):
    """versions: [(graph, created_at, rationale)]"""
    db.add(WorkflowModel(id=wid, name=wid, description="", nodes=current["nodes"], edges=current["edges"]))
    for i, (g, at, why) in enumerate(versions, 1):
        db.add(WorkflowVersionModel(id=f"{wid}_v{i}", workflow_id=wid, version_number=i, nodes=g["nodes"],
                                    edges=g["edges"], change_rationale=why, created_at=at))
    db.commit()


def _runs(db, wid, at, outcomes, snapshot=None, prefix="r"):
    """outcomes: string of c (completed) / f (failed) / x (completed but flagged wrong)."""
    for i, o in enumerate(outcomes):
        eid = f"{wid}_{prefix}{at:%m%d%H%M}_{i}"
        db.add(WorkflowExecutionModel(
            id=eid, workflow_id=wid, workflow_name=wid, started_at=at + timedelta(minutes=i),
            status=ExecutionStatus.FAILED if o == "f" else ExecutionStatus.COMPLETED,
        ))
        if o == "x":
            db.add(RunCorrectionModel(execution_id=eid, workflow_id=wid, kind="wrong_result"))
        if snapshot:
            db.add(RunMetaModel(execution_id=eid, snapshot=snapshot, input_context={}))
    db.commit()


# ── version history correctness ──

def test_layout_moves_and_noop_saves_do_not_create_versions(db):
    _workflow(db, "w", BASE, [])
    svc = GenealogyService(db)
    v1 = svc.save_version("w", BASE["nodes"], BASE["edges"], "first")
    moved = [{**n, "position": {"x": 999, "y": 5}} for n in BASE["nodes"]]
    assert svc.save_version("w", moved, BASE["edges"]).id == v1.id                  # layout only
    assert svc.save_version("w", list(reversed(BASE["nodes"])), BASE["edges"]).id == v1.id  # order only
    assert not compute_diff(BASE["nodes"], BASE["edges"], moved, BASE["edges"]).has_changes
    v2 = svc.save_version("w", WITH_RETRY["nodes"], WITH_RETRY["edges"], "add retry")
    assert v2.version_number == 2 and "modified 1 node" in v2.change_summary


def test_api_save_keeps_baseline_and_skips_noop(client):
    try:
        db = TestingSessionLocal()
        _workflow(db, "legacy", BASE, [])                                            # e.g. planner-made, no versions
        db.close()
        payload = {"name": "legacy", "description": "", **WITH_RETRY, "workflow_id": "legacy", "rationale": "API flaky"}
        client.post("/api/workflows", json=payload)
        client.post("/api/workflows", json=payload)                                  # same again: no new version
        versions = client.get("/api/workflows/legacy/history").json()["versions"]
        assert [v["version_number"] for v in versions] == [2, 1]
        assert versions[1]["change_rationale"].startswith("Baseline")                  # pre-edit state kept
        assert versions[0]["change_rationale"] == "API flaky"
        assert versions[1]["nodes"][1].get("retry_count") is None
    finally:
        _cleanup()


def test_applying_a_suggestion_is_versioned(client):
    try:
        db = TestingSessionLocal()
        _workflow(db, "ap", BASE, [])
        db.close()
        patch_ = {"type": "update_node", "node_id": "a", "field": "retry_count", "value": 3}
        r = client.post("/api/workflows/ap/suggestions/apply", json={"patch": patch_, "rationale": "from Invoice flow"})
        assert r.status_code == 200 and r.json()["version_number"] == 2
        versions = client.get("/api/workflows/ap/history").json()["versions"]
        assert versions[0]["change_rationale"] == "from Invoice flow"
        assert versions[0]["nodes"][1]["retry_count"] == 3 and "retry_count" not in versions[1]["nodes"][1]
    finally:
        _cleanup()


def test_restore_and_version_ownership(client):
    try:
        db = TestingSessionLocal()
        _workflow(db, "rs", WITH_RETRY, [(BASE, T0, "v1"), (WITH_RETRY, T0 + timedelta(days=1), "v2")])
        _workflow(db, "other", BASE, [(BASE, T0, "o1")])
        db.close()
        assert client.get("/api/workflows/rs/versions/other_v1").status_code == 404   # not this workflow's
        r = client.post("/api/workflows/rs/versions/rs_v1/restore", json={"rationale": "retry caused dupes"})
        assert r.status_code == 200 and r.json()["version_number"] == 3
        assert r.json()["change_rationale"] == "Restored v1: retry caused dupes"
        wf = client.get("/api/workflows/rs").json()
        assert "retry_count" not in wf["nodes"][1]                                   # current state is v1 again
        assert client.post("/api/workflows/rs/versions/other_v1/restore", json={}).status_code == 404
    finally:
        _cleanup()


def test_branch_records_parent_in_metadata(client):
    try:
        db = TestingSessionLocal()
        _workflow(db, "src", BASE, [(BASE, T0, "v1")])
        db.close()
        new_id = client.post("/api/workflows/src/branch", json={"name": "fork"}).json()["new_workflow_id"]
        assert client.get(f"/api/workflows/{new_id}").json()["metadata"]["branched_from"] == "src"
    finally:
        _cleanup()


# ── runs are attributed to the version they ran on ──

def test_runs_attributed_by_snapshot_then_by_time(db):
    _workflow(db, "b", WITH_RETRY, [(BASE, T0, None), (WITH_RETRY, T0 + timedelta(days=1), "retry")])
    _runs(db, "b", T0 + timedelta(hours=1), "cc")                                  # during v1
    _runs(db, "b", T0 + timedelta(days=2), "f")                                    # during v2
    _runs(db, "b", T0 + timedelta(days=3), "f", snapshot=BASE, prefix="replay")   # late replay of v1's graph
    timeline = pattern_timeline(db, "b")
    out = version_outcomes(db, "b", timeline)
    assert out[0] == [True, True, False] and out[1] == [False]


# ── history-backed suggestions ──

def _no_llm():
    return patch("app.genealogy.cross_pollination.enrich_with_llm", return_value=None)


def test_suggests_pattern_that_improved_a_similar_workflow(db):
    adopted_at = T0 + timedelta(days=1)
    _workflow(db, "invoice", WITH_RETRY, [(BASE, T0, None), (WITH_RETRY, adopted_at, "API started timing out")])
    _runs(db, "invoice", T0 + timedelta(hours=1), "cfxf")      # v1: 1 of 4 really succeeded ("x" flagged wrong)
    _runs(db, "invoice", adopted_at + timedelta(hours=1), "cccc")  # v2: 4 of 4
    _workflow(db, "target", BASE, [(BASE, T0, None)])

    with _no_llm():
        s = get_suggestions(db, "target")
    top = s[0]
    assert top["origin"] == "history" and top["pattern"] in ("retry_logic", "error_handling")
    ev = top["evidence"]
    assert ev["verdict"] == "improved" and ev["before"] == {"runs": 4, "rate": 0.25} and ev["after"] == {"runs": 4, "rate": 1.0}
    assert "API started timing out" in ev["text"] and "25% -> 100%" in ev["text"]
    assert top["apply_patch"]                                    # still one click to apply


def test_skips_patterns_that_made_things_worse(db):
    adopted_at = T0 + timedelta(days=1)
    _workflow(db, "bad", WITH_RETRY, [(BASE, T0, None), (WITH_RETRY, adopted_at, "tried retries")])
    _runs(db, "bad", T0 + timedelta(hours=1), "cccc")
    _runs(db, "bad", adopted_at + timedelta(hours=1), "ffff")   # retries made it worse there
    _workflow(db, "target", BASE, [(BASE, T0, None)])
    with _no_llm():
        s = get_suggestions(db, "target")
    assert not [x for x in s if x["origin"] == "history"]


def test_suggests_restoring_a_pattern_this_workflow_dropped(db):
    dropped_at = T0 + timedelta(days=1)
    _workflow(db, "solo", BASE, [(WITH_RETRY, T0, None), (BASE, dropped_at, "simplify")])
    _runs(db, "solo", T0 + timedelta(hours=1), "cccc")
    _runs(db, "solo", dropped_at + timedelta(hours=1), "cfff")
    with _no_llm():
        s = get_suggestions(db, "solo")                          # no other workflows needed
    restore = [x for x in s if x["origin"] == "self_history"]
    assert restore and restore[0]["suggestion"].startswith("Restore it")
    assert restore[0]["evidence"]["verdict"] == "worse" and "simplify" in restore[0]["evidence"]["text"]


def test_without_run_data_history_still_explains_but_ranks_lower(db):
    _workflow(db, "cand", WITH_RETRY, [(BASE, T0, None), (WITH_RETRY, T0 + timedelta(days=1), "flaky API")])
    _workflow(db, "target", BASE, [(BASE, T0, None)])
    with _no_llm():
        s = get_suggestions(db, "target")
    h = [x for x in s if x["origin"] == "history"]
    assert h and h[0]["evidence"]["verdict"] == "unknown" and "flaky API" in h[0]["evidence"]["text"]


# ── every suggestion patch keeps the workflow valid ──

def test_every_suggestion_patch_applies_cleanly_or_refuses():
    from app.agents.compiler import WorkflowCompiler
    from app.genealogy.cross_pollination import EIGHT_PATTERNS, PatchError, _build_suggestion, apply_patch_to_workflow
    from app.schemas.workflow import Workflow
    from app.tools.registry import registry

    wf = {
        "nodes": [
            {"id": "t", "type": "trigger", "name": "Start", "trigger": {"type": "manual"}},
            {"id": "a1", "type": "action", "name": "Fetch", "tool": "http", "inputs": {"url": "https://x"}},
            {"id": "a2", "type": "action", "name": "Notify", "tool": "send_email",
             "inputs": {"to": "a@b.c", "subject": "s", "body": "b"}},
            {"id": "e", "type": "end", "name": "Done", "outcome": "ok"},
        ],
        "edges": [{"from": "t", "to": "a1"}, {"from": "a1", "to": "a2"}, {"from": "a2", "to": "e"}],
    }
    details = {k: ["x"] for k in ("retry_nodes", "error_handling_nodes", "approval_nodes", "human_escalation_nodes",
                                  "branching_nodes", "wait_nodes", "fallback_path_nodes")}
    applied = 0
    for pattern in EIGHT_PATTERNS:
        s = _build_suggestion(pattern, details)
        if not s:
            continue
        try:
            nodes, edges = apply_patch_to_workflow(wf["nodes"], wf["edges"], s["apply_patch"])
        except PatchError:
            continue  # e.g. no approval node to configure: refusing is correct
        applied += 1
        ids = {n["id"] for n in nodes}
        assert all(e["from"] in ids and e["to"] in ids for e in edges), (pattern, edges)   # no dangling edges
        reach, todo = set(), ["t"]
        while todo:
            n = todo.pop()
            if n not in reach:
                reach.add(n)
                todo += [e["to"] for e in edges if e["from"] == n]
        assert reach == ids, (pattern, ids - reach)                                       # nothing orphaned
        WorkflowCompiler(tool_registry=registry).compile(
            Workflow.model_validate({"name": "w", "description": "", "nodes": nodes, "edges": edges}))
    assert applied >= 5


# ── canvas-shaped graphs are normalized; suggestions work from the workflow alone ──

CANVAS = {
    "nodes": [
        {"id": "n1", "type": "flowNode", "position": {"x": 0, "y": 0},
         "data": {"name": "Start", "tool": "HTTP Request", "detail": "Tool: ", "nodeType": "trigger"}},
        {"id": "n2", "type": "flowNode", "position": {"x": 0, "y": 100},
         "data": {"name": "Fetch", "tool": "HTTP Request", "detail": "Tool: http", "nodeType": "action"}},
        {"id": "n3", "type": "flowNode", "position": {"x": 0, "y": 200},
         "data": {"name": "Save", "tool": "update_database", "detail": "write the row", "nodeType": "action"}},
        {"id": "n4", "type": "flowNode", "position": {"x": 0, "y": 300},
         "data": {"name": "Done", "tool": "HTTP Request", "detail": "Tool: ", "nodeType": "end"}},
    ],
    "edges": [{"id": f"e-{i}", "source": f"n{i}", "target": f"n{i + 1}", "animated": True} for i in (1, 2, 3)],
}


def test_canvas_shaped_graph_is_normalized():
    from app.utils.graph import normalize_graph, is_canvas_shaped
    nodes, edges = normalize_graph(CANVAS["nodes"], CANVAS["edges"])
    assert [n["type"] for n in nodes] == ["trigger", "action", "action", "end"]
    assert "tool" not in nodes[0] and "tool" not in nodes[3]          # default tool on non-actions dropped
    assert nodes[1]["tool"] == "http" and "detail" not in nodes[1]     # display name mapped, filler dropped
    assert nodes[2]["detail"] == "write the row"                       # real text kept
    assert edges == [{"from": "n1", "to": "n2"}, {"from": "n2", "to": "n3"}, {"from": "n3", "to": "n4"}]
    assert not is_canvas_shaped(nodes, edges) and normalize_graph(nodes, edges) == (nodes, edges)  # idempotent


def test_save_normalizes_and_startup_fixes_stored_rows(client):
    try:
        wid = client.post("/api/workflows", json={"name": "c", **CANVAS}).json()["id"]
        stored = client.get(f"/api/workflows/{wid}").json()
        assert stored["nodes"][1]["type"] == "action" and stored["edges"][0] == {"from": "n1", "to": "n2"}

        from app.utils.graph import normalize_stored_graphs
        from tests.test_api import test_engine
        db = TestingSessionLocal()
        db.add(WorkflowModel(id="legacy_canvas", name="legacy", nodes=CANVAS["nodes"], edges=CANVAS["edges"]))
        db.commit()
        db.close()
        assert normalize_stored_graphs(test_engine) >= 1
        assert normalize_stored_graphs(test_engine) == 0
    finally:
        _cleanup()


def test_suggestions_from_the_workflow_alone(db):
    from app.genealogy.cross_pollination import apply_patch_to_workflow
    from app.models import StepExecutionModel as Step
    from app.schemas.execution import StepStatus
    from app.utils.graph import normalize_graph
    nodes, edges = normalize_graph(CANVAS["nodes"], CANVAS["edges"])
    _workflow(db, "only", {"nodes": nodes, "edges": edges}, [])            # no other workflows, no history
    for i in range(2):                                                      # "Save" failed twice before
        db.add(WorkflowExecutionModel(id=f"x{i}", workflow_id="only", workflow_name="only", status=ExecutionStatus.FAILED))
        db.add(Step(execution_id=f"x{i}", node_id="n3", node_type="action", node_name="Save", status=StepStatus.FAILED))
    db.commit()

    with _no_llm():
        s = {x["pattern"]: x for x in get_suggestions(db, "only")}
    retry, gate = s["retry_logic"], s["approval_gate"]
    assert retry["origin"] == "self" and retry["target_node_id"] == "n3" and "failed in 2" in retry["description"]
    assert gate["target_node_id"] == "n3" and "update_database" in gate["description"]

    n2, e2 = apply_patch_to_workflow(nodes, edges, gate["apply_patch"])
    approval = next(n for n in n2 if n["type"] == "approval")
    assert {"from": "n2", "to": approval["id"]} in e2 and {"from": approval["id"], "to": "n3"} in e2

    wf = db.get(WorkflowModel, "only")                                       # once applied, it's not suggested again
    wf.nodes, wf.edges = apply_patch_to_workflow(n2, e2, retry["apply_patch"])
    db.commit()
    with _no_llm():
        after = get_suggestions(db, "only")
    assert not [x for x in after if x["target_node_id"] == "n3"]        # Save is covered now
    assert [x["target_node_id"] for x in after if x["pattern"] == "retry_logic"] == ["n2"]  # next outbound node


def test_history_evidence_uses_this_workflows_precise_target(db):
    from app.utils.graph import normalize_graph
    nodes, edges = normalize_graph(CANVAS["nodes"], CANVAS["edges"])     # Fetch (http, n2) and Save (update_database, n3)
    risky_first = {"nodes": nodes, "edges": edges}
    with_retry = {"nodes": [dict(n, retry_count=3) if n["id"] == "n3" else n for n in nodes], "edges": edges}
    adopted_at = T0 + timedelta(days=1)
    _workflow(db, "peer", with_retry, [(risky_first, T0, None), (with_retry, adopted_at, "db writes were flaky")])
    _runs(db, "peer", T0 + timedelta(hours=1), "ffff")
    _runs(db, "peer", adopted_at + timedelta(hours=1), "cccc")
    _workflow(db, "mine", risky_first, [(risky_first, T0, None)])
    for i in range(2):  # here, Save is the node that fails
        db.add(WorkflowExecutionModel(id=f"m{i}", workflow_id="mine", workflow_name="mine", status=ExecutionStatus.FAILED))
        db.add(StepExecutionModel(execution_id=f"m{i}", node_id="n3", node_type="action", node_name="Save",
                                  status=__import__("app.schemas.execution", fromlist=["StepStatus"]).StepStatus.FAILED))
    db.commit()
    with _no_llm():
        retry = next(x for x in get_suggestions(db, "mine") if x["pattern"] == "retry_logic")
    assert retry["origin"] == "history" and retry["evidence"]["verdict"] == "improved"
    assert retry["apply_patch"]["node_id"] == "n3" and retry["target_node_id"] == "n3"   # not "the first action"
