"use client";

import { useEffect, useState } from "react";
import { getAnalyticsStats, type AnalyticsStats } from "@/lib/api";

const pct = (n: number) => `${(n * 100).toFixed(1)}%`;

export default function AnalyticsPage() {
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnalyticsStats()
      .then(setStats)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  if (error) return <div className="p-6 text-sm text-warn">{error}</div>;
  if (!stats) return <div className="p-6 text-sm text-text-muted">Loading...</div>;

  return (
    <div className="p-6 flex flex-col gap-6 overflow-auto">
      <h1 className="text-lg font-medium text-text">Analytics</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Total runs" value={String(stats.total_runs)} />
        <Stat label="Failure rate" value={pct(stats.failure_rate)} warn={stats.failure_rate > 0.2} />
        {Object.entries(stats.by_status).map(([s, n]) => (
          <Stat key={s} label={s} value={String(n)} />
        ))}
      </div>

      <div>
        <h2 className="text-sm font-medium text-text mb-2">Output quality by workflow</h2>
        {stats.workflows.length === 0 ? (
          <p className="text-xs text-text-muted">No completed runs yet.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {stats.workflows.map((w) => (
              <div key={w.id} className="p-3 bg-surface border border-border rounded-lg">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-text font-medium">{w.name}</span>
                  <span className="text-text-muted">
                    {w.corrected}/{w.runs} flagged · {pct(w.override_rate)} override
                    {w.avg_score !== null && ` · ${Math.round(w.avg_score * 100)}% avg score`}
                  </span>
                </div>
                <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden">
                  <div className="h-full bg-warn" style={{ width: pct(w.override_rate) }} />
                </div>
                {w.insight && <p className="text-[11px] text-warn mt-1.5">{w.insight}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className="text-sm font-medium text-text mb-2">By tool</h2>
        {stats.tools.length === 0 ? (
          <p className="text-xs text-text-muted">No tool steps recorded yet. Run a workflow first.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {stats.tools.map((t) => (
              <div key={t.tool} className="p-3 bg-surface border border-border rounded-lg">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-text font-medium">{t.tool}</span>
                  <span className="text-text-muted">
                    {t.steps} steps · {t.avg_seconds ?? "–"}s avg · {pct(t.failure_rate)} failed
                  </span>
                </div>
                <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden">
                  <div className="h-full bg-warn" style={{ width: pct(t.failure_rate) }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, warn }: { label: string; value: string; warn?: boolean }) {
  return (
    <div className="p-3 bg-surface border border-border rounded-lg">
      <p className="text-[10px] uppercase tracking-wide text-text-muted">{label}</p>
      <p className={`text-xl font-medium ${warn ? "text-warn" : "text-text"}`}>{value}</p>
    </div>
  );
}
