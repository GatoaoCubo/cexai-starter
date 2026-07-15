"use client";

// ----------------------------------------------------------------------------
// /dashboard/settings -- the settings / tenant SHELL (cross-cutting, not a card).
//
// Three sections, all TENANT-DRIVEN via ApiClient.getSettings():
//   1. tenant context     -- tenant_id / label / operator, from the session
//   2. integrations       -- status list from the overlay (connection state only)
//   3. secrets / Vault     -- STATUS-ONLY surface: which secrets are configured.
//
// SECURE-BY-DEFAULT -- the cornerstone of this shell:
//   * The TenantSettings shape has NO secret value field anywhere (lib/types).
//     The backend reports only whether each NAMED secret is configured. The
//     client therefore cannot render a value -- it never receives one.
//   * Even the secret NAMES are shown read-only; there is no reveal affordance.
//   * tenant_id is read from the session, never set by the client.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { brandbookCard } from "@/lib/fixtures";
import type { TenantSettings } from "@/lib/types";
import { RunModal } from "@/components/RunModal";
import { Spinner, StatusPill } from "@/components/ui";
import {
  AlertIcon,
  BrandMark,
  CheckIcon,
  KeyIcon,
  LockIcon,
  PlugIcon,
} from "@/components/icons";

export default function SettingsPage() {
  const { session } = useAuth();
  const [data, setData] = useState<TenantSettings | null>(null);
  const [error, setError] = useState<string | null>(null);
  // B2: the brand-setup run flow -- the same RunModal the grid uses, opened from the Brand section.
  const [brandRunOpen, setBrandRunOpen] = useState(false);

  const token = session?.access_token ?? "";

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      setData(await new ApiClient(token).getSettings());
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Could not load settings.";
      setError(msg);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  // Identity falls back to the session (always present) even before /settings loads.
  const tenantLabel = data?.tenant_label || session?.tenant_label || "Tenant";
  const tenantId = data?.tenant_id || session?.tenant_id || "";
  const operator = data?.operator_email || session?.email || "";

  return (
    <div className="mx-auto max-w-4xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Tenant</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Settings
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            Your tenant context, wired integrations, and the secret surface.
            Secrets show configured status only -- values live in the Vault and
            are never sent to the browser.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          tenant={tenantLabel}
          <br />
          {config.fixtures ? "fixtures" : "live"} . tenant_settings
        </div>
      </header>

      {error && (
        <div
          role="alert"
          className="mt-6 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{error}</span>
        </div>
      )}

      {/* ---- 1. tenant context ------------------------------------------- */}
      <section className="mt-8">
        <p className="eyebrow mb-4">// tenant context</p>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="panel px-5 py-4">
            <p className="font-mono text-2xs uppercase tracking-wider text-text-faint">
              Tenant
            </p>
            <p className="mt-1.5 font-display text-base font-600 text-text">
              {tenantLabel}
            </p>
          </div>
          <div className="panel px-5 py-4">
            <p className="font-mono text-2xs uppercase tracking-wider text-text-faint">
              Tenant ID
            </p>
            <p
              className="mt-1.5 truncate font-mono text-xs text-text-muted"
              title={tenantId}
            >
              {tenantId || "unbound"}
            </p>
          </div>
          <div className="panel px-5 py-4">
            <p className="font-mono text-2xs uppercase tracking-wider text-text-faint">
              Operator
            </p>
            <p
              className="mt-1.5 truncate text-sm text-text-muted"
              title={operator}
            >
              {operator || "--"}
            </p>
          </div>
        </div>
        {data?.identity_note && (
          <p className="mt-3 flex items-start gap-2 rounded-lg border border-line bg-panel-sunken px-4 py-3 text-sm text-text-muted">
            <span className="mt-0.5 shrink-0 text-synapse">
              <LockIcon />
            </span>
            {data.identity_note}
          </p>
        )}
      </section>

      {/* ---- B2: brand / marca (the brand-setup path) -------------------- */}
      <section className="mt-9">
        <p className="eyebrow mb-4 flex items-center gap-2">
          <BrandMark width={15} height={15} />
          // marca . brand
        </p>
        <div className="rounded-card border border-line bg-panel p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0 max-w-xl">
              <p className="font-display text-base font-600 text-text">
                Configure a sua marca
              </p>
              <p className="mt-1.5 text-sm text-text-muted">
                Envie o logotipo, o site/brand book e a paleta de cores. O CEXAI gera o{" "}
                <span className="text-text">brand book completo</span> e grava a config da
                sua marca -- a partir dai{" "}
                <span className="text-text">toda capacidade sai na sua marca</span> (nome,
                cores e voz difundidos automaticamente). A marca nunca e fixa no codigo: e
                uma variavel preenchida com os seus valores.
              </p>
              <p className="mt-2 inline-flex items-center gap-1.5 rounded-md border border-danger/30 bg-danger/5 px-2 py-1 font-mono text-2xs text-danger">
                amostra -- dados simulados ate rodar com os seus materiais
              </p>
            </div>
            <button
              type="button"
              onClick={() => setBrandRunOpen(true)}
              className="btn-primary shrink-0"
            >
              <BrandMark width={15} height={15} />
              Gerar brand book
            </button>
          </div>
        </div>
      </section>

      {/* loading shimmer for the data-dependent sections */}
      {data === null && !error ? (
        <div className="mt-8 flex items-center gap-3 py-10 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading settings
          </span>
        </div>
      ) : (
        data && (
          <>
            {/* ---- 2. integrations ------------------------------------- */}
            <section className="mt-9">
              <p className="eyebrow mb-4 flex items-center gap-2">
                <PlugIcon />
                // integrations
              </p>
              {data.integrations.length === 0 ? (
                <p className="rounded-card border border-dashed border-line px-6 py-10 text-center text-sm text-text-muted">
                  No integrations declared in this tenant&apos;s overlay.
                </p>
              ) : (
                <div className="overflow-hidden rounded-card border border-line">
                  <ul>
                    {data.integrations.map((it, i) => (
                      <li
                        key={it.key}
                        style={{ animationDelay: `${i * 35}ms` }}
                        className="flex animate-rise-in items-center justify-between gap-3 border-b border-line bg-panel px-5 py-3.5 last:border-b-0"
                      >
                        <div className="min-w-0">
                          <p className="font-display text-sm font-600 text-text">
                            {it.label}
                          </p>
                          {it.detail && (
                            <p className="mt-0.5 truncate font-mono text-2xs text-text-faint">
                              {it.detail}
                            </p>
                          )}
                        </div>
                        <StatusPill state={it.state} />
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>

            {/* ---- 3. secrets / Vault (STATUS ONLY) -------------------- */}
            <section className="mt-9">
              <p className="eyebrow mb-4 flex items-center gap-2">
                <KeyIcon />
                // secrets . vault
              </p>

              {/* the secure-by-default contract, stated to the operator */}
              <div className="mb-4 flex items-start gap-2 rounded-lg border border-synapse/20 bg-synapse/[0.04] px-4 py-3 text-sm text-text-muted">
                <span className="mt-0.5 shrink-0 text-synapse">
                  <LockIcon />
                </span>
                <span>
                  <span className="text-text">Status only.</span> Values live in
                  the Vault and are never sent to the browser. This surface shows
                  which named secrets are configured -- nothing more.
                </span>
              </div>

              {data.secrets.length === 0 ? (
                <p className="rounded-card border border-dashed border-line px-6 py-10 text-center text-sm text-text-muted">
                  No secrets declared for this tenant.
                </p>
              ) : (
                <div className="overflow-hidden rounded-card border border-line">
                  {/* header */}
                  <div className="hidden grid-cols-[1.6fr_1fr_0.8fr] gap-4 border-b border-line bg-panel-sunken px-5 py-2.5 font-mono text-2xs uppercase tracking-wider text-text-faint sm:grid">
                    <span>Secret</span>
                    <span>Last rotated</span>
                    <span className="text-right">Status</span>
                  </div>
                  <ul>
                    {data.secrets.map((s, i) => (
                      <li
                        key={s.name}
                        style={{ animationDelay: `${i * 35}ms` }}
                        className="grid animate-rise-in grid-cols-1 gap-2 border-b border-line bg-panel px-5 py-3.5 last:border-b-0 sm:grid-cols-[1.6fr_1fr_0.8fr] sm:items-center sm:gap-4"
                      >
                        <div className="min-w-0">
                          {/* the NAME only -- there is no value to show */}
                          <p className="truncate font-mono text-xs text-text">
                            {s.name}
                          </p>
                          {s.label && (
                            <p className="mt-0.5 truncate text-2xs text-text-faint">
                              {s.label}
                            </p>
                          )}
                        </div>
                        <span className="font-mono text-2xs text-text-muted">
                          {s.last_rotated
                            ? new Date(s.last_rotated).toLocaleDateString()
                            : "--"}
                        </span>
                        <span className="sm:text-right">
                          {s.configured ? (
                            <span className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-synapse">
                              <CheckIcon />
                              configured
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-faint">
                              <span className="h-1.5 w-1.5 rounded-full bg-line-strong" />
                              missing
                            </span>
                          )}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <p className="mt-3 font-mono text-2xs text-text-faint">
                Rotation is operator-gated and happens in the Vault -- not here.
                Rotate once; every PC re-pulls.
              </p>
            </section>
          </>
        )
      )}

      {/* B2: brand-setup run flow -- the SAME RunModal the capability grid uses (upload ->
          run -> brand book + dual-output upload face). Running it writes the tenant brand
          config so every other capability re-personalizes. */}
      <RunModal
        card={brandRunOpen ? brandbookCard : null}
        tenantId={tenantId}
        tenantLabel={tenantLabel}
        accessToken={token}
        onClose={() => setBrandRunOpen(false)}
      />
    </div>
  );
}
