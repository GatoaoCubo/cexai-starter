"use client";

// ----------------------------------------------------------------------------
// /dashboard/data -- the management INDEX (the "what can I manage?" list).
//
// TENANT-DRIVEN + OVERLAY-SOURCED: the entity cards come from the tenant overlay
// via ApiClient.listEntitySchemas() (GET /entities-config in live mode, fixtures
// in fixtures mode -- the same path the capability cards take). A tenant with no
// declared entities sees the empty state; each declared entity links to
// /dashboard/data/[entity] where <DataManager/> renders its table + form from the
// schema alone. Nothing is hardcoded per entity -- this index is generated from
// the overlay-loaded list. tenant_id is read from the session; never sent.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { getEntitySchemas } from "@/lib/entities";
import type { EntitySchema } from "@/lib/types";
import { iconFor, ArrowRight, TableIcon } from "@/components/icons";
import { Spinner } from "@/components/ui";

export default function DataIndexPage() {
  const { session } = useAuth();
  const token = session?.access_token ?? "";
  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);

  const [schemas, setSchemas] = useState<EntitySchema[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!client) return;
    setError(null);
    try {
      setSchemas(await getEntitySchemas(client));
    } catch (err) {
      setError(messageOf(err, "Could not load your entities."));
      setSchemas([]);
    }
  }, [client]);

  useEffect(() => {
    load();
  }, [load]);

  const count = schemas?.length ?? 0;

  return (
    <div className="mx-auto max-w-6xl">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Manage</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Your data
          </h1>
          <p className="mt-2 max-w-xl text-sm text-text-muted">
            The entities your tenant manages. Each table + edit form is generated
            from a schema declared in your overlay -- add your own (products,
            contacts, leads); the management surface adapts with no code change.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          {schemas === null ? "loading" : `${count} ${count === 1 ? "entity" : "entities"}`}
          <br />
          schema-driven CRUD
        </div>
      </header>

      {error && (
        <div
          role="alert"
          className="mt-6 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span>{error}</span>
        </div>
      )}

      {schemas === null && !error ? (
        <div className="mt-8 flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading entities
          </span>
        </div>
      ) : count === 0 && !error ? (
        <div className="mt-8 rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
            <TableIcon />
          </span>
          <p className="font-display text-lg text-text">No managed entities</p>
          <p className="mt-1 text-sm">
            This tenant&apos;s overlay declares no manageable entities yet.
          </p>
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(schemas ?? []).map((s, i) => {
            const Icon = iconFor(s.icon ?? "table");
            return (
              <Link
                key={s.entity}
                href={`/dashboard/data/${s.entity}`}
                style={{ animationDelay: `${i * 45}ms` }}
                className="group relative flex animate-rise-in flex-col overflow-hidden rounded-card border border-line bg-panel p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-synapse/40 hover:shadow-glow-soft"
              >
                <div className="flex items-start justify-between">
                  <span className="grid h-11 w-11 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted transition-colors duration-300 group-hover:border-synapse/40 group-hover:text-synapse">
                    <Icon />
                  </span>
                  <div className="flex items-center gap-1.5">
                    {s.writable === false && (
                      <span className="chip">read-only</span>
                    )}
                    {s.nucleus && <span className="chip">{s.nucleus}</span>}
                  </div>
                </div>
                <h3 className="mt-4 font-display text-lg font-600 tracking-tight text-text">
                  {s.plural}
                </h3>
                {s.description && (
                  <p className="mt-1.5 line-clamp-2 text-sm text-text-muted">
                    {s.description}
                  </p>
                )}
                <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                  <span className="font-mono text-2xs text-text-faint">
                    entity={s.entity}
                  </span>
                  <span className="inline-flex items-center gap-1 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors group-hover:text-synapse">
                    open
                    <ArrowRight />
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

// --- shared error normalizer -------------------------------------------------

function messageOf(err: unknown, fallback: string): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return fallback;
}
