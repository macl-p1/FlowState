"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Sparkles,
  X,
  Loader2,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Lightbulb,
} from "lucide-react";
import { getWorkflowSuggestions, applySuggestion, type SuggestionItem, type BackendNode, type BackendEdge } from "@/lib/api";

const PATTERN_COLORS: Record<string, string> = {
  retry_logic: "bg-signal/10 text-signal border-signal/20",
  error_handling: "bg-warn/10 text-warn border-warn/20",
  approval_gate: "bg-accent/10 text-accent border-accent/20",
  branching: "bg-accent/10 text-accent border-accent/20",
  input_validation: "bg-success/10 text-success border-success/20",
  wait_delay: "bg-text-muted/10 text-text-muted border-text-muted/20",
  human_escalation: "bg-warn/10 text-warn border-warn/20",
  fallback_path: "bg-signal/10 text-signal border-signal/20",
};

interface SuggestionsPanelProps {
  workflowId: string;
  workflowName: string;
  isOpen: boolean;
  onClose: () => void;
  onApplySuggestion?: (nodes: BackendNode[], edges: BackendEdge[]) => void;
}

export default function SuggestionsPanel({
  workflowId,
  workflowName,
  isOpen,
  onClose,
  onApplySuggestion,
}: SuggestionsPanelProps) {
  const [suggestions, setSuggestions] = useState<SuggestionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState<string | null>(null);
  const [applied, setApplied] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const loadSuggestions = useCallback(async () => {
    if (!isOpen || !workflowId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getWorkflowSuggestions(workflowId);
      setSuggestions(data.suggestions);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load suggestions");
    } finally {
      setLoading(false);
    }
  }, [isOpen, workflowId]);

  useEffect(() => {
    loadSuggestions();
  }, [loadSuggestions]);

  const handleApply = async (suggestion: SuggestionItem) => {
    setApplying(suggestion.id);
    setError(null);
    try {
      const why = suggestion.evidence?.text ?? `from '${suggestion.source_workflow_name}'`;
      const result = await applySuggestion(workflowId, suggestion.apply_patch, `Applied suggestion: ${suggestion.pattern_label} (${why})`);
      setApplied((prev) => new Set(prev).add(suggestion.id));
      onApplySuggestion?.(result.nodes, result.edges);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to apply suggestion");
    } finally {
      setApplying(null);
    }
  };

  // Group by source workflow
  const grouped = suggestions.reduce<Record<string, SuggestionItem[]>>((acc, s) => {
    const key = s.source_workflow_id === workflowId ? "This workflow" : s.source_workflow_name;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div className="absolute right-0 top-0 bottom-0 w-[420px] bg-base border-l border-border shadow-2xl flex flex-col">
        {/* Header */}
        <div className="shrink-0 flex items-center justify-between px-4 h-14 border-b border-border">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent" />
            <div>
              <h2 className="text-sm font-medium text-text">Suggestions</h2>
              <p className="text-[10px] text-text-muted">{workflowName}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-text-muted hover:text-text hover:bg-surface-2 rounded-md transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto p-4">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <Loader2 className="w-5 h-5 text-text-muted animate-spin" />
              <p className="text-xs text-text-muted">Analyzing workflows...</p>
            </div>
          )}

          {error && (
            <div className="p-3 bg-warn/10 border border-warn/20 rounded-lg text-xs text-warn">
              {error}
            </div>
          )}

          {!loading && suggestions.length === 0 && !error && (
            <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
              <div className="w-10 h-10 rounded-full bg-surface-2 border border-border flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-text-muted" />
              </div>
              <p className="text-sm text-text-muted">No suggestions yet</p>
              <p className="text-xs text-text-muted/70">
                This workflow already has retries and approvals where they matter, and no similar workflow does
                anything it lacks
              </p>
            </div>
          )}

          {!loading && suggestions.length > 0 && (
            <div className="flex flex-col gap-4">
              {Object.entries(grouped).map(([sourceName, group]) => (
                <div key={sourceName}>
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-xs font-medium text-text-muted">{sourceName}</p>
                    {sourceName !== "This workflow" && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-surface-2 border border-border rounded-full text-text-muted">
                        {Math.round((group[0]?.similarity_score || 0) * 100)}% similar
                      </span>
                    )}
                  </div>
                  <div className="flex flex-col gap-2">
                    {group.map((s) => (
                      <SuggestionCard
                        key={s.id}
                        suggestion={s}
                        isApplying={applying === s.id}
                        isApplied={applied.has(s.id)}
                        onApply={() => handleApply(s)}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="shrink-0 px-4 py-2.5 border-t border-border">
          <p className="text-[10px] text-text-muted/70 text-center">
            Based on structural similarity across all workflows in your workspace
          </p>
        </div>
      </div>
    </div>
  );
}

function SuggestionCard({
  suggestion,
  isApplying,
  isApplied,
  onApply,
}: {
  suggestion: SuggestionItem;
  isApplying: boolean;
  isApplied: boolean;
  onApply: () => void;
}) {
  const colorClass = PATTERN_COLORS[suggestion.pattern] || "bg-surface-2 text-text-muted border-border";

  return (
    <div className="p-3 bg-surface border border-border rounded-lg">
      <div className="flex items-start gap-2 mb-2">
        <span className={`shrink-0 px-2 py-0.5 text-[10px] font-medium rounded-full border ${colorClass}`}>
          {suggestion.pattern_label}
        </span>
        {isApplied && (
          <span className="flex items-center gap-1 text-[10px] text-success">
            <CheckCircle2 className="w-3 h-3" />
            Applied
          </span>
        )}
      </div>

      <p className="text-xs text-text mb-1.5 leading-relaxed">
        {suggestion.description}
      </p>
      <p className="text-xs text-text-muted mb-3 leading-relaxed">
        {suggestion.suggestion}
      </p>
      {suggestion.evidence && (
        <div
          className={`mb-3 p-2 rounded-md border text-[11px] leading-relaxed ${
            suggestion.evidence.verdict === "improved" || suggestion.evidence.verdict === "worse"
              ? "bg-success/5 border-success/20 text-text"
              : "bg-surface-2 border-border text-text-muted"
          }`}
        >
          <span className="font-medium">
            {suggestion.origin === "self_history" ? "From this workflow's history: " : "From version history: "}
          </span>
          {suggestion.evidence.text}
          {suggestion.evidence.verdict === "unknown" && " (not enough runs yet to measure the effect)"}
        </div>
      )}

      {suggestion.actionable && !isApplied && (
        <button
          onClick={onApply}
          disabled={isApplying}
          className="h-7 px-3 bg-text text-base text-xs font-medium rounded-md hover:bg-text/90 transition-all disabled:opacity-40 flex items-center gap-1.5"
        >
          {isApplying ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin" />
              Applying...
            </>
          ) : (
            <>
              <ExternalLink className="w-3 h-3" />
              Apply
            </>
          )}
        </button>
      )}
    </div>
  );
}
