"use client";

// ----------------------------------------------------------------------------
// The COMPOSE PICKER (mission BUILD C, on top of DASHBOARD_COMPOSITION W2/W3).
//
// The founder's model made real as a real PICKER: "YOUR composition -- pull what you
// need." It reads GET /capabilities-config (the {declared, enabled, disabled} attach
// state) and splits the DECLARED universe into two honest sections:
//
//   * IN YOUR DASHBOARD  -- the enabled set. Each row is a card already on your grid;
//                           "Remove" detaches it (PATCH /capabilities/{slug} detach).
//   * AVAILABLE TO ADD   -- the declared-but-DISABLED set (the platform catalog you have
//                           NOT pulled yet). "Add" attaches it (PATCH ... attach) and the
//                           card appears on the grid (the parent refetches via onChanged).
//
// Toggling re-composes the dashboard: an attached module's card appears in the grid, a
// detached one is hidden. Rich rows come from the FULL catalog metadata (listCatalog) so
// an available-but-disabled module still reads richly; an absent catalog (live mode, no
// full-catalog route yet) degrades to a humanized slug -- never an invented capability.
//
// HONEST by construction: it renders WHATEVER /capabilities-config DECLARES -- zero
// hard-coded tenant or module list, and it NEVER shows a capability the state does not
// declare. The counts (declared / on / available) are derived from that state. tenant_id
// is never sent (the backend derives it from the JWT). Errors (409 undeclared / 400
// unknown action / network) surface inline -- never a blank crash.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import type { CapabilitiesConfig, Card } from "@/lib/types";
import { Spinner } from "./ui";
import { AlertIcon, CheckIcon, PlusIcon, RefreshIcon, TrashIcon } from "./icons";

interface Props {
  /** whether the picker is open (the parent owns the toggle). */
  open: boolean;
  /** Bearer for live backend calls (lib/api). Ignored in fixtures mode. */
  accessToken: string;
  /** the grid's loaded cards -- a label/provenance source for enabled modules. */
  cards: Card[];
  /** close the picker. */
  onClose: () => void;
  /** fired after a successful attach/detach so the parent can refresh the grid. */
  onChanged: () => void;
}

/** Humanize a capability slug for display when no card metadata is available. */
function humanize(slug: string): string {
  return slug
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

/** One declared module the picker can render: its slug + the best metadata we resolved. */
interface PickerRow {
  slug: string;
  on: boolean;
  card?: Card;
}

/** A rich, honest row for one declared module (enabled or available). The action button is
 *  supplied by the caller so the two sections read distinctly (Remove vs Add). */
function ModuleRow({
  row,
  busy,
  error,
  onToggle,
}: {
  row: PickerRow;
  busy: boolean;
  error?: string;
  onToggle: () => void;
}) {
  const { slug, on, card } = row;
  const label = card?.title || card?.label || humanize(slug);
  const sig = [slug, card?.kind, card?.pillar].filter(Boolean).join(" . ");
  return (
    <li className="rounded-lg border border-line bg-panel-sunken px-4 py-3">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="truncate font-display text-sm font-600 text-text">
              {label}
            </span>
            {card?.source === "overlay" && (
              <span className="chip border-synapse/30 text-synapse">overlay</span>
            )}
            {card?.nucleus && <span className="chip">{card.nucleus}</span>}
          </div>
          {card?.description && (
            <p className="mt-1 line-clamp-2 text-2xs text-text-muted">
              {card.description}
            </p>
          )}
          <p className="mt-1 truncate font-mono text-2xs text-text-faint">{sig}</p>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={onToggle}
          aria-label={`${on ? "Remove" : "Add"} ${label}`}
          className={[
            "inline-flex shrink-0 items-center gap-1.5 rounded-lg border px-3 py-1.5 font-mono text-2xs uppercase tracking-wider transition-colors",
            busy
              ? "cursor-wait border-line bg-panel text-text-faint opacity-70"
              : on
                ? "border-line bg-panel text-text-muted hover:border-danger/40 hover:text-danger"
                : "border-synapse/40 bg-synapse/10 text-synapse hover:bg-synapse/20",
          ].join(" ")}
        >
          {busy ? (
            "..."
          ) : on ? (
            <>
              <TrashIcon />
              Remove
            </>
          ) : (
            <>
              <PlusIcon />
              Add
            </>
          )}
        </button>
      </div>
      {error && (
        <p className="mt-2 flex items-start gap-1.5 text-2xs text-danger">
          <span className="mt-px shrink-0">
            <AlertIcon />
          </span>
          <span>{error}</span>
        </p>
      )}
    </li>
  );
}

export function ModuleManager({
  open,
  accessToken,
  cards,
  onClose,
  onChanged,
}: Props) {
  const [cfg, setCfg] = useState<CapabilitiesConfig | null>(null);
  // The FULL declared catalog metadata (rich rows for the available set). In live mode
  // listCatalog degrades to [] -> available rows humanize the slug (zero-regression).
  const [catalog, setCatalog] = useState<Card[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const [rowError, setRowError] = useState<Record<string, string>>({});

  // A slug -> Card map for the richest metadata available: the FULL catalog first (covers
  // the disabled/available set), with the loaded grid cards layered on top (authoritative
  // for what is currently rendered). Either source alone is fine; together they let BOTH
  // the enabled and the available rows read richly. Pure derivation, no fabrication.
  const cardMap = useMemo(() => {
    const m = new Map<string, Card>();
    for (const c of catalog) m.set(c.capability, c);
    for (const c of cards) m.set(c.capability, c);
    return m;
  }, [catalog, cards]);

  const enabledSet = useMemo(() => new Set(cfg?.enabled ?? []), [cfg]);

  // Split the DECLARED universe into the two picker sections. We iterate over ``declared``
  // ONLY -- a capability the state does not declare can never appear (honest). ``enabled``
  // -> "in your dashboard"; everything else declared -> "available to add".
  const { enabledRows, availableRows } = useMemo(() => {
    const declared = cfg?.declared ?? [];
    const en: PickerRow[] = [];
    const av: PickerRow[] = [];
    for (const slug of declared) {
      const on = enabledSet.has(slug);
      const r: PickerRow = { slug, on, card: cardMap.get(slug) };
      (on ? en : av).push(r);
    }
    return { enabledRows: en, availableRows: av };
  }, [cfg, enabledSet, cardMap]);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    setRowError({});
    try {
      const client = new ApiClient(accessToken);
      // The attach state is authoritative; the catalog is enrichment (degrade-never if it
      // fails -- the state still renders, available rows just humanize their slug).
      const [next, cat] = await Promise.all([
        client.getCapabilitiesConfig(),
        client.listCatalog().catch(() => [] as Card[]),
      ]);
      setCfg(next);
      setCatalog(cat);
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load the module catalog.";
      setLoadError(msg);
      setCfg(null);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  // (Re)load every time the picker opens -- the state may have changed since last open
  // (e.g. an N07 intent-driven attach).
  useEffect(() => {
    if (open) load();
  }, [open, load]);

  // Close on Escape.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const toggle = useCallback(
    async (slug: string, isOn: boolean) => {
      setBusy((b) => new Set(b).add(slug));
      setRowError((m) => {
        const n = { ...m };
        delete n[slug];
        return n;
      });
      try {
        const next = await new ApiClient(accessToken).setCapability(
          slug,
          isOn ? "detach" : "attach",
        );
        setCfg(next);
        onChanged(); // re-compose the grid (card appears / disappears).
      } catch (err) {
        const msg =
          err instanceof ApiClientError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Could not update this module.";
        setRowError((m) => ({ ...m, [slug]: msg }));
      } finally {
        setBusy((b) => {
          const n = new Set(b);
          n.delete(slug);
          return n;
        });
      }
    },
    [accessToken, onChanged],
  );

  if (!open) return null;

  const declared = cfg?.declared ?? [];
  const onCount = cfg?.enabled.length ?? 0;
  const availableCount = availableRows.length;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label="Compose your dashboard"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="panel relative max-h-[90vh] w-full max-w-2xl animate-rise-in overflow-auto">
        {/* close */}
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute right-4 top-4 grid h-8 w-8 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted transition-colors hover:border-line-strong hover:text-text"
        >
          <span className="text-lg leading-none">&times;</span>
        </button>

        {/* head */}
        <div className="border-b border-line px-6 py-5">
          <p className="eyebrow mb-2">Compose</p>
          <h2 className="font-display text-2xl font-600 tracking-tight text-text">
            Your composition -- pull what you need
          </h2>
          <p className="mt-2 max-w-lg text-sm text-text-muted">
            This is YOUR decentralized dashboard. Pull a capability from the platform
            catalog and its card appears on your grid; remove one and it leaves. You compose
            the surface -- nothing here is a capability your tenant does not declare.
          </p>
          {cfg && (
            <p className="mt-3 font-mono text-2xs text-text-faint">
              {onCount} on . {availableCount} available . {declared.length} declared
            </p>
          )}
        </div>

        <div className="px-6 py-5">
          {/* load error */}
          {loadError && (
            <div
              role="alert"
              className="mb-4 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
            >
              <span className="mt-0.5 shrink-0">
                <AlertIcon />
              </span>
              <span className="flex-1">{loadError}</span>
              <button
                onClick={load}
                className="shrink-0 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-text"
              >
                retry
              </button>
            </div>
          )}

          {/* loading */}
          {loading && !cfg ? (
            <div className="flex items-center gap-3 py-12 text-text-muted">
              <Spinner />
              <span className="font-mono text-2xs uppercase tracking-wider">
                loading catalog
              </span>
            </div>
          ) : declared.length === 0 && !loadError ? (
            <div className="rounded-card border border-dashed border-line px-6 py-12 text-center text-text-muted">
              <p className="font-display text-lg text-text">No modules declared</p>
              <p className="mt-1 text-sm">
                This tenant&apos;s overlay declares no capability modules to compose.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-6">
              {/* ---- AVAILABLE TO ADD (the pull-set: declared-but-disabled) ---- */}
              <section>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <p className="eyebrow">// available to add</p>
                  <span className="font-mono text-2xs text-text-faint">
                    {availableCount}
                  </span>
                </div>
                {availableRows.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-line px-4 py-6 text-center text-2xs text-text-muted">
                    <span className="inline-flex items-center gap-1.5">
                      <CheckIcon />
                      Everything declared is already on your dashboard.
                    </span>
                  </div>
                ) : (
                  <ul className="flex flex-col gap-2">
                    {availableRows.map((row) => (
                      <ModuleRow
                        key={row.slug}
                        row={row}
                        busy={busy.has(row.slug)}
                        error={rowError[row.slug]}
                        onToggle={() => toggle(row.slug, row.on)}
                      />
                    ))}
                  </ul>
                )}
              </section>

              {/* ---- IN YOUR DASHBOARD (the enabled set) ---- */}
              <section>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <p className="eyebrow">// in your dashboard</p>
                  <span className="font-mono text-2xs text-text-faint">{onCount}</span>
                </div>
                {enabledRows.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-line px-4 py-6 text-center text-2xs text-text-muted">
                    Nothing pulled yet -- add a capability above to start your composition.
                  </div>
                ) : (
                  <ul className="flex flex-col gap-2">
                    {enabledRows.map((row) => (
                      <ModuleRow
                        key={row.slug}
                        row={row}
                        busy={busy.has(row.slug)}
                        error={rowError[row.slug]}
                        onToggle={() => toggle(row.slug, row.on)}
                      />
                    ))}
                  </ul>
                )}
              </section>
            </div>
          )}

          {/* footer: manual refresh + provenance */}
          <div className="mt-6 flex items-center justify-between border-t border-line pt-4">
            <span className="font-mono text-2xs text-text-faint">
              overlay-driven . per-tenant . you compose the surface
            </span>
            <button
              onClick={load}
              disabled={loading}
              className="btn-ghost text-sm disabled:opacity-40"
            >
              <RefreshIcon />
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
