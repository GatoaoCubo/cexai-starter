"use client";

// ----------------------------------------------------------------------------
// DataManager -- the reusable, SCHEMA-DRIVEN management primitive (the mold's
// "CRUD half"). Hand it an EntitySchema and it renders:
//
//   * a DataTable (columns from schema.columns)
//   * a create button + an edit form modal (fields from schema.fields)
//   * delete (with a confirm step)
//
// It is ENTITY-AGNOSTIC: nothing about products / contacts / leads is baked in.
// Any tenant entity plugs in by passing its schema -- the component is identical.
// Records are plain key/value maps (EntityRecord), so one table serves all shapes.
//
// SECURE-BY-DEFAULT:
//   * every read/write goes through ApiClient (auth'd Bearer); the client NEVER
//     sends tenant_id (the backend derives it from the JWT, RLS is the boundary).
//   * if schema.writable === false the surface is READ-ONLY (no create/edit/
//     delete affordances render at all) -- a role/permission can disable writes
//     without changing the component.
//   * MARGIN GUARD: any column/field flagged ``admin_only`` is EXCLUDED from the
//     default view BY CONSTRUCTION -- it never reaches the table or the form. A
//     tenant marks cost/price/margin columns admin_only in its overlay and the
//     leak is prevented for EVERY tenant entity, not by a per-tenant opt-in. The
//     filter lives here (one place), so no per-entity code can forget it.
//
// Mode-transparent: fixtures vs live is entirely inside ApiClient.
// ----------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ApiClient, ApiClientError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { usePagination } from "@/lib/pagination";
import type {
  EntityField,
  EntityRecord,
  EntitySchema,
  FieldValue,
} from "@/lib/types";
import { iconFor } from "./icons";
import {
  AlertIcon,
  LandingIcon,
  PencilIcon,
  PlusIcon,
  RefreshIcon,
  TrashIcon,
} from "./icons";
import { Pagination, Spinner } from "./ui";

// SPEC 10 W1: a row's PUBLISHED state is its top-level ``published`` column (the L2 publish
// gate). EntityManager.list() surfaces it as a real boolean (or absent on a non-publishable /
// legacy row); read it truthily so an absent/false gate reads as draft and only an explicit
// true reads as published.
function isPublished(record: EntityRecord): boolean {
  return record.published === true;
}

// Stable empty fallback so usePagination's source identity does not churn while
// records are still null/loading.
const EMPTY_RECORDS: EntityRecord[] = [];

interface Props {
  schema: EntitySchema;
  /**
   * SPEC 10 W5 -- optional "New via manifest" affordance. When set (and the entity is
   * writable), a secondary link renders next to "New" that opens the field_manifest
   * editor (the schema-to-form mold) at this href. Absent -> no link (zero-regression:
   * the masthead is byte-identical to before). The quick-add modal is unaffected.
   */
  newManifestHref?: string;
}

// --- value formatting (presentation only -- never logic) ---------------------

function formatCell(value: FieldValue, type?: string): string {
  if (value === null || value === undefined || value === "") return "--";
  switch (type) {
    case "currency": {
      const n = typeof value === "number" ? value : Number(value);
      if (Number.isNaN(n)) return String(value);
      // Brand-neutral grouping; no locale/currency assumption baked in.
      return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    case "number": {
      const n = typeof value === "number" ? value : Number(value);
      return Number.isNaN(n) ? String(value) : n.toLocaleString();
    }
    case "date": {
      const t = new Date(String(value)).getTime();
      if (Number.isNaN(t)) return String(value);
      const mins = Math.max(0, Math.round((Date.now() - t) / 60000));
      if (mins < 1) return "just now";
      if (mins < 60) return `${mins}m ago`;
      const hrs = Math.round(mins / 60);
      if (hrs < 24) return `${hrs}h ago`;
      return `${Math.round(hrs / 24)}d ago`;
    }
    case "boolean":
      return value ? "yes" : "no";
    default:
      return String(value);
  }
}

/**
 * SECURE-BY-DEFAULT margin guard: return a copy of the schema with every
 * ``admin_only`` column AND field removed. This is the single chokepoint -- the
 * filtered schema is what the table + form consume, so a sensitive column (cost /
 * B2B price / margin) can NEVER render in the default view for any tenant entity.
 * (The wire-level ``EntitySchema`` keeps the full declaration; only the rendered
 * surface is narrowed. The backend RLS + projection are the authority; this is
 * defence-in-depth on the presentation layer.)
 */
function viewSchema(schema: EntitySchema): EntitySchema {
  return {
    ...schema,
    columns: schema.columns.filter((c) => !c.admin_only),
    fields: schema.fields.filter((f) => !f.admin_only),
  };
}

/** Seed an empty form from the schema's fields (typed defaults). */
function emptyForm(fields: EntityField[]): Record<string, FieldValue> {
  const out: Record<string, FieldValue> = {};
  for (const f of fields) {
    out[f.key] =
      f.type === "boolean" ? false : f.type === "number" ? "" : "";
  }
  return out;
}

/** Pull only the schema's field keys out of a record (for editing). */
function formFromRecord(
  fields: EntityField[],
  record: EntityRecord,
): Record<string, FieldValue> {
  const out: Record<string, FieldValue> = {};
  for (const f of fields) {
    const v = record[f.key];
    out[f.key] = v === undefined ? (f.type === "boolean" ? false : "") : v;
  }
  return out;
}

export function DataManager({ schema: rawSchema, newManifestHref }: Props) {
  const { session } = useAuth();
  const token = session?.access_token ?? "";

  // MARGIN GUARD: render only the non-admin_only columns/fields. Computed once so
  // the table, form, validation, and submit all operate on the SAME narrowed set.
  const schema = useMemo(() => viewSchema(rawSchema), [rawSchema]);
  const writable = schema.writable !== false;
  // SPEC 10 W1: the L2 publish gate. Only renders when the entity opted in (overlay
  // ``publishable: true``) AND writes are allowed (publishing is a write).
  const publishable = schema.publishable === true && writable;

  const [rows, setRows] = useState<EntityRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  // editing === undefined -> closed; null -> creating; record -> editing it.
  const [editing, setEditing] = useState<EntityRecord | null | undefined>(
    undefined,
  );
  const [confirmDelete, setConfirmDelete] = useState<EntityRecord | null>(null);
  // the id of the row whose publish flip is in flight (disables its toggle).
  const [publishingId, setPublishingId] = useState<string | null>(null);

  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);
  const Icon = iconFor(schema.icon ?? "table");

  const load = useCallback(async () => {
    if (!client) return;
    setError(null);
    try {
      setRows(await client.listEntity(schema.entity));
    } catch (err) {
      setError(messageOf(err, "Could not load records."));
      setRows([]);
    }
  }, [client, schema.entity]);

  useEffect(() => {
    load();
  }, [load]);

  // Client-side window over the loaded records (the fetch is already server-capped
  // at 200). A reload resets to page 1; single-page tables render no control.
  const pager = usePagination(rows ?? EMPTY_RECORDS, 25);

  async function remove(record: EntityRecord) {
    if (!client) return;
    setError(null);
    try {
      await client.deleteEntity(schema.entity, record.id);
      setConfirmDelete(null);
      await load();
    } catch (err) {
      setError(messageOf(err, "Delete failed."));
    }
  }

  // SPEC 10 W1: flip ONE row's PUBLISHED gate (publish | unpublish) via the auth'd
  // PATCH /entity/{slug}/{id}/publish. tenant_id is NEVER sent (the client passes only the
  // Bearer; the backend derives the tenant from the JWT). Optimistic-then-reconcile: we reload
  // so the row reflects the backend's authoritative {published, published_at}. A failure surfaces
  // inline and the table is reloaded (so the toggle never shows a state the backend rejected).
  async function togglePublish(record: EntityRecord) {
    if (!client) return;
    setError(null);
    setPublishingId(record.id);
    const next = !isPublished(record);
    try {
      await client.setEntityPublished(schema.entity, record.id, next);
      await load();
    } catch (err) {
      setError(
        messageOf(err, next ? "Publish failed." : "Unpublish failed."),
      );
    } finally {
      setPublishingId(null);
    }
  }

  return (
    <div className="mx-auto max-w-6xl">
      {/* ---- masthead ---------------------------------------------------- */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div className="flex items-start gap-3.5">
          <span className="mt-0.5 grid h-11 w-11 shrink-0 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted">
            <Icon />
          </span>
          <div>
            <p className="eyebrow mb-2">Manage</p>
            <h1 className="font-display text-3xl font-600 tracking-tight text-text">
              {schema.plural}
            </h1>
            {schema.description && (
              <p className="mt-2 max-w-2xl text-sm text-text-muted">
                {schema.description}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            className="btn-ghost"
            aria-label="Refresh"
            title="Refresh"
          >
            <RefreshIcon />
          </button>
          {writable && newManifestHref && (
            <Link href={newManifestHref} className="btn-ghost">
              <PlusIcon />
              New via manifest
            </Link>
          )}
          {writable && (
            <button onClick={() => setEditing(null)} className="btn-primary">
              <PlusIcon />
              New {schema.singular.toLowerCase()}
            </button>
          )}
        </div>
      </header>

      {/* read-only banner when writes are disabled by config/role */}
      {!writable && (
        <div className="mt-5 flex items-center gap-2 rounded-lg border border-line bg-panel-sunken px-4 py-2.5 text-sm text-text-muted">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            read-only
          </span>
          This entity is read-only for your role. Create / edit / delete are
          disabled.
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

      {/* ---- the table --------------------------------------------------- */}
      <div className="mt-6">
        {rows === null ? (
          <div className="flex items-center gap-3 py-16 text-text-muted">
            <Spinner />
            <span className="font-mono text-2xs uppercase tracking-wider">
              loading {schema.plural.toLowerCase()}
            </span>
          </div>
        ) : rows.length === 0 && !error ? (
          <div className="rounded-card border border-dashed border-line px-6 py-16 text-center text-text-muted">
            <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg border border-line bg-panel-sunken text-text-faint">
              <Icon />
            </span>
            <p className="font-display text-lg text-text">
              No {schema.plural.toLowerCase()} yet
            </p>
            <p className="mt-1 text-sm">
              {writable
                ? `Create your first ${schema.singular.toLowerCase()} to populate this table.`
                : "This table is empty."}
            </p>
          </div>
        ) : (
          <DataTable
            schema={schema}
            rows={pager.items}
            writable={writable}
            publishable={publishable}
            publishingId={publishingId}
            onEdit={(r) => setEditing(r)}
            onDelete={(r) => setConfirmDelete(r)}
            onTogglePublish={togglePublish}
          />
        )}
      </div>

      {/* pagination control (renders nothing for a single page) */}
      {rows && rows.length > 0 && (
        <Pagination
          page={pager.page}
          pageCount={pager.pageCount}
          total={pager.total}
          start={pager.start}
          end={pager.end}
          canPrev={pager.canPrev}
          canNext={pager.canNext}
          onPrev={pager.prev}
          onNext={pager.next}
          unit={schema.plural.toLowerCase()}
        />
      )}

      {/* count + provenance footer */}
      {rows && rows.length > 0 && (
        <footer className="mt-5 flex flex-wrap items-center justify-between gap-2 font-mono text-2xs text-text-faint">
          <span>
            {rows.length} {rows.length === 1 ? "row" : "rows"}
          </span>
          <span>
            entity={schema.entity}
            {schema.nucleus ? ` . ${schema.nucleus}` : ""} .{" "}
            {config.fixtures ? "fixtures" : "live"} . RLS by tenant_id
          </span>
        </footer>
      )}

      {/* ---- create / edit form ------------------------------------------ */}
      {writable && editing !== undefined && client && (
        <EntityForm
          schema={schema}
          record={editing}
          client={client}
          onClose={() => setEditing(undefined)}
          onSaved={async () => {
            setEditing(undefined);
            await load();
          }}
        />
      )}

      {/* ---- delete confirm ---------------------------------------------- */}
      {writable && confirmDelete && (
        <ConfirmDelete
          schema={schema}
          record={confirmDelete}
          onCancel={() => setConfirmDelete(null)}
          onConfirm={() => remove(confirmDelete)}
        />
      )}
    </div>
  );
}

// --- DataTable ---------------------------------------------------------------

function DataTable({
  schema,
  rows,
  writable,
  publishable,
  publishingId,
  onEdit,
  onDelete,
  onTogglePublish,
}: {
  schema: EntitySchema;
  rows: EntityRecord[];
  writable: boolean;
  publishable: boolean;
  publishingId: string | null;
  onEdit: (r: EntityRecord) => void;
  onDelete: (r: EntityRecord) => void;
  onTogglePublish: (r: EntityRecord) => void;
}) {
  const cols = schema.columns;
  // The actions column is shown when writable (edit/delete) OR publishable (the toggle). A
  // publishable row also gets a leading STATUS column (published/draft) so the gate state is
  // legible at a glance, honest from the row's own ``published`` field.
  const showActions = writable || publishable;
  // grid template: optional status column + one column per field + an actions column.
  const template =
    (publishable ? "0.7fr " : "") +
    cols.map((c) => (c.primary ? "1.6fr" : "1fr")).join(" ") +
    (showActions ? " 0.6fr" : "");

  return (
    <div className="overflow-hidden rounded-card border border-line">
      {/* header */}
      <div
        className="hidden gap-4 border-b border-line bg-panel-sunken px-5 py-2.5 font-mono text-2xs uppercase tracking-wider text-text-faint sm:grid"
        style={{ gridTemplateColumns: template }}
      >
        {publishable && <span>Status</span>}
        {cols.map((c) => (
          <span key={c.key} className={c.align === "right" ? "text-right" : ""}>
            {c.label}
          </span>
        ))}
        {showActions && <span className="text-right">Actions</span>}
      </div>

      <ul>
        {rows.map((r, i) => (
          <li
            key={r.id}
            style={{
              animationDelay: `${i * 30}ms`,
              ["--row-cols" as string]: template,
            }}
            className="flex animate-rise-in flex-col gap-2 border-b border-line bg-panel px-5 py-3.5 last:border-b-0 sm:grid sm:items-center sm:gap-4 sm:[grid-template-columns:var(--row-cols)]"
          >
            {publishable && <PublishBadge published={isPublished(r)} />}
            {cols.map((c) => (
              <Cell key={c.key} column={c} value={r[c.key] ?? null} />
            ))}
            {showActions && (
              <div className="mt-2 flex items-center justify-end gap-1 sm:mt-0">
                {publishable && (
                  <PublishToggle
                    published={isPublished(r)}
                    busy={publishingId === r.id}
                    label={schema.singular}
                    onClick={() => onTogglePublish(r)}
                  />
                )}
                {writable && (
                  <>
                    <button
                      onClick={() => onEdit(r)}
                      className="grid h-8 w-8 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted transition-colors hover:border-synapse/40 hover:text-synapse"
                      aria-label={`Edit ${schema.singular}`}
                      title="Edit"
                    >
                      <PencilIcon />
                    </button>
                    <button
                      onClick={() => onDelete(r)}
                      className="grid h-8 w-8 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted transition-colors hover:border-danger/40 hover:text-danger"
                      aria-label={`Delete ${schema.singular}`}
                      title="Delete"
                    >
                      <TrashIcon />
                    </button>
                  </>
                )}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Cell({
  column,
  value,
}: {
  column: EntitySchema["columns"][number];
  value: FieldValue;
}) {
  const text = formatCell(value, column.type);

  if (column.type === "badge" && value !== null && value !== "") {
    return (
      <span className={column.align === "right" ? "text-right" : ""}>
        <span className="chip">{text}</span>
      </span>
    );
  }

  if (column.type === "boolean") {
    return (
      <span className={column.align === "right" ? "sm:text-right" : ""}>
        <span
          className={[
            "inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider",
            value ? "text-synapse" : "text-text-faint",
          ].join(" ")}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${value ? "bg-synapse" : "bg-line-strong"}`}
          />
          {text}
        </span>
      </span>
    );
  }

  return (
    <span
      className={[
        column.primary
          ? "font-display text-sm font-600 text-text"
          : column.type === "currency" || column.type === "number" || column.type === "date"
            ? "font-mono text-2xs text-text-muted"
            : "text-sm text-text-muted",
        column.align === "right" ? "sm:text-right" : "",
      ].join(" ")}
    >
      {/* mobile: show the column label inline for context */}
      <span className="mr-2 font-mono text-2xs uppercase tracking-wider text-text-faint sm:hidden">
        {column.label}
      </span>
      {text}
    </span>
  );
}

// --- PublishBadge + PublishToggle (SPEC 10 W1 -- the L2 publish gate) ---------

/**
 * The honest published/draft STATUS chip for a publishable row. Reads the row's own
 * ``published`` state (no fabrication): "public" (synapse) when published, "draft" (muted)
 * otherwise. This is the read-only mirror of the toggle's action -- the gate state is legible
 * even before you reach the actions column.
 */
function PublishBadge({ published }: { published: boolean }) {
  return (
    <span>
      <span
        className={[
          "inline-flex items-center gap-1.5 font-mono text-2xs uppercase tracking-wider",
          published ? "text-synapse" : "text-text-faint",
        ].join(" ")}
      >
        <span
          className={`h-1.5 w-1.5 rounded-full ${published ? "bg-synapse" : "bg-line-strong"}`}
        />
        {published ? "public" : "draft"}
      </span>
    </span>
  );
}

/**
 * The Publish/Unpublish toggle button for ONE row. Calls onClick (which PATCHes the publish gate
 * via the auth'd client -- NO tenant_id, Bearer only). While the flip is in flight it is disabled
 * + shows a busy glyph. The label + title make the action explicit ("Publish" vs "Unpublish") so
 * the supervisor knows exactly what flipping the L2 gate does.
 */
function PublishToggle({
  published,
  busy,
  label,
  onClick,
}: {
  published: boolean;
  busy: boolean;
  label: string;
  onClick: () => void;
}) {
  const action = published ? "Unpublish" : "Publish";
  return (
    <button
      onClick={onClick}
      disabled={busy}
      aria-label={`${action} ${label}`}
      aria-pressed={published}
      title={`${action} (L2 public site)`}
      className={[
        "grid h-8 w-8 place-items-center rounded-lg border bg-panel-sunken transition-colors disabled:opacity-40",
        published
          ? "border-synapse/40 text-synapse hover:border-synapse/60"
          : "border-line text-text-muted hover:border-synapse/40 hover:text-synapse",
      ].join(" ")}
    >
      {busy ? <Spinner /> : <LandingIcon />}
    </button>
  );
}

// --- EntityForm (create / edit modal) ----------------------------------------

function EntityForm({
  schema,
  record,
  client,
  onClose,
  onSaved,
}: {
  schema: EntitySchema;
  /** null = create, a record = edit. */
  record: EntityRecord | null;
  client: ApiClient;
  onClose: () => void;
  onSaved: () => void;
}) {
  const isEdit = record !== null;
  const [form, setForm] = useState<Record<string, FieldValue>>(() =>
    record ? formFromRecord(schema.fields, record) : emptyForm(schema.fields),
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Escape closes (unless saving).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !busy) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onClose]);

  function setField(key: string, value: FieldValue) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function validate(): string | null {
    for (const f of schema.fields) {
      if (!f.required) continue;
      const v = form[f.key];
      if (v === "" || v === null || v === undefined) {
        return `${f.label} is required.`;
      }
    }
    return null;
  }

  async function submit() {
    const v = validate();
    if (v) {
      setError(v);
      return;
    }
    setBusy(true);
    setError(null);

    // Coerce number fields to numbers; drop empty optionals.
    const payload: Record<string, unknown> = {};
    for (const f of schema.fields) {
      let value = form[f.key];
      if (value === "" && !f.required) continue;
      if (f.type === "number" && value !== "" && value !== null) {
        const n = Number(value);
        value = Number.isNaN(n) ? value : n;
      }
      payload[f.key] = value;
    }

    try {
      if (isEdit && record) {
        await client.updateEntity(schema.entity, record.id, payload);
      } else {
        await client.createEntity(schema.entity, payload);
      }
      onSaved();
    } catch (err) {
      setError(messageOf(err, "Save failed."));
      setBusy(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label={`${isEdit ? "Edit" : "New"} ${schema.singular}`}
      onClick={(e) => {
        if (e.target === e.currentTarget && !busy) onClose();
      }}
    >
      <div className="panel relative max-h-[90vh] w-full max-w-lg animate-rise-in overflow-auto">
        <button
          onClick={() => !busy && onClose()}
          disabled={busy}
          aria-label="Close"
          className="absolute right-4 top-4 grid h-8 w-8 place-items-center rounded-lg border border-line bg-panel-sunken text-text-muted transition-colors hover:border-line-strong hover:text-text disabled:opacity-40"
        >
          <span className="text-lg leading-none">&times;</span>
        </button>

        <div className="border-b border-line px-6 py-5">
          <h2 className="font-display text-2xl font-600 tracking-tight text-text">
            {isEdit ? `Edit ${schema.singular}` : `New ${schema.singular}`}
          </h2>
          <p className="mt-1 font-mono text-2xs text-text-faint">
            entity={schema.entity}
            {isEdit && record ? ` . id=${record.id}` : ""}
          </p>
        </div>

        <div className="space-y-4 px-6 py-5">
          {schema.fields.map((f) => (
            <FieldInput
              key={f.key}
              field={f}
              value={form[f.key]}
              disabled={busy}
              onChange={(v) => setField(f.key, v)}
            />
          ))}

          {error && (
            <div
              role="alert"
              className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-3.5 py-2.5 text-sm text-danger"
            >
              <span className="mt-0.5 shrink-0">
                <AlertIcon />
              </span>
              <span>{error}</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-line px-6 py-4">
          <button onClick={onClose} disabled={busy} className="btn-ghost">
            Cancel
          </button>
          <button onClick={submit} disabled={busy} className="btn-primary">
            {busy ? "Saving..." : isEdit ? "Save changes" : `Create ${schema.singular.toLowerCase()}`}
          </button>
        </div>
      </div>
    </div>
  );
}

function FieldInput({
  field,
  value,
  disabled,
  onChange,
}: {
  field: EntityField;
  value: FieldValue;
  disabled: boolean;
  onChange: (v: FieldValue) => void;
}) {
  const id = `field-${field.key}`;
  const label = (
    <label
      htmlFor={id}
      className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
    >
      {field.label}
      {field.required && <span className="ml-1 text-synapse">*</span>}
    </label>
  );

  let control: JSX.Element;
  if (field.type === "boolean") {
    control = (
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={Boolean(value)}
        disabled={disabled}
        onClick={() => onChange(!value)}
        className={[
          "relative inline-flex h-6 w-11 items-center rounded-pill border transition-colors disabled:opacity-50",
          value ? "border-synapse/50 bg-synapse/20" : "border-line bg-panel-sunken",
        ].join(" ")}
      >
        <span
          className={[
            "inline-block h-4 w-4 transform rounded-full transition-transform",
            value ? "translate-x-5 bg-synapse" : "translate-x-1 bg-text-faint",
          ].join(" ")}
        />
      </button>
    );
  } else if (field.type === "select") {
    control = (
      <select
        id={id}
        value={value === null ? "" : String(value)}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="field disabled:opacity-60"
      >
        <option value="">--</option>
        {(field.options ?? []).map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    );
  } else if (field.type === "textarea") {
    control = (
      <textarea
        id={id}
        rows={3}
        value={value === null ? "" : String(value)}
        disabled={disabled}
        placeholder={field.placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="field resize-none disabled:opacity-60"
      />
    );
  } else {
    control = (
      <input
        id={id}
        type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"}
        value={value === null ? "" : String(value)}
        disabled={disabled}
        placeholder={field.placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="field disabled:opacity-60"
      />
    );
  }

  return (
    <div>
      {label}
      {control}
      {field.help && (
        <p className="mt-1 font-mono text-2xs text-text-faint">{field.help}</p>
      )}
    </div>
  );
}

// --- ConfirmDelete -----------------------------------------------------------

function ConfirmDelete({
  schema,
  record,
  onCancel,
  onConfirm,
}: {
  schema: EntitySchema;
  record: EntityRecord;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const primaryCol = schema.columns.find((c) => c.primary);
  const name = primaryCol ? String(record[primaryCol.key] ?? record.id) : record.id;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label={`Delete ${schema.singular}`}
      onClick={(e) => {
        if (e.target === e.currentTarget) onCancel();
      }}
    >
      <div className="panel w-full max-w-sm animate-rise-in p-6">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-danger/30 bg-danger/5 text-danger">
            <TrashIcon />
          </span>
          <div>
            <h3 className="font-display text-lg font-600 text-text">
              Delete {schema.singular.toLowerCase()}?
            </h3>
            <p className="mt-1 text-sm text-text-muted">
              <span className="text-text">{name}</span> will be removed from your
              data plane. This cannot be undone.
            </p>
          </div>
        </div>
        <div className="mt-5 flex items-center justify-end gap-2">
          <button onClick={onCancel} className="btn-ghost">
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="inline-flex items-center justify-center gap-2 rounded-pill border border-danger/40 bg-danger/10 px-5 py-2.5 font-medium text-danger transition-colors hover:bg-danger/20"
          >
            <TrashIcon />
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

// --- shared error normalizer -------------------------------------------------

function messageOf(err: unknown, fallback: string): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return fallback;
}
