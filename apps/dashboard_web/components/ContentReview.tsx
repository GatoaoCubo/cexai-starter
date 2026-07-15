"use client";

// =============================================================================
// ContentReview -- the content-review HITL gate (SPEC 10 W5, L3).
// =============================================================================
//
// The human-in-the-loop step that sits BEFORE publish. It lists the tenant's DRAFT
// content (rows whose top-level ``published`` gate is not true) for the entities that
// opted into publishing (EntitySchema.publishable), renders each item for review, and
// offers ONE decision per item:
//
//   * APPROVE -> PUBLISH = ApiClient.setEntityPublished(slug, id, true) -- the EXACT
//     publish seam DataManager's toggle uses (SPEC 10 W1). On success the item leaves
//     the draft list (it is no longer a draft), so the queue shrinks honestly.
//   * KEEP DRAFT = dismiss it from THIS review pass (a local, non-destructive hide --
//     it stays a draft in the data plane; a reload brings it back). No backend write.
//
// HONEST BY CONSTRUCTION:
//   * The queue is REAL drafts read via ApiClient.listEntity -- filtered to
//     ``published !== true`` from each row's own gate field. Nothing is fabricated;
//     an empty queue shows "nada para revisar" (there is nothing to review).
//   * The publish ACTION is the gated W1 seam. In dev/fixtures it flips locally
//     (fxSetEntityPublished); against prod the founder-gated backend authorizes it.
//     This component does not invent a second publish path -- it reuses the client.
//   * tenant_id is NEVER sent (Bearer only; the backend derives it from the JWT).
//
// REUSE: the publish client (api.ts setEntityPublished) + the EntitySchema contract.
// It re-implements neither the publish wire nor a bespoke entity reader.

import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiClient, ApiClientError } from "@/lib/api";
import { config } from "@/lib/config";
import type { EntityRecord, EntitySchema } from "@/lib/types";
import { iconFor, AlertIcon, CheckIcon, LandingIcon } from "./icons";
import { Spinner } from "./ui";

export interface ContentReviewProps {
  /** A live ApiClient bound to the session token (reads drafts + publishes). */
  client: ApiClient;
  /** The tenant's publishable entity schemas (the review queue's sources). */
  schemas: EntitySchema[];
}

/** A draft awaiting review: its source schema + the row + a stable composite key. */
interface DraftItem {
  schema: EntitySchema;
  record: EntityRecord;
  /** entity slug + row id -- unique across entities. */
  key: string;
}

// A row is a DRAFT unless its publish gate is explicitly true (an absent/false gate
// reads as draft -- the SAME truthiness DataManager.isPublished uses, inverted).
function isDraft(record: EntityRecord): boolean {
  return record.published !== true;
}

// The human label for a row: the schema's primary column value, else the id. Honest
// -- it reads the row's real value, never a placeholder.
function rowLabel(schema: EntitySchema, record: EntityRecord): string {
  const primary = schema.columns.find((c) => c.primary);
  if (primary) {
    const v = record[primary.key];
    if (v !== null && v !== undefined && v !== "") return String(v);
  }
  return record.id;
}

export function ContentReview({ client, schemas }: ContentReviewProps) {
  // Only entities that opted into publishing have a draft/published gate to review.
  const publishable = useMemo(
    () => schemas.filter((s) => s.publishable === true),
    [schemas],
  );

  // null = loading; [] = loaded-empty; items = the draft queue.
  const [drafts, setDrafts] = useState<DraftItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  // composite keys the operator chose to keep as draft THIS pass (local hide only).
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  // the composite key whose publish flip is in flight (disables its buttons).
  const [publishingKey, setPublishingKey] = useState<string | null>(null);
  // a brief confirmation of the last item published (provenance for the supervisor).
  const [justPublished, setJustPublished] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    setDrafts(null);
    try {
      // Read each publishable entity's rows and keep the drafts. Per-entity failures
      // surface as an error but never fabricate a row.
      const collected: DraftItem[] = [];
      for (const schema of publishable) {
        const rows = await client.listEntity(schema.entity);
        for (const record of rows) {
          if (isDraft(record)) {
            collected.push({
              schema,
              record,
              key: `${schema.entity}:${record.id}`,
            });
          }
        }
      }
      setDrafts(collected);
    } catch (err) {
      setError(messageOf(err, "Could not load drafts for review."));
      setDrafts([]);
    }
  }, [client, publishable]);

  useEffect(() => {
    load();
  }, [load]);

  // APPROVE -> PUBLISH the item via the W1 seam, then drop it from the queue (it is
  // no longer a draft). A failure surfaces inline and the item stays for another try.
  async function approve(item: DraftItem) {
    setError(null);
    setJustPublished(null);
    setPublishingKey(item.key);
    try {
      await client.setEntityPublished(item.schema.entity, item.record.id, true);
      setDrafts((prev) => (prev ? prev.filter((d) => d.key !== item.key) : prev));
      setJustPublished(rowLabel(item.schema, item.record));
    } catch (err) {
      setError(messageOf(err, "Publish failed."));
    } finally {
      setPublishingKey(null);
    }
  }

  // KEEP DRAFT: hide from THIS pass only (no backend write -- it stays a draft).
  function keepDraft(item: DraftItem) {
    setDismissed((prev) => {
      const next = new Set(prev);
      next.add(item.key);
      return next;
    });
  }

  // The visible queue = loaded drafts minus the ones kept-as-draft this pass.
  const visible = useMemo(
    () => (drafts ?? []).filter((d) => !dismissed.has(d.key)),
    [drafts, dismissed],
  );

  return (
    <div className="mx-auto max-w-4xl">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow mb-2">Review</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-text">
            Content review
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-text-muted">
            The human-in-the-loop gate before publish. Review each draft, then
            approve it to publish (it becomes eligible for the public site) or keep
            it as a draft. Nothing publishes without your approval here.
          </p>
        </div>
        <div className="text-right font-mono text-2xs leading-relaxed text-text-faint">
          {drafts === null ? "loading" : `${visible.length} to review`}
          <br />
          {config.fixtures ? "fixtures" : "live"} . publish gated
        </div>
      </header>

      {justPublished && (
        <div
          role="status"
          className="mt-5 flex items-start gap-2 rounded-lg border border-synapse/30 bg-synapse/5 px-4 py-3 text-sm text-synapse"
        >
          <span className="mt-0.5 shrink-0">
            <CheckIcon />
          </span>
          <span>
            Published <span className="text-text">{justPublished}</span>. It is now
            eligible for the public site.
          </span>
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="mt-5 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{error}</span>
        </div>
      )}

      {/* ---- the queue --------------------------------------------------- */}
      <div className="mt-6">
        {drafts === null && !error ? (
          <div className="flex items-center gap-3 py-16 text-text-muted">
            <Spinner />
            <span className="font-mono text-2xs uppercase tracking-wider">
              loading drafts
            </span>
          </div>
        ) : visible.length === 0 ? (
          <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
            <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
              <CheckIcon />
            </span>
            <p className="font-display text-lg text-text">Nada para revisar</p>
            <p className="mt-1 text-sm">
              {publishable.length === 0
                ? "No publishable entity is declared for this tenant yet."
                : "There are no drafts waiting for review. Everything is published or there is nothing to publish."}
            </p>
          </div>
        ) : (
          <ul className="space-y-4">
            {visible.map((item, i) => (
              <ReviewCard
                key={item.key}
                item={item}
                index={i}
                busy={publishingKey === item.key}
                onApprove={() => approve(item)}
                onKeepDraft={() => keepDraft(item)}
              />
            ))}
          </ul>
        )}
      </div>

      {drafts && visible.length > 0 && (
        <footer className="mt-5 flex flex-wrap items-center justify-between gap-2 font-mono text-2xs text-text-faint">
          <span>
            {visible.length} {visible.length === 1 ? "draft" : "drafts"} awaiting
            review
          </span>
          <span>
            approve =&gt; publish (W1 seam) . {config.fixtures ? "fixtures" : "live"}{" "}
            . RLS by tenant_id
          </span>
        </footer>
      )}
    </div>
  );
}

// --- ReviewCard --------------------------------------------------------------

/**
 * One draft rendered for human review: the entity + label + the row's own fields
 * (read-only, the REAL values), and the two decisions. The publish action reuses the
 * W1 seam through the parent; keep-draft is a local hide. Honest -- it surfaces what
 * the row actually contains, never a fabricated preview.
 */
function ReviewCard({
  item,
  index,
  busy,
  onApprove,
  onKeepDraft,
}: {
  item: DraftItem;
  index: number;
  busy: boolean;
  onApprove: () => void;
  onKeepDraft: () => void;
}) {
  const { schema, record } = item;
  const Icon = iconFor(schema.icon ?? "table");
  const label = rowLabel(schema, record);

  // The fields to preview: the schema's declared columns (their real row values),
  // excluding admin_only (the margin guard) so a sensitive value never shows here.
  const previewCols = schema.columns.filter((c) => !c.admin_only && !c.primary);

  return (
    <li
      style={{ animationDelay: `${index * 40}ms` }}
      className="animate-rise-in rounded-card border border-line bg-panel p-5"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <span className="mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted">
            <Icon />
          </span>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                {schema.singular}
              </span>
              {/* honest draft chip -- straight from the row's gate */}
              <span className="inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider text-text-faint">
                <span className="h-1.5 w-1.5 rounded-full bg-line-strong" />
                draft
              </span>
            </div>
            <h3 className="mt-1 truncate font-display text-lg font-600 tracking-tight text-text">
              {label}
            </h3>
            <p className="mt-0.5 font-mono text-2xs text-text-faint">
              entity={schema.entity} . id={record.id}
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={onKeepDraft}
            disabled={busy}
            className="btn-ghost disabled:opacity-40"
          >
            Keep draft
          </button>
          <button
            type="button"
            onClick={onApprove}
            disabled={busy}
            aria-label={`Approve and publish ${schema.singular}`}
            className="btn-primary disabled:opacity-40"
          >
            {busy ? (
              <>
                <Spinner className="h-3.5 w-3.5" />
                Publishing...
              </>
            ) : (
              <>
                <LandingIcon />
                Approve & publish
              </>
            )}
          </button>
        </div>
      </div>

      {/* the row's real fields, read-only -- what the supervisor is approving */}
      {previewCols.length > 0 && (
        <dl className="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 border-t border-line pt-4 sm:grid-cols-2">
          {previewCols.map((c) => {
            const v = record[c.key];
            const text =
              v === null || v === undefined || v === "" ? "--" : String(v);
            return (
              <div key={c.key} className="flex items-baseline justify-between gap-3">
                <dt className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                  {c.label}
                </dt>
                <dd className="truncate text-right text-sm text-text-muted">
                  {text}
                </dd>
              </div>
            );
          })}
        </dl>
      )}
    </li>
  );
}

// --- shared error normalizer -------------------------------------------------

function messageOf(err: unknown, fallback: string): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return fallback;
}
