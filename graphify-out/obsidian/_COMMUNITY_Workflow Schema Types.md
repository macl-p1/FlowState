---
type: community
cohesion: 0.14
members: 22
---

# Workflow Schema Types

**Cohesion:** 0.14 - loosely connected
**Members:** 22 nodes

## Members
- [[ActionNode]] - code - backend/app/schemas/workflow.py
- [[ApprovalNode]] - code - backend/app/schemas/workflow.py
- [[BaseModel]] - code
- [[ConditionNode]] - code - backend/app/schemas/workflow.py
- [[Deserialize workflow from JSON-compatible dict.]] - rationale - backend/app/schemas/workflow.py
- [[Edge]] - code - backend/app/schemas/workflow.py
- [[EndNode]] - code - backend/app/schemas/workflow.py
- [[Enum]] - code
- [[NodeType]] - code - backend/app/schemas/workflow.py
- [[PermissionLevel]] - code - backend/app/schemas/workflow.py
- [[Serialize workflow to JSON-compatible dict.]] - rationale - backend/app/schemas/workflow.py
- [[Supported workflow node types.]] - rationale - backend/app/schemas/workflow.py
- [[Tool permission levels.]] - rationale - backend/app/schemas/workflow.py
- [[Trigger]] - code - backend/app/schemas/workflow.py
- [[TriggerNode]] - code - backend/app/schemas/workflow.py
- [[TriggerType]] - code - backend/app/schemas/workflow.py
- [[WaitNode]] - code - backend/app/schemas/workflow.py
- [[Workflow schema definitions — Pydantic models for the universal workflow format.]] - rationale - backend/app/schemas/workflow.py
- [[str]] - code
- [[workflow.py]] - code - backend/app/schemas/workflow.py
- [[workflow_from_dict()]] - code - backend/app/schemas/workflow.py
- [[workflow_to_dict()]] - code - backend/app/schemas/workflow.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workflow_Schema_Types
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Core Engine Services]]
- 4 edges to [[_COMMUNITY_Workflow Schemas]]
- 3 edges to [[_COMMUNITY_Community 21]]
- 3 edges to [[_COMMUNITY_Community 50]]
- 2 edges to [[_COMMUNITY_Community 35]]
- 1 edge to [[_COMMUNITY_Community 43]]
- 1 edge to [[_COMMUNITY_Compiler + AST]]
- 1 edge to [[_COMMUNITY_Approvals API]]
- 1 edge to [[_COMMUNITY_Community 36]]

## Top bridge nodes
- [[workflow.py]] - degree 30, connects to 8 communities
- [[PermissionLevel]] - degree 10, connects to 4 communities
- [[NodeType]] - degree 8, connects to 3 communities
- [[BaseModel]] - degree 9, connects to 1 community
- [[workflow_from_dict()]] - degree 3, connects to 1 community