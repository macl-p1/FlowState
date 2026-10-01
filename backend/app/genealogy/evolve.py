"""Evolution engine: mutate a workflow, test variants in a sandbox, breed the best, keep improvements.

A variant's genome is a list of operations (patches) applied to the baseline graph.
Generation 0 tries every single-op genome; later generations cross survivors (union of
their ops) and extend them with one fresh op. Fitness = sandbox success rate minus a
small parsimony penalty so simpler variants win ties.
"""

import random
from itertools import combinations
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.engine.runner import WorkflowRunner
from app.genealogy.cross_pollination import apply_patch_to_workflow, get_suggestions
from app.models import WorkflowModel
from app.schemas.execution import ExecutionStatus
from app.tools.registry import ToolRegistry

PARSIMONY = 0.01  # fitness penalty per operation in a genome


class SandboxRegistry(ToolRegistry):
    """Always uses mock tool implementations, never real integrations."""

    def _get_custom_tool_by_name(self, name: str) -> Any:
        return None


def _sandbox_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


async def fitness(name: str, nodes: list[dict], edges: list[dict], trials: int = 3) -> float:
    """Success rate over `trials` sandbox runs; runs needing a human or failing score 0."""
    db = _sandbox_db()
    try:
        db.add(WorkflowModel(id="sandbox", name=name, description="", nodes=nodes, edges=edges))
        db.commit()
        runner = WorkflowRunner(db, tool_registry=SandboxRegistry(), evaluate=False)
        ok = 0
        for _ in range(trials):
            try:
                ok += (await runner.run("sandbox")).status == ExecutionStatus.COMPLETED
            except Exception:  # compile/run errors are just a failed trial
                pass
        return ok / trials
    finally:
        db.close()


def _remove_node(nodes: list[dict], edges: list[dict], node_id: str) -> tuple[list[dict], list[dict]]:
    """Delete a node and bridge each incoming edge to each outgoing target."""
    ins = [e for e in edges if e["to"] == node_id]
    outs = [e for e in edges if e["from"] == node_id]
    keep = [e for e in edges if node_id not in (e["from"], e["to"])]
    bridged = [
        {**o, "from": i["from"], **({"condition": i["condition"]} if i.get("condition") else {})}
        for i in ins for o in outs
    ]
    return [n for n in nodes if n["id"] != node_id], keep + bridged


def apply_ops(nodes: list[dict], edges: list[dict], ops: list[dict]) -> tuple[list[dict], list[dict]]:
    for op in ops:
        if op["type"] == "remove_node":
            nodes, edges = _remove_node(nodes, edges, op["node_id"])
        else:
            nodes, edges = apply_patch_to_workflow(nodes, edges, op)
    return nodes, edges


def candidate_ops(db, wf: WorkflowModel, allow_gate_removal: bool) -> list[dict]:
    """Single mutations: cross-pollination patches, retry bumps, and (opt-in) approval-gate removal."""
    out = []
    for s in get_suggestions(db, wf.id):
        if s.get("apply_patch"):
            out.append({"desc": s["suggestion"], "op": s["apply_patch"]})
    for n in wf.nodes or []:
        if n.get("type") == "action" and n.get("retry_count", 0) < 3:
            out.append({"desc": f"retry_count=3 on {n['id']}",
                        "op": {"type": "update_node", "node_id": n["id"], "field": "retry_count", "value": 3}})
        # Removing a human approval gate is a safety change, so it is only offered when explicitly allowed.
        if allow_gate_removal and n.get("type") == "approval":
            out.append({"desc": f"remove approval gate '{n.get('name', n['id'])}'",
                        "op": {"type": "remove_node", "node_id": n["id"]}})
    return out


async def evolve(
    db,
    wf: WorkflowModel,
    trials: int = 3,
    generations: int = 1,
    allow_gate_removal: bool = False,
    seed: int = 0,
    keep: int = 3,
) -> dict:
    """Run `generations` rounds; return every scored variant best-first plus the winner (if it beats baseline)."""
    rng = random.Random(seed)
    nodes0, edges0 = wf.nodes or [], wf.edges or []
    base = await fitness(wf.name, nodes0, edges0, trials)
    pool = candidate_ops(db, wf, allow_gate_removal)
    scored: dict[tuple, dict] = {}

    async def score(genome: list[dict], generation: int) -> None:
        key = tuple(g["desc"] for g in genome)
        if key in scored:
            return
        try:
            n, e = apply_ops(nodes0, edges0, [g["op"] for g in genome])
        except Exception:
            return
        f = await fitness(wf.name, n, e, trials)
        scored[key] = {
            "description": " + ".join(key), "fitness": f, "adjusted": f - PARSIMONY * len(genome),
            "generation": generation, "ops": len(genome), "genome": genome, "nodes": n, "edges": e,
            "removes_approval": any(g["op"]["type"] == "remove_node" for g in genome),
        }

    for g in pool:
        await score([g], 0)
    for gen in range(1, max(1, generations)):
        survivors = [v["genome"] for v in sorted(scored.values(), key=lambda v: v["adjusted"], reverse=True)[:keep]]
        children = [a + [x for x in b if x not in a] for a, b in combinations(survivors, 2)]  # crossover
        for s in survivors:  # mutation: extend with one unused op
            unused = [g for g in pool if g not in s]
            if unused:
                children.append(s + [rng.choice(unused)])
        for c in children:
            await score(c, gen)

    variants = sorted(scored.values(), key=lambda v: v["adjusted"], reverse=True)
    for v in variants:
        del v["genome"]
    winner = variants[0] if variants and variants[0]["fitness"] > base else None
    return {"baseline": base, "generations": max(1, generations), "variants": variants, "winner": winner}
