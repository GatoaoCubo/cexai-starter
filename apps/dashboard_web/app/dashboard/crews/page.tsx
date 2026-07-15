"use client";

// ----------------------------------------------------------------------------
// /dashboard/crews -- the Crews catalog (the layer ABOVE single agents).
//
// A crew is a multi-role TEAM (a crew_template artifact) that ships ONE coherent
// deliverable via N roles with handoffs and a process topology (ADR
// adr_agents_sdk_dashboard, Phase D). This CLONES the Agents grid (the masthead + stat
// hero + card grid + dark visual language) and GROUPS the cards by nucleus (the 8 nuclei
// as the org spine). Clicking an enabled crew opens its detail page -- this grid is the
// read-only catalog; running a crew is the next, founder-gated phase (no run here).
//
// Data source is mode-transparent: ApiClient.listCrews() returns fixtures in FIXTURES
// mode and the live, overlay-gated /crews otherwise -- the component is identical in
// both. tenant_id is read from the session, never set here.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import type { Crew } from "@/lib/types";
import { CrewCard } from "@/components/CrewCard";
import { Spinner } from "@/components/ui";
import { AlertIcon } from "@/components/icons";

// The nucleus order + label spine (mirrors the org grouping in nucleus_def).
const NUCLEUS_ORDER = ["N01", "N02", "N03", "N04", "N05", "N06", "N07"];
const NUCLEUS_LABEL: Record<string, string> = {
  N01: "Intelligence",
  N02: "Marketing",
  N03: "Engineering",
  N04: "Knowledge",
  N05: "Operations",
  N06: "Commercial",
  N07: "Orchestration",
};

export default function CrewsPage() {
  const { session } = useAuth();
  const [crews, setCrews] = useState<Crew[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const token = session?.access_token ?? "";

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const list = await new ApiClient(token).listCrews();
      setCrews(list);
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load crews.";
      setError(msg);
      setCrews([]);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  // Honest stat hero -- derived from the loaded crews, not invented.
  const stats = useMemo(() => {
    const all = crews ?? [];
    const enabled = all.filter((c) => c.enabled).length;
    const nuclei = new Set(all.map((c) => c.nucleus).filter(Boolean)).size;
    const roles = all.reduce(
      (sum, c) => sum + (c.role_count || (c.roles ?? []).length),
      0,
    );
    return [
      { label: "crews", value: all.length },
      { label: "enabled", value: enabled },
      { label: "nuclei", value: nuclei },
      { label: "roles wired", value: roles },
    ];
  }, [crews]);

  // Group the crews by nucleus, preserving the nucleus spine order; any unknown
  // nucleus bucket is appended after the known ones.
  const groups = useMemo(() => {
    const all = crews ?? [];
    const byNucleus = new Map<string, Crew[]>();
    for (const c of all) {
      const key = c.nucleus || "--";
      if (!byNucleus.has(key)) byNucleus.set(key, []);
      byNucleus.get(key)!.push(c);
    }
    const ordered: { nucleus: string; label: string; items: Crew[] }[] = [];
    for (const n of NUCLEUS_ORDER) {
      const items = byNucleus.get(n);
      if (items && items.length) {
        ordered.push({ nucleus: n, label: NUCLEUS_LABEL[n] ?? n, items });
        byNucleus.delete(n);
      }
    }
    // any remaining (unknown) nucleus buckets
    for (const [n, items] of byNucleus.entries()) {
      ordered.push({ nucleus: n, label: NUCLEUS_LABEL[n] ?? n, items });
    }
    return ordered;
  }, [crews]);

  const tenantLabel = session?.tenant_label || "Tenant";

  return (
    <div className="mx-auto max-w-6xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Crew console</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Your crews
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Multi-role teams above the single agents. Browse the catalog grouped by
            nucleus and inspect each crew&apos;s roles, process topology, and handoff
            protocol.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          read-only . overlay-gated . {config.fixtures ? "fixtures" : "live"}
        </div>
      </header>

      {/* ---- stat hero --------------------------------------------------- */}
      <div className="mt-7 grid grid-cols-2 overflow-hidden rounded-card border border-line sm:grid-cols-4">
        {stats.map((s, i) => (
          <div
            key={s.label}
            className={[
              "bg-panel px-5 py-4",
              i < stats.length - 1 ? "border-b border-line sm:border-b-0 sm:border-r" : "",
              i % 2 === 0 ? "border-r border-line sm:border-r" : "",
            ].join(" ")}
          >
            <b className="block font-display text-3xl font-600 leading-none text-text">
              {crews === null ? "--" : s.value}
            </b>
            <span className="mt-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted">
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {/* ---- the grouped grid -------------------------------------------- */}
      {error && (
        <div
          role="alert"
          className="mt-10 mb-5 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{error}</span>
        </div>
      )}

      {crews === null ? (
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading crews
          </span>
        </div>
      ) : crews.length === 0 && !error ? (
        <div className="mt-10 rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <p className="font-display text-lg text-text">No crews yet</p>
          <p className="mt-1 text-sm">
            This tenant&apos;s overlay exposes no crews.
          </p>
        </div>
      ) : (
        groups.map((g) => (
          <section key={g.nucleus} className="mt-10">
            <p className="eyebrow mb-4">
              // {g.nucleus} {g.label}
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {g.items.map((crew, i) => (
                <CrewCard key={crew.id} crew={crew} index={i} />
              ))}
            </div>
          </section>
        ))
      )}

      {/* ---- footer note (mirrors the agents "same engine" line) --------- */}
      <footer className="mt-12 border-t border-line pt-5 text-sm text-text-muted">
        <span className="text-text">Crews above agents.</span> Each crew is a typed
        artifact (crew_template) scoped to{" "}
        <span className="font-mono text-2xs text-text-faint">tenant={tenantLabel}</span>.
        This is the read-only catalog; open a crew to inspect its roles, topology, and
        handoff protocol. Running a crew is the next, gated phase.
      </footer>
    </div>
  );
}
