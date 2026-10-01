"""Durable run queue, trigger scheduler and worker.

Runs are PENDING rows in the database (so they survive restarts). One worker loop per database:
fires due schedule triggers, then starts pending runs up to `max_concurrent_runs`, each under a timeout.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.agents.compiler import WorkflowCompiler
from app.config import settings
from app.engine.runner import WorkflowRunner
from app.models import WorkflowModel, WorkflowExecutionModel
from app.models.triggers import TriggerModel, RunMetaModel
from app.schemas.execution import ExecutionStatus
from app.schemas.workflow import Workflow
from app.tools.registry import registry

log = logging.getLogger(__name__)

_LIVE = (ExecutionStatus.PENDING, ExecutionStatus.RUNNING, ExecutionStatus.RETRYING)


class WorkflowInvalid(Exception):
    """The workflow (or snapshot) does not validate/compile, so a run could never start."""


# ── cron ──────────────────────────────────────────────

def _cron_field(spec: str, lo: int, hi: int) -> set[int]:
    out: set[int] = set()
    for part in spec.split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            step = int(s)
        if part in ("*", ""):
            a, b = lo, hi
        elif "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
        else:
            a = b = int(part)
            if "/" in spec and step != 1:  # "5/10" means from 5 to the end, every 10
                b = hi
        if a < lo or b > hi or a > b or step < 1:
            raise ValueError(f"cron field out of range: {spec}")
        out.update(range(a, b + 1, step))
    return out


def parse_cron(expr: str):
    """5-field cron (min hour dom month dow, UTC). Returns (sets, dom_restricted, dow_restricted)."""
    f = expr.split()
    if len(f) != 5:
        raise ValueError("cron needs 5 fields: minute hour day-of-month month day-of-week")
    mins, hours, doms, months = (_cron_field(f[0], 0, 59), _cron_field(f[1], 0, 23),
                                 _cron_field(f[2], 1, 31), _cron_field(f[3], 1, 12))
    dows = {d % 7 for d in _cron_field(f[4], 0, 7)}  # 0 and 7 are both Sunday
    return (mins, hours, doms, months, dows), f[2] != "*", f[4] != "*"


def cron_next(expr: str, after: datetime) -> datetime:
    """Next matching minute strictly after `after`. Minute-stepping scan, bounded to ~1 year."""
    (mins, hours, doms, months, dows), dom_r, dow_r = parse_cron(expr)
    t = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    for _ in range(366 * 24 * 60):
        dow = (t.weekday() + 1) % 7  # python Monday=0 -> cron Sunday=0
        if dom_r and dow_r:  # standard cron: either day field may match
            day_ok = t.day in doms or dow in dows
        else:
            day_ok = t.day in doms and dow in dows
        if t.month in months and day_ok and t.hour in hours and t.minute in mins:
            return t
        t += timedelta(minutes=1)
    raise ValueError(f"cron '{expr}' never fires")


def next_fire(config: dict, after: datetime) -> datetime:
    if config.get("cron"):
        return cron_next(config["cron"], after)
    return after + timedelta(seconds=int(config["interval_seconds"]))


# ── queue ─────────────────────────────────────────────

def enqueue_run(
    db: Session,
    workflow_id: str,
    context: dict | None = None,
    source: str = "manual",
    trigger_id: str | None = None,
    replay_of: str | None = None,
    snapshot: dict | None = None,
) -> str:
    """Create a PENDING run (validated up front) and return its id. The worker starts it."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise LookupError(f"Workflow {workflow_id} not found")
    graph = snapshot or {"nodes": wf.nodes, "edges": wf.edges}
    try:
        WorkflowCompiler(tool_registry=registry).compile(Workflow.model_validate({
            "name": wf.name, "description": wf.description or "",
            "nodes": graph["nodes"], "edges": graph["edges"], "metadata": wf.wf_metadata or {},
        }))
    except Exception as e:
        raise WorkflowInvalid(str(e)) from e

    ctx = context or {}
    exec_id = f"exec_{uuid.uuid4().hex[:8]}"
    db.add(WorkflowExecutionModel(
        id=exec_id, workflow_id=workflow_id, workflow_name=wf.name,
        status=ExecutionStatus.PENDING, context=ctx, started_at=datetime.utcnow(),
    ))
    db.add(RunMetaModel(
        execution_id=exec_id, source=source, trigger_id=trigger_id, replay_of=replay_of,
        input_context=ctx, snapshot=graph,
    ))
    db.commit()
    return exec_id


def recover_interrupted(bind) -> int:
    """After a restart, runs that were mid-flight can't continue: fail them so they can be replayed."""
    with Session(bind) as db:
        rows = db.query(WorkflowExecutionModel).filter(
            WorkflowExecutionModel.status.in_((ExecutionStatus.RUNNING, ExecutionStatus.RETRYING))
        ).all()
        for r in rows:
            r.status = ExecutionStatus.FAILED
            r.error_message = "Interrupted by server restart (replay to run it again)"
            r.completed_at = datetime.utcnow()
        db.commit()
        return len(rows)


# ── worker ────────────────────────────────────────────

class Worker:
    # ponytail: single-process; running several API processes needs a row-level claim on PENDING runs
    def __init__(self, bind):
        self.bind = bind
        self.active: dict[str, asyncio.Task] = {}
        self._loop = None
        self._task: asyncio.Task | None = None

    def kick(self) -> None:
        """Make sure the background loop is running on the current event loop."""
        loop = asyncio.get_running_loop()
        if self._task is None or self._task.done() or self._loop is not loop:
            if self._loop is not loop:
                self.active = {}  # tasks of a previous (dead) loop
            self._loop = loop
            self._task = loop.create_task(self._forever())

    async def _forever(self) -> None:
        while True:
            try:
                await self.tick()
            except Exception:
                log.exception("worker tick failed")
            await asyncio.sleep(settings.scheduler_poll_seconds)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
        for t in list(self.active.values()):
            t.cancel()
        await asyncio.gather(*self.active.values(), return_exceptions=True)

    async def tick(self) -> None:
        self._fire_due_triggers()
        self._dispatch()

    async def drain(self) -> None:
        """Wait for in-flight runs (tests, graceful shutdown)."""
        while self.active:
            await asyncio.gather(*list(self.active.values()), return_exceptions=True)
            await asyncio.sleep(0)

    def cancel(self, execution_id: str) -> bool:
        task = self.active.get(execution_id)
        if task:
            task.cancel()
            # Record it now: a task cancelled before its first step never runs its own cleanup.
            self._finish(execution_id, ExecutionStatus.CANCELLED, "Cancelled")
        return task is not None

    def _fire_due_triggers(self) -> None:
        now = datetime.utcnow()
        with Session(self.bind) as db:
            due = db.query(TriggerModel).filter(
                TriggerModel.kind == "schedule", TriggerModel.enabled.is_(True), TriggerModel.next_run_at <= now,
            ).all()
            for t in due:
                # Missed fires collapse into one run; the next fire is computed from now.
                t.last_run_at, t.next_run_at = now, next_fire(t.config or {}, now)
                try:
                    enqueue_run(db, t.workflow_id, (t.config or {}).get("context"), "schedule", trigger_id=t.id)
                    t.config = {k: v for k, v in (t.config or {}).items() if k != "last_error"}
                except Exception as e:  # deleted/broken workflow: keep the trigger, record why
                    t.config = {**(t.config or {}), "last_error": str(e)}
            db.commit()

    def _dispatch(self) -> None:
        free = settings.max_concurrent_runs - len(self.active)
        if free <= 0:
            return
        with Session(self.bind) as db:
            ids = [
                r[0] for r in db.query(WorkflowExecutionModel.id)
                .join(RunMetaModel, RunMetaModel.execution_id == WorkflowExecutionModel.id)
                .filter(WorkflowExecutionModel.status == ExecutionStatus.PENDING)
                .order_by(RunMetaModel.created_at)
                .limit(free + len(self.active)).all()
            ]
        for eid in [i for i in ids if i not in self.active][:free]:
            task = asyncio.get_running_loop().create_task(self._execute(eid))
            task.add_done_callback(lambda _t, eid=eid: self.active.pop(eid, None))
            self.active[eid] = task

    async def _execute(self, eid: str) -> None:
        try:
            with Session(self.bind) as db:
                ex, meta = db.get(WorkflowExecutionModel, eid), db.get(RunMetaModel, eid)
                if not ex or ex.status != ExecutionStatus.PENDING:
                    return  # cancelled while queued
                wid, ctx, graph = ex.workflow_id, dict(meta.input_context or {}), meta.snapshot
            with Session(self.bind) as db:
                await asyncio.wait_for(
                    WorkflowRunner(db=db, tool_registry=registry).run(wid, ctx, execution_id=eid, graph=graph),
                    timeout=settings.run_timeout_seconds,
                )
        except asyncio.TimeoutError:
            self._finish(eid, ExecutionStatus.FAILED, f"Timed out after {settings.run_timeout_seconds}s")
        except asyncio.CancelledError:
            self._finish(eid, ExecutionStatus.CANCELLED, "Cancelled")
        except Exception as e:  # the runner already recorded run failures; this covers setup errors
            self._finish(eid, ExecutionStatus.FAILED, str(e))
        finally:
            self.active.pop(eid, None)

    def _finish(self, eid: str, status: ExecutionStatus, message: str) -> None:
        with Session(self.bind) as db:
            ex = db.get(WorkflowExecutionModel, eid)
            if ex and ex.status in _LIVE:
                ex.status, ex.error_message, ex.completed_at = status, message, datetime.utcnow()
                db.commit()


_workers: dict[int, Worker] = {}


def get_worker(bind) -> Worker:
    """One worker per database engine."""
    return _workers.setdefault(id(bind), Worker(bind))
