"use client";

import { useState, useEffect, useCallback } from "react";
import { Zap, X, Loader2, Trash2, Copy, Clock, Webhook } from "lucide-react";
import {
  listTriggers,
  createTrigger,
  setTriggerEnabled,
  deleteTrigger,
  webhookUrl,
  type TriggerItem,
} from "@/lib/api";

const PRESETS: { label: string; seconds: number }[] = [
  { label: "Every minute", seconds: 60 },
  { label: "Every 5 minutes", seconds: 300 },
  { label: "Every hour", seconds: 3600 },
  { label: "Every day", seconds: 86400 },
];

interface TriggersPanelProps {
  workflowId: string;
  workflowName: string;
  isOpen: boolean;
  onClose: () => void;
}

function describe(t: TriggerItem): string {
  if (t.kind === "webhook") return "Webhook";
  if (t.config.cron) return `Cron ${t.config.cron}`;
  const preset = PRESETS.find((p) => p.seconds === t.config.interval_seconds);
  return preset ? preset.label : `Every ${t.config.interval_seconds}s`;
}

export default function TriggersPanel({ workflowId, workflowName, isOpen, onClose }: TriggersPanelProps) {
  const [items, setItems] = useState<TriggerItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [kind, setKind] = useState<"schedule" | "webhook">("schedule");
  const [seconds, setSeconds] = useState(300);
  const [cron, setCron] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!isOpen) return;
    setLoading(true);
    try {
      setItems(await listTriggers(workflowId));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load triggers");
    } finally {
      setLoading(false);
    }
  }, [isOpen, workflowId]);

  useEffect(() => {
    load();
  }, [load]);

  const act = async (fn: () => Promise<unknown>) => {
    try {
      await fn();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    }
  };

  const add = () =>
    act(() =>
      createTrigger(workflowId, kind === "webhook" ? { kind } : cron.trim() ? { kind, cron: cron.trim() } : { kind, interval_seconds: seconds })
    );

  const copy = (t: TriggerItem) => {
    navigator.clipboard.writeText(webhookUrl(t));
    setCopied(t.id);
    setTimeout(() => setCopied(null), 1500);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" onClick={onClose} />
      <div className="absolute right-0 top-0 bottom-0 w-[420px] bg-base border-l border-border shadow-2xl flex flex-col">
        <div className="shrink-0 flex items-center justify-between px-4 h-14 border-b border-border">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-accent" />
            <div>
              <h2 className="text-sm font-medium text-text">Triggers</h2>
              <p className="text-[10px] text-text-muted">{workflowName}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-text-muted hover:text-text hover:bg-surface-2 rounded-md transition-all">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4 flex flex-col gap-4">
          <div className="p-3 bg-surface border border-border rounded-lg flex flex-col gap-2.5">
            <p className="text-xs font-medium text-text">Run this workflow automatically</p>
            <div className="flex gap-2">
              {(["schedule", "webhook"] as const).map((k) => (
                <button
                  key={k}
                  onClick={() => setKind(k)}
                  className={`flex-1 h-8 rounded-md border text-xs flex items-center justify-center gap-1.5 transition-all ${
                    kind === k ? "border-accent/50 text-accent bg-accent/10" : "border-border text-text-muted hover:text-text"
                  }`}
                >
                  {k === "schedule" ? <Clock className="w-3.5 h-3.5" /> : <Webhook className="w-3.5 h-3.5" />}
                  {k === "schedule" ? "Schedule" : "Webhook"}
                </button>
              ))}
            </div>
            {kind === "schedule" ? (
              <>
                <select
                  value={seconds}
                  onChange={(e) => setSeconds(Number(e.target.value))}
                  disabled={!!cron.trim()}
                  className="h-8 px-2 bg-base border border-border rounded-md text-xs text-text disabled:opacity-40"
                >
                  {PRESETS.map((p) => (
                    <option key={p.seconds} value={p.seconds}>{p.label}</option>
                  ))}
                </select>
                <input
                  value={cron}
                  onChange={(e) => setCron(e.target.value)}
                  placeholder="or cron (UTC), e.g. 0 9 * * 1"
                  className="h-8 px-2 bg-base border border-border rounded-md text-xs text-text placeholder:text-text-muted/50 font-mono"
                />
              </>
            ) : (
              <p className="text-[11px] text-text-muted">
                Gives you a secret URL. POST JSON to it and the body becomes the run&apos;s input.
              </p>
            )}
            <button
              onClick={add}
              className="h-8 rounded-md bg-text text-base text-xs font-medium hover:bg-text/90 transition-all"
            >
              Add trigger
            </button>
          </div>

          {error && <div className="p-3 bg-warn/10 border border-warn/20 rounded-lg text-xs text-warn">{error}</div>}
          {loading && <Loader2 className="w-4 h-4 text-text-muted animate-spin self-center" />}
          {!loading && items.length === 0 && !error && (
            <p className="text-xs text-text-muted text-center py-6">No triggers yet. This workflow only runs when you start it.</p>
          )}

          {items.map((t) => (
            <div key={t.id} className="p-3 bg-surface border border-border rounded-lg flex flex-col gap-1.5">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-text flex items-center gap-1.5">
                  {t.kind === "webhook" ? <Webhook className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
                  {describe(t)}
                </span>
                <div className="flex items-center gap-1">
                  <label className="flex items-center gap-1 text-[11px] text-text-muted">
                    <input
                      type="checkbox"
                      checked={t.enabled}
                      onChange={(e) => act(() => setTriggerEnabled(t.id, e.target.checked))}
                    />
                    On
                  </label>
                  <button
                    onClick={() => act(() => deleteTrigger(t.id))}
                    className="p-1 text-text-muted hover:text-warn hover:bg-warn/10 rounded-md transition-all"
                    title="Delete trigger"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              {t.kind === "webhook" ? (
                <button
                  onClick={() => copy(t)}
                  className="text-left text-[10px] font-mono text-text-muted hover:text-text break-all flex items-start gap-1.5"
                >
                  <Copy className="w-3 h-3 shrink-0 mt-0.5" />
                  {copied === t.id ? "Copied!" : webhookUrl(t)}
                </button>
              ) : (
                <p className="text-[10px] text-text-muted">
                  {t.enabled && t.next_run_at ? `Next: ${new Date(t.next_run_at + "Z").toLocaleString()}` : "Paused"}
                  {t.config.last_error ? ` · last error: ${t.config.last_error}` : ""}
                </p>
              )}
              {t.last_run_at && (
                <p className="text-[10px] text-text-muted/70">Last fired {new Date(t.last_run_at + "Z").toLocaleString()}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
