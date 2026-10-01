"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Workflow,
  Zap,
  Shield,
  ArrowRight,
  Sparkles,
  Terminal,
  ChevronRight,
  Send,
  Play,
  CheckCircle2,
  Loader2,
  X,
  FileText,
  GitBranch,
  Rocket,
  Eye,
} from "lucide-react";
import Link from "next/link";
import LandingNav from "@/components/LandingNav";

/* ------------------------------------------------------------------ */
/*  Data                                                               */
/* ------------------------------------------------------------------ */

const features = [
  {
    icon: FileText,
    title: "Natural Language Input",
    description:
      "Describe any process in plain English. No node graphs, no YAML — just tell FlowState what you need.",
    color: "text-accent",
  },
  {
    icon: GitBranch,
    title: "Auto-Generate Workflows",
    description:
      "Your prompt compiles into a structured workflow graph with triggers, actions, conditions, and approval gates.",
    color: "text-signal",
  },
  {
    icon: Shield,
    title: "Human Approval Gates",
    description:
      "Pause execution when it matters. Approve, reject, or modify — the engine waits and resumes seamlessly.",
    color: "text-success",
  },
  {
    icon: Eye,
    title: "Fully Observable",
    description:
      "Real-time logs, node-level outcomes, and AI verification. Every run is inspectable and auditable.",
    color: "text-warn",
  },
];

const templates = [
  {
    name: "Customer Onboarding",
    desc: "New user setup, email verification, welcome flow",
    prompt:
      "Send a welcome email to a new customer, create their account in the CRM, and notify the sales team.",
    status: "completed",
  },
  {
    name: "Daily Report Generator",
    desc: "Fetch metrics, compile PDF, send to stakeholders",
    prompt:
      "Every morning, fetch yesterday's sales metrics, compile a PDF report, and email it to the leadership team.",
    status: "running",
  },
  {
    name: "Invoice Processor",
    desc: "Extract data, validate, post to accounting system",
    prompt:
      "When a new invoice arrives, extract line items, validate totals, and post the record to the accounting system.",
    status: "pending",
  },
  {
    name: "Support Triage",
    desc: "Categorize tickets, assign priority, notify team",
    prompt:
      "When a support ticket is submitted, categorize it by topic, assign priority based on SLA rules, and notify the right team.",
    status: "pending",
  },
  {
    name: "Lead Qualification",
    desc: "Score leads, enrich data, route to sales",
    prompt:
      "When a lead is captured, enrich their data, score based on criteria, and route high-value leads to the sales team.",
    status: "completed",
  },
  {
    name: "Deploy Pipeline",
    desc: "Run tests, build, deploy, notify channel",
    prompt:
      "On code push, run the test suite, build the project, deploy to staging, and post a summary to the team Slack channel.",
    status: "running",
  },
];

const demoSteps = [
  {
    key: "input",
    label: "Input",
    icon: FileText,
    description: "Describe your process in plain English",
  },
  {
    key: "plan",
    label: "Plan",
    icon: GitBranch,
    description: "AI compiles a structured workflow graph",
  },
  {
    key: "execute",
    label: "Execute",
    icon: Rocket,
    description: "Run nodes with real-time observability",
  },
  {
    key: "verify",
    label: "Verify",
    icon: CheckCircle2,
    description: "AI verifier checks outputs and outcomes",
  },
];

/* ------------------------------------------------------------------ */
/*  RunIdSpan – generates a stable run ID on the client               */
/* ------------------------------------------------------------------ */

function RunIdSpan() {
  const [runId, setRunId] = useState<string>("");

  useEffect(() => {
    setRunId(`run_${Math.random().toString(36).slice(2, 6)}`);
  }, []);

  return <span>{runId}</span>;
}

/* ------------------------------------------------------------------ */
/*  Main page                                                          */
/* ------------------------------------------------------------------ */

export default function LandingPage() {
  const [step, setStep] = useState(0);
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [showOutput, setShowOutput] = useState(false);
  const stepIntervalRef = useRef<number | null>(null);

  // Cycle demo steps
  const startDemo = useCallback(() => {
    setStep(0);
    setShowOutput(false);
    setGenerating(true);
    setError(null);

    if (stepIntervalRef.current) clearInterval(stepIntervalRef.current);

    let current = 0;
    stepIntervalRef.current = window.setInterval(() => {
      current += 1;
      if (current >= demoSteps.length) {
        if (stepIntervalRef.current) clearInterval(stepIntervalRef.current);
        setGenerating(false);
        setShowOutput(true);
        return;
      }
      setStep(current);
    }, 900);
  }, []);

  useEffect(() => {
    return () => {
      if (stepIntervalRef.current) clearInterval(stepIntervalRef.current);
    };
  }, []);

  const handleTemplateClick = (tplPrompt: string) => {
    setSelectedTemplate(tplPrompt);
    setPrompt(tplPrompt);
    startDemo();
  };

  const handleGenerate = () => {
    if (!prompt.trim()) {
      setError("Enter a workflow description or pick a template to begin.");
      return;
    }
    setError(null);
    setWorkflowName(prompt.trim().split(" ").slice(0, 4).join(" "));
    startDemo();
  };

  const handleClear = () => {
    setPrompt("");
    setSelectedTemplate(null);
    setShowOutput(false);
    setGenerating(false);
    setError(null);
    setWorkflowName("");
    if (stepIntervalRef.current) clearInterval(stepIntervalRef.current);
    setStep(0);
  };

  const activeStep = demoSteps[step];

  return (
    <div className="min-h-screen bg-base text-text flex flex-col">
      <LandingNav />

      {/* ============ HERO ============ */}
      <section className="relative overflow-hidden min-h-screen flex flex-col items-center justify-center">
        {/* Ambient glow */}
        <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
          <div
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] opacity-[0.04]"
            style={{
              background:
                "radial-gradient(ellipse at center, var(--color-accent) 0%, transparent 70%)",
            }}
          />
        </div>

        <div className="px-6 pt-28 pb-20 text-center relative">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-surface mb-8">
            <Sparkles className="w-3.5 h-3.5 text-accent" />
            <span className="text-[11px] font-medium text-text-muted">
              AI-powered workflow automation
            </span>
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.1] mb-4">
            Turn words into
            <br />
            <span className="text-accent">executable workflows</span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-xl mx-auto text-base sm:text-lg text-text-muted leading-relaxed mb-10">
            Describe any business process in natural language. FlowState
            compiles, runs, and verifies it — so you can ship automation in
            seconds, not sprints.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-6">
            <Link
              href="/dashboard"
              className="h-11 px-6 bg-text text-base text-sm font-medium rounded-lg hover:bg-text/90 transition-all flex items-center gap-2"
            >
              Open Dashboard
              <ArrowRight className="w-4 h-4" />
            </Link>
            <button
              onClick={() =>
                document
                  .getElementById("playground")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
              className="h-11 px-6 border border-border text-text text-sm font-medium rounded-lg hover:bg-surface-2 hover:border-text-muted/40 transition-all flex items-center gap-2"
            >
              <Play className="w-4 h-4 text-signal" />
              Try it Live
            </button>
          </div>
        </div>
      </section>

      {/* ============ STATS BAR ============ */}
      <section className="border-y border-border bg-surface/40">
        <div className="px-6 py-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { value: "6+", label: "Built-in Tools" },
              { value: "100%", label: "Observable Runs" },
              { value: "AI", label: "Powered Planning" },
              { value: "0", label: "Config Required" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-2xl font-semibold text-accent tracking-tight">
                  {stat.value}
                </p>
                <p className="text-xs text-text-muted mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============ INTERACTIVE PLAYGROUND ============ */}
      <section id="playground" className="py-24">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight mb-3">
              See it in action
            </h2>
            <p className="text-sm text-text-muted max-w-md mx-auto">
              Type a process description or pick a template and watch
              FlowState plan, execute, and verify it.
            </p>
          </div>

          {/* Glass card */}
          <div className="bg-surface/80 backdrop-blur-xl border border-border rounded-2xl p-6 sm:p-8">
            {/* Prompt input */}
            <label className="block text-xs text-text-muted mb-2 font-medium">
              Workflow description
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Send a welcome email to every new customer and notify the sales team"
              rows={3}
              disabled={generating}
              className="w-full rounded-xl border border-border bg-surface-2 text-text text-sm placeholder:text-text-muted/50 p-4 resize-none focus:outline-none focus:border-accent/60 transition-colors disabled:opacity-60"
            />

            {error && (
              <p className="text-warn text-xs mt-2 flex items-center gap-1.5">
                <X className="w-3.5 h-3.5" />
                {error}
              </p>
            )}

            <div className="flex items-center gap-3 mt-4">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="h-10 px-5 bg-text text-base text-sm font-medium rounded-lg hover:bg-text/90 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                {generating ? "Generating..." : "Generate Workflow"}
              </button>

              {(prompt || selectedTemplate) && !generating && (
                <button
                  onClick={handleClear}
                  className="h-10 px-4 border border-border text-text-muted text-sm font-medium rounded-lg hover:bg-surface-2 hover:text-text transition-all"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Animated demo steps */}
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                {demoSteps.map((s, i) => {
                  const Icon = s.icon;
                  const isActive = i === step;
                  const isPast = i < step;
                  return (
                    <div key={s.key} className="flex flex-col items-center gap-1.5 flex-1">
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-500 ${
                          isPast
                            ? "bg-success/20 border-success"
                            : isActive
                            ? "bg-accent/20 border-accent scale-110"
                            : "bg-surface-2 border-border"
                        }`}
                      >
                        {isPast ? (
                          <CheckCircle2 className="w-5 h-5 text-success" />
                        ) : (
                          <Icon
                            className={`w-5 h-5 ${
                              isActive ? "text-accent" : "text-text-muted"
                            }`}
                          />
                        )}
                      </div>
                      <span
                        className={`text-[10px] font-medium transition-colors duration-500 ${
                          isActive ? "text-accent" : "text-text-muted"
                        }`}
                      >
                        {s.label}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Connector line */}
              <div className="relative h-0.5 bg-border rounded-full mb-4 overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 bg-accent rounded-full transition-all duration-500"
                  style={{
                    width: step === 0
                      ? "0%"
                      : step === 1
                      ? "33%"
                      : step === 2
                      ? "66%"
                      : "100%",
                  }}
                />
              </div>

              {/* Step description */}
              <div className="bg-surface-2 border border-border rounded-xl p-4 min-h-[60px] flex items-center transition-all duration-300">
                <div className="flex items-center gap-3">
                  {activeStep && (
                    <>
                      <activeStep.icon className="w-5 h-5 text-accent flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-text">
                          {activeStep.label}
                        </p>
                        <p className="text-xs text-text-muted">
                          {activeStep.description}
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Output panel */}
              {showOutput && workflowName && (
                <div className="mt-4 bg-surface-2 border border-border rounded-xl p-4 animate-in">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-medium text-text-muted">
                      Generated workflow
                    </span>
                    <span className="px-2 py-0.5 text-[10px] font-medium rounded-full bg-success/10 text-success border border-success/20">
                      verified
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text font-medium">
                      {workflowName}
                    </span>
                    <span className="text-xs text-text-muted font-mono">
                      <RunIdSpan />
                    </span>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Link
                      href={`/builder?prompt=${encodeURIComponent(prompt)}`}
                      className="h-8 px-3 bg-text text-base text-xs font-medium rounded-md hover:bg-text/90 transition-all flex items-center gap-1.5"
                    >
                      <ArrowRight className="w-3 h-3" />
                      Open in Builder
                    </Link>
                    <Link
                      href="/console"
                      className="h-8 px-3 border border-border text-text-muted text-xs font-medium rounded-md hover:bg-surface hover:text-text transition-all flex items-center gap-1.5"
                    >
                      <Terminal className="w-3 h-3" />
                      View Console
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ============ HOW IT WORKS ============ */}
      <section id="how-it-works" className="py-24 bg-surface/30 border-y border-border">
        <div className="px-6">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight mb-3">
              How it works
            </h2>
            <p className="text-sm text-text-muted max-w-md mx-auto">
              From a sentence to a running workflow in four steps.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {demoSteps.map((s, i) => {
              const Icon = s.icon;
              return (
                <div
                  key={s.key}
                  className="relative p-6 bg-surface border border-border rounded-xl"
                >
                  <span className="text-[10px] font-mono text-text-muted/40 mb-3 block">
                    STEP {String(i + 1).padStart(2, "0")}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-surface-2 border border-border flex items-center justify-center mb-3">
                    <Icon className="w-4 h-4 text-text-muted" />
                  </div>
                  <h3 className="text-sm font-semibold text-text mb-1.5">
                    {s.label}
                  </h3>
                  <p className="text-xs text-text-muted leading-relaxed">
                    {s.description}
                  </p>
                  {i < demoSteps.length - 1 && (
                    <ChevronRight className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-wire" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============ FEATURES ============ */}
      <section className="py-24">
        <div className="px-6">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight mb-3">
              Built for reliability
            </h2>
            <p className="text-sm text-text-muted max-w-md mx-auto">
              Every workflow is executable, observable, and verified — not just
              generated.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div
                  key={feature.title}
                  className="p-6 bg-surface border border-border rounded-xl hover:border-text-muted/30 hover:shadow-md hover:shadow-black/5 transition-all"
                >
                  <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border flex items-center justify-center mb-4">
                    <Icon
                      className={`w-4.5 h-4.5 ${feature.color}`}
                      strokeWidth={1.5}
                    />
                  </div>
                  <h3 className="text-sm font-semibold text-text mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-xs text-text-muted leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============ TEMPLATES ============ */}
      <section id="templates" className="py-24 bg-surface/30 border-y border-border">
        <div className="px-6">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight mb-3">
              Start from a template
            </h2>
            <p className="text-sm text-text-muted max-w-md mx-auto">
              Pre-built patterns for common automation scenarios. Click to try.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {templates.map((tpl) => (
              <button
                key={tpl.name}
                onClick={() => handleTemplateClick(tpl.prompt)}
                disabled={generating}
                className="text-left block p-5 bg-surface border border-border rounded-xl hover:border-text-muted/30 hover:shadow-md hover:shadow-black/5 transition-all group disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-8 h-8 rounded-lg bg-surface-2 border border-border flex items-center justify-center">
                    <Workflow className="w-4 h-4 text-text-muted" />
                  </div>
                  <span
                    className={`px-2 py-0.5 text-[10px] font-medium rounded-full border ${
                      tpl.status === "completed"
                        ? "bg-success/10 text-success border-success/20"
                        : tpl.status === "running"
                        ? "bg-signal/10 text-signal border-signal/20"
                        : "bg-accent/10 text-accent border-accent/20"
                    }`}
                  >
                    {tpl.status}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-text mb-1 group-hover:text-accent transition-colors">
                  {tpl.name}
                </h3>
                <p className="text-xs text-text-muted leading-relaxed">
                  {tpl.desc}
                </p>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ============ CTA ============ */}
      <section className="py-24">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <Zap className="w-8 h-8 text-accent mx-auto mb-6" />
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight mb-4">
            Ready to automate?
          </h2>
          <p className="text-sm text-text-muted mb-8 max-w-md mx-auto">
            Open the dashboard, describe your first workflow, and let
            FlowState do the rest.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex h-11 px-6 bg-text text-base text-sm font-medium rounded-lg hover:bg-text/90 transition-all items-center gap-2"
          >
            Get Started
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* ============ FOOTER ============ */}
      <footer className="border-t border-border py-8">
        <div className="px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-md bg-text flex items-center justify-center">
              <Workflow className="w-3.5 h-3.5 text-base" strokeWidth={2.5} />
            </div>
            <span className="text-sm font-semibold text-text tracking-tight">
              FlowState
            </span>
          </div>
          <p className="text-xs text-text-muted">
            FlowState — AI Workflow Automation
          </p>
          <div className="flex items-center gap-4">
            <a
              href="#how-it-works"
              className="text-xs text-text-muted hover:text-text transition-colors"
            >
              How it works
            </a>
            <a
              href="#templates"
              className="text-xs text-text-muted hover:text-text transition-colors"
            >
              Templates
            </a>
            <Link
              href="/dashboard"
              className="text-xs text-text-muted hover:text-text transition-colors"
            >
              Sign in
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
