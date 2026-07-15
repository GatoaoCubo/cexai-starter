"use client";

// ----------------------------------------------------------------------------
// /dashboard/review -- the content-review HITL gate (SPEC 10 W5).
//
// Loads the tenant's entity schemas (the SAME overlay-driven path as /dashboard/data
// via ApiClient.listEntitySchemas) and hands them to <ContentReview/>, which lists the
// DRAFT rows (published !== true) of the publishable entities, renders each for human
// review, and offers APPROVE -> PUBLISH (the W1 publish seam, ApiClient.setEntityPublished)
// or keep-draft. The review IS the gate: nothing publishes without a human approval here.
//
// There is no per-entity code here -- the queue is generated from the publishable
// schemas. tenant_id is read from the session; never sent (Bearer only).
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { getEntitySchemas } from "@/lib/entities";
import { ContentReview } from "@/components/ContentReview";
import type { EntitySchema } from "@/lib/types";
import { Spinner } from "@/components/ui";

export default function ReviewPage() {
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

  if (schemas === null && !error) {
    return (
      <div className="mx-auto max-w-4xl">
        <div className="flex items-center gap-3 py-16 text-text-muted">
          <Spinner />
          <span className="font-mono text-2xs uppercase tracking-wider">
            loading review queue
          </span>
        </div>
      </div>
    );
  }

  if (!client) return null;

  // A failed schema load still mounts ContentReview with an empty list (it renders the
  // honest "nada para revisar" empty state) rather than a blank page.
  return <ContentReview client={client} schemas={schemas ?? []} />;
}

function messageOf(err: unknown, fallback: string): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return fallback;
}
