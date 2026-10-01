---
type: community
cohesion: 0.10
members: 27
---

# Approval Service Models

**Cohesion:** 0.10 - loosely connected
**Members:** 27 nodes

## Members
- [[dot-__init__()]] - code - backend/app/approval/service.py
- [[dot-__init__()_1]] - code - backend/app/approval/service.py
- [[dot-__init__()_2]] - code - backend/app/approval/service.py
- [[dot-approve()]] - code - backend/app/approval/service.py
- [[dot-create_request()]] - code - backend/app/approval/service.py
- [[dot-get()]] - code - backend/app/approval/service.py
- [[dot-list_pending()]] - code - backend/app/approval/service.py
- [[dot-reject()]] - code - backend/app/approval/service.py
- [[dot-test_approval_survives_session_close()]] - code - backend/tests/test_approval.py
- [[Any_2]] - code
- [[ApprovalAlreadyResolvedError]] - code - backend/app/approval/service.py
- [[ApprovalNotFoundError]] - code - backend/app/approval/service.py
- [[ApprovalService]] - code - backend/app/approval/service.py
- [[Approve an approval request.]] - rationale - backend/app/approval/service.py
- [[Create a new approval request.]] - rationale - backend/app/approval/service.py
- [[Create approval, close session, reopen, verify data persists.]] - rationale - backend/tests/test_approval.py
- [[Exception]] - code
- [[Get an approval request by ID.]] - rationale - backend/app/approval/service.py
- [[List all pending approval requests.]] - rationale - backend/app/approval/service.py
- [[Manages human-in-the-loop approval requests.]] - rationale - backend/app/approval/service.py
- [[Raised when an approval request is not found.]] - rationale - backend/app/approval/service.py
- [[Raised when trying to resolve an already-resolved approval.]] - rationale - backend/app/approval/service.py
- [[Reject an approval request.]] - rationale - backend/app/approval/service.py
- [[Session_1]] - code
- [[TestApprovalPersistence]] - code - backend/tests/test_approval.py
- [[approval_service()]] - code - backend/tests/test_approval.py
- [[fixture_1]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Approval_Service_Models
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Core Engine Services]]
- 6 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 4 edges to [[_COMMUNITY_Approvals API]]
- 1 edge to [[_COMMUNITY_Community 71]]
- 1 edge to [[_COMMUNITY_Compiler + AST]]

## Top bridge nodes
- [[ApprovalService]] - degree 24, connects to 4 communities
- [[ApprovalAlreadyResolvedError]] - degree 8, connects to 2 communities
- [[ApprovalNotFoundError]] - degree 8, connects to 2 communities
- [[dot-approve()]] - degree 6, connects to 1 community
- [[dot-reject()]] - degree 6, connects to 1 community