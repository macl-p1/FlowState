---
type: community
cohesion: 0.07
members: 47
---

# Approvals API

**Cohesion:** 0.07 - loosely connected
**Members:** 47 nodes

## Members
- [[ApplyPatchRequest]] - code - backend/app/schemas/suggestions.py
- [[Approvals API routes.]] - rationale - backend/app/api/approvals.py
- [[Approve an approval request and resume the workflow.]] - rationale - backend/app/api/approvals.py
- [[ApproveRequest]] - code - backend/app/api/approvals.py
- [[BaseModel_4]] - code
- [[BaseModel_5]] - code
- [[Database configuration and session management.]] - rationale - backend/app/database.py
- [[Dependency for FastAPI routes.]] - rationale - backend/app/database.py
- [[FastAPI]] - code
- [[Genealogy API routes — version history, branching, and lineage.]] - rationale - backend/app/api/genealogy.py
- [[List all pending approvals.]] - rationale - backend/app/api/approvals.py
- [[OrchestrAI Backend — FastAPI application entry point.]] - rationale - backend/app/main.py
- [[Reject an approval request and cancel the workflow.]] - rationale - backend/app/api/approvals.py
- [[RejectRequest]] - code - backend/app/api/approvals.py
- [[Request to apply a suggestion's patch to a workflow.]] - rationale - backend/app/schemas/suggestions.py
- [[Schemas for the suggestions  cross-pollination feature.]] - rationale - backend/app/schemas/suggestions.py
- [[Session_5]] - code
- [[Session_6]] - code
- [[Single cross-pollination suggestion.]] - rationale - backend/app/schemas/suggestions.py
- [[Startup and shutdown events.]] - rationale - backend/app/main.py
- [[SuggestionResponse]] - code - backend/app/schemas/suggestions.py
- [[Suggestions API routes — cross-pollination and pattern suggestions.]] - rationale - backend/app/api/suggestions.py
- [[SuggestionsResponse_1]] - code - backend/app/schemas/suggestions.py
- [[Wrapper for a list of suggestions.]] - rationale - backend/app/schemas/suggestions.py
- [[api__init__.py]] - code - backend/app/api/__init__.py
- [[apigenealogy.py]] - code - backend/app/api/genealogy.py
- [[apisuggestions.py]] - code - backend/app/api/suggestions.py
- [[approvals.py]] - code - backend/app/api/approvals.py
- [[approve_request()]] - code - backend/app/api/approvals.py
- [[contextlib]] - concept
- [[database.py]] - code - backend/app/database.py
- [[fastapi_middleware_cors]] - concept
- [[fastapi_responses]] - concept
- [[get_4]] - code
- [[get_5]] - code
- [[get_db()]] - code - backend/app/database.py
- [[health()]] - code - backend/app/main.py
- [[lifespan()]] - code - backend/app/main.py
- [[list_approvals()]] - code - backend/app/api/approvals.py
- [[main.py]] - code - backend/app/main.py
- [[post_4]] - code
- [[pydantic]] - concept
- [[reject_request()]] - code - backend/app/api/approvals.py
- [[runs.py]] - code - backend/app/api/runs.py
- [[schemassuggestions.py]] - code - backend/app/schemas/suggestions.py
- [[sqlalchemy_ext_declarative]] - concept
- [[uvicorn]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Approvals_API
SORT file.name ASC
```

## Connections to other communities
- 32 edges to [[_COMMUNITY_Core Engine Services]]
- 7 edges to [[_COMMUNITY_Community 29]]
- 7 edges to [[_COMMUNITY_Suggestions + Cross-Pollination]]
- 5 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 5 edges to [[_COMMUNITY_Community 28]]
- 5 edges to [[_COMMUNITY_Integrations API]]
- 5 edges to [[_COMMUNITY_Community 41]]
- 4 edges to [[_COMMUNITY_Approval Service Models]]
- 3 edges to [[_COMMUNITY_Community 60]]
- 3 edges to [[_COMMUNITY_Community 35]]
- 3 edges to [[_COMMUNITY_Community 40]]
- 2 edges to [[_COMMUNITY_Community 66]]
- 1 edge to [[_COMMUNITY_Community 42]]
- 1 edge to [[_COMMUNITY_Community 62]]
- 1 edge to [[_COMMUNITY_Workflow Schema Types]]
- 1 edge to [[_COMMUNITY_Community 21]]
- 1 edge to [[_COMMUNITY_Community 47]]
- 1 edge to [[_COMMUNITY_Community 34]]
- 1 edge to [[_COMMUNITY_Community 36]]
- 1 edge to [[_COMMUNITY_Community 50]]

## Top bridge nodes
- [[database.py]] - degree 24, connects to 8 communities
- [[pydantic]] - degree 12, connects to 7 communities
- [[main.py]] - degree 21, connects to 6 communities
- [[runs.py]] - degree 20, connects to 6 communities
- [[FastAPI]] - degree 11, connects to 5 communities