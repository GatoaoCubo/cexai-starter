"use client";

// ----------------------------------------------------------------------------
// /dashboard/data/[entity]/new -- MOUNT the field_manifest mold LIVE (SPEC 10 W5).
//
// The "New via manifest" route. It resolves the EntitySchema by slug (the SAME
// overlay-driven path as /dashboard/data/[entity]) to confirm the slug is a managed,
// writable entity for this tenant, then mounts <ManifestEntityForm/> -- the live
// field_manifest editor that derives its form + validation + publish gate from one
// declarative manifest and, on submit, calls ApiClient.createEntity (POST /entity).
//
// The proof manifest is lib/field-manifest/productManifest (the FIRST field_manifest
// instance). There is NO per-entity code here: the form is generated from the
// manifest, the submit targets the [entity] slug, and a slug that is not managed (or
// is read-only) renders an honest fallback instead of a form.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { getEntitySchema } from "@/lib/entities";
import { ManifestEntityForm } from "@/components/ManifestEntityForm";
import { productManifest } from "@/lib/field-manifest";
import type { EntitySchema } from "@/lib/types";
import { ArrowRight, TableIcon } from "@/components/icons";
import { Spinner } from "@/components/ui";

export default function NewViaManifestPage() {
  const params = useParams<{ entity: string }>();
  const slug = typeof params.entity === "string" ? params.entity : "";

  const { session } = useAuth();
  const token = session?.access_token ?? "";
  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);

  // undefined = resolving; null = not a managed entity; schema = resolved.
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
      <div className="mx-auto max-w-3xl">
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading entity
          </span>
        </div>
      </div>
    );
  }

  // Not a managed entity, or read-only for this role -> no manifest form.
  const writable = schema ? schema.writable !== false : false;
  if (!schema || !writable) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
          <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
            <TableIcon />
          </span>
          <p className="font-display text-lg text-text">
            {schema && !writable ? "Read-only entity" : "Unknown entity"}
          </p>
          <p className="mt-1 text-sm">
            {schema && !writable ? (
              <>
                <span className="font-mono text-2xs text-text-faint">{slug}</span>{" "}
                is read-only for your role -- you cannot create here.
              </>
            ) : (
              <>
                <span className="font-mono text-2xs text-text-faint">{slug}</span>{" "}
                is not a managed entity for this tenant.
              </>
            )}
          </p>
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
          <Link
            href={schema ? `/dashboard/data/${slug}` : "/dashboard/data"}
            className="mt-5 inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
          >
            {schema ? "back to table" : "back to data"}
            <ArrowRight />
          </Link>
        </div>
      </div>
    );
  }

  if (!client) return null;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-5">
        <Link
          href={`/dashboard/data/${slug}`}
          className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
        >
          <span className="rotate-180">
            <ArrowRight />
          </span>
          {schema.plural}
        </Link>
      </div>
      <ManifestEntityForm
        entity={schema.entity}
        singular={schema.singular}
        manifest={productManifest}
        client={client}
      />
    </div>
  );
}
