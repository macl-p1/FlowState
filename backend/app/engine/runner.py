"""Workflow Runner — execution engine that runs compiled workflows."""

import asyncio
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models import WorkflowModel, WorkflowExecutionModel, StepExecutionModel
from app.schemas.workflow import Workflow
from app.schemas.execution import ExecutionStatus, StepStatus, WorkflowExecution, StepExecution
from app.schemas.tool import ToolResult
from app.agents.compiler import WorkflowCompiler, CompiledWorkflow, CompilationError
from app.tools.registry import registry
from app.approval.service import ApprovalService
from app.utils.safe_eval import safe_eval, SafeEvalError


class WorkflowNotFoundError(Exception):
    pass


class RunnerError(Exception):
    pass


class WorkflowRunner:
    """
    Executes compiled workflows with full observability.
    Manages the execution lifecycle: start → run steps → pause for approval → resume → complete/fail.
    """

    def __init__(self, db: Session, tool_registry=None, evaluate: bool = True):
        self.db = db
        self.evaluate = evaluate
        self.registry = tool_registry or registry
        self.compiler = WorkflowCompiler(tool_registry=self.registry)
        self.approval_service = ApprovalService(db)

    def _create_execution_record(
        self,
        workflow_model: WorkflowModel,
        compiled: CompiledWorkflow,
        context: dict[str, Any] | None = None,
    ) -> WorkflowExecutionModel:
        """Create the initial execution record in the database."""
        execution = WorkflowExecutionModel(
            id=f"exec_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_model.id,
            workflow_name=workflow_model.name,
            status=ExecutionStatus.PENDING,
            context=context or {},
            started_at=datetime.utcnow(),
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    async def run(
        self,
        workflow_id: str,
        context: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow by ID.

        Returns the execution record with all steps.
        """
        # Load workflow
        workflow_model = self.db.query(WorkflowModel).filter(
            WorkflowModel.id == workflow_id
        ).first()
        if not workflow_model:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")

        # Parse workflow
        workflow = Workflow.model_validate({
            "name": workflow_model.name,
            "description": workflow_model.description,
            "nodes": workflow_model.nodes,
            "edges": workflow_model.edges,
            "metadata": workflow_model.wf_metadata or {},
        })

        # Compile
        compiled = self.compiler.compile(workflow)

        # Create execution record
        exec_model = self._create_execution_record(workflow_model, compiled, context)
        exec_model.status = ExecutionStatus.RUNNING
        self.db.commit()

        # Persist steps incrementally during execution
        persisted_count = 0

        def _persist_steps(steps_data: list[dict]) -> None:
            nonlocal persisted_count
            new_steps = steps_data[persisted_count:]
            for step_data in new_steps:
                step_model = StepExecutionModel(
                    execution_id=exec_model.id,
                    node_id=step_data.get("node_id", ""),
                    node_type=step_data.get("node_type", ""),
                    node_name=step_data.get("node_name", ""),
                    status=step_data.get("status", StepStatus.COMPLETED),
                    tool_name=step_data.get("tool_name"),
                    tool_inputs=step_data.get("tool_inputs"),
                    tool_result=step_data.get("tool_result"),
                    attempt_count=step_data.get("attempt_count", 1),
                    error=step_data.get("error"),
                    started_at=step_data.get("started_at"),
                    completed_at=step_data.get("completed_at"),
                )
                self.db.add(step_model)
            persisted_count = len(steps_data)
            self.db.commit()

        try:
            # Execute the graph, streaming state after each node for incremental step persistence
            initial_state = {
                "execution_id": exec_model.id,
                "steps": [],
                "context": context or {},
                "status": ExecutionStatus.RUNNING,
                "current_node": None,
            }

            app = compiled.get_compiled()
            config = {"configurable": {"thread_id": exec_model.id}}
            final_state = initial_state

            async for state in app.astream(initial_state, config=config):
                # state is {node_name: updated_state_dict} — merge all node outputs
                merged: dict[str, Any] = {}
                for node_output in state.values():
                    if isinstance(node_output, dict):
                        merged.update(node_output)

                # Persist any new steps after each node execution
                current_steps = merged.get("steps", [])
                if len(current_steps) > persisted_count:
                    _persist_steps(current_steps)

                final_state = merged if merged else final_state

            # Update execution with final state
            exec_model.status = final_state.get("status", ExecutionStatus.COMPLETED)
            exec_model.current_node_id = final_state.get("current_node")
            exec_model.completed_at = datetime.utcnow()

            if exec_model.status == ExecutionStatus.FAILED:
                exec_model.error_message = final_state.get("error", "Unknown error")

            # Persist any remaining steps not yet saved
            final_steps = final_state.get("steps", [])
            if len(final_steps) > persisted_count:
                _persist_steps(final_steps)

            # Check for approval gate
            pending_approval = final_state.get("pending_approval")
            if pending_approval:
                exec_model.status = ExecutionStatus.WAITING_APPROVAL
                approval = self.approval_service.create_request(
                    workflow_execution_id=exec_model.id,
                    node_id=pending_approval["node_id"],
                    reason=pending_approval["reason"],
                    context=pending_approval.get("context", {}),
                )
            self.db.commit()
            self.db.refresh(exec_model)
            self._evaluate(exec_model.id)

            return self._to_pydantic(exec_model)

        except Exception as e:
            exec_model.status = ExecutionStatus.FAILED
            exec_model.error_message = str(e)
            exec_model.completed_at = datetime.utcnow()
            self.db.commit()
            raise RunnerError(f"Workflow execution failed: {e}") from e

    async def resume(self, execution_id: str) -> WorkflowExecution:
        """
        Resume a workflow that was paused for approval.

        After approval, continue execution from the approval node.
        """
        exec_model = self.db.query(WorkflowExecutionModel).filter(
            WorkflowExecutionModel.id == execution_id
        ).first()
        if not exec_model:
            raise WorkflowNotFoundError(f"Execution {execution_id} not found")

        if exec_model.status != ExecutionStatus.WAITING_APPROVAL:
            raise RunnerError(
                f"Cannot resume execution in status: {exec_model.status}"
            )

        # Load and recompile the workflow
        workflow_model = self.db.query(WorkflowModel).filter(
            WorkflowModel.id == exec_model.workflow_id
        ).first()

        workflow = Workflow.model_validate({
            "name": workflow_model.name,
            "description": workflow_model.description,
            "nodes": workflow_model.nodes,
            "edges": workflow_model.edges,
            "metadata": workflow_model.wf_metadata or {},
        })

        compiled = self.compiler.compile(workflow)

        # Get existing steps
        existing_steps = [
            {
                "id": s.id,
                "execution_id": s.execution_id,
                "node_id": s.node_id,
                "node_type": s.node_type,
                "node_name": s.node_name,
                "status": s.status.value,
                "tool_name": s.tool_name,
                "tool_inputs": s.tool_inputs,
                "tool_result": s.tool_result,
                "attempt_count": s.attempt_count,
                "error": s.error,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in exec_model.steps
        ]

        # Reconstruct state and resume — execute remaining nodes directly
        exec_model.status = ExecutionStatus.RUNNING
        self.db.commit()

        # Find the approval node to resume from
        approval_node_id = exec_model.current_node_id
        nodes = workflow.nodes
        node_map = {n.get("id"): n for n in nodes}
        edges = workflow.edges

        # Find the next node after approval
        next_node_id = None
        for edge in edges:
            if edge.get("from") == approval_node_id:
                next_node_id = edge.get("to")
                break

        if not next_node_id:
            # Approval was the last meaningful node, go to end
            for node in nodes:
                if node.get("type") == "end":
                    next_node_id = node["id"]
                    break

        # Build a state dict from existing steps and context
        resumed_steps = list(existing_steps)
        resumed_context = exec_model.context or {}

        # Execute remaining nodes sequentially from next_node_id
        current_id = next_node_id
        status = ExecutionStatus.RUNNING
        while current_id and current_id != "__end__":
            node = node_map.get(current_id)
            if not node:
                break

            node_type = node.get("type", "")

            if node_type == "end":
                status = ExecutionStatus.COMPLETED
                resumed_steps.append({
                    "id": str(uuid.uuid4()),
                    "execution_id": exec_model.id,
                    "node_id": current_id,
                    "node_type": node_type,
                    "node_name": node.get("name", current_id),
                    "status": StepStatus.COMPLETED,
                    "started_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                })
                break

            elif node_type == "condition":
                expression = node.get("expression", "")
                try:
                    # Evaluate expression safely (no eval, whitelisted operators only)
                    result = safe_eval(expression, resumed_context)
                    branch = "true" if result else "false"
                except SafeEvalError:
                    branch = "true"
                except Exception:
                    branch = "true"

                # Find next node based on branch
                next_candidates = [
                    e.get("to") for e in edges
                    if e.get("from") == current_id and e.get("condition") == branch
                ]
                current_id = next_candidates[0] if next_candidates else None
                continue

            elif node_type == "action":
                tool_name = node.get("tool")
                if tool_name:
                    raw_inputs = node.get("inputs", {})
                    resolved_inputs = {}
                    for key, value in raw_inputs.items():
                        if isinstance(value, str) and "{{" in value:
                            resolved = value
                            for ctx_key, ctx_val in resumed_context.items():
                                resolved = resolved.replace(f"{{{{{ctx_key}}}}}", str(ctx_val))
                            resolved_inputs[key] = resolved
                        else:
                            resolved_inputs[key] = value

                    try:
                        result = await self.registry.execute(tool_name, resolved_inputs)
                        if result.output:
                            resumed_context.update(result.output)
                        step_status = StepStatus.COMPLETED if result.success else StepStatus.FAILED
                        if not result.success:
                            status = ExecutionStatus.FAILED
                    except Exception as e:
                        step_status = StepStatus.FAILED
                        status = ExecutionStatus.FAILED
                        result = None
                else:
                    step_status = StepStatus.COMPLETED
                    result = None

                resumed_steps.append({
                    "id": str(uuid.uuid4()),
                    "execution_id": exec_model.id,
                    "node_id": current_id,
                    "node_type": node_type,
                    "node_name": node.get("name", current_id),
                    "status": step_status.value,
                    "tool_name": tool_name,
                    "tool_inputs": resolved_inputs if tool_name else None,
                    "tool_result": result.model_dump() if result else None,
                    "attempt_count": 1,
                    "started_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                })

                # Find next node
                next_candidates = [e.get("to") for e in edges if e.get("from") == current_id and e.get("condition") is None]
                current_id = next_candidates[0] if next_candidates else None
                continue

            # For other node types, find next
            next_candidates = [e.get("to") for e in edges if e.get("from") == current_id and e.get("condition") is None]
            current_id = next_candidates[0] if next_candidates else None

        # Persist all new steps
        for step_data in resumed_steps[len(existing_steps):]:
            step_model = StepExecutionModel(
                execution_id=exec_model.id,
                node_id=step_data.get("node_id", ""),
                node_type=step_data.get("node_type", ""),
                node_name=step_data.get("node_name", ""),
                status=step_data.get("status", StepStatus.COMPLETED.value),
                tool_name=step_data.get("tool_name"),
                tool_inputs=step_data.get("tool_inputs"),
                tool_result=step_data.get("tool_result"),
                attempt_count=step_data.get("attempt_count", 1),
                error=step_data.get("error"),
                started_at=datetime.fromisoformat(step_data["started_at"]) if step_data.get("started_at") else None,
                completed_at=datetime.fromisoformat(step_data["completed_at"]) if step_data.get("completed_at") else None,
            )
            self.db.add(step_model)

        # Update execution
        exec_model.status = status
        exec_model.current_node_id = None
        exec_model.context = resumed_context
        exec_model.completed_at = datetime.utcnow()
        self.db.commit()
        self._evaluate(exec_model.id)

        return self._to_pydantic(exec_model)

    def _evaluate(self, execution_id: str) -> None:
        """Quality check on completed runs; fail-soft, off for sandbox runners."""
        if self.evaluate:
            from app.agents.evaluator import evaluate_run
            evaluate_run(self.db, execution_id)

    async def cancel(self, execution_id: str) -> WorkflowExecution:
        """Cancel a running workflow."""
        exec_model = self.db.query(WorkflowExecutionModel).filter(
            WorkflowExecutionModel.id == execution_id
        ).first()
        if not exec_model:
            raise WorkflowNotFoundError(f"Execution {execution_id} not found")

        exec_model.status = ExecutionStatus.CANCELLED
        exec_model.completed_at = datetime.utcnow()
        self.db.commit()
        return self._to_pydantic(exec_model)

    def _to_pydantic(self, exec_model: WorkflowExecutionModel) -> WorkflowExecution:
        """Convert ORM model to Pydantic schema."""
        steps = []
        for s in exec_model.steps:
            tool_result = None
            if s.tool_result:
                tool_result = ToolResult(**s.tool_result)
            steps.append(StepExecution(
                id=s.id,
                execution_id=s.execution_id,
                node_id=s.node_id,
                node_type=s.node_type,
                node_name=s.node_name,
                status=StepStatus(s.status),
                tool_name=s.tool_name,
                tool_inputs=s.tool_inputs,
                tool_result=tool_result,
                attempt_count=s.attempt_count,
                error=s.error,
                started_at=s.started_at,
                completed_at=s.completed_at,
            ))

        return WorkflowExecution(
            id=exec_model.id,
            workflow_id=exec_model.workflow_id,
            workflow_name=exec_model.workflow_name,
            status=ExecutionStatus(exec_model.status),
            current_node_id=exec_model.current_node_id,
            context=exec_model.context or {},
            steps=steps,
            started_at=exec_model.started_at,
            completed_at=exec_model.completed_at,
            error_message=exec_model.error_message,
        )
