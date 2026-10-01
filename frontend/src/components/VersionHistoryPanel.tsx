"use client";

import { useState, useEffect } from "react";
import { XIcon, GitBranch, History, ChevronDown, ChevronRight, Save, GitFork } from "lucide-react";
import {
  getWorkflowHistory,
  getWorkflowVersion,
  saveWorkflowVersion,
  branchWorkflow,
  type BackendNode,
  type BackendEdge,
} from "@/lib/api";

export interface VersionHistoryPanelProps {
  workflowId: string;
  workflowName: string;
  isOpen: boolean;
  onClose: () => void;
  onLoadVersion?: (nodes: BackendNode[], edges: BackendEdge[]) => void;
}

interface VersionItemData {
  id: string;
  version_number: number;
  change_rationale: string | null;
  change_summary: string | null;
  diff_details: Record<string, unknown> | null;
  created_at: string | null;
  parent_version_id: string | null;
  nodes: BackendNode[];
  edges: BackendEdge[];
}

const CHANGE_TYPE_COLORS: Record<string, string> = {
  added: "bg-success/10 text-success border-success/20",
  removed: "bg-warn/10 text-warn border-warn/20",
  modified: "bg-accent/10 text-accent border-accent/20",
  structural: "bg-signal/10 text-signal border-signal/20",
  logic: "bg-accent/10 text-accent border-accent/20",
  configuration: "bg-success/10 text-success border-success/20",
  minor: "bg-text-muted/10 text-text-muted border-text-muted/20",
};

function ChangeTypeBadge({ summary }: { summary: string | null }) {
  if (!summary) return null;
  const lower = summary.toLowerCase();
  let type = "minor";
  if (lower.includes("added") && lower.includes("removed")) type = "structural";
  else if (lower.includes("added") || lower.includes("removed")) {
    type = lower.includes("node") ? "structural" : "minor";
  } else if (lower.includes("modif")) type = "logic";
  else if (lower.includes("edge")) type = "configuration";

  const colorClass = CHANGE_TYPE_COLORS[type] || CHANGE_TYPE_COLORS.minor;
  return (
    <span className={`px-1.5 py-0.5 text-[9px] font-medium rounded border ${colorClass}`}>
      {type}
    </span>
  );
}

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function VersionHistoryPanel({
  workflowId,
  workflowName,
  isOpen,
  onClose,
  onLoadVersion,
}: VersionHistoryPanelProps) {
  const [versions, setVersions] = useState<VersionItemData[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [rationale, setRationale] = useState("");
  const [showRationaleInput, setShowRationaleInput] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
  const [versionDetail, setVersionDetail] = useState<VersionItemData | null>(null);
  const [branching, setBranching] = useState(false);
  const [branchName, setBranchName] = useState("");
  const [branchRationale, setBranchRationale] = useState("");
  const [expandedVersions, setExpandedVersions] = useState<Set<string>>(new Set());

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getWorkflowHistory(workflowId);
      setVersions(data.versions);
    } catch (e) {
      console.error("Failed to load version history:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadHistory();
      setRationale("");
      setShowRationaleInput(false);
      setSelectedVersion(null);
      setVersionDetail(null);
      setBranching(false);
      setBranchName("");
      setBranchRationale("");
    }
  }, [isOpen, workflowId]);

  const handleSaveVersion = async () => {
    if (!rationale.trim()) return;
    setSaving(true);
    try {
      await saveWorkflowVersion(workflowId, { rationale: rationale.trim() });
      setRationale("");
      setShowRationaleInput(false);
      await loadHistory();
    } catch (e) {
      console.error("Failed to save version:", e);
    } finally {
      setSaving(false);
    }
  };

  const handleViewVersion = async (version: VersionItemData) => {
    setSelectedVersion(version.id);
    setVersionDetail(version);
  };

  const handleLoadVersion = () => {
    if (versionDetail && onLoadVersion) {
      onLoadVersion(versionDetail.nodes, versionDetail.edges);
    }
  };

  const handleBranch = async () => {
    if (!branchName.trim()) return;
    setBranching(true);
    try {
      await branchWorkflow(workflowId, {
        name: branchName.trim(),
        rationale: branchRationale.trim() || undefined,
      });
      setBranchName("");
      setBranchRationale("");
      setBranching(false);
      onClose();
    } catch (e) {
      console.error("Failed to branch workflow:", e);
      setBranching(false);
    }
  };

  const toggleExpanded = (versionId: string) => {
    setExpandedVersions((prev) => {
      const next = new Set(prev);
      if (next.has(versionId)) next.delete(versionId);
      else next.add(versionId);
      return next;
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div className="relative w-[420px] h-full bg-surface border-l border-border shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-accent" />
            <div>
              <h2 className="text-sm font-medium text-text">Version History</h2>
              <p className="text-[10px] text-text-muted">{workflowName}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-text-muted hover:text-text hover:bg-base transition-colors"
          >
            <XIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Save new version */}
        <div className="p-4 border-b border-border bg-base/30">
          {!showRationaleInput ? (
            <button
              onClick={() => setShowRationaleInput(true)}
              className="w-full h-9 rounded-lg border border-border bg-surface text-xs text-text-muted hover:text-text hover:border-text-muted/40 transition-all flex items-center justify-center gap-1.5"
            >
              <Save className="w-3.5 h-3.5" />
              Save New Version
            </button>
          ) : (
            <div className="space-y-2">
              <textarea
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                placeholder="What changed and why? (e.g., 'Added error handling for API timeouts')"
                rows={3}
                className="w-full px-3 py-2 bg-base border border-border rounded-lg text-xs text-text placeholder:text-text-muted/40 focus:outline-none focus:border-text-muted/40 resize-none"
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSaveVersion}
                  disabled={saving || !rationale.trim()}
                  className="flex-1 h-8 rounded-lg bg-accent text-white text-xs font-medium hover:bg-accent/90 disabled:opacity-50 transition-all flex items-center justify-center gap-1.5"
                >
                  {saving ? "Saving…" : "Save Version"}
                </button>
                <button
                  onClick={() => { setShowRationaleInput(false); setRationale(""); }}
                  className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-text transition-all"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Branch section */}
        <div className="p-4 border-b border-border">
          {!branching ? (
            <button
              onClick={() => setBranching(true)}
              className="w-full h-9 rounded-lg border border-border bg-surface text-xs text-text-muted hover:text-text hover:border-text-muted/40 transition-all flex items-center justify-center gap-1.5"
            >
              <GitBranch className="w-3.5 h-3.5" />
              Branch into New Workflow
            </button>
          ) : (
            <div className="space-y-2">
              <input
                value={branchName}
                onChange={(e) => setBranchName(e.target.value)}
                placeholder="New workflow name"
                className="w-full h-8 px-3 bg-base border border-border rounded-lg text-xs text-text placeholder:text-text-muted/40 focus:outline-none focus:border-text-muted/40"
                autoFocus
              />
              <textarea
                value={branchRationale}
                onChange={(e) => setBranchRationale(e.target.value)}
                placeholder="Why create this branch?"
                rows={2}
                className="w-full px-3 py-2 bg-base border border-border rounded-lg text-xs text-text placeholder:text-text-muted/40 focus:outline-none focus:border-text-muted/40 resize-none"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleBranch}
                  disabled={branching || !branchName.trim()}
                  className="flex-1 h-8 rounded-lg bg-signal text-white text-xs font-medium hover:bg-signal/90 disabled:opacity-50 transition-all flex items-center justify-center gap-1.5"
                >
                  {branching ? "Creating…" : "Create Branch"}
                </button>
                <button
                  onClick={() => { setBranching(false); setBranchName(""); setBranchRationale(""); }}
                  className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-text transition-all"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Version list */}
        <div className="flex-1 overflow-y-auto p-2">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-5 h-5 border-2 border-text-muted/20 border-t-accent rounded-full animate-spin" />
            </div>
          ) : versions.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-xs text-text-muted">No versions saved yet.</p>
              <p className="text-[10px] text-text-muted/60 mt-1">Save a version to start tracking changes.</p>
            </div>
          ) : (
            <div className="space-y-1">
              {versions.map((version, index) => (
                <div
                  key={version.id}
                  className={`rounded-lg border transition-colors ${
                    selectedVersion === version.id
                      ? "border-accent/40 bg-accent/5"
                      : "border-border bg-surface hover:border-text-muted/30"
                  }`}
                >
                  <button
                    onClick={() => {
                      if (expandedVersions.has(version.id)) {
                        setExpandedVersions((prev) => {
                          const next = new Set(prev);
                          next.delete(version.id);
                          return next;
                        });
                      } else {
                        setExpandedVersions((prev) => new Set(prev).add(version.id));
                      }
                    }}
                    className="w-full p-3 flex items-start gap-3 text-left"
                  >
                    <div className="mt-0.5 shrink-0">
                      <div className="w-6 h-6 rounded-md bg-accent/10 border border-accent/20 flex items-center justify-center">
                        <span className="text-[10px] font-bold text-accent font-mono">
                          v{version.version_number}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-text">v{version.version_number}</span>
                        <ChangeTypeBadge summary={version.change_summary} />
                        {index === 0 && versions.length > 1 && (
                          <span className="px-1.5 py-0.5 text-[9px] font-medium rounded bg-accent/5 text-accent border border-accent/10">
                            current
                          </span>
                        )}
                      </div>
                      {version.change_rationale && (
                        <p className="text-[11px] text-text-muted leading-relaxed line-clamp-2">
                          {version.change_rationale}
                        </p>
                      )}
                      {version.change_summary && !version.change_rationale && (
                        <p className="text-[11px] text-text-muted/70 italic">
                          {version.change_summary}
                        </p>
                      )}
                      <span className="text-[10px] text-text-muted/50 mt-1.5 block">
                        {formatTime(version.created_at)}
                      </span>
                    </div>
                    {expandedVersions.has(version.id) ? (
                      <ChevronDown className="w-4 h-4 text-text-muted/50 shrink-0 mt-1" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-text-muted/50 shrink-0 mt-1" />
                    )}
                  </button>

                  {/* Expanded version detail */}
                  {expandedVersions.has(version.id) && (
                    <div className="px-3 pb-3 border-t border-border/50">
                      <div className="pt-3 space-y-2">
                        {/* Change summary */}
                        {version.change_summary && (
                          <div className="p-2 bg-base/50 rounded-md">
                            <p className="text-[10px] font-medium text-text-muted uppercase tracking-wider mb-1">
                              Changes
                            </p>
                            <p className="text-[11px] text-text">{version.change_summary}</p>
                          </div>
                        )}

                        {/* Diff details */}
                        {version.diff_details && (
                          <div className="p-2 bg-base/50 rounded-md">
                            <p className="text-[10px] font-medium text-text-muted uppercase tracking-wider mb-1">
                              Diff Detail
                            </p>
                            <div className="space-y-1 text-[11px]">
                              {(version.diff_details.added_nodes as any[])?.length > 0 && (
                                <div className="flex gap-2">
                                  <span className="text-success/80 shrink-0">+{Array.isArray(version.diff_details.added_nodes) ? (version.diff_details.added_nodes as any[]).length : 0} nodes</span>
                                </div>
                              )}
                              {(version.diff_details.removed_nodes as any[])?.length > 0 && (
                                <div className="flex gap-2">
                                  <span className="text-warn/80 shrink-0">-{Array.isArray(version.diff_details.removed_nodes) ? (version.diff_details.removed_nodes as any[]).length : 0} nodes</span>
                                </div>
                              )}
                              {(version.diff_details.added_edges as any[])?.length > 0 && (
                                <div className="flex gap-2">
                                  <span className="text-success/80 shrink-0">+{Array.isArray(version.diff_details.added_edges) ? (version.diff_details.added_edges as any[]).length : 0} edges</span>
                                </div>
                              )}
                              {(version.diff_details.removed_edges as any[])?.length > 0 && (
                                <div className="flex gap-2">
                                  <span className="text-warn/80 shrink-0">-{Array.isArray(version.diff_details.removed_edges) ? (version.diff_details.removed_edges as any[]).length : 0} edges</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Node/Edge counts */}
                        <div className="flex gap-3 text-[10px] text-text-muted">
                          <span>{Array.isArray(version.nodes) ? version.nodes.length : 0} nodes</span>
                          <span>{Array.isArray(version.edges) ? version.edges.length : 0} edges</span>
                        </div>

                        {/* Action buttons */}
                        <div className="flex gap-2 pt-1">
                          <button
                            onClick={() => handleViewVersion(version)}
                            className="flex-1 h-7 rounded-md border border-border text-[11px] text-text-muted hover:text-text hover:border-text-muted/40 transition-all"
                          >
                            View Graph
                          </button>
                          {onLoadVersion && (
                            <button
                              onClick={handleLoadVersion}
                              className="flex-1 h-7 rounded-md bg-accent/10 border border-accent/20 text-[11px] text-accent hover:bg-accent/20 transition-all"
                            >
                              Restore to Canvas
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Version detail modal overlay */}
        {versionDetail && (
          <div className="absolute inset-0 bg-base/95 backdrop-blur-sm flex flex-col z-10">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-text">
                  v{versionDetail.version_number} — Full Graph
                </span>
                <ChangeTypeBadge summary={versionDetail.change_summary} />
              </div>
              <button
                onClick={() => { setSelectedVersion(null); setVersionDetail(null); }}
                className="p-1.5 rounded-md text-text-muted hover:text-text hover:bg-surface transition-colors"
              >
                <XIcon className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {versionDetail.change_rationale && (
                <div className="p-3 bg-surface rounded-lg border border-border">
                  <p className="text-[10px] font-medium text-text-muted uppercase tracking-wider mb-1">Rationale</p>
                  <p className="text-xs text-text">{versionDetail.change_rationale}</p>
                </div>
              )}
              <div>
                <p className="text-[10px] font-medium text-text-muted uppercase tracking-wider mb-2">
                  Nodes ({Array.isArray(versionDetail.nodes) ? versionDetail.nodes.length : 0})
                </p>
                <div className="space-y-1.5">
                  {versionDetail.nodes.map((node) => (
                    <div key={node.id} className="p-2 bg-surface rounded-md border border-border text-[11px]">
                      <span className="font-medium text-text">{node.name || node.id}</span>
                      <span className="text-text-muted ml-2">({node.type}{node.tool ? `, ${node.tool}` : ""})</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] font-medium text-text-muted uppercase tracking-wider mb-2">
                  Edges ({Array.isArray(versionDetail.edges) ? versionDetail.edges.length : 0})
                </p>
                <div className="space-y-1">
                  {versionDetail.edges.map((edge, i) => (
                    <div key={i} className="text-[11px] text-text-muted font-mono">
                      {edge.from} → {edge.to}{edge.condition ? ` [${edge.condition}]` : ""}
                    </div>
                  ))}
                </div>
              </div>
            </div>
            {onLoadVersion && (
              <div className="p-4 border-t border-border">
                <button
                  onClick={handleLoadVersion}
                  className="w-full h-9 rounded-lg bg-accent text-white text-xs font-medium hover:bg-accent/90 transition-all flex items-center justify-center gap-1.5"
                >
                  <GitFork className="w-3.5 h-3.5" />
                  Restore This Version to Canvas
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
