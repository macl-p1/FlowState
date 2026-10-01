export interface BackendNode {
  id: string;
  type: string;
  name: string;
  tool?: string;
  detail?: string;
  expression?: string;
  reason?: string;
  duration_seconds?: number;
  outcome?: string;
  trigger?: { type: string; schedule?: string };
  [key: string]: unknown;
}

export interface BackendEdge {
  from: string;
  to: string;
  condition?: string;
}

export interface GenerateResponse {
  preview?: boolean;
  name: string;
  description: string;
  nodes: BackendNode[];
  edges: BackendEdge[];
  metadata?: Record<string, unknown>;
  id?: string;
}

// ── Workflows ────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

function authHeaders(): Record<string, string> {
  return API_KEY ? { "X-API-Key": API_KEY } : {};
}

/** fetch that automatically injects the API key header when configured. */
async function fetchWithAuth(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const headers = { ...authHeaders(), ...(init.headers as Record<string, string> | undefined) };
  return fetch(input, { ...init, headers });
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export interface WorkflowListItem {
  id: string;
  name: string;
  description: string;
  status?: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface WorkflowDetail extends WorkflowListItem {
  nodes: BackendNode[];
  edges: BackendEdge[];
}

export async function listWorkflows(): Promise<WorkflowListItem[]> {
  const res = await fetchWithAuth(`${API_BASE}/workflows`);
  return handleResponse(res);
}

export async function getWorkflow(id: string): Promise<WorkflowDetail> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(id)}`);
  return handleResponse(res);
}

export async function deleteWorkflow(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(id)}`, { method: "DELETE" });
  handleResponse(res);
}

export async function generateWorkflow(prompt: string, preview = true): Promise<GenerateResponse> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, preview }),
  });
  return handleResponse(res);
}

export async function saveWorkflowFromBuilder(nodes: BackendNode[], edges: BackendEdge[], name?: string): Promise<GenerateResponse> {
  // Build a prompt from the current canvas state so the backend can persist it
  const workflowName = name || "Untitled Workflow";
  const nodeDescriptions = nodes.map(
    (n) => `- ${n.type}: ${n.name}${n.tool ? ` (tool: ${n.tool})` : ""}`
  ).join("\n");
  const prompt = `Create a workflow called "${workflowName}" with these steps:\n${nodeDescriptions}`;

  const res = await fetchWithAuth(`${API_BASE}/workflows/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, preview: false }),
  });
  return handleResponse(res);
}

const DISPLAY_TO_TOOL: Record<string, string> = {
  "HTTP Request": "http",
  "Database Query": "database",
  "Send Email": "send_email",
  "Webhook": "webhook",
  "Wait / Delay": "delay",
  "Transform": "transform",
};

/** Map builder display names → registry tool names so execution works */
export function resolveToolName(raw: string | undefined): string | undefined {
  if (!raw) return undefined;
  return DISPLAY_TO_TOOL[raw] ?? raw.toLowerCase().replace(/\s+/g, "_");
}

export async function saveWorkflowDirect(data: {
  name: string;
  description?: string;
  nodes: BackendNode[];
  edges: BackendEdge[];
  workflowId?: string;
}): Promise<GenerateResponse> {
  // Translate display tool names to internal registry names
  const normalizedNodes = data.nodes.map((n) => ({
    ...n,
    tool: resolveToolName((n as BackendNode & { tool?: string }).tool),
  }));
  const body: Record<string, unknown> = {
    name: data.name,
    description: data.description || "",
    nodes: normalizedNodes,
    edges: data.edges,
  };
  if (data.workflowId) {
    body.workflow_id = data.workflowId;
  }
  const res = await fetchWithAuth(`${API_BASE}/workflows`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function saveWorkflow(data: {
  name: string;
  description?: string;
  nodes: BackendNode[];
  edges: BackendEdge[];
}): Promise<GenerateResponse> {
  // Build a natural-language prompt from the canvas so the planner can re-construct it
  const nodeSteps = data.nodes
    .map(
      (n) =>
        `- Step "${n.name}": ${n.type} node${
          n.tool ? ` using tool "${n.tool}"` : ""
        }${n.detail ? ` — ${n.detail}` : ""}`
    )
    .join("\n");
  const connections = data.edges
    .map((e) => `  "${e.from}" -> "${e.to}"${e.condition ? ` [${e.condition}]` : ""}`)
    .join("\n");
  const prompt =
    data.description && data.description.trim()
      ? `${data.description}\n\nSteps:\n${nodeSteps}\n\nFlow connections:\n${connections}`
      : `Create a workflow called "${data.name}" with these steps:\n${nodeSteps}\n\nFlow connections:\n${connections}`;

  const res = await fetchWithAuth(`${API_BASE}/workflows/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, preview: false }),
  });
  return handleResponse(res);
}

export async function runWorkflow(id: string, context?: Record<string, unknown>): Promise<unknown> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(id)}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context: context || {} }),
  });
  return handleResponse(res);
}

// ── Runs / Executions ────────────────────────

export interface RunListItem {
  source?: string;
  replay_of?: string | null;
  id: string;
  workflow_id: string;
  workflow_name: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface RunDetail {
  id: string;
  workflow_id: string;
  workflow_name: string;
  status: string;
  current_node_id: string | null;
  context: Record<string, unknown>;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  steps: RunStep[];
  approval: { id: string; reason: string; context: Record<string, unknown>; status: string } | null;
  quality?: RunQuality | null;
  source?: string;
  replay_of?: string | null;
}

export interface RunQuality {
  score: number;
  verdict: "ok" | "suspect" | "bad";
  reasons: string[];
  source: string;
}

export interface WorkflowQuality {
  runs: number;
  corrected: number;
  override_rate: number;
  avg_score: number | null;
  top_reasons: string[];
  insight: string | null;
}

export interface RunStep {
  id: string;
  node_id: string;
  node_name: string;
  node_type: string;
  status: string;
  tool_name: string | null;
  tool_inputs: Record<string, unknown> | null;
  tool_result: Record<string, unknown> | null;
  attempt_count: number;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export async function listRuns(limit = 50): Promise<RunListItem[]> {
  const res = await fetchWithAuth(`${API_BASE}/runs?limit=${limit}`);
  return handleResponse(res);
}

export async function getRun(id: string): Promise<RunDetail> {
  const res = await fetchWithAuth(`${API_BASE}/runs/${encodeURIComponent(id)}`);
  return handleResponse(res);
}

export async function cancelRun(id: string): Promise<{ id: string; status: string }> {
  const res = await fetchWithAuth(`${API_BASE}/runs/${encodeURIComponent(id)}/cancel`, { method: "POST" });
  return handleResponse(res);
}

// ── Approvals ────────────────────────────────

export interface ApprovalItem {
  id: string;
  execution_id: string;
  node_id: string;
  reason: string;
  context: Record<string, unknown>;
  approver_role: string | null;
  status: string;
  created_at: string;
}

export async function listApprovals(): Promise<ApprovalItem[]> {
  const res = await fetchWithAuth(`${API_BASE}/approvals`);
  return handleResponse(res);
}

export async function approveApproval(id: string, approverId: string): Promise<unknown> {
  const res = await fetchWithAuth(`${API_BASE}/approvals/${encodeURIComponent(id)}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approver_id: approverId }),
  });
  return handleResponse(res);
}

export async function rejectApproval(id: string, approverId: string, reason?: string): Promise<unknown> {
  const res = await fetchWithAuth(`${API_BASE}/approvals/${encodeURIComponent(id)}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approver_id: approverId, reason: reason || "" }),
  });
  return handleResponse(res);
}

// ── Custom Tools (unchanged) ─────────────────

export interface CustomTool {
  id: string;
  name: string;
  description: string;
  tool_type: string;
  status: string;
  input_schema: Record<string, unknown>;
  config: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  integration_config: Record<string, unknown> | null;
  last_test_result: Record<string, unknown> | null;
  verified_at: string | null;
  verified_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface ToolCategory {
  type: string;
  label: string;
  icon: string;
  description: string;
  count: number;
}

export async function getToolCategories(): Promise<ToolCategory[]> {
  const res = await fetchWithAuth(`${API_BASE}/tools/categories`);
  return handleResponse(res);
}

export async function getCustomTools(type?: string): Promise<CustomTool[]> {
  const res = await fetchWithAuth(`${API_BASE}/tools/all`);
  const all = await handleResponse<CustomTool[]>(res);
  if (type && type !== "all") {
    return all.filter((t) => t.tool_type === type);
  }
  return all;
}

export async function createCustomTool(data: {
  name: string;
  description: string;
  tool_type?: string;
  input_schema?: Record<string, unknown>;
  config?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
}): Promise<CustomTool> {
  const res = await fetchWithAuth(`${API_BASE}/tools/custom`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function updateCustomTool(id: string, data: Record<string, unknown>): Promise<CustomTool> {
  const res = await fetchWithAuth(`${API_BASE}/tools/custom/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function deleteCustomTool(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}/tools/custom/${encodeURIComponent(id)}`, { method: "DELETE" });
  handleResponse(res);
}

export interface VerifyToolResponse {
  success: boolean;
  message: string;
}

export async function verifyCustomTool(id: string, testInputs: Record<string, unknown> = {}): Promise<VerifyToolResponse> {
  const res = await fetchWithAuth(`${API_BASE}/tools/custom/${encodeURIComponent(id)}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ test_inputs: testInputs }),
  });
  return handleResponse(res);
}

export async function registerCustomTool(id: string): Promise<{ message: string; registered: boolean }> {
  const res = await fetchWithAuth(`${API_BASE}/tools/custom/${encodeURIComponent(id)}/register`, { method: "POST" });
  return handleResponse(res);
}

// ── Integrations ────────────────────────────

export interface IntegrationListItem {
  id: string;
  name: string;
  tool_type: string;
  status: string;
  integration_config: Record<string, unknown>;
  verified_at: string | null;
  last_test_result: Record<string, unknown> | null;
}

export interface IntegrationTestResponse {
  success: boolean;
  output: Record<string, unknown> | null;
  error: string | null;
  message: string;
  elapsed_seconds: number;
}

export async function listIntegrations(): Promise<IntegrationListItem[]> {
  const res = await fetchWithAuth(`${API_BASE}/integrations`);
  return handleResponse(res);
}

export async function getIntegration(toolId: string): Promise<CustomTool> {
  const res = await fetchWithAuth(`${API_BASE}/integrations/${encodeURIComponent(toolId)}`);
  return handleResponse(res);
}

export async function setIntegrationConfig(
  toolId: string,
  integrationConfig: Record<string, unknown> | null,
): Promise<CustomTool> {
  const res = await fetchWithAuth(`${API_BASE}/integrations/${encodeURIComponent(toolId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ integration_config: integrationConfig }),
  });
  return handleResponse(res);
}

export async function removeIntegrationConfig(toolId: string): Promise<{ deleted: boolean; tool_id: string }> {
  const res = await fetchWithAuth(`${API_BASE}/integrations/${encodeURIComponent(toolId)}`, { method: "DELETE" });
  return handleResponse(res);
}

// ── Genealogy ──────────────────────────────

export interface VersionInfo {
  id: string;
  workflow_id: string;
  parent_version_id: string | null;
  version_number: number;
  nodes: BackendNode[];
  edges: BackendEdge[];
  change_rationale: string | null;
  change_summary: string | null;
  diff_details: Record<string, unknown> | null;
  created_at: string | null;
}

export interface BranchInfo {
  branch_id: string;
  target_workflow_id: string;
  target_name: string;
  branch_name: string | null;
  rationale: string | null;
  at_version: string | null;
  created_at: string | null;
}

export interface LineageResponse {
  workflow_id: string;
  workflow_name: string;
  current_version: number;
  versions: VersionInfo[];
  branches: BranchInfo[];
  ancestry: Array<{
    workflow_id: string;
    workflow_name: string;
    branched_at_version: string | null;
    branch_rationale: string | null;
    created_at: string | null;
  }>;
}

export interface SaveVersionResponse {
  version_id: string;
  workflow_id: string;
  version_number: number;
  change_summary: string | null;
  created_at: string | null;
}

export interface BranchWorkflowResponse {
  new_workflow_id: string;
  new_workflow_name: string;
  branch_id: string;
  version_id: string;
  version_number: number;
  created_at: string | null;
}

export async function saveWorkflowVersion(
  workflowId: string,
  data: { rationale?: string; nodes?: BackendNode[]; edges?: BackendEdge[] }
): Promise<SaveVersionResponse> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function branchWorkflow(
  workflowId: string,
  data: { name: string; rationale?: string; nodes?: BackendNode[]; edges?: BackendEdge[]; branch_name?: string }
): Promise<BranchWorkflowResponse> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/branch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function getWorkflowHistory(workflowId: string): Promise<{ workflow_id: string; versions: VersionInfo[] }> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/history`);
  return handleResponse(res);
}

export async function getWorkflowVersion(workflowId: string, versionId: string): Promise<VersionInfo> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/versions/${encodeURIComponent(versionId)}`);
  return handleResponse(res);
}

export async function getWorkflowLineage(workflowId: string): Promise<LineageResponse> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/lineage`);
  return handleResponse(res);
}

export async function testIntegration(
  toolId: string,
  testInputs: Record<string, unknown> = {},
): Promise<IntegrationTestResponse> {
  const res = await fetchWithAuth(`${API_BASE}/integrations/${encodeURIComponent(toolId)}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ test_inputs: testInputs }),
  });
  return handleResponse(res);
}

// ── Suggestions ────────────────────────────

export interface SuggestionItem {
  id: string;
  workflow_id: string;
  source_workflow_id: string;
  source_workflow_name: string;
  similarity_score: number;
  pattern: string;
  pattern_label: string;
  description: string;
  suggestion: string;
  target_node_id: string | null;
  actionable: boolean;
  apply_patch: Record<string, unknown>;
}

export interface SuggestionsResponse {
  workflow_id: string;
  suggestions: SuggestionItem[];
}

export async function getWorkflowSuggestions(
  workflowId: string,
): Promise<SuggestionsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}/workflows/${encodeURIComponent(workflowId)}/suggestions`,
  );
  return handleResponse(res);
}

export async function applySuggestion(
  workflowId: string,
  patch: Record<string, unknown>,
): Promise<{ id: string; name: string; nodes: BackendNode[]; edges: BackendEdge[] }> {
  const res = await fetchWithAuth(
    `${API_BASE}/workflows/${encodeURIComponent(workflowId)}/suggestions/apply`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patch }),
    },
  );
  return handleResponse(res);
}

// ── Analytics & Evolution ────────────────────

export interface AnalyticsStats {
  workflows: (WorkflowQuality & { id: string; name: string })[];
  total_runs: number;
  by_status: Record<string, number>;
  failure_rate: number;
  tools: { tool: string; steps: number; failure_rate: number; avg_seconds: number | null }[];
}

export async function getAnalyticsStats(): Promise<AnalyticsStats> {
  return handleResponse(await fetchWithAuth(`${API_BASE}/analytics/stats`));
}

export interface EvolveVariant {
  description: string;
  fitness: number;
  generation: number;
  removes_approval: boolean;
  nodes: BackendNode[];
  edges: BackendEdge[];
}

export interface EvolveResult {
  baseline: number;
  variants: EvolveVariant[];
  winner: EvolveVariant | null;
  applied_version_id: string | null;
}

export async function evolveWorkflow(
  workflowId: string,
  opts: { trials?: number; generations?: number; allowGateRemoval?: boolean } = {},
): Promise<EvolveResult> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/evolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trials: opts.trials ?? 3,
      generations: opts.generations ?? 1,
      allow_gate_removal: opts.allowGateRemoval ?? false,
      apply: false,
    }),
  });
  return handleResponse(res);
}

// ── Quality (silent-success detection) ───────

export async function getRunEvaluation(runId: string): Promise<RunQuality | null> {
  return handleResponse(await fetchWithAuth(`${API_BASE}/runs/${encodeURIComponent(runId)}/evaluation`));
}

export async function flagRun(runId: string, note?: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}/runs/${encodeURIComponent(runId)}/correction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ kind: "wrong_result", note }),
  });
  await handleResponse(res);
}

export async function getWorkflowQuality(workflowId: string): Promise<WorkflowQuality> {
  return handleResponse(await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/quality`));
}

export async function deleteRun(id: string): Promise<void> {
  await handleResponse(await fetchWithAuth(`${API_BASE}/runs/${encodeURIComponent(id)}`, { method: "DELETE" }));
}

// ── Live runs ────────────────────────────────

/** Start a run in the background; resolves with the run id as soon as the run exists. */
export async function startWorkflowRun(id: string, context?: Record<string, unknown>): Promise<{ id: string }> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(id)}/run/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context: context || {} }),
  });
  return handleResponse(res);
}

export interface RunStreamHandlers {
  onSnapshot?: (run: RunDetail) => void;
  onStep?: (step: RunStep) => void;
  onStatus?: (status: string, currentNodeId: string | null, currentNodeName: string | null) => void;
  onDone?: () => void;
  onError?: () => void;
}

/** Subscribe to a run's SSE stream. Returns a function that closes it. */
export function openRunStream(runId: string, h: RunStreamHandlers): () => void {
  const url = new URL(`${API_BASE}/runs/${encodeURIComponent(runId)}/stream`);
  if (API_KEY) url.searchParams.set("api_key", API_KEY);
  const es = new EventSource(url.toString());
  es.onmessage = (evt) => {
    try {
      const m = JSON.parse(evt.data);
      if (m.type === "step") h.onStep?.(m.data);
      else if (m.type === "status") h.onStatus?.(m.data.status, m.data.current_node_id ?? null, m.data.current_node_name ?? null);
    } catch { /* ignore malformed event */ }
  };
  es.addEventListener("snapshot", (evt) => {
    try { h.onSnapshot?.(JSON.parse((evt as MessageEvent).data)); } catch { /* ignore */ }
  });
  es.addEventListener("done", () => { es.close(); h.onDone?.(); });
  es.onerror = () => { es.close(); h.onError?.(); };
  return () => es.close();
}

// ── Triggers & replay ────────────────────────

export interface TriggerItem {
  id: string;
  workflow_id: string;
  kind: "schedule" | "webhook";
  enabled: boolean;
  config: { interval_seconds?: number; cron?: string; last_error?: string };
  webhook_path: string | null;
  next_run_at: string | null;
  last_run_at: string | null;
}

/** Absolute URL external systems should POST to. */
export function webhookUrl(t: TriggerItem): string {
  return t.webhook_path ? new URL(t.webhook_path, API_BASE).toString() : "";
}

export async function listTriggers(workflowId: string): Promise<TriggerItem[]> {
  return handleResponse(await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/triggers`));
}

export async function createTrigger(
  workflowId: string,
  data: { kind: "schedule" | "webhook"; interval_seconds?: number; cron?: string },
): Promise<TriggerItem> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/${encodeURIComponent(workflowId)}/triggers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function setTriggerEnabled(id: string, enabled: boolean): Promise<TriggerItem> {
  const res = await fetchWithAuth(`${API_BASE}/triggers/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled }),
  });
  return handleResponse(res);
}

export async function deleteTrigger(id: string): Promise<void> {
  await handleResponse(await fetchWithAuth(`${API_BASE}/triggers/${encodeURIComponent(id)}`, { method: "DELETE" }));
}

/** Re-run with the same input. By default uses the workflow as it was when the run was queued. */
export async function replayRun(id: string, latest = false): Promise<{ id: string; replay_of: string }> {
  const res = await fetchWithAuth(`${API_BASE}/runs/${encodeURIComponent(id)}/replay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latest }),
  });
  return handleResponse(res);
}
