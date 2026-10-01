---
type: community
cohesion: 0.20
members: 10
---

# Community 49

**Cohesion:** 0.20 - loosely connected
**Members:** 10 nodes

## Members
- [[dot-__init__()_12]] - code - backend/app/agents/compiler.py
- [[dot-_create_execution_record()]] - code - backend/app/engine/runner.py
- [[dot-get_compiled()]] - code - backend/app/agents/compiler.py
- [[dot-get_node()]] - code - backend/app/agents/compiler.py
- [[Any_4]] - code
- [[CompiledWorkflow]] - code - backend/app/agents/compiler.py
- [[Create the initial execution record in the database.]] - rationale - backend/app/engine/runner.py
- [[Get node definition by ID.]] - rationale - backend/app/agents/compiler.py
- [[StateGraph]] - code
- [[Wrapper around a compiled LangGraph StateGraph.]] - rationale - backend/app/agents/compiler.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_49
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 3 edges to [[_COMMUNITY_Core Engine Services]]
- 2 edges to [[_COMMUNITY_Compiler + AST]]

## Top bridge nodes
- [[CompiledWorkflow]] - degree 9, connects to 3 communities
- [[dot-_create_execution_record()]] - degree 7, connects to 2 communities
- [[Any_4]] - degree 2, connects to 1 community