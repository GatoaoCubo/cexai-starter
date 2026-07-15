"use client";

// ----------------------------------------------------------------------------
// The ASYNC MULTI-STEP agent cockpit, as a modal overlay (ADR adr_agents_sdk_dashboard,
// Phase C). The SIBLING of AgentRunModal: same Props, same kickoff UX (a typed form
// from the Input Schema, or a free-text intent box). The ONE difference is the run
// itself -- here the agent runs the multi-step plan/act/observe/tool LOOP, so the run
// is ASYNC and the cockpit shows the live step ledger as it progresses.
//
//   agent -> [typed form] -> Run loop -> POLL the snapshot -> live step ledger -> ResultView
//
// TRANSPORT: the cockpit drives progress by POLLING client.getAgentRun(run_id) on an
// interval (~900ms) until the snapshot is ``done``. It does NOT use the browser
// EventSource for the SSE endpoint -- EventSource cannot send the Authorization: Bearer
// header the backend requires, so polling the snapshot (the documented OQ3 fallback) is
// the auth-clean primary path and works identically in FIXTURES mode (no backend). A
// fetch-stream SSE reader against /agent/run/{id}/events is a possible future live
// enhancement; polling is what ships here.
//
// HONEST TRACE: the step ledger renders the REAL steps_log the backend records --
// each step's index + kind (plan/act/observe/tool) + a readable content view, and for
// tool steps the tool name + tool_io ({args,result}). A step gated through HITL
// (approval_id set, OQ8 emit-and-defer) shows a clear "approval pending" chip -- the
// tool was NOT executed. This is the real signal, not a fake ramp. The FilamentTrace is
// kept as a subtle motion accent while the run is live. The cost meter shows steps +
// tokens vs their ceilings (degrade-never: it hides what is absent).
//
// tenant_id is never set here; the scope chips show the SESSION tenant as provenance.
// No credential/api_key is ever rendered (the DTOs are credential-free by construction).
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import {
  parseSchemaFields,
  coerceFieldValue,
  type SchemaField,
} from "@/lib/agentSchema";
import type {
  AgentDetail,
  AgentRun,
  AgentRunCost,
  AgentStep,
  AgentStepKind,
  FieldValue,
  RunStatus,
} from "@/lib/types";
import { FilamentTrace } from "./FilamentTrace";
import { ResultView } from "./ResultView";
import { StatusBadge } from "./ui";
import { AlertIcon, ArrowRight } from "./icons";

interface Props {
  agent: AgentDetail | null;
  /** the session's verified tenant (provenance only; never sent to the backend). */
  tenantId: string;
  tenantLabel?: string;
  /** Bearer for live backend calls (lib/api). Ignored in fixtures mode. */
  accessToken: string;
  onClose: () => void;
  /** fired after a successful run so the parent can refresh history. */
  onComplete?: () => void;
}

// How often the cockpit polls the run snapshot (OQ3 poll transport). ~900ms reads as
// live without hammering the backend; fixtures reveal one step per poll.
const POLL_MS = 900;

// The local UI status. ``idle`` before kickoff; ``running`` while polling; ``done``
// once the snapshot is terminal; ``error`` on a failed kickoff/poll. (The run's OWN
// status -- completed/failed/refused/budget_exceeded -- is read off the snapshot.)
type CockpitStatus = "idle" | "running" | "done" | "error";

export function AgentRunCockpit({
  agent,
  tenantId,
  tenantLabel,
  accessToken,
  onClose,
  onComplete,
}: Props) {
  // The typed fields derived from the agent's Input Schema (or [] -> free-text fallback).
  const fields = useMemo<SchemaField[]>(
    () => (agent ? parseSchemaFields(agent.input_schema) : []),
    [agent],
  );
  const hasSchema = fields.length > 0;

  // One value per field (string-backed; coerced at submit). Free-text uses ``intent``.
  const [values, setValues] = useState<Record<string, string>>({});
  const [intent, setIntent] = useState("");
  const [status, setStatus] = useState<CockpitStatus>("idle");
  const [run, setRun] = useState<AgentRun | null>(null);
  const [error, setError] = useState<string | null>(null);

  // The polling interval handle + the active run_id (so the loop and unmount can clear).
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const runIdRef = useRef<string | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  // Reset whenever a new agent opens (or it closes). Also clears any live poll.
  useEffect(() => {
    stopPolling();
    runIdRef.current = null;
    setStatus("idle");
    setRun(null);
    setError(null);
    setValues({});
    setIntent(agent?.goal ?? "");
  }, [agent, stopPolling]);

  // Close on Escape (only when not mid-run, mirrors AgentRunModal).
  useEffect(() => {
    if (!agent) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && status !== "running") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [agent, onClose, status]);

  // Stop the poll on unmount (no leaked interval).
  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  // Assemble the typed inputs payload from the form (or the free-text intent).
  const buildInputs = useCallback((): Record<string, unknown> => {
    if (!hasSchema) {
      return { intent: intent.trim() || agent?.goal || agent?.name || "" };
    }
    const out: Record<string, unknown> = {};
    for (const f of fields) {
      const raw = values[f.key];
      if (raw === undefined || raw === "") continue; // omit empties (the agent's schema defaults)
      out[f.key] = coerceFieldValue(raw, f);
    }
    return out;
  }, [hasSchema, fields, values, intent, agent]);

  async function run_() {
    if (!agent || status === "running") return;
    setStatus("running");
    setError(null);
    setRun(null);

    const client = new ApiClient(accessToken);
    try {
      // 1. Kick the async run -> a run_id handle (202).
      const started = await client.startAgentRun(agent.id, buildInputs());
      runIdRef.current = started.run_id;

      // 2. Poll the snapshot until ``done`` (the OQ3 poll transport). Each poll
      //    refreshes the live step ledger + the cost meter.
      const poll = async () => {
        const rid = runIdRef.current;
        if (!rid) return;
        try {
          const snap = await client.getAgentRun(rid);
          setRun(snap);
          if (snap.done) {
            stopPolling();
            setStatus("done");
            onComplete?.();
          }
        } catch (err) {
          stopPolling();
          setStatus("error");
          setError(pollErrorMessage(err));
        }
      };

      // Poll once immediately so the first step shows without waiting a full interval.
      await poll();
      if (runIdRef.current && !pollRef.current) {
        pollRef.current = setInterval(poll, POLL_MS);
      }
    } catch (err) {
      stopPolling();
      setStatus("error");
      setError(
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "The agent run could not be started.",
      );
    }
  }

  if (!agent) return null;

  const sig = [
    `agent=${agent.id}`,
    agent.kind ? `kind=${agent.kind}` : null,
    agent.pillar ?? null,
    `nucleus ${agent.nucleus}`,
    `tenant=${tenantLabel || tenantId.slice(0, 8)}`,
  ]
    .filter(Boolean)
    .join(" . ");

  const running = status === "running";
  const runStatus = run?.status;
  const budgetExceeded = runStatus === "budget_exceeded";
  const runRefused = runStatus === "refused";
  const runFailed = runStatus === "failed";
  // The run reached a terminal state but did NOT complete cleanly (gate/budget/refuse).
  const terminalNotOk =
    status === "done" && (budgetExceeded || runRefused || runFailed);

  // Drive the filament from the budget (steps_used / ceiling), falling back to the
  // ledger length over a nominal horizon when no cost ceiling is present.
  const progress = filamentProgress(run);

  // The local status badge maps to the shared RunStatus vocabulary.
  const badgeStatus: RunStatus | null =
    status === "idle"
      ? null
      : status === "running"
        ? "running"
        : status === "error" || terminalNotOk
          ? "error"
          : "done";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label={`Run loop ${agent.name}`}
      onClick={(e) => {
        if (e.target === e.currentTarget && !running) onClose();
      }}
    >
      <div className="panel relative max-h-[90vh] w-full max-w-2xl animate-rise-in overflow-auto">
        {/* close */}
        <button
          onClick={() => !running && onClose()}
          disabled={running}
          aria-label="Close"
          className="absolute right-4 top-4 grid h-8 w-8 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted transition-colors hover:border-line-strong hover:text-text disabled:opacity-40"
        >
          <span className="text-lg leading-none">&times;</span>
        </button>

        {/* head */}
        <div className="border-b border-line px-6 py-5">
          <div className="flex items-center gap-3">
            <h2 className="font-display text-2xl font-600 tracking-tight text-text">
              {agent.name}
            </h2>
            <span className="chip border-synapse/30 text-synapse">multi-step</span>
            {!agent.enabled && <span className="chip">disabled</span>}
            {badgeStatus && <StatusBadge status={badgeStatus} />}
          </div>
          <p className="mt-2 font-mono text-2xs text-text-faint">{sig}</p>
        </div>

        <div className="px-6 py-5">
          {/* ---- the typed form (from the Input Schema), or the free-text fallback --- */}
          {status === "idle" && (
            <div className="space-y-4">
              <p className="eyebrow">
                // {hasSchema ? "typed inputs (Input Schema)" : "intent"}
              </p>

              {hasSchema ? (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {fields.map((f) => (
                    <AgentField
                      key={f.key}
                      field={f}
                      value={values[f.key] ?? ""}
                      disabled={running}
                      onChange={(v) =>
                        setValues((prev) => ({ ...prev, [f.key]: v }))
                      }
                    />
                  ))}
                </div>
              ) : (
                <div>
                  <label
                    htmlFor="cockpit-intent"
                    className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
                  >
                    Intent
                  </label>
                  <textarea
                    id="cockpit-intent"
                    value={intent}
                    onChange={(e) => setIntent(e.target.value)}
                    disabled={running}
                    rows={2}
                    className="field resize-none disabled:opacity-60"
                    placeholder={agent.goal || "Describe what you want this agent to do."}
                  />
                  <p className="mt-1.5 font-mono text-2xs text-text-faint">
                    This agent declares no Input Schema -- runs from a free-text intent.
                  </p>
                </div>
              )}

              <button
                onClick={run_}
                disabled={running}
                className="btn-primary mt-2 w-full"
              >
                Run loop
                <ArrowRight />
              </button>

              {/* multi-step honesty note */}
              <p className="text-center font-mono text-2xs text-text-faint">
                multi-step . plan -&gt; act -&gt; observe -&gt; tool . live step trace . async (polled)
              </p>
            </div>
          )}

          {/* ---- the live step ledger + filament accent --------------------------- */}
          {status !== "idle" && status !== "error" && (
            <div className="space-y-5">
              {/* filament accent (subtle motion while the loop runs) */}
              <div className="rounded-lg border border-line bg-panel-sunken px-5 py-6">
                <FilamentTrace progress={progress} />
              </div>

              {/* cost / budget meter (degrade-never: hides absent fields) */}
              {run?.cost && <BudgetMeter cost={run.cost} exceeded={budgetExceeded} />}

              {/* the honest multi-step trace */}
              <div>
                <div className="mb-3 flex items-center justify-between">
                  <p className="eyebrow">// step trace</p>
                  <span className="font-mono text-2xs text-text-faint">
                    {(run?.steps_log?.length ?? 0)} step
                    {(run?.steps_log?.length ?? 0) === 1 ? "" : "s"}
                    {running && " . polling"}
                  </span>
                </div>
                <StepLedger steps={run?.steps_log ?? []} running={running} />
              </div>

              {/* an honest banner if the run terminated NOT-ok (budget/refuse/fail) */}
              {terminalNotOk && (
                <div
                  role="alert"
                  className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
                >
                  <span className="mt-0.5 shrink-0">
                    <AlertIcon />
                  </span>
                  <span>
                    {budgetExceeded
                      ? "The run stopped: it crossed its step/token budget ceiling (budget_exceeded)."
                      : runRefused
                        ? "The run was refused before completing (a mid-run guard denied it)."
                        : "The run failed before completing."}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* error path (kickoff/poll failure -- e.g. disabled agent, expired session) */}
          {status === "error" && error && (
            <div
              role="alert"
              className="mt-6 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
            >
              <span className="mt-0.5 shrink-0">
                <AlertIcon />
              </span>
              <span>{error}</span>
            </div>
          )}

          {/* result + tenant scope lock (only on a CLEAN terminal run) */}
          {status === "done" && run && !terminalNotOk && (
            <div className="mt-6">
              <ResultView result={run} />
              <div className="mt-4 flex flex-wrap items-center gap-2 font-mono text-2xs text-text-muted">
                <span className="chip border-synapse/30 text-synapse">
                  &#128274; tenant={tenantLabel || tenantId.slice(0, 8)}
                </span>
                <span className="chip">RLS isolated</span>
                <span className="chip">own credential</span>
                <span className="chip">multi-step</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// The live step ledger -- the REAL steps_log rendered as an ordered list. Each step
// shows its index + kind chip + a readable content view; tool steps add the tool name
// + the tool_io ({args,result}); a HITL-gated step (approval_id set) shows the
// "approval pending" chip (the tool was NOT executed). This is the honest signal.
// ----------------------------------------------------------------------------
function StepLedger({
  steps,
  running,
}: {
  steps: AgentStep[];
  running: boolean;
}) {
  if (steps.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-line bg-panel-sunken px-4 py-6 text-center font-mono text-2xs text-text-faint">
        {running ? "awaiting the first step..." : "no steps recorded"}
      </div>
    );
  }
  return (
    <ol className="space-y-2.5">
      {steps.map((step) => (
        <StepRow key={step.index} step={step} />
      ))}
    </ol>
  );
}

const KIND_STYLE: Record<AgentStepKind, { cls: string; word: string }> = {
  plan: { cls: "border-signal/30 bg-signal/10 text-signal", word: "plan" },
  act: { cls: "border-synapse/30 bg-synapse/10 text-synapse", word: "act" },
  observe: {
    cls: "border-line-strong bg-panel-sunken text-text-muted",
    word: "observe",
  },
  tool: { cls: "border-synapse-deep/40 bg-synapse-deep/10 text-synapse", word: "tool" },
};

function StepRow({ step }: { step: AgentStep }) {
  const kindStyle = KIND_STYLE[step.kind as AgentStepKind] ?? {
    cls: "border-line bg-panel-sunken text-text-muted",
    word: String(step.kind),
  };
  const gated = Boolean(step.approval_id);
  const isTool = step.kind === "tool";
  const io = isTool ? readToolIo(step.tool_io) : null;

  return (
    <li className="rounded-lg border border-line bg-panel px-4 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-2xs text-text-faint">
          #{step.index}
        </span>
        <span
          className={`inline-flex items-center rounded-pill border px-2 py-0.5 font-mono text-2xs uppercase tracking-wider ${kindStyle.cls}`}
        >
          {kindStyle.word}
        </span>
        {isTool && step.tool && (
          <span className="rounded-pill border border-line bg-panel-sunken px-2 py-0.5 font-mono text-2xs text-text-muted">
            {step.tool}
          </span>
        )}
        {gated && (
          <span className="inline-flex items-center gap-1 rounded-pill border border-signal/40 bg-signal/10 px-2 py-0.5 font-mono text-2xs uppercase tracking-wider text-signal">
            &#128274; HITL -- approval pending
          </span>
        )}
      </div>

      {/* readable content view */}
      <div className="mt-2 space-y-1">
        {renderContent(step.content)}
      </div>

      {/* tool I/O (args + result), tool steps only */}
      {io && (
        <div className="mt-2.5 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {io.args !== undefined && (
            <div className="overflow-hidden rounded-md border border-line">
              <p className="border-b border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs uppercase tracking-wider text-text-faint">
                args
              </p>
              <pre className="max-h-32 overflow-auto bg-ink-800 px-2.5 py-2 font-mono text-2xs leading-relaxed text-text-muted">
                {prettyJson(io.args)}
              </pre>
            </div>
          )}
          {io.result !== undefined ? (
            <div className="overflow-hidden rounded-md border border-line">
              <p className="border-b border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs uppercase tracking-wider text-text-faint">
                result
              </p>
              <pre className="max-h-32 overflow-auto bg-ink-800 px-2.5 py-2 font-mono text-2xs leading-relaxed text-text-muted">
                {prettyJson(io.result)}
              </pre>
            </div>
          ) : (
            gated && (
              <div className="grid place-items-center rounded-md border border-dashed border-signal/30 bg-signal/5 px-2.5 py-2 text-center font-mono text-2xs text-signal">
                gated -- not executed
              </div>
            )
          )}
        </div>
      )}
    </li>
  );
}

// ----------------------------------------------------------------------------
// The cost / budget meter -- steps_used vs the ceiling, and tokens_used vs max_tokens
// when present. Degrade-never: a missing optional field simply does not render its bar.
// ----------------------------------------------------------------------------
function BudgetMeter({
  cost,
  exceeded,
}: {
  cost: AgentRunCost;
  exceeded: boolean;
}) {
  const stepCeiling = cost.step_ceiling ?? cost.max_steps ?? undefined;
  const hasTokens =
    typeof cost.tokens_used === "number" &&
    typeof cost.max_tokens === "number" &&
    (cost.max_tokens ?? 0) > 0;

  return (
    <div className="rounded-lg border border-line bg-panel-sunken px-4 py-3">
      <div className="mb-2 flex items-center justify-between">
        <p className="eyebrow">// budget</p>
        {exceeded && (
          <span className="font-mono text-2xs uppercase tracking-wider text-danger">
            ceiling crossed
          </span>
        )}
      </div>
      <div className="space-y-2.5">
        <Meter
          label="steps"
          used={cost.steps_used}
          max={stepCeiling}
          danger={exceeded}
        />
        {hasTokens && (
          <Meter
            label="tokens"
            used={cost.tokens_used as number}
            max={cost.max_tokens as number}
            danger={exceeded}
          />
        )}
      </div>
    </div>
  );
}

function Meter({
  label,
  used,
  max,
  danger,
}: {
  label: string;
  used: number;
  max?: number;
  danger: boolean;
}) {
  const pct =
    typeof max === "number" && max > 0
      ? Math.max(0, Math.min(100, (used / max) * 100))
      : null;
  const tone = danger
    ? "bg-danger"
    : pct !== null && pct >= 85
      ? "bg-signal"
      : "bg-synapse";
  return (
    <div className="flex items-center gap-3">
      <span className="w-12 shrink-0 font-mono text-2xs uppercase tracking-wider text-text-faint">
        {label}
      </span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-line">
        {pct !== null && (
          <div className={`h-full rounded-full ${tone}`} style={{ width: `${pct}%` }} />
        )}
      </div>
      <span className="w-16 shrink-0 text-right font-mono text-2xs text-text-muted">
        {used}
        {typeof max === "number" ? ` / ${max}` : ""}
      </span>
    </div>
  );
}

// ----------------------------------------------------------------------------
// One typed field, rendered from a SchemaField (copied from AgentRunModal -- the
// cockpit is a sibling, not a refactor; keeping it local avoids over-engineering a
// shared module). An enum becomes a <select>; a boolean a true/false select;
// everything else a text input (number gets inputMode numeric).
// ----------------------------------------------------------------------------
function AgentField({
  field,
  value,
  disabled,
  onChange,
}: {
  field: SchemaField;
  value: string;
  disabled: boolean;
  onChange: (v: string) => void;
}) {
  const label = (
    <label
      htmlFor={`cockpit-field-${field.key}`}
      className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
    >
      {field.key}
      <span className="ml-1.5 text-text-faint normal-case">{field.typeLabel}</span>
    </label>
  );

  if (field.kind === "enum" && field.options.length > 0) {
    return (
      <div>
        {label}
        <select
          id={`cockpit-field-${field.key}`}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          className="field disabled:opacity-60"
        >
          <option value="">--</option>
          {field.options.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </div>
    );
  }

  if (field.kind === "boolean") {
    return (
      <div>
        {label}
        <select
          id={`cockpit-field-${field.key}`}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          className="field disabled:opacity-60"
        >
          <option value="">--</option>
          <option value="true">true</option>
          <option value="false">false</option>
        </select>
      </div>
    );
  }

  return (
    <div>
      {label}
      <input
        id={`cockpit-field-${field.key}`}
        type="text"
        inputMode={field.kind === "number" ? "numeric" : "text"}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="field disabled:opacity-60"
        placeholder={field.placeholder}
      />
    </div>
  );
}

// ----------------------------------------------------------------------------
// helpers (pure, total -- never throw on a malformed snapshot)
// ----------------------------------------------------------------------------

/** The filament progress (0..1) from the run's budget, or its ledger length. */
function filamentProgress(run: AgentRun | null): number {
  if (!run) return 0.04;
  if (run.done) return 1;
  const cost = run.cost;
  const ceiling = cost?.step_ceiling ?? cost?.max_steps ?? undefined;
  if (cost && typeof ceiling === "number" && ceiling > 0) {
    return Math.max(0.04, Math.min(0.96, cost.steps_used / ceiling));
  }
  // No ceiling: ramp off the ledger length over a nominal 8-step horizon.
  const n = run.steps_log?.length ?? 0;
  return Math.max(0.04, Math.min(0.96, n / 8));
}

/** A friendly message for a poll error (a 404 means the run aged out of the registry). */
function pollErrorMessage(err: unknown): string {
  if (err instanceof ApiClientError) {
    if (err.status === 404) {
      return "The run is no longer available (it may have completed and aged out, or it is not visible to this tenant).";
    }
    return err.message;
  }
  if (err instanceof Error) return err.message;
  return "Lost contact with the run while polling.";
}

/** Read { args, result } off a tool step's tool_io defensively (the shape is loose). */
function readToolIo(
  io: Record<string, unknown> | undefined,
): { args?: unknown; result?: unknown } | null {
  if (!io || typeof io !== "object") return null;
  const out: { args?: unknown; result?: unknown } = {};
  if ("args" in io) out.args = (io as Record<string, unknown>).args;
  if ("result" in io) out.result = (io as Record<string, unknown>).result;
  // If neither key is present but the object is non-empty, surface it as the result.
  if (out.args === undefined && out.result === undefined) {
    if (Object.keys(io).length > 0) out.result = io;
    else return null;
  }
  return out;
}

/** Pretty-print a JSON value for a <pre>, total (falls back to String on a cycle). */
function prettyJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

/**
 * Render a step's ``content`` map as readable lines. ``content`` is a loose
 * key->value map (string / number / bool / list / nested object); we show each
 * top-level key with a compact value. Total -- never throws on an odd shape.
 */
function renderContent(
  content: Record<string, FieldValue | FieldValue[] | Record<string, unknown>> | undefined,
) {
  if (!content || typeof content !== "object") return null;
  const entries = Object.entries(content);
  if (entries.length === 0) return null;
  return entries.map(([key, val]) => (
    <p key={key} className="text-sm leading-relaxed text-text-muted">
      <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
        {key}
      </span>{" "}
      <span className="text-text">{formatContentValue(val)}</span>
    </p>
  ));
}

/** Format one content value compactly (a list joins with commas; an object inlines). */
function formatContentValue(
  val: FieldValue | FieldValue[] | Record<string, unknown>,
): string {
  if (val === null || val === undefined) return "--";
  if (Array.isArray(val)) {
    return val.map((v) => (v === null ? "--" : String(v))).join(", ");
  }
  if (typeof val === "object") {
    return prettyJson(val);
  }
  return String(val);
}
