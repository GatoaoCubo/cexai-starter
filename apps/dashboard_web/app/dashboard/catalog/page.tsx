"use client";

// ----------------------------------------------------------------------------
// /dashboard/catalog -- Spec Catalog: navigable quality map of all capabilities,
// agents, and crews. One tab where the founder bats an eye and knows "is this
// capability good enough or does it have gaps?"
//
// Data: composes from the EXISTING endpoints (listCards + listAgents + listCrews)
// in parallel. No new backend route. Quality badges are derived from molds.ts +
// a hardcoded completeness map (sourced from the 2026-06-22 audit).
//
// Mode-transparent: NEXT_PUBLIC_FIXTURES=1 works offline (same ApiClient calls
// hit the in-memory fixtures). degrade-never: a failed load shows an empty
// section, never a blank crash.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import type { Agent, Card, Crew } from "@/lib/types";
import { moldFor } from "@/lib/molds";
import { AlertIcon } from "@/components/icons";
import { Spinner } from "@/components/ui";

// ----------------------------------------------------------------------------
// Quality map -- from the output-completeness audit 2026-06-22.
// "live-gen": real generator exists and produces structured output.
// "spec-pinned": typed mold exists but no live generator yet.
// "no-spec": neither mold nor generator.
// ----------------------------------------------------------------------------

type QualityStatus = "live-gen" | "spec-pinned" | "no-spec";

interface QualityEntry {
  status: QualityStatus;
  gaps: string[];
}

const QUALITY_MAP: Record<string, QualityEntry> = {
  research:             { status: "live-gen",    gaps: [] },
  ads:                  { status: "live-gen",    gaps: [] },
  media_photo:          { status: "live-gen",    gaps: [] },
  pricing:              { status: "live-gen",    gaps: ["segment posture (W1 partial)"] },
  roi_calc:             { status: "live-gen",    gaps: [] },
  funnel_diag:          { status: "live-gen",    gaps: [] },
  docs:                 { status: "live-gen",    gaps: [] },
  tier_designer:        { status: "live-gen",    gaps: [] },
  product_docs:         { status: "live-gen",    gaps: [] },
  email_builder:        { status: "live-gen",    gaps: [] },
  oauth_connect:        { status: "live-gen",    gaps: [] },
  competitor_benchmark: { status: "live-gen",    gaps: [] },
  pesquisa_produto:     { status: "live-gen",    gaps: ["provenance + versioning"] },
  research_universe:    { status: "live-gen",    gaps: ["confidence breakdown"] },
  landing:              { status: "spec-pinned", gaps: ["no live gen"] },
  custom_intake_form:   { status: "spec-pinned", gaps: ["overlay-defined"] },
};

function qualityFor(capability: string): QualityEntry {
  if (QUALITY_MAP[capability]) return QUALITY_MAP[capability];
  const mold = moldFor(capability);
  if (mold) return { status: "spec-pinned", gaps: [] };
  return { status: "no-spec", gaps: ["no typed contract"] };
}

// ----------------------------------------------------------------------------
// Quality badge
// ----------------------------------------------------------------------------

function QualityBadge({ status }: { status: QualityStatus }) {
  if (status === "live-gen") {
    return (
      <span className="inline-flex items-center rounded-pill border border-synapse/30 bg-synapse/5 px-2 py-0.5 font-mono text-2xs text-synapse">
        live gen
      </span>
    );
  }
  if (status === "spec-pinned") {
    return (
      <span className="inline-flex items-center rounded-pill border border-signal/30 bg-signal/5 px-2 py-0.5 font-mono text-2xs text-signal">
        spec pinned
      </span>
    );
  }
  return (
    <span className="inline-flex items-center rounded-pill border border-line bg-panel px-2 py-0.5 font-mono text-2xs text-text-faint">
      no spec
    </span>
  );
}

// ----------------------------------------------------------------------------
// Capability card row
// ----------------------------------------------------------------------------

function CapabilityRow({ card }: { card: Card }) {
  const mold = moldFor(card.capability);
  const q = qualityFor(card.capability);
  const sectionCount = mold ? mold.output_sections.length : 0;
  const sectionTitles = mold ? mold.output_sections.map((s) => s.title) : [];

  return (
    <div
      className={[
        "rounded-lg border p-4 transition-colors",
        card.enabled
          ? "border-line bg-panel/50 hover:border-line/80"
          : "border-line/50 bg-panel/20 opacity-60",
      ].join(" ")}
    >
      {/* top row: name + badge */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-display text-sm font-600 text-text">
              {card.title || card.label}
            </span>
            {!card.enabled && (
              <span className="inline-flex items-center rounded-pill border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
                disabled
              </span>
            )}
          </div>
          {card.description && (
            <p className="mt-1 text-xs leading-relaxed text-text-muted">
              {card.description}
            </p>
          )}
        </div>
        <div className="shrink-0 pt-0.5">
          <QualityBadge status={q.status} />
        </div>
      </div>

      {/* signature line: kind | pillar | nucleus | verb | N sections */}
      <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
        {card.kind && (
          <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
            {card.kind}
          </span>
        )}
        {card.pillar && (
          <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
            {card.pillar}
          </span>
        )}
        <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
          {card.nucleus}
        </span>
        {card.verb && (
          <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
            {card.verb}
          </span>
        )}
        {sectionCount > 0 && (
          <span className="rounded border border-synapse/20 bg-synapse/5 px-1.5 py-0.5 font-mono text-2xs text-synapse/70">
            {sectionCount} sections
          </span>
        )}
      </div>

      {/* output sections preview */}
      {sectionTitles.length > 0 && (
        <p className="mt-1.5 font-mono text-2xs text-text-faint">
          {sectionTitles.join(" | ")}
        </p>
      )}

      {/* gaps */}
      {q.gaps.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {q.gaps.map((g) => (
            <span
              key={g}
              className="rounded border border-danger/20 bg-danger/5 px-1.5 py-0.5 font-mono text-2xs text-danger/80"
            >
              gap: {g}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------------------------------
// Agent row
// ----------------------------------------------------------------------------

function AgentRow({ agent }: { agent: Agent }) {
  return (
    <div
      className={[
        "flex items-start justify-between gap-3 rounded-lg border p-3.5",
        agent.enabled ? "border-line bg-panel/50" : "border-line/50 bg-panel/20 opacity-60",
      ].join(" ")}
    >
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-display text-sm font-600 text-text">
            {agent.name}
          </span>
          <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
            {agent.nucleus}
          </span>
        </div>
        {agent.goal && (
          <p className="mt-1 line-clamp-2 text-xs text-text-muted">{agent.goal}</p>
        )}
        {agent.tools && agent.tools.length > 0 && (
          <p className="mt-1 font-mono text-2xs text-text-faint">
            tools: {agent.tools.slice(0, 4).join(", ")}
            {agent.tools.length > 4 ? ` + ${agent.tools.length - 4} more` : ""}
          </p>
        )}
      </div>
      <div className="shrink-0">
        <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
          {agent.kind || "agent"}
        </span>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// Crew row
// ----------------------------------------------------------------------------

function CrewRow({ crew }: { crew: Crew }) {
  return (
    <div
      className={[
        "flex items-start justify-between gap-3 rounded-lg border p-3.5",
        crew.enabled ? "border-line bg-panel/50" : "border-line/50 bg-panel/20 opacity-60",
      ].join(" ")}
    >
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-display text-sm font-600 text-text">
            {crew.name}
          </span>
          <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
            {crew.process}
          </span>
          <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
            {crew.role_count} roles
          </span>
        </div>
        {crew.goal && (
          <p className="mt-1 line-clamp-2 text-xs text-text-muted">{crew.goal}</p>
        )}
        {crew.roles && crew.roles.length > 0 && (
          <p className="mt-1 font-mono text-2xs text-text-faint">
            {crew.roles.map((r) => r.name).join(" -> ")}
          </p>
        )}
      </div>
      <div className="shrink-0">
        <span className="rounded border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
          {crew.nucleus}
        </span>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// Empty state
// ----------------------------------------------------------------------------

function EmptySection({ label }: { label: string }) {
  return (
    <div className="rounded-lg border border-dashed border-line px-6 py-10 text-center text-text-muted">
      <p className="font-display text-sm text-text">No {label} in catalog</p>
      <p className="mt-1 text-xs">
        The tenant overlay exposes none for this session.
      </p>
    </div>
  );
}

// ----------------------------------------------------------------------------
// Page
// ----------------------------------------------------------------------------

export default function CatalogPage() {
  const { session } = useAuth();
  const [cards, setCards] = useState<Card[] | null>(null);
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const [crews, setCrews] = useState<Crew[] | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const token = session?.access_token ?? "";

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setErrors([]);
    const errs: string[] = [];

    const client = new ApiClient(token);
    const [cardsResult, agentsResult, crewsResult] = await Promise.allSettled([
      client.listCards(),
      client.listAgents(),
      client.listCrews(),
    ]);

    if (cardsResult.status === "fulfilled") {
      setCards(cardsResult.value);
    } else {
      const msg =
        cardsResult.reason instanceof ApiClientError
          ? cardsResult.reason.message
          : "Could not load capabilities.";
      errs.push(msg);
      setCards([]);
    }

    if (agentsResult.status === "fulfilled") {
      setAgents(agentsResult.value);
    } else {
      const msg =
        agentsResult.reason instanceof ApiClientError
          ? agentsResult.reason.message
          : "Could not load agents.";
      errs.push(msg);
      setAgents([]);
    }

    if (crewsResult.status === "fulfilled") {
      setCrews(crewsResult.value);
    } else {
      const msg =
        crewsResult.reason instanceof ApiClientError
          ? crewsResult.reason.message
          : "Could not load crews.";
      errs.push(msg);
      setCrews([]);
    }

    setErrors(errs);
    setLoading(false);
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  // Honest stat hero -- derived from loaded data, not invented.
  const stats = useMemo(() => {
    const allCards = cards ?? [];
    const allAgents = agents ?? [];
    const allCrews = crews ?? [];
    const liveGen = allCards.filter(
      (c) => (QUALITY_MAP[c.capability]?.status ?? "no-spec") === "live-gen",
    ).length;
    return [
      { label: "capabilities", value: allCards.length },
      { label: "live gen", value: liveGen },
      { label: "agents", value: allAgents.length },
      { label: "crews", value: allCrews.length },
    ];
  }, [cards, agents, crews]);

  const tenantLabel = session?.tenant_label || "Tenant";
  const isLoading = loading && cards === null;

  return (
    <div className="mx-auto max-w-6xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Spec Catalog</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Quality map
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Every capability, agent, and crew -- what each does, its typed output
            contract, and whether the generator is live or spec-pinned. Bat an eye
            and know if something is ready or has gaps.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          read-only . {config.fixtures ? "fixtures" : "live"}
        </div>
      </header>

      {/* ---- stat hero --------------------------------------------------- */}
      <div className="mt-7 grid grid-cols-2 overflow-hidden rounded-card border border-line sm:grid-cols-4">
        {stats.map((s, i) => (
          <div
            key={s.label}
            className={[
              "bg-panel px-5 py-4",
              i < stats.length - 1
                ? "border-b border-line sm:border-b-0 sm:border-r"
                : "",
              i % 2 === 0 ? "border-r border-line sm:border-r" : "",
            ].join(" ")}
          >
            <b className="block font-display text-3xl font-600 leading-none text-text">
              {isLoading ? "--" : s.value}
            </b>
            <span className="mt-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted">
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {/* ---- errors ------------------------------------------------------ */}
      {errors.length > 0 && (
        <div
          role="alert"
          className="mt-8 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{errors.join(" | ")}</span>
        </div>
      )}

      {/* ---- loading spinner --------------------------------------------- */}
      {isLoading && (
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading catalog
          </span>
        </div>
      )}

      {/* ---- CAPABILITIES ----------------------------------------------- */}
      {!isLoading && (
        <section className="mt-10">
          <p className="eyebrow mb-4">// Capabilities ({cards?.length ?? 0})</p>

          {/* legend */}
          <div className="mb-4 flex flex-wrap gap-3 text-2xs text-text-muted">
            <span className="flex items-center gap-1.5">
              <QualityBadge status="live-gen" />
              <span>real generator -- runs and produces structured output</span>
            </span>
            <span className="flex items-center gap-1.5">
              <QualityBadge status="spec-pinned" />
              <span>typed mold exists; no live generator yet</span>
            </span>
            <span className="flex items-center gap-1.5">
              <QualityBadge status="no-spec" />
              <span>no typed contract</span>
            </span>
          </div>

          {cards && cards.length === 0 ? (
            <EmptySection label="capabilities" />
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {(cards ?? []).map((card) => (
                <CapabilityRow key={card.capability} card={card} />
              ))}
            </div>
          )}
        </section>
      )}

      {/* ---- AGENTS ----------------------------------------------------- */}
      {!isLoading && (
        <section className="mt-10">
          <p className="eyebrow mb-4">// Agents ({agents?.length ?? 0})</p>
          {agents && agents.length === 0 ? (
            <EmptySection label="agents" />
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {(agents ?? []).map((agent) => (
                <AgentRow key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </section>
      )}

      {/* ---- CREWS ------------------------------------------------------ */}
      {!isLoading && (
        <section className="mt-10">
          <p className="eyebrow mb-4">// Crews ({crews?.length ?? 0})</p>
          {crews && crews.length === 0 ? (
            <EmptySection label="crews" />
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {(crews ?? []).map((crew) => (
                <CrewRow key={crew.id} crew={crew} />
              ))}
            </div>
          )}
        </section>
      )}

      {/* ---- footer note ------------------------------------------------- */}
      {!isLoading && (
        <footer className="mt-12 border-t border-line pt-5 text-sm text-text-muted">
          <span className="text-text">Spec Catalog.</span> Read-only quality map
          sourced from the capability registry, agents catalog, and crews catalog.
          Quality badges from the 2026-06-22 output-completeness audit.{" "}
          <span className="font-mono text-2xs text-text-faint">
            tenant={tenantLabel}
          </span>
        </footer>
      )}
    </div>
  );
}
