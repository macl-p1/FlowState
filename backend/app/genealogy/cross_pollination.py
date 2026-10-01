"""Cross-pollination engine — similarity scoring, pattern extraction, gap detection, and suggestion generation."""

from collections import Counter
from typing import Any
from anthropic import Anthropic

from app.config import settings

MIN_SIMILARITY = 0.15  # ponytail: structural relevance threshold


# ── Pattern Definitions ──────────────────────────────────────────────────────

PATTERN_LABELS: dict[str, str] = {
    "retry_logic": "Retry Logic",
    "error_handling": "Error Handling",
    "approval_gate": "Approval Gate",
    "human_escalation": "Human Escalation",
    "branching": "Branching",
    "input_validation": "Input Validation",
    "wait_delay": "Wait / Delay",
    "fallback_path": "Fallback Path",
}

EIGHT_PATTERNS = list(PATTERN_LABELS.keys())


# ── Pattern Extraction ──────────────────────────────────────────────────────

def extract_patterns(nodes: list[dict], edges: list[dict]) -> dict[str, Any]:
    """
    Analyze a workflow graph and extract structural patterns.

    Returns a dict with node_types, tools, edge_signatures, patterns (bool flags),
    and pattern_details (supporting lists).
    """
    node_list = nodes if nodes else []
    edge_list = edges if edges else []

    # Basic stats
    node_types = Counter(n.get("type", "unknown") for n in node_list)
    tools = sorted({n.get("tool") for n in node_list if n.get("tool")})

    # Edge signatures: "source_type->target_type"
    node_type_map = {n["id"]: n.get("type", "unknown") for n in node_list if "id" in n}
    edge_signatures = Counter()
    for e in edge_list:
        src_type = node_type_map.get(e.get("from", ""), "unknown")
        tgt_type = node_type_map.get(e.get("to", ""), "unknown")
        edge_signatures[f"{src_type}->{tgt_type}"] += 1

    # Pattern detection
    patterns: dict[str, bool] = {p: False for p in EIGHT_PATTERNS}
    pattern_details: dict[str, Any] = {}

    # retry_logic: action nodes with retry_count > 0 or retry_delay != 1.0
    retry_nodes = [
        n["id"] for n in node_list
        if n.get("type") == "action"
        and (n.get("retry_count", 0) > 0 or n.get("retry_delay", 1.0) != 1.0)
    ]
    patterns["retry_logic"] = len(retry_nodes) > 0
    pattern_details["retry_nodes"] = retry_nodes

    # error_handling: action nodes with expected_outcome or retry_count > 0
    error_nodes = [
        n["id"] for n in node_list
        if n.get("type") == "action"
        and (n.get("expected_outcome") is not None or n.get("retry_count", 0) > 0)
    ]
    patterns["error_handling"] = len(error_nodes) > 0
    pattern_details["error_handling_nodes"] = error_nodes

    # approval_gate: any approval node
    approval_nodes = [n["id"] for n in node_list if n.get("type") == "approval"]
    patterns["approval_gate"] = len(approval_nodes) > 0
    pattern_details["approval_nodes"] = approval_nodes

    # human_escalation: approval node with approver_role
    human_nodes = [
        n["id"] for n in node_list
        if n.get("type") == "approval" and n.get("approver_role")
    ]
    patterns["human_escalation"] = len(human_nodes) > 0
    pattern_details["human_escalation_nodes"] = human_nodes

    # branching: condition node with 2+ outgoing edges
    out_degree: dict[str, int] = {}
    for e in edge_list:
        from_id = e.get("from", "")
        out_degree[from_id] = out_degree.get(from_id, 0) + 1
    branching_nodes = [
        n["id"] for n in node_list
        if n.get("type") == "condition" and out_degree.get(n["id"], 0) >= 2
    ]
    patterns["branching"] = len(branching_nodes) > 0
    pattern_details["branching_nodes"] = branching_nodes

    # input_validation: condition node is immediate child of trigger
    trigger_ids = {n["id"] for n in node_list if n.get("type") == "trigger"}
    condition_after_trigger = any(
        e.get("from") in trigger_ids and _get_node_by_id(node_list, e.get("to", ""), "condition")
        for e in edge_list
    )
    patterns["input_validation"] = condition_after_trigger

    # wait_delay: any wait node
    wait_nodes = [n["id"] for n in node_list if n.get("type") == "wait"]
    patterns["wait_delay"] = len(wait_nodes) > 0
    pattern_details["wait_nodes"] = wait_nodes

    # fallback_path: condition → end(failed) or action with "fallback" in name
    end_fail_ids = {
        n["id"] for n in node_list
        if n.get("type") == "end" and n.get("outcome") in ("failed", "cancelled", "error")
    }
    fallback_condition = any(
        e.get("from") in _get_condition_node_ids(node_list)
        and e.get("to") in end_fail_ids
        for e in edge_list
    )
    fallback_action = [
        n["id"] for n in node_list
        if "fallback" in n.get("name", "").lower()
    ]
    patterns["fallback_path"] = fallback_condition or len(fallback_action) > 0
    pattern_details["fallback_path_nodes"] = fallback_action

    return {
        "node_types": dict(node_types),
        "tools": tools,
        "edge_signatures": dict(edge_signatures),
        "patterns": patterns,
        "pattern_details": pattern_details,
    }


def _get_node_by_id(nodes: list[dict], node_id: str, node_type: str) -> bool:
    for n in nodes:
        if n.get("id") == node_id and n.get("type") == node_type:
            return True
    return False


def _get_condition_node_ids(nodes: list[dict]) -> set[str]:
    return {n["id"] for n in nodes if n.get("type") == "condition"}


# ── Similarity Scoring ──────────────────────────────────────────────────────

def compute_similarity(
    target_info: dict[str, Any],
    candidate_info: dict[str, Any],
) -> float:
    """
    Compute weighted Jaccard similarity between two workflow profiles.

    Weights: node types 0.30, edge signatures 0.30, tools 0.40.
    Returns a value in [0.0, 1.0].
    """
    def jaccard(a: set, b: set) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    node_types_a = set(target_info.get("node_types", {}).keys())
    node_types_b = set(candidate_info.get("node_types", {}).keys())
    edge_sigs_a = set(target_info.get("edge_signatures", {}).keys())
    edge_sigs_b = set(candidate_info.get("edge_signatures", {}).keys())
    tools_a = set(target_info.get("tools", []))
    tools_b = set(candidate_info.get("tools", []))

    score = (
        0.30 * jaccard(node_types_a, node_types_b)
        + 0.30 * jaccard(edge_sigs_a, edge_sigs_b)
        + 0.40 * jaccard(tools_a, tools_b)
    )
    return round(score, 4)


# ── Pattern Gap Detection ───────────────────────────────────────────────────

def find_pattern_gaps(
    target_info: dict[str, Any],
    candidate_info: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Find patterns the candidate has that the target is missing.

    Both args are the full extract_patterns() output dicts.
    Returns a list of suggestion dicts with structured apply_patch instructions.
    """
    gaps = []
    target_pats = target_info.get("patterns", {})
    cand_pats = candidate_info.get("patterns", {})
    cand_details = candidate_info.get("pattern_details", {})

    for pattern_key in EIGHT_PATTERNS:
        if cand_pats.get(pattern_key) and not target_pats.get(pattern_key):
            suggestion = _build_suggestion(pattern_key, cand_details)
            if suggestion:
                gaps.append(suggestion)

    return gaps


def _build_suggestion(pattern_key: str, cand_details: dict[str, Any]) -> dict[str, Any] | None:
    """Build a structured suggestion with an apply_patch for a pattern gap."""
    label = PATTERN_LABELS.get(pattern_key, pattern_key)

    if pattern_key == "retry_logic":
        retry_nodes = cand_details.get("retry_nodes", [])
        if not retry_nodes:
            return None
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": f"Workflow has retry logic configured on {len(retry_nodes)} action node(s)",
            "suggestion": f"Add retry configuration (retry_count: 3, retry_delay: 1.0) to your action nodes to handle transient failures",
            "target_node_id": retry_nodes[0],
            "apply_patch": {
                "type": "update_node",
                "node_id": "__first_action__",
                "field": "retry_count",
                "value": 3,
                "secondary_fields": {"retry_delay": 1.0},
            },
        }

    elif pattern_key == "error_handling":
        err_nodes = cand_details.get("error_handling_nodes", [])
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": f"Workflow has error handling on {len(err_nodes)} action node(s)",
            "suggestion": "Add expected_outcome descriptions to your action nodes so failures are diagnosable",
            "target_node_id": err_nodes[0] if err_nodes else None,
            "apply_patch": {
                "type": "update_node",
                "node_id": "__first_action__",
                "field": "expected_outcome",
                "value": "Operation completed successfully",
            },
        }

    elif pattern_key == "approval_gate":
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": "Workflow has an approval gate for human review",
            "suggestion": "Add an approval node before critical actions to enable human-in-the-loop review",
            "target_node_id": None,
            "apply_patch": {
                "type": "insert_between",
                "from_node_id": "__trigger__",
                "to_node_id": "__first_action__",
                "new_node": {
                    "id": "__new_approval__",
                    "type": "approval",
                    "name": "Approval Gate",
                    "reason": "Manual review required before proceeding",
                },
                "new_edges": [
                    {"from": "__trigger__", "to": "__new_approval__"},
                    {"from": "__new_approval__", "to": "__first_action__"},
                ],
            },
        }

    elif pattern_key == "human_escalation":
        human_nodes = cand_details.get("human_escalation_nodes", [])
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": f"Workflow routes failures to a human reviewer ({len(human_nodes)} escalation point(s))",
            "suggestion": "Add an approver_role to your approval node so failures go to the right team",
            "target_node_id": human_nodes[0] if human_nodes else None,
            "apply_patch": {
                "type": "update_node",
                "node_id": "__first_approval__",
                "field": "approver_role",
                "value": "manager",
            },
        }

    elif pattern_key == "branching":
        branch_nodes = cand_details.get("branching_nodes", [])
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": f"Workflow has conditional branching ({len(branch_nodes)} branch point(s))",
            "suggestion": "Add a condition node to split the workflow based on a runtime check",
            "target_node_id": branch_nodes[0] if branch_nodes else None,
            "apply_patch": {
                "type": "insert_between_with_branch",
                "from_node_id": "__first_action__",
                "to_node_id": "__end__",
                "condition_node": {
                    "id": "__new_condition__",
                    "type": "condition",
                    "name": "Check Result",
                    "expression": "True",
                },
                "branch_node": {
                    "id": "__new_branch__",
                    "type": "action",
                    "name": "Alternate Path",
                    "tool": "http",
                },
            },
        }

    elif pattern_key == "input_validation":
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": "Workflow validates inputs before processing",
            "suggestion": "Add a condition node right after the trigger to validate incoming data",
            "target_node_id": None,
            "apply_patch": {
                "type": "insert_between",
                "from_node_id": "__trigger__",
                "to_node_id": "__first_action__",
                "new_node": {
                    "id": "__new_condition__",
                    "type": "condition",
                    "name": "Validate Input",
                    "expression": "context.get('valid', True)",
                },
            },
        }

    elif pattern_key == "wait_delay":
        wait_nodes = cand_details.get("wait_nodes", [])
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": f"Workflow has {len(wait_nodes)} wait/delay node(s)",
            "suggestion": "Add a wait node to introduce delays between dependent operations",
            "target_node_id": wait_nodes[0] if wait_nodes else None,
            "apply_patch": {
                "type": "insert_between",
                "from_node_id": "__first_action__",
                "to_node_id": "__second_action__",
                "new_node": {
                    "id": "__new_wait__",
                    "type": "wait",
                    "name": "Delay",
                    "duration_seconds": 5,
                },
            },
        }

    elif pattern_key == "fallback_path":
        return {
            "pattern": pattern_key,
            "pattern_label": label,
            "description": "Workflow has a fallback/error path",
            "suggestion": "Add a fallback branch that handles failures gracefully instead of stopping",
            "target_node_id": None,
            "apply_patch": {
                "type": "insert_between_with_branch",
                "from_node_id": "__first_action__",
                "to_node_id": "__end__",
                "condition_node": {
                    "id": "__new_condition__",
                    "type": "condition",
                    "name": "Check Success",
                    "expression": "last_result.get('success', False)",
                },
                "branch_node": {
                    "id": "__new_fallback__",
                    "type": "action",
                    "name": "Fallback Handler",
                    "tool": "http",
                },
            },
        }

    return None


# ── LLM Enrichment ──────────────────────────────────────────────────────────

def enrich_with_llm(
    target_info: dict[str, Any],
    target_nodes: list[dict],
    target_edges: list[dict],
    candidates: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> list[dict[str, Any]] | None:
    """
    Send top candidates to Claude for richer, more contextual suggestions.

    Returns refined suggestions or None on failure (caller uses structural suggestions).
    """
    if not settings.anthropic_api_key or not candidates:
        return None

    try:
        client = Anthropic(
            api_key=settings.anthropic_api_key,
            base_url=settings.anthropic_base_url or None,
        )

        # Build a compact summary of the target workflow
        target_summary = _summarize_workflow(target_nodes, target_edges)
        candidate_summaries = []
        for c in candidates[:3]:
            candidate_summaries.append({
                "name": c.get("name", "unknown"),
                "similarity": c.get("score", 0),
                "summary": _summarize_workflow(c.get("nodes", []), c.get("edges", [])),
                "gaps": [g for g in gaps if g.get("pattern") in c.get("gap_patterns", [])],
            })

        prompt = f"""You are a workflow optimization advisor. Compare two workflows and suggest concrete improvements.

TARGET WORKFLOW:
{target_summary}

CANDIDATE WORKFLOWS (ranked by similarity):
{chr(10).join(f"{i+1}. {c['name']} (similarity: {c['similarity']:.0%}){chr(10)}{c['summary']}{chr(10)}Missing patterns: {', '.join(g['pattern'] for g in c.get('gaps', []))}" for i, c in enumerate(candidate_summaries))}

For each candidate with missing patterns, generate up to 3 specific, actionable suggestions.
Each suggestion must include:
- pattern: one of [retry_logic, error_handling, approval_gate, human_escalation, branching, input_validation, wait_delay, fallback_path]
- pattern_label: human-readable label
- description: what the candidate workflow does
- suggestion: concrete advice for the target workflow
- target_node_id: the node ID in the target where this should be applied (or null)

Respond as a JSON array of suggestion objects. No markdown, no extra text."""

        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text, skipping thinking blocks
        text_content = ""
        for block in response.content:
            if hasattr(block, "text") and block.text:
                text_content += block.text

        import json
        llm_suggestions = json.loads(text_content.strip())
        if isinstance(llm_suggestions, list):
            return llm_suggestions
        return None
    except Exception:
        return None


def _summarize_workflow(nodes: list[dict], edges: list[dict]) -> str:
    """Compact summary for LLM prompt."""
    lines = [f"  Nodes ({len(nodes)}):"]
    for n in nodes:
        lines.append(f"    - {n.get('id')}: {n.get('type')} / {n.get('name', '?')}" + (f" [tool: {n.get('tool')}]" if n.get("tool") else ""))
    lines.append(f"  Edges ({len(edges)}):")
    for e in edges:
        cond = f" [{e.get('condition')}]" if e.get("condition") else ""
        lines.append(f"    - {e.get('from')} -> {e.get('to')}{cond}")
    return "\n".join(lines)


# ── Apply Patch ─────────────────────────────────────────────────────────────

class PatchError(ValueError):
    """The patch cannot be applied cleanly to this workflow (missing anchor node, not connected, no-op)."""


def _anchor_refs(nodes: list[dict]) -> dict[str, str | None]:
    """Placeholders that suggestions use to point at existing nodes."""
    def ids(t: str) -> list[str]:
        return [n["id"] for n in nodes if n.get("type") == t]
    actions = ids("action")
    return {
        "__trigger__": next(iter(ids("trigger")), None),
        "__first_action__": actions[0] if actions else None,
        "__second_action__": actions[1] if len(actions) > 1 else None,
        "__first_approval__": next(iter(ids("approval")), None),
        "__end__": next(iter(ids("end")), None),
    }


def apply_patch_to_workflow(
    nodes: list[dict],
    edges: list[dict],
    patch: dict[str, Any],
) -> tuple[list[dict], list[dict]]:
    """
    Apply a structured patch to a workflow's nodes and edges.

    Placeholders (__trigger__, __first_action__, ...) are resolved against this workflow; new nodes
    with placeholder ids get real ids. New nodes are always spliced into the existing edge so the
    graph stays connected. Raises PatchError instead of producing a broken or unchanged graph.
    Returns (new_nodes, new_edges); originals are not mutated.
    """
    import uuid

    patch_type = patch.get("type")
    nodes_out = [dict(n) for n in nodes]
    edges_out = [dict(e) for e in edges]
    anchors = _anchor_refs(nodes_out)
    existing = {n["id"] for n in nodes_out}

    def ref(x: str | None) -> str:
        if x in anchors:
            if anchors[x] is None:
                raise PatchError(f"this workflow has no node for {x.strip('_').replace('_', ' ')}")
            return anchors[x]
        if x not in existing:
            raise PatchError(f"node {x!r} does not exist in this workflow")
        return x

    def fresh(spec: dict) -> dict:
        n = dict(spec)
        if not n.get("id") or n["id"].startswith("__") or n["id"] in existing:
            n["id"] = f"node_{uuid.uuid4().hex[:6]}"
        return n

    if patch_type == "update_node":
        target = ref(patch.get("node_id"))
        n = next(n for n in nodes_out if n["id"] == target)
        n[patch.get("field")] = patch.get("value")
        for k, v in (patch.get("secondary_fields") or {}).items():
            n[k] = v

    elif patch_type == "insert_between":
        a, b = ref(patch.get("from_node_id")), ref(patch.get("to_node_id"))
        link = next((e for e in edges_out if e.get("from") == a and e.get("to") == b), None)
        if not link:
            raise PatchError("those nodes are not directly connected, so there is nothing to insert between")
        new_node = fresh(patch.get("new_node", {}))
        edges_out.remove(link)
        edges_out.append({**link, "to": new_node["id"]})  # keeps a branch condition on the first segment
        edges_out.append({"from": new_node["id"], "to": b})
        nodes_out.append(new_node)

    elif patch_type == "insert_between_with_branch":
        # After node a: condition true -> wherever a used to go, false -> new branch node -> end.
        a, end = ref(patch.get("from_node_id")), ref(patch.get("to_node_id"))
        outs = [e for e in edges_out if e.get("from") == a]
        link = outs[0] if len(outs) == 1 else next((e for e in outs if e.get("to") == end), None)
        nxt = link["to"] if link else end
        if link:
            edges_out.remove(link)
        cond, branch = fresh(patch.get("condition_node", {})), fresh(patch.get("branch_node", {}))
        edges_out += [
            {"from": a, "to": cond["id"], **({"condition": link["condition"]} if link and link.get("condition") else {})},
            {"from": cond["id"], "to": nxt, "condition": "true"},
            {"from": cond["id"], "to": branch["id"], "condition": "false"},
            {"from": branch["id"], "to": end},
        ]
        nodes_out += [cond, branch]

    elif patch_type == "append_node":
        a = ref(patch.get("from_node_id"))
        new_node = fresh(patch.get("new_node", {}))
        edges_out.append({"from": a, "to": new_node["id"]})
        nodes_out.append(new_node)

    else:
        raise PatchError(f"unknown patch type {patch_type!r}")

    if nodes_out == nodes and edges_out == edges:
        raise PatchError("this change is already in the workflow")
    return nodes_out, edges_out


def _find_node(nodes: list[dict], node_id: str) -> dict | None:
    for n in nodes:
        if n.get("id") == node_id:
            return n
    return None


def _find_first_by_type(nodes: list[dict], node_type: str) -> dict | None:
    for n in nodes:
        if n.get("type") == node_type:
            return n
    return None


# ── Main Entry Point ────────────────────────────────────────────────────────

def get_suggestions(
    db,
    workflow_id: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Suggestions for a workflow: history-backed ones first (patterns similar workflows adopted with
    measurable benefit, or patterns this workflow dropped and then got worse), then structural
    cross-pollination for the remaining patterns. Each suggestion has `origin` and `evidence`.
    """
    from app.genealogy.history_insights import history_suggestions

    intrinsic = {s["pattern"]: s for s in intrinsic_suggestions(db, workflow_id)}
    history = []
    for h in history_suggestions(db, workflow_id):
        mine = intrinsic.get(h["pattern"])
        if mine:  # history's evidence, but aimed at the node this workflow's own check picked
            h = {**h, "apply_patch": mine["apply_patch"], "target_node_id": mine["target_node_id"],
                 "description": f"{mine['description']}. {h['description']}"}
        history.append(h)
    seen = {h["pattern"] for h in history}
    structural = {}
    for s in _structural_suggestions(db, workflow_id, top_k):
        structural.setdefault(s["pattern"], s)
    own = []
    for s in intrinsic.values():
        if s["pattern"] in seen:
            continue
        twin = structural.get(s["pattern"])
        if twin:  # keep our precise target, credit the similar workflow that already does it
            s = {**s, "source_workflow_id": twin["source_workflow_id"], "source_workflow_name": twin["source_workflow_name"],
                 "similarity_score": twin["similarity_score"],
                 "description": f"{s['description']}. '{twin['source_workflow_name']}' already does this."}
        own.append(s)
    seen |= {s["pattern"] for s in own}
    rest = [{**s, "origin": "structural", "evidence": None} for p, s in structural.items() if p not in seen]
    return (history + own + rest)[: top_k * 2]


# Tools that only compute locally: retrying them doesn't help.
_LOCAL_TOOLS = frozenset({
    "transform", "transform_data", "merge_data", "hash_content", "conditional_router", "delay", "wait",
    "aggregate_metrics", "classify_text", "fan_in", "fan_out",
})


def intrinsic_suggestions(db, workflow_id: str) -> list[dict[str, Any]]:
    """
    Suggestions from the workflow itself, needing no other workflows:
    - retry on actions that call out (ranked by how often that node actually failed in past runs)
    - an approval gate before irreversible actions (tools the registry marks CONFIRM / HUMAN_ONLY)
    """
    import uuid
    from app.models import WorkflowModel, WorkflowExecutionModel, StepExecutionModel
    from app.schemas.execution import StepStatus
    from app.schemas.workflow import PermissionLevel
    from app.tools.registry import registry

    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        return []
    nodes, edges = wf.nodes or [], wf.edges or []
    info = extract_patterns(nodes, edges)
    actions = [n for n in nodes if n.get("type") == "action" and n.get("tool")]

    failures: dict[str, int] = {}
    for (node_id,) in (
        db.query(StepExecutionModel.node_id)
        .join(WorkflowExecutionModel, WorkflowExecutionModel.id == StepExecutionModel.execution_id)
        .filter(WorkflowExecutionModel.workflow_id == workflow_id, StepExecutionModel.status == StepStatus.FAILED)
    ):
        failures[node_id] = failures.get(node_id, 0) + 1

    def make(pattern: str, description: str, suggestion: str, node: dict, patch: dict) -> dict[str, Any]:
        return {
            "id": f"sugg_{uuid.uuid4().hex[:8]}", "workflow_id": workflow_id,
            "source_workflow_id": workflow_id, "source_workflow_name": wf.name, "similarity_score": 1.0,
            "pattern": pattern, "pattern_label": PATTERN_LABELS[pattern], "description": description,
            "suggestion": suggestion, "target_node_id": node["id"], "actionable": True, "apply_patch": patch,
            "origin": "self", "evidence": None,
        }

    out = []
    outbound = [n for n in actions if n["tool"] not in _LOCAL_TOOLS and not n.get("retry_count")]
    if outbound:
        node = max(outbound, key=lambda n: failures.get(n["id"], 0))  # stable: first outbound if no failures
        failed = failures.get(node["id"], 0)
        out.append(make(
            "retry_logic",
            f"'{node.get('name', node['id'])}' calls {node['tool']} with no retry"
            + (f"; it failed in {failed} past run(s)" if failed else ""),
            f"Retry '{node.get('name', node['id'])}' up to 3 times so a transient error doesn't fail the whole run",
            node, {"type": "update_node", "node_id": node["id"], "field": "retry_count", "value": 3,
                   "secondary_fields": {"retry_delay": 2.0}},
        ))

    def risky(n: dict) -> bool:
        tool = registry.get(n["tool"])
        return bool(tool and tool.permission in (PermissionLevel.CONFIRM, PermissionLevel.HUMAN_ONLY))

    if not info["patterns"]["approval_gate"]:
        for node in (n for n in actions if risky(n)):
            pred = next((e["from"] for e in edges if e.get("to") == node["id"]), None)
            if pred:
                out.append(make(
                    "approval_gate",
                    f"'{node.get('name', node['id'])}' runs {node['tool']}, which can't be undone, without human review",
                    f"Add an approval step before '{node.get('name', node['id'])}'",
                    node, {"type": "insert_between", "from_node_id": pred, "to_node_id": node["id"],
                           "new_node": {"id": "__new_approval__", "type": "approval", "name": "Approve before "
                                        + node.get("name", node["id"]), "reason": f"Review before {node['tool']}"}},
                ))
                break
    return out


def _structural_suggestions(
    db,
    workflow_id: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Cross-pollination suggestions from similar workflows, weighted by outcome evidence.

    A candidate that adopted a pattern AND improved gets a higher similarity score
    than one that merely has it. Collective consensus (N workflows already using it)
    also strengthens the suggestion.
    """
    from app.models import WorkflowModel
    from app.api.quality import workflow_quality

    target = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not target:
        return []

    all_workflows = db.query(WorkflowModel).filter(
        WorkflowModel.id != workflow_id
    ).all()

    if not all_workflows:
        return []

    target_info = extract_patterns(target.nodes or [], target.edges or [])
    target_nodes = target.nodes or []
    target_edges = target.edges or []

    # Pre-compute: outcome evidence per workflow (success rate, override rate, eval score)
    wf_evidence: dict[str, dict] = {}
    for wf in all_workflows:
        try:
            q = workflow_quality(db, wf.id)
            wf_evidence[wf.id] = q
        except Exception:
            wf_evidence[wf.id] = {}

    # Pre-compute: pattern adoption timelines for outcome evidence
    from app.genealogy.history_insights import pattern_timeline, pattern_events, version_outcomes, event_evidence
    wf_timelines: dict[str, list[dict]] = {}
    wf_outcomes: dict[str, dict] = {}
    for wf in all_workflows:
        try:
            tl = pattern_timeline(db, wf.id)
            wf_timelines[wf.id] = tl
            wf_outcomes[wf.id] = version_outcomes(db, wf.id, tl)
        except Exception:
            wf_timelines[wf.id] = []
            wf_outcomes[wf.id] = {}

    # Score all candidates
    candidates = []
    for wf in all_workflows:
        wf_nodes = wf.nodes or []
        wf_edges = wf.edges or []
        if not wf_nodes:
            continue

        cand_info = extract_patterns(wf_nodes, wf_edges)
        score = compute_similarity(target_info, cand_info)

        if score < MIN_SIMILARITY:
            continue

        # Find pattern gaps
        gaps = find_pattern_gaps(target_info, cand_info)
        if not gaps:
            continue

        # Attach outcome evidence to each gap
        timeline = wf_timelines.get(wf.id, [])
        outcomes = wf_outcomes.get(wf.id, {})
        ev = wf_evidence.get(wf.id, {})

        # Pattern adoption events with outcome evidence
        adoption_evidence: dict[str, dict] = {}
        for evt in pattern_events(timeline):
            if evt["kind"] == "adopted" and evt["pattern"] in cand_info["patterns"] and cand_info["patterns"][evt["pattern"]]:
                ee = event_evidence(evt, timeline, outcomes)
                if ee["verdict"] != "worse":
                    adoption_evidence[evt["pattern"]] = ee

        # For patterns the workflow always had, estimate from overall quality
        for g in gaps:
            pat = g["pattern"]
            if pat not in adoption_evidence and cand_info["patterns"].get(pat):
                adoption_evidence[pat] = {
                    "verdict": "unknown",
                    "before": {"runs": 0, "rate": None},
                    "after": {"runs": ev.get("runs", 0), "rate": ev.get("avg_score")},
                    "from_quality": True,
                }

        # Count how many other workflows also have this pattern (consensus)
        pattern_consensus: dict[str, int] = {}
        for other in all_workflows:
            if other.id == wf.id:
                continue
            o_info = extract_patterns(other.nodes or [], other.edges or [])
            for g in gaps:
                if o_info["patterns"].get(g["pattern"]):
                    pattern_consensus[g["pattern"]] = pattern_consensus.get(g["pattern"], 0) + 1

        for g in gaps:
            pat = g["pattern"]
            ae = adoption_evidence.get(pat)
            evidence_text = ""
            if ae:
                if ae["verdict"] == "improved":
                    b_rate = ae["before"]["rate"] or 0
                    a_rate = ae["after"]["rate"] or 0
                    evidence_text = f"'{wf.name}' adopted this and success went {b_rate:.0%} → {a_rate:.0%}"
                elif ae.get("from_quality"):
                    a_rate = ae["after"]["rate"]
                    if a_rate is not None:
                        evidence_text = f"'{wf.name}' has this; avg run score {a_rate:.0%}"
                    else:
                        evidence_text = f"'{wf.name}' has this pattern"
                else:
                    evidence_text = f"'{wf.name}' adopted this (too few runs to measure effect)"
            else:
                evidence_text = f"'{wf.name}' has this pattern"

            # Consensus boost
            consensus_n = pattern_consensus.get(pat, 0)
            if consensus_n > 0:
                evidence_text += f"; {consensus_n + 1} workflow(s) total use it"

            # Outcome-weighted similarity: base score + evidence boost
            weighted = score
            if ae and ae["verdict"] == "improved":
                weighted = min(1.0, weighted + 0.15)
            elif ae and ae["verdict"] == "unknown" and ae.get("from_quality"):
                weighted = weighted + 0.05

            g["_evidence_text"] = evidence_text
            g["_weighted_score"] = round(weighted, 4)

        candidates.append({
            "id": wf.id,
            "name": wf.name,
            "nodes": wf_nodes,
            "edges": wf_edges,
            "score": score,
            "info": cand_info,
            "gaps": gaps,
            "gap_patterns": [g["pattern"] for g in gaps],
            "evidence": ev,
        })

    # Sort by weighted score descending, take top_k
    candidates.sort(key=lambda c: max((g["_weighted_score"] for g in c["gaps"]), default=0), reverse=True)
    top_candidates = candidates[:top_k]

    if not top_candidates:
        return []

    # Try LLM enrichment for the top 3
    llm_suggestions = enrich_with_llm(
        target_info, target_nodes, target_edges, top_candidates,
        [g for c in top_candidates for g in c["gaps"]],
    )

    # Build final suggestion list
    suggestions = []
    seen_patterns: set[str] = set()

    if llm_suggestions:
        for sugg in llm_suggestions:
            pat = sugg.get("pattern", "")
            if pat not in seen_patterns:
                seen_patterns.add(pat)
                suggestions.append(_finalize_suggestion(
                    workflow_id, top_candidates[0], sugg
                ))
    else:
        # Fallback: use weighted structural suggestions with evidence
        for cand in top_candidates:
            for gap in cand["gaps"]:
                pat = gap["pattern"]
                if pat not in seen_patterns:
                    seen_patterns.add(pat)
                    suggestions.append(_finalize_suggestion(
                        workflow_id, cand, gap, "structural",
                        gap.get("_evidence_text"),
                    ))

    def _sort_key(s):
        ws = (s.get("evidence") or {}).get("weighted_score")
        return -ws if ws is not None else -s["similarity_score"]

    suggestions.sort(key=_sort_key)
    return suggestions[:top_k * 2]  # up to 2 suggestions per candidate


def _finalize_suggestion(
    workflow_id: str,
    candidate: dict[str, Any],
    gap: dict[str, Any],
    origin: str = "structural",
    evidence_text: str | None = None,
) -> dict[str, Any]:
    """Build the final suggestion dict with a stable ID."""
    import uuid
    ev: dict[str, Any] = {}
    if evidence_text:
        ev = {"text": evidence_text, "verdict": "unknown", "weighted_score": gap.get("_weighted_score", candidate["score"])}
    return {
        "id": f"sugg_{uuid.uuid4().hex[:8]}",
        "workflow_id": workflow_id,
        "source_workflow_id": candidate["id"],
        "source_workflow_name": candidate["name"],
        "similarity_score": candidate["score"],
        "pattern": gap["pattern"],
        "pattern_label": gap["pattern_label"],
        "description": gap["description"],
        "suggestion": gap["suggestion"],
        "target_node_id": gap.get("target_node_id"),
        "actionable": True,
        "apply_patch": gap.get("apply_patch", {}),
        "origin": origin,
        "evidence": ev or None,
    }
