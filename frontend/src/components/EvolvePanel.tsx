"use client";

import { useState } from "react";
import { Dna, X, Loader2 } from "lucide-react";
import { evolveWorkflow, type EvolveResult, type EvolveVariant, type BackendNode, type BackendEdge } from "@/lib/api";

interface EvolvePanelProps {
  workflowId: string;
  workflowName: string;
  isOpen: boolean;
  onClose: () => void;
  onLoadVariant: (nodes: BackendNode[], edges: BackendEdge[]) => void;
}

const pct = (n: number) => `${Math.round(n * 100)}%`;

export default function EvolvePanel({ workflowId, workflowName, isOpen, onClose, onLoadVariant }: EvolvePanelProps) {
  const [result, setResult] = useState<EvolveResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [generations, setGenerations] = useState(1);
  const [allowGateRemoval, setAllowGateRemoval] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await evolveWorkflow(workflowId, { generations, allowGateRemoval }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Evolution failed");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" onClick={onClose} />
      <div className="absolute right-0 top-0 bottom-0 w-[420px] bg-base border-l border-border shadow-2xl flex flex-col">
        <div className="shrink-0 flex items-center justify-between px-4 h-14 border-b border-border">
          <div className="flex items-center gap-2">
            <Dna className="w-4 h-4 text-accent" />
            <div>
              <h2 className="text-sm font-medium text-text">Evolve</h2>
              <p className="text-[10px] text-text-muted">{workflowName}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-text-muted hover:text-text hover:bg-surface-2 rounded-md transition-all">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4 flex flex-col gap-3">
          <p className="text-xs text-text-muted">
            Mutates this workflow, test-runs each variant in a sandbox (mock tools only), and ranks them by how often they
            finish without failing or needing a human.
          </p>
          <label className="flex items-center justify-between text-xs text-text-muted">
            Generations
            <select
              value={generations}
              onChange={(e) => setGenerations(Number(e.target.value))}
              className="h-7 px-2 bg-surface border border-border rounded-md text-text"
            >
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <label className="flex items-start gap-2 text-xs text-text-muted">
            <input type="checkbox" checked={allowGateRemoval} onChange={(e) => setAllowGateRemoval(e.target.checked)} className="mt-0.5" />
            <span>Also try removing approval gates (a safety change: review any variant that does before using it)</span>
          </label>
          <button
            onClick={run}
            disabled={loading}
            className="h-8 px-3 rounded-lg bg-text text-base text-xs font-medium hover:bg-text/90 transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Dna className="w-3.5 h-3.5" />}
            {loading ? "Testing variants..." : result ? "Run again" : "Run evolution"}
          </button>

          {error && <div className="p-3 bg-warn/10 border border-warn/20 rounded-lg text-xs text-warn">{error}</div>}

          {result && (
            <>
              <p className="text-xs text-text-muted">
                Baseline: <span className="text-text font-medium">{pct(result.baseline)}</span> success
              </p>
              {result.variants.length === 0 && (
                <p className="text-xs text-text-muted">No mutations available for this workflow.</p>
              )}
              {result.variants.map((v, i) => (
                <VariantCard key={i} v={v} baseline={result.baseline} onLoad={() => onLoadVariant(v.nodes, v.edges)} />
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function VariantCard({ v, baseline, onLoad }: { v: EvolveVariant; baseline: number; onLoad: () => void }) {
  const better = v.fitness > baseline;
  return (
    <div className="p-3 bg-surface border border-border rounded-lg">
      <p className="text-xs text-text mb-2">{v.description}</p>
      <div className="flex items-center justify-between">
        <span
          className={`px-2 py-0.5 text-[10px] font-medium rounded-full border ${
            better ? "bg-success/10 text-success border-success/20" : "bg-surface-2 text-text-muted border-border"
          }`}
        >
          {pct(v.fitness)} success{better ? " ▲" : ""}
        </span>
        {v.removes_approval && <span className="text-[10px] text-warn">removes approval gate</span>}
        <button onClick={onLoad} className="text-[11px] text-text-muted hover:text-accent transition-all">
          Load into canvas
        </button>
      </div>
    </div>
  );
}
