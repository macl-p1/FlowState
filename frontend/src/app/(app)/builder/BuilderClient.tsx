"use client";

import { useState, useCallback, useEffect, useRef, memo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ReactFlowProvider, useReactFlow } from "@xyflow/react";
import {
  ReactFlow,
  Background,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
  BackgroundVariant,
  type OnConnect,
} from "@xyflow/react";
import {
  generateWorkflow,
  getWorkflow,
  startWorkflowRun,
  openRunStream,
  getRun,
  type RunStep,
  saveWorkflow,
  saveWorkflowDirect,
  runWorkflow,
  type BackendNode,
  type BackendEdge,
} from "@/lib/api";
import type { FlowNode, FlowEdge, FlowNodeData } from "@/components/FlowNode";
import {
  Plus,
  Save,
  MessageSquare,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Dna,
  Zap,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize,
  XIcon,
  Play,
  Terminal,
  History,
} from "lucide-react";
import { flowNodeTypes } from "@/components/FlowNode";
import VersionHistoryPanel from "@/components/VersionHistoryPanel";
import SuggestionsPanel from "@/components/SuggestionsPanel";
import EvolvePanel from "@/components/EvolvePanel";
import TriggersPanel from "@/components/TriggersPanel";

/* ── Custom edge with visible delete button ── */
import { BaseEdge, EdgeProps, getSmoothStepPath, type Edge as EdgeType } from "@xyflow/react";

function LabeledEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  markerEnd,
  style,
}: EdgeProps<EdgeType>) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX, sourceY, targetX, targetY,
    sourcePosition, targetPosition,
  });
  const label = typeof data?.label === "string" ? data.label : "";

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
      {label && (
        <foreignObject
          x={labelX - 40}
          y={labelY - 10}
          width={80}
          height={20}
          style={{ overflow: "visible", pointerEvents: "none" }}
        >
          <div className="flex items-center justify-center">
            <span
              className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-base/80 border border-border text-text-muted whitespace-nowrap pointer-events-auto"
              style={{ backdropFilter: "blur(4px)" }}
            >
              {label}
            </span>
          </div>
        </foreignObject>
      )}
      <foreignObject
        x={labelX - 12}
        y={labelY - 24}
        width={24}
        height={24}
        style={{ overflow: "visible", opacity: selected ? 1 : 0, transition: "opacity 0.15s", pointerEvents: "none" }}
      >
        <button
          onClick={(e) => {
            e.stopPropagation();
            window.dispatchEvent(new CustomEvent("flow:deleteEdge", { detail: { id } }));
          }}
          className="w-5 h-5 flex items-center justify-center rounded-full bg-warn/90 hover:bg-warn border border-warn/50 text-white pointer-events-auto active:scale-90 transition-all shadow-lg"
          style={{ fontSize: 10 }}
        >
          <XIcon className="w-3 h-3" />
        </button>
      </foreignObject>
    </>
  );
}

const LabeledEdgeMemo = memo(LabeledEdge);

export { LabeledEdgeMemo as LabeledEdge };

/* ──────────────────────────────────────────────
   Configuration
   ────────────────────────────────────────────── */
const GRID = 15;

const tools = [
  { name: "HTTP Request", category: "integration" },
  { name: "Database Query", category: "data" },
  { name: "Send Email", category: "communication" },
  { name: "Wait / Delay", category: "control" },
  { name: "Transform", category: "data" },
  { name: "Webhook", category: "integration" },
];

const defaultNodes: FlowNode[] = [];

const defaultEdges: FlowEdge[] = [];

function snap(v: number) {
  return Math.round(v / GRID) * GRID;
}

/** Backend graph -> React Flow graph. Keeps the original node in data.raw so saving loses nothing. */
function toFlowGraph(bNodes: BackendNode[], bEdges: BackendEdge[]): { nodes: FlowNode[]; edges: FlowEdge[] } {
  const nodes: FlowNode[] = bNodes.map((node, index) => ({
    id: node.id,
    type: "flowNode",
    position: (node.position as { x: number; y: number } | undefined) ?? {
      x: snap(80 + (index % 3) * 300),
      y: snap(80 + Math.floor(index / 3) * 180),
    },
    data: {
      name: node.name || `Node ${index + 1}`,
      tool: (node.tool as string) || "",
      detail: (node.detail || node.expression || node.reason || "") as string,
      nodeType: node.type || "action",
      raw: node,
    },
  }));
  const edges: FlowEdge[] = bEdges.map((e, i) => ({
    id: `e-${i}`,
    source: e.from,
    target: e.to,
    animated: true,
    style: { stroke: "#3A3F4E", strokeWidth: 1.5 },
    label: e.condition,
  }));
  return { nodes, edges };
}

/** React Flow graph -> backend graph (what the API stores and the runner compiles). */
function toBackendGraph(fNodes: FlowNode[], fEdges: FlowEdge[]): { nodes: BackendNode[]; edges: BackendEdge[] } {
  return {
    nodes: fNodes.map((n) => {
      const d = n.data as FlowNodeData;
      return {
        ...((d.raw as BackendNode | undefined) ?? {}),
        id: n.id,
        type: d.nodeType || "action",
        name: d.name,
        tool: d.tool,
        detail: d.detail,
        position: n.position,
      };
    }),
    edges: fEdges.map((e) => ({ from: e.source, to: e.target, ...(e.label ? { condition: String(e.label) } : {}) })),
  };
}

/* ──────────────────────────────────────────────
   Inner component (needs useReactFlow)
   ────────────────────────────────────────────── */
function BuilderInner({
  initialPrompt = "",
  initialName = "",
  initialId = "",
}: { initialPrompt: string; initialName: string; initialId?: string }) {
  const router = useRouter();
  const reactFlowInstance = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [configName, setConfigName] = useState(initialName || "");
  const [configPrompt, setConfigPrompt] = useState(defaultNodes[0]?.data.detail || "");
  const [saved, setSaved] = useState(false);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);
  const [genSuccess, setGenSuccess] = useState(false);
  const [savedWorkflowId, setSavedWorkflowId] = useState<string | null>(null);

  // Execution
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<{
    execution_id: string;
    status: string;
    steps: Array<{
      id: string;
      node_name: string;
      node_type: string;
      status: string;
      tool_name: string | null;
      error: string | null;
    }>;
  } | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  // Version history panel
  const [historyOpen, setHistoryOpen] = useState(false);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const [evolveOpen, setEvolveOpen] = useState(false);
  const [triggersOpen, setTriggersOpen] = useState(false);

  const handleLoadVersion = useCallback((nodes: BackendNode[], edges: BackendEdge[]) => {
    const g = toFlowGraph(nodes, edges);
    setNodes(g.nodes);
    setEdges(g.edges);
    setSelectedNode(null);
  }, [setNodes, setEdges]);

  /* Open an existing workflow (?id=...) so Save adds a version instead of creating a copy */
  useEffect(() => {
    if (!initialId) return;
    getWorkflow(initialId)
      .then((wf) => {
        const g = toFlowGraph(wf.nodes, wf.edges);
        setNodes(g.nodes);
        setEdges(g.edges);
        setSavedWorkflowId(wf.id);
        setConfigName(wf.name);
        setConfigPrompt(wf.description || "");
      })
      .catch((e) => setGenError(e instanceof Error ? e.message : "Failed to load workflow"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialId]);

  const nodesRef = useRef(nodes);
  nodesRef.current = nodes;

  /* Auto-generate when a prompt is passed from the Dashboard */
  const didAutoGenerate = useRef(false);
  useEffect(() => {
    if (initialPrompt && !didAutoGenerate.current) {
      didAutoGenerate.current = true;
      // Fire generation — we can't call handleGenerate directly since it's not a ref,
      // so set the prompt and simulate the same logic inline.
      (async () => {
        setGenerating(true);
        setGenError(null);
        setGenSuccess(false);
        setPrompt(initialPrompt);
        try {
          const result = await generateWorkflow(initialPrompt, true);
          const toolNameMap: Record<string, string> = {
            HTTPRequest: "HTTP Request",
            DatabaseQuery: "Database Query",
            SendEmail: "Send Email",
            WaitDelay: "Wait / Delay",
            Transform: "Transform",
            Webhook: "Webhook",
          };
          const newNodes: FlowNode[] = result.nodes.map((node: BackendNode, index: number) => {
            const rawTool = (node.tool || "").toString();
            const toolName = toolNameMap[rawTool] || rawTool || "HTTP Request";
            const nodeType = (node.type as string) || "action";
            return {
              id: node.id || `node-${Date.now()}-${index}`,
              type: "flowNode",
              position: { x: snap(80 + (index % 3) * 300), y: snap(80 + Math.floor(index / 3) * 180) },
              data: {
                name: (node.name as string) || `Node ${index + 1}`,
                tool: toolName,
                detail: (node.detail || node.expression || node.reason || `Tool: ${rawTool}`) as string,
                nodeType,
              },
            };
          });
          const newEdges: FlowEdge[] = result.edges.map((edge: BackendEdge, index: number) => ({
            id: `e-${index}`,
            source: edge.from as string,
            target: edge.to as string,
            animated: true,
            style: { stroke: "#3A3F4E", strokeWidth: 1.5 },
            label: edge.condition as string | undefined,
          }));
          setNodes(newNodes);
          setEdges(newEdges);
          setGenSuccess(true);
          setTimeout(() => setGenSuccess(false), 3000);
          if (newNodes.length > 0) {
            setSelectedNode(newNodes[0].id);
            setConfigName(newNodes[0].data.name);
            setConfigPrompt(newNodes[0].data.detail);
          }
        } catch (err) {
          setGenError(err instanceof Error ? err.message : "Failed to generate workflow");
        } finally {
          setGenerating(false);
        }
      })();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPrompt]);

  /* ── Selection + config sync ── */
  useEffect(() => {
    const handler = (e: Event) => {
      const customEvent = e as CustomEvent<{ id: string }>;
      if (customEvent.detail?.id) {
        const id = customEvent.detail.id;
        setSelectedNode(id);
        const node = nodesRef.current.find((n) => n.id === id);
        if (node) {
          setConfigName(node.data.name);
          setConfigPrompt(node.data.detail);
        }
      }
    };
    window.addEventListener("flow:selectNode", handler);
    return () => window.removeEventListener("flow:selectNode", handler);
  }, []);

  const removeNode = useCallback((id: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== id));
    setEdges((prev) => prev.filter((e) => e.source !== id && e.target !== id));
    if (selectedNode === id) setSelectedNode(null);
  }, [selectedNode, setNodes, setEdges]);

  useEffect(() => {
    const handler = (e: Event) => {
      const customEvent = e as CustomEvent<{ id: string }>;
      if (customEvent.detail?.id) removeNode(customEvent.detail.id);
    };
    window.addEventListener("flow:deleteNode", handler);
    return () => window.removeEventListener("flow:deleteNode", handler);
  }, [removeNode]);

  useEffect(() => {
    const handler = (e: Event) => {
      const customEvent = e as CustomEvent<{ id: string }>;
      if (customEvent.detail?.id) setEdges((prev) => prev.filter((ed) => ed.id !== customEvent.detail.id));
    };
    window.addEventListener("flow:deleteEdge", handler);
    return () => window.removeEventListener("flow:deleteEdge", handler);
  }, [setEdges]);

  const addNode = useCallback(() => {
    const id = `node-${Date.now()}`;
    const tool = tools[Math.floor(Math.random() * tools.length)];
    const newNode: FlowNode = {
      id,
      type: "flowNode",
      position: { x: snap(100 + Math.random() * 200), y: snap(100 + Math.random() * 200) },
      data: { name: "New Node", tool: tool.name, detail: "Configure me…", nodeType: "action" },
    };
    setNodes((prev: FlowNode[]) => [...prev, newNode]);
    setSelectedNode(id);
  }, [setNodes]);

  const onConnect: OnConnect = useCallback(
    (connection) => {
      setEdges((prev) =>
        addEdge(
          {
            ...connection,
            animated: true,
            style: { stroke: "#3A3F4E", strokeWidth: 1.5 },
          },
          prev
        )
      );
    },
    [setEdges]
  );

  const handleConfigSave = useCallback(() => {
    setNodes((prev) =>
      prev.map((n) =>
        n.id === selectedNode
          ? { ...n, data: { ...(n.data as FlowNodeData), name: configName, detail: configPrompt } }
          : n
      )
    );
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }, [selectedNode, configName, configPrompt, setNodes]);

  const handleNodeClick = useCallback((_: React.MouseEvent, node: FlowNode) => {
    setSelectedNode(node.id);
    window.dispatchEvent(new CustomEvent("flow:selectNode", { detail: { id: node.id } }));
  }, []);

  /* ── AI generation ── */
  const handleGenerate = async () => {
    if (!prompt.trim() || generating) return;

    setGenerating(true);
    setGenError(null);
    setGenSuccess(false);

    try {
      const result = await generateWorkflow(prompt.trim(), true);

      // Map backend nodes → React Flow nodes
      const toolNameMap: Record<string, string> = {
        HTTPRequest: "HTTP Request",
        DatabaseQuery: "Database Query",
        SendEmail: "Send Email",
        WaitDelay: "Wait / Delay",
        Transform: "Transform",
        Webhook: "Webhook",
      };

      const newNodes: FlowNode[] = result.nodes.map((node: BackendNode, index: number) => {
        const rawTool = (node.tool || "").toString();
        const toolName = toolNameMap[rawTool] || rawTool || "HTTP Request";
        const nodeType = (node.type as string) || "action";

        return {
          id: node.id || `node-${Date.now()}-${index}`,
          type: "flowNode",
          position: { x: snap(80 + (index % 3) * 300), y: snap(80 + Math.floor(index / 3) * 180) },
          data: {
            name: (node.name as string) || `Node ${index + 1}`,
            tool: toolName,
            detail: (node.detail || node.expression || node.reason || `Tool: ${rawTool}`) as string,
            nodeType,
          },
        };
      });

      // Map backend edges → React Flow edges
      const newEdges: FlowEdge[] = result.edges.map((edge: BackendEdge, index: number) => ({
        id: `e-${index}`,
        source: edge.from as string,
        target: edge.to as string,
        animated: true,
        style: { stroke: "#3A3F4E", strokeWidth: 1.5 },
        label: edge.condition as string | undefined,
      }));

      setNodes(newNodes);
      setEdges(newEdges);
      setPrompt("");

      setGenSuccess(true);
      setTimeout(() => setGenSuccess(false), 3000);

      if (newNodes.length > 0) {
        setSelectedNode(newNodes[0].id);
        setConfigName(newNodes[0].data.name);
        setConfigPrompt(newNodes[0].data.detail);
      }
    } catch (err) {
      setGenError(err instanceof Error ? err.message : "Failed to generate workflow");
    } finally {
      setGenerating(false);
    }
  };

  /* ── Save workflow (direct graph persistence) ── */
  const handleSave = useCallback(async () => {
    setSaved(false);
    try {
      const workflowName = configName || "Untitled Workflow";
      const g = toBackendGraph(nodes, edges);
      const result = await saveWorkflowDirect({
        name: workflowName,
        description: configPrompt,
        nodes: g.nodes,
        edges: g.edges,
        workflowId: savedWorkflowId || undefined,
      });
      setSavedWorkflowId(result.id || null);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // Save failed silently
    }
  }, [nodes, edges, configName, configPrompt, savedWorkflowId]);

  /* ── Run workflow (auto-saves then executes) ── */
  /* ── Live run: highlight nodes as the backend reports them ── */
  const closeStreamRef = useRef<(() => void) | null>(null);
  const playbackRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopLive = useCallback(() => {
    closeStreamRef.current?.();
    closeStreamRef.current = null;
    if (playbackRef.current) clearInterval(playbackRef.current);
    playbackRef.current = null;
  }, []);
  useEffect(() => stopLive, [stopLive]);

  const setRunStatus = useCallback(
    (nodeId: string | null, status: FlowNodeData["runStatus"]) =>
      setNodes((ns) =>
        ns.map((n) =>
          nodeId === null || n.id === nodeId ? { ...n, data: { ...(n.data as FlowNodeData), runStatus: status } } : n
        )
      ),
    [setNodes]
  );

  const followRun = useCallback(
    (runId: string) => {
      // Events are queued and shown ~350ms apart so fast runs are still visible.
      const queue: { id: string; status: FlowNodeData["runStatus"] }[] = [];
      const seen = new Set<string>();
      let finished = false;
      const TERMINAL = ["completed", "failed", "cancelled", "waiting_approval"];
      const STEP_TO_NODE: Record<string, FlowNodeData["runStatus"]> = {
        completed: "completed", failed: "failed", waiting_approval: "waiting", skipped: "skipped",
      };

      const pushStep = (s: RunStep) => {
        if (seen.has(s.id)) return;
        seen.add(s.id);
        queue.push({ id: s.node_id, status: "running" });
        queue.push({ id: s.node_id, status: STEP_TO_NODE[s.status] ?? "completed" });
      };
      const finalize = async () => {
        stopLive();
        try {
          const run = await getRun(runId);
          setRunResult({ execution_id: run.id, status: run.status, steps: run.steps } as typeof runResult);
        } catch (e) {
          setRunError(e instanceof Error ? e.message : "Failed to load run result");
        } finally {
          setRunning(false);
        }
      };

      closeStreamRef.current = openRunStream(runId, {
        onSnapshot: (run) => {
          run.steps.forEach(pushStep);
          if (TERMINAL.includes(run.status)) finished = true;
        },
        onStep: pushStep,
        onStatus: (status, nodeId) => {
          if (status === "running" && nodeId && queue[queue.length - 1]?.id !== nodeId) {
            queue.push({ id: nodeId, status: "running" });
          }
          if (TERMINAL.includes(status)) finished = true;
        },
        onDone: () => { finished = true; },
        onError: () => { finished = true; },
      });

      playbackRef.current = setInterval(() => {
        const ev = queue.shift();
        if (ev) setRunStatus(ev.id, ev.status);
        else if (finished) finalize();
      }, 350);
    },
    [setRunStatus, stopLive]
  );

  const handleRun = useCallback(async () => {
    setRunError(null);
    setRunResult(null);
    let workflowId = savedWorkflowId;

    // Auto-persist the graph before running
    if (!workflowId) {
      try {
        const workflowName = configName || "Untitled Workflow";
        const g = toBackendGraph(nodes, edges);
        const result = await saveWorkflowDirect({
          name: workflowName,
          description: configPrompt,
          nodes: g.nodes,
          edges: g.edges,
        });
        workflowId = result.id || null;
        setSavedWorkflowId(workflowId);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } catch (e) {
        setRunError(e instanceof Error ? e.message : "Failed to save before run");
        return;
      }
    }

    if (!workflowId) {
      setRunError("Could not persist workflow — save it manually first");
      return;
    }

    setRunning(true);
    stopLive();
    setRunStatus(null, undefined);
    try {
      const { id: runId } = await startWorkflowRun(workflowId);
      followRun(runId);
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Failed to run workflow");
      setRunning(false);
    }
  }, [savedWorkflowId, configName, configPrompt, nodes, edges, followRun, setRunStatus, stopLive]);

  /* ──────────────────────────────────────────────
     Render
     ────────────────────────────────────────────── */

  const selectedData = selectedNode ? (nodes.find((n) => n.id === selectedNode)?.data as FlowNodeData) : undefined;

  return (
    <div className="flex h-screen overflow-hidden bg-base">
      {/* ── LEFT TOOLS PANEL ── */}
      <aside className="w-[200px] shrink-0 border-r border-border flex flex-col">
        <div className="p-3 border-b border-border">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-lg bg-signal/10 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-signal" />
            </div>
            <span className="text-xs font-semibold text-text tracking-wide uppercase">Tools</span>
          </div>
          <p className="text-[10px] text-text-muted leading-relaxed">Click a tool to add it to the canvas</p>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
          {tools.map((tool) => (
            <button
              key={tool.name}
              onClick={() => {
                const id = `node-${Date.now()}`;
                const pos = reactFlowInstance.screenToFlowPosition({ x: 300, y: 100 });
                const newNode: FlowNode = {
                  id,
                  type: "flowNode",
                  position: { x: snap(pos.x), y: snap(pos.y) },
                  data: { name: tool.name, tool: tool.name, detail: "Configure me…", nodeType: "action" },
                };
                setNodes((prev: FlowNode[]) => [...prev, newNode]);
              }}
              className="w-full text-left p-2.5 rounded-lg border border-border bg-surface hover:bg-surface/80 hover:border-text-muted/30 transition-all group"
            >
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded flex items-center justify-center shrink-0 bg-base border border-border group-hover:border-text-muted/20 transition-colors">
                  <span className="text-[8px] font-bold font-mono text-text-muted">
                    {tool.name.split(" ").map((w: string) => w[0]).join("").slice(0, 2)}
                  </span>
                </div>
                <div className="min-w-0">
                  <div className="text-[11px] font-medium text-text truncate">{tool.name}</div>
                  <div className="text-[9px] text-text-muted capitalize">{tool.category}</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="p-2 border-t border-border">
          <button
            onClick={addNode}
            className="w-full h-8 flex items-center justify-center gap-1.5 bg-surface border border-border rounded-lg text-[11px] text-text-muted hover:text-text hover:border-text-muted/40 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            Add Node
          </button>
        </div>
      </aside>

      {/* ── MAIN CANVAS AREA ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-12 shrink-0 border-b border-border flex items-center px-4 justify-between">
          <nav className="flex items-center gap-2 text-xs">
            <span className="text-text-muted">Dashboard</span>
            <ChevronRight className="w-3 h-3 text-text-muted/50" />
            <span className="text-text-muted">Workflows</span>
            <ChevronRight className="w-3 h-3 text-text-muted/50" />
            <span className="text-text-muted">New Workflow</span>
            <ChevronRight className="w-3 h-3 text-text-muted/50" />
            <span className="text-text font-medium">{configName || "Untitled Workflow"}</span>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-medium bg-signal/10 text-signal border border-signal/20">Draft</span>
          </nav>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRun}
              disabled={running || nodes.length === 0}
              className="h-8 px-3 rounded-lg bg-success/15 text-success text-xs font-medium hover:bg-success/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 border border-success/20"
            >
              {running ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Running…
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" />
                  Run
                </>
              )}
            </button>
            <button className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-text hover:border-text-muted/40 transition-all flex items-center gap-1.5">
              <XIcon className="w-3.5 h-3.5" />
              Cancel
            </button>
            <button onClick={handleSave} className="h-8 px-3 rounded-lg bg-text text-base text-xs font-medium hover:bg-text/90 transition-all flex items-center gap-1.5">
              <Save className="w-3.5 h-3.5" />
              {saved ? "Saved!" : "Save"}
            </button>
            <button
              onClick={() => setHistoryOpen(true)}
              className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-text hover:border-text-muted/40 transition-all flex items-center gap-1.5"
            >
              <History className="w-3.5 h-3.5" />
              History
            </button>
            <button
              onClick={() => setSuggestionsOpen(true)}
              disabled={!savedWorkflowId}
              title={savedWorkflowId ? "Get suggestions" : "Save workflow first"}
              className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-accent hover:border-accent/40 transition-all flex items-center gap-1.5 disabled:opacity-30 disabled:pointer-events-none"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Suggestions
            </button>
            <button
              onClick={() => setEvolveOpen(true)}
              disabled={!savedWorkflowId}
              title={savedWorkflowId ? "Test mutated variants" : "Save workflow first"}
              className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-accent hover:border-accent/40 transition-all flex items-center gap-1.5 disabled:opacity-30 disabled:pointer-events-none"
            >
              <Dna className="w-3.5 h-3.5" />
              Evolve
            </button>
            <button
              onClick={() => setTriggersOpen(true)}
              disabled={!savedWorkflowId}
              title={savedWorkflowId ? "Schedules and webhooks" : "Save workflow first"}
              className="h-8 px-3 rounded-lg border border-border text-xs text-text-muted hover:text-accent hover:border-accent/40 transition-all flex items-center gap-1.5 disabled:opacity-30 disabled:pointer-events-none"
            >
              <Zap className="w-3.5 h-3.5" />
              Triggers
            </button>
          </div>
        </header>

        {/* React Flow Canvas */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={handleNodeClick}
            nodeTypes={flowNodeTypes}
            edgeTypes={{ smoothstep: LabeledEdgeMemo }}
            fitView
            snapToGrid
            snapGrid={[GRID, GRID]}
            defaultEdgeOptions={{
              type: "smoothstep",
              style: { stroke: "#3A3F4E", strokeWidth: 1.5 },
              deletable: true,
              selectable: true,
            }}
          >
            <Background variant={BackgroundVariant.Dots} gap={GRID} size={1} color="#1E2130" />
            <Panel position="bottom-left">
              <div className="flex flex-col gap-1 p-1.5 bg-surface/95 backdrop-blur-md border border-border rounded-lg shadow-lg">
                <button
                  onClick={() => reactFlowInstance.zoomIn()}
                  className="w-8 h-8 flex items-center justify-center rounded-md text-text-muted hover:text-text hover:bg-surface-2 transition-all"
                  title="Zoom in"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => reactFlowInstance.zoomOut()}
                  className="w-8 h-8 flex items-center justify-center rounded-md text-text-muted hover:text-text hover:bg-surface-2 transition-all"
                  title="Zoom out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <button
                  onClick={() => reactFlowInstance.fitView({ padding: 0.2 })}
                  className="w-8 h-8 flex items-center justify-center rounded-md text-text-muted hover:text-text hover:bg-surface-2 transition-all"
                  title="Fit view"
                >
                  <Maximize className="w-4 h-4" />
                </button>
              </div>
            </Panel>
            <Panel position="top-center">
              <button
                onClick={addNode}
                className="h-8 px-3 bg-surface border border-border rounded-lg text-xs text-text-muted hover:text-text hover:border-text-muted/40 hover:bg-surface/80 transition-all flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                Add Node
              </button>
            </Panel>
          </ReactFlow>

          {/* ── EXECUTION RESULTS ── */}
          {(runResult || runError) && (
            <div className="absolute bottom-4 left-4 right-4 max-h-72 bg-surface/95 backdrop-blur-md border border-border rounded-xl shadow-2xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-border">
                <div className="flex items-center gap-2">
                  <Terminal className="w-3.5 h-3.5 text-text-muted" />
                  <span className="text-xs font-medium text-text">
                    Execution Result
                    <span className={`ml-2 px-1.5 py-0.5 text-[9px] font-medium rounded-full border ${
                      runResult?.status === "completed" ? "bg-success/10 text-success border-success/20" :
                      runResult?.status === "failed" ? "bg-warn/10 text-warn border-warn/20" :
                      "bg-accent/10 text-accent border-accent/20"
                    }`}>
                      {runResult?.status || "error"}
                    </span>
                  </span>
                </div>
                <button
                  onClick={() => { setRunResult(null); setRunError(null); }}
                  className="p-1 text-text-muted hover:text-text rounded-md"
                >
                  <XIcon className="w-3 h-3" />
                </button>
              </div>
              {runError && (
                <div className="px-4 py-2.5 text-xs text-warn bg-warn/5 border-b border-warn/10">
                  {runError}
                </div>
              )}
              {runResult && runResult.steps.length > 0 && (
                <div className="p-3 overflow-auto max-h-52">
                  <div className="space-y-1">
                    {runResult.steps.map((step, i) => (
                      <div
                        key={step.id}
                        className={`flex items-center gap-2 px-2.5 py-2 rounded-md text-xs ${
                          step.status === "completed" ? "bg-success/5 border-l-2 border-success/30" :
                          step.status === "failed" ? "bg-warn/5 border-l-2 border-warn/30" :
                          "bg-surface-2 border-l-2 border-border"
                        }`}
                      >
                        <span className="text-text-muted/50 font-mono text-[10px] w-5 shrink-0">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <span className="text-text font-medium truncate flex-1">{step.node_name}</span>
                        {step.tool_name && (
                          <span className="text-text-muted/60 font-mono text-[10px]">{step.tool_name}</span>
                        )}
                        <span className={`shrink-0 px-1.5 py-0.5 text-[9px] font-medium rounded ${
                          step.status === "completed" ? "bg-success/10 text-success" :
                          step.status === "failed" ? "bg-warn/10 text-warn" :
                          "bg-accent/10 text-accent"
                        }`}>
                          {step.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {runResult && (
                <div className="px-4 py-2 border-t border-border flex items-center gap-3">
                  <span className="text-[10px] text-text-muted">
                    {runResult.steps.filter((s) => s.status === "completed").length}/{runResult.steps.length} steps completed
                  </span>
                  <span className="text-[10px] text-text-muted/40">
                    execution: {runResult.execution_id?.slice(0, 8)}
                  </span>
                  <Link
                    href={`/console?run=${runResult.execution_id}`}
                    className="ml-auto text-[10px] text-accent hover:underline flex items-center gap-1"
                  >
                    <Terminal className="w-3 h-3" />
                    Open Console
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* ── RIGHT CONFIG PANEL ── */}
          <div className="absolute top-4 right-4 w-72 bg-surface/95 backdrop-blur-md border border-border rounded-xl shadow-2xl overflow-hidden">
            {selectedData ? (
              <>
                <div className="p-4 border-b border-border">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-text-muted" />
                      <span className="text-xs font-medium text-text">Node Configuration</span>
                    </div>
                    {saved && (
                      <span className="flex items-center gap-1 text-[10px] text-success">
                        <CheckCircle2 className="w-3 h-3" />
                        Saved
                      </span>
                    )}
                  </div>
                </div>
                <div className="p-4 space-y-3">
                  <div>
                    <label className="block text-[10px] font-medium text-text-muted uppercase tracking-wider mb-1.5">
                      Node Name
                    </label>
                    <input
                      value={configName}
                      onChange={(e) => setConfigName(e.target.value)}
                      className="w-full h-8 px-2.5 bg-base border border-border rounded-lg text-xs text-text placeholder:text-text-muted/40 focus:outline-none focus:border-text-muted/40 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-medium text-text-muted uppercase tracking-wider mb-1.5">
                      Configuration Prompt
                    </label>
                    <textarea
                      value={configPrompt}
                      onChange={(e) => setConfigPrompt(e.target.value)}
                      rows={4}
                      className="w-full px-2.5 py-2 bg-base border border-border rounded-lg text-xs text-text placeholder:text-text-muted/40 focus:outline-none focus:border-text-muted/40 transition-colors resize-none font-mono"
                    />
                  </div>
                  <button
                    onClick={handleConfigSave}
                    className="w-full h-8 bg-surface border border-border rounded-lg text-xs text-text hover:border-text-muted/40 hover:bg-surface/80 transition-all flex items-center justify-center gap-1.5"
                  >
                    <Save className="w-3 h-3" />
                    Update Node
                  </button>
                </div>
              </>
            ) : (
              <div className="p-6 text-center">
                <div className="w-10 h-10 mx-auto mb-3 rounded-lg bg-base border border-border flex items-center justify-center">
                  <MessageSquare className="w-4 h-4 text-text-muted/40" />
                </div>
                <p className="text-[11px] text-text-muted leading-relaxed">
                  Select a node on the canvas to configure its properties
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ── BOTTOM PROMPT BAR ── */}
        <div className="h-28 shrink-0 border-t border-border bg-surface/50 backdrop-blur-sm p-3">
          <div className="flex items-center gap-3 h-full">
            <div className="flex-1 flex flex-col">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-signal" />
                  <span className="text-[10px] font-medium text-text-muted uppercase tracking-wider">
                    AI Workflow Prompt
                  </span>
                </div>
                <span className="text-[10px] text-text-muted/60">
                  Describe the workflow you want to build
                </span>
              </div>
              <div className="flex gap-2 flex-1">
                <div className="flex-1 relative">
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g., Send email notification when a new customer signs up, fetch their data from the API, and store it in the database..."
                    rows={3}
                    className="w-full h-full px-3 py-2 bg-base border border-border rounded-lg text-xs text-text placeholder:text-text-muted/30 focus:outline-none focus:border-text-muted/40 focus:ring-1 focus:ring-text-muted/10 transition-all resize-none font-mono"
                  />
                </div>
                <div className="flex flex-col justify-end gap-1.5">
                  <button
                    onClick={handleGenerate}
                    disabled={generating || !prompt.trim()}
                    className="h-10 px-4 bg-signal text-white rounded-lg text-xs font-medium hover:bg-signal/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-1.5 whitespace-nowrap"
                  >
                    {generating ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        Generating…
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3.5 h-3.5" />
                        Generate Workflow
                      </>
                    )}
                  </button>
                </div>
              </div>
              {genError && (
                <div className="flex items-center gap-1.5 mt-1.5">
                  <AlertCircle className="w-3 h-3 text-signal" />
                  <span className="text-[10px] text-signal">{genError}</span>
                </div>
              )}
              {genSuccess && (
                <div className="flex items-center gap-1.5 mt-1.5">
                  <CheckCircle2 className="w-3 h-3 text-success" />
                  <span className="text-[10px] text-success">Workflow generated! Click nodes to configure.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Version History Panel ── */}
      {savedWorkflowId && (
        <VersionHistoryPanel
          workflowId={savedWorkflowId}
          workflowName={configName || "Untitled Workflow"}
          isOpen={historyOpen}
          onClose={() => setHistoryOpen(false)}
          onLoadVersion={handleLoadVersion}
        />
      )}

      {/* ── Suggestions Panel ── */}
      {savedWorkflowId && (
        <SuggestionsPanel
          workflowId={savedWorkflowId}
          workflowName={configName || "Untitled Workflow"}
          isOpen={suggestionsOpen}
          onClose={() => setSuggestionsOpen(false)}
          onApplySuggestion={handleLoadVersion}
        />
      )}

      {/* Triggers Panel */}
      {savedWorkflowId && (
        <TriggersPanel
          workflowId={savedWorkflowId}
          workflowName={configName || "Untitled Workflow"}
          isOpen={triggersOpen}
          onClose={() => setTriggersOpen(false)}
        />
      )}

      {/* Evolve Panel */}
      {savedWorkflowId && (
        <EvolvePanel
          workflowId={savedWorkflowId}
          workflowName={configName || "Untitled Workflow"}
          isOpen={evolveOpen}
          onClose={() => setEvolveOpen(false)}
          onLoadVariant={(n, e) => { setEvolveOpen(false); handleLoadVersion(n, e); }}
        />
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────
   Wrapper with Provider + Suspense
   ────────────────────────────────────────────── */
export default function BuilderClient({ initialPrompt = "", initialName = "" }: { initialPrompt?: string; initialName?: string }) {
  const searchParams = useSearchParams();
  const promptFromUrl = searchParams.get("prompt") || "";
  const nameFromUrl = searchParams.get("name") || "";
  const effectivePrompt = promptFromUrl || initialPrompt;
  const effectiveName = nameFromUrl || initialName;

  return (
    <ReactFlowProvider>
      <BuilderInner initialPrompt={effectivePrompt} initialName={effectiveName} initialId={searchParams.get("id") || ""} />
    </ReactFlowProvider>
  );
}
