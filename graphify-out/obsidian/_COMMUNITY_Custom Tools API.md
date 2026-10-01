---
type: community
cohesion: 0.17
members: 21
---

# Custom Tools API

**Cohesion:** 0.17 - loosely connected
**Members:** 21 nodes

## Members
- [[Base]] - code
- [[Create a new custom tool (starts as draft).]] - rationale - backend/app/api/custom_tools.py
- [[CustomTool]] - code - backend/app/models/custom_tool.py
- [[Delete a custom tool.]] - rationale - backend/app/api/custom_tools.py
- [[Get a specific custom tool.]] - rationale - backend/app/api/custom_tools.py
- [[List all custom (user-created) tools.]] - rationale - backend/app/api/custom_tools.py
- [[List custom tools filtered by type.]] - rationale - backend/app/api/custom_tools.py
- [[Register a verified custom tool into the runtime registry.]] - rationale - backend/app/api/custom_tools.py
- [[Return built-in tools + custom tools in one unified list.]] - rationale - backend/app/api/custom_tools.py
- [[Session_2]] - code
- [[_tool_to_response()]] - code - backend/app/api/custom_tools.py
- [[create_custom_tool()]] - code - backend/app/api/custom_tools.py
- [[delete]] - code
- [[delete_custom_tool()]] - code - backend/app/api/custom_tools.py
- [[get_1]] - code
- [[get_custom_tool()]] - code - backend/app/api/custom_tools.py
- [[list_all_tools()]] - code - backend/app/api/custom_tools.py
- [[list_custom_tools()]] - code - backend/app/api/custom_tools.py
- [[list_custom_tools_by_type()]] - code - backend/app/api/custom_tools.py
- [[post_1]] - code
- [[register_custom_tool()]] - code - backend/app/api/custom_tools.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Custom_Tools_API
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Community 28]]
- 7 edges to [[_COMMUNITY_Community 47]]
- 6 edges to [[_COMMUNITY_Integrations API]]
- 2 edges to [[_COMMUNITY_Integration Tool Tests]]
- 1 edge to [[_COMMUNITY_Integration Tests]]
- 1 edge to [[_COMMUNITY_Core Engine Services]]
- 1 edge to [[_COMMUNITY_Community 35]]
- 1 edge to [[_COMMUNITY_Community 61]]
- 1 edge to [[_COMMUNITY_Community 44]]

## Top bridge nodes
- [[CustomTool]] - degree 24, connects to 9 communities
- [[_tool_to_response()]] - degree 10, connects to 4 communities
- [[Session_2]] - degree 10, connects to 2 communities
- [[create_custom_tool()]] - degree 8, connects to 2 communities
- [[list_all_tools()]] - degree 7, connects to 2 communities