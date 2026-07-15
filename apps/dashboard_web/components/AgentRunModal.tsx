"use client";

// ----------------------------------------------------------------------------
// The AGENT run cockpit, as a modal overlay (ADR adr_agents_sdk_dashboard, Phase B).
//
//   agent -> [typed form from Input Schema] -> Run -> 8F filament -> ResultView
//
// CLONES RunModal (the capability run flow) and reuses FilamentTrace + ResultView
// verbatim. The ONE difference: instead of a single free-text intent box, it renders
// a TYPED FORM derived from the agent's Input Schema (one field per schema key).
// An agent with NO Input Schema falls back to a single free-text intent box -- which
// is sent as { intent: "..." } (the run_agent free-text contract).
//
// The backend run is SYNCHRONOUS (POST /agent/run returns the full AgentRunResultView
// in one call -- single step, no run_id/poll). The filament is driven client-side
// around that one request, exactly as RunModal does. tenant_id is never set here;
// the scope chips show the SESSION tenant as provenance.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { config } from "@/lib/config";
import { fxRunProgress } from "@/lib/fixtures";
import {
  parseSchemaFields,
  coerceFieldValue,
  type SchemaField,
} from "@/lib/agentSchema";
import type { AgentDetail, AgentRunResultView, RunStatus } from "@/lib/types";
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

// Synthetic ramp for LIVE mode (no server progress signal). Mirrors RunModal.
const LIVE_RAMP_MS = 9000;

export function AgentRunModal({
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
  const [status, setStatus] = useState<RunStatus | "idle">("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<AgentRunResultView | null>(null);
  const [error, setError] = useState<string | null>(null);

  const raf = useRef<number | null>(null);
  const liveStart = useRef<number>(0);

  // Reset whenever a new agent opens (or it closes).
  useEffect(() => {
    setStatus("idle");
    setProgress(0);
    setResult(null);
    setError(null);
    setValues({});
    setIntent(agent?.goal ?? "");
  }, [agent]);

  // Close on Escape.
  useEffect(() => {
    if (!agent) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [agent, onClose]);

  // Stop the progress loop on unmount.
  useEffect(() => {
    return () => {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, []);

  const tick = useCallback(() => {
    let next: number;
    if (config.fixtures) {
      next = fxRunProgress();
    } else {
      const elapsed = Date.now() - liveStart.current;
      next = Math.min(0.92, elapsed / LIVE_RAMP_MS);
    }
    setProgress(next);
    if (next < 1) {
      raf.current = requestAnimationFrame(tick);
    }
  }, []);

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

  async function run() {
    if (!agent || status === "running") return;
    setStatus("running");
    setError(null);
    setResult(null);
    setProgress(0.02);
    liveStart.current = Date.now();
    raf.current = requestAnimationFrame(tick);

    try {
      const client = new ApiClient(accessToken);
      const view = await client.runAgent(agent.id, buildInputs());
      if (raf.current !== null) cancelAnimationFrame(raf.current);
      setProgress(1);
      setResult(view);
      setStatus("done");
      onComplete?.();
    } catch (err) {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
      setStatus("error");
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "The agent run could not be completed.";
      setError(msg);
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

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label={`Run ${agent.name}`}
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
            {!agent.enabled && <span className="chip">disabled</span>}
            {status !== "idle" && <StatusBadge status={status as RunStatus} />}
          </div>
          <p className="mt-2 font-mono text-2xs text-text-faint">{sig}</p>
        </div>

        <div className="px-6 py-5">
          {/* ---- the typed form (from the Input Schema), or the free-text fallback --- */}
          {status !== "done" && (
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
                    htmlFor="agent-intent"
                    className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
                  >
                    Intent
                  </label>
                  <textarea
                    id="agent-intent"
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
                onClick={run}
                disabled={running}
                className="btn-primary mt-2 w-full"
              >
                {running ? "Running agent..." : "Run agent"}
                {!running && <ArrowRight />}
              </button>

              {/* single-step honesty note */}
              <p className="text-center font-mono text-2xs text-text-faint">
                single step . one pass . tool loop + async land in Phase C
              </p>
            </div>
          )}

          {/* the 8F filament -- the signature motion moment (reused verbatim) */}
          {status !== "idle" && status !== "error" && (
            <div className="mt-7 rounded-lg border border-line bg-panel-sunken px-5 py-6">
              <FilamentTrace progress={progress} />
            </div>
          )}

          {/* error path (e.g. disabled agent -> capability_disabled) */}
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

          {/* result + tenant scope lock (reused verbatim from RunModal) */}
          {status === "done" && result && (
            <div className="mt-6">
              <ResultView result={result} />
              <div className="mt-4 flex flex-wrap items-center gap-2 font-mono text-2xs text-text-muted">
                <span className="chip border-synapse/30 text-synapse">
                  &#128274; tenant={tenantLabel || tenantId.slice(0, 8)}
                </span>
                <span className="chip">RLS isolated</span>
                <span className="chip">own credential</span>
                <span className="chip">single step</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// One typed field, rendered from a SchemaField. An enum (a|b|c) becomes a <select>;
// a boolean a checkbox; everything else a text input (number gets inputMode numeric).
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
      htmlFor={`agent-field-${field.key}`}
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
          id={`agent-field-${field.key}`}
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
          id={`agent-field-${field.key}`}
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
        id={`agent-field-${field.key}`}
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
