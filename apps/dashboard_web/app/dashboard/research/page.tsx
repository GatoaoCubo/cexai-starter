"use client";

// ----------------------------------------------------------------------------
// /dashboard/research -- the Research Universe HERO flow (spec_dashboard_roadmap W4).
//
//   seed (product / brand / CNPJ) [+ optional lane selection]
//        -> run the ``research_universe`` capability (8F filament fires live)
//        -> render the multi-source report via UniverseResultView (per ResultView)
//
// REUSES the W1 run plumbing verbatim:
//   * ApiClient.runCapability("research_universe", seed, options) -- SYNCHRONOUS, the
//     run completes in one call (no run_id/poll), exactly like RunModal.
//   * the client-side FilamentTrace ramp around that one request (fixtures poll the
//     mock's true elapsed fraction; live ramps a synthetic estimate, snaps to 1 on
//     resolve) -- the SAME device RunModal uses.
//   * ResultView -> UniverseResultView (the universe discriminator wins) renders the
//     per-section cards + honest blocked/skipped states (never fabricated) + the
//     md/html ?render_format toggle.
//
// Works in FIXTURES (offline-demoable -- buildUniverseResult) AND live (the backend
// research_universe orchestrator). tenant_id is read from the session as provenance
// only; the client never sends it (the backend derives it from the JWT).
//
// OPTIONAL LANES: the lane chips are an ADDITIVE hint passed as options.lanes. The
// orchestrator is registry-driven (select_lanes); an empty selection = "all relevant
// lanes for the seed" (the default routing), and a backend that ignores the hint is a
// harmless no-op -- never a fabricated narrowing.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { fxFetchResultRender, fxRunProgress } from "@/lib/fixtures";
import type { CapabilityResultView, RunStatus } from "@/lib/types";
import { FilamentTrace } from "@/components/FilamentTrace";
import { ResultView } from "@/components/ResultView";
import { StatusBadge } from "@/components/ui";
import { AlertIcon, ArrowRight, ResearchIcon } from "@/components/icons";

// The research_universe capability id (resolved by the backend/overlay + present in
// FIXTURE_CARDS). The hero flow IS this one capability.
const UNIVERSE_CAPABILITY = "research_universe";

// Synthetic ramp for LIVE mode (no server progress signal) -- mirrors RunModal.
const LIVE_RAMP_MS = 9000;

// The selectable research lanes (an OPTIONAL hint -> options.lanes). Labels are the
// orchestrator's lane keys, humanized; the seed-routing decides which actually run,
// so this is a narrowing hint, never a guarantee. Mirrors the lanes the universe
// report surfaces (endpoint_status keys).
const LANES: { key: string; label: string; hint: string }[] = [
  { key: "seo", label: "SEO", hint: "autocomplete keywords" },
  { key: "questions", label: "Questions", hint: "multi-perspective" },
  { key: "youtube", label: "YouTube", hint: "video signals" },
  { key: "reddit", label: "Reddit", hint: "community threads" },
  { key: "reclame_aqui", label: "Reclame Aqui", hint: "reputation" },
  { key: "appstore", label: "App Store", hint: "app reviews" },
  { key: "cnpj", label: "CNPJ", hint: "firmographics" },
  { key: "ibge", label: "IBGE", hint: "market sizing" },
];

export default function ResearchPage() {
  const { session } = useAuth();
  const [seed, setSeed] = useState("");
  const [lanes, setLanes] = useState<string[]>([]);
  const [status, setStatus] = useState<RunStatus | "idle">("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<CapabilityResultView | null>(null);
  const [error, setError] = useState<string | null>(null);

  const raf = useRef<number | null>(null);
  const liveStart = useRef<number>(0);

  const token = session?.access_token ?? "";
  const tenantLabel = session?.tenant_label || "Tenant";
  const running = status === "running";

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

  function toggleLane(key: string) {
    setLanes((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
    );
  }

  const run = useCallback(async () => {
    const trimmed = seed.trim();
    if (!trimmed || running) return;
    setStatus("running");
    setError(null);
    setResult(null);
    setProgress(0.02);
    liveStart.current = Date.now();
    raf.current = requestAnimationFrame(tick);

    try {
      const client = new ApiClient(token);
      // OPTIONAL lane hint -> options.lanes (additive; empty = default routing).
      const options = lanes.length > 0 ? { lanes } : undefined;
      const view = await client.runCapability(UNIVERSE_CAPABILITY, trimmed, options);
      if (raf.current !== null) cancelAnimationFrame(raf.current);
      setProgress(1);
      setResult(view);
      setStatus("done");
    } catch (err) {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
      setStatus("error");
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "The research run could not be completed.";
      setError(msg);
    }
  }, [seed, lanes, running, token, tick]);

  function reset() {
    setStatus("idle");
    setProgress(0);
    setResult(null);
    setError(null);
  }

  return (
    <div className="mx-auto max-w-4xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Research console</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Research Universe
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            One seed -- a product, a brand, or a CNPJ -- opens the relevant research
            lanes and assembles a multi-source report, with an honest status per
            source. Nothing is fabricated: a blocked or skipped lane says so.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          8F=ready . {config.fixtures ? "fixtures" : "live"} . research_universe
        </div>
      </header>

      {/* ---- the seed box + lane selection ------------------------------- */}
      <div className="mt-7 panel px-5 py-5 sm:px-6 sm:py-6">
        <div className="flex items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-lg border border-line bg-panel-sunken text-synapse">
            <ResearchIcon width={18} height={18} />
          </span>
          <div>
            <h2 className="font-display text-lg font-600 tracking-tight text-text">
              What do you want researched?
            </h2>
            <p className="font-mono text-2xs text-text-faint">
              seed -&gt; lane routing -&gt; multi-source report
            </p>
          </div>
        </div>

        <label
          htmlFor="research-seed"
          className="mb-1.5 mt-5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
        >
          Pesquisar (produto / marca / CNPJ)
        </label>
        <textarea
          id="research-seed"
          value={seed}
          onChange={(e) => setSeed(e.target.value)}
          disabled={running}
          rows={2}
          className="field resize-none disabled:opacity-60"
          placeholder="ex.: comedouro gato automatico -- ou uma marca, ou um CNPJ"
        />

        {/* optional lane selection */}
        <div className="mt-5">
          <div className="mb-2 flex items-center justify-between gap-3">
            <p className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              Lanes (opcional)
            </p>
            {lanes.length > 0 && (
              <button
                onClick={() => setLanes([])}
                disabled={running}
                className="font-mono text-2xs uppercase tracking-wider text-text-faint transition-colors hover:text-synapse disabled:opacity-40"
              >
                limpar ({lanes.length})
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {LANES.map((lane) => {
              const on = lanes.includes(lane.key);
              return (
                <button
                  key={lane.key}
                  type="button"
                  onClick={() => toggleLane(lane.key)}
                  disabled={running}
                  title={lane.hint}
                  className={[
                    "rounded-pill border px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors disabled:opacity-40",
                    on
                      ? "border-synapse/40 bg-synapse/10 text-synapse"
                      : "border-line bg-panel-sunken text-text-muted hover:text-text",
                  ].join(" ")}
                >
                  {lane.label}
                </button>
              );
            })}
          </div>
          <p className="mt-2 font-mono text-2xs text-text-faint">
            {lanes.length === 0
              ? "vazio = todas as lanes relevantes para o seed (roteamento padrao)."
              : "dica de narrowing -- o roteamento por seed decide o que de fato roda."}
          </p>
        </div>

        {status !== "done" ? (
          <button
            onClick={run}
            disabled={running || seed.trim().length === 0}
            className="btn-primary mt-5 w-full"
          >
            {running ? "Pesquisando..." : "Rodar Research Universe"}
            {!running && <ArrowRight />}
          </button>
        ) : (
          <button onClick={reset} className="btn-ghost mt-5 w-full">
            Nova pesquisa
          </button>
        )}

        {/* status badge */}
        {status !== "idle" && (
          <div className="mt-4 flex items-center gap-2">
            <StatusBadge status={status as RunStatus} />
            {result && (
              <span className="font-mono text-2xs text-text-faint">
                seed={result.capability}
              </span>
            )}
          </div>
        )}

        {/* the 8F filament -- the signature motion moment (mirrors RunModal) */}
        {status !== "idle" && status !== "error" && (
          <div className="mt-5 rounded-lg border border-line bg-panel-sunken px-5 py-6">
            <FilamentTrace progress={progress} />
          </div>
        )}
      </div>

      {/* ---- error path -------------------------------------------------- */}
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

      {/* ---- the multi-source report (UniverseResultView via ResultView) - */}
      {status === "done" && result && (
        <div className="mt-7">
          <ResultView
            result={result}
            // research_universe raw md/html projection (render_universe). In live mode
            // it stays undefined -> UniverseResultView falls back to the render the
            // backend attached (?render_format) else an honest "unavailable" note. A
            // live wire would re-POST /capability/run?render_format=<fmt>. MIRRORS RunModal.
            onFetchRender={
              config.fixtures
                ? (format) => fxFetchResultRender(result, format)
                : undefined
            }
          />
          <div className="mt-4 flex flex-wrap items-center gap-2 font-mono text-2xs text-text-muted">
            <span className="chip border-synapse/30 text-synapse">
              &#128274; tenant={tenantLabel}
            </span>
            <span className="chip">RLS isolated</span>
            <span className="chip">own credential</span>
            <span className="chip">0 cross-tenant</span>
          </div>
        </div>
      )}
    </div>
  );
}
