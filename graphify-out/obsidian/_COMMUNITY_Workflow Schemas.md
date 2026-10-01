---
type: community
cohesion: 0.09
members: 26
---

# Workflow Schemas

**Cohesion:** 0.09 - loosely connected
**Members:** 26 nodes

## Members
- [[dot-validate_edges()]] - code - backend/app/schemas/workflow.py
- [[dot-validate_nodes()]] - code - backend/app/schemas/workflow.py
- [[dot-validate_trigger_exists()]] - code - backend/app/schemas/workflow.py
- [[Create a SQLite in-memory database engine for the test session.]] - rationale - backend/tests/conftest.py
- [[Create a fresh database session for each test, wrapping in a transaction that…]] - rationale - backend/tests/conftest.py
- [[Customer complaint workflow for reuse.]] - rationale - backend/tests/conftest.py
- [[Employee onboarding workflow for reuse.]] - rationale - backend/tests/conftest.py
- [[Fresh tool registry with all default tools.]] - rationale - backend/tests/conftest.py
- [[Invoice processing workflow for reuse.]] - rationale - backend/tests/conftest.py
- [[Onboarding workflow persisted in the database.]] - rationale - backend/tests/conftest.py
- [[Registry with seeded mock data.]] - rationale - backend/tests/conftest.py
- [[Universal workflow definition.]] - rationale - backend/app/schemas/workflow.py
- [[Workflow]] - code - backend/app/schemas/workflow.py
- [[WorkflowRunner with database and tool registry.]] - rationale - backend/tests/conftest.py
- [[db_engine()]] - code - backend/tests/conftest.py
- [[db_session()]] - code - backend/tests/conftest.py
- [[field_validator]] - code
- [[fixture_2]] - code
- [[model_validator]] - code
- [[persisted_onboarding_workflow()]] - code - backend/tests/conftest.py
- [[registry_with_context()]] - code - backend/tests/conftest.py
- [[runner()]] - code - backend/tests/conftest.py
- [[sample_complaint_workflow()]] - code - backend/tests/conftest.py
- [[sample_invoice_workflow()]] - code - backend/tests/conftest.py
- [[sample_onboarding_workflow()]] - code - backend/tests/conftest.py
- [[tool_registry()]] - code - backend/tests/conftest.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workflow_Schemas
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Core Engine Services]]
- 4 edges to [[_COMMUNITY_Community 21]]
- 4 edges to [[_COMMUNITY_Workflow Schema Types]]
- 3 edges to [[_COMMUNITY_Compiler + AST]]
- 3 edges to [[_COMMUNITY_Community 36]]
- 2 edges to [[_COMMUNITY_Community 50]]
- 2 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 1 edge to [[_COMMUNITY_Community 77]]
- 1 edge to [[_COMMUNITY_Community 32]]
- 1 edge to [[_COMMUNITY_Community 57]]
- 1 edge to [[_COMMUNITY_Community 58]]
- 1 edge to [[_COMMUNITY_Community 44]]

## Top bridge nodes
- [[Workflow]] - degree 33, connects to 11 communities
- [[runner()]] - degree 4, connects to 2 communities
- [[tool_registry()]] - degree 4, connects to 2 communities
- [[fixture_2]] - degree 10, connects to 1 community
- [[persisted_onboarding_workflow()]] - degree 4, connects to 1 community