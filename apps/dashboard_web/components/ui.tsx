"use client";

// ----------------------------------------------------------------------------
// Small shared UI atoms: brand wordmark, status badge, score meter, nucleus tag,
// spinner. Kept quiet -- the filament is the one loud element.
// ----------------------------------------------------------------------------

import { config } from "@/lib/config";
import { resolveAdminTheme, monogramDataUri } from "@/lib/adminTheme";
import { useAdminThemeContext } from "./TenantTheme";
import type { RunStatus } from "@/lib/types";
import { BrandMark } from "./icons";

/**
 * Brand wordmark in the admin chrome. For an ACTIVE tenant (an active-tenant admin
 * theme example) it shows the tenant LOGO (same-origin /tenants/<id>/logo.png) + the tenant name;
 * the logo sits in the brand accent (which is itself the tenant's on-dark brand
 * colour via --accent). For the DEFAULT (no active tenant) it shows the existing
 * CEXAI brand mark + config.brandName -- byte-unchanged.
 *
 * PREVIEW-tenant source: when a <TenantThemeProvider> is mounted (the app shell) the
 * brand follows the RUNTIME ?tenant override (admin runtime-tenant); standalone (no
 * provider, e.g. a unit test) it falls back to the build-time env theme -- byte-
 * identical to the pre-runtime behaviour. This is THEME/PREVIEW ONLY; the data tenant
 * shown in the spine's "Tenant context" card stays session-bound (auth/RLS).
 */
export function Wordmark({ compact = false }: { compact?: boolean }) {
  const ctx = useAdminThemeContext();
  const tenant = ctx !== undefined ? ctx : resolveAdminTheme();
  const name = tenant ? tenant.brandName : config.brandName;

  return (
    <span className="inline-flex items-center gap-2.5 text-text">
      <span className="text-synapse">
        {tenant && tenant.logoPath ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={tenant.logoPath}
            alt={tenant.logoAlt}
            width={24}
            height={24}
            className="h-6 w-6 object-contain"
          />
        ) : tenant && tenant.monogramSvg ? (
          // R-006 D2: a KNOWN tenant with no logo renders its brand-initials MONOGRAM --
          // never the CEXAI mark, never empty. Data-URI image sink (no raw-HTML injection).
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={monogramDataUri(tenant.monogramSvg)}
            alt={tenant.logoAlt}
            width={24}
            height={24}
            className="h-6 w-6 rounded object-contain"
          />
        ) : (
          <BrandMark />
        )}
      </span>
      {!compact && (
        <span className="font-display text-lg font-600 tracking-tight">
          {name}
        </span>
      )}
    </span>
  );
}

const STATUS_STYLE: Record<RunStatus, { label: string; cls: string; dot: string }> = {
  started: {
    label: "Starting",
    cls: "border-signal/30 bg-signal/10 text-signal",
    dot: "bg-signal animate-pulse-dot",
  },
  running: {
    label: "Running",
    cls: "border-synapse/30 bg-synapse/10 text-synapse",
    dot: "bg-synapse animate-pulse-dot",
  },
  done: {
    label: "Done",
    cls: "border-synapse/40 bg-synapse/10 text-synapse",
    dot: "bg-synapse",
  },
  error: {
    label: "Failed",
    cls: "border-danger/40 bg-danger/10 text-danger",
    dot: "bg-danger",
  },
};

export function StatusBadge({ status }: { status: RunStatus }) {
  const s = STATUS_STYLE[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 font-mono text-2xs uppercase tracking-wider ${s.cls}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  );
}

/** A score 0..10 rendered as a thin meter + numeric. */
export function ScoreMeter({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(100, (score / 10) * 100));
  const tone =
    score >= 9 ? "bg-synapse" : score >= 8 ? "bg-synapse-deep" : "bg-signal";
  return (
    <div className="flex items-center gap-2.5">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-line">
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono text-xs text-text">{score.toFixed(1)}</span>
    </div>
  );
}

export function NucleusTag({ nucleus }: { nucleus: string }) {
  return <span className="chip">{nucleus}</span>;
}

export function Spinner({ className = "" }: { className?: string }) {
  return (
    <span
      className={`inline-block h-4 w-4 animate-spin-slow rounded-full border-2 border-synapse/30 border-t-synapse ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}

// ----------------------------------------------------------------------------
// Shell atoms (home + settings + management). Same quiet token language; the
// filament stays the one loud element.
// ----------------------------------------------------------------------------

/** A headline stat tile. ``value`` is shown big; ``hint`` is the sub-line. */
export function StatCard({
  label,
  value,
  hint,
  tone = "muted",
}: {
  label: string;
  value: number | string;
  hint?: string;
  tone?: "synapse" | "signal" | "muted";
}) {
  const valueTone =
    tone === "synapse"
      ? "text-synapse"
      : tone === "signal"
        ? "text-signal"
        : "text-text";
  return (
    <div className="panel px-5 py-4">
      <b className={`block font-display text-3xl font-600 leading-none ${valueTone}`}>
        {value}
      </b>
      <span className="mt-2 block font-mono text-2xs uppercase tracking-wider text-text-muted">
        {label}
      </span>
      {hint && (
        <span className="mt-1 block font-mono text-2xs text-text-faint">{hint}</span>
      )}
    </div>
  );
}

/**
 * A status dot + label for health / integration / connection states. Maps a
 * small fixed vocabulary of states to the token palette (ok=synapse,
 * degraded/available=signal, down/error=danger, unknown=faint).
 */
export type StatusTone =
  | "ok"
  | "degraded"
  | "down"
  | "unknown"
  | "connected"
  | "available"
  | "error";

const STATUS_TONE: Record<StatusTone, { dot: string; text: string; word: string }> = {
  ok: { dot: "bg-synapse", text: "text-synapse", word: "ok" },
  connected: { dot: "bg-synapse", text: "text-synapse", word: "connected" },
  degraded: { dot: "bg-signal animate-pulse-dot", text: "text-signal", word: "degraded" },
  available: { dot: "bg-text-faint", text: "text-text-muted", word: "available" },
  down: { dot: "bg-danger", text: "text-danger", word: "down" },
  error: { dot: "bg-danger", text: "text-danger", word: "error" },
  unknown: { dot: "bg-text-faint", text: "text-text-faint", word: "unknown" },
};

export function StatusPill({
  state,
  label,
}: {
  state: StatusTone;
  label?: string;
}) {
  const s = STATUS_TONE[state] ?? STATUS_TONE.unknown;
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      <span className={`font-mono text-2xs uppercase tracking-wider ${s.text}`}>
        {label ?? s.word}
      </span>
    </span>
  );
}

// ----------------------------------------------------------------------------
// Pagination control (HARDEN mission). Presentational only: it takes the window
// reported by lib/pagination.usePagination and renders prev/next + a
// "showing X-Y of N . page P/PC" line. Renders NOTHING when there is a single
// page, so a small list looks identical to before (degrade-never).
// ----------------------------------------------------------------------------

export function Pagination({
  page,
  pageCount,
  total,
  start,
  end,
  canPrev,
  canNext,
  onPrev,
  onNext,
  unit = "rows",
}: {
  page: number;
  pageCount: number;
  total: number;
  start: number;
  end: number;
  canPrev: boolean;
  canNext: boolean;
  onPrev: () => void;
  onNext: () => void;
  /** Noun for the count line, e.g. "rows" / "results" / "products". */
  unit?: string;
}) {
  if (pageCount <= 1) return null;
  return (
    <nav
      aria-label="Pagination"
      className="mt-5 flex flex-wrap items-center justify-between gap-3 font-mono text-2xs text-text-faint"
    >
      <span>
        showing {start}-{end} of {total} {unit} . page {page}/{pageCount}
      </span>
      <span className="flex items-center gap-2">
        <button
          type="button"
          onClick={onPrev}
          disabled={!canPrev}
          aria-label="Previous page"
          className="rounded-pill border border-line bg-panel-sunken px-3 py-1 uppercase tracking-wider text-text-muted transition-colors hover:border-line-strong hover:text-text disabled:cursor-not-allowed disabled:opacity-40"
        >
          prev
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={!canNext}
          aria-label="Next page"
          className="rounded-pill border border-line bg-panel-sunken px-3 py-1 uppercase tracking-wider text-text-muted transition-colors hover:border-line-strong hover:text-text disabled:cursor-not-allowed disabled:opacity-40"
        >
          next
        </button>
      </span>
    </nav>
  );
}
