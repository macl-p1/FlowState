"use client";

import { useState, useMemo, useEffect } from "react";
import Link from "next/link";
import { listRuns, deleteRun, type RunListItem } from "@/lib/api";
import {
  Search,
  ArrowUp,
  ArrowDown,
  Trash2,
} from "lucide-react";

interface HistoryRow {
  id: string;
  name: string;
  status: string;
  startedAt: string;
  completedAt: string | null;
  duration: string;
}

/** Backend statuses -> the 4 display buckets used below. */
const STATUS_BUCKET: Record<string, string> = {
  completed: "completed",
  running: "running",
  retrying: "running",
  pending: "pending",
  waiting_approval: "pending",
  failed: "error",
  cancelled: "error",
};

function toRow(r: RunListItem): HistoryRow {
  const secs = r.started_at && r.completed_at ? (Date.parse(r.completed_at) - Date.parse(r.started_at)) / 1000 : null;
  return {
    id: r.id,
    name: r.workflow_name,
    status: STATUS_BUCKET[r.status] ?? "pending",
    startedAt: r.started_at ? new Date(r.started_at).toLocaleString() : "—",
    completedAt: r.completed_at ? new Date(r.completed_at).toLocaleTimeString() : null,
    duration: secs === null ? (r.status === "running" ? "Running" : "—") : `${secs.toFixed(1)}s`,
  };
}

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

const statusDot: Record<string, string> = {
  completed: "bg-success",
  running: "bg-signal",
  pending: "bg-accent",
  error: "bg-warn",
};

export default function HistoryPage() {
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState<"date" | "name">("date");
  const [runs, setRuns] = useState<HistoryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listRuns(200)
      .then((data) => setRuns(data.map(toRow)))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load runs"))
      .finally(() => setLoading(false));
  }, []);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const handleDeleteRun = (id: string) => {
    if (deleteConfirmId !== id) {
      setDeleteConfirmId(id);
      setTimeout(() => setDeleteConfirmId(null), 3000);
      return;
    }
    setDeleteConfirmId(null);
    deleteRun(id)
      .then(() => setRuns((prev) => prev.filter((r) => r.id !== id)))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to delete run"));
  };

  const sorted = useMemo(() => [...runs]
    .filter(
      (r) =>
        r.name.toLowerCase().includes(query.toLowerCase()) ||
        r.id.includes(query)
    )
    .sort((a, b) => {
      if (sortBy === "name") return a.name.localeCompare(b.name);
      return b.startedAt.localeCompare(a.startedAt);
    }),
  [runs, query, sortBy]);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="shrink-0 border-b border-border">
        <div className="flex items-center justify-between px-5 h-14">
          <div>
            <h1 className="text-base font-semibold text-text tracking-tight">
              Run History
            </h1>
            <p className="text-xs text-text-muted">
              All workflow executions across your workspace
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="text"
                placeholder="Search runs..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="h-9 pl-8 pr-3 bg-surface border border-border rounded-md text-sm text-text placeholder:text-text-muted/60 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/50 w-52"
              />
            </div>
            <button
              onClick={() =>
                setSortBy((s) => (s === "date" ? "name" : "date"))
              }
              className="h-9 px-3.5 border border-wire text-text-muted text-xs rounded-md hover:border-text-muted hover:text-text hover:bg-surface-2 hover:opacity-90 transition-all flex items-center gap-1.5"
            >
              {sortBy === "date" ? (
                <ArrowDown className="w-3.5 h-3.5" />
              ) : (
                <ArrowUp className="w-3.5 h-3.5" />
              )}
              Sort: {sortBy === "date" ? "Date" : "Name"}
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-5 pb-20 md:pb-5 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[length:20px_20px] pointer-events-none" aria-hidden="true" />
        <div className="relative">
        {/* Table */}
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          {/* Table header */}
          <div
            className="grid gap-3 px-4 py-2.5 border-b border-wire bg-surface-2"
            style={{ gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 60px" }}
          >
            <span className="text-xs text-text-muted font-medium">Run</span>
            <span className="text-xs text-text-muted font-medium">Started</span>
            <span className="text-xs text-text-muted font-medium">Duration</span>
            <span className="text-xs text-text-muted font-medium">Status</span>
            <span className="text-xs text-text-muted font-medium">Completed</span>
            <span></span>
          </div>

          {/* Rows */}
          {sorted.map((run, idx) => (
            <div
              key={run.id}
              className={`grid gap-3 px-4 py-3 border-b border-border last:border-b-0 items-center text-left ${
                idx % 2 === 1 ? "bg-surface-2/30" : "bg-transparent"
              } hover:bg-surface-2/80 hover:opacity-95 transition-all`}
              style={{ gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 60px" }}
            >
              {/* Name */}
              <div className="flex items-center gap-2 min-w-0">
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${statusDot[run.status]}`}
                />
                <Link href={`/console?run=${encodeURIComponent(run.id)}`} className="text-sm text-text truncate hover:text-accent">{run.name}</Link>
              </div>

              {/* Started */}
              <span className="text-xs text-text-muted whitespace-nowrap truncate">{run.startedAt}</span>

              {/* Duration */}
              <span className="text-xs text-text-muted">{run.duration}</span>

              {/* Status */}
              <span
                className={`px-2 py-0.5 text-[10px] font-medium rounded-full border w-fit ${statusStyles[run.status]}`}
              >
                {statusLabel[run.status]}
              </span>

              {/* Completed */}
              <span className="text-xs text-text-muted">
                {run.completedAt ?? "—"}
              </span>

              {/* Actions */}
              <button
                onClick={() => handleDeleteRun(run.id)}
                className={`p-2 rounded-md transition-all w-fit shrink-0 ${
                  deleteConfirmId === run.id
                    ? "text-warn bg-warn/10 border border-warn/30"
                    : "text-text-muted hover:text-warn hover:bg-warn/10 opacity-70 hover:opacity-100"
                }`}
                title={deleteConfirmId === run.id ? "Click again to confirm deletion" : "Delete"}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}

          {error && <div className="p-3 text-xs text-warn">{error}</div>}
          {!loading && !error && sorted.length === 0 && (
            <div className="text-center py-12 text-text-muted text-sm">
              {runs.length === 0 ? "No runs yet. Run a workflow from the builder." : "No runs match your search."}
            </div>
          )}
        </div>

        </div>
      </div>
    </div>
  );
}
