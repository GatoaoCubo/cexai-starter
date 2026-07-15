"use client";

// ----------------------------------------------------------------------------
// /dashboard/home -- the home / analytics SHELL (cross-cutting, not a card).
//
// Three rows, all TENANT-DRIVEN via ApiClient.getSummary() (fixtures in FIXTURES
// mode, the live /summary projection otherwise -- identical component):
//   1. stat cards   -- counts derived from the tenant's capabilities + results
//   2. recent runs  -- the latest artifacts (same rows the Results ledger uses)
//   3. health strip -- the wired surfaces + their live state
//
// Nothing is hardcoded: every number/label is a projection of the tenant's own
// data. tenant_id is read from the session; the client never sends it.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import type { SummaryResponse } from "@/lib/types";
import { ScoreMeter, Spinner, StatCard, StatusPill } from "@/components/ui";
import { AlertIcon, ArrowRight, HistoryIcon, PulseIcon } from "@/components/icons";

function timeAgo(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const mins = Math.max(0, Math.round((Date.now() - then) / 60000));
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

export default function HomePage() {
  const { session } = useAuth();
  const [data, setData] = useState<SummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const token = session?.access_token ?? "";

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      setData(await new ApiClient(token).getSummary());
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load the overview.";
      setError(msg);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  const tenantLabel = session?.tenant_label || "Tenant";
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="mx-auto max-w-6xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Overview</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            {greeting}.
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Your tenant at a glance -- capabilities, recent artifacts, and the
            health of every wired surface. All scoped to{" "}
            <span className="font-mono text-2xs text-text-faint">
              tenant={tenantLabel}
            </span>
            .
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          {config.fixtures ? "fixtures" : "live"} . overview
        </div>
      </header>

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

      {/* ---- 1. stat cards ----------------------------------------------- */}
      {data === null && !error ? (
        <div className="mt-7 flex items-center gap-3 py-10 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading overview
          </span>
        </div>
      ) : (
        data && (
          <>
            <div className="mt-7 grid grid-cols-2 gap-4 lg:grid-cols-4">
              {data.stats.map((s) => (
                <StatCard
                  key={s.key}
                  label={s.label}
                  value={s.value}
                  hint={s.hint}
                  tone={s.tone}
                />
              ))}
            </div>

            {/* ---- 2. recent runs + 3. health (two columns) --------------- */}
            <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[1.5fr_1fr]">
              {/* recent runs strip */}
              <section>
                <div className="mb-4 flex items-center justify-between">
                  <p className="eyebrow">// recent artifacts</p>
                  <Link
                    href="/dashboard/results"
                    className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
                  >
                    all results
                    <ArrowRight />
                  </Link>
                </div>

                {data.recent.length === 0 ? (
                  <div className="rounded-card border border-dashed border-line px-6 py-12 text-center text-text-muted">
                    <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
                      <HistoryIcon />
                    </span>
                    <p className="font-display text-base text-text">No runs yet</p>
                    <p className="mt-1 text-sm">
                      Run a capability and it will appear here.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-hidden rounded-card border border-line">
                    <ul>
                      {data.recent.map((r, i) => (
                        <li
                          key={r.id}
                          style={{ animationDelay: `${i * 35}ms` }}
                          className="grid animate-rise-in grid-cols-1 gap-2 border-b border-line bg-panel px-5 py-3.5 last:border-b-0 sm:grid-cols-[1.5fr_0.9fr_0.7fr] sm:items-center sm:gap-4"
                        >
                          <div className="flex items-center gap-2.5">
                            <span className="chip">{r.nucleus ?? "N0?"}</span>
                            <span className="font-display text-sm font-600 text-text">
                              {r.label ?? r.capability}
                            </span>
                          </div>
                          <span>
                            {typeof r.score === "number" ? (
                              <ScoreMeter score={r.score} />
                            ) : (
                              <span className="font-mono text-2xs text-text-faint">
                                --
                              </span>
                            )}
                          </span>
                          <span className="font-mono text-2xs text-text-muted sm:text-right">
                            {timeAgo(r.created_at)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>

              {/* health strip */}
              <section>
                <p className="eyebrow mb-4 flex items-center gap-2">
                  <PulseIcon />
                  // system health
                </p>
                <div className="overflow-hidden rounded-card border border-line">
                  <ul>
                    {data.health.map((h, i) => (
                      <li
                        key={h.key}
                        style={{ animationDelay: `${i * 35}ms` }}
                        className="flex animate-rise-in items-center justify-between gap-3 border-b border-line bg-panel px-5 py-3.5 last:border-b-0"
                      >
                        <div className="min-w-0">
                          <p className="font-display text-sm font-600 text-text">
                            {h.label}
                          </p>
                          {h.detail && (
                            <p className="mt-0.5 truncate font-mono text-2xs text-text-faint">
                              {h.detail}
                            </p>
                          )}
                        </div>
                        <StatusPill state={h.state} />
                      </li>
                    ))}
                  </ul>
                </div>
              </section>
            </div>
          </>
        )
      )}
    </div>
  );
}
