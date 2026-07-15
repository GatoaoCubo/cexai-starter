"use client";

// ----------------------------------------------------------------------------
// The signature element: the 8F filament.
//
// When a capability runs, the 8F pipeline (F1..F8) is literally how CEX thinks.
// This component renders that as a horizontal filament of 8 nodes that fire in
// sequence as the run progresses -- a memorable, justified motion moment that
// is true to the subject (not decoration). Boldness lives HERE; everything
// else in the app stays quiet.
//
// Driven by `progress` (0..1). At rest (progress<=0) it is dim and idle.
// ----------------------------------------------------------------------------

import { F8_STEPS } from "@/lib/fixtures";

interface Props {
  /** 0..1 fraction of the run complete. */
  progress: number;
  /** compact = inline row (in a panel); full = larger with labels. */
  variant?: "compact" | "full";
}

export function FilamentTrace({ progress, variant = "full" }: Props) {
  const steps = F8_STEPS;
  const active = Math.min(steps.length, Math.floor(progress * steps.length));
  const compact = variant === "compact";

  return (
    <div className="w-full" aria-hidden>
      <div className="relative flex items-center">
        {/* the connecting wire */}
        <div className="absolute left-0 right-0 top-1/2 h-px -translate-y-1/2 bg-line" />
        {/* the energized portion of the wire */}
        <div
          className="absolute left-0 top-1/2 h-px -translate-y-1/2 bg-gradient-to-r from-synapse-deep to-synapse transition-[width] duration-500 ease-out"
          style={{ width: `${Math.min(100, progress * 100)}%` }}
        />
        {/* a travelling spark on the active wire */}
        {progress > 0 && progress < 1 && (
          <div className="pointer-events-none absolute left-0 right-0 top-1/2 -translate-y-1/2 overflow-hidden">
            <div className="h-px w-1/4 animate-trace-sweep bg-gradient-to-r from-transparent via-synapse-bright to-transparent" />
          </div>
        )}

        <ol className="relative z-10 flex w-full items-center justify-between">
          {steps.map((step, i) => {
            const isDone = i < active;
            const isFiring = i === active && progress < 1;
            const isComplete = progress >= 1;
            return (
              <li
                key={step.id}
                className="flex flex-col items-center"
                style={{ flex: "0 0 auto" }}
              >
                <span
                  className={[
                    "grid place-items-center rounded-full border transition-all duration-300",
                    compact ? "h-3.5 w-3.5" : "h-5 w-5",
                    isComplete || isDone
                      ? "border-synapse bg-synapse text-ink"
                      : isFiring
                        ? "animate-filament-pulse border-synapse bg-synapse/20 text-synapse"
                        : "border-line bg-ink text-text-faint",
                  ].join(" ")}
                >
                  {!compact && (
                    <span className="font-mono text-[8px] font-semibold leading-none">
                      {step.id.replace("F", "")}
                    </span>
                  )}
                </span>
                {!compact && (
                  <span
                    className={[
                      "mt-2 font-mono text-[9px] uppercase tracking-wider transition-colors",
                      isDone || isComplete
                        ? "text-text-muted"
                        : isFiring
                          ? "text-synapse"
                          : "text-text-faint",
                    ].join(" ")}
                  >
                    {step.id}
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      </div>

      {!compact && (
        <p className="mt-3 text-center font-mono text-2xs text-text-muted">
          {progress >= 1
            ? "F8 COLLABORATE -- artifact persisted + signalled"
            : active < steps.length
              ? `${steps[active].id} ${steps[active].name} -- ${steps[active].note}`
              : "initializing pipeline"}
        </p>
      )}
    </div>
  );
}
