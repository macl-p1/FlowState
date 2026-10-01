---
type: community
cohesion: 0.06
members: 61
---

# Suggestions + Cross-Pollination

**Cohesion:** 0.06 - loosely connected
**Members:** 61 nodes

## Members
- [[dot-test_completely_different_scores_zero()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_detects_approval_gate()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_detects_branching()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_detects_retry_logic()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_detects_wait_delay()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_finds_missing_retry()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_identical_workflows_score_one()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_insert_between_patch()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_insert_between_with_branch_patch()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_no_false_positives()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_no_gap_when_both_have()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_no_suggestions_with_single_workflow()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_partial_overlap()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_returns_suggestions_for_similar_workflow()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_scores_sorted_descending()]] - code - backend/tests/test_cross_pollination.py
- [[dot-test_update_node_patch()]] - code - backend/tests/test_cross_pollination.py
- [[Analyze a workflow graph and extract structural patterns. Returns a dict with…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Any_1]] - code
- [[Apply a structured patch to a workflow's nodes and edges. Returns (new_nodes,…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Apply a suggestion's patch to a workflow.]] - rationale - backend/app/api/suggestions.py
- [[Build a structured suggestion with an apply_patch for a pattern gap.]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Build the final suggestion dict with a stable ID.]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Compact summary for LLM prompt.]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Compute weighted Jaccard similarity between two workflow profiles. Weights…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Cross-pollination engine — similarity scoring, pattern extraction, gap…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Find patterns the candidate has that the target is missing. Both args are the…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Generate cross-pollination suggestions for a workflow. Compares against all…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Get cross-pollination suggestions for a workflow.]] - rationale - backend/app/api/suggestions.py
- [[Send top candidates to Claude for richer, more contextual suggestions. Returns…]] - rationale - backend/app/genealogy/cross_pollination.py
- [[Session]] - code
- [[TestApplyPatch]] - code - backend/tests/test_cross_pollination.py
- [[TestGetSuggestions]] - code - backend/tests/test_cross_pollination.py
- [[TestPatternExtraction]] - code - backend/tests/test_cross_pollination.py
- [[TestPatternGaps]] - code - backend/tests/test_cross_pollination.py
- [[TestSimilarityScoring]] - code - backend/tests/test_cross_pollination.py
- [[Tests for the cross-pollination engine — similarity, patterns, gaps, patches,…]] - rationale - backend/tests/test_cross_pollination.py
- [[_build_suggestion()]] - code - backend/app/genealogy/cross_pollination.py
- [[_finalize_suggestion()]] - code - backend/app/genealogy/cross_pollination.py
- [[_find_first_by_type()]] - code - backend/app/genealogy/cross_pollination.py
- [[_find_node()]] - code - backend/app/genealogy/cross_pollination.py
- [[_get_condition_node_ids()]] - code - backend/app/genealogy/cross_pollination.py
- [[_get_node_by_id()]] - code - backend/app/genealogy/cross_pollination.py
- [[_make_workflow()]] - code - backend/tests/test_cross_pollination.py
- [[_summarize_workflow()]] - code - backend/app/genealogy/cross_pollination.py
- [[anthropic_2]] - concept
- [[apply_patch_to_workflow()]] - code - backend/app/genealogy/cross_pollination.py
- [[apply_suggestion()]] - code - backend/app/api/suggestions.py
- [[collections]] - concept
- [[compute_similarity()]] - code - backend/app/genealogy/cross_pollination.py
- [[cross_pollination.py]] - code - backend/app/genealogy/cross_pollination.py
- [[db()]] - code - backend/tests/test_cross_pollination.py
- [[enrich_with_llm()]] - code - backend/app/genealogy/cross_pollination.py
- [[extract_patterns()]] - code - backend/app/genealogy/cross_pollination.py
- [[find_pattern_gaps()]] - code - backend/app/genealogy/cross_pollination.py
- [[fixture]] - code
- [[get]] - code
- [[get_suggestions()]] - code - backend/app/genealogy/cross_pollination.py
- [[jaccard()]] - code - backend/app/genealogy/cross_pollination.py
- [[list_suggestions()]] - code - backend/app/api/suggestions.py
- [[post]] - code
- [[test_cross_pollination.py]] - code - backend/tests/test_cross_pollination.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Suggestions__Cross-Pollination
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Approvals API]]
- 7 edges to [[_COMMUNITY_Core Engine Services]]
- 1 edge to [[_COMMUNITY_Community 40]]
- 1 edge to [[_COMMUNITY_Community 50]]

## Top bridge nodes
- [[cross_pollination.py]] - degree 21, connects to 3 communities
- [[test_cross_pollination.py]] - degree 20, connects to 3 communities
- [[get_suggestions()]] - degree 14, connects to 1 community
- [[apply_patch_to_workflow()]] - degree 11, connects to 1 community
- [[apply_suggestion()]] - degree 6, connects to 1 community