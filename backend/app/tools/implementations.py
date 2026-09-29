"""Mock tool implementations for the workflow engine."""

import asyncio
import random
import json
import hashlib
from typing import Any
from datetime import datetime
from app.schemas.tool import ToolResult


# ---- In-memory mock data stores ----

MOCK_EMAILS: list[dict] = []
MOCK_SLACK_MESSAGES: list[dict] = []
MOCK_DB_RECORDS: dict[str, list[dict]] = {
    "purchase_orders": [
        {"id": "po_001", "vendor": "Acme Corp", "amount": 45000, "status": "active"},
        {"id": "po_002", "vendor": "Globex Inc", "amount": 120000, "status": "active"},
    ],
    "invoices": [
        {"id": "inv_001", "vendor": "Acme Corp", "amount": 45000, "invoice_number": "INV-2024-001"},
        {"id": "inv_002", "vendor": "Globex Inc", "amount": 120000, "invoice_number": "INV-2024-002"},
    ],
    "employees": [
        {"id": "emp_001", "name": "Alice", "department": "Engineering", "documents_verified": True},
        {"id": "emp_002", "name": "Bob", "department": "Marketing", "documents_verified": False},
    ],
    "customers": [
        {"id": "cust_001", "name": "Acme Corp", "tier": "enterprise", "orders": 12},
        {"id": "cust_002", "name": "Globex Inc", "tier": "standard", "orders": 3},
    ],
}
MOCK_TICKETS: list[dict] = []
MOCK_CALENDAR_EVENTS: list[dict] = []
MOCK_APPROVALS: dict[str, dict] = {}
MOCK_FILES: dict[str, str] = {}
MOCK_HTTP_LOGS: list[dict] = []
MOCK_LEADS: list[dict] = [
    {"id": "lead_001", "name": "Prospect A", "email": "prospect_a@example.com", "score": 85},
    {"id": "lead_002", "name": "Prospect B", "email": "prospect_b@example.com", "score": 42},
]
MOCK_METRICS: list[dict] = [
    {"name": "cpu_usage", "value": 73.5, "unit": "%"},
    {"name": "memory_usage", "value": 62.1, "unit": "%"},
    {"name": "disk_io", "value": 120.0, "unit": "MB/s"},
]
MOCK_NOTIFICATIONS: list[dict] = []
MOCK_TASKS: list[dict] = []
MOCK_USERS: dict[str, dict] = {
    "alice": {"id": "u1", "name": "Alice", "department": "Engineering", "role": "employee"},
    "bob": {"id": "u2", "name": "Bob", "department": "Marketing", "role": "employee"},
    "charlie": {"id": "u3", "name": "Charlie", "department": "Sales", "role": "manager"},
}
MOCK_TRANSACTIONS: list[dict] = []


# ---- Original tool implementations ----

async def send_email(inputs: dict[str, Any]) -> ToolResult:
    """Send an email (mock)."""
    to = inputs.get("to")
    subject = inputs.get("subject", "")
    body = inputs.get("body", "")

    if not to:
        return ToolResult(success=False, error="Missing required field: 'to'", retryable=False)

    msg_id = f"msg_{random.randint(1000, 9999)}"
    MOCK_EMAILS.append({"id": msg_id, "to": to, "subject": subject, "body": body})
    return ToolResult(success=True, output={"message_id": msg_id, "to": to})


async def send_slack_message(inputs: dict[str, Any]) -> ToolResult:
    """Send a Slack message (mock)."""
    channel = inputs.get("channel", "#general")
    message = inputs.get("message", "")

    if not channel:
        return ToolResult(success=False, error="Missing required field: 'channel'", retryable=False)

    msg_id = f"slack_{random.randint(1000, 9999)}"
    MOCK_SLACK_MESSAGES.append({"id": msg_id, "channel": channel, "message": message})
    return ToolResult(success=True, output={"message_id": msg_id, "channel": channel})


async def search_database(inputs: dict[str, Any]) -> ToolResult:
    """Search records in a database table (mock)."""
    query = inputs.get("query", "")
    table = inputs.get("table", "")

    if not table or table not in MOCK_DB_RECORDS:
        available = list(MOCK_DB_RECORDS.keys())
        return ToolResult(
            success=False,
            error=f"Table '{table}' not found. Available: {available}",
            retryable=False,
        )

    records = MOCK_DB_RECORDS[table]
    return ToolResult(success=True, output={"records": records, "count": len(records)})


async def update_database(inputs: dict[str, Any]) -> ToolResult:
    """Update a record in the database (mock)."""
    table = inputs.get("table", "")
    record_id = inputs.get("id", "")
    updates = inputs.get("updates", {})

    if table not in MOCK_DB_RECORDS:
        return ToolResult(success=False, error=f"Table '{table}' not found", retryable=False)

    records = MOCK_DB_RECORDS[table]
    for record in records:
        if record.get("id") == record_id:
            record.update(updates)
            return ToolResult(success=True, output={"updated": True, "record": record})

    return ToolResult(success=False, error=f"Record {record_id} not found in {table}", retryable=False)


async def create_ticket(inputs: dict[str, Any]) -> ToolResult:
    """Create a support ticket (mock)."""
    title = inputs.get("title", "")
    priority = inputs.get("priority", "medium")
    assignee = inputs.get("assignee", "unassigned")

    ticket_id = f"ticket_{random.randint(1000, 9999)}"
    ticket = {"id": ticket_id, "title": title, "priority": priority, "assignee": assignee}
    MOCK_TICKETS.append(ticket)
    return ToolResult(success=True, output={"ticket_id": ticket_id, "ticket": ticket})


async def create_calendar_event(inputs: dict[str, Any]) -> ToolResult:
    """Create a calendar event (mock)."""
    title = inputs.get("title", "")
    date = inputs.get("date", "")
    attendees = inputs.get("attendees", [])

    event_id = f"evt_{random.randint(1000, 9999)}"
    event = {"id": event_id, "title": title, "date": date, "attendees": attendees}
    MOCK_CALENDAR_EVENTS.append(event)
    return ToolResult(success=True, output={"event_id": event_id, "event": event})


async def request_human_approval(inputs: dict[str, Any]) -> ToolResult:
    """Request human approval — creates an approval record and pauses execution."""
    reason = inputs.get("reason", "Approval required")
    context = inputs.get("context", {})
    approver_role = inputs.get("approver_role")

    approval_id = f"approval_{random.randint(1000, 9999)}"
    MOCK_APPROVALS[approval_id] = {
        "id": approval_id,
        "reason": reason,
        "context": context,
        "approver_role": approver_role,
        "status": "pending",
    }
    return ToolResult(
        success=True,
        output={"approval_id": approval_id, "status": "pending"},
    )


async def wait_tool(inputs: dict[str, Any]) -> ToolResult:
    """Wait for a specified duration."""
    seconds = inputs.get("seconds", 1)
    max_seconds = min(seconds, 5)  # Cap at 5 seconds for testing
    await asyncio.sleep(max_seconds)
    return ToolResult(success=True, output={"waited_seconds": max_seconds})


async def extract_invoice_data(inputs: dict[str, Any]) -> ToolResult:
    """Mock invoice data extraction."""
    document = inputs.get("document", "mock_invoice.pdf")
    return ToolResult(success=True, output={
        "vendor": "Acme Corp",
        "amount": 45000,
        "invoice_number": "INV-2024-001",
        "date": "2024-01-15",
        "line_items": [
            {"description": "Widget A", "quantity": 10, "unit_price": 4500},
        ],
    })


async def validate_invoice(inputs: dict[str, Any]) -> ToolResult:
    """Validate invoice against business rules."""
    amount = inputs.get("amount", 0)
    po_id = inputs.get("purchase_order_id", "")

    warnings = []
    if amount > 100000:
        warnings.append(f"Amount ${amount:,} exceeds approval threshold of $100,000")

    return ToolResult(
        success=True,
        output={"valid": True, "amount": amount, "po_id": po_id},
        warnings=warnings,
    )


async def process_payment(inputs: dict[str, Any]) -> ToolResult:
    """Mock payment processing."""
    invoice_id = inputs.get("invoice_id", "")
    amount = inputs.get("amount", 0)

    return ToolResult(
        success=True,
        output={
            "payment_id": f"pay_{random.randint(1000, 9999)}",
            "invoice_id": invoice_id,
            "amount": amount,
            "status": "processed",
        },
    )


# ---- NEW: Additional tool implementations ----

# --- Communication ---

async def send_sms(inputs: dict[str, Any]) -> ToolResult:
    """Send an SMS message (mock)."""
    phone = inputs.get("phone_number", "")
    message = inputs.get("message", "")

    if not phone:
        return ToolResult(success=False, error="Missing required field: 'phone_number'", retryable=False)

    msg_id = f"sms_{random.randint(1000, 9999)}"
    MOCK_SMS_LOG = getattr(send_sms, "_log", [])
    MOCK_SMS_LOG.append({"id": msg_id, "phone": phone, "message": message})
    send_sms._log = MOCK_SMS_LOG
    return ToolResult(success=True, output={"message_id": msg_id, "phone": phone})


async def send_notification(inputs: dict[str, Any]) -> ToolResult:
    """Send an in-app notification to a user."""
    user_id = inputs.get("user_id", "")
    title = inputs.get("title", "")
    message = inputs.get("message", "")

    if not user_id:
        return ToolResult(success=False, error="Missing required field: 'user_id'", retryable=False)

    notif_id = f"notif_{random.randint(1000, 9999)}"
    MOCK_NOTIFICATIONS.append({
        "id": notif_id, "user_id": user_id, "title": title, "message": message,
        "read": False, "created_at": datetime.utcnow().isoformat(),
    })
    return ToolResult(success=True, output={"notification_id": notif_id, "user_id": user_id})


# --- Data / Analytics ---

async def run_query(inputs: dict[str, Any]) -> ToolResult:
    """Run an arbitrary SQL-like query on mock data tables."""
    table = inputs.get("table", "")
    filters = inputs.get("filters", {})
    limit = inputs.get("limit", 50)

    if not table or table not in MOCK_DB_RECORDS:
        available = list(MOCK_DB_RECORDS.keys())
        return ToolResult(success=False, error=f"Table '{table}' not found. Available: {available}", retryable=False)

    results = list(MOCK_DB_RECORDS[table])
    for key, value in filters.items():
        results = [r for r in results if str(r.get(key, "")) == str(value)]

    results = results[:limit]
    return ToolResult(success=True, output={"records": results, "count": len(results)})


async def delete_record(inputs: dict[str, Any]) -> ToolResult:
    """Delete a record from a database table (mock)."""
    table = inputs.get("table", "")
    record_id = inputs.get("id", "")

    if table not in MOCK_DB_RECORDS:
        return ToolResult(success=False, error=f"Table '{table}' not found", retryable=False)

    records = MOCK_DB_RECORDS[table]
    for i, record in enumerate(records):
        if record.get("id") == record_id:
            deleted = records.pop(i)
            return ToolResult(success=True, output={"deleted": True, "record": deleted})

    return ToolResult(success=False, error=f"Record {record_id} not found in {table}", retryable=False)


async def aggregate_metrics(inputs: dict[str, Any]) -> ToolResult:
    """Aggregate and summarize system metrics."""
    operation = inputs.get("operation", "average")
    metric_name = inputs.get("metric_name", "")

    filtered = [m for m in MOCK_METRICS if not metric_name or m["name"] == metric_name]
    if not filtered:
        return ToolResult(success=False, error=f"No metrics found for '{metric_name}'", retryable=False)

    values = [m["value"] for m in filtered]
    if operation == "average":
        result = round(sum(values) / len(values), 2)
    elif operation == "sum":
        result = round(sum(values), 2)
    elif operation == "max":
        result = max(values)
    elif operation == "min":
        result = min(values)
    elif operation == "count":
        result = len(values)
    else:
        result = values

    return ToolResult(success=True, output={
        "operation": operation, "metric": metric_name or "all",
        "result": result, "sample_size": len(values),
    })


async def export_csv(inputs: dict[str, Any]) -> ToolResult:
    """Export records from a table as a CSV string."""
    table = inputs.get("table", "")
    fields = inputs.get("fields", [])

    if not table or table not in MOCK_DB_RECORDS:
        available = list(MOCK_DB_RECORDS.keys())
        return ToolResult(success=False, error=f"Table '{table}' not found. Available: {available}", retryable=False)

    records = MOCK_DB_RECORDS[table]
    if not records:
        return ToolResult(success=True, output={"csv": "", "row_count": 0})

    keys = fields if fields else list(records[0].keys())
    lines = [",".join(keys)]
    for record in records:
        lines.append(",".join(str(record.get(k, "")) for k in keys))

    csv_data = "\n".join(lines)
    return ToolResult(success=True, output={"csv": csv_data, "row_count": len(records), "columns": keys})


# --- File Operations ---

async def read_file(inputs: dict[str, Any]) -> ToolResult:
    """Read a file by name from the mock file store."""
    filename = inputs.get("filename", "")

    if filename not in MOCK_FILES:
        return ToolResult(success=False, error=f"File '{filename}' not found", retryable=False)

    return ToolResult(success=True, output={"filename": filename, "content": MOCK_FILES[filename]})


async def write_file(inputs: dict[str, Any]) -> ToolResult:
    """Write content to a file in the mock file store."""
    filename = inputs.get("filename", "")
    content = inputs.get("content", "")

    if not filename:
        return ToolResult(success=False, error="Missing required field: 'filename'", retryable=False)

    MOCK_FILES[filename] = content
    return ToolResult(success=True, output={"filename": filename, "bytes_written": len(content)})


async def delete_file(inputs: dict[str, Any]) -> ToolResult:
    """Delete a file from the mock file store."""
    filename = inputs.get("filename", "")

    if filename not in MOCK_FILES:
        return ToolResult(success=False, error=f"File '{filename}' not found", retryable=False)

    del MOCK_FILES[filename]
    return ToolResult(success=True, output={"filename": filename, "deleted": True})


async def hash_content(inputs: dict[str, Any]) -> ToolResult:
    """Generate a SHA-256 hash of the given content."""
    content = inputs.get("content", "")
    hash_value = hashlib.sha256(content.encode()).hexdigest()
    return ToolResult(success=True, output={"hash": hash_value, "algorithm": "sha256"})


# --- Integration / HTTP ---

async def http_request(inputs: dict[str, Any]) -> ToolResult:
    """Make an HTTP request (mock)."""
    url = inputs.get("url", "")
    method = inputs.get("method", "GET")
    headers = inputs.get("headers", {})
    body = inputs.get("body", "")

    if not url:
        return ToolResult(success=False, error="Missing required field: 'url'", retryable=False)

    status = 200 if not url.startswith("http://error") else 500
    log_entry = {
        "id": f"http_{random.randint(1000, 9999)}",
        "url": url, "method": method, "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    MOCK_HTTP_LOGS.append(log_entry)

    body_out = {"mock": True, "url": url, "method": method} if status == 200 else None
    return ToolResult(success=status < 400, output=body_out or {}, error="" if status < 400 else f"HTTP {status}")


# --- CRM / Sales ---

async def create_lead(inputs: dict[str, Any]) -> ToolResult:
    """Create a new lead in the CRM (mock)."""
    name = inputs.get("name", "")
    email = inputs.get("email", "")
    source = inputs.get("source", "website")

    if not name or not email:
        return ToolResult(success=False, error="Missing required fields: 'name' and 'email'", retryable=False)

    lead_id = f"lead_{random.randint(1000, 9999)}"
    lead = {
        "id": lead_id, "name": name, "email": email,
        "source": source, "score": 0, "status": "new",
        "created_at": datetime.utcnow().isoformat(),
    }
    MOCK_LEADS.append(lead)
    return ToolResult(success=True, output={"lead_id": lead_id, "lead": lead})


async def score_lead(inputs: dict[str, Any]) -> ToolResult:
    """Score a lead based on engagement signals (mock)."""
    lead_id = inputs.get("lead_id", "")
    email_opens = inputs.get("email_opens", 0)
    page_views = inputs.get("page_views", 0)
    form_fills = inputs.get("form_fills", 0)

    score = min(100, email_opens * 5 + page_views * 3 + form_fills * 15)
    for lead in MOCK_LEADS:
        if lead["id"] == lead_id:
            lead["score"] = score
            return ToolResult(success=True, output={"lead_id": lead_id, "score": score, "tier": "hot" if score > 70 else "warm" if score > 40 else "cold"})

    return ToolResult(success=False, error=f"Lead {lead_id} not found", retryable=False)


# --- Task / Project Management ---

async def create_task(inputs: dict[str, Any]) -> ToolResult:
    """Create a task (mock)."""
    title = inputs.get("title", "")
    assignee = inputs.get("assignee", "unassigned")
    priority = inputs.get("priority", "medium")
    due_date = inputs.get("due_date", "")

    if not title:
        return ToolResult(success=False, error="Missing required field: 'title'", retryable=False)

    task_id = f"task_{random.randint(1000, 9999)}"
    task = {
        "id": task_id, "title": title, "assignee": assignee,
        "priority": priority, "due_date": due_date, "status": "open",
    }
    MOCK_TASKS.append(task)
    return ToolResult(success=True, output={"task_id": task_id, "task": task})


async def update_task_status(inputs: dict[str, Any]) -> ToolResult:
    """Update the status of a task (mock)."""
    task_id = inputs.get("task_id", "")
    status = inputs.get("status", "")

    for task in MOCK_TASKS:
        if task["id"] == task_id:
            task["status"] = status
            return ToolResult(success=True, output={"task_id": task_id, "status": status})

    return ToolResult(success=False, error=f"Task {task_id} not found", retryable=False)


# --- Monitoring / Observability ---

async def check_health(inputs: dict[str, Any]) -> ToolResult:
    """Check the health of a service (mock)."""
    service = inputs.get("service", "all")

    services = ["api", "database", "cache", "queue"] if service == "all" else [service]
    health = {}
    for svc in services:
        cpu = random.uniform(10, 95)
        health[svc] = {
            "status": "healthy" if cpu < 80 else "degraded" if cpu < 95 else "unhealthy",
            "cpu": round(cpu, 1),
            "memory": round(random.uniform(20, 90), 1),
            "uptime_seconds": random.randint(3600, 86400),
        }

    overall = all(v["status"] == "healthy" for v in health.values())
    return ToolResult(success=overall, output={"services": health, "overall": "healthy" if overall else "degraded"})


async def trigger_alert(inputs: dict[str, Any]) -> ToolResult:
    """Trigger a monitoring alert (mock)."""
    severity = inputs.get("severity", "warning")
    message = inputs.get("message", "")
    service = inputs.get("service", "unknown")

    alert_id = f"alert_{random.randint(1000, 9999)}"
    alert = {
        "id": alert_id, "severity": severity, "message": message,
        "service": service, "timestamp": datetime.utcnow().isoformat(), "acknowledged": False,
    }
    MOCK_NOTIFICATIONS.append({**alert, "type": "alert"})
    return ToolResult(success=True, output={"alert_id": alert_id, "severity": severity})


# --- Finance ---

async def create_invoice(inputs: dict[str, Any]) -> ToolResult:
    """Create a new invoice record (mock)."""
    vendor = inputs.get("vendor", "")
    amount = inputs.get("amount", 0)
    description = inputs.get("description", "")

    if not vendor or not amount:
        return ToolResult(success=False, error="Missing required fields: 'vendor' and 'amount'", retryable=False)

    invoice_id = f"inv_{random.randint(1000, 9999)}"
    invoice = {
        "id": invoice_id, "vendor": vendor, "amount": amount,
        "description": description, "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
    }
    MOCK_DB_RECORDS["invoices"].append(invoice)
    return ToolResult(success=True, output={"invoice_id": invoice_id, "invoice": invoice})


async def record_transaction(inputs: dict[str, Any]) -> ToolResult:
    """Record a financial transaction (mock)."""
    amount = inputs.get("amount", 0)
    category = inputs.get("category", "general")
    description = inputs.get("description", "")

    txn_id = f"txn_{random.randint(1000, 9999)}"
    transaction = {
        "id": txn_id, "amount": amount, "category": category,
        "description": description, "timestamp": datetime.utcnow().isoformat(),
    }
    MOCK_TRANSACTIONS.append(transaction)
    return ToolResult(success=True, output={"transaction_id": txn_id, "transaction": transaction})


async def refund_payment(inputs: dict[str, Any]) -> ToolResult:
    """Process a refund for a payment (mock)."""
    payment_id = inputs.get("payment_id", "")
    reason = inputs.get("reason", "")

    refund_id = f"refund_{random.randint(1000, 9999)}"
    refund = {
        "id": refund_id, "payment_id": payment_id, "reason": reason,
        "status": "processed", "timestamp": datetime.utcnow().isoformat(),
    }
    return ToolResult(success=True, output={"refund_id": refund_id, "refund": refund})


# --- HR / People ---

async def get_employee_info(inputs: dict[str, Any]) -> ToolResult:
    """Look up employee information by name or ID."""
    employee_id = inputs.get("employee_id", "")
    name = inputs.get("name", "")

    if employee_id:
        user = MOCK_USERS.get(employee_id.lower())
        if user:
            return ToolResult(success=True, output={"employee": user})
        return ToolResult(success=False, error=f"Employee '{employee_id}' not found", retryable=False)

    if name:
        for user in MOCK_USERS.values():
            if user["name"].lower() == name.lower():
                return ToolResult(success=True, output={"employee": user})
        return ToolResult(success=False, error=f"Employee '{name}' not found", retryable=False)

    return ToolResult(success=False, error="Provide 'employee_id' or 'name'", retryable=False)


async def update_employee_record(inputs: dict[str, Any]) -> ToolResult:
    """Update an employee record (mock)."""
    employee_id = inputs.get("employee_id", "")
    updates = inputs.get("updates", {})

    if not employee_id:
        return ToolResult(success=False, error="Missing required field: 'employee_id'", retryable=False)

    user = MOCK_USERS.get(employee_id.lower())
    if not user:
        return ToolResult(success=False, error=f"Employee '{employee_id}' not found", retryable=False)

    user.update(updates)
    return ToolResult(success=True, output={"employee_id": employee_id, "updated": user})


# --- Logistics ---

async def track_shipment(inputs: dict[str, Any]) -> ToolResult:
    """Track a shipment by tracking number (mock)."""
    tracking_number = inputs.get("tracking_number", "")

    statuses = ["in_transit", "out_for_delivery", "delivered", "delayed"]
    status = random.choice(statuses)

    return ToolResult(success=True, output={
        "tracking_number": tracking_number,
        "status": status,
        "carrier": "MockExpress",
        "estimated_delivery": "2026-10-01",
        "history": [
            {"timestamp": "2026-09-25T08:00:00Z", "event": "Package picked up"},
            {"timestamp": "2026-09-26T14:00:00Z", "event": f"In transit - {status}"},
        ],
    })


async def generate_shipping_label(inputs: dict[str, Any]) -> ToolResult:
    """Generate a shipping label (mock)."""
    recipient = inputs.get("recipient", "")
    address = inputs.get("address", "")
    weight = inputs.get("weight", 1.0)

    if not recipient or not address:
        return ToolResult(success=False, error="Missing required fields: 'recipient' and 'address'", retryable=False)

    label_id = f"label_{random.randint(1000, 9999)}"
    label = {
        "id": label_id, "recipient": recipient, "address": address,
        "weight_kg": weight, "carrier": "MockExpress",
        "tracking_number": f"MX{random.randint(1000000, 9999999)}",
    }
    return ToolResult(success=True, output={"label_id": label_id, "label": label})


# --- Workflow Utilities ---

async def transform_data(inputs: dict[str, Any]) -> ToolResult:
    """Transform data from one step to another (mock formatting/conversion)."""
    data = inputs.get("data", {})
    operation = inputs.get("operation", "format")

    if operation == "format":
        result = json.dumps(data, indent=2)
    elif operation == "uppercase":
        result = {k: str(v).upper() for k, v in data.items()}
    elif operation == "filter_nulls":
        result = {k: v for k, v in data.items() if v is not None and v != ""}
    elif operation == "flatten":
        result = {}
        for k, v in data.items():
            if isinstance(v, dict):
                for sk, sv in v.items():
                    result[f"{k}.{sk}"] = sv
            else:
                result[k] = v
    else:
        result = data

    return ToolResult(success=True, output={"transformed": result, "operation": operation})


async def merge_data(inputs: dict[str, Any]) -> ToolResult:
    """Merge two data objects (mock)."""
    source = inputs.get("source", {})
    target = inputs.get("target", {})

    if not isinstance(source, dict) or not isinstance(target, dict):
        return ToolResult(success=False, error="'source' and 'target' must be objects", retryable=False)

    merged = {**target, **source}
    return ToolResult(success=True, output={"merged": merged, "keys_added": len(source)})


async def conditional_router(inputs: dict[str, Any]) -> ToolResult:
    """Evaluate a condition and return the matching branch."""
    condition = inputs.get("condition", "")
    branches = inputs.get("branches", {})
    context = inputs.get("context", {})

    # Simple mock evaluation — check if any context key matches a branch name
    selected = "default"
    for branch_name, branch_condition in branches.items():
        if branch_condition in str(context) or branch_condition == condition:
            selected = branch_name
            break

    return ToolResult(success=True, output={"selected_branch": selected, "condition": condition})


async def delay(inputs: dict[str, Any]) -> ToolResult:
    """Delay execution by a specified number of seconds (mock)."""
    seconds = inputs.get("seconds", 1)
    max_seconds = min(seconds, 5)
    await asyncio.sleep(max_seconds)
    return ToolResult(success=True, output={"delayed_seconds": max_seconds})


async def fan_out(inputs: dict[str, Any]) -> ToolResult:
    """Fan out to multiple parallel targets (mock)."""
    targets = inputs.get("targets", [])
    payload = inputs.get("payload", {})

    if not targets:
        return ToolResult(success=False, error="Missing required field: 'targets' (list)", retryable=False)

    results = []
    for target in targets:
        results.append({
            "target": target,
            "status": "completed",
            "output": {"received": payload},
        })

    return ToolResult(success=True, output={"dispatched": len(results), "results": results})


async def fan_in(inputs: dict[str, Any]) -> ToolResult:
    """Collect results from a fan-out (mock)."""
    results = inputs.get("results", [])
    strategy = inputs.get("strategy", "all")

    if strategy == "all":
        combined = {"all_results": results, "count": len(results)}
    elif strategy == "first_success":
        combined = {"first_success": next((r for r in results if r.get("status") == "completed"), None)}
    else:
        combined = {"results": results}

    return ToolResult(success=True, output={"combined": combined, "strategy": strategy})


# --- Communication Templates ---

async def send_template_email(inputs: dict[str, Any]) -> ToolResult:
    """Send an email using a predefined template (mock)."""
    template_name = inputs.get("template_name", "")
    to = inputs.get("to", "")
    variables = inputs.get("variables", {})

    templates = {
        "welcome": {"subject": "Welcome to our platform!", "body": "Hi {{name}}, welcome aboard!"},
        "invoice": {"subject": "Invoice #{{invoice_id}}", "body": "Dear {{name}}, your invoice for ${{amount}} is ready."},
        "reminder": {"subject": "Reminder: Action Required", "body": "Hi {{name}}, this is a reminder about {{task}}."},
    }

    if template_name not in templates:
        return ToolResult(success=False, error=f"Template '{template_name}' not found. Available: {list(templates.keys())}", retryable=False)

    if not to:
        return ToolResult(success=False, error="Missing required field: 'to'", retryable=False)

    template = templates[template_name]
    subject = template["subject"]
    body = template["body"]
    for key, value in variables.items():
        subject = subject.replace(f"{{{{{key}}}}}", str(value))
        body = body.replace(f"{{{{{key}}}}}", str(value))

    msg_id = f"msg_{random.randint(1000, 9999)}"
    MOCK_EMAILS.append({"id": msg_id, "to": to, "subject": subject, "body": body, "template": template_name})
    return ToolResult(success=True, output={"message_id": msg_id, "to": to, "template": template_name})


# --- AI / Content Generation ---

async def generate_content(inputs: dict[str, Any]) -> ToolResult:
    """Generate content using AI (mock)."""
    content_type = inputs.get("content_type", "text")
    prompt = inputs.get("prompt", "")
    max_length = inputs.get("max_length", 200)

    responses = {
        "email": f"Subject: Follow-up on our conversation\n\nHi,\n\nThank you for your interest. Based on your request '{prompt[:50]}', I wanted to reach out with some relevant information.\n\nBest regards",
        "summary": f"Summary: The key points from the discussion include the main topics related to '{prompt[:50]}'. Action items have been identified and assigned.",
        "response": f"Thank you for your message regarding '{prompt[:50]}'. We appreciate your interest and will follow up shortly with more details.",
        "report": f"REPORT\n{'='*40}\nTopic: {prompt[:50]}\n\nKey Findings:\n1. Initial analysis completed\n2. Recommendations prepared\n3. Next steps outlined\n\nStatus: Draft",
    }

    content = responses.get(content_type, f"Generated content for: {prompt[:100]}")
    content = content[:max_length]

    return ToolResult(success=True, output={
        "content": content, "content_type": content_type,
        "tokens_used": len(content.split()),
    })


async def classify_text(inputs: dict[str, Any]) -> ToolResult:
    """Classify text into categories (mock)."""
    text = inputs.get("text", "")

    categories = {
        "urgent": ["urgent", "emergency", "critical", "asap", "immediately"],
        "billing": ["invoice", "payment", "charge", "refund", "billing"],
        "support": ["help", "issue", "problem", "error", "bug"],
        "general": [],
    }

    text_lower = text.lower()
    for category, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            return ToolResult(success=True, output={
                "category": category, "confidence": 0.92,
                "text": text[:100],
            })

    return ToolResult(success=True, output={"category": "general", "confidence": 0.75, "text": text[:100]})


# --- Scheduling ---

async def list_available_slots(inputs: dict[str, Any]) -> ToolResult:
    """List available time slots for scheduling (mock)."""
    date = inputs.get("date", "")
    duration_minutes = inputs.get("duration_minutes", 30)
    timezone = inputs.get("timezone", "UTC")

    if not date:
        return ToolResult(success=False, error="Missing required field: 'date'", retryable=False)

    slots = []
    for hour in range(9, 18):
        for minute in [0, 30]:
            slots.append({
                "start": f"{date}T{hour:02d}:{minute:02d}:00Z",
                "end": f"{date}T{hour:02d}:{minute + duration_minutes:02d}:00Z",
                "available": random.choice([True, True, True, False]),
            })

    available = [s for s in slots if s["available"]]
    return ToolResult(success=True, output={
        "date": date, "duration_minutes": duration_minutes,
        "available_slots": available, "total_slots": len(slots),
    })


# ---- Tool registry mapping ----

TOOL_IMPLEMENTATIONS: dict[str, Any] = {
    # Original
    "send_email": send_email,
    "send_slack_message": send_slack_message,
    "search_database": search_database,
    "update_database": update_database,
    "create_ticket": create_ticket,
    "create_calendar_event": create_calendar_event,
    "request_human_approval": request_human_approval,
    "wait": wait_tool,
    "extract_invoice_data": extract_invoice_data,
    "validate_invoice": validate_invoice,
    "process_payment": process_payment,
    # Communication
    "send_sms": send_sms,
    "send_notification": send_notification,
    "send_template_email": send_template_email,
    # Data / Analytics
    "run_query": run_query,
    "delete_record": delete_record,
    "aggregate_metrics": aggregate_metrics,
    "export_csv": export_csv,
    # File Operations
    "read_file": read_file,
    "write_file": write_file,
    "delete_file": delete_file,
    "hash_content": hash_content,
    # Integration
    "http_request": http_request,
    # CRM / Sales
    "create_lead": create_lead,
    "score_lead": score_lead,
    # Task / Project Management
    "create_task": create_task,
    "update_task_status": update_task_status,
    # Monitoring
    "check_health": check_health,
    "trigger_alert": trigger_alert,
    # Finance
    "create_invoice": create_invoice,
    "record_transaction": record_transaction,
    "refund_payment": refund_payment,
    # HR / People
    "get_employee_info": get_employee_info,
    "update_employee_record": update_employee_record,
    # Logistics
    "track_shipment": track_shipment,
    "generate_shipping_label": generate_shipping_label,
    # Workflow Utilities
    "transform_data": transform_data,
    "merge_data": merge_data,
    "conditional_router": conditional_router,
    "delay": delay,
    "fan_out": fan_out,
    "fan_in": fan_in,
    # AI / Content
    "generate_content": generate_content,
    "classify_text": classify_text,
    # Scheduling
    "list_available_slots": list_available_slots,
}
