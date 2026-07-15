"use client";

// ----------------------------------------------------------------------------
// /dashboard/agents/[id] -- ONE agent's READ-ONLY detail (ADR Phase A).
//
// Shows the agent's persona, capabilities table, typed Input/Output JSON Schema,
// SLA, and toolkit -- parsed from the agent + agent_card on disk when resolvable
// (else the registry record). The route clones the generic [entity] detail
// pattern: resolve by id via ApiClient.getAgent (fixtures or live), render its
// read-only sections.
//
// RUN TRIGGERS: this page exposes BOTH run paths the agents-SDK layer ships.
//   * "Run" (ADR Phase B) opens AgentRunModal -- a TYPED FORM from the agent's Input
//     Schema, a SINGLE-STEP synchronous run (POST /agent/run), one pass, result via
//     the reused ResultView + FilamentTrace.
//   * "Run loop" (ADR Phase C) opens AgentRunCockpit -- the SAME typed-form kickoff,
//     then the MULTI-STEP plan/act/observe/tool loop (POST /agent/runs, async),
//     polled to a live step trace + budget meter, terminal result via ResultView.
// Both are overlays gated by their own open-state. tenant_id is read from the session;
// never sent.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AgentDetail } from "@/lib/types";
import { AgentRunModal } from "@/components/AgentRunModal";
import { AgentRunCockpit } from "@/components/AgentRunCockpit";
import { iconForNucleus, AgentIcon, ArrowRight } from "@/components/icons";
import { Spinner } from "@/components/ui";

export default function AgentDetailPage() {
  const params = useParams<{ id: string }>();
  const id = typeof params.id === "string" ? params.id : "";

  const { session } = useAuth();
  const token = session?.access_token ?? "";
  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);

  // undefined = still resolving; null = not found; agent = resolved.
  const [agent, setAgent] = useState<AgentDetail | null | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  // The two run overlays, each gated by its own open-state: the single-step modal
  // (Phase B) and the multi-step cockpit (Phase C).
  const [runOpen, setRunOpen] = useState(false);
  const [cockpitOpen, setCockpitOpen] = useState(false);

  const load = useCallback(async () => {
    if (!client || !id) return;
    setError(null);
    try {
      setAgent(await client.getAgent(id));
    } catch (err) {
      // A 404 (unknown agent for this tenant) is a "not found" state, not an error banner.
      if (err instanceof ApiClientError && err.status === 404) {
        setAgent(null);
        return;
      }
      setError(
        err instanceof ApiClientError || err instanceof Error
          ? err.message
          : "Could not load this agent.",
      );
      setAgent(null);
    }
  }, [client, id]);

  useEffect(() => {
    load();
  }, [load]);

  if (agent === undefined && !error) {
    return (
      <div className="mx-auto max-w-4xl">
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading agent
          </span>
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
            <AgentIcon />
          </span>
          <p className="font-display text-lg text-text">Unknown agent</p>
          <p className="mt-1 text-sm">
            <span className="font-mono text-2xs text-text-faint">{id}</span> is not
            an agent for this tenant.
          </p>
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
          <Link
            href="/dashboard/agents"
            className="mt-5 inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
          >
            back to agents
            <ArrowRight />
          </Link>
        </div>
      </div>
    );
  }

  const Icon = iconForNucleus(agent.nucleus);
  const tools = agent.tools ?? [];
  const capabilities = agent.capabilities ?? [];
  const sla = agent.sla ?? [];

  return (
    <div className="mx-auto max-w-4xl">
      {/* ---- back link --------------------------------------------------- */}
      <Link
        href="/dashboard/agents"
        className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
      >
        <span className="rotate-180">
          <ArrowRight />
        </span>
        agents
      </Link>

      {/* ---- masthead ---------------------------------------------------- */}
      <header className="mt-4 flex flex-wrap items-start justify-between gap-4 border-b border-line pb-6">
        <div className="flex items-start gap-4">
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted">
            <Icon />
          </span>
          <div>
            <h1 className="font-display text-2xl font-600 tracking-tight text-text">
              {agent.name}
            </h1>
            {agent.goal && (
              <p className="mt-1.5 max-w-xl text-sm text-text-muted">{agent.goal}</p>
            )}
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <span className="chip">{agent.nucleus || "--"}</span>
              <span className="chip">{agent.kind || "agent"}</span>
              {agent.pillar && <span className="chip">{agent.pillar}</span>}
              {agent.model && (
                <span className="chip border-synapse/30 text-synapse">
                  {agent.model}
                </span>
              )}
              {!agent.enabled && <span className="chip">disabled</span>}
            </div>
          </div>
        </div>

        {/* ---- run triggers: single-step (Phase B) + multi-step (Phase C) - */}
        <div className="text-right">
          <div className="flex flex-wrap items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setRunOpen(true)}
              disabled={!agent.enabled}
              aria-disabled={!agent.enabled}
              title={
                agent.enabled
                  ? "Run this agent (single step, one pass)"
                  : "This agent is disabled for your tenant"
              }
              className={[
                "inline-flex items-center gap-2 rounded-lg px-4 py-2 font-mono text-2xs uppercase tracking-wider transition-colors",
                agent.enabled
                  ? "btn-primary"
                  : "cursor-not-allowed border border-line-soft bg-panel text-text-faint opacity-60",
              ].join(" ")}
            >
              <span
                className={[
                  "h-1.5 w-1.5 rounded-full",
                  agent.enabled ? "bg-ink" : "bg-text-faint",
                ].join(" ")}
              />
              Run
            </button>
            <button
              type="button"
              onClick={() => setCockpitOpen(true)}
              disabled={!agent.enabled}
              aria-disabled={!agent.enabled}
              title={
                agent.enabled
                  ? "Run the multi-step agent loop (live step trace)"
                  : "This agent is disabled for your tenant"
              }
              className={[
                "inline-flex items-center gap-2 rounded-lg border px-4 py-2 font-mono text-2xs uppercase tracking-wider transition-colors",
                agent.enabled
                  ? "border-synapse/40 bg-synapse/10 text-synapse hover:bg-synapse/15"
                  : "cursor-not-allowed border-line-soft bg-panel text-text-faint opacity-60",
              ].join(" ")}
            >
              <span
                className={[
                  "h-1.5 w-1.5 rounded-full",
                  agent.enabled ? "bg-synapse" : "bg-text-faint",
                ].join(" ")}
              />
              Run loop
            </button>
          </div>
          <p className="mt-1.5 font-mono text-2xs text-text-faint">
            single step = one pass . loop = multi-step
          </p>
        </div>
      </header>

      {/* ---- persona ----------------------------------------------------- */}
      {agent.persona && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// persona</p>
          <p className="rounded-card border border-line bg-panel px-5 py-4 text-sm leading-relaxed text-text-muted">
            {agent.persona}
          </p>
        </section>
      )}

      {/* ---- toolkit ----------------------------------------------------- */}
      {tools.length > 0 && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// toolkit</p>
          <div className="flex flex-wrap items-center gap-2">
            {tools.map((t) => (
              <span
                key={t}
                className="rounded-pill border border-line bg-panel-sunken px-3 py-1 font-mono text-2xs text-text-muted"
              >
                {t}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* ---- capabilities ------------------------------------------------ */}
      {capabilities.length > 0 && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// capabilities</p>
          <div className="overflow-hidden rounded-card border border-line">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-line bg-panel-sunken font-mono text-2xs uppercase tracking-wider text-text-muted">
                  <th className="px-4 py-2.5 font-500">Capability</th>
                  <th className="px-4 py-2.5 font-500">Description</th>
                  <th className="px-4 py-2.5 font-500">Tools</th>
                </tr>
              </thead>
              <tbody>
                {capabilities.map((c, i) => (
                  <tr
                    key={`${c.capability}-${i}`}
                    className="border-b border-line last:border-b-0"
                  >
                    <td className="px-4 py-3 font-500 text-text">{c.capability}</td>
                    <td className="px-4 py-3 text-text-muted">{c.description ?? ""}</td>
                    <td className="px-4 py-3 font-mono text-2xs text-text-faint">
                      {c.tools ?? ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ---- typed I/O schemas ------------------------------------------- */}
      {(agent.input_schema || agent.output_schema) && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// I/O contract</p>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {agent.input_schema && (
              <div className="rounded-card border border-line bg-panel">
                <p className="border-b border-line px-4 py-2.5 font-mono text-2xs uppercase tracking-wider text-text-muted">
                  Input Schema
                </p>
                <pre className="overflow-x-auto px-4 py-3 font-mono text-2xs leading-relaxed text-text-muted">
                  {agent.input_schema}
                </pre>
              </div>
            )}
            {agent.output_schema && (
              <div className="rounded-card border border-line bg-panel">
                <p className="border-b border-line px-4 py-2.5 font-mono text-2xs uppercase tracking-wider text-text-muted">
                  Output Schema
                </p>
                <pre className="overflow-x-auto px-4 py-3 font-mono text-2xs leading-relaxed text-text-muted">
                  {agent.output_schema}
                </pre>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ---- SLA --------------------------------------------------------- */}
      {sla.length > 0 && (
        <section className="mt-8">
          <p className="eyebrow mb-3">// SLA</p>
          <div className="overflow-hidden rounded-card border border-line">
            <table className="w-full text-left text-sm">
              <tbody>
                {sla.map((row, i) => (
                  <tr
                    key={`${row.label}-${i}`}
                    className="border-b border-line last:border-b-0"
                  >
                    <td className="w-1/3 px-4 py-3 font-mono text-2xs uppercase tracking-wider text-text-muted">
                      {row.label}
                    </td>
                    <td className="px-4 py-3 text-text">{row.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ---- provenance + read-only note --------------------------------- */}
      <footer className="mt-10 border-t border-line pt-5">
        {agent.artifact_path && (
          <p className="font-mono text-2xs text-text-faint">
            source: {agent.artifact_path}
          </p>
        )}
        <p className="mt-2 text-sm text-text-muted">
          <span className="text-text">Run</span> drives a single-step run (the
          agent&apos;s persona + typed I/O contract honored, one pass).{" "}
          <span className="text-text">Run loop</span> drives the multi-step,
          tool-using agent loop (POST /agent/runs, async) with a live
          plan/act/observe/tool step trace, a budget meter, and HITL-gated tool
          steps surfaced honestly.
        </p>
      </footer>

      {/* ---- the run overlays (each gated by its own open-state) --------- */}
      {runOpen && (
        <AgentRunModal
          agent={agent}
          tenantId={session?.tenant_id ?? ""}
          tenantLabel={session?.tenant_label}
          accessToken={token}
          onClose={() => setRunOpen(false)}
        />
      )}
      {cockpitOpen && (
        <AgentRunCockpit
          agent={agent}
          tenantId={session?.tenant_id ?? ""}
          tenantLabel={session?.tenant_label}
          accessToken={token}
          onClose={() => setCockpitOpen(false)}
        />
      )}
    </div>
  );
}
