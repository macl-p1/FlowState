---
source_file: "backend/app/schemas/execution.py"
type: "code"
community: "Workflow Runner Errors"
location: "L20"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workflow_Runner_Errors
---

# StepStatus

## Connections
- [[dot-_to_pydantic()]] - `calls` [EXTRACTED]
- [[Enum_1]] - `inherits` [EXTRACTED]
- [[Individual step execution states.]] - `rationale_for` [EXTRACTED]
- [[StepExecutionModel]] - `uses` [INFERRED]
- [[TestExecutionStatuses]] - `uses` [INFERRED]
- [[WorkflowRunner]] - `uses` [INFERRED]
- [[_make_node_executor()]] - `uses` [INFERRED]
- [[compiler.py]] - `imports` [EXTRACTED]
- [[conftest.py]] - `imports` [EXTRACTED]
- [[create_execution_at_approval()]] - `uses` [INFERRED]
- [[execution.py]] - `contains` [EXTRACTED]
- [[models__init__.py]] - `imports` [EXTRACTED]
- [[runner.py]] - `imports` [EXTRACTED]
- [[str_2]] - `inherits` [EXTRACTED]
- [[test_api.py]] - `imports` [EXTRACTED]
- [[test_runner.py]] - `imports` [EXTRACTED]
- [[test_runner_happy_path_simple_workflow()]] - `uses` [INFERRED]
- [[test_runner_steps_have_observability()]] - `uses` [INFERRED]
- [[test_schemas.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workflow_Runner_Errors