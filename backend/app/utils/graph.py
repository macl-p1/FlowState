"""Normalize workflow graphs that were stored in React Flow's canvas shape.

Older builder versions saved canvas objects ({type: "flowNode", data: {...}}, edges with source/target).
Nothing downstream understands that shape: the compiler can't run it and pattern mining sees no
actions/tools, so suggestions come back empty. Convert it to the backend shape on save and once at startup.
"""

from typing import Any

from sqlalchemy.orm import Session

# Builder palette display names -> tool registry names (mirrors frontend resolveToolName)
DISPLAY_TO_TOOL = {
    "HTTP Request": "http",
    "Database Query": "database",
    "Send Email": "send_email",
    "Webhook": "webhook",
    "Wait / Delay": "delay",
    "Transform": "transform",
}
_CANVAS_ONLY_EDGE_KEYS = {"id", "source", "target", "animated", "style", "type", "label",
                          "deletable", "selectable", "sourceHandle", "targetHandle", "markerEnd"}


def _tool(raw: str | None) -> str | None:
    if not raw:
        return None
    return DISPLAY_TO_TOOL.get(raw, raw.lower().replace(" ", "_"))


def _node(n: dict) -> dict:
    if n.get("type") != "flowNode" or not isinstance(n.get("data"), dict):
        return n
    d = n["data"]
    raw = d.get("raw") if isinstance(d.get("raw"), dict) else {}
    kind = d.get("nodeType") or raw.get("type") or "action"
    out: dict[str, Any] = {**raw, "id": n["id"], "type": kind, "name": d.get("name") or raw.get("name") or n["id"]}
    if kind == "action":  # the old builder put a default "HTTP Request" tool on every node; only actions have tools
        tool = _tool(d.get("tool") or raw.get("tool"))
        if tool:
            out["tool"] = tool
    else:
        out.pop("tool", None)
    detail = d.get("detail")
    if detail and not str(detail).startswith("Tool:"):  # "Tool: x" was generated filler, not user text
        out["detail"] = detail
    if "position" in n:
        out["position"] = n["position"]
    return out


def _edge(e: dict) -> dict:
    if "from" in e and "to" in e:
        return e
    out = {k: v for k, v in e.items() if k not in _CANVAS_ONLY_EDGE_KEYS}
    out["from"], out["to"] = e.get("source"), e.get("target")
    if e.get("label"):
        out["condition"] = str(e["label"])
    return out


def is_canvas_shaped(nodes: list[dict] | None, edges: list[dict] | None) -> bool:
    return any(n.get("type") == "flowNode" for n in nodes or []) or any(
        "source" in e and "from" not in e for e in edges or []
    )


def normalize_graph(nodes: list[dict] | None, edges: list[dict] | None) -> tuple[list[dict], list[dict]]:
    return [_node(n) for n in nodes or []], [_edge(e) for e in edges or []]


def normalize_stored_graphs(bind) -> int:
    """One-time, idempotent: convert canvas-shaped workflows and versions in the database. Returns rows fixed."""
    from app.models import WorkflowModel, WorkflowVersionModel

    fixed = 0
    with Session(bind) as db:
        for model in (WorkflowModel, WorkflowVersionModel):
            for row in db.query(model).all():
                if is_canvas_shaped(row.nodes, row.edges):
                    row.nodes, row.edges = normalize_graph(row.nodes, row.edges)
                    fixed += 1
        db.commit()
    return fixed
