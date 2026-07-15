"use client";

// ----------------------------------------------------------------------------
// /dashboard/waitlist -- the GO_ONLINE A2 lead queue view (spec 23, FR-003).
//
// FRONTEND-ONLY today: waitlist_intake (supabase/migrations/20260711000001_
// waitlist_intake.sql) is anon INSERT-only / readable ONLY by the privileged
// service-role Postgres role. This app is a PURE CLIENT (next.config.mjs's
// own CSP comment) -- it cannot legally hold a service-role key, so there is
// NO live backend route yet (apps/dashboard_api/* is explicitly out of this
// lane's fence -- see the PROPOSAL comment on ApiClient.listWaitlist(),
// lib/api.ts).
// ApiClient.listWaitlist() therefore always rejects in LIVE mode; this page
// catches that and renders an HONEST pending state, never a broken page.
// FIXTURES mode (the local default) instead resolves cleanly to an empty
// list -- no fixture rows are fabricated for a table with no live reader yet
// -- so the local dev/manual check renders the "No signups yet" empty state.
//
// Sortable by wtp_band (the spec's own ask -- "founder sees the queue
// sortable by wtp_band"): a client-side toggle. It has nothing to sort
// against yet (no live rows), but the sort itself is real and will work the
// moment listWaitlist() is backed by a real reader -- nothing here is a stub
// that needs rewriting later.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError, type WaitlistRow } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { Spinner } from "@/components/ui";
import { AlertIcon, TableIcon } from "@/components/icons";

type SortKey = "wtp_band" | "created_at";

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

export default function WaitlistPage() {
  const { session } = useAuth();
  const [rows, setRows] = useState<WaitlistRow[] | null>(null);
  // Honest "not wired up yet" state -- DISTINCT from `error` (an unexpected
  // failure). Pending is the EXPECTED state today (no backend route exists).
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("wtp_band");

  const token = session && session.access_token ? session.access_token : "";

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    setPending(false);
    try {
      const list = await new ApiClient(token).listWaitlist();
      setRows(list);
    } catch (err) {
      // A missing/unset API URL (status 0) or a 404 both mean "no /waitlist
      // route exists yet" in LIVE mode -- the EXPECTED pre-integration shape,
      // not a broken page. Any OTHER status (401/500/...) is a real error.
      if (
        !config.fixtures &&
        err instanceof ApiClientError &&
        (err.status === 404 || err.status === 0)
      ) {
        setPending(true);
        setRows([]);
        return;
      }
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load the waitlist.";
      setError(msg);
      setRows([]);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  const sorted = useMemo(() => {
    const list = [...(rows ?? [])];
    if (sortKey === "wtp_band") {
      list.sort((a, b) => (a.wtp_band ?? "").localeCompare(b.wtp_band ?? ""));
    } else {
      list.sort((a, b) => (b.created_at ?? "").localeCompare(a.created_at ?? ""));
    }
    return list;
  }, [rows, sortKey]);

  return (
    <div className="mx-auto max-w-5xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Lead queue</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Waitlist
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Visitors who joined the waitlist from the public /intake form,
            sortable by willingness-to-pay band.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          {config.fixtures ? "fixtures" : "live"} . waitlist_intake
        </div>
      </header>

      {/* ---- sort toggle --------------------------------------------------- */}
      <div className="mt-6 flex flex-wrap items-center gap-2">
        <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
          sort:
        </span>
        <button
          type="button"
          onClick={() => setSortKey("wtp_band")}
          aria-pressed={sortKey === "wtp_band"}
          className={[
            "rounded-pill border px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
            sortKey === "wtp_band"
              ? "border-synapse/40 bg-synapse/10 text-synapse"
              : "border-line bg-panel-sunken text-text-muted hover:text-text",
          ].join(" ")}
        >
          wtp_band
        </button>
        <button
          type="button"
          onClick={() => setSortKey("created_at")}
          aria-pressed={sortKey === "created_at"}
          className={[
            "rounded-pill border px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
            sortKey === "created_at"
              ? "border-synapse/40 bg-synapse/10 text-synapse"
              : "border-line bg-panel-sunken text-text-muted hover:text-text",
          ].join(" ")}
        >
          newest
        </button>
      </div>

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

      {/* ---- the queue ----------------------------------------------------- */}
      <div className="mt-6">
        {rows === null && !pending ? (
          <div className="flex items-center gap-3 py-16 text-text-muted">
            <Spinner />
            <span className="font-mono text-2xs uppercase tracking-wider">
              loading waitlist
            </span>
          </div>
        ) : pending ? (
          <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
            <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
              <TableIcon />
            </span>
            <p className="font-display text-lg text-text">
              Waiting for backend integration
            </p>
            <p className="mx-auto mt-1 max-w-md text-sm">
              waitlist_intake rows are readable only by the privileged
              service-role Postgres role (LGPD by design) -- this view is
              ready and will populate as soon as a backend reader is wired up.
              Nothing is broken; there is simply no live route yet.
            </p>
          </div>
        ) : sorted.length === 0 ? (
          <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
            <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
              <TableIcon />
            </span>
            <p className="font-display text-lg text-text">No signups yet</p>
            <p className="mt-1 text-sm">
              Waitlist joins from /intake will appear here.
            </p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-card border border-line">
            <div className="hidden grid-cols-[1.4fr_1fr_0.8fr_0.8fr] gap-4 border-b border-line bg-panel-sunken px-5 py-2.5 font-mono text-2xs uppercase tracking-wider text-text-faint sm:grid">
              <span>Email</span>
              <span>Brand</span>
              <span>WTP band</span>
              <span className="text-right">Joined</span>
            </div>
            <ul>
              {sorted.map((r, i) => (
                <li
                  key={r.id}
                  style={{ animationDelay: `${i * 35}ms` }}
                  className="animate-rise-in grid grid-cols-1 gap-2 border-b border-line bg-panel px-5 py-3.5 last:border-b-0 sm:grid-cols-[1.4fr_1fr_0.8fr_0.8fr] sm:items-center sm:gap-4"
                >
                  <span className="truncate font-mono text-xs text-text" title={r.email}>
                    {r.email}
                  </span>
                  <span className="truncate text-sm text-text-muted">
                    {r.brand_name ?? "--"}
                  </span>
                  <span className="font-mono text-2xs text-text-muted">
                    {r.wtp_band ?? "--"}
                  </span>
                  <span className="font-mono text-2xs text-text-muted sm:text-right">
                    {timeAgo(r.created_at)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
