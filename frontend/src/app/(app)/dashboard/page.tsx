"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Workflow,
  Terminal,
  Puzzle,
  ChevronRight,
  RefreshCw,
  Search,
  Plus,
  Inbox,
  Trash2,
} from "lucide-react";
import {
  listWorkflows,
  deleteWorkflow as apiDeleteWorkflow,
  runWorkflow,
  type WorkflowListItem,
} from "@/lib/api";

const statusStyles: Record<string, string> = {
  completed: "bg-success/10 text-success border-success/20",
  running: "bg-signal/10 text-signal border-signal/20",
  pending: "bg-accent/10 text-accent border-accent/20",
  error: "bg-warn/10 text-warn border-warn/20",
};

const statusLabel: Record<string, string> = {
  completed: "Completed",
  running: "Running",
  pending: "Pending",
  error: "Failed",
};

export default function DashboardPage() {
  const [workflows, setWorkflows] = useState<WorkflowListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<string>("all");
  const [runningId, setRunningId] = useState<string | null>(null);
  const router = useRouter();

  const loadWorkflows = useCallback(async () => {
    setError(null);
    try {
      const data = await listWorkflows();
      // Map backend status strings to frontend labels
      const mapped = data.map((w) => ({
        ...w,
        status: w.metadata?.last_status as string || "pending",
      }));
      setWorkflows(mapped);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load workflows");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWorkflows();
  }, [loadWorkflows]);

  const handleDelete = useCallback(async (id: string) => {
    try {
      await apiDeleteWorkflow(id);
      setWorkflows((prev) => prev.filter((wf) => wf.id !== id));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to delete");
    }
  }, []);

  const handleRerun = useCallback(async (id: string) => {
    setRunningId(id);
    try {
      const result = await runWorkflow(id);
      const executionId = (result as { id?: string })?.id;
      await loadWorkflows();
      if (executionId) {
        router.push(`/console?run=${executionId}`);
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to run workflow");
    } finally {
      setRunningId(null);
    }
  }, [loadWorkflows, router]);

  const filtered = useMemo(() => {
    return workflows.filter((wf) => {
      const matchesQuery =
        wf.name.toLowerCase().includes(query.toLowerCase()) ||
        wf.description.toLowerCase().includes(query.toLowerCase());
      const matchesFilter = filter === "all" || (wf.status || "") === filter;
      return matchesQuery && matchesFilter;
    });
  }, [workflows, query, filter]);

  return (
    <div className="flex flex-col h-screen">
      <header className="shrink-0 border-b border-border bg-base/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-5 h-14">
          <div>
            <h1 className="text-base font-semibold text-text tracking-tight">
              Dashboard
            </h1>
            <p className="text-xs text-text-muted">
              Monitor your workflows and recent runs
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="text"
                placeholder="Search workflows..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="h-9 pl-8 pr-3 bg-surface border border-border rounded-md text-sm text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-1 focus:ring-text-muted/40 w-52"
              />
            </div>
            <Link
              href="/builder"
              className="h-9 px-3 bg-text text-base text-sm font-medium rounded-md hover:bg-text/90 transition-all hover:opacity-80 flex items-center gap-1.5 shrink-0"
            >
              <Plus className="w-4 h-4 shrink-0" />
              <span className="hidden sm:inline">New workflow</span>
              <span className="sm:hidden">New</span>
            </Link>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-5 pb-20 md:pb-5">
        {error && (
          <div className="mb-4 p-3 bg-warn/10 border border-warn/20 rounded-lg text-xs text-warn">
            {error}
          </div>
        )}

        {/* ── STAT TILES ── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            {
              value: String(workflows.length),
              label: "Total workflows",
              icon: Workflow,
            },
            {
              value: String(workflows.filter((w) => w.status === "running").length),
              label: "Active runs",
              accent: true,
              icon: Terminal,
            },
            {
              value: "—",
              label: "Success rate",
              icon: Puzzle,
            },
            {
              value: "—",
              label: "Avg duration",
              icon: ChevronRight,
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className="p-5 bg-surface border border-border rounded-xl"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-8 h-8 rounded-lg bg-surface-2 border border-border/50 flex items-center justify-center">
                  <stat.icon className="w-4 h-4 text-text-muted" />
                </div>
              </div>
              <p
                className={`text-2xl font-semibold tracking-tight ${
                  stat.accent ? "text-signal" : "text-text"
                }`}
              >
                {stat.value}
              </p>
              <p className="text-xs text-text-muted mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* ── FILTER TABS ── */}
        <div className="flex items-center gap-1.5 mb-4">
          {["all", "running", "completed", "pending", "error"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3.5 py-2 text-xs font-medium rounded-md transition-all capitalize ${
                filter === f
                  ? "bg-text/8 border border-text-muted/30 text-text"
                  : "border border-transparent text-text-muted hover:text-text hover:bg-surface-2 hover:border-border/60"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* ── WORKFLOW LIST ── */}
        <h2 className="text-sm font-medium text-text mb-3">Workflows</h2>
        {loading ? (
          <div className="text-center py-16 text-text-muted text-sm">
            Loading workflows...
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-surface-2 border border-border mb-4">
              <Inbox className="w-5 h-5 text-text-muted" />
            </div>
            <p className="text-sm text-text-muted mb-1">No workflows found</p>
            <p className="text-xs text-text-muted/70">
              {query || filter !== "all"
                ? "Try adjusting your search or filter criteria"
                : "Create your first workflow to get started"}
            </p>
          </div>
        ) : (
          <div className="flex flex-col">
            {filtered.map((wf) => (
              <div
                key={wf.id}
                className="flex items-center gap-3 px-4 py-3.5 bg-surface border border-border rounded-lg mb-2 hover:bg-surface-2 transition-colors group"
              >
                <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/50 flex items-center justify-center shrink-0">
                  <Workflow className="w-4 h-4 text-text-muted" />
                </div>

                <div className="flex-1 min-w-0">
                  <Link href={`/builder?id=${encodeURIComponent(wf.id)}`} className="block text-sm font-medium text-text truncate hover:text-accent">
                    {wf.name}
                  </Link>
                  <p className="text-xs text-text-muted truncate mt-0.5">
                    {wf.description}
                  </p>
                </div>

                <span
                  className={`shrink-0 px-2.5 py-1 text-xs font-medium rounded-full border ${
                    statusStyles[wf.status || "pending"] || statusStyles.pending
                  }`}
                >
                  {statusLabel[wf.status || "pending"] || wf.status || "pending"}
                </span>

                <span className="text-xs text-text-muted w-24 text-right hidden sm:block">
                  {wf.created_at ? new Date(wf.created_at).toLocaleDateString() : "—"}
                </span>

                <div className="flex items-center gap-0.5 shrink-0">
                  <button
                    onClick={() => handleRerun(wf.id)}
                    disabled={runningId === wf.id}
                    className="p-2 text-text-muted hover:text-signal hover:bg-signal/10 rounded-md transition-all hover:opacity-80 disabled:opacity-40"
                    title="Run workflow"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${runningId === wf.id ? "animate-spin" : ""}`} />
                  </button>
                  <button
                    onClick={() => handleDelete(wf.id)}
                    className="p-2 text-text-muted hover:text-warn hover:bg-warn/10 rounded-md transition-all hover:opacity-80"
                    title="Delete"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
