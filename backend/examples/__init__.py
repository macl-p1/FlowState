"""Example workflow definitions."""

INVOICE_PROCESSING = {
    "name": "Invoice Processing",
    "description": "Process incoming invoices with validation and approval for large amounts",
    "nodes": [
        {"id": "n1", "type": "trigger", "name": "Invoice Received"},
        {"id": "n2", "type": "action", "name": "Extract Invoice Data", "tool": "extract_invoice_data", "inputs": {"document": "invoice.pdf"}},
        {"id": "n3", "type": "action", "name": "Find Purchase Order", "tool": "search_database", "inputs": {"table": "purchase_orders", "query": "active"}},
        {"id": "n4", "type": "condition", "name": "Amount Check", "expression": "amount > 10000"},
        {"id": "n5", "type": "approval", "name": "Manager Approval", "reason": "Invoice exceeds approval threshold of $100,000"},
        {"id": "n6", "type": "action", "name": "Process Payment", "tool": "process_payment", "inputs": {"invoice_id": "INV-2024-001", "amount": 45000}},
        {"id": "n7", "type": "end", "name": "Workflow Complete"},
    ],
    "edges": [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "n3"},
        {"from": "n3", "to": "n4"},
        {"from": "n4", "to": "n5", "condition": "true"},
        {"from": "n4", "to": "n6", "condition": "false"},
        {"from": "n5", "to": "n6"},
        {"from": "n6", "to": "n7"},
    ],
}

EMPLOYEE_ONBOARDING = {
    "name": "Employee Onboarding",
    "description": "Onboard a new employee with document verification and notifications",
    "nodes": [
        {"id": "n1", "type": "trigger", "name": "Employee Added"},
        {"id": "n2", "type": "action", "name": "Request Documents", "tool": "send_email", "inputs": {"to": "employee@example.com", "subject": "Documents needed", "body": "Please submit your documents."}},
        {"id": "n3", "type": "condition", "name": "Documents Complete", "expression": "documents_verified"},
        {"id": "n4", "type": "action", "name": "Notify HR", "tool": "send_slack_message", "inputs": {"channel": "#hr", "message": "New employee onboarded"}},
        {"id": "n5", "type": "action", "name": "Send Reminder", "tool": "send_email", "inputs": {"to": "employee@example.com", "subject": "Reminder", "body": "Still waiting for docs."}},
        {"id": "n6", "type": "action", "name": "Notify Manager", "tool": "send_email", "inputs": {"to": "manager@example.com", "subject": "New hire", "body": "Employee joined."}},
        {"id": "n7", "type": "end", "name": "Onboarding Complete"},
    ],
    "edges": [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "n3"},
        {"from": "n3", "to": "n4", "condition": "true"},
        {"from": "n3", "to": "n5", "condition": "false"},
        {"from": "n4", "to": "n6"},
        {"from": "n5", "to": "n6"},
        {"from": "n6", "to": "n7"},
    ],
}

CUSTOMER_SUPPORT = {
    "name": "Customer Complaint Resolution",
    "description": "Handle customer complaints with identification, investigation, and resolution",
    "nodes": [
        {"id": "n1", "type": "trigger", "name": "Complaint Received"},
        {"id": "n2", "type": "action", "name": "Identify Customer", "tool": "search_database", "inputs": {"table": "employees", "query": "active"}},
        {"id": "n3", "type": "action", "name": "Find Order", "tool": "search_database", "inputs": {"table": "purchase_orders", "query": "active"}},
        {"id": "n4", "type": "action", "name": "Check Delivery", "tool": "search_database", "inputs": {"table": "invoices", "query": "active"}},
        {"id": "n5", "type": "action", "name": "Determine Issue", "tool": "create_ticket", "inputs": {"title": "Customer complaint", "priority": "high", "assignee": "support"}},
        {"id": "n6", "type": "condition", "name": "Needs Escalation", "expression": "needs_escalation"},
        {"id": "n7", "type": "action", "name": "Generate Response", "tool": "send_email", "inputs": {"to": "customer@example.com", "subject": "Your complaint", "body": "We are looking into it."}},
        {"id": "n8", "type": "action", "name": "Escalate", "tool": "create_ticket", "inputs": {"title": "Escalated complaint", "priority": "critical", "assignee": "manager"}},
        {"id": "n9", "type": "end", "name": "Resolved"},
    ],
    "edges": [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "n3"},
        {"from": "n3", "to": "n4"},
        {"from": "n4", "to": "n5"},
        {"from": "n5", "to": "n6"},
        {"from": "n6", "to": "n7", "condition": "false"},
        {"from": "n6", "to": "n8", "condition": "true"},
        {"from": "n7", "to": "n9"},
        {"from": "n8", "to": "n9"},
    ],
}
