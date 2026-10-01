"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import {
  Puzzle,
  Search,
  Plus,
  ExternalLink,
  CheckCircle2,
  Clock,
  XCircle,
  Workflow,
  X,
  Play,
  Loader2,
  Trash2,
  Save,
  Globe,
  Database,
  Mail,
  Link2,
  MessageSquare,
  HardDrive,
  Lock,
  Eye,
  EyeOff,
  Key,
  Server,
  User,
  Globe2,
  Link as LinkIcon,
} from "lucide-react";
import type { CustomTool, ToolCategory } from "@/lib/api";
import {
  getToolCategories,
  getCustomTools,
  createCustomTool,
  updateCustomTool,
  deleteCustomTool,
  verifyCustomTool,
  registerCustomTool,
  setIntegrationConfig,
  removeIntegrationConfig,
  testIntegration,
} from "@/lib/api";

/* ── Icon map ── */
const TYPE_ICONS: Record<string, React.ElementType> = {
  http: Globe,
  database: Database,
  email: Mail,
  webhook: Link2,
  transform: Workflow,
  delay: Clock,
  messaging: MessageSquare,
  storage: HardDrive,
  custom: Puzzle,
  all: Puzzle,
};

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-text-muted/10 text-text-muted border-text-muted/20",
  pending_verification: "bg-accent/10 text-accent border-accent/20",
  verified: "bg-success/10 text-success border-success/20",
  rejected: "bg-warn/10 text-warn border-warn/20",
  error: "bg-warn/10 text-warn border-warn/20",
};

const STATUS_LABEL: Record<string, string> = {
  draft: "Draft",
  pending_verification: "Verifying…",
  verified: "Verified",
  rejected: "Rejected",
  error: "Failed",
};

const TOOL_TYPES = [
  { value: "http", label: "HTTP / API", icon: Globe },
  { value: "database", label: "Database", icon: Database },
  { value: "email", label: "Email", icon: Mail },
  { value: "webhook", label: "Webhook", icon: Link2 },
  { value: "transform", label: "Transform", icon: Workflow },
  { value: "delay", label: "Delay / Wait", icon: Clock },
  { value: "messaging", label: "Messaging", icon: MessageSquare },
  { value: "storage", label: "Storage", icon: HardDrive },
  { value: "custom", label: "Custom Code", icon: Puzzle },
];

const TOOL_TYPE_LABELS: Record<string, string> = Object.fromEntries(
  TOOL_TYPES.map((t) => [t.value, t.label])
);

type FormData = {
  name: string;
  description: string;
  tool_type: string;
  input_schema: Record<string, unknown>;
  config: Record<string, unknown>;
  output_schema: Record<string, unknown>;
};

/* ────────────────────────────────────────────── */

export default function ToolsPage() {
  const [categories, setCategories] = useState<ToolCategory[]>([]);
  const [tools, setTools] = useState<CustomTool[]>([]);
  const [activeCategory, setActiveCategory] = useState("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  // Modal
  const [showModal, setShowModal] = useState(false);
  const [editingTool, setEditingTool] = useState<CustomTool | null>(null);
  const [formData, setFormData] = useState<FormData>({
    name: "",
    description: "",
    tool_type: "custom",
    input_schema: { type: "object", properties: {} },
    config: {},
    output_schema: { type: "object", properties: {} },
  });
  const [configJson, setConfigJson] = useState("{}");
  const [configJsonError, setConfigJsonError] = useState<string | null>(null);

  // Integration config
  const [activeTab, setActiveTab] = useState<"definition" | "integration" | "config">("definition");
  const [integrationJson, setIntegrationJson] = useState("{}");
  const [integrationJsonError, setIntegrationJsonError] = useState<string | null>(null);
  const [testingIntegration, setTestingIntegration] = useState(false);
  const [integrationTestResult, setIntegrationTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [showSecrets, setShowSecrets] = useState(false);

  // Typed integration config form state (synced with integrationJson)
  const [icForm, setIcForm] = useState<Record<string, Record<string, string>>>({
    http: { integration_type: "http", base_url: "", auth_type: "none", api_key: "", bearer_token: "", username: "", password: "", api_key_header: "X-API-Key", timeout_seconds: "30" },
    email_smtp: { integration_type: "email_smtp", smtp_host: "", smtp_port: "587", smtp_user: "", smtp_password: "", from_address: "", use_tls: "true" },
    email_api: { integration_type: "email_api", provider: "sendgrid", api_endpoint: "", api_key: "", from_address: "" },
    database: { integration_type: "database", driver: "", connection_string: "" },
    messaging_slack: { integration_type: "messaging_slack", bot_token: "" },
    storage_s3: { integration_type: "storage_s3", access_key: "", secret_key: "", bucket: "", region: "us-east-1", endpoint_url: "" },
    webhook: { integration_type: "webhook", endpoint_url: "", http_method: "POST" },
  });

  const getIntegrationType = (): string => {
    try {
      const parsed = JSON.parse(integrationJson);
      return parsed.integration_type || "http";
    } catch {
      return "http";
    }
  };

  const syncIcFormToJson = () => {
    const itype = getIntegrationType();
    const fields = icForm[itype] || icForm.http;
    const obj: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(fields)) {
      if (k === "password" || k === "smtp_password" || k === "secret_key" || k === "bearer_token" || k === "api_key" || k === "bot_token" || k === "access_key") {
        // Preserve existing value if field is empty and we have a saved value
        const existing = (() => { try { return JSON.parse(integrationJson)[k] || ""; } catch { return ""; } })();
        obj[k] = v || existing;
      } else if (k === "use_tls") {
        obj[k] = v === "true";
      } else if (v) {
        obj[k] = isNaN(Number(v)) ? v : Number(v);
      }
    }
    setIntegrationJson(JSON.stringify(obj, null, 2));
  };

  const loadIcFromJson = () => {
    try {
      const parsed = JSON.parse(integrationJson);
      const itype = parsed.integration_type || "http";
      const fields = icForm[itype] || icForm.http;
      const updated: Record<string, Record<string, string>> = { ...icForm };
      updated[itype] = { ...fields };
      for (const [k, v] of Object.entries(parsed)) {
        if (k in updated[itype]) {
          updated[itype] = { ...updated[itype], [k]: String(v) };
        }
      }
      setIcForm(updated);
    } catch {}
  };

  // Verification
  const [verifyingId, setVerifyingId] = useState<string | null>(null);
  const [lastVerify, setLastVerify] = useState<{ id: string; success: boolean; message: string } | null>(null);

  // Delete confirmation
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const refreshCategories = useCallback(async () => {
    try {
      const data = await getToolCategories();
      setCategories(data);
    } catch (e) {
      console.error("Failed to load categories:", e);
    }
  }, []);

  const refreshTools = useCallback(async () => {
    try {
      const data = await getCustomTools();
      setTools(data);
    } catch (e) {
      console.error("Failed to load tools:", e);
    }
  }, []);

  // Reset search when category changes
  const handleCategoryChange = useCallback(
    (type: string) => {
      setActiveCategory(type);
      setQuery("");
    },
    []
  );

  useEffect(() => {
    let cancelled = false;
    const init = async () => {
      setLoading(true);
      await Promise.all([refreshCategories(), refreshTools()]);
      if (!cancelled) setLoading(false);
    };
    init();
    return () => {
      cancelled = true;
    };
  }, [refreshCategories, refreshTools]);

  const openCreate = () => {
    setEditingTool(null);
    setFormData({
      name: "",
      description: "",
      tool_type: "custom",
      input_schema: { type: "object", properties: {} },
      config: {},
      output_schema: { type: "object", properties: {} },
    });
    setConfigJson("{}");
    setIntegrationJson("{}");
    setIcForm({
      http: { integration_type: "http", base_url: "", auth_type: "none", api_key: "", bearer_token: "", username: "", password: "", api_key_header: "X-API-Key", timeout_seconds: "30" },
      email_smtp: { integration_type: "email_smtp", smtp_host: "", smtp_port: "587", smtp_user: "", smtp_password: "", from_address: "", use_tls: "true" },
      email_api: { integration_type: "email_api", provider: "sendgrid", api_endpoint: "", api_key: "", from_address: "" },
      database: { integration_type: "database", driver: "", connection_string: "" },
      messaging_slack: { integration_type: "messaging_slack", bot_token: "" },
      storage_s3: { integration_type: "storage_s3", access_key: "", secret_key: "", bucket: "", region: "us-east-1", endpoint_url: "" },
      webhook: { integration_type: "webhook", endpoint_url: "", http_method: "POST" },
    });
    setIntegrationTestResult(null);
    setLastVerify(null);
    setActiveTab("definition");
    setShowModal(true);
  };

  const openEdit = (tool: CustomTool) => {
    setEditingTool(tool);
    setFormData({
      name: tool.name,
      description: tool.description,
      tool_type: tool.tool_type,
      input_schema: tool.input_schema as Record<string, unknown>,
      config: tool.config,
      output_schema: tool.output_schema as Record<string, unknown>,
    });
    setConfigJson(JSON.stringify(tool.config, null, 2));
    setIntegrationJson(JSON.stringify(tool.integration_config || {}, null, 2));
    loadIcFromJson();
    setIntegrationTestResult(null);
    setShowModal(true);
  };

  const handleSave = async () => {
    setConfigJsonError(null);
    setIntegrationJsonError(null);
    try {
      const parsedConfig = JSON.parse(configJson);
      setFormData((f) => ({ ...f, config: parsedConfig }));

      // Parse integration config (empty object = null)
      let integrationConfig: Record<string, unknown> | null = null;
      const trimmedIntegration = integrationJson.trim();
      if (trimmedIntegration && trimmedIntegration !== "{}") {
        integrationConfig = JSON.parse(trimmedIntegration);
      }

      const payload = {
        name: formData.name,
        description: formData.description,
        tool_type: formData.tool_type,
        input_schema: formData.input_schema,
        config: parsedConfig,
        output_schema: formData.output_schema,
        integration_config: integrationConfig,
      };

      if (editingTool) {
        await updateCustomTool(editingTool.id, payload);
      } else {
        await createCustomTool(payload);
      }
      setShowModal(false);
      refreshTools();
      refreshCategories();
    } catch (e) {
      if (e instanceof SyntaxError) {
        // Determine which field has invalid JSON
        const msg = (e as Error).message.toLowerCase();
        if (msg.includes("integration") || msg.includes("line") && integrationJsonError) {
          setIntegrationJsonError("Invalid JSON in integration config");
          return;
        }
        setConfigJsonError("Invalid JSON in configuration field");
        return;
      }
      setConfigJsonError((e as Error).message);
      console.error("Save error:", e);
    }
  };

  const handleVerify = async (tool: CustomTool) => {
    setVerifyingId(tool.id);
    setLastVerify(null);
    try {
      const res = await verifyCustomTool(tool.id);
      if (res && typeof res.success === "boolean") {
        setLastVerify({
          id: tool.id,
          success: res.success,
          message: res.message || "Verification complete",
        });
      } else {
        setLastVerify({
          id: tool.id,
          success: false,
          message: "Unexpected response from verification",
        });
      }
      refreshTools();
      refreshCategories();
    } catch (e) {
      setLastVerify({ id: tool.id, success: false, message: e instanceof Error ? e.message : "Verification failed" });
    } finally {
      setVerifyingId(null);
    }
  };

  const handleRegister = async (tool: CustomTool) => {
    try {
      await registerCustomTool(tool.id);
      refreshCategories();
    } catch (e) {
      alert((e as Error).message);
    }
  };

  const handleDelete = async (id: string) => {
    if (deleteConfirmId !== id) {
      setDeleteConfirmId(id);
      setTimeout(() => setDeleteConfirmId(null), 3000);
      return;
    }
    setDeleteConfirmId(null);
    try {
      await deleteCustomTool(id);
      setTools((prev) => prev.filter((t) => t.id !== id));
      refreshCategories();
    } catch (e) {
      alert((e as Error).message);
    }
  };

  // Compute category counts from actual tools data
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: tools.length };
    tools.forEach((t) => {
      counts[t.tool_type] = (counts[t.tool_type] || 0) + 1;
    });
    return counts;
  }, [tools]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let pool = activeCategory === "all" ? tools : tools.filter((t) => t.tool_type === activeCategory);
    if (!q) return pool;
    return pool.filter(
      (t) =>
        t.name.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q)
    );
  }, [tools, query, activeCategory]);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="shrink-0 border-b border-border">
        <div className="flex items-center justify-between px-5 h-14">
          <div>
            <h1 className="text-base font-semibold text-text tracking-tight">Tools</h1>
            <p className="text-xs text-text-muted">
              Browse, configure, and manage your workflow tools
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="text"
                placeholder="Search tools…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="h-9 pl-8 pr-3 bg-surface border border-border rounded-md text-sm text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 w-60"
              />
            </div>
            <button
              onClick={openCreate}
              className="h-9 px-4 bg-text text-base text-sm font-medium rounded-md hover:bg-text/90 transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              Add Tool
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto pb-20 md:pb-0">
        <div className="p-5 flex gap-6">
          {/* ── Sidebar: Categories ── */}
          <aside className="w-52 shrink-0 hidden md:block">
            <p className="text-[10px] font-medium text-text-muted/60 uppercase tracking-wider mb-2 px-3">
              Categories
            </p>
            <div className="space-y-0.5">
              {categories.map((cat) => {
                const Icon = TYPE_ICONS[cat.type] || Puzzle;
                return (
                  <button
                    key={cat.type}
                    onClick={() => handleCategoryChange(cat.type)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-all text-left ${
                      activeCategory === cat.type
                        ? "bg-surface-2 text-text border border-border"
                        : "text-text-muted hover:text-text hover:bg-surface-2/50"
                    }`}
                  >
                    <span className="shrink-0 opacity-70">
                      <Icon className="w-4 h-4" />
                    </span>
                    <span className="flex-1 truncate">{cat.label}</span>
                    <span className="text-[10px] font-mono text-text-muted/60">{categoryCounts[cat.type] ?? 0}</span>
                  </button>
                );
              })}
            </div>
          </aside>

          {/* Mobile category pills */}
          <div className="md:hidden col-span-full mb-2 overflow-x-auto flex gap-1.5 pb-1 -mx-1 px-1">
            {categories.map((cat) => (
              <button
                key={cat.type}
                onClick={() => handleCategoryChange(cat.type)}
                className={`px-3 py-1.5 text-xs rounded-md border whitespace-nowrap transition-all ${
                  activeCategory === cat.type
                    ? "border-text-muted/40 text-text bg-surface-2"
                    : "border-border text-text-muted"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* ── Main content ── */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-medium text-text">
                {categories.find((c) => c.type === activeCategory)?.label ?? activeCategory}
                <span className="ml-2 text-xs text-text-muted font-mono">({filtered.length})</span>
              </h2>
            </div>

            {/* Tool cards */}
            {loading ? (
              <div className="flex items-center justify-center py-20 text-text-muted">
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Loading tools…
              </div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-20 text-text-muted border border-dashed border-border rounded-lg">
                {query ? "No tools match your search." : "No tools in this category yet."}
                <br />
                {!query && (
                  <button
                    onClick={openCreate}
                    className="mt-3 text-xs text-accent hover:underline"
                  >
                    Add your first tool
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {filtered.map((tool) => {
                  const isVerifying = verifyingId === tool.id;
                  const toolVerifyResult =
                    lastVerify !== null && lastVerify.id === tool.id ? lastVerify : null;

                  return (
                    <div
                      key={tool.id}
                      className="p-5 bg-surface border border-border rounded-lg hover:border-text-muted/30 hover:shadow-md hover:shadow-black/10 transition-all"
                    >
                      <div className="flex items-center gap-2.5 mb-3">
                        <div className="w-8 h-8 rounded-md bg-surface-2 flex items-center justify-center shrink-0">
                          <Puzzle className="w-4 h-4 text-text-muted" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="text-sm font-medium text-text truncate">{tool.name}</h3>
                            <span
                              className={`px-1.5 py-0.5 text-[10px] font-medium rounded-full border shrink-0 ${STATUS_STYLES[tool.status] || STATUS_STYLES.draft}`}
                            >
                              {STATUS_LABEL[tool.status] || tool.status}
                            </span>
                          </div>
                          <p className="text-[10px] text-text-muted">
                            {TOOL_TYPE_LABELS[tool.tool_type] || tool.tool_type} &middot;{" "}
                            {new Date(tool.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <p className="text-xs text-text-muted leading-relaxed mb-3 line-clamp-2">
                        {tool.description}
                      </p>

                      {/* Verify result toast */}
                      {toolVerifyResult && (
                        <div
                          className={`mb-3 p-2.5 rounded-md text-xs flex items-start gap-2 ${
                            toolVerifyResult.success
                              ? "bg-success/5 border border-success/20 text-success"
                              : "bg-warn/5 border border-warn/20 text-warn"
                          }`}
                        >
                          {toolVerifyResult.success ? (
                            <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                          ) : (
                            <XCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                          )}
                          <span>{toolVerifyResult.message}</span>
                        </div>
                      )}

                      {/* Raw test output (collapsed) */}
                      {tool.last_test_result && (
                        <details className="mb-3">
                          <summary className="text-[10px] text-text-muted/60 cursor-pointer hover:text-text-muted select-none">
                            View test result
                          </summary>
                          <pre className="mt-1.5 p-2.5 rounded-md bg-surface-2 border border-border text-[11px] font-mono text-text-muted overflow-auto max-h-28">
                            {JSON.stringify(tool.last_test_result, null, 2)}
                          </pre>
                        </details>
                      )}

                      {/* Actions */}
                      <div className="flex items-center gap-1.5">
                        {tool.id.startsWith("builtin_") ? (
                          <span className="text-[10px] text-text-muted/60 flex items-center gap-1">
                            <Lock className="w-3 h-3" />
                            Built-in
                          </span>
                        ) : (
                          <>
                            <button
                              onClick={() => openEdit(tool)}
                              className="flex items-center gap-1 px-2.5 py-1.5 text-xs text-text-muted hover:text-text border border-transparent hover:border-border rounded-md transition-all"
                            >
                              <ExternalLink className="w-3 h-3" />
                              Edit
                            </button>

                            {tool.status !== "verified" && (
                              <button
                                onClick={() => handleVerify(tool)}
                                disabled={isVerifying}
                                className="flex items-center gap-1 px-2.5 py-1.5 text-xs text-success hover:bg-success/10 border border-transparent hover:border-success/20 rounded-md transition-all disabled:opacity-50"
                              >
                                {isVerifying ? (
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                ) : (
                                  <Play className="w-3 h-3" />
                                )}
                                {isVerifying ? "Testing…" : "Verify"}
                              </button>
                            )}

                            {tool.status === "verified" && (
                              <button
                                onClick={() => handleRegister(tool)}
                                className="flex items-center gap-1 px-2.5 py-1.5 text-xs text-accent hover:bg-accent/10 border border-transparent hover:border-accent/20 rounded-md transition-all"
                              >
                                <Save className="w-3 h-3" />
                                Register
                              </button>
                            )}

                            {tool.status === "verified" && tool.verified_at && (
                              <span className="text-[10px] text-text-muted ml-auto flex items-center gap-1 shrink-0">
                                <CheckCircle2 className="w-3 h-3 text-success" />
                                {new Date(tool.verified_at).toLocaleDateString()}
                              </span>
                            )}

                            <button
                              onClick={() => handleDelete(tool.id)}
                              className={`ml-auto p-1.5 rounded-md transition-all ${
                                deleteConfirmId === tool.id
                                  ? "text-warn bg-warn/10 border border-warn/30"
                                  : "text-text-muted hover:text-warn hover:bg-warn/10"
                              }`}
                              title={deleteConfirmId === tool.id ? "Click again to confirm deletion" : "Delete"}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Add / Edit Modal ── */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setShowModal(false)}
          />
          <div className="relative bg-base border border-border rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-auto mx-4">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border sticky top-0 bg-base z-10">
              <h2 className="text-base font-semibold text-text">
                {editingTool ? "Edit Tool" : "Add New Tool"}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 text-text-muted hover:text-text rounded-md"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-5">
              {/* Name */}
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1.5">
                  Tool Name <span className="text-warn">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Stripe Payment, Slack Notify"
                  className="w-full h-9 px-3 bg-surface border border-border rounded-md text-sm text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1.5">
                  Description <span className="text-warn">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="What does this tool do? How is it used?"
                  rows={2}
                  className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 resize-none"
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1.5">
                  Tool Type
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {TOOL_TYPES.map((tt) => (
                    <button
                      key={tt.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, tool_type: tt.value })}
                      className={`flex items-center gap-1.5 px-2.5 py-1.5 text-xs rounded-md border transition-all ${
                        formData.tool_type === tt.value
                          ? "border-text-muted/40 text-text bg-surface-2"
                          : "border-border text-text-muted hover:text-text"
                      }`}
                    >
                      <tt.icon className="w-3 h-3" />
                      {tt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tabs: Definition | Integration | Config */}
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1.5">
                  Details
                </label>
                <div className="flex rounded-md overflow-hidden border border-border mb-3">
                  {(["definition", "integration", "config"] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`flex-1 py-1.5 text-[10px] font-medium uppercase tracking-wider transition-colors ${
                        activeTab === tab
                          ? "bg-surface text-text border-b-2 border-text"
                          : "text-text-muted hover:text-text hover:bg-surface/50"
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                {/* Definition tab — input/output schema */}
                {activeTab === "definition" && (
                  <div className="space-y-3">
                    <div className="text-xs text-text-muted mb-2">
                      Define the tool's input parameters and expected output schema.
                    </div>
                    <label className="block text-xs font-medium text-text-muted mb-1.5">
                      Input Schema{" "}
                      <span className="text-text-muted/60">(JSON)</span>
                    </label>
                    <textarea
                      value={JSON.stringify(formData.input_schema, null, 2)}
                      onChange={(e) => {
                        try {
                          setFormData((f) => ({ ...f, input_schema: JSON.parse(e.target.value) }));
                        } catch {}
                      }}
                      placeholder='{"type": "object", "properties": {}}'
                      rows={5}
                      spellCheck={false}
                      className="w-full px-3 py-2 bg-surface border border-border rounded-md text-xs font-mono text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 resize-none"
                    />
                    <label className="block text-xs font-medium text-text-muted mb-1.5">
                      Output Schema{" "}
                      <span className="text-text-muted/60">(JSON)</span>
                    </label>
                    <textarea
                      value={JSON.stringify(formData.output_schema, null, 2)}
                      onChange={(e) => {
                        try {
                          setFormData((f) => ({ ...f, output_schema: JSON.parse(e.target.value) }));
                        } catch {}
                      }}
                      placeholder='{"type": "object", "properties": {}}'
                      rows={5}
                      spellCheck={false}
                      className="w-full px-3 py-2 bg-surface border border-border rounded-md text-xs font-mono text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 resize-none"
                    />
                  </div>
                )}

                {/* Integration tab — real service credentials */}
                {activeTab === "integration" && (
                  <div className="space-y-3">
                    {(() => {
                      const itype = getIntegrationType();
                      const fields = icForm[itype] || icForm.http;
                      const isSecret = (k: string) => ["password", "smtp_password", "secret_key", "bearer_token", "api_key", "bot_token", "access_key"].includes(k);

                      const updateField = (key: string, value: string) => {
                        setIcForm((prev) => {
                          const next = { ...prev };
                          next[itype] = { ...next[itype], [key]: value };
                          return next;
                        });
                      };

                      const renderField = (key: string, label: string, type = "text", placeholder = "") => {
                        const secret = isSecret(key);
                        return (
                          <div key={key}>
                            <label className="block text-[10px] font-medium text-text-muted mb-1">
                              {label} {secret && <span className="text-warn/70">(sensitive)</span>}
                            </label>
                            <div className="relative">
                              <input
                                type={secret && !showSecrets ? "password" : "text"}
                                value={fields[key] || ""}
                                onChange={(e) => { updateField(key, e.target.value); syncIcFormToJson(); }}
                                placeholder={placeholder}
                                spellCheck={false}
                                className="w-full h-8 px-2.5 pr-8 bg-surface border border-border rounded-md text-xs text-text placeholder:text-text-muted/50 focus:outline-none focus:border-text-muted focus:ring-1 focus:ring-text-muted/30"
                              />
                              {secret && (
                                <button
                                  type="button"
                                  onClick={() => setShowSecrets((s) => !s)}
                                  className="absolute right-1.5 top-1/2 -translate-y-1/2 p-1 text-text-muted/50 hover:text-text-muted"
                                  title={showSecrets ? "Hide" : "Show"}
                                >
                                  {showSecrets ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      };

                      return (
                        <>
                          {/* Integration type selector */}
                          <div>
                            <label className="block text-[10px] font-medium text-text-muted mb-1">
                              Integration Type
                            </label>
                            <div className="flex flex-wrap gap-1">
                              {[
                                { v: "http", l: "HTTP / API", i: Globe },
                                { v: "email_smtp", l: "Email (SMTP)", i: Mail },
                                { v: "email_api", l: "Email (API)", i: Mail },
                                { v: "database", l: "Database", i: Database },
                                { v: "messaging_slack", l: "Slack", i: MessageSquare },
                                { v: "storage_s3", l: "S3 Storage", i: HardDrive },
                                { v: "webhook", l: "Webhook", i: Link2 },
                              ].map(({ v, l, i: Icon }) => (
                                <button
                                  key={v}
                                  type="button"
                                  onClick={() => {
                                    setIcForm((prev) => ({ ...prev, [v]: { ...prev[v] } }));
                                    syncIcFormToJson();
                                  }}
                                  className={`flex items-center gap-1 px-2 py-1 text-[10px] rounded-md border transition-all ${
                                    itype === v
                                      ? "border-text-muted/40 text-text bg-surface-2"
                                      : "border-border text-text-muted hover:text-text"
                                  }`}
                                >
                                  <Icon className="w-3 h-3" />
                                  {l}
                                </button>
                              ))}
                            </div>
                          </div>

                          {/* Raw JSON toggle */}
                          <details className="text-[10px]">
                            <summary className="text-text-muted/60 cursor-pointer hover:text-text-muted select-none mb-2">
                              Advanced: edit raw JSON
                            </summary>
                            <textarea
                              value={integrationJson}
                              onChange={(e) => {
                                setIntegrationJson(e.target.value);
                                loadIcFromJson();
                                setIntegrationJsonError(null);
                              }}
                              rows={8}
                              spellCheck={false}
                              className="w-full px-3 py-2 bg-surface border border-border rounded-md text-[10px] font-mono text-text placeholder:text-text-muted/50 focus:outline-none focus:border-text-muted resize-none"
                            />
                          </details>

                          {/* Type-specific fields */}
                          <div className="grid grid-cols-2 gap-2.5">
                            {itype === "http" && <>
                              {renderField("base_url", "Base URL", "text", "https://api.example.com")}
                              {renderField("auth_type", "Auth Type", "text", "none / bearer / api_key / basic")}
                              {renderField("api_key", "API Key")}
                              {renderField("bearer_token", "Bearer Token")}
                              {renderField("username", "Username (basic auth)")}
                              {renderField("password", "Password (basic auth)", "password")}
                              {renderField("api_key_header", "API Key Header", "text", "X-API-Key")}
                              {renderField("timeout_seconds", "Timeout (s)", "text", "30")}
                            </>}
                            {itype === "email_smtp" && <>
                              {renderField("smtp_host", "SMTP Host", "text", "smtp.gmail.com")}
                              {renderField("smtp_port", "SMTP Port", "text", "587")}
                              {renderField("smtp_user", "SMTP Username")}
                              {renderField("smtp_password", "SMTP Password", "password")}
                              {renderField("from_address", "From Address")}
                              <div>
                                <label className="block text-[10px] font-medium text-text-muted mb-1">Use TLS</label>
                                <select
                                  value={fields["use_tls"] || "true"}
                                  onChange={(e) => { updateField("use_tls", e.target.value); syncIcFormToJson(); }}
                                  className="w-full h-8 px-2.5 bg-surface border border-border rounded-md text-xs text-text focus:outline-none focus:border-text-muted"
                                >
                                  <option value="true">Yes</option>
                                  <option value="false">No</option>
                                </select>
                              </div>
                            </>}
                            {itype === "email_api" && <>
                              {renderField("provider", "Provider", "text", "sendgrid / mailgun")}
                              {renderField("api_endpoint", "API Endpoint")}
                              {renderField("api_key", "API Key")}
                              {renderField("from_address", "From Address")}
                            </>}
                            {itype === "database" && <>
                              {renderField("driver", "Driver", "text", "postgresql / mysql / sqlite")}
                              {renderField("connection_string", "Connection String", "text", "postgresql://...")}
                            </>}
                            {itype === "messaging_slack" && <>
                              {renderField("bot_token", "Bot Token (xoxb-...)")}
                            </>}
                            {itype === "storage_s3" && <>
                              {renderField("access_key", "Access Key ID")}
                              {renderField("secret_key", "Secret Access Key", "password")}
                              {renderField("bucket", "Bucket Name")}
                              {renderField("region", "Region", "text", "us-east-1")}
                              {renderField("endpoint_url", "Endpoint URL (optional)")}
                            </>}
                            {itype === "webhook" && <>
                              {renderField("endpoint_url", "Webhook URL")}
                              {renderField("http_method", "HTTP Method", "text", "POST")}
                            </>}
                          </div>
                        </>
                      );
                    })()}
                  </div>
                )}

                {/* Config tab — tool runtime config */}
                {activeTab === "config" && (
                  <div>
                    <label className="block text-xs font-medium text-text-muted mb-1.5">
                      Configuration{" "}
                      <span className="text-text-muted/60">(JSON)</span>
                    </label>
                    <textarea
                      value={configJson}
                      onChange={(e) => {
                        setConfigJson(e.target.value);
                        setConfigJsonError(null);
                      }}
                      placeholder='{"key": "value"}'
                      rows={10}
                      spellCheck={false}
                      className="w-full px-3 py-2 bg-surface border border-border rounded-md text-xs font-mono text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 resize-none"
                    />
                    <p className="mt-1 text-[10px] text-text-muted/60">
                      Define connection strings, endpoints, API keys, or any
                      runtime config this tool needs.
                    </p>
                    {configJsonError && (
                      <p className="mt-1.5 text-[10px] text-warn flex items-center gap-1">
                        <X className="w-3 h-3 shrink-0" />
                        {configJsonError}
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Input Schema */}
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1.5">
                  Input Schema{" "}
                  <span className="text-text-muted/60">(JSON)</span>
                </label>
                <textarea
                  value={JSON.stringify(formData.input_schema, null, 2)}
                  onChange={(e) => {
                    try {
                      setFormData({
                        ...formData,
                        input_schema: JSON.parse(e.target.value),
                      });
                    } catch {
                      // ignore parse errors while typing
                    }
                  }}
                  placeholder='{"type": "object", "properties": {...}}'
                  rows={4}
                  spellCheck={false}
                  className="w-full px-3 py-2 bg-surface border border-border rounded-md text-xs font-mono text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 resize-none"
                />
              </div>

              {/* Output Schema */}
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1.5">
                  Output Schema{" "}
                  <span className="text-text-muted/60">(JSON)</span>
                </label>
                <textarea
                  value={JSON.stringify(formData.output_schema, null, 2)}
                  onChange={(e) => {
                    try {
                      setFormData({
                        ...formData,
                        output_schema: JSON.parse(e.target.value),
                      });
                    } catch {
                      // ignore parse errors while typing
                    }
                  }}
                  placeholder='{"type": "object", "properties": {...}}'
                  rows={4}
                  spellCheck={false}
                  className="w-full px-3 py-2 bg-surface border border-border rounded-md text-xs font-mono text-text placeholder:text-text-muted/60 focus:outline-none focus:border-text-muted focus:ring-2 focus:ring-text-muted/20 resize-none"
                />
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-border sticky bottom-0 bg-base">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm text-text-muted hover:text-text border border-border rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={!formData.name || !formData.description}
                className="px-4 py-2 text-sm font-medium bg-text text-base rounded-md hover:bg-text/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {editingTool ? "Save Changes" : "Create Tool"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
