---
type: community
cohesion: 0.27
members: 12
---

# Community 44

**Cohesion:** 0.27 - loosely connected
**Members:** 12 nodes

## Members
- [[dot-has()]] - code - backend/app/tools/registry.py
- [[dot-test_duplicate_registration_raises()]] - code - backend/tests/test_tools.py
- [[dot-test_get_returns_none_for_unknown()]] - code - backend/tests/test_tools.py
- [[dot-test_has_returns_false_for_unknown()]] - code - backend/tests/test_tools.py
- [[dot-test_has_returns_true_for_registered()]] - code - backend/tests/test_tools.py
- [[dot-test_list_all_returns_defaults()]] - code - backend/tests/test_tools.py
- [[dot-test_register_and_retrieve()]] - code - backend/tests/test_tools.py
- [[dot-test_registry_has_all_expected_tools()]] - code - backend/tests/test_tools.py
- [[Central registry for all executable tools. The LLM may ONLY call tools from…]] - rationale - backend/app/tools/registry.py
- [[Check if a tool is registered.]] - rationale - backend/app/tools/registry.py
- [[TestToolRegistration]] - code - backend/tests/test_tools.py
- [[ToolRegistry]] - code - backend/app/tools/registry.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_44
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Community 37]]
- 6 edges to [[_COMMUNITY_Community 43]]
- 5 edges to [[_COMMUNITY_Community 35]]
- 2 edges to [[_COMMUNITY_Community 21]]
- 2 edges to [[_COMMUNITY_Community 72]]
- 2 edges to [[_COMMUNITY_Community 62]]
- 1 edge to [[_COMMUNITY_Custom Tools API]]
- 1 edge to [[_COMMUNITY_Community 22]]
- 1 edge to [[_COMMUNITY_Core Engine Services]]
- 1 edge to [[_COMMUNITY_Community 36]]
- 1 edge to [[_COMMUNITY_Workflow Schemas]]

## Top bridge nodes
- [[ToolRegistry]] - degree 39, connects to 11 communities
- [[TestToolRegistration]] - degree 11, connects to 2 communities
- [[dot-test_duplicate_registration_raises()]] - degree 3, connects to 1 community
- [[dot-test_register_and_retrieve()]] - degree 3, connects to 1 community