"""Planner Agent — converts natural language to validated workflow JSON using Claude."""

import json
import re
import uuid
import traceback
from typing import Any
from anthropic import Anthropic

from app.config import settings
from app.schemas.workflow import Workflow, NodeType
from app.tools.registry import registry


SYSTEM_PROMPT = """You are a workflow planning agent. Convert natural language workflow descriptions
into structured workflow JSON.

You MUST follow this exact schema:
{
  "name": "string - workflow name",
  "description": "string - what this workflow does",
  "nodes": [
    {
      "id": "string - unique id like n1, n2...",
      "type": "trigger | action | condition | approval | wait | end",
      "name": "string - human readable name"
    }
  ],
  "edges": [
    {
      "from": "string - source node id",
      "to": "string - target node id",
      "condition": "optional string - 'true' or 'false' for branches"
    }
  ]
}

RULES:
1. The first node MUST be type "trigger" with name describing what starts the workflow
2. The last node MUST be type "end" with name describing the final outcome
3. For condition nodes, create exactly two outgoing edges: one with condition="true", one with condition="false"
4. For approval nodes, add a "reason" field explaining why human approval is needed
5. For action nodes, add a "tool" field with the exact tool name from the available tools list
6. For action nodes, add an "inputs" object with realistic placeholder values for the tool's required parameters (e.g., send_email needs "to", "subject", "body")
7. Use template syntax "{{variable_name}}" in inputs when the value should come from a previous step's output
8. Every node referenced in an edge must exist in the nodes list
9. Output ONLY valid JSON. No explanations, no markdown, no code fences.

AVAILABLE TOOLS:
{available_tools}

EXAMPLES:

Invoice Processing:
{{
  "name": "Invoice Processing",
  "description": "Extract invoice data, validate against PO, request approval for large amounts, process payment",
  "nodes": [
    {{"id": "n1", "type": "trigger", "name": "Invoice Received"}},
    {{"id": "n2", "type": "action", "name": "Extract Invoice Data", "tool": "extract_invoice_data", "inputs": {{"document": "invoice_001"}}}},
    {{"id": "n3", "type": "action", "name": "Find Purchase Order", "tool": "search_database", "inputs": {{"table": "purchase_orders", "query": "vendor_id"}}}},
    {{"id": "n4", "type": "condition", "name": "Amount Check", "expression": "amount > 100000"}},
    {{"id": "n5", "type": "approval", "name": "Manager Approval", "reason": "Invoice exceeds approval threshold"}},
    {{"id": "n6", "type": "action", "name": "Process Payment", "tool": "process_payment", "inputs": {{"invoice_id": "inv_001", "amount": 45000}}}},
    {{"id": "n7", "type": "end", "name": "Workflow Complete"}}
  ],
  "edges": [
    {{"from": "n1", "to": "n2"}},
    {{"from": "n2", "to": "n3"}},
    {{"from": "n3", "to": "n4"}},
    {{"from": "n4", "to": "n5", "condition": "true"}},
    {{"from": "n4", "to": "n6", "condition": "false"}},
    {{"from": "n5", "to": "n6"}},
    {{"from": "n6", "to": "n7"}}
  ]
}}

Customer Notification:
{{
  "name": "New Customer Signup Notification",
  "description": "Send email when a new customer signs up",
  "nodes": [
    {{"id": "n1", "type": "trigger", "name": "New Customer Signup"}},
    {{"id": "n2", "type": "action", "name": "Send Welcome Email", "tool": "send_email", "inputs": {{"to": "{{customer_email}}", "subject": "Welcome!", "body": "Thanks for signing up"}}}},
    {{"id": "n3", "type": "end", "name": "Notification Sent"}}
  ],
  "edges": [
    {{"from": "n1", "to": "n2"}},
    {{"from": "n2", "to": "n3"}}
  ]
}}

Employee Onboarding:
{{
  "name": "Employee Onboarding",
  "description": "Onboard a new employee with document verification and notifications",
  "nodes": [
    {{"id": "n1", "type": "trigger", "name": "Employee Added"}},
    {{"id": "n2", "type": "action", "name": "Request Documents", "tool": "send_email"}},
    {{"id": "n3", "type": "condition", "name": "Documents Complete"}},
    {{"id": "n4", "type": "action", "name": "Notify HR", "tool": "send_slack_message"}},
    {{"id": "n5", "type": "action", "name": "Send Reminder", "tool": "send_email"}},
    {{"id": "n6", "type": "action", "name": "Notify Manager", "tool": "send_email"}},
    {{"id": "n7", "type": "end", "name": "Onboarding Complete"}}
  ],
  "edges": [
    {{"from": "n1", "to": "n2"}},
    {{"from": "n2", "to": "n3"}},
    {{"from": "n3", "to": "n4", "condition": "true"}},
    {{"from": "n3", "to": "n5", "condition": "false"}},
    {{"from": "n4", "to": "n6"}},
    {{"from": "n5", "to": "n6"}},
    {{"from": "n6", "to": "n7"}}
  ]
}}"""


REPAIR_PROMPT = """The previous workflow JSON was invalid. Here are the validation errors:
{errors}

Please fix the JSON and output ONLY the corrected valid JSON. No explanations."""


class PlanningError(Exception):
    """Raised when planning fails after all retries."""

    def __init__(self, message: str, raw_response: str | None = None):
        self.raw_response = raw_response
        super().__init__(message)


class PlanningResult:
    """Result of a planning attempt — either a workflow or an error."""

    def __init__(self, workflow: Workflow | None = None, error: str | None = None, raw_response: str | None = None):
        self.workflow = workflow
        self.error = error
        self.raw_response = raw_response

    @property
    def success(self) -> bool:
        return self.workflow is not None


class PlannerAgent:
    """Converts natural language descriptions into validated workflow JSON."""

    def __init__(self, tool_registry=None, llm_client: Anthropic | None = None):
        self.registry = tool_registry or registry
        self.client = llm_client or Anthropic(
            api_key=settings.anthropic_api_key,
            base_url=settings.anthropic_base_url or None,
        )
        self.model = settings.anthropic_model
        self.max_retries = settings.planner_max_retries

    def _get_available_tools(self) -> str:
        """Format available tools for the system prompt."""
        tools = self.registry.list_all()
        lines = []
        for t in tools:
            lines.append(f"- {t.name}: {t.description} [{t.permission.value}]")
        return "\n".join(lines)

    def _extract_json(self, text: str) -> dict | None:
        """Extract JSON from LLM response, handling code fences."""
        # Try to find JSON in code fences first
        fence_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if fence_match:
            return json.loads(fence_match.group(1))

        # Try to find raw JSON object
        try:
            # Find first { and last }
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end + 1])
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    def _validate_tool_references(self, data: dict) -> list[str]:
        """Check that all tool references exist in the registry."""
        errors = []
        registered = {t.name for t in self.registry.list_all()}
        for node in data.get("nodes", []):
            if node.get("type") == "action" and "tool" in node:
                if node["tool"] not in registered:
                    errors.append(
                        f"Node '{node['id']}' references unknown tool '{node['tool']}'. "
                        f"Available: {sorted(registered)}"
                    )
        return errors

    async def plan(self, prompt: str) -> PlanningResult:
        """
        Convert natural language prompt into a validated Workflow.

        Pipeline:
        1. Send prompt to Claude with tool list
        2. Extract JSON from response
        3. Validate with Pydantic schema
        4. Validate tool references
        5. Return Workflow or error

        If validation fails, retry with repair prompt up to max_retries times.
        """
        available_tools = self._get_available_tools()
        system_prompt = SYSTEM_PROMPT.replace("{available_tools}", available_tools)

        messages = [{"role": "user", "content": prompt}]
        raw_response = ""

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=settings.planner_temperature,
                    system=system_prompt if attempt == 0 else REPAIR_PROMPT.format(
                        errors="\n".join(last_errors) if attempt > 0 else ""
                    ),
                    messages=messages,
                )
                # Extract text from response (handle thinking blocks)
                raw_response = ""
                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        raw_response += block.text

                if not raw_response:
                    last_errors = ["Empty response from LLM"]
                    messages.append({"role": "user", "content": "Please output valid JSON only."})
                    continue

                # Extract JSON
                data = self._extract_json(raw_response)
                if data is None:
                    last_errors = ["No valid JSON found in response"]
                    messages.append({"role": "assistant", "content": raw_response})
                    messages.append({"role": "user", "content": "Please output valid JSON only."})
                    continue

                # Validate tool references
                tool_errors = self._validate_tool_references(data)
                if tool_errors:
                    last_errors = tool_errors
                    messages.append({"role": "assistant", "content": raw_response})
                    messages.append({
                        "role": "user",
                        "content": f"Tool validation errors:\n" + "\n".join(tool_errors) + "\nFix the JSON with only valid tools."
                    })
                    continue

                # Validate with Pydantic
                workflow = Workflow.model_validate(data)

                # Add unique IDs if missing
                for i, node in enumerate(workflow.nodes):
                    if not node.get("id"):
                        node["id"] = f"n{i + 1}"

                return PlanningResult(workflow=workflow, raw_response=raw_response)

            except (json.JSONDecodeError, ValueError) as e:
                last_errors = [f"Invalid JSON: {e}"]
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": f"JSON parse error: {e}. Output valid JSON only."})
            except Exception as e:
                tb = traceback.format_exc()
                last_errors = [f"{type(e).__name__}: {e}\n{tb}"]
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": f"Error: {e}. Fix and output valid JSON."})

        return PlanningResult(
            error=f"Failed to generate valid workflow after {self.max_retries} retries. Last errors: {'; '.join(last_errors)}",
            raw_response=raw_response,
        )

    def get_planning_metadata(self, workflow: Workflow) -> dict[str, Any]:
        """Extract planning metadata from a validated workflow."""
        node_types = [n.get("type", "unknown") for n in workflow.nodes]
        tools_used = list({n.get("tool") for n in workflow.nodes if n.get("tool")})
        approval_gates = [n.get("id") for n in workflow.nodes if n.get("type") == "approval"]

        return {
            "node_count": len(workflow.nodes),
            "node_types": node_types,
            "tools_used": tools_used,
            "approval_gates": len(approval_gates),
            "has_branching": "condition" in node_types,
            "has_retry": any(n.get("retry_count", 0) > 0 for n in workflow.nodes),
            "complexity": "high" if len(workflow.nodes) > 8 else "medium" if len(workflow.nodes) > 4 else "low",
        }
