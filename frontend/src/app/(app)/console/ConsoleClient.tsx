"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import {
  ChevronRight,
  Clock,
  AlertTriangle,
  Play,
  Square,
  Copy,
  RefreshCw,
  MoreHorizontal,
  User,
  FileText,
  Terminal,
  Code,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";
import {
  listRuns,
  getRun,
  getRunEvaluation,
  flagRun,
  getWorkflowQuality,
  type RunQuality,
  type WorkflowQuality,
  cancelRun as apiCancelRun,
  replayRun,
  listApprovals,
  approveApproval,
  rejectApproval,
  type RunListItem,
  type RunDetail,
  type RunStep,
  type ApprovalItem,
} from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

/* ── Node icon mapping ── */
const NODE_ICONS: Record<string, React.ElementType> = {
  trigger: Play,
  action: Code,
  condition: FileText,
  approval: User,
  wait: Clock,
  end: CheckCircle2,
};

type NodeState = "done" | "active" | "pending" | "error";

function getNodeState(index: number, steps: RunStep[], currentStatus: string): NodeState {
  if (currentStatus === "completed") {
    if (index < steps.length) return "done";
    return "pending";
  }
  if (currentStatus === "failed" || currentStatus === "cancelled") {
    const failedIdx = steps.findIndex((s) => s.status === "failed");
    if (failedIdx >= 0 && index === failedIdx) return "error";
    if (index < failedIdx || (failedIdx < 0 && index < steps.length)) return "done";
    return "pending";
  }
  if (currentStatus === "running") {
    const runningIdx = steps.findIndex((s) => s.status === "running");
    if (runningIdx >= 0 && index === runningIdx) return "active";
    if (index < runningIdx || (runningIdx < 0 && index < steps.length)) return "done";
    return "pending";
  }
  if (currentStatus === "waiting_approval") {
    const approvalIdx = steps.findIndex((s) => s.status === "waiting_approval");
    if (approvalIdx >= 0 && index === approvalIdx) return "active";
    if (index < approvalIdx) return "done";
    return "pending";
  }
  if (currentStatus === "pending") return "pending";
  return "pending";
}

const nodeStateStyles: Record<NodeState, { border: string; bg: string; iconBg: string; text: string; dot: string }> = {
  done: {
    border: "border-success/30",
    bg: "bg-success/5",
    iconBg: "bg-success/15",
    text: "text-success",
    dot: "bg-success",
  },
  active: {
    border: "border-signal/30",
    bg: "bg-signal/5",
    iconBg: "bg-signal/15",
    text: "text-signal",
    dot: "bg-signal",
  },
  pending: {
    border: "border-border",
    bg: "bg-surface-2/50",
    iconBg: "bg-surface-2",
    text: "text-text-muted",
    dot: "bg-text-muted/30",
  },
  error: {
    border: "border-warn/30",
    bg: "bg-warn/5",
    iconBg: "bg-warn/15",
    text: "text-warn",
    dot: "bg-warn",
  },
};

const statusStyles: Record<string, string> = {
  completed: "bg-success/10 text-success border-success/20",
  running: "bg-signal/10 text-signal border-signal/20",
  pending: "bg-accent/10 text-accent border-accent/20",
  failed: "bg-warn/10 text-warn border-warn/20",
  cancelled: "bg-warn/10 text-warn border-warn/20",
  waiting_approval: "bg-accent/10 text-accent border-accent/20",
};

const statusLabel: Record<string, string> = {
  completed: "Completed",
  running: "Running",
  pending: "Pending",
  failed: "Failed",
  cancelled: "Cancelled",
  waiting_approval: "Awaiting Approval",
};

interface ConsoleClientProps {
  initialRunId: string | null;
}

export default function ConsoleClient({ initialRunId }: ConsoleClientProps) {
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(initialRunId);
  const [selectedRun, setSelectedRun] = useState<RunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [runLoading, setRunLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeDetailTab, setActiveDetailTab] = useState<"details" | "logs" | "io">("details");
  const [selectedNodeIdx, setSelectedNodeIdx] = useState(0);
  const [cancelling, setCancelling] = useState(false);
  const [quality, setQuality] = useState<RunQuality | null>(null);
  const [wfQuality, setWfQuality] = useState<WorkflowQuality | null>(null);
  const [flagged, setFlagged] = useState(false);
  const [runningNodeName, setRunningNodeName] = useState<string | null>(null);
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [approvingId, setApprovingId] = useState<string | null>(null);

  // Load runs list
  const loadRuns = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listRuns();
      setRuns(data);
      if (data.length > 0 && !selectedRunId) {
        setSelectedRunId(data[0].id);
      }
    } catch (e) {
      console.error("Failed to load runs:", e);
    } finally {
      setLoading(false);
    }
  }, [selectedRunId]);

  // Load approvals
  const loadApprovals = useCallback(async () => {
    try {
      const data = await listApprovals();
      setApprovals(data);
    } catch (e) {
      console.error("Failed to load approvals:", e);
    }
  }, []);

  useEffect(() => {
    loadRuns();
    loadApprovals();
    const interval = setInterval(() => {
      loadRuns();
      loadApprovals();
    }, 5000);
    return () => clearInterval(interval);
  }, [loadRuns, loadApprovals]);

  // Load selected run detail — prefer SSE streaming for live updates
  useEffect(() => {
    if (!selectedRunId) return;
    let cancelled = false;
    setRunLoading(true);

    const loadInitialDetail = async () => {
      try {
        const data = await getRun(selectedRunId);
        if (!cancelled) {
          setSelectedRun(data);
          setSelectedNodeIdx(0);
          setRunLoading(false);
        }
      } catch (e) {
        console.error("Failed to load run detail:", e);
        if (!cancelled) setRunLoading(false);
      }
    };

    loadInitialDetail();

    // Open SSE stream for real-time step updates
    let es: EventSource | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

    const connectStream = () => {
      if (cancelled) return;
      const url = new URL(`${API_BASE}/runs/${encodeURIComponent(selectedRunId)}/stream`);
      if (API_KEY) url.searchParams.set("api_key", API_KEY);
      es = new EventSource(url.toString());

      es.onmessage = (evt: MessageEvent) => {
        if (cancelled) return;
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === "step" && msg.data) {
            setSelectedRun((prev) => {
              if (!prev) return prev;
              const exists = prev.steps.some((s) => s.id === msg.data.id);
              if (!exists) {
                return { ...prev, steps: [...prev.steps, msg.data] };
              }
              return prev;
            });
          } else if (msg.type === "status" && msg.data) {
            setRunningNodeName(msg.data.status === "running" ? msg.data.current_node_name ?? null : null);
            setSelectedRun((prev) => {
              if (!prev) return prev;
              return { ...prev, status: msg.data.status, current_node_id: msg.data.current_node_id ?? null };
            });
          }
        } catch { /* ignore parse errors */ }
      };

      es.addEventListener("snapshot", (evt: MessageEvent) => {
        if (cancelled) return;
        try {
          const data = JSON.parse((evt as MessageEvent).data);
          setSelectedRun((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              status: data.status,
              steps: data.steps || prev.steps,
              error_message: data.error_message ?? prev.error_message,
              completed_at: data.completed_at ?? prev.completed_at,
            };
          });
        } catch { /* ignore parse errors */ }
      });

      es.addEventListener("done", () => {
        if (es) {
          es.close();
          es = null;
        }
        // Refresh run list when execution completes
        if (!cancelled) {
          loadRuns();
          setRunLoading(false);
        }
      });

      es.onerror = () => {
        if (es) { es.close(); es = null; }
        if (!cancelled) {
          reconnectTimeout = setTimeout(connectStream, 3000);
        }
      };
    };

    connectStream();

    return () => {
      cancelled = true;
      if (es) { es.close(); }
      if (reconnectTimeout) { clearTimeout(reconnectTimeout); }
    };
  }, [selectedRunId, loadRuns]);

  // Auto-select first approval if any
  useEffect(() => {
    if (approvals.length > 0 && !selectedRunId) {
      setSelectedRunId(approvals[0].execution_id);
    }
  }, [approvals, selectedRunId]);

  /* Quality: evaluation of the selected completed run + workflow-level override insight */
  const selectedWorkflowId = runs.find((r) => r.id === selectedRunId)?.workflow_id;
  const selectedStatus = selectedRun?.status;
  useEffect(() => {
    setQuality(null);
    setFlagged(false);
    setWfQuality(null);
    if (!selectedRunId || selectedStatus !== "completed") return;
    getRunEvaluation(selectedRunId).then(setQuality).catch(() => {});
    if (selectedWorkflowId) getWorkflowQuality(selectedWorkflowId).then(setWfQuality).catch(() => {});
  }, [selectedRunId, selectedStatus, selectedWorkflowId]);

  const handleFlag = useCallback(async () => {
    if (!selectedRunId) return;
    try {
      await flagRun(selectedRunId);
      setFlagged(true);
      if (selectedWorkflowId) setWfQuality(await getWorkflowQuality(selectedWorkflowId));
    } catch {
      /* ignore: button stays clickable */
    }
  }, [selectedRunId, selectedWorkflowId]);

  const [replaying, setReplaying] = useState(false);
  const handleReplay = useCallback(async () => {
    if (!selectedRunId) return;
    setReplaying(true);
    try {
      const { id } = await replayRun(selectedRunId);
      await loadRuns();
      setSelectedRunId(id);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to replay");
    } finally {
      setReplaying(false);
    }
  }, [selectedRunId, loadRuns]);

  const handleCancel = useCallback(async () => {
    if (!selectedRunId) return;
    setCancelling(true);
    try {
      await apiCancelRun(selectedRunId);
      await loadRuns();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to cancel");
    } finally {
      setCancelling(false);
    }
  }, [selectedRunId, loadRuns]);

  const handleApprove = useCallback(async (approvalId: string) => {
    setApprovingId(approvalId);
    try {
      await approveApproval(approvalId, "current_user");
      await loadApprovals();
      await loadRuns();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to approve");
    } finally {
      setApprovingId(null);
    }
  }, [loadApprovals, loadRuns]);

  const handleReject = useCallback(async (approvalId: string) => {
    setApprovingId(approvalId);
    try {
      await rejectApproval(approvalId, "current_user", "Rejected from console");
      await loadApprovals();
      await loadRuns();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to reject");
    } finally {
      setApprovingId(null);
    }
  }, [loadApprovals, loadRuns]);

  const copyLogs = useCallback(() => {
    if (!selectedRun) return;
    const logs = selectedRun.steps.map((s) => `[${s.status}] ${s.node_name}${s.tool_name ? ` (${s.tool_name})` : ""}${s.error ? ` — ${s.error}` : ""}`);
    navigator.clipboard.writeText(logs.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, [selectedRun]);

  const copyRunId = useCallback(() => {
    if (selectedRunId) {
      navigator.clipboard.writeText(selectedRunId);
    }
  }, [selectedRunId]);

  const selectedNode = selectedRun ? selectedRun.steps[selectedNodeIdx] : null;

  // Format duration
  const formatDuration = (started: string | null, completed: string | null): string => {
    if (!started) return "—";
    const start = new Date(started);
    const end = completed ? new Date(completed) : new Date();
    const diffMs = end.getTime() - start.getTime();
    if (diffMs < 1000) return `${diffMs}ms`;
    if (diffMs < 60000) return `${(diffMs / 1000).toFixed(1)}s`;
    return `${Math.floor(diffMs / 60000)}m ${Math.floor((diffMs % 60000) / 1000)}s`;
  };

  return (
    <div className="flex flex-col h-screen">
      {/* ============ RUN LIST BAR (horizontal) ============ */}
      <div className="shrink-0 border-b border-border bg-surface/30">
        <div className="flex items-center gap-2 px-4 h-12">
          <p className="text-xs text-text-muted shrink-0 mr-1">Execution Runs</p>
          <div className="flex items-center gap-1.5 overflow-x-auto">
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin text-text-muted" />
            ) : runs.length === 0 ? (
              <span className="text-xs text-text-muted">No runs yet</span>
            ) : (
              runs.map((run) => (
                <button
                  key={run.id}
                  onClick={() => setSelectedRunId(run.id)}
                  className={`shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-md border text-xs transition-all ${
                    selectedRunId === run.id
                      ? "bg-surface-2 border-text-muted/20 text-text"
                      : "border-transparent text-text-muted hover:text-text hover:bg-surface-2/50"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                      run.status === "completed"
                        ? "bg-success"
                        : run.status === "running"
                          ? "bg-signal animate-pulse"
                          : run.status === "failed"
                            ? "bg-warn"
                            : run.status === "waiting_approval"
                              ? "bg-accent animate-pulse"
                              : "bg-accent/60"
                    }`}
                  />
                  <span className="truncate max-w-[140px]">{run.workflow_name}</span>
                  <span
                    className={`shrink-0 px-1.5 py-0.5 text-[9px] font-medium rounded-md ${statusStyles[run.status] || statusStyles.pending}`}
                  >
                    {statusLabel[run.status] || run.status}
                  </span>
                </button>
              ))
            )}
          </div>
          <div className="ml-auto flex items-center gap-2 shrink-0">
            <button
              onClick={loadRuns}
              className="p-1.5 text-text-muted hover:text-text rounded transition-all hover:bg-surface-2"
              title="Refresh"
            >
              <RefreshCw className="w-3.5 h-3.5 shrink-0" />
            </button>
          </div>
        </div>

        {/* ── Approvals bar ── */}
        {approvals.length > 0 && (
          <div className="px-4 pb-2 flex items-center gap-2 overflow-x-auto">
            <span className="text-[10px] text-text-muted shrink-0">Pending approvals:</span>
            {approvals.map((a) => (
              <div
                key={a.id}
                className="shrink-0 flex items-center gap-2 px-3 py-1.5 bg-accent/10 border border-accent/20 rounded-md"
              >
                <span className="text-[10px] text-accent font-medium">{a.reason.slice(0, 40)}</span>
                <button
                  onClick={() => handleApprove(a.id)}
                  disabled={approvingId === a.id}
                  className="text-[10px] px-2 py-0.5 bg-success/20 text-success rounded hover:bg-success/30 disabled:opacity-50"
                >
                  {approvingId === a.id ? "..." : "Approve"}
                </button>
                <button
                  onClick={() => handleReject(a.id)}
                  disabled={approvingId === a.id}
                  className="text-[10px] px-2 py-0.5 bg-warn/20 text-warn rounded hover:bg-warn/30 disabled:opacity-50"
                >
                  Reject
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ============ MAIN CONSOLE ============ */}
      <main className="flex-1 overflow-auto pb-20 md:pb-0">
        {!selectedRun || runLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-5 h-5 animate-spin text-text-muted" />
          </div>
        ) : (
          <>
            {/* ── Header ── */}
            <header className="shrink-0 border-b border-border bg-base/80 backdrop-blur-sm">
              <div className="px-5 pt-3 pb-2">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h1 className="text-base font-semibold text-text tracking-tight">
                        {selectedRun.workflow_name}
                      </h1>
                      <span
                        className={`px-2 py-0.5 text-[10px] font-medium rounded-full border ${statusStyles[selectedRun.status] || ""}`}
                      >
                        {statusLabel[selectedRun.status] || selectedRun.status}
                      </span>
                      {selectedRun.source && selectedRun.source !== "manual" && (
                        <span className="px-2 py-0.5 text-[10px] rounded-full border border-border text-text-muted">
                          {selectedRun.source}
                          {selectedRun.replay_of ? ` of ${selectedRun.replay_of.slice(-8)}` : ""}
                        </span>
                      )}
                      {selectedRun.status === "running" && runningNodeName && (
                        <span className="flex items-center gap-1.5 text-[10px] text-signal">
                          <span className="w-1.5 h-1.5 rounded-full bg-signal animate-pulse" />
                          {runningNodeName}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-1.5">
                      <span className="text-[10px] text-text-muted">
                        Started {selectedRun.started_at ? new Date(selectedRun.started_at).toLocaleString() : "—"}
                      </span>
                      <span className="text-[10px] text-text-muted/50">|</span>
                      <span className="text-[10px] text-text-muted">
                        Ended {selectedRun.completed_at ? new Date(selectedRun.completed_at).toLocaleString() : "—"}
                      </span>
                      <span className="text-[10px] text-text-muted/50">|</span>
                      <span className="text-[10px] text-text-muted flex items-center gap-1">
                        <Clock className="w-2.5 h-2.5" />
                        {formatDuration(selectedRun.started_at, selectedRun.completed_at)}
                      </span>
                      <span className="text-[10px] text-text-muted/50">|</span>
                      <button
                        onClick={copyRunId}
                        className="text-[10px] text-text-muted hover:text-text font-mono flex items-center gap-1 transition-colors"
                      >
                        {selectedRun.id}
                        <Copy className="w-2.5 h-2.5" />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleReplay}
                      disabled={replaying || selectedRun.status === "running" || selectedRun.status === "pending"}
                      title="Run again with the same input and workflow definition"
                      className="h-8 px-3 border border-border text-text-muted text-xs rounded-md hover:text-text hover:border-text-muted/40 transition-colors disabled:opacity-40 flex items-center gap-1.5"
                    >
                      {replaying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                      Replay
                    </button>
                    {(selectedRun.status === "running" || selectedRun.status === "pending" || selectedRun.status === "waiting_approval") && (
                      <button
                        onClick={handleCancel}
                        disabled={cancelling}
                        className="h-8 px-3 bg-warn/10 text-warn text-xs font-medium rounded-md hover:bg-warn/20 transition-colors disabled:opacity-50 flex items-center gap-1.5"
                      >
                        {cancelling ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Square className="w-3.5 h-3.5" />
                        )}
                        {cancelling ? "Cancelling..." : "Cancel"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </header>

            <div className="p-5 flex flex-col gap-5">
              {/* ── Error message ── */}
              {selectedRun.error_message && (
                <div className="p-4 bg-warn/10 border border-warn/20 rounded-lg flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-warn shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-medium text-warn">Error</p>
                    <p className="text-xs text-text-muted mt-0.5">{selectedRun.error_message}</p>
                  </div>
                </div>
              )}

              {/* ── Quality (silent-success check) ── */}
              {selectedRun.status === "completed" && (
                <div className="flex flex-col gap-2">
                  {wfQuality?.insight && (
                    <div className="p-3 bg-warn/10 border border-warn/20 rounded-lg text-xs text-warn">{wfQuality.insight}</div>
                  )}
                  <div className="p-3 bg-surface border border-border rounded-lg flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-text">
                        Output quality{" "}
                        {quality ? (
                          <span className={quality.verdict === "ok" ? "text-success" : "text-warn"}>
                            {Math.round(quality.score * 100)}% · {quality.verdict}
                          </span>
                        ) : (
                          <span className="text-text-muted">not evaluated</span>
                        )}
                      </p>
                      {quality?.reasons.map((r, i) => (
                        <p key={i} className="text-[11px] text-text-muted mt-1">• {r}</p>
                      ))}
                    </div>
                    <button
                      onClick={handleFlag}
                      disabled={flagged}
                      className="shrink-0 h-7 px-2.5 rounded-md border border-border text-[11px] text-text-muted hover:text-warn hover:border-warn/40 transition-all disabled:opacity-50"
                    >
                      {flagged ? "Flagged" : "Flag as wrong"}
                    </button>
                  </div>
                </div>
              )}

              {/* ── Stats Row ── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={`p-4 flex items-center gap-3 ${
                  selectedRun.status === "failed" || selectedRun.status === "cancelled"
                    ? "bg-warn/5 border border-warn/20"
                    : selectedRun.status === "completed"
                      ? "bg-success/5 border border-success/20"
                      : "bg-signal/5 border border-signal/20"
                } rounded-lg`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    selectedRun.status === "completed"
                      ? "bg-success/15 text-success"
                      : selectedRun.status === "failed" || selectedRun.status === "cancelled"
                        ? "bg-warn/15 text-warn"
                        : "bg-signal/15 text-signal"
                  }`}>
                    {selectedRun.status === "completed" ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : selectedRun.status === "failed" || selectedRun.status === "cancelled" ? (
                      <XCircle className="w-4 h-4" />
                    ) : (
                      <Terminal className="w-4 h-4" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text">
                      Run {statusLabel[selectedRun.status] || selectedRun.status}
                    </p>
                    <p className="text-xs text-text-muted mt-0.5">
                      {selectedRun.steps.length} steps executed
                    </p>
                  </div>
                </div>
                <div className="p-4 bg-surface border border-border rounded-lg flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-surface-2 flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4 text-text-muted" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text">
                      {selectedRun.steps.filter((s) => s.status === "completed").length} / {selectedRun.steps.length} completed
                    </p>
                    <p className="text-xs text-text-muted mt-0.5">
                      {selectedRun.steps.filter((s) => s.status === "failed").length} failed, {selectedRun.steps.filter((s) => s.status === "waiting_approval").length} awaiting approval
                    </p>
                  </div>
                </div>
              </div>

              {/* ── Execution Flow ── */}
              {selectedRun.steps.length > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-xs font-medium text-text">Execution Flow</p>
                      <p className="text-[10px] text-text-muted mt-0.5">
                        Step-by-step execution status
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      {[
                        { label: "Completed", color: "bg-success" },
                        { label: "Running", color: "bg-signal" },
                        { label: "Pending", color: "bg-accent" },
                        { label: "Failed", color: "bg-warn" },
                        { label: "Approval", color: "bg-accent" },
                      ].map((legend) => (
                        <div key={legend.label} className="flex items-center gap-1.5">
                          <span className={`w-1.5 h-1.5 rounded-full ${legend.color}`} />
                          <span className="text-[10px] text-text-muted">{legend.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-surface border border-border rounded-lg p-4 sm:p-6">
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-0 overflow-x-auto">
                      {selectedRun.steps.map((step, i) => {
                        const Icon = NODE_ICONS[step.node_type] || Code;
                        const state = getNodeState(i, selectedRun.steps, selectedRun.status);
                        const s = nodeStateStyles[state];
                        const isSelected = selectedNodeIdx === i;

                        return (
                          <div key={step.id} className="flex items-center">
                            <button
                              onClick={() => setSelectedNodeIdx(i)}
                              className={`flex flex-col items-center gap-2 px-3 py-3 rounded-lg border transition-all cursor-pointer min-w-[100px] ${
                                isSelected ? `${s.border} ${s.bg}` : "border-transparent hover:bg-surface-2/50"
                              }`}
                            >
                              <div className={`w-8 h-8 rounded-md flex items-center justify-center ${s.iconBg}`}>
                                <Icon className={`w-4 h-4 ${s.text}`} />
                              </div>
                              <span className={`text-xs font-mono ${s.text}`}>{step.node_name.slice(0, 16)}</span>
                              <span className="text-[10px] text-text-muted">{step.node_type}</span>
                              {step.tool_name && (
                                <span className="text-[10px] text-text-muted/70">{step.tool_name}</span>
                              )}
                              {state === "active" && (
                                <span className="w-1.5 h-1.5 rounded-full bg-signal animate-pulse" />
                              )}
                            </button>
                            {i < selectedRun.steps.length - 1 && (
                              <ChevronRight className="w-4 h-4 text-wire mx-1 sm:mx-3 shrink-0 hidden sm:block" />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* ── Node Detail Panel ── */}
              {selectedNode && (
                <div>
                  <div className="bg-surface border border-border rounded-lg overflow-hidden">
                    <div className="flex items-center justify-between px-5 py-3 border-b border-border">
                      <div className="flex items-center gap-3">
                        <h3 className="text-sm font-medium text-text">
                          {selectedNode.node_name}
                        </h3>
                        <span
                          className={`px-2 py-0.5 text-[10px] font-medium rounded-full border ${statusStyles[selectedNode.status] || ""}`}
                        >
                          {selectedNode.status}
                        </span>
                        {selectedNode.started_at && (
                          <span className="text-[10px] text-text-muted">
                            {formatDuration(selectedNode.started_at, selectedNode.completed_at)}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2">
                      {/* Left: Metadata */}
                      <div className="p-5 border-b lg:border-b-0 lg:border-r border-border">
                        <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                          {[
                            { label: "Node ID", value: selectedNode.node_id },
                            { label: "Type", value: selectedNode.node_type },
                            { label: "Tool", value: selectedNode.tool_name || "—" },
                            { label: "Attempt", value: String(selectedNode.attempt_count) },
                            { label: "Started", value: selectedNode.started_at ? new Date(selectedNode.started_at).toLocaleTimeString() : "—" },
                            { label: "Completed", value: selectedNode.completed_at ? new Date(selectedNode.completed_at).toLocaleTimeString() : "—" },
                          ].map((row) => (
                            <div key={row.label}>
                              <p className="text-[10px] text-text-muted/60 uppercase tracking-wider mb-0.5">
                                {row.label}
                              </p>
                              <p className="text-xs text-text font-mono">{row.value}</p>
                            </div>
                          ))}
                        </div>
                        {selectedNode.error && (
                          <div className="mt-3 p-2.5 bg-warn/5 border border-warn/20 rounded-md">
                            <p className="text-[10px] text-warn/80 font-medium mb-0.5">Error</p>
                            <p className="text-xs text-warn font-mono">{selectedNode.error}</p>
                          </div>
                        )}
                      </div>

                      {/* Right: Tabs */}
                      <div>
                        <div className="flex items-center border-b border-border">
                          {[
                            { key: "details" as const, label: "Details", icon: FileText },
                            { key: "logs" as const, label: "Logs", icon: Terminal },
                            { key: "io" as const, label: "Input / Output", icon: Code },
                          ].map((tab) => {
                            const Icon = tab.icon;
                            return (
                              <button
                                key={tab.key}
                                onClick={() => setActiveDetailTab(tab.key)}
                                className={`flex items-center gap-1.5 px-4 py-2.5 text-xs transition-all border-b-2 ${
                                  activeDetailTab === tab.key
                                    ? "border-signal text-signal"
                                    : "border-transparent text-text-muted hover:text-text"
                                }`}
                              >
                                <Icon className="w-3 h-3" />
                                {tab.label}
                              </button>
                            );
                          })}
                        </div>

                        <div className="p-4">
                          {activeDetailTab === "details" && (
                            <div className="space-y-2">
                              <p className="text-xs text-text-muted leading-relaxed">
                                Node <span className="text-text font-mono">{selectedNode.node_name}</span>{" "}
                                ({selectedNode.node_type}) executed with status{" "}
                                <span className={selectedNode.status === "completed" ? "text-success" : selectedNode.status === "failed" ? "text-warn" : "text-signal"}>
                                  {selectedNode.status}
                                </span>
                                .
                              </p>
                              {selectedNode.tool_name && (
                                <p className="text-xs text-text-muted">
                                  Tool: <span className="text-text font-mono">{selectedNode.tool_name}</span>
                                </p>
                              )}
                              {selectedNode.attempt_count > 1 && (
                                <p className="text-xs text-text-muted">
                                  Attempts: <span className="text-text font-mono">{selectedNode.attempt_count}</span>
                                </p>
                              )}
                            </div>
                          )}

                          {activeDetailTab === "logs" && (
                            <div className="space-y-1">
                              {(() => {
                                const lines: string[] = [];
                                if (selectedNode.started_at) {
                                  lines.push(`${new Date(selectedNode.started_at).toLocaleTimeString()} → [info] executing node ${selectedNode.node_id}`);
                                }
                                if (selectedNode.status === "completed") {
                                  lines.push(`${selectedNode.completed_at ? new Date(selectedNode.completed_at).toLocaleTimeString() : ""} → [success] node ${selectedNode.node_id} completed`);
                                } else if (selectedNode.status === "failed") {
                                  lines.push(`${selectedNode.completed_at ? new Date(selectedNode.completed_at).toLocaleTimeString() : ""} → [error] node ${selectedNode.node_id} failed: ${selectedNode.error || "unknown"}`);
                                } else if (selectedNode.status === "waiting_approval") {
                                  lines.push(` → [info] node ${selectedNode.node_id} waiting for approval`);
                                } else {
                                  lines.push(` → [info] node ${selectedNode.node_id} ${selectedNode.status}`);
                                }
                                return lines.map((log, i) => {
                                  const isSuccess = log.includes("[success]");
                                  const isError = log.includes("[error]");
                                  const parts = log.split(" → ");
                                  return (
                                    <div
                                      key={i}
                                      className={`flex gap-2 px-2 py-1 rounded ${
                                        isSuccess
                                          ? "bg-success/5 border-l-2 border-success/30"
                                          : isError
                                            ? "bg-warn/5 border-l-2 border-warn/30"
                                            : ""
                                      }`}
                                    >
                                      <span className="text-text-muted/60 shrink-0 text-[11px]">{parts[0]}</span>
                                      <span
                                        className={
                                          isSuccess
                                            ? "text-success text-[11px]"
                                            : isError
                                              ? "text-warn text-[11px]"
                                              : "text-text-muted text-[11px]"
                                        }
                                      >
                                        {parts[1] || log}
                                      </span>
                                    </div>
                                  );
                                });
                              })()}
                            </div>
                          )}

                          {activeDetailTab === "io" && (
                            <div className="space-y-3">
                              <div>
                                <p className="text-[10px] text-text-muted/60 mb-1.5">Inputs</p>
                                <pre className="bg-surface-2 border border-border rounded-md p-3 text-[11px] font-mono text-text-muted overflow-x-auto">
                                  {selectedNode.tool_inputs
                                    ? JSON.stringify(selectedNode.tool_inputs, null, 2)
                                    : "No inputs"}
                                </pre>
                              </div>
                              <div>
                                <div className="flex items-center justify-between mb-1.5">
                                  <p className="text-[10px] text-text-muted/60">Output</p>
                                  {selectedNode.tool_result && (
                                    <button
                                      onClick={() => navigator.clipboard.writeText(JSON.stringify(selectedNode.tool_result, null, 2))}
                                      className="text-[10px] text-text-muted hover:text-text flex items-center gap-1 transition-colors"
                                    >
                                      <Copy className="w-2.5 h-2.5" />
                                      Copy
                                    </button>
                                  )}
                                </div>
                                <pre className="bg-surface-2 border border-border rounded-md p-3 text-[11px] font-mono text-text-muted overflow-x-auto">
                                  {selectedNode.tool_result
                                    ? JSON.stringify(selectedNode.tool_result, null, 2)
                                    : "No output"}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ── Console Output ── */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-medium text-text-muted">Console Output</p>
                  <button
                    onClick={copyLogs}
                    className="flex items-center gap-1 text-xs text-text-muted hover:text-text transition-all px-2 py-1 rounded-md hover:bg-surface-2"
                  >
                    <Copy className="w-3 h-3 shrink-0" />
                    {copied ? "Copied!" : "Copy"}
                  </button>
                </div>
                <div className="bg-surface-2 border border-border rounded-lg p-4 font-mono text-xs leading-relaxed overflow-x-auto">
                  <div className="flex flex-col gap-0.5">
                    {selectedRun.steps.map((step, i) => {
                      const isSuccess = step.status === "completed";
                      const isError = step.status === "failed";
                      const timeStr = step.started_at ? new Date(step.started_at).toLocaleTimeString() : "?";
                      return (
                        <div
                          key={step.id}
                          className={`flex gap-2 px-2 py-1 rounded -mx-2 ${
                            isSuccess
                              ? "bg-success/5 border-l-2 border-success/30"
                              : isError
                                ? "bg-warn/5 border-l-2 border-warn/30"
                                : step.status === "waiting_approval"
                                  ? "bg-accent/5 border-l-2 border-accent/30"
                                  : ""
                          }`}
                        >
                          <span className="text-text-muted/60 shrink-0">{timeStr}</span>
                          <span
                            className={
                              isSuccess
                                ? "text-success"
                                : isError
                                  ? "text-warn"
                                  : step.status === "waiting_approval"
                                    ? "text-accent"
                                    : "text-text-muted"
                            }
                          >
                            [{step.status}] {step.node_name}
                            {step.tool_name ? ` → ${step.tool_name}` : ""}
                            {step.error ? ` — ${step.error}` : ""}
                          </span>
                        </div>
                      );
                    })}
                    {selectedRun.steps.length === 0 && (
                      <span className="text-text-muted/60">No steps recorded</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
