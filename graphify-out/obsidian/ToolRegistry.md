---
source_file: "backend/app/tools/registry.py"
type: "code"
community: "Community 44"
location: "L24"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_44
---

# ToolRegistry

## Connections
- [[dot-__init__()_9]] - `method` [EXTRACTED]
- [[dot-_get_custom_tool_by_name()]] - `method` [EXTRACTED]
- [[dot-_register_default_tools()]] - `method` [EXTRACTED]
- [[dot-execute()]] - `method` [EXTRACTED]
- [[dot-get()_1]] - `method` [EXTRACTED]
- [[dot-has()]] - `method` [EXTRACTED]
- [[dot-list_all()]] - `method` [EXTRACTED]
- [[dot-register()]] - `method` [EXTRACTED]
- [[dot-test_create_ticket()]] - `calls` [EXTRACTED]
- [[dot-test_duplicate_registration_raises()]] - `calls` [EXTRACTED]
- [[dot-test_execute_extract_invoice()]] - `calls` [EXTRACTED]
- [[dot-test_execute_human_approval()]] - `calls` [EXTRACTED]
- [[dot-test_execute_process_payment()]] - `calls` [EXTRACTED]
- [[dot-test_execute_search_database()]] - `calls` [EXTRACTED]
- [[dot-test_execute_search_invalid_table()]] - `calls` [EXTRACTED]
- [[dot-test_execute_send_email()]] - `calls` [EXTRACTED]
- [[dot-test_execute_send_email_missing_to()]] - `calls` [EXTRACTED]
- [[dot-test_execute_unknown_tool_raises()]] - `calls` [EXTRACTED]
- [[dot-test_execute_update_database()]] - `calls` [EXTRACTED]
- [[dot-test_execute_wait()]] - `calls` [EXTRACTED]
- [[dot-test_get_returns_none_for_unknown()]] - `calls` [EXTRACTED]
- [[dot-test_has_returns_false_for_unknown()]] - `calls` [EXTRACTED]
- [[dot-test_has_returns_true_for_registered()]] - `calls` [EXTRACTED]
- [[dot-test_list_all_returns_defaults()]] - `calls` [EXTRACTED]
- [[dot-test_register_and_retrieve()]] - `calls` [EXTRACTED]
- [[dot-test_registry_has_all_expected_tools()]] - `calls` [EXTRACTED]
- [[Central registry for all executable tools. The LLM may ONLY call tools from…]] - `rationale_for` [EXTRACTED]
- [[CustomTool]] - `uses` [INFERRED]
- [[TestToolExecution]] - `uses` [INFERRED]
- [[TestToolRegistration]] - `uses` [INFERRED]
- [[Tool]] - `uses` [INFERRED]
- [[ToolResult]] - `uses` [INFERRED]
- [[conftest.py]] - `imports` [EXTRACTED]
- [[mock_registry()]] - `uses` [INFERRED]
- [[registry.py]] - `contains` [EXTRACTED]
- [[test_compiler.py]] - `imports` [EXTRACTED]
- [[test_planner.py]] - `imports` [EXTRACTED]
- [[test_tools.py]] - `imports` [EXTRACTED]
- [[tool_registry()]] - `uses` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Community_44