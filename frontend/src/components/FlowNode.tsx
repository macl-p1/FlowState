"use client";

import { memo } from "react";
import {
  Handle,
  Position,
  type Node,
  type Edge,
} from "@xyflow/react";
import { GripVertical, Trash2 } from "lucide-react";
import "@xyflow/react/dist/style.css";

/* ── Tool icon map ── */
const TOOL_ICONS: Record<string, { color: string; label: string }> = {
  "HTTP Request": { color: "#4A9EFF", label: "HTTP" },
  "Database Query": { color: "#3DD68C", label: "DB" },
  "Send Email": { color: "#E8A83E", label: "EML" },
  "Wait / Delay": { color: "#6B6F7B", label: "WAIT" },
  "Transform": { color: "#A78BFA", label: "XFM" },
  "Webhook": { color: "#4A9EFF", label: "WEB" },
};

/* ── Node type color map ── */
const TYPE_COLORS: Record<string, { border: string; bg: string; badge: string }> = {
  trigger:   { border: "border-success/40", bg: "bg-success/5", badge: "bg-success/10 text-success" },
  action:    { border: "border-wire", bg: "bg-surface", badge: "bg-base text-text-muted" },
  condition: { border: "border-accent/40", bg: "bg-accent/5", badge: "bg-accent/10 text-accent" },
  approval:  { border: "border-signal/40", bg: "bg-signal/5", badge: "bg-signal/10 text-signal" },
  wait:      { border: "border-text-muted/30", bg: "bg-surface", badge: "bg-base text-text-muted" },
  end:       { border: "border-success/40", bg: "bg-success/5", badge: "bg-success/10 text-success" },
};

export interface FlowNodeData {
  name: string;
  tool: string;
  detail: string;
  nodeType?: string;
  /** Live execution state set by the builder while a run is in progress. */
  runStatus?: "running" | "completed" | "failed" | "waiting" | "skipped";
  [key: string]: unknown;
}

export type FlowNode = Node<FlowNodeData>;
export type FlowEdge = Edge;

type FlowNodeComponentProps = {
  id: string;
  data: FlowNodeData;
  selected: boolean;
};

const RUN_RING: Record<string, string> = {
  running: "border-signal shadow-lg shadow-signal/30 ring-2 ring-signal/40 animate-pulse",
  completed: "border-success/60 ring-1 ring-success/30",
  failed: "border-warn shadow-lg shadow-warn/20 ring-2 ring-warn/40",
  waiting: "border-accent/60 ring-2 ring-accent/30",
  skipped: "opacity-50",
};

function FlowNodeComponent({ data, selected, id }: FlowNodeComponentProps) {
  const toolInfo = TOOL_ICONS[data.tool] || { color: "#6B6F7B", label: "?" };
  const typeInfo = TYPE_COLORS[data.nodeType || "action"] || TYPE_COLORS.action;

  return (
    <div
      className={`
        min-w-[220px] max-w-[260px] rounded-xl border backdrop-blur-sm
        transition-shadow duration-200
        ${data.runStatus
          ? RUN_RING[data.runStatus]
          : selected
          ? "border-signal/50 shadow-lg shadow-signal/10 ring-1 ring-signal/20"
          : `${typeInfo.border} ${typeInfo.bg} hover:shadow-md`
        }
      `}
      style={selected ? { background: "rgba(15,17,23,0.98)" } : undefined}
    >
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !border-2 !border-border !bg-surface"
      />

      {/* Header — drag handle */}
      <div
        className="flex items-center gap-2 px-3 py-2 border-b border-border cursor-grab active:cursor-grabbing select-none"
        style={{ borderLeft: `2px solid ${toolInfo.color}20` }}
      >
        <GripVertical className="w-3 h-3 text-text-muted/40 shrink-0" />
        <span className="text-[10px] text-text-muted/50 font-medium truncate">
          {data.nodeType?.toUpperCase() || "ACTION"}
        </span>
        <span className="ml-auto text-[10px] font-mono text-text-muted/30">
          {id?.slice(-4)}
        </span>
      </div>

      {/* Body */}
      <div className="p-3">
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
            style={{ background: `${toolInfo.color}15`, border: `1px solid ${toolInfo.color}30` }}
          >
            <span className="text-[9px] font-bold font-mono" style={{ color: toolInfo.color }}>
              {toolInfo.label}
            </span>
          </div>
          <span className="text-sm font-medium text-text truncate flex-1">
            {data.name}
          </span>
          <button
            onClick={() => {
              window.dispatchEvent(new CustomEvent("flow:deleteNode", { detail: { id } }));
            }}
            className="p-1 text-text-muted hover:text-warn hover:bg-warn/10 rounded-md active:scale-95 transition-all shrink-0"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-1.5 mb-2">
          <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${typeInfo.badge}`}>
            {data.tool}
          </span>
        </div>

        <p className="text-xs text-text-muted/70 leading-relaxed line-clamp-2">
          {data.detail}
        </p>
      </div>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !border-2 !border-border !bg-surface"
      />
    </div>
  );
}

export const flowNodeTypes = {
  flowNode: memo(FlowNodeComponent),
};
