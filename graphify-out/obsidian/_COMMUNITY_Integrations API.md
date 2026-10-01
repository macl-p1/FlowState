---
type: community
cohesion: 0.11
members: 30
---

# Integrations API

**Cohesion:** 0.11 - loosely connected
**Members:** 30 nodes

## Members
- [[BaseModel_8]] - code
- [[Build response with masked integration config.]] - rationale - backend/app/api/integrations.py
- [[CustomToolResponse]] - code - backend/app/schemas/custom_tool.py
- [[Get a single tool's integration config (credentials masked).]] - rationale - backend/app/api/integrations.py
- [[IntegrationConfigUpdate]] - code - backend/app/schemas/integration.py
- [[IntegrationTestRequest]] - code - backend/app/schemas/integration.py
- [[IntegrationTestResponse_1]] - code - backend/app/schemas/integration.py
- [[Integrations API routes — manage real service configs for tools.]] - rationale - backend/app/api/integrations.py
- [[List all tools that have integration configs (credentials masked).]] - rationale - backend/app/api/integrations.py
- [[Remove integration config — reverts tool to mock execution.]] - rationale - backend/app/api/integrations.py
- [[Request to test a real integration connection.]] - rationale - backend/app/schemas/integration.py
- [[Result of testing an integration connection.]] - rationale - backend/app/schemas/integration.py
- [[Schemas for integration config management.]] - rationale - backend/app/schemas/integration.py
- [[Session_10]] - code
- [[Set or remove integration config for a tool.]] - rationale - backend/app/api/integrations.py
- [[Set or update integration config for a tool.]] - rationale - backend/app/schemas/integration.py
- [[Test the real connection for a tool's integration config.]] - rationale - backend/app/api/integrations.py
- [[_get_tool_or_404()]] - code - backend/app/api/integrations.py
- [[_tool_to_response()_1]] - code - backend/app/api/integrations.py
- [[apiintegrations.py]] - code - backend/app/api/integrations.py
- [[delete_2]] - code
- [[get_8]] - code
- [[get_integration()]] - code - backend/app/api/integrations.py
- [[integration.py]] - code - backend/app/schemas/integration.py
- [[list_integrations()]] - code - backend/app/api/integrations.py
- [[post_6]] - code
- [[put_1]] - code
- [[remove_integration()]] - code - backend/app/api/integrations.py
- [[set_integration()]] - code - backend/app/api/integrations.py
- [[verify_integration()]] - code - backend/app/api/integrations.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Integrations_API
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Custom Tools API]]
- 5 edges to [[_COMMUNITY_Integration Tool Tests]]
- 5 edges to [[_COMMUNITY_Approvals API]]
- 4 edges to [[_COMMUNITY_Community 28]]
- 3 edges to [[_COMMUNITY_Core Engine Services]]
- 1 edge to [[_COMMUNITY_Community 47]]

## Top bridge nodes
- [[apiintegrations.py]] - degree 24, connects to 6 communities
- [[CustomToolResponse]] - degree 8, connects to 2 communities
- [[integration.py]] - degree 7, connects to 2 communities
- [[list_integrations()]] - degree 6, connects to 2 communities
- [[_tool_to_response()_1]] - degree 6, connects to 2 communities