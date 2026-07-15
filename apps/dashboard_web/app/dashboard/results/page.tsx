"use client";

// ----------------------------------------------------------------------------
// /dashboard/results -- run history (the tenant's recent artifacts), now with a
// DEEP-LINK to each stored artifact rendered INLINE (spec_dashboard_roadmap W4).
//
// Reads GET /results via ApiClient.listResults() -- fixtures in FIXTURES mode, the
// live tenant-scoped Supabase rows otherwise (the backend resolves tenant_id from
// the verified JWT; RLS is the boundary). Same component in both modes.
//
// THE LEDGER stays: rows are the lightweight {id, capability, kind, created_at,
// +UI score/label/nucleus} shape (lib/types.ResultRow). NEW: a row EXPANDS to
// render its stored artifact inline. The artifact body is fetched on demand as the
// backend's canonical projection -- GET /results?render_format=md|html attaches each
// row's ``render`` (research_universe -> render_universe, product -> marketplace
// render, plain -> canonical MD). We match the expanded row by id and render that.
//
// HONEST DEEP-LINK (backend gap): there is NO single-artifact-by-id GET on the
// backend, and a /results row does NOT carry the raw ``structured`` payload -- only
// the rendered string. So the inline view renders the canonical md/html projection
// (degrade-to-ledger-data), NOT the full per-section UniverseResultView/ResultView
// cards (those need ``structured``, which only the live RUN carries -- see the
// Research view + RunModal for the rich per-section render). A row with no projectable
// body shows an honest "unavailable" note, never a fabricated artifact.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { usePagination } from "@/lib/pagination";
import type { ResultRow } from "@/lib/types";
import { Pagination, ScoreMeter, Spinner } from "@/components/ui";
import { AlertIcon, ArrowRight, HistoryIcon } from "@/components/icons";
import { StoredArtifactView } from "@/components/StoredArtifactView";

// Stable empty fallback so usePagination's source identity does not churn (and
// reset the page) while rows are still null/loading.
const EMPTY_ROWS: ResultRow[] = [];

function timeAgo(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const mins = Math.max(0, Math.round((Date.now() - then) / 60000));
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.round(hrs / 24);
  return `${days}d ago`;
}

export default function ResultsPage() {
  const { session } = useAuth();
  const [rows, setRows] = useState<ResultRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string | null>(null);
  // which row is expanded (its stored artifact rendered inline). One at a time.
  const [openId, setOpenId] = useState<string | null>(null);

  const token = session?.access_token ?? "";

  // Per-(capability, format) cache of the rendered rows from GET /results?render_format=.
  // The deep-link fetch resolves ONE row's projection by re-using the per-capability
  // rendered fetch and matching on id -- so opening N rows of one capability is ONE call.
  const renderCache = useRef<Map<string, Promise<ResultRow[]>>>(new Map());

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const list = await new ApiClient(token).listResults(filter ?? undefined);
      setRows(list);
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load results.";
      setError(msg);
      setRows([]);
    }
  }, [token, filter]);

  useEffect(() => {
    load();
    // a fresh load invalidates the render cache + collapses any open row
    renderCache.current.clear();
    setOpenId(null);
  }, [load]);

  /**
   * Resolve ONE stored row's canonical projection (md|html). Calls GET
   * /results?capability=<cap>&render_format=<fmt> (cached per capability+format) and
   * returns the matching row's ``render``. Honest '': a row the backend did not
   * project (or a backend that returned no render) yields an empty string, which the
   * inline view surfaces as "projection unavailable". tenant_id stays server-derived.
   */
  const fetchRowRender = useCallback(
    async (row: ResultRow, format: "md" | "html"): Promise<string> => {
      const key = `${row.capability}::${format}`;
      let pending = renderCache.current.get(key);
      if (!pending) {
        pending = new ApiClient(token).listResults(row.capability, format);
        renderCache.current.set(key, pending);
      }
      try {
        const rendered = await pending;
        const match = rendered.find((r) => r.id === row.id);
        return match?.render ?? "";
      } catch {
        // a failed render fetch must not throw into the row -- degrade to empty.
        renderCache.current.delete(key);
        return "";
      }
    },
    [token],
  );

  // Capability filter chips, derived from the loaded history.
  const capabilities = useMemo(() => {
    const set = new Set<string>();
    (rows ?? []).forEach((r) => set.add(r.capability));
    // When a filter is active the server already narrowed rows, so keep the
    // active one visible regardless.
    if (filter) set.add(filter);
    return Array.from(set).sort();
  }, [rows, filter]);

  // Client-side window over the loaded ledger (the fetch is already server-capped;
  // this bounds the rendered DOM + scan cost). A fresh load / filter switch resets
  // to page 1. Single-page result sets render the control as nothing (degrade-never).
  const pager = usePagination(rows ?? EMPTY_ROWS, 25);

  const tenantLabel = session?.tenant_label || "Tenant";

  return (
    <div className="mx-auto max-w-5xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Run history</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Results
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Recent artifacts produced for your tenant. Stored in your own data
            plane, scoped by RLS. Expand a row to read its stored artifact inline.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          {config.fixtures ? "fixtures" : "live"} . tenant_data
        </div>
      </header>

      {/* ---- filter chips ------------------------------------------------ */}
      {capabilities.length > 0 && (
        <div className="mt-6 flex flex-wrap items-center gap-2">
          <button
            onClick={() => setFilter(null)}
            className={[
              "rounded-pill border px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              filter === null
                ? "border-synapse/40 bg-synapse/10 text-synapse"
                : "border-line bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            all
          </button>
          {capabilities.map((cap) => (
            <button
              key={cap}
              onClick={() => setFilter(cap)}
              className={[
                "rounded-pill border px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
                filter === cap
                  ? "border-synapse/40 bg-synapse/10 text-synapse"
                  : "border-line bg-panel-sunken text-text-muted hover:text-text",
              ].join(" ")}
            >
              {cap}
            </button>
          ))}
        </div>
      )}

      {error && (
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

      {/* ---- the ledger -------------------------------------------------- */}
      <div className="mt-6">
        {rows === null ? (
          <div className="flex items-center gap-3 py-16 text-text-muted">
            <Spinner />
            <span className="font-mono text-2xs uppercase tracking-wider">
              loading history
            </span>
          </div>
        ) : rows.length === 0 && !error ? (
          <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
            <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
              <HistoryIcon />
            </span>
            <p className="font-display text-lg text-text">No runs yet</p>
            <p className="mt-1 text-sm">
              Run a capability from the console and it will appear here.
            </p>
          </div>
        ) : (
          <>
          <div className="overflow-hidden rounded-card border border-line">
            {/* header row */}
            <div className="hidden grid-cols-[1.4fr_1fr_0.8fr_0.8fr_2rem] gap-4 border-b border-line bg-panel-sunken px-5 py-2.5 font-mono text-2xs uppercase tracking-wider text-text-faint sm:grid">
              <span>Capability</span>
              <span>Kind</span>
              <span>Score</span>
              <span className="text-right">When</span>
              <span />
            </div>
            <ul>
              {pager.items.map((r, i) => {
                const open = openId === r.id;
                return (
                  <li
                    key={r.id}
                    style={{ animationDelay: `${i * 35}ms` }}
                    className="animate-rise-in border-b border-line last:border-b-0"
                  >
                    {/* the ledger row -- now a deep-link toggle */}
                    <button
                      type="button"
                      onClick={() => setOpenId(open ? null : r.id)}
                      aria-expanded={open}
                      className={[
                        "grid w-full grid-cols-1 items-center gap-2 px-5 py-3.5 text-left transition-colors sm:grid-cols-[1.4fr_1fr_0.8fr_0.8fr_2rem] sm:gap-4",
                        open ? "bg-panel-sunken" : "bg-panel hover:bg-panel-sunken/60",
                      ].join(" ")}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="chip">{r.nucleus ?? "N0?"}</span>
                        <span className="font-display text-sm font-600 text-text">
                          {r.label ?? r.capability}
                        </span>
                      </div>
                      <span className="font-mono text-2xs text-text-faint">
                        {r.kind ?? "--"}
                      </span>
                      <span>
                        {typeof r.score === "number" ? (
                          <ScoreMeter score={r.score} />
                        ) : (
                          <span className="font-mono text-2xs text-text-faint">--</span>
                        )}
                      </span>
                      <span className="font-mono text-2xs text-text-muted sm:text-right">
                        {timeAgo(r.created_at)}
                      </span>
                      <span
                        className={[
                          "hidden text-text-faint transition-transform sm:inline-flex sm:justify-end",
                          open ? "rotate-90 text-synapse" : "",
                        ].join(" ")}
                        aria-hidden
                      >
                        <ArrowRight />
                      </span>
                    </button>

                    {/* the inline-rendered stored artifact (the deep-link target) */}
                    {open && (
                      <div className="border-t border-line bg-ink-800/40 px-5 py-4">
                        <StoredArtifactView
                          recordId={r.id}
                          onFetchRender={(format) => fetchRowRender(r, format)}
                        />
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
          <Pagination
            page={pager.page}
            pageCount={pager.pageCount}
            total={pager.total}
            start={pager.start}
            end={pager.end}
            canPrev={pager.canPrev}
            canNext={pager.canNext}
            onPrev={pager.prev}
            onNext={pager.next}
            unit="results"
          />
          </>
        )}
      </div>
    </div>
  );
}
