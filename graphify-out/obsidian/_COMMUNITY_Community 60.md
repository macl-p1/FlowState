---
type: community
cohesion: 0.29
members: 7
---

# Community 60

**Cohesion:** 0.29 - loosely connected
**Members:** 7 nodes

## Members
- [[API-key authentication dependency.]] - rationale - backend/app/api/auth.py
- [[Authenticate requests via API key. - If settings.api_key is empty → dev mode,…]] - rationale - backend/app/api/auth.py
- [[HTTPAuthorizationCredentials]] - code
- [[Request]] - code
- [[auth.py]] - code - backend/app/api/auth.py
- [[fastapi_security]] - concept
- [[get_api_key()]] - code - backend/app/api/auth.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_60
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Approvals API]]
- 1 edge to [[_COMMUNITY_Community 40]]

## Top bridge nodes
- [[auth.py]] - degree 6, connects to 2 communities
- [[get_api_key()]] - degree 5, connects to 1 community