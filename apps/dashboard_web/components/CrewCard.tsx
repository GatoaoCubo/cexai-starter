"use client";

// ----------------------------------------------------------------------------
// One crew card in the crews catalog. CLONES AgentCard's visual language (quiet at
// rest; on hover the synapse edge lights and a faint sheen sweeps; disabled crews are
// muted) and ADDS the crew-specific surface: a goal line, a process-topology chip, a
// role count + the first role names, and the nucleus badge. The "function signature"
// line (kind/pillar) is mono -- these are typed identifiers.
//
// READ-ONLY: a card is a LINK to the crew detail (browse), NOT a run trigger. A crew
// is the layer ABOVE single agents; running a crew is the founder-gated control-plane
// step -- there is no run wire here. A disabled crew is non-interactive (the overlay
// disabled it), mirroring a disabled agent card.
// ----------------------------------------------------------------------------

import Link from "next/link";
import type { Crew } from "@/lib/types";
import { iconForNucleus } from "./icons";

interface Props {
  crew: Crew;
  index: number;
}

export function CrewCard({ crew, index }: Props) {
  const Icon = iconForNucleus(crew.nucleus);
  const disabled = !crew.enabled;
  // Show at most a few role names on the card; the full roster lives on the detail page.
  const roles = crew.roles ?? [];
  const shownRoles = roles.slice(0, 3);
  const extraRoles = (crew.role_count || roles.length) - shownRoles.length;

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
          <span className="chip" title={`process: ${crew.process}`}>
            {crew.process}
          </span>
          <span className="chip">{crew.nucleus || "--"}</span>
        </div>
      </div>

      <h3 className="relative z-10 mt-4 font-display text-lg font-600 tracking-tight text-text">
        {crew.name}
      </h3>

      {crew.goal && (
        <p className="relative z-10 mt-1.5 line-clamp-2 text-sm text-text-muted">
          {crew.goal}
        </p>
      )}

      {/* role roster -- the crew's roles (the team) */}
      {shownRoles.length > 0 && (
        <div className="relative z-10 mt-3 flex flex-wrap items-center gap-1.5">
          {shownRoles.map((r) => (
            <span
              key={r.name}
              className="rounded-pill border border-line bg-panel-sunken px-2 py-0.5 font-mono text-2xs text-text-muted"
            >
              {r.name}
            </span>
          ))}
          {extraRoles > 0 && (
            <span className="font-mono text-2xs text-text-faint">
              +{extraRoles}
            </span>
          )}
        </div>
      )}

      <div className="relative z-10 mt-4 flex items-center justify-between border-t border-line pt-3">
        <span className="font-mono text-2xs text-text-faint">
          {crew.role_count || roles.length} role
          {(crew.role_count || roles.length) === 1 ? "" : "s"}
          {crew.pillar ? ` . ${crew.pillar}` : ""}
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

  // A disabled crew is a non-interactive panel (no navigation); an enabled one is a
  // Link to its read-only detail page.
  if (disabled) {
    return (
      <div
        style={{ animationDelay: `${index * 45}ms` }}
        className={cardClass}
        aria-disabled="true"
        aria-label={`${crew.name} (disabled)`}
      >
        {inner}
      </div>
    );
  }

  return (
    <Link
      href={`/dashboard/crews/${encodeURIComponent(crew.id)}`}
      style={{ animationDelay: `${index * 45}ms` }}
      className={cardClass}
      aria-label={`Inspect ${crew.name}`}
    >
      {inner}
    </Link>
  );
}
