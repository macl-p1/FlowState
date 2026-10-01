"""Workflow Compiler — converts validated Workflow JSON into executable LangGraph."""

import json
import uuid
from contextvars import ContextVar
from typing import Any, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.schemas.workflow import Workflow
from app.schemas.execution import ExecutionStatus, StepStatus, StepExecution
from app.utils.safe_eval import safe_eval, SafeEvalError
from app.tools.registry import registry
from datetime import datetime
import uuid


# Set by the runner so it learns which node is executing (for live progress); None when unused.
node_start_hook: ContextVar[Callable[[str, str], None] | None] = ContextVar("node_start_hook", default=None)


class CompilationError(Exception):
    """Raised when workflow cannot be compiled."""
    pass


class CompiledWorkflow:
    """Wrapper around a compiled LangGraph StateGraph."""

    def __init__(self, graph: StateGraph, node_order: list[str], node_defs: dict[str, dict] | None = None):
        self.graph = graph
        self.node_order = node_order
        self.node_defs = node_defs or {}
        self._compiled = None

    def get_compiled(self):
        if self._compiled is None:
            self._compiled = self.graph.compile(checkpointer=MemorySaver())
        return self._compiled

    def get_node(self, node_id: str) -> dict | None:
        """Get node definition by ID."""
        return self.node_defs.get(node_id)


def _make_node_executor(node: dict, tool_registry):
    """Create an async node executor function for LangGraph."""
    node_type = node.get("type")
    node_id = node.get("id")
    node_name = node.get("name", node_id)

    async def execute(state: dict) -> dict:
        """Execute a single workflow node."""
        hook = node_start_hook.get()
        if hook:
            hook(node_id, node_name)
        steps = state.get("steps", [])
        context = state.get("context", {})

        if node_type == "trigger":
            # Trigger nodes just pass through
            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=state.get("execution_id", ""),
                node_id=node_id,
                node_type=node_type,
                node_name=node_name,
                status=StepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            steps.append(step.model_dump())
            return {**state, "steps": steps, "current_node": node_id}

        elif node_type == "action":
            tool_name = node.get("tool")
            if not tool_name:
                step = StepExecution(
                    id=str(uuid.uuid4()),
                    execution_id=state.get("execution_id", ""),
                    node_id=node_id,
                    node_type=node_type,
                    node_name=node_name,
                    status=StepStatus.FAILED,
                    error="Action node missing 'tool' field",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )
                steps.append(step.model_dump())
                return {
                    **state,
                    "steps": steps,
                    "current_node": node_id,
                    "error": "Action node missing 'tool' field",
                    "status": ExecutionStatus.FAILED,
                }

            # Resolve inputs with context substitution
            raw_inputs = dict(node.get("inputs", {}))

            # Fill defaults from tool schema for any missing required fields
            tool_def = tool_registry.get(tool_name)
            if tool_def and tool_def.input_schema:
                props = tool_def.input_schema.get("properties", {})
                required_fields = set(tool_def.input_schema.get("required", []))
                for field in required_fields:
                    if field not in raw_inputs:
                        field_schema = props.get(field, {})
                        default_val = field_schema.get("default")
                        if default_val is not None:
                            raw_inputs[field] = default_val
                        elif field_schema.get("type") == "string":
                            raw_inputs[field] = f"{{{{default_{field}}}}}"

            resolved_inputs = {}
            for key, value in raw_inputs.items():
                if isinstance(value, str) and "{{" in value:
                    # Simple template substitution
                    resolved = value
                    for ctx_key, ctx_val in context.items():
                        resolved = resolved.replace(f"{{{{{ctx_key}}}}}", str(ctx_val))
                    resolved_inputs[key] = resolved
                else:
                    resolved_inputs[key] = value

            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=state.get("execution_id", ""),
                node_id=node_id,
                node_type=node_type,
                node_name=node_name,
                status=StepStatus.RUNNING,
                tool_name=tool_name,
                tool_inputs=resolved_inputs,
                started_at=datetime.utcnow(),
            )
            step = step.model_dump()
            steps.append(step)

            # Check if this is a human approval tool
            if tool_name == "request_human_approval":
                step["status"] = StepStatus.WAITING_APPROVAL
                return {
                    **state,
                    "steps": steps,
                    "current_node": node_id,
                    "status": ExecutionStatus.WAITING_APPROVAL,
                    "pending_approval": {
                        "node_id": node_id,
                        "reason": node.get("reason", resolved_inputs.get("reason", "Approval required")),
                        "context": resolved_inputs,
                    },
                }

            # Execute the tool
            try:
                result = await tool_registry.execute(tool_name, resolved_inputs)
                step["tool_result"] = result.model_dump()
                step["error"] = result.error
                step["status"] = StepStatus.COMPLETED if result.success else StepStatus.FAILED
                step["completed_at"] = datetime.utcnow()

                # Store outputs in context for downstream nodes
                if result.output:
                    for key, val in result.output.items():
                        context[key] = val

                return {
                    **state,
                    "steps": steps,
                    "current_node": node_id,
                    "context": context,
                    "last_tool_result": result.model_dump(),
                }
            except Exception as e:
                step["status"] = StepStatus.FAILED
                step["error"] = str(e)
                step["completed_at"] = datetime.utcnow()
                return {
                    **state,
                    "steps": steps,
                    "current_node": node_id,
                    "error": str(e),
                    "status": ExecutionStatus.FAILED,
                }

        elif node_type == "condition":
            expression = node.get("expression", "")
            try:
                # Evaluate expression safely (no eval, whitelisted operators only)
                result = safe_eval(expression, context)
                branch = "true" if result else "false"
            except SafeEvalError:
                branch = "true"  # Default to true branch on invalid expression
            except Exception:
                branch = "true"  # Default to true branch on error

            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=state.get("execution_id", ""),
                node_id=node_id,
                node_type=node_type,
                node_name=node_name,
                status=StepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            steps.append(step.model_dump())
            return {**state, "steps": steps, "current_node": node_id, "condition_result": branch}

        elif node_type == "wait":
            duration = node.get("duration_seconds", 1)
            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=state.get("execution_id", ""),
                node_id=node_id,
                node_type=node_type,
                node_name=node_name,
                status=StepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            steps.append(step.model_dump())
            return {**state, "steps": steps, "current_node": node_id}

        elif node_type == "end":
            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=state.get("execution_id", ""),
                node_id=node_id,
                node_type=node_type,
                node_name=node_name,
                status=StepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            steps.append(step.model_dump())
            return {**state, "steps": steps, "current_node": node_id, "status": ExecutionStatus.COMPLETED}

        elif node_type == "approval":
            # Pause workflow and request human approval
            reason = node.get("reason", f"Approval required at {node_name}")
            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=state.get("execution_id", ""),
                node_id=node_id,
                node_type=node_type,
                node_name=node_name,
                status=StepStatus.WAITING_APPROVAL,
                started_at=datetime.utcnow(),
            )
            steps.append(step.model_dump())
            return {
                **state,
                "steps": steps,
                "current_node": node_id,
                "status": ExecutionStatus.WAITING_APPROVAL,
                "pending_approval": {
                    "node_id": node_id,
                    "reason": reason,
                    "context": context,
                },
            }

        # Unknown node type — pass through
        return {**state, "current_node": node_id}

    return execute


class WorkflowCompiler:
    """Compiles a validated Workflow into an executable LangGraph StateGraph."""

    def __init__(self, tool_registry=None):
        self.registry = tool_registry or registry

    def compile(self, workflow: Workflow) -> CompiledWorkflow:
        """
        Convert a Workflow into an executable LangGraph.

        Returns a CompiledWorkflow with the graph ready for execution.
        """
        nodes = workflow.nodes
        edges = workflow.edges

        if not nodes:
            raise CompilationError("Workflow has no nodes")

        # Validate trigger
        trigger_nodes = [n for n in nodes if n.get("type") == "trigger"]
        if len(trigger_nodes) == 0:
            raise CompilationError("Workflow must have a trigger node")
        if len(trigger_nodes) > 1:
            raise CompilationError("Workflow must have exactly one trigger node")

        # Build node lookup (store definitions for get_node)
        node_map = {n["id"]: n for n in nodes}

        # Build edge lookup: from -> [(to, condition)]
        edge_map: dict[str, list[tuple[str, str | None]]] = {}
        for edge in edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            condition = edge.get("condition")
            if from_id not in edge_map:
                edge_map[from_id] = []
            edge_map[from_id].append((to_id, condition))

        # Create the state graph
        builder = StateGraph(dict)

        # Add nodes
        node_order = []
        for node in nodes:
            node_id = node["id"]
            node_order.append(node_id)
            executor = _make_node_executor(node, self.registry)
            builder.add_node(node_id, executor)

        # Set entry point
        trigger_id = trigger_nodes[0]["id"]
        builder.set_entry_point(trigger_id)

        # Add edges
        for node in nodes:
            node_id = node["id"]
            node_type = node.get("type")

            if node_type == "end":
                builder.add_edge(node_id, END)
                continue

            # Approval nodes pause the graph — no outgoing edges wired here
            if node_type == "approval":
                continue

            outgoing = edge_map.get(node_id, [])
            if not outgoing:
                # Dead end — add edge to END with failure implication
                continue

            if node_type == "condition":
                # Condition nodes have conditional edges
                true_targets = [t for t, c in outgoing if c == "true"]
                false_targets = [t for t, c in outgoing if c == "false"]
                default_targets = [t for t, c in outgoing if c is None]

                if true_targets:
                    builder.add_conditional_edges(
                        node_id,
                        lambda state: state.get("condition_result", "true"),
                        {"true": true_targets[0], "false": false_targets[0] if false_targets else (default_targets[0] if default_targets else END)},
                    )
                elif default_targets:
                    builder.add_edge(node_id, default_targets[0])
            else:
                # Sequential edges — take first non-conditional
                targets = [t for t, c in outgoing if c is None]
                if targets:
                    builder.add_edge(node_id, targets[0])

        return CompiledWorkflow(graph=builder, node_order=node_order, node_defs=node_map)
