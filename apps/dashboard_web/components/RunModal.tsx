"use client";

// ----------------------------------------------------------------------------
// The run flow, as a modal overlay (mirrors public/showcase.html's run overlay).
//
//   card -> [intent] -> Run -> 8F filament fires live -> ResultView + scope lock
//
// The backend run is SYNCHRONOUS (POST /capability/run returns the full result in
// one call -- see lib/api.ts). The filament is driven CLIENT-SIDE around that one
// request:
//   * FIXTURES: poll lib/fixtures.fxRunProgress() -- the mock run reports a true
//     elapsed fraction over RUN_DURATION_MS, so the 8 nodes fire on real timing.
//   * LIVE: there is no server progress signal, so we ramp a synthetic estimate
//     and SNAP to 1.0 the moment the network promise resolves.
//
// tenant_id is never set here; the scope chips show the SESSION tenant (read once
// in lib/auth) as provenance -- the same "lock" device the showcase mock uses.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { config } from "@/lib/config";
import {
  fxChainToAds,
  fxFetchResultMd,
  fxFetchResultRender,
  fxRunProgress,
} from "@/lib/fixtures";
import {
  contractFields,
  coerceContractValue,
  type ContractField,
} from "@/lib/inputContract";
import type { Card, CapabilityResultView, RunStatus } from "@/lib/types";
import { FilamentTrace } from "./FilamentTrace";
import { ResultView } from "./ResultView";
import { ExportAgentButton } from "./ExportAgentButton";
import { StatusBadge } from "./ui";
import { AlertIcon, ArrowRight } from "./icons";

interface Props {
  card: Card | null;
  /** the session's verified tenant (provenance only; never sent to the backend). */
  tenantId: string;
  tenantLabel?: string;
  /** Bearer for live backend calls (lib/api). Ignored in fixtures mode. */
  accessToken: string;
  onClose: () => void;
  /** fired after a successful run so the parent can refresh history. */
  onComplete?: () => void;
}

// Synthetic ramp for LIVE mode (no server progress signal). Approaches ~0.92 and
// holds until the real promise resolves, then the caller snaps it to 1.
const LIVE_RAMP_MS = 9000;

export function RunModal({
  card,
  tenantId,
  tenantLabel,
  accessToken,
  onClose,
  onComplete,
}: Props) {
  // The typed fields from the card's input_contract (mission BRANDBOOK, Cell A); [] -> the
  // free-text intent fallback (degrade-never). Mirrors AgentRunModal's parseSchemaFields.
  const fields = useMemo<ContractField[]>(
    () => contractFields(card?.input_contract),
    [card],
  );
  const hasContract = fields.length > 0;

  const [intent, setIntent] = useState("");
  // One value per typed field (string-backed; coerced at submit; a file holds its data: URI).
  const [values, setValues] = useState<Record<string, string>>({});
  // Per-field validation note (e.g. a too-large upload); cleared on a new pick.
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<RunStatus | "idle">("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<CapabilityResultView | null>(null);
  const [error, setError] = useState<string | null>(null);

  const raf = useRef<number | null>(null);
  const liveStart = useRef<number>(0);

  // Reset the modal whenever a new card opens (or it closes).
  useEffect(() => {
    setStatus("idle");
    setProgress(0);
    setResult(null);
    setError(null);
    setIntent(card?.default_intent_hint ?? "");
    setValues({});
    setFieldErrors({});
  }, [card]);

  // Close on Escape.
  useEffect(() => {
    if (!card) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [card, onClose]);

  // Stop the progress loop on unmount.
  useEffect(() => {
    return () => {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, []);

  const tick = useCallback(() => {
    // FIXTURES: trust the mock's true elapsed fraction. LIVE: synthetic ramp.
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

  // Assemble the typed inputs payload from the form (omit empties; coerce numbers). A file
  // field holds its data: URI; the backend resolver turns an image into a palette and a doc
  // into text. Mirrors AgentRunModal.buildInputs.
  const buildInputs = useCallback((): Record<string, unknown> => {
    const out: Record<string, unknown> = {};
    for (const f of fields) {
      const raw = values[f.key];
      if (raw === undefined || raw === "") continue; // omit empties
      out[f.key] = coerceContractValue(raw, f);
    }
    return out;
  }, [fields, values]);

  async function run() {
    if (!card || status === "running") return;
    setStatus("running");
    setError(null);
    setResult(null);
    setProgress(0.02);
    liveStart.current = Date.now();
    raf.current = requestAnimationFrame(tick);

    try {
      const client = new ApiClient(accessToken);
      // With a contract: the user's signal is the typed inputs; ``intent`` is the seed/fallback
      // the backend requires (min_length 1). Without one: the classic free-text intent.
      const inputs = hasContract ? buildInputs() : undefined;
      const intentToSend = hasContract
        ? card.default_intent_hint || card.label
        : intent.trim() || card.default_intent_hint || card.label;
      const view = await client.runCapability(
        card.capability,
        intentToSend,
        undefined,
        inputs,
      );
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
            : "The run could not be completed.";
      setError(msg);
    }
  }

  if (!card) return null;

  const sig = [
    card.kind ? `kind=${card.kind}` : null,
    card.pillar ?? null,
    `nucleus ${card.nucleus}`,
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
      aria-label={`Run ${card.label}`}
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
              {card.label}
            </h2>
            {card.source === "overlay" && (
              <span className="chip border-synapse/30 text-synapse">overlay</span>
            )}
            {status !== "idle" && <StatusBadge status={status as RunStatus} />}
          </div>
          <p className="mt-2 font-mono text-2xs text-text-faint">{sig}</p>
          {/* Export this capability as a portable agent package (GPT Builder / Claude / MCP).
              Independent of the run flow -- exports the agent DEFINITION. Dev-gated UI. */}
          <ExportAgentButton
            tenant={config.activeTenant || tenantId}
            capability={card.capability}
            disabled={running}
          />
        </div>

        <div className="px-6 py-5">
          {/* the typed form (from input_contract), or the free-text intent fallback */}
          {hasContract ? (
            <div>
              <p className="mb-3 font-mono text-2xs uppercase tracking-wider text-text-muted">
                // typed inputs (input contract)
              </p>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {fields.map((f) => (
                  <ContractFieldInput
                    key={f.key}
                    field={f}
                    value={values[f.key] ?? ""}
                    error={fieldErrors[f.key]}
                    disabled={running || status === "done"}
                    onChange={(v) =>
                      setValues((prev) => ({ ...prev, [f.key]: v }))
                    }
                    onError={(msg) =>
                      setFieldErrors((prev) => ({ ...prev, [f.key]: msg }))
                    }
                  />
                ))}
              </div>
            </div>
          ) : (
            <>
              <label
                htmlFor="run-intent"
                className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
              >
                Intent
              </label>
              <textarea
                id="run-intent"
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                disabled={running || status === "done"}
                rows={2}
                className="field resize-none disabled:opacity-60"
                placeholder={card.default_intent_hint || "Describe what you want."}
              />
            </>
          )}

          {status !== "done" && (
            <button
              onClick={run}
              disabled={running}
              className="btn-primary mt-4 w-full"
            >
              {running ? "Running pipeline..." : "Run capability"}
              {!running && <ArrowRight />}
            </button>
          )}

          {/* the 8F filament -- the signature motion moment */}
          {status !== "idle" && status !== "error" && (
            <div className="mt-7 rounded-lg border border-line bg-panel-sunken px-5 py-6">
              <FilamentTrace progress={progress} />
            </div>
          )}

          {/* error path (e.g. disabled capability -> capability_disabled) */}
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

          {/* result + tenant scope lock */}
          {status === "done" && result && (
            <div className="mt-6">
              <ResultView
                result={result}
                // The research->ads chain + canonical-MD fetch are wired in
                // FIXTURES mode (the chain is a pipeline, not one endpoint). In live
                // mode they stay undefined -> ResearchResultView shows the chain CTA
                // as a disabled, honest next-step affordance.
                onChainToAds={
                  config.fixtures ? () => fxChainToAds(result) : undefined
                }
                onFetchMd={
                  config.fixtures ? () => fxFetchResultMd(result) : undefined
                }
                // research_universe raw md/html projection (render_universe). In live
                // mode it stays undefined -> UniverseResultView falls back to the
                // render the backend already attached (?render_format), else an honest
                // "projection unavailable" note. A live wire would re-POST
                // /capability/run?render_format=<fmt> and read response.render.
                onFetchRender={
                  config.fixtures
                    ? (format) => fxFetchResultRender(result, format)
                    : undefined
                }
                // The upload-persist wire: a human upload into a dual-output media slot is
                // stored + persisted tenant-scoped. Mode-transparent -- ApiClient.uploadSlotMedia
                // resolves fixtures offline. Wired only when the run actually persisted a row.
                onUploadMedia={
                  result.record_id
                    ? (slotKey, file) =>
                        new ApiClient(accessToken).uploadSlotMedia(
                          result.record_id as string,
                          slotKey,
                          file,
                        )
                    : undefined
                }
              />
              <div className="mt-4 flex flex-wrap items-center gap-2 font-mono text-2xs text-text-muted">
                <span className="chip border-synapse/30 text-synapse">
                  &#128274; tenant={tenantLabel || tenantId.slice(0, 8)}
                </span>
                <span className="chip">RLS isolated</span>
                <span className="chip">own credential</span>
                <span className="chip">0 cross-tenant</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// One typed field from a capability's input_contract (mission BRANDBOOK, Cell A). The
// control kind drives the widget:
//   file   -> an <input type=file>; the pick is read to a data: URI (the upload shape the
//             backend resolver parses -> an image becomes a palette, a doc becomes text).
//   url    -> a URL input; the backend FETCHES it -> text.
//   text   -> a multi-line textarea (the guided free description / a comma-joined list).
//   enum   -> a <select> of the declared options.
//   boolean-> a true/false select.
//   number/string -> a (numeric) text input.
// Mirrors AgentRunModal's AgentField, plus the file/url/textarea ingest controls.
// ----------------------------------------------------------------------------
const MAX_UPLOAD_BYTES = 4 * 1024 * 1024; // mirror cex_media_store's default 4 MiB cap

function ContractFieldInput({
  field,
  value,
  error,
  disabled,
  onChange,
  onError,
}: {
  field: ContractField;
  value: string;
  error?: string;
  disabled: boolean;
  onChange: (v: string) => void;
  onError: (msg: string) => void;
}) {
  const id = `run-field-${field.key}`;
  const label = (
    <label
      htmlFor={id}
      className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
    >
      {field.label}
      {field.required && <span className="ml-1 text-danger">*</span>}
      <span className="ml-1.5 normal-case text-text-faint">{field.typeLabel}</span>
    </label>
  );

  // file: read the pick to a data: URI (the upload shape the backend resolver parses).
  if (field.control === "file") {
    const picked = value.startsWith("data:");
    const isImage = value.startsWith("data:image");
    const onPick = (file: File | undefined) => {
      onError("");
      if (!file) {
        onChange("");
        return;
      }
      if (file.size > MAX_UPLOAD_BYTES) {
        onError(
          `arquivo muito grande (${Math.round(file.size / 1024)} KB; limite ${Math.round(
            MAX_UPLOAD_BYTES / 1024,
          )} KB)`,
        );
        return;
      }
      const reader = new FileReader();
      reader.onload = () => onChange(String(reader.result || ""));
      reader.onerror = () => onError("falha ao ler o arquivo");
      reader.readAsDataURL(file);
    };
    return (
      <div className="sm:col-span-2">
        {label}
        <input
          id={id}
          type="file"
          accept={field.accept || undefined}
          disabled={disabled}
          onChange={(e) => onPick(e.target.files?.[0])}
          className="block w-full text-2xs text-text-muted file:mr-3 file:rounded-md file:border file:border-line file:bg-panel-sunken file:px-3 file:py-1.5 file:text-text file:transition-colors hover:file:border-line-strong disabled:opacity-60"
        />
        {picked && (
          <p className="mt-1.5 font-mono text-2xs text-synapse">
            {isImage
              ? "imagem selecionada -- paleta de cores extraida no servidor"
              : "arquivo selecionado -- texto extraido no servidor"}
            <button
              type="button"
              onClick={() => onChange("")}
              disabled={disabled}
              className="ml-2 text-text-faint underline hover:text-text disabled:opacity-60"
            >
              remover
            </button>
          </p>
        )}
        {field.note && !picked && (
          <p className="mt-1.5 font-mono text-2xs text-text-faint">{field.note}</p>
        )}
        {error && <p className="mt-1.5 font-mono text-2xs text-danger">{error}</p>}
      </div>
    );
  }

  if (field.control === "textarea") {
    return (
      <div className="sm:col-span-2">
        {label}
        <textarea
          id={id}
          value={value}
          disabled={disabled}
          rows={2}
          onChange={(e) => onChange(e.target.value)}
          className="field resize-none disabled:opacity-60"
          placeholder={field.placeholder}
        />
        {field.note && (
          <p className="mt-1.5 font-mono text-2xs text-text-faint">{field.note}</p>
        )}
      </div>
    );
  }

  if (field.control === "enum" && field.options.length > 0) {
    return (
      <div>
        {label}
        <select
          id={id}
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

  if (field.control === "boolean") {
    return (
      <div>
        {label}
        <select
          id={id}
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

  // text / url / number -> a (typed) single-line input.
  return (
    <div>
      {label}
      <input
        id={id}
        type={field.control === "url" ? "url" : "text"}
        inputMode={field.control === "number" ? "numeric" : "text"}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="field disabled:opacity-60"
        placeholder={field.placeholder}
      />
      {field.note && (
        <p className="mt-1.5 font-mono text-2xs text-text-faint">{field.note}</p>
      )}
    </div>
  );
}
