---
type: community
cohesion: 0.20
members: 12
---

# Community 41

**Cohesion:** 0.20 - loosely connected
**Members:** 12 nodes

## Members
- [[Cancel a running execution.]] - rationale - backend/app/api/runs.py
- [[List recent executions.]] - rationale - backend/app/api/runs.py
- [[SSE stream of execution updates — sends steps as they appear in the DB.]] - rationale - backend/app/api/runs.py
- [[Session_7]] - code
- [[_serialize_exec()]] - code - backend/app/api/runs.py
- [[_serialize_step()]] - code - backend/app/api/runs.py
- [[cancel_run()]] - code - backend/app/api/runs.py
- [[event_generator()]] - code - backend/app/api/runs.py
- [[get_6]] - code
- [[list_runs()]] - code - backend/app/api/runs.py
- [[post_5]] - code
- [[stream_run()]] - code - backend/app/api/runs.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_41
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Approvals API]]
- 2 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 1 edge to [[_COMMUNITY_Core Engine Services]]

## Top bridge nodes
- [[cancel_run()]] - degree 6, connects to 2 communities
- [[_serialize_step()]] - degree 4, connects to 2 communities
- [[stream_run()]] - degree 5, connects to 1 community
- [[list_runs()]] - degree 4, connects to 1 community
- [[_serialize_exec()]] - degree 3, connects to 1 community