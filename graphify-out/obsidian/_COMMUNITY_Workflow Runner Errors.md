---
type: community
cohesion: 0.10
members: 44
---

# Workflow Runner Errors

**Cohesion:** 0.10 - loosely connected
**Members:** 44 nodes

## Members
- [[dot-_to_pydantic()]] - code - backend/app/engine/runner.py
- [[dot-cancel()]] - code - backend/app/engine/runner.py
- [[dot-resume()]] - code - backend/app/engine/runner.py
- [[dot-run()]] - code - backend/app/engine/runner.py
- [[After approving, workflow should complete.]] - rationale - backend/tests/test_runner.py
- [[Cancel a running workflow.]] - rationale - backend/app/engine/runner.py
- [[Cancel a running workflow._1]] - rationale - backend/tests/test_runner.py
- [[Complete a simple workflow end-to-end (or pause for approval).]] - rationale - backend/tests/test_runner.py
- [[Context variables should be available to condition nodes.]] - rationale - backend/tests/test_runner.py
- [[Convert ORM model to Pydantic schema.]] - rationale - backend/app/engine/runner.py
- [[Employee onboarding workflow runs to completion.]] - rationale - backend/tests/test_runner.py
- [[Enum_1]] - code
- [[Every step should have timestamps, inputs, outputs.]] - rationale - backend/tests/test_runner.py
- [[Exception_3]] - code
- [[Execute a workflow by ID. Returns the execution record with all steps.]] - rationale - backend/app/engine/runner.py
- [[Executes compiled workflows with full observability. Manages the execution…]] - rationale - backend/app/engine/runner.py
- [[ExecutionStatus]] - code - backend/app/schemas/execution.py
- [[Individual step execution states.]] - rationale - backend/app/schemas/execution.py
- [[Record of a full workflow run.]] - rationale - backend/app/schemas/execution.py
- [[Rejecting an approval and cancelling the workflow.]] - rationale - backend/tests/test_runner.py
- [[Resume a workflow that was paused for approval. After approval, continue…]] - rationale - backend/app/engine/runner.py
- [[Runner  execution engine tests.]] - rationale - backend/tests/test_runner.py
- [[RunnerError]] - code - backend/app/engine/runner.py
- [[Running the same workflow multiple times should produce independent executions.]] - rationale - backend/tests/test_runner.py
- [[StepStatus]] - code - backend/app/schemas/execution.py
- [[Workflow execution lifecycle states.]] - rationale - backend/app/schemas/execution.py
- [[Workflow with approval node should pause and wait.]] - rationale - backend/tests/test_runner.py
- [[WorkflowExecution]] - code - backend/app/schemas/execution.py
- [[WorkflowNotFoundError]] - code - backend/app/engine/runner.py
- [[WorkflowRunner]] - code - backend/app/engine/runner.py
- [[_persist_steps()]] - code - backend/app/engine/runner.py
- [[asyncio_3]] - code
- [[str_2]] - code
- [[test_runner.py]] - code - backend/tests/test_runner.py
- [[test_runner_cancel_running_workflow()]] - code - backend/tests/test_runner.py
- [[test_runner_context_passed_through()]] - code - backend/tests/test_runner.py
- [[test_runner_happy_path_simple_workflow()]] - code - backend/tests/test_runner.py
- [[test_runner_multiple_runs_no_state_leakage()]] - code - backend/tests/test_runner.py
- [[test_runner_onboarding_workflow()]] - code - backend/tests/test_runner.py
- [[test_runner_pauses_at_approval()]] - code - backend/tests/test_runner.py
- [[test_runner_rejects_and_cancels()]] - code - backend/tests/test_runner.py
- [[test_runner_resumes_after_approval()]] - code - backend/tests/test_runner.py
- [[test_runner_steps_have_observability()]] - code - backend/tests/test_runner.py
- [[test_runner_unknown_workflow_raises()]] - code - backend/tests/test_runner.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workflow_Runner_Errors
SORT file.name ASC
```

## Connections to other communities
- 35 edges to [[_COMMUNITY_Core Engine Services]]
- 11 edges to [[_COMMUNITY_Compiler + AST]]
- 6 edges to [[_COMMUNITY_Approval Service Models]]
- 6 edges to [[_COMMUNITY_Community 50]]
- 5 edges to [[_COMMUNITY_Approvals API]]
- 4 edges to [[_COMMUNITY_Community 49]]
- 3 edges to [[_COMMUNITY_Community 22]]
- 2 edges to [[_COMMUNITY_Workflow Schemas]]
- 2 edges to [[_COMMUNITY_Community 41]]
- 1 edge to [[_COMMUNITY_Community 25]]
- 1 edge to [[_COMMUNITY_Community 35]]

## Top bridge nodes
- [[WorkflowRunner]] - degree 38, connects to 9 communities
- [[test_runner.py]] - degree 27, connects to 5 communities
- [[ExecutionStatus]] - degree 27, connects to 3 communities
- [[StepStatus]] - degree 19, connects to 3 communities
- [[dot-_to_pydantic()]] - degree 11, connects to 3 communities