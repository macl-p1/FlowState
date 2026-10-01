---
type: community
cohesion: 0.18
members: 13
---

# Community 34

**Cohesion:** 0.18 - loosely connected
**Members:** 13 nodes

## Members
- [[dot-branch_workflow()]] - code - backend/app/genealogy/service.py
- [[dot-save_version()]] - code - backend/app/genealogy/service.py
- [[Base_1]] - code
- [[Create a new workflow branched from an existing one. The new workflow gets its…]] - rationale - backend/app/genealogy/service.py
- [[Save a new version of a workflow. Computes diff from the previous version and…]] - rationale - backend/app/genealogy/service.py
- [[Snapshot of a workflow at a point in time with change tracking.]] - rationale - backend/app/models/genealogy.py
- [[Tests for the genealogy engine — version tracking, diff, branching, lineage.]] - rationale - backend/tests/test_genealogy.py
- [[Tracks when a workflow is forked from another (for lineage tree).]] - rationale - backend/app/models/genealogy.py
- [[WorkflowBranchModel]] - code - backend/app/models/genealogy.py
- [[WorkflowVersionModel]] - code - backend/app/models/genealogy.py
- [[db()_1]] - code - backend/tests/test_genealogy.py
- [[fixture_5]] - code
- [[test_genealogy.py]] - code - backend/tests/test_genealogy.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_34
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Core Engine Services]]
- 5 edges to [[_COMMUNITY_Community 42]]
- 4 edges to [[_COMMUNITY_Community 26]]
- 1 edge to [[_COMMUNITY_Community 55]]
- 1 edge to [[_COMMUNITY_Community 63]]
- 1 edge to [[_COMMUNITY_Approvals API]]
- 1 edge to [[_COMMUNITY_Community 50]]

## Top bridge nodes
- [[test_genealogy.py]] - degree 18, connects to 6 communities
- [[WorkflowVersionModel]] - degree 9, connects to 2 communities
- [[dot-branch_workflow()]] - degree 5, connects to 2 communities
- [[dot-save_version()]] - degree 4, connects to 2 communities
- [[WorkflowBranchModel]] - degree 7, connects to 1 community