"use client";

// ----------------------------------------------------------------------------
// /dashboard/crews/[id] -- ONE crew's READ-ONLY detail (ADR Phase D).
//
// A crew is a multi-role TEAM (a crew_template). This page shows the crew's process
// topology, its Roles table (role -> agent + goal), its handoff protocol, and the
// provenance -- parsed from the crew_template on disk when resolvable (else the list
// record). The route clones the agent [id] detail pattern: resolve by id via
// ApiClient.getCrew (fixtures or live), render its read-only sections.
//
// NO RUN: unlike the agent detail (which exposes the single-step + multi-step run
// triggers), this page has NO run button. A crew run is the founder-gated control-plane
// step -- the page carries a small honest note saying so (mirroring how the agents page
// noted Phase B/C). tenant_id is read from the session; never sent.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { CrewDetail } from "@/lib/types";
import { iconForNucleus, AgentIcon, ArrowRight } from "@/components/icons";
import { Spinner } from "@/components/ui";

export default function CrewDetailPage() {
  const params = useParams<{ id: string }>();
  const id = typeof params.id === "string" ? params.id : "";

  const { session } = useAuth();
  const token = session?.access_token ?? "";
  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);

  // undefined = still resolving; null = not found; crew = resolved.
  const [crew, setCrew] = useState<CrewDetail | null | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!client || !id) return;
    setError(null);
    try {
      setCrew(await client.getCrew(id));
    } catch (err) {
      // A 404 (unknown crew for this tenant) is a "not found" state, not an error banner.
      if (err instanceof ApiClientError && err.status === 404) {
        setCrew(null);
        return;
      }
      setError(
        err instanceof ApiClientError || err instanceof Error
          ? err.message
          : "Could not load this crew.",
      );
      setCrew(null);
    }
  }, [client, id]);

  useEffect(() => {
    load();
  }, [load]);

  if (crew === undefined && !error) {
    return (
      <div className="mx-auto max-w-4xl">
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading crew
          </span>
        </div>
      </div>
    );
  }

  if (!crew) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
            <AgentIcon />
          </span>
          <p className="font-display text-lg text-text">Unknown crew</p>
          <p className="mt-1 text-sm">
            <span className="font-mono text-2xs text-text-faint">{id}</span> is not a
            crew for this tenant.
          </p>
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
          <Link
            href="/dashboard/crews"
            className="mt-5 inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
          >
            back to crews
            <ArrowRight />
          </Link>
        </div>
      </div>
    );
  }

  const Icon = iconForNucleus(crew.nucleus);
  const roles = crew.roles ?? [];
  const roleCount = crew.role_count || roles.length;

  return (
    <div className="mx-auto max-w-4xl">
      {/* ---- back link --------------------------------------------------- */}
      <Link
        href="/dashboard/crews"
        className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
      >
        <span className="rotate-180">
          <ArrowRight />
        </span>
        crews
      </Link>

      {/* ---- masthead ---------------------------------------------------- */}
      <header className="mt-4 flex flex-wrap items-start justify-between gap-4 border-b border-line pb-6">
        <div className="flex items-start gap-4">
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted">
            <Icon />
          </span>
          <div>
            <h1 className="font-display text-2xl font-600 tracking-tight text-text">
              {crew.name}
            </h1>
            {crew.goal && (
              <p className="mt-1.5 max-w-xl text-sm text-text-muted">{crew.goal}</p>
            )}
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <span className="chip">{crew.nucleus || "--"}</span>
              <span className="chip">{crew.kind || "crew_template"}</span>
              {crew.pillar && <span className="chip">{crew.pillar}</span>}
              {/* the process-topology chip -- the crew's defining property */}
              <span className="chip border-synapse/30 text-synapse">
                {crew.process}
              </span>
              <span className="chip">
                {roleCount} role{roleCount === 1 ? "" : "s"}
              </span>
              {!crew.enabled && <span className="chip">disabled</span>}
            </div>
          </div>
        </div>

        {/* ---- read-only note (NO run -- a crew run is the gated phase) ---- */}
        <div className="text-right">
          <span className="inline-flex items-center gap-2 rounded-lg border border-line-soft bg-panel px-4 py-2 font-mono text-2xs uppercase tracking-wider text-text-faint">
            <span className="h-1.5 w-1.5 rounded-full bg-text-faint" />
            read-only
          </span>
          <p className="mt-1.5 font-mono text-2xs text-text-faint">
            running a crew = next, gated phase
          </p>
        </div>
      </header>

      {/* ---- description ------------------------------------------------- */}
      {crew.description && crew.description !== crew.goal && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// overview</p>
          <p className="rounded-card border border-line bg-panel px-5 py-4 text-sm leading-relaxed text-text-muted">
            {crew.description}
          </p>
        </section>
      )}

      {/* ---- process topology -------------------------------------------- */}
      <section className="mt-8">
        <p className="eyebrow mb-3">// process</p>
        <div className="rounded-card border border-line bg-panel px-5 py-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="chip border-synapse/30 text-synapse">{crew.process}</span>
            <span className="text-sm text-text-muted">{processNote(crew.process)}</span>
          </div>
        </div>
      </section>

      {/* ---- roles table ------------------------------------------------- */}
      {roles.length > 0 && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// roles</p>
          <div className="overflow-hidden rounded-card border border-line">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-line bg-panel-sunken font-mono text-2xs uppercase tracking-wider text-text-muted">
                  <th className="px-4 py-2.5 font-500">Role</th>
                  <th className="px-4 py-2.5 font-500">Agent / binding</th>
                  <th className="px-4 py-2.5 font-500">Goal</th>
                </tr>
              </thead>
              <tbody>
                {roles.map((r, i) => (
                  <tr
                    key={`${r.name}-${i}`}
                    className="border-b border-line last:border-b-0"
                  >
                    <td className="px-4 py-3 font-500 text-text">{r.name}</td>
                    <td className="px-4 py-3 font-mono text-2xs text-text-faint">
                      {r.agent ?? ""}
                    </td>
                    <td className="px-4 py-3 text-text-muted">{r.goal ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ---- handoff protocol -------------------------------------------- */}
      {(crew.handoff_protocol || crew.handoff_note) && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// handoff protocol</p>
          <div className="rounded-card border border-line bg-panel px-5 py-4">
            {crew.handoff_protocol && (
              <span className="rounded-pill border border-line bg-panel-sunken px-3 py-1 font-mono text-2xs text-text-muted">
                {crew.handoff_protocol}
              </span>
            )}
            {crew.handoff_note && (
              <p className="mt-3 text-sm leading-relaxed text-text-muted">
                {crew.handoff_note}
              </p>
            )}
          </div>
        </section>
      )}

      {/* ---- provenance + read-only note --------------------------------- */}
      <footer className="mt-10 border-t border-line pt-5">
        {crew.artifact_path && (
          <p className="font-mono text-2xs text-text-faint">
            source: {crew.artifact_path}
          </p>
        )}
        <p className="mt-2 text-sm text-text-muted">
          This is the read-only crew catalog -- browse the roles, the process topology,
          and the handoff protocol. <span className="text-text">Running a crew</span>{" "}
          (the multi-role team executing its roles with handoffs) is the next, gated
          phase of the agents-SDK layer; it is not wired here.
        </p>
      </footer>
    </div>
  );
}

/** A one-line gloss for each process topology (read-only context). */
function processNote(process: string): string {
  switch (process) {
    case "sequential":
      return "Roles run in strict order -- each role grounds on the previous role's artifact.";
    case "hierarchical":
      return "A manager role coordinates workers and may delegate -- it owns the final decision.";
    case "consensus":
      return "All roles work in parallel and vote -- independence guards against single-model bias.";
    default:
      return "The crew's role topology.";
  }
}
