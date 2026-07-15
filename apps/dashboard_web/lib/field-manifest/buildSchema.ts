// =============================================================================
// buildSchema -- derive { baseSchema, schema, updateSchema, publishRequirements }
// from a declarative ProductManifest.
// =============================================================================
//
// This is the schema half of the schema-to-form mold (the de-dup keystone). It
// REUSES the exact zod atoms in the leaf module product.atoms.ts so the generated
// schema + gate behave identically to a hand-written equivalent. ONE manifest is
// the single source -- the zod base schema, the publish-gate, the partial update
// schema, and the form (via the renderer registry) are ALL derived from it, so
// they cannot drift. Zero tenant literals live here.
//
// Base-vs-refined split (CRITICAL -- the superRefine landmine):
//   baseSchema  = z.object(...)                  <- ZodObject, has .partial()/.extend()
//   schema      = baseSchema.superRefine(gate)   <- ZodEffects, the publish gate
//   updateSchema= baseSchema.partial().extend()  <- partial of the BASE, gate-free
// We NEVER superRefine before .partial() (that would strip .partial off ZodEffects).
//
// Ported from the reference implementation (lib/field-manifest/buildSchema.ts).
// The ONLY adaptation: the atom import path resolves to the central
// leaf module (@/lib/product.atoms) rather than the reference @/lib/validations/product.atoms.

import { z } from "zod";
// The EXACT atoms the schema is built from. They live in the LEAF module
// product.atoms.ts (importing nothing back from this file or any tenant schema)
// so a future tenant schema can derive FROM buildSchema with no circular import.
import {
  emptyToUndefined as fmEmptyToUndefined,
  slugSchema as fmSlugSchema,
  priceSchema as fmPriceSchema,
  textArraySchema as fmTextArraySchema,
  faqSchema as fmFaqSchema,
  mediaKitImageSchema as fmMediaKitImageSchema,
  countItems as fmCountItems,
  countFaq as fmCountFaq,
  textLen as fmTextLen,
  isPositiveNumber as fmIsPositiveNumber,
} from "@/lib/product.atoms";
import type { FieldDef, FieldKind, ProductManifest, PublishRule } from "./types";

// ---------------------------------------------------------------------------
// Publish requirement shape -- {field, label, isSatisfied, errorMessage}. The
// SAME row drives BOTH the zod superRefine AND the live UI checklist (via
// getMissingPublishRequirements), so schema and UI cannot drift.
// ---------------------------------------------------------------------------
export interface PublishRequirement {
  /** Field path the error maps to (drives scroll-to + FormMessage highlight). */
  field: string;
  /** Short label for the checklist banner. */
  label: string;
  /** True when this requirement is met for the given data. */
  isSatisfied: (data: Record<string, unknown>) => boolean;
  /** Error/checklist message, may include the current count. */
  errorMessage: (data: Record<string, unknown>) => string;
}

export interface BuiltSchema {
  /** ZodObject base -- supports .partial()/.extend(). */
  baseSchema: z.ZodObject<z.ZodRawShape>;
  /** baseSchema + publish gate (ZodEffects). The one the live form uses. */
  schema: z.ZodTypeAny;
  /** baseSchema.partial().extend({status}) -- gate-free partial update schema. */
  updateSchema: z.ZodTypeAny;
  /** Derived publish-gate rows -- one per field that declares `publish`. */
  publishRequirements: PublishRequirement[];
}

// ---------------------------------------------------------------------------
// Kind -> base zod type. Each branch returns the SAME atom a hand-written schema
// uses for that semantic. Defaults + optionality are applied by `applyModifiers`
// below, so this mapping stays focused on the "core" type per kind.
// ---------------------------------------------------------------------------
function coreTypeFor(field: FieldDef): z.ZodTypeAny {
  const kind: FieldKind = field.kind;
  switch (kind) {
    case "text": {
      // Required text uses .min(required-bound); optional text allows ""
      // (handled in applyModifiers).
      let s = z.string().trim();
      if (field.required && typeof field.min === "number") {
        s = s.min(field.min, `Mínimo ${field.min} caracteres`);
      }
      if (typeof field.max === "number") {
        s = s.max(field.max, `Máximo ${field.max} caracteres`);
      }
      return s;
    }
    case "textarea": {
      let s = z.string().trim();
      if (field.required && typeof field.min === "number") {
        s = s.min(field.min, `Mínimo ${field.min} caracteres`);
      }
      if (typeof field.max === "number") {
        s = s.max(field.max, `Máximo ${field.max} caracteres`);
      }
      return s;
    }
    case "slug":
      return fmSlugSchema;
    case "price":
      return fmPriceSchema;
    case "number": {
      // Optional numeric twins use emptyToUndefined so an empty input persists as
      // NULL not 0 (applied in applyModifiers). Required numbers drop that wrap.
      let n = z.coerce.number();
      if (typeof field.min === "number") n = n.min(field.min);
      if (typeof field.max === "number") n = n.max(field.max);
      return n;
    }
    case "tags":
    case "stringArray":
    case "orderedArray": {
      // All three reuse the text-array list atom. A per-field max overrides the
      // default 50-cap via .max(...) on the array.
      if (typeof field.max === "number") {
        return fmTextArraySchema.max(field.max, `Máximo de ${field.max} itens permitidos`);
      }
      return fmTextArraySchema;
    }
    case "faq":
      return fmFaqSchema;
    case "images": {
      // array(string.trim.min(1)).min(1 if required).max(field.max ?? 9).
      let arr = z.array(
        z.string().trim().min(1, "URL de imagem/vídeo não pode estar vazia"),
      );
      if (field.required) arr = arr.min(1, "Adicione pelo menos 1 imagem ou vídeo");
      arr = arr.max(field.max ?? 9, `Máximo de ${field.max ?? 9} imagens/vídeos permitidos`);
      return arr;
    }
    case "mediaKit":
      return z.array(fmMediaKitImageSchema).max(field.max ?? 9);
    case "select": {
      const values = (field.options ?? []).map((o) => o.value);
      // z.enum([]) throws -- fall back to z.string() for an empty option set.
      if (values.length === 0) return z.string();
      return z.enum(values as [string, ...string[]]);
    }
    case "keyValue":
      return z.record(z.string(), z.unknown());
    case "boolean":
      return z.boolean();
    default: {
      // Exhaustiveness guard: a new FieldKind MUST extend this switch (no silent drop).
      const _never: never = kind;
      throw new Error(`buildSchema: unmapped FieldKind ${String(_never)}`);
    }
  }
}

// ---------------------------------------------------------------------------
// Apply optionality + default + the "" escape hatch on optional string fields
// (.optional().or(z.literal(""))). This makes generated optional fields accept
// the SAME empty-string sentinel a controlled form sends.
// ---------------------------------------------------------------------------
function applyModifiers(core: z.ZodTypeAny, field: FieldDef): z.ZodTypeAny {
  const kind = field.kind;

  // Numbers: optional twins use emptyToUndefined (the wrap already yields optional).
  if (kind === "number") {
    if (field.required) return core;
    return fmEmptyToUndefined(core.optional());
  }

  // Arrays (tags/stringArray/orderedArray/mediaKit/faq): .optional().default([]).
  if (
    kind === "tags" ||
    kind === "stringArray" ||
    kind === "orderedArray" ||
    kind === "mediaKit" ||
    kind === "faq"
  ) {
    if (field.required) return core;
    return core.optional().default((field.default as unknown[]) ?? []);
  }

  // images: required -> as-is; optional -> .optional().default([]).
  if (kind === "images") {
    return field.required ? core : core.optional().default([]);
  }

  // select with a default (e.g. condition -> "new").
  if (kind === "select") {
    if (field.default !== undefined) return core.optional().default(field.default as string);
    if (!field.required) return core.optional();
    return core;
  }

  // boolean -> .default(false) like has_media_kit.
  if (kind === "boolean") {
    return core.default((field.default as boolean) ?? false);
  }

  // keyValue (attributes) -> optional, no default.
  if (kind === "keyValue") {
    return field.required ? core : core.optional();
  }

  // slug/price required -> as-is; optional -> .optional().or("").
  if (kind === "slug" || kind === "price") {
    if (field.required) return core;
    return core.optional().or(z.literal(""));
  }

  // text / textarea: required -> core; optional -> .optional().or(z.literal("")).
  if (kind === "text" || kind === "textarea") {
    if (field.required) return core;
    if (field.default !== undefined) {
      return core.optional().or(z.literal("")).default(field.default as string);
    }
    return core.optional().or(z.literal(""));
  }

  return core;
}

// ---------------------------------------------------------------------------
// Publish-rule -> (isSatisfied, errorMessage). Reuses the SAME counting helpers
// the atoms expose so a generated rule and a hand-written one count identically.
// ---------------------------------------------------------------------------
function makeSatisfier(
  field: FieldDef,
  rule: PublishRule,
): Pick<PublishRequirement, "isSatisfied" | "errorMessage"> {
  const name = field.name;
  const threshold = rule.threshold ?? 0;

  switch (rule.rule) {
    case "minCount": {
      // FAQ counts pairs (q AND a); other lists count non-empty trimmed entries.
      const count = (d: Record<string, unknown>): number =>
        field.kind === "faq"
          ? fmCountFaq(d[name] as Array<{ question?: string | null; answer?: string | null }>)
          : fmCountItems(d[name] as Array<string | null | undefined>);
      return {
        isSatisfied: (d) => count(d) >= threshold,
        errorMessage: (d) =>
          `Para publicar, adicione ao menos ${threshold} ${rule.label} (tem ${count(d)}).`,
      };
    }
    case "minLength": {
      return {
        isSatisfied: (d) => fmTextLen(d[name] as string | null | undefined) >= threshold,
        errorMessage: (d) =>
          `Para publicar, escreva ${rule.label} com ao menos ${threshold} caracteres (tem ${fmTextLen(
            d[name] as string | null | undefined,
          )}).`,
      };
    }
    case "positive": {
      // The numeric gate may span companion fields (dims: L+W+H all positive),
      // mapping a single error to this field.
      const fields = [name, ...(rule.companions ?? [])];
      return {
        isSatisfied: (d) => fields.every((f) => fmIsPositiveNumber(d[f] as number | null | undefined)),
        errorMessage: () => `Para publicar, informe ${rule.label}.`,
      };
    }
    case "present":
    default: {
      const present = (d: Record<string, unknown>): boolean => {
        const v = d[name];
        if (Array.isArray(v)) return fmCountItems(v as Array<string | null | undefined>) > 0;
        if (typeof v === "number") return Number.isFinite(v);
        return fmTextLen(v as string | null | undefined) > 0;
      };
      return {
        isSatisfied: (d) => present(d),
        errorMessage: () => `Para publicar, preencha ${rule.label}.`,
      };
    }
  }
}

/** Build the publish requirement rows from the fields that declare `publish`. */
function buildPublishRequirements(manifest: ProductManifest): PublishRequirement[] {
  const reqs: PublishRequirement[] = [];
  for (const field of manifest.fields) {
    if (!field.publish) continue;
    const { isSatisfied, errorMessage } = makeSatisfier(field, field.publish);
    reqs.push({ field: field.name, label: field.publish.label, isSatisfied, errorMessage });
  }
  return reqs;
}

/**
 * Generate { baseSchema, schema, updateSchema, publishRequirements } from a
 * manifest. The status + _wasPublished helper fields are injected automatically
 * (every product editor needs them for the publish gate).
 */
export function buildSchema(manifest: ProductManifest): BuiltSchema {
  const shape: z.ZodRawShape = {};
  for (const field of manifest.fields) {
    shape[field.name] = applyModifiers(coreTypeFor(field), field);
  }

  // Status + the non-persisted _wasPublished UI helper -- the gate only gates the
  // new-publish transition. The manifest field WINS for status (if it declared one).
  if (!shape.status) {
    shape.status = z.enum(["draft", "published", "archived"], {
      errorMap: () => ({ message: "Status deve ser: draft, published ou archived" }),
    });
  }
  shape._wasPublished = z.boolean().optional().default(false);

  const baseSchema = z.object(shape);
  const publishRequirements = buildPublishRequirements(manifest);

  // Publish gate: early-return unless a NEW publish (status === "published" AND
  // not already published). Then add one issue per unsatisfied requirement.
  const schema = baseSchema.superRefine((data, ctx) => {
    const d = data as Record<string, unknown>;
    if (d.status !== "published") return;
    if (d._wasPublished === true) return;
    for (const req of publishRequirements) {
      if (!req.isSatisfied(d)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: [req.field],
          message: req.errorMessage(d),
        });
      }
    }
  });

  const updateSchema = baseSchema.partial().extend({
    status: z.enum(["draft", "published", "archived"]).optional(),
  });

  return { baseSchema, schema, updateSchema, publishRequirements };
}

/** Convenience: just the missing requirements for the live-form checklist (same rule set). */
export function getMissingPublishRequirements(
  publishRequirements: PublishRequirement[],
  data: Record<string, unknown>,
): PublishRequirement[] {
  return publishRequirements.filter((req) => !req.isSatisfied(data));
}
