"use client";

// ----------------------------------------------------------------------------
// One capability card in the function matrix. Quiet at rest; on hover the
// synapse edge lights and a faint sheen sweeps. Disabled cards are muted and
// non-interactive (the overlay hid them). The "function signature" line
// (kind/pillar/verb) is rendered in mono -- these are typed identifiers, so
// monospace is structurally honest, not decorative.
// ----------------------------------------------------------------------------

import type { Card } from "@/lib/types";
import { iconFor } from "./icons";

interface Props {
  card: Card;
  index: number;
  onOpen: (card: Card) => void;
}

export function CapabilityCard({ card, index, onOpen }: Props) {
  const Icon = iconFor(card.icon);
  const disabled = !card.enabled;

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onOpen(card)}
      style={{ animationDelay: `${index * 45}ms` }}
      className={[
        "group relative flex animate-rise-in flex-col overflow-hidden rounded-card border bg-panel p-5 text-left transition-all duration-300",
        disabled
          ? "cursor-not-allowed border-line-soft opacity-45"
          : "border-line hover:-translate-y-0.5 hover:border-synapse/40 hover:shadow-glow-soft",
      ].join(" ")}
      aria-label={`Run ${card.label}`}
    >
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
          {card.source === "overlay" && (
            <span className="chip border-synapse/30 text-synapse">overlay</span>
          )}
          <span className="chip">{card.nucleus}</span>
        </div>
      </div>

      <h3 className="relative z-10 mt-4 font-display text-lg font-600 tracking-tight text-text">
        {card.label}
      </h3>

      {card.description && (
        <p className="relative z-10 mt-1.5 line-clamp-2 text-sm text-text-muted">
          {card.description}
        </p>
      )}

      <div className="relative z-10 mt-4 flex items-center justify-between border-t border-line pt-3">
        <span className="font-mono text-2xs text-text-faint">
          {card.kind ? card.kind : "capability"}
          {card.pillar ? ` . ${card.pillar}` : ""}
        </span>
        <span
          className={[
            "font-mono text-2xs uppercase tracking-wider transition-colors",
            disabled
              ? "text-text-faint"
              : "text-text-muted group-hover:text-synapse",
          ].join(" ")}
        >
          {disabled ? "disabled" : "run ->"}
        </span>
      </div>
    </button>
  );
}
