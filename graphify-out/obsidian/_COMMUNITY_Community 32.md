---
type: community
cohesion: 0.31
members: 15
---

# Community 32

**Cohesion:** 0.31 - loosely connected
**Members:** 15 nodes

## Members
- [[dot-test_planner_exhausts_retries()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_generates_invoice_workflow()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_generates_onboarding_workflow()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_linear_workflow()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_metadata_extraction()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_no_api_key_graceful_failure()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_rejects_unknown_tools()]] - code - backend/tests/test_planner.py
- [[dot-test_planner_repairs_malformed_output()]] - code - backend/tests/test_planner.py
- [[Converts natural language descriptions into validated workflow JSON.]] - rationale - backend/app/agents/planner.py
- [[Create a mock Anthropic client that returns a fixed response. Note Anthropic…]] - rationale - backend/tests/test_planner.py
- [[PlannerAgent]] - code - backend/app/agents/planner.py
- [[TestPlannerAgent]] - code - backend/tests/test_planner.py
- [[Without an API key, planner should still return a valid result via fallback.]] - rationale - backend/tests/test_planner.py
- [[asyncio_1]] - code
- [[make_mock_client()]] - code - backend/tests/test_planner.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_32
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Community 21]]
- 4 edges to [[_COMMUNITY_Community 54]]
- 2 edges to [[_COMMUNITY_Community 40]]
- 2 edges to [[_COMMUNITY_Core Engine Services]]
- 2 edges to [[_COMMUNITY_Community 79]]
- 1 edge to [[_COMMUNITY_Workflow Schemas]]
- 1 edge to [[_COMMUNITY_Community 77]]
- 1 edge to [[_COMMUNITY_Community 25]]

## Top bridge nodes
- [[PlannerAgent]] - degree 24, connects to 7 communities
- [[TestPlannerAgent]] - degree 10, connects to 1 community
- [[make_mock_client()]] - degree 7, connects to 1 community
- [[dot-test_planner_exhausts_retries()]] - degree 4, connects to 1 community
- [[dot-test_planner_repairs_malformed_output()]] - degree 4, connects to 1 community