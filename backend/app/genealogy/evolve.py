"""Evolution engine: mutate a workflow, test variants in a sandbox, keep improvements."""

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
        runner = WorkflowRunner(db, tool_registry=SandboxRegistry())
        ok = 0
        for _ in range(trials):
            try:
                ok += (await runner.run("sandbox")).status == ExecutionStatus.COMPLETED
            except Exception:  # compile/run errors are just a failed trial
                pass
        return ok / trials
    finally:
        db.close()


def mutations(db, wf: WorkflowModel) -> list[tuple[str, list[dict], list[dict]]]:
    """Candidate variants: cross-pollination patches plus a retry bump per action node."""
    nodes, edges = wf.nodes or [], wf.edges or []
    out = []
    for s in get_suggestions(db, wf.id):
        patch = s.get("apply_patch")
        if patch:
            try:
                out.append((s["suggestion"], *apply_patch_to_workflow(nodes, edges, patch)))
            except Exception:
                pass
    for n in nodes:
        if n.get("type") == "action" and n.get("retry_count", 0) < 3:
            out.append((f"retry_count=3 on {n['id']}",
                        [{**m, "retry_count": 3} if m is n else m for m in nodes], edges))
    return out


async def evolve(db, wf: WorkflowModel, trials: int = 3) -> dict:
    """One generation: score baseline and every mutation, return them best-first."""
    # ponytail: single generation, no crossover between variants; loop evolve() on the winner for more
    base = await fitness(wf.name, wf.nodes or [], wf.edges or [], trials)
    variants = []
    for desc, n, e in mutations(db, wf):
        variants.append({"description": desc, "fitness": await fitness(wf.name, n, e, trials),
                         "nodes": n, "edges": e})
    variants.sort(key=lambda v: v["fitness"], reverse=True)
    return {"baseline": base, "variants": variants,
            "winner": variants[0] if variants and variants[0]["fitness"] > base else None}
