"use client";

// ----------------------------------------------------------------------------
// /dashboard/data/[entity] -- ONE managed entity, rendered by <DataManager/>.
//
// The route is fully generic + OVERLAY-SOURCED: it resolves the EntitySchema by
// slug from the tenant overlay (via ApiClient.listEntitySchemas, fixtures or live)
// and hands it to the schema-driven DataManager. There is no per-entity code here
// -- any tenant entity declared in its overlay gets a working table +
// create/edit/delete from this single route. A slug that is not a managed entity
// for this tenant renders the "unknown entity" state.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { getEntitySchema } from "@/lib/entities";
import { DataManager } from "@/components/DataManager";
import type { EntitySchema } from "@/lib/types";
import { ArrowRight, TableIcon } from "@/components/icons";
import { Spinner } from "@/components/ui";

export default function EntityPage() {
  const params = useParams<{ entity: string }>();
  const slug = typeof params.entity === "string" ? params.entity : "";

  const { session } = useAuth();
  const token = session?.access_token ?? "";
  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);

  // undefined = still resolving; null = not a managed entity; schema = resolved.
  const [schema, setSchema] = useState<EntitySchema | null | undefined>(
    undefined,
  );
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!client || !slug) return;
    setError(null);
    try {
      setSchema(await getEntitySchema(client, slug));
    } catch (err) {
      setError(
        err instanceof ApiClientError || err instanceof Error
          ? err.message
          : "Could not load this entity.",
      );
      setSchema(null);
    }
  }, [client, slug]);

  useEffect(() => {
    load();
  }, [load]);

  if (schema === undefined && !error) {
    return (
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading entity
          </span>
        </div>
      </div>
    );
  }

  if (!schema) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
            <TableIcon />
          </span>
          <p className="font-display text-lg text-text">Unknown entity</p>
          <p className="mt-1 text-sm">
            <span className="font-mono text-2xs text-text-faint">{slug}</span> is
            not a managed entity for this tenant.
          </p>
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
          <Link
            href="/dashboard/data"
            className="mt-5 inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
          >
            back to data
            <ArrowRight />
          </Link>
        </div>
      </div>
    );
  }

  // SPEC 10 W5: offer the "New via manifest" affordance only for a publishable entity --
  // that is the product editor the field_manifest mold (productManifest) targets, and the
  // one with a draft/published gate. Other entities keep just the quick-add modal.
  const newManifestHref =
    schema.publishable === true ? `/dashboard/data/${schema.entity}/new` : undefined;

  return <DataManager schema={schema} newManifestHref={newManifestHref} />;
}
