---
type: community
cohesion: 0.11
members: 43
---

# Core Engine Services

**Cohesion:** 0.11 - loosely connected
**Members:** 43 nodes

## Members
- [[dot-test_health_endpoint()]] - code - backend/tests/test_api.py
- [[Approval  HITL service tests.]] - rationale - backend/tests/test_approval.py
- [[ApprovalRequestModel]] - code - backend/app/models/__init__.py
- [[Base_2]] - code
- [[Create a pending approval request in the database.]] - rationale - backend/tests/conftest.py
- [[Database.py (SQLAlchemy)]] - code - CLAUDE.md
- [[Example workflow definitions.]] - rationale - backend/examples/__init__.py
- [[Execution schema definitions — Pydantic models for workflow runs and steps.]] - rationale - backend/app/schemas/execution.py
- [[Genealogy models — workflow version history and lineage tracking.]] - rationale - backend/app/models/genealogy.py
- [[Genealogy service — workflow version tracking, branching, and lineage.]] - rationale - backend/app/genealogy/service.py
- [[Helper create a workflow execution that's paused at the approval node.]] - rationale - backend/tests/conftest.py
- [[Human Approval Service — pauseresume workflow execution.]] - rationale - backend/app/approval/service.py
- [[Invoice workflow persisted in the database.]] - rationale - backend/tests/conftest.py
- [[SQLAlchemy ORM]] - code - CLAUDE.md
- [[SQLAlchemy ORM models.]] - rationale - backend/app/models/__init__.py
- [[Shared pytest fixtures for all tests.]] - rationale - backend/tests/conftest.py
- [[StepExecutionModel]] - code - backend/app/models/__init__.py
- [[TestHealth]] - code - backend/tests/test_api.py
- [[Workflow Runner — execution engine that runs compiled workflows.]] - rationale - backend/app/engine/runner.py
- [[WorkflowExecutionModel]] - code - backend/app/models/__init__.py
- [[WorkflowModel]] - code - backend/app/models/__init__.py
- [[any_5]] - code
- [[approvalservice.py]] - code - backend/app/approval/service.py
- [[conftest.py]] - code - backend/tests/conftest.py
- [[create_execution_at_approval()]] - code - backend/tests/conftest.py
- [[create_pending_approval()]] - code - backend/tests/conftest.py
- [[datetime]] - concept
- [[examples__init__.py]] - code - backend/examples/__init__.py
- [[execution.py]] - code - backend/app/schemas/execution.py
- [[fastapi_testclient]] - concept
- [[gen_id()]] - code - backend/app/models/__init__.py
- [[genealogyservice.py]] - code - backend/app/genealogy/service.py
- [[models__init__.py]] - code - backend/app/models/__init__.py
- [[modelsgenealogy.py]] - code - backend/app/models/genealogy.py
- [[persisted_invoice_workflow()]] - code - backend/tests/conftest.py
- [[runner.py]] - code - backend/app/engine/runner.py
- [[sqlalchemy]] - concept
- [[sqlalchemy_pool]] - concept
- [[test_api.py]] - code - backend/tests/test_api.py
- [[test_approval.py]] - code - backend/tests/test_approval.py
- [[typing]] - concept
- [[uuid]] - concept
- [[workflows.py]] - code - backend/app/api/workflows.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Core_Engine_Services
SORT file.name ASC
```

## Connections to other communities
- 35 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 32 edges to [[_COMMUNITY_Approvals API]]
- 16 edges to [[_COMMUNITY_Approval Service Models]]
- 16 edges to [[_COMMUNITY_Workflow Schemas]]
- 16 edges to [[_COMMUNITY_Compiler + AST]]
- 12 edges to [[_COMMUNITY_Workflow Schema Types]]
- 12 edges to [[_COMMUNITY_Community 34]]
- 11 edges to [[_COMMUNITY_Community 25]]
- 8 edges to [[_COMMUNITY_Community 35]]
- 7 edges to [[_COMMUNITY_Suggestions + Cross-Pollination]]
- 6 edges to [[_COMMUNITY_Community 21]]
- 4 edges to [[_COMMUNITY_Community 56]]
- 4 edges to [[_COMMUNITY_Community 28]]
- 4 edges to [[_COMMUNITY_Community 50]]
- 3 edges to [[_COMMUNITY_Community 22]]
- 3 edges to [[_COMMUNITY_Community 42]]
- 3 edges to [[_COMMUNITY_Community 49]]
- 3 edges to [[_COMMUNITY_Community 26]]
- 3 edges to [[_COMMUNITY_Integrations API]]
- 2 edges to [[_COMMUNITY_Community 32]]
- 2 edges to [[_COMMUNITY_Tool Implementations]]
- 2 edges to [[_COMMUNITY_Integration Tool Tests]]
- 2 edges to [[_COMMUNITY_Community 47]]
- 1 edge to [[_COMMUNITY_Custom Tools API]]
- 1 edge to [[_COMMUNITY_Community 30]]
- 1 edge to [[_COMMUNITY_Community 44]]
- 1 edge to [[_COMMUNITY_Community 41]]
- 1 edge to [[_COMMUNITY_Community 70]]
- 1 edge to [[_COMMUNITY_Community 71]]
- 1 edge to [[_COMMUNITY_Community 73]]
- 1 edge to [[_COMMUNITY_Community 74]]
- 1 edge to [[_COMMUNITY_Community 75]]
- 1 edge to [[_COMMUNITY_Community 76]]
- 1 edge to [[_COMMUNITY_Community 78]]
- 1 edge to [[_COMMUNITY_Community 55]]
- 1 edge to [[_COMMUNITY_Community 27]]
- 1 edge to [[_COMMUNITY_Community 40]]
- 1 edge to [[_COMMUNITY_Community 31]]
- 1 edge to [[_COMMUNITY_Community 45]]
- 1 edge to [[_COMMUNITY_Community 46]]

## Top bridge nodes
- [[test_api.py]] - degree 32, connects to 16 communities
- [[conftest.py]] - degree 44, connects to 12 communities
- [[typing]] - degree 22, connects to 12 communities
- [[runner.py]] - degree 38, connects to 10 communities
- [[workflows.py]] - degree 31, connects to 9 communities