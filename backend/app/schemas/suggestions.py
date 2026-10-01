"""Schemas for the suggestions / cross-pollination feature."""

from pydantic import BaseModel
from typing import Any


class SuggestionResponse(BaseModel):
    """Single cross-pollination suggestion."""
    id: str
    workflow_id: str
    source_workflow_id: str
    source_workflow_name: str
    similarity_score: float
    pattern: str
    pattern_label: str
    description: str
    suggestion: str
    target_node_id: str | None
    actionable: bool
    apply_patch: dict[str, Any]


class SuggestionsResponse(BaseModel):
    """Wrapper for a list of suggestions."""
    workflow_id: str
    suggestions: list[SuggestionResponse]


class ApplyPatchRequest(BaseModel):
    """Request to apply a suggestion's patch to a workflow."""
    patch: dict[str, Any]
