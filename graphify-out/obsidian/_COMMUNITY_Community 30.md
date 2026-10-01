---
type: community
cohesion: 0.12
members: 16
---

# Community 30

**Cohesion:** 0.12 - loosely connected
**Members:** 16 nodes

## Members
- [[dot-test_dev_mode_no_auth_required()]] - code - backend/tests/test_api.py
- [[dot-test_health_always_public()]] - code - backend/tests/test_api.py
- [[dot-test_stream_accepts_query_param_key()]] - code - backend/tests/test_api.py
- [[dot-test_workflows_accept_bearer_token()]] - code - backend/tests/test_api.py
- [[dot-test_workflows_accept_correct_header()]] - code - backend/tests/test_api.py
- [[dot-test_workflows_reject_without_key()]] - code - backend/tests/test_api.py
- [[dot-test_workflows_reject_wrong_key()]] - code - backend/tests/test_api.py
- [[Health endpoint should never require auth.]] - rationale - backend/tests/test_api.py
- [[Non-health endpoints should reject requests without a key when API_KEY is set.]] - rationale - backend/tests/test_api.py
- [[Requests with the correct X-API-Key header should succeed.]] - rationale - backend/tests/test_api.py
- [[Requests with the key in Authorization Bearer should succeed.]] - rationale - backend/tests/test_api.py
- [[Requests with the wrong API key should be rejected.]] - rationale - backend/tests/test_api.py
- [[SSE stream should accept the key as a query param.]] - rationale - backend/tests/test_api.py
- [[TestApiKeyAuth]] - code - backend/tests/test_api.py
- [[Tests for X-API-Key authentication.]] - rationale - backend/tests/test_api.py
- [[When API_KEY is empty (dev mode), no auth should be required.]] - rationale - backend/tests/test_api.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_30
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Core Engine Services]]

## Top bridge nodes
- [[TestApiKeyAuth]] - degree 9, connects to 1 community