"""Diff engine — compares two workflow graphs and produces a structured change report."""

import hashlib
import json
from typing import Any

# Canvas layout is not a workflow change: moving a node must not create a version.
LAYOUT_KEYS = frozenset({"position"})


def graph_key(nodes: list[dict], edges: list[dict]) -> str:
    """Stable fingerprint of a workflow graph, ignoring layout and ordering."""
    canon_nodes = sorted(
        ({k: v for k, v in n.items() if k not in LAYOUT_KEYS} for n in nodes or []),
        key=lambda n: str(n.get("id")),
    )
    canon_edges = sorted((e.get("from"), e.get("to"), e.get("condition") or None) for e in edges or [])
    blob = json.dumps([canon_nodes, canon_edges], sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


class DiffResult:
    """Structured result of comparing two workflow graphs."""

    def __init__(self):
        self.added_nodes: list[dict] = []
        self.removed_nodes: list[dict] = []
        self.modified_nodes: list[dict] = []  # {id, changes: {field: {old, new}}}
        self.added_edges: list[dict] = []
        self.removed_edges: list[dict] = []

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added_nodes or self.removed_nodes or self.modified_nodes
            or self.added_edges or self.removed_edges
        )

    def to_dict(self) -> dict:
        return {
            "added_nodes": self.added_nodes,
            "removed_nodes": self.removed_nodes,
            "modified_nodes": self.modified_nodes,
            "added_edges": self.added_edges,
            "removed_edges": self.removed_edges,
        }

    def summary(self) -> str:
        """Human-readable summary of changes."""
        parts = []
        if self.added_nodes:
            names = [n.get("name", n.get("id", "?")) for n in self.added_nodes]
            parts.append(f"added {len(names)} node(s): {', '.join(names)}")
        if self.removed_nodes:
            names = [n.get("name", n.get("id", "?")) for n in self.removed_nodes]
            parts.append(f"removed {len(names)} node(s): {', '.join(names)}")
        if self.modified_nodes:
            names = [m["id"] for m in self.modified_nodes]
            parts.append(f"modified {len(names)} node(s): {', '.join(names)}")
        if self.added_edges:
            parts.append(f"added {len(self.added_edges)} edge(s)")
        if self.removed_edges:
            parts.append(f"removed {len(self.removed_edges)} edge(s)")
        if not parts:
            return "no changes"
        return "; ".join(parts)


def compute_diff(
    old_nodes: list[dict],
    old_edges: list[dict],
    new_nodes: list[dict],
    new_edges: list[dict],
) -> DiffResult:
    """
    Compare two workflow graphs and return structured diff.

    Node comparison: by ID. If a node exists in both, compare fields.
    Edge comparison: by (from, to, condition) tuple.
    """
    result = DiffResult()

    old_node_map = {n["id"]: n for n in old_nodes if "id" in n}
    new_node_map = {n["id"]: n for n in new_nodes if "id" in n}

    # Nodes: added, removed, modified
    for node_id in sorted(new_node_map.keys() - old_node_map.keys()):
        result.added_nodes.append(new_node_map[node_id])

    for node_id in sorted(old_node_map.keys() - new_node_map.keys()):
        result.removed_nodes.append(old_node_map[node_id])

    # Modified nodes: every field except layout
    for node_id in sorted(old_node_map.keys() & new_node_map.keys()):
        old_node = old_node_map[node_id]
        new_node = new_node_map[node_id]
        changes = {}

        all_keys = set(old_node.keys()) | set(new_node.keys())
        for key in all_keys:
            if key == "id" or key in LAYOUT_KEYS:
                continue
            old_val = old_node.get(key)
            new_val = new_node.get(key)
            if old_val != new_val:
                changes[key] = {"old": _serialize(old_val), "new": _serialize(new_val)}

        if changes:
            result.modified_nodes.append({"id": node_id, "changes": changes})

    # Edges: compare as (from, to, condition) tuples
    old_edge_set = {
        (e.get("from"), e.get("to"), _edge_condition_key(e))
        for e in old_edges
    }
    new_edge_set = {
        (e.get("from"), e.get("to"), _edge_condition_key(e))
        for e in new_edges
    }

    for edge_tuple in sorted(new_edge_set - old_edge_set):
        result.added_edges.append({"from": edge_tuple[0], "to": edge_tuple[1], "condition": edge_tuple[2]})

    for edge_tuple in sorted(old_edge_set - new_edge_set):
        result.removed_edges.append({"from": edge_tuple[0], "to": edge_tuple[1], "condition": edge_tuple[2]})

    return result


def _edge_condition_key(edge: dict) -> str | None:
    """Normalize edge condition for comparison."""
    cond = edge.get("condition")
    return cond if cond else None


def _serialize(value: Any) -> Any:
    """Make a value JSON-safe for comparison output."""
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, (list, dict)):
        return value
    return str(value)
