"use client";

// ----------------------------------------------------------------------------
// One agent card in the agents catalog. CLONES CapabilityCard's visual language
// (quiet at rest; on hover the synapse edge lights and a faint sheen sweeps;
// disabled agents are muted) and ADDS the agent-specific surface: a goal line,
// toolkit chips, a model chip, and the nucleus badge. The "function signature"
// line (kind/pillar) is mono -- these are typed identifiers.
//
// READ-ONLY: a card is a LINK to the agent detail (browse), NOT a run trigger.
// Running an agent is the multi-step Phase B/C loop -- there is no run wire here.
// A disabled agent is non-interactive (the overlay disabled it), mirroring a
// disabled capability card.
// ----------------------------------------------------------------------------

import Link from "next/link";
import type { Agent } from "@/lib/types";
import { iconForNucleus } from "./icons";

interface Props {
  agent: Agent;
  index: number;
}

export function AgentCard({ agent, index }: Props) {
  const Icon = iconForNucleus(agent.nucleus);
  const disabled = !agent.enabled;
  // Show at most a few toolkit chips on the card; the rest live on the detail page.
  const tools = agent.tools ?? [];
  const shownTools = tools.slice(0, 3);
  const extraTools = tools.length - shownTools.length;

  const inner = (
    <>
      {/* hover sheen */}
      {!disabled && (
        <span className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-synapse/[0.06] to-transparent transition-transform duration-700 group-hover:translate-x-full" />
      )}

      <div className="relative z-10 flex items-start justify-between">
        <span
          className={[
            "grid h-11 w-11 place-items-center rounded-lg border transition-colors duration-300",
            disabled
              ? "border-line bg-panel-sunken text-text-faint"
              : "border-line bg-panel-sunken text-text-muted group-hover:border-synapse/40 group-hover:text-synapse",
          ].join(" ")}
        >
          <Icon />
        </span>

        <div className="flex items-center gap-1.5">
          {agent.model && (
            <span className="chip" title={`model: ${agent.model}`}>
              {agent.model}
            </span>
          )}
          <span className="chip">{agent.nucleus || "--"}</span>
        </div>
      </div>

      <h3 className="relative z-10 mt-4 font-display text-lg font-600 tracking-tight text-text">
        {agent.name}
      </h3>

      {agent.goal && (
        <p className="relative z-10 mt-1.5 line-clamp-2 text-sm text-text-muted">
          {agent.goal}
        </p>
      )}

      {/* toolkit chips -- the agent's tool grants */}
      {shownTools.length > 0 && (
        <div className="relative z-10 mt-3 flex flex-wrap items-center gap-1.5">
          {shownTools.map((t) => (
            <span
              key={t}
              className="rounded-pill border border-line bg-panel-sunken px-2 py-0.5 font-mono text-2xs text-text-muted"
            >
              {t}
            </span>
          ))}
          {extraTools > 0 && (
            <span className="font-mono text-2xs text-text-faint">
              +{extraTools}
            </span>
          )}
        </div>
      )}

      <div className="relative z-10 mt-4 flex items-center justify-between border-t border-line pt-3">
        <span className="font-mono text-2xs text-text-faint">
          {agent.kind ? agent.kind : "agent"}
          {agent.pillar ? ` . ${agent.pillar}` : ""}
        </span>
        <span
          className={[
            "font-mono text-2xs uppercase tracking-wider transition-colors",
            disabled
              ? "text-text-faint"
              : "text-text-muted group-hover:text-synapse",
          ].join(" ")}
        >
          {disabled ? "disabled" : "inspect ->"}
        </span>
      </div>
    </>
  );

  const cardClass = [
    "group relative flex animate-rise-in flex-col overflow-hidden rounded-card border bg-panel p-5 text-left transition-all duration-300",
    disabled
      ? "cursor-not-allowed border-line-soft opacity-45"
      : "border-line hover:-translate-y-0.5 hover:border-synapse/40 hover:shadow-glow-soft",
  ].join(" ");

  // A disabled agent is a non-interactive panel (no navigation); an enabled one
  // is a Link to its read-only detail page.
  if (disabled) {
    return (
      <div
        style={{ animationDelay: `${index * 45}ms` }}
        className={cardClass}
        aria-disabled="true"
        aria-label={`${agent.name} (disabled)`}
      >
        {inner}
      </div>
    );
  }

  return (
    <Link
      href={`/dashboard/agents/${encodeURIComponent(agent.id)}`}
      style={{ animationDelay: `${index * 45}ms` }}
      className={cardClass}
      aria-label={`Inspect ${agent.name}`}
    >
      {inner}
    </Link>
  );
}
