---
type: community
cohesion: 0.14
members: 20
---

# Integration Tool Tests

**Cohesion:** 0.14 - loosely connected
**Members:** 20 nodes

## Members
- [[dot-test_does_not_mutate_original()]] - code - backend/tests/test_integrations.py
- [[dot-test_handles_empty_dict()]] - code - backend/tests/test_integrations.py
- [[dot-test_masks_api_key()]] - code - backend/tests/test_integrations.py
- [[dot-test_masks_password()]] - code - backend/tests/test_integrations.py
- [[dot-test_preserves_non_sensitive()]] - code - backend/tests/test_integrations.py
- [[Mask a credential value for safe logging  display.]] - rationale - backend/app/tools/integrations.py
- [[Real integration handlers — execute tools against actual services. Each handler…]] - rationale - backend/app/tools/integrations.py
- [[Return a copy of integration_config with credential values masked.]] - rationale - backend/app/tools/integrations.py
- [[TestCredentialMasking]] - code - backend/tests/test_integrations.py
- [[Tests for integration config and real tool execution.]] - rationale - backend/tests/test_integrations.py
- [[_mask()]] - code - backend/app/tools/integrations.py
- [[_mask_credentials()]] - code - backend/app/tools/integrations.py
- [[hashlib]] - concept
- [[hmac]] - concept
- [[httpx]] - concept
- [[logging]] - concept
- [[test_integrations.py]] - code - backend/tests/test_integrations.py
- [[toolsintegrations.py]] - code - backend/app/tools/integrations.py
- [[unittest_mock]] - concept
- [[urllib_parse]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Integration_Tool_Tests
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Integrations API]]
- 4 edges to [[_COMMUNITY_Integration Handlers]]
- 2 edges to [[_COMMUNITY_Integration Tests]]
- 2 edges to [[_COMMUNITY_Custom Tools API]]
- 2 edges to [[_COMMUNITY_Community 22]]
- 2 edges to [[_COMMUNITY_Community 28]]
- 2 edges to [[_COMMUNITY_Community 21]]
- 2 edges to [[_COMMUNITY_Core Engine Services]]
- 1 edge to [[_COMMUNITY_Tool Implementations]]
- 1 edge to [[_COMMUNITY_Community 40]]
- 1 edge to [[_COMMUNITY_Community 35]]
- 1 edge to [[_COMMUNITY_Community 50]]
- 1 edge to [[_COMMUNITY_Community 27]]

## Top bridge nodes
- [[toolsintegrations.py]] - degree 18, connects to 8 communities
- [[_mask_credentials()]] - degree 17, connects to 4 communities
- [[test_integrations.py]] - degree 10, connects to 4 communities
- [[unittest_mock]] - degree 4, connects to 3 communities
- [[hashlib]] - degree 2, connects to 1 community