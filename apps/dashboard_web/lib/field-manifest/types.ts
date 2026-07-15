// =============================================================================
// Field Manifest -- tenant-AGNOSTIC type vocabulary for the schema-to-form mold
// =============================================================================
//
// ONE declarative manifest describes a product editor. From it we DERIVE the zod
// schema, the publish-gate (publishRequirements), and the rendered form -- so the
// three never drift. Central mints a product editor per tenant by supplying a
// different manifest; this file holds ZERO tenant literals.
//
// Ported from the reference implementation (lib/field-manifest/types.ts).
// See docs/specs/02_products_admin/{spec,plan}.md (FR-001/FR-002) for the rationale.

/**
 * The widget/validation archetype of a field. Each kind maps to (a) a zod type in
 * buildSchema.ts and (b) a renderer in renderers.tsx. Adding a product field that
 * does not fit an existing kind means extending THIS union (and both maps) -- an
 * exhaustiveness guard throws on an unmapped kind so a new kind cannot be dropped.
 */
export type FieldKind =
  | "text" // single-line string -> Input + z.string
  | "textarea" // multi-line string -> Textarea + z.string
  | "number" // numeric (free range) -> number Input + z.coerce.number
  | "slug" // url-safe identifier -> Input + slugSchema
  | "price" // money, 2dp, positive -> number Input + priceSchema
  | "tags" // string[] chips -> TagInput + textArraySchema
  | "stringArray" // string[] generic -> TagInput + textArraySchema
  | "orderedArray" // ordered string[] -> ArrayFieldEditor + textArraySchema
  | "faq" // {question,answer}[] -> FAQEditor + faqSchema
  | "images" // media URL[] -> ImageUploader + image array schema
  | "mediaKit" // MediaKitImage[] -> MediaKitUploader + mediaKitImage array
  | "select" // enum choice -> Select + z.enum
  | "keyValue" // jsonb bag -> AttributesEditor + z.record
  | "boolean"; // toggle -> Switch + z.boolean

/**
 * A single publish-gate rule attached to a field. The generated PublishRequirement
 * maps its error to THIS field's `name` (so the FormMessage highlight lands on it).
 *
 * - minCount   : count of non-empty list items (or FAQ pairs) >= threshold
 * - minLength  : trimmed string length >= threshold
 * - present    : value is non-empty / defined
 * - positive   : numeric value present and > 0 (AND all `companions`, if any)
 */
export interface PublishRule {
  rule: "minCount" | "minLength" | "present" | "positive";
  /** Numeric bar for minCount / minLength. Ignored by present / positive. */
  threshold?: number;
  /** Short label shown in the "Para publicar, faltam" banner (any locale). */
  label: string;
  /**
   * Extra field names that must ALSO satisfy the same rule for this requirement
   * to pass (e.g. the dims gate: dim_length_cm requires dim_width_cm + dim_height_cm
   * all positive, but maps a single error to dim_length_cm). The honest expression
   * of a multi-field gate as one requirement.
   */
  companions?: string[];
}

/**
 * One field of the product editor. Tenant data (productManifest.ts) is a list of
 * these. Everything the schema generator + form renderer need is here.
 */
export interface FieldDef {
  /** Field key -- matches the zod object key + the DB column + the form `name`. */
  name: string;
  /** Human label shown above the control. */
  label: string;
  /** Widget/validation archetype. */
  kind: FieldKind;
  /** Which SectionDef.id this field renders under. */
  section: string;
  /** Optional placeholder for the control. */
  placeholder?: string;
  /** Hard-required (base schema) -- contributes a min/refine that always applies. */
  required?: boolean;
  /** Min bound: min length for text/textarea, min value for number/price. */
  min?: number;
  /** Max bound: max length for text/textarea, max value for number/price, max items for arrays. */
  max?: number;
  /** Options for `select` kind. */
  options?: { value: string; label: string }[];
  /**
   * For `orderedArray` only: render the ArrayFieldEditor with a 1. 2. 3. number
   * gutter. Render-only flag -- ignored by buildSchema. Defaults to false.
   */
  numbered?: boolean;
  /** Default value baked into the schema (z `.default(...)`). */
  default?: unknown;
  /** Helper/description text under the control. */
  helpText?: string;
  /** Publish-gate rule (only on fields that gate the published transition). */
  publish?: PublishRule;
  /**
   * Marks a field as tenant-SPECIFIC. Documentation-only flag the central
   * distiller reads to know which fields are tenant fill vs GENERIC base. Does
   * NOT change schema/render behavior.
   */
  tenantParam?: boolean;
}

/** A form section grouping (one heading + block in the rendered form). */
export interface SectionDef {
  /** Stable id referenced by FieldDef.section. */
  id: string;
  /** Section heading. */
  title: string;
}

/** The whole declarative editor: sections (ordered) + fields (ordered). */
export interface ProductManifest {
  sections: SectionDef[];
  fields: FieldDef[];
}
