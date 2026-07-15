"use client";

// =============================================================================
// ManifestEntityForm -- MOUNT the field_manifest mold LIVE (SPEC 10 W5, L3).
// =============================================================================
//
// The field_manifest core (lib/field-manifest) shipped UNMOUNTED: ManifestForm is a
// pure layout component (it lays fields out by section through the kind->renderer
// registry) and buildSchema derives the zod schema + publish gate from the SAME
// declarative manifest. The CALLER owns the <form> + the react-hook-form control +
// the submit -- exactly like the reference editor. THIS component is that caller:
// it wires one ProductManifest to a live form and, on submit, calls the generic
// entity client (ApiClient.createEntity -> POST /entity/{slug}). It RE-USES the
// manifest engine + api.ts verbatim -- it re-implements neither.
//
//   * VALIDATION reuses buildSchema(manifest).schema (the publish-gate ZodEffects).
//     There is no @hookform/resolvers in this app, so we resolve zod by hand in the
//     submit: safeParse the form values, and on failure map each ZodIssue to an RHF
//     field error (setError) so the SAME ManifestFormField scaffold renders the
//     honest inline "FormMessage" the live editor uses. No fabricated value ever
//     enters the payload -- the form submits exactly what the operator typed (after
//     zod's own trims/coercions), and a required field that is empty BLOCKS submit
//     with its inline error.
//   * SUBMIT reuses ApiClient.createEntity(slug, values) -- the existing POST /entity
//     wire (Bearer-only; tenant_id is server-derived, never sent). Mode-transparent:
//     fixtures vs live is entirely inside ApiClient, so this mounts + tests offline.
//
// ZERO tenant literals live here. The product specifics travel on the injected
// manifest (lib/field-manifest/productManifest), so central mints a per-tenant
// editor by swapping the manifest -- this component is unchanged.

import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import type { FieldValues } from "react-hook-form";
import { z } from "zod";
import { ApiClient, ApiClientError } from "@/lib/api";
import {
  buildSchema,
  ManifestForm,
  type ProductManifest,
} from "@/lib/field-manifest";
import { AlertIcon, CheckIcon } from "./icons";
import { Spinner } from "./ui";

export interface ManifestEntityFormProps {
  /** The api slug the create targets (POST /entity/{slug}). */
  entity: string;
  /** Singular noun for the submit button / heading (e.g. "Product"). */
  singular?: string;
  /** The declarative editor (sections + fields). The proof input is productManifest. */
  manifest: ProductManifest;
  /** A live ApiClient bound to the session token (the create wire). */
  client: ApiClient;
  /** Called with the created record after a successful POST /entity. */
  onCreated?: (record: { id: string } & Record<string, unknown>) => void;
}

// ---------------------------------------------------------------------------
// Seed the RHF default values from the manifest so every control is CONTROLLED
// from first render (an empty string / empty list / the field default). This
// mirrors the editor's "start from a typed empty draft" contract -- no value is
// invented (an unfilled optional stays empty and is dropped/zod-defaulted), and a
// required field starts empty so its inline error surfaces only after a submit
// attempt, never as a fabricated placeholder value.
// ---------------------------------------------------------------------------
function manifestDefaults(manifest: ProductManifest): FieldValues {
  const out: FieldValues = {};
  for (const f of manifest.fields) {
    switch (f.kind) {
      case "tags":
      case "stringArray":
      case "orderedArray":
      case "faq":
      case "images":
      case "mediaKit":
        out[f.name] = (f.default as unknown[]) ?? [];
        break;
      case "boolean":
        out[f.name] = (f.default as boolean) ?? false;
        break;
      case "select":
        out[f.name] = (f.default as string) ?? "";
        break;
      case "keyValue":
        out[f.name] = (f.default as Record<string, unknown>) ?? {};
        break;
      default:
        // text / textarea / slug / price / number -> a controlled empty string
        // ("" persists an optional numeric as NULL, not 0 -- see renderers).
        out[f.name] = (f.default as string) ?? "";
    }
  }
  // The schema injects status + _wasPublished; seed status to the manifest's own
  // default (or "draft") so the publish gate early-returns for a draft create.
  const statusField = manifest.fields.find((f) => f.name === "status");
  out.status = (statusField?.default as string) ?? "draft";
  out._wasPublished = false;
  return out;
}

export function ManifestEntityForm({
  entity,
  singular = "record",
  manifest,
  client,
  onCreated,
}: ManifestEntityFormProps) {
  // Derive the zod schema + publish gate ONCE from the manifest (the de-dup keystone).
  const built = useMemo(() => buildSchema(manifest), [manifest]);
  const defaults = useMemo(() => manifestDefaults(manifest), [manifest]);

  const {
    control,
    handleSubmit,
    setError,
    reset,
    formState: { isSubmitting, errors },
  } = useForm<FieldValues>({ defaultValues: defaults });

  const [serverError, setServerError] = useState<string | null>(null);
  const [createdId, setCreatedId] = useState<string | null>(null);

  // The top-of-form summary: how many fields currently carry an inline error after
  // a blocked submit. Honest -- derived from RHF's own error map, not a guess.
  const errorCount = Object.keys(errors).length;

  async function onValid(values: FieldValues) {
    setServerError(null);
    setCreatedId(null);

    // Resolve zod by hand (no @hookform/resolvers in this app). The publish gate
    // early-returns for a draft, so a draft create validates the BASE shape; a
    // values.status === "published" create additionally enforces the publish gate.
    const parsed = built.schema.safeParse(values);
    if (!parsed.success) {
      applyZodErrors(parsed.error, setError);
      return;
    }

    try {
      const record = await client.createEntity(
        entity,
        parsed.data as Record<string, unknown>,
      );
      setCreatedId(record.id);
      onCreated?.(record as { id: string } & Record<string, unknown>);
      // Reset back to a clean typed draft so the operator can add another.
      reset(defaults);
    } catch (err) {
      setServerError(messageOf(err, "Create failed."));
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onValid)}
      noValidate
      aria-label={`New ${singular} via manifest`}
      className="mx-auto max-w-3xl"
    >
      <header className="border-b border-line pb-5">
        <p className="eyebrow mb-2">New via manifest</p>
        <h1 className="font-display text-2xl font-600 tracking-tight text-text">
          New {singular.toLowerCase()}
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-text-muted">
          A schema-driven editor generated from one declarative field manifest --
          the same mold that derives the validation + publish gate. Fields,
          sections, and rules all come from the manifest; nothing is hardcoded here.
        </p>
        <p className="mt-2 font-mono text-2xs text-text-faint">
          entity={entity} . {manifest.fields.length} fields . manifest-driven
        </p>
      </header>

      <div className="mt-7 panel p-5">
        <ManifestForm manifest={manifest} control={control} />
      </div>

      {/* honest validation summary -- only after a blocked submit */}
      {errorCount > 0 && (
        <div
          role="alert"
          className="mt-5 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>
            {errorCount} {errorCount === 1 ? "field needs" : "fields need"}{" "}
            attention. See the highlighted {errorCount === 1 ? "field" : "fields"}{" "}
            above.
          </span>
        </div>
      )}

      {serverError && (
        <div
          role="alert"
          className="mt-5 flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{serverError}</span>
        </div>
      )}

      {createdId && (
        <div
          role="status"
          className="mt-5 flex items-start gap-2 rounded-lg border border-synapse/30 bg-synapse/5 px-4 py-3 text-sm text-synapse"
        >
          <span className="mt-0.5 shrink-0">
            <CheckIcon />
          </span>
          <span>
            Created. The new {singular.toLowerCase()} landed in your data plane
            <span className="ml-1 font-mono text-2xs text-text-faint">
              id={createdId}
            </span>
            .
          </span>
        </div>
      )}

      <div className="sticky bottom-0 z-10 mt-6 flex items-center justify-end gap-2 border-t border-line bg-ink-800/90 py-4 backdrop-blur">
        <button type="submit" disabled={isSubmitting} className="btn-primary disabled:opacity-40">
          {isSubmitting ? (
            <>
              <Spinner className="h-3.5 w-3.5" />
              Creating...
            </>
          ) : (
            `Create ${singular.toLowerCase()}`
          )}
        </button>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------------------
// Map a ZodError onto react-hook-form field errors so the existing
// ManifestFormField scaffold renders each message inline (the "FormMessage"
// analogue). The first issue per path wins (RHF keeps one message per field).
// ---------------------------------------------------------------------------
function applyZodErrors(
  error: z.ZodError,
  setError: ReturnType<typeof useForm<FieldValues>>["setError"],
): void {
  const seen = new Set<string>();
  for (const issue of error.issues) {
    const name = issue.path.length ? String(issue.path[0]) : "";
    if (!name || seen.has(name)) continue;
    seen.add(name);
    setError(name, { type: "zod", message: issue.message });
  }
}

function messageOf(err: unknown, fallback: string): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return fallback;
}
