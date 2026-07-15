"use client";

// ----------------------------------------------------------------------------
// /dashboard -- the Capabilities grid (the "function matrix").
//
// The organic, per-tenant capability cards. The grid + masthead mirror the locked
// visual target (public/showcase.html): a masthead with a tenant console line, a
// stat hero strip, a "// capabilities" section label, then the card grid. Clicking
// an enabled card opens the RunModal (card -> intent -> 8F run -> result).
//
// Data source is mode-transparent: ApiClient.listCards() returns fixtures in
// FIXTURES mode and the live /capabilities cards otherwise -- the component is
// identical in both. tenant_id is read from the session, never set here.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import type { Card } from "@/lib/types";
import { CapabilityCard } from "@/components/CapabilityCard";
import { ModuleManager } from "@/components/ModuleManager";
import { RunModal } from "@/components/RunModal";
import { Spinner } from "@/components/ui";
import { AlertIcon, PlusIcon } from "@/components/icons";

export default function CapabilitiesPage() {
  const { session } = useAuth();
  const [cards, setCards] = useState<Card[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState<Card | null>(null);
  const [manageOpen, setManageOpen] = useState(false);

  const token = session?.access_token ?? "";

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const list = await new ApiClient(token).listCards();
      setCards(list);
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load capabilities.";
      setError(msg);
      setCards([]);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  // Honest stat hero -- derived from the loaded cards, not invented.
  const stats = useMemo(() => {
    const all = cards ?? [];
    const enabled = all.filter((c) => c.enabled).length;
    const overlay = all.filter((c) => c.source === "overlay").length;
    const nuclei = new Set(all.map((c) => c.nucleus)).size;
    return [
      { label: "capabilities", value: all.length },
      { label: "enabled", value: enabled },
      { label: "custom (overlay)", value: overlay },
      { label: "nuclei wired", value: nuclei },
    ];
  }, [cards]);

  const tenantLabel = session?.tenant_label || "Tenant";
  const tenantId = session?.tenant_id || "";

  return (
    <div className="mx-auto max-w-6xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Capability console</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            What do you want to create?
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Every card fires the 8-function pipeline, scoped to your tenant. The
            result lands in your own data plane, isolated by RLS.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          8F=ready . RLS=on . {config.fixtures ? "fixtures" : "live"} . CEXAI core
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
              {cards === null ? "--" : s.value}
            </b>
            <span className="mt-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted">
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {/* ---- the grid ---------------------------------------------------- */}
      <div className="mt-10 mb-4 flex items-center justify-between gap-3">
        <p className="eyebrow">// capabilities</p>
        <button
          type="button"
          onClick={() => setManageOpen(true)}
          className="btn-ghost text-sm"
          aria-haspopup="dialog"
        >
          <PlusIcon />
          Add module
        </button>
      </div>

      {error && (
        <div
          role="alert"
          className="mb-5 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{error}</span>
        </div>
      )}

      {cards === null ? (
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading capabilities
          </span>
        </div>
      ) : cards.length === 0 && !error ? (
        <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <p className="font-display text-lg text-text">No capabilities yet</p>
          <p className="mt-1 text-sm">
            This tenant&apos;s overlay exposes no enabled capabilities.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cards.map((card, i) => (
            <CapabilityCard
              key={card.capability}
              card={card}
              index={i}
              onOpen={setActive}
            />
          ))}
        </div>
      )}

      {/* ---- footer note (mirrors the showcase "same engine" line) ------- */}
      <footer className="mt-12 border-t border-line pt-5 text-sm text-text-muted">
        <span className="text-text">Same framework. Your own dashboard.</span>{" "}
        Each card runs the CEXAI 8F pipeline scoped to{" "}
        <span className="font-mono text-2xs text-text-faint">tenant={tenantLabel}</span>:
        your credential, your Supabase, isolated by RLS on tenant_id.
      </footer>

      {/* ---- run flow ---------------------------------------------------- */}
      <RunModal
        card={active}
        tenantId={tenantId}
        tenantLabel={session?.tenant_label}
        accessToken={token}
        onClose={() => setActive(null)}
      />

      {/* ---- compose flow (attach / detach modules) ---------------------- */}
      <ModuleManager
        open={manageOpen}
        accessToken={token}
        cards={cards ?? []}
        onClose={() => setManageOpen(false)}
        onChanged={load}
      />
    </div>
  );
}
