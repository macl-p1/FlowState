"""Tool registry — safe, controlled tool execution system."""

from typing import Any
from app.schemas.tool import Tool, ToolResult, PermissionLevel
from app.tools.implementations import TOOL_IMPLEMENTATIONS


class ToolAlreadyRegisteredError(Exception):
    """Raised when attempting to register a duplicate tool."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' is already registered")


class UnknownToolError(Exception):
    """Raised when trying to execute an unregistered tool."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Unknown tool: '{tool_name}'. Available tools: {list(TOOL_IMPLEMENTATIONS.keys())}")


class ToolRegistry:
    """
    Central registry for all executable tools.
    The LLM may ONLY call tools from this registry.
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register all built-in mock tools."""
        default_tools = [
            Tool(
                name="send_email",
                description="Send an email to a recipient",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"},
                    },
                    "required": ["to"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="send_slack_message",
                description="Send a message to a Slack channel",
                input_schema={
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "description": "Slack channel name"},
                        "message": {"type": "string", "description": "Message content"},
                    },
                    "required": ["channel"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="search_database",
                description="Search records in a database table",
                input_schema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name to search"},
                        "query": {"type": "string", "description": "Search query"},
                    },
                    "required": ["table"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="update_database",
                description="Update a record in the database",
                input_schema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "id": {"type": "string"},
                        "updates": {"type": "object"},
                    },
                    "required": ["table", "id"],
                },
                permission=PermissionLevel.CONFIRM,
            ),
            Tool(
                name="create_ticket",
                description="Create a support ticket",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "priority": {"type": "string"},
                        "assignee": {"type": "string"},
                    },
                    "required": ["title"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="create_calendar_event",
                description="Create a calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "date": {"type": "string"},
                        "attendees": {"type": "array"},
                    },
                    "required": ["title", "date"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="request_human_approval",
                description="Pause workflow and request human approval",
                input_schema={
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"},
                        "context": {"type": "object"},
                        "approver_role": {"type": "string"},
                    },
                    "required": ["reason"],
                },
                permission=PermissionLevel.HUMAN_ONLY,
            ),
            Tool(
                name="wait",
                description="Wait for a specified duration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "seconds": {"type": "integer"},
                    },
                    "required": ["seconds"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="extract_invoice_data",
                description="Extract structured data from an invoice document",
                input_schema={
                    "type": "object",
                    "properties": {
                        "document": {"type": "string", "description": "Document path or ID"},
                    },
                    "required": ["document"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="validate_invoice",
                description="Validate invoice against business rules",
                input_schema={
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "purchase_order_id": {"type": "string"},
                    },
                    "required": ["amount"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="process_payment",
                description="Process a payment for an invoice",
                input_schema={
                    "type": "object",
                    "properties": {
                        "invoice_id": {"type": "string"},
                        "amount": {"type": "number"},
                    },
                    "required": ["invoice_id", "amount"],
                },
                permission=PermissionLevel.CONFIRM,
            ),

            # --- Communication ---
            Tool(
                name="send_sms",
                description="Send an SMS message to a phone number",
                input_schema={
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string", "description": "Recipient phone number"},
                        "message": {"type": "string", "description": "SMS content"},
                    },
                    "required": ["phone_number"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="send_notification",
                description="Send an in-app notification to a user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "Target user ID"},
                        "title": {"type": "string", "description": "Notification title"},
                        "message": {"type": "string", "description": "Notification body"},
                    },
                    "required": ["user_id"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="send_template_email",
                description="Send an email using a predefined template (welcome, invoice, reminder)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "template_name": {"type": "string", "description": "Template: welcome, invoice, reminder"},
                        "to": {"type": "string"},
                        "variables": {"type": "object"},
                    },
                    "required": ["template_name", "to"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Data / Analytics ---
            Tool(
                name="run_query",
                description="Query records from a database table with optional filters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "filters": {"type": "object"},
                        "limit": {"type": "integer"},
                    },
                    "required": ["table"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="delete_record",
                description="Delete a record from a database table",
                input_schema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "id": {"type": "string"},
                    },
                    "required": ["table", "id"],
                },
                permission=PermissionLevel.CONFIRM,
            ),
            Tool(
                name="aggregate_metrics",
                description="Aggregate system metrics (average, sum, max, min, count)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "description": "average, sum, max, min, count"},
                        "metric_name": {"type": "string", "description": "Filter by metric name"},
                    },
                    "required": ["operation"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="export_csv",
                description="Export records from a database table as CSV",
                input_schema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "fields": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["table"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- File Operations ---
            Tool(
                name="read_file",
                description="Read a file by name from the file store",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                    },
                    "required": ["filename"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="write_file",
                description="Write content to a file in the file store",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["filename", "content"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="delete_file",
                description="Delete a file from the file store",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                    },
                    "required": ["filename"],
                },
                permission=PermissionLevel.CONFIRM,
            ),
            Tool(
                name="hash_content",
                description="Generate a SHA-256 hash of content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to hash"},
                    },
                    "required": ["content"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Integration ---
            Tool(
                name="http_request",
                description="Make an HTTP request to an external service (mock)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target URL"},
                        "method": {"type": "string", "description": "HTTP method"},
                        "headers": {"type": "object"},
                        "body": {"type": "string"},
                    },
                    "required": ["url"],
                },
                permission=PermissionLevel.CONFIRM,
            ),

            # --- CRM / Sales ---
            Tool(
                name="create_lead",
                description="Create a new lead in the CRM",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "source": {"type": "string"},
                    },
                    "required": ["name", "email"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="score_lead",
                description="Score a lead based on engagement signals",
                input_schema={
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string"},
                        "email_opens": {"type": "integer"},
                        "page_views": {"type": "integer"},
                        "form_fills": {"type": "integer"},
                    },
                    "required": ["lead_id"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Task / Project Management ---
            Tool(
                name="create_task",
                description="Create a task with title, assignee, priority, and due date",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "assignee": {"type": "string"},
                        "priority": {"type": "string", "description": "low, medium, high, critical"},
                        "due_date": {"type": "string", "description": "ISO date string"},
                    },
                    "required": ["title"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="update_task_status",
                description="Update the status of an existing task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "status": {"type": "string", "description": "open, in_progress, done, blocked"},
                    },
                    "required": ["task_id", "status"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Monitoring / Observability ---
            Tool(
                name="check_health",
                description="Check the health status of services (api, database, cache, queue)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "Service name or 'all'"},
                    },
                    "required": [],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="trigger_alert",
                description="Trigger a monitoring alert with severity level",
                input_schema={
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "description": "info, warning, critical"},
                        "message": {"type": "string"},
                        "service": {"type": "string"},
                    },
                    "required": ["severity"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Finance ---
            Tool(
                name="create_invoice",
                description="Create a new invoice record",
                input_schema={
                    "type": "object",
                    "properties": {
                        "vendor": {"type": "string"},
                        "amount": {"type": "number"},
                        "description": {"type": "string"},
                    },
                    "required": ["vendor", "amount"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="record_transaction",
                description="Record a financial transaction",
                input_schema={
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "category": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["amount"],
                },
                permission=PermissionLevel.CONFIRM,
            ),
            Tool(
                name="refund_payment",
                description="Process a refund for a payment",
                input_schema={
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["payment_id"],
                },
                permission=PermissionLevel.CONFIRM,
            ),

            # --- HR / People ---
            Tool(
                name="get_employee_info",
                description="Look up employee information by ID or name",
                input_schema={
                    "type": "object",
                    "properties": {
                        "employee_id": {"type": "string"},
                        "name": {"type": "string"},
                    },
                    "required": [],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="update_employee_record",
                description="Update an employee record",
                input_schema={
                    "type": "object",
                    "properties": {
                        "employee_id": {"type": "string"},
                        "updates": {"type": "object"},
                    },
                    "required": ["employee_id", "updates"],
                },
                permission=PermissionLevel.CONFIRM,
            ),

            # --- Logistics ---
            Tool(
                name="track_shipment",
                description="Track a shipment by tracking number",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tracking_number": {"type": "string"},
                    },
                    "required": ["tracking_number"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="generate_shipping_label",
                description="Generate a shipping label for a package",
                input_schema={
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string"},
                        "address": {"type": "string"},
                        "weight": {"type": "number"},
                    },
                    "required": ["recipient", "address"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Workflow Utilities ---
            Tool(
                name="transform_data",
                description="Transform data — format, uppercase, filter_nulls, or flatten",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "operation": {"type": "string", "description": "format, uppercase, filter_nulls, flatten"},
                    },
                    "required": ["data", "operation"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="merge_data",
                description="Merge two data objects together",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {"type": "object"},
                        "target": {"type": "object"},
                    },
                    "required": ["source", "target"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="conditional_router",
                description="Evaluate a condition and select a branch",
                input_schema={
                    "type": "object",
                    "properties": {
                        "condition": {"type": "string"},
                        "branches": {"type": "object"},
                        "context": {"type": "object"},
                    },
                    "required": ["condition", "branches"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="delay",
                description="Delay execution by a specified number of seconds",
                input_schema={
                    "type": "object",
                    "properties": {
                        "seconds": {"type": "integer", "description": "Delay in seconds (max 5)"},
                    },
                    "required": ["seconds"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="fan_out",
                description="Dispatch work to multiple parallel targets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "targets": {"type": "array", "items": {"type": "string"}},
                        "payload": {"type": "object"},
                    },
                    "required": ["targets"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="fan_in",
                description="Collect results from a fan-out with a merge strategy",
                input_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "array"},
                        "strategy": {"type": "string", "description": "all, first_success"},
                    },
                    "required": ["results"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- AI / Content ---
            Tool(
                name="generate_content",
                description="Generate AI content — email, summary, response, or report (mock)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string", "description": "email, summary, response, report"},
                        "prompt": {"type": "string", "description": "Content description"},
                        "max_length": {"type": "integer"},
                    },
                    "required": ["content_type"],
                },
                permission=PermissionLevel.AUTO,
            ),
            Tool(
                name="classify_text",
                description="Classify text into categories (urgent, billing, support, general)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to classify"},
                    },
                    "required": ["text"],
                },
                permission=PermissionLevel.AUTO,
            ),

            # --- Scheduling ---
            Tool(
                name="list_available_slots",
                description="List available time slots for scheduling on a given date",
                input_schema={
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "ISO date string"},
                        "duration_minutes": {"type": "integer"},
                        "timezone": {"type": "string"},
                    },
                    "required": ["date"],
                },
                permission=PermissionLevel.AUTO,
            ),
        ]
        for tool in default_tools:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        """Register a new tool. Raises if name already exists."""
        if tool.name in self._tools:
            raise ToolAlreadyRegisteredError(tool.name)
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_all(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def has(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    async def execute(self, tool_name: str, inputs: dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name with the given inputs.
        Only registered tools can be executed.

        If a custom tool with this name has an integration_config set,
        the call is routed to the real integration handler. Otherwise,
        the mock implementation is used.
        """
        if tool_name not in TOOL_IMPLEMENTATIONS:
            raise UnknownToolError(tool_name)

        # Check for real integration config on a custom tool
        custom_tool = self._get_custom_tool_by_name(tool_name)
        if custom_tool and custom_tool.integration_config:
            from app.tools.integrations import integration_handler
            return await integration_handler.execute(
                custom_tool.integration_config, inputs
            )

        # Mock path (unchanged)
        tool_func = TOOL_IMPLEMENTATIONS[tool_name]
        try:
            result = await tool_func(inputs)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                retryable=True,
            )

    def _get_custom_tool_by_name(self, name: str) -> Any:
        """Look up a CustomTool record by name. Returns None if not found."""
        from app.database import get_db_context
        from app.models.custom_tool import CustomTool
        try:
            with get_db_context() as db:
                return db.query(CustomTool).filter(CustomTool.name == name).first()
        except Exception:
            return None


# Singleton
registry = ToolRegistry()
