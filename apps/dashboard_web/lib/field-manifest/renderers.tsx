"use client";

// =============================================================================
// renderers.tsx -- FieldKind -> renderer registry (the form half of the mold)
// =============================================================================
//
// Each FieldKind maps to a renderer that reuses a shared domain-neutral
// sub-component (TagInput / ArrayFieldEditor / FAQEditor / ImageUploader /
// MediaKitUploader / AttributesEditor from components/editor/) or a primitive
// (input / textarea / select / checkbox), wired to a react-hook-form control
// through the ManifestFormField scaffold. The registry is what lets ManifestForm
// pick a widget from `field.kind` alone. ZERO tenant literals.
//
// Ported from the reference implementation (lib/field-manifest/renderers.tsx).
// Adaptations for the central (shadcn-free, Next) host:
//   - the shadcn FormField scaffold -> ManifestFormField (RHF Controller + the
//     dashboard's CSS atoms);
//   - the shadcn ui/admin imports -> components/editor/* + plain HTML controls;
//   - import.meta.env.DEV (Vite) -> process.env.NODE_ENV (Next);
//   - FIX a latent bug in the reference: getManifestField / ManifestField use
//     `ProductManifest` but the source never imported it -- imported here.

import type { Control, ControllerRenderProps, FieldValues } from "react-hook-form";
import { ManifestFormField } from "@/components/editor/FormField";
import { TagInput } from "@/components/editor/TagInput";
import { ArrayFieldEditor } from "@/components/editor/ArrayFieldEditor";
import { FAQEditor } from "@/components/editor/FAQEditor";
import { ImageUploader } from "@/components/editor/ImageUploader";
import { MediaKitUploader } from "@/components/editor/MediaKitUploader";
import { AttributesEditor } from "@/components/editor/AttributesEditor";
import type { FAQItem, MediaKitImage } from "@/components/editor/types";
import type { FieldDef, FieldKind, ProductManifest } from "./types";

/** Props every kind-renderer receives. `control` is the RHF form control. */
export interface FieldRendererProps {
  field: FieldDef;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  control: Control<FieldValues>;
}

type Renderer = (props: FieldRendererProps) => JSX.Element;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type RHF = ControllerRenderProps<FieldValues, string>;

/**
 * Wrap a control in the standard ManifestFormField scaffold (label + control +
 * help + error), supplying the manifest field's label/required/helpText. The
 * `renderControl` callback receives the RHF render-prop field object.
 */
function withFormField(
  def: FieldDef,
  control: Control<FieldValues>,
  renderControl: (rhf: RHF) => JSX.Element,
): JSX.Element {
  return (
    <ManifestFormField
      control={control}
      name={def.name}
      label={def.label}
      required={def.required}
      helpText={def.helpText}
    >
      {(rhf) => renderControl(rhf)}
    </ManifestFormField>
  );
}

const renderText: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <input
      className="field w-full"
      placeholder={field.placeholder}
      maxLength={field.max}
      name={rhf.name}
      ref={rhf.ref}
      value={(rhf.value as string) ?? ""}
      onChange={rhf.onChange}
      onBlur={rhf.onBlur}
    />
  ));

const renderTextarea: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <textarea
      className="field min-h-[120px] w-full"
      placeholder={field.placeholder}
      maxLength={field.max}
      name={rhf.name}
      ref={rhf.ref}
      value={(rhf.value as string) ?? ""}
      onChange={rhf.onChange}
      onBlur={rhf.onBlur}
    />
  ));

const renderNumber: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <input
      type="number"
      className="field w-full"
      step={field.kind === "price" ? "0.01" : "1"}
      min={typeof field.min === "number" ? field.min : 0}
      placeholder={field.placeholder}
      name={rhf.name}
      ref={rhf.ref}
      onChange={rhf.onChange}
      onBlur={rhf.onBlur}
      // null/undefined -> "" so the input stays controlled and an empty value
      // persists as NULL (not 0) -- mirrors the live numeric-twin binding.
      value={(rhf.value as number | string | undefined) ?? ""}
    />
  ));

const renderSlug: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <input
      className="field w-full"
      placeholder={field.placeholder}
      maxLength={field.max ?? 100}
      name={rhf.name}
      ref={rhf.ref}
      value={(rhf.value as string) ?? ""}
      onChange={rhf.onChange}
      onBlur={rhf.onBlur}
    />
  ));

const renderTags: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <TagInput
      value={(rhf.value as string[]) ?? []}
      onChange={rhf.onChange}
      placeholder={field.placeholder}
      maxItems={field.max ?? 50}
    />
  ));

const renderOrderedArray: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <ArrayFieldEditor
      value={(rhf.value as string[]) ?? []}
      onChange={rhf.onChange}
      placeholder={field.placeholder}
      // Only numbered when the field opts in.
      numbered={field.numbered ?? false}
      maxItems={field.max ?? 20}
    />
  ));

const renderFaq: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <FAQEditor
      value={(rhf.value as FAQItem[]) ?? []}
      onChange={rhf.onChange}
      maxItems={field.max ?? 20}
    />
  ));

const renderImages: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <ImageUploader
      images={(rhf.value as string[]) ?? []}
      onImagesChange={rhf.onChange}
      // The manifest form is a structural proof: file-select is the HANDLER seam,
      // an inert no-op here. A live page wires onFilesSelected to the tenant
      // upload handler (HandlerRegistry.upload).
      onFilesSelected={() => undefined}
      maxFiles={field.max ?? 9}
    />
  ));

const renderMediaKit: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <MediaKitUploader
      images={(rhf.value as MediaKitImage[]) ?? []}
      onImagesChange={rhf.onChange}
      hasMediaKit={Array.isArray(rhf.value) && (rhf.value as MediaKitImage[]).length > 0}
      onHasMediaKitChange={() => undefined}
    />
  ));

const renderSelect: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <select
      className="field w-full"
      name={rhf.name}
      ref={rhf.ref}
      value={(rhf.value as string) || (field.default as string) || ""}
      onChange={rhf.onChange}
      onBlur={rhf.onBlur}
    >
      <option value="" disabled>
        {field.placeholder ?? "Selecione"}
      </option>
      {(field.options ?? []).map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  ));

const renderKeyValue: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <AttributesEditor
      value={rhf.value as Record<string, unknown> | undefined}
      onChange={rhf.onChange}
      maxItems={field.max ?? 50}
    />
  ));

const renderBoolean: Renderer = ({ field, control }) =>
  withFormField(field, control, (rhf) => (
    <input
      type="checkbox"
      name={rhf.name}
      ref={rhf.ref}
      checked={!!rhf.value}
      onChange={(e) => rhf.onChange(e.target.checked)}
      onBlur={rhf.onBlur}
    />
  ));

/**
 * The registry. ManifestForm looks a renderer up by FieldKind. Adding a kind to
 * the union in types.ts requires an entry here (and a branch in buildSchema).
 */
export const FIELD_KIND_RENDERERS: Record<FieldKind, Renderer> = {
  text: renderText,
  textarea: renderTextarea,
  number: renderNumber,
  slug: renderSlug,
  price: renderNumber,
  tags: renderTags,
  stringArray: renderTags,
  orderedArray: renderOrderedArray,
  faq: renderFaq,
  images: renderImages,
  mediaKit: renderMediaKit,
  select: renderSelect,
  keyValue: renderKeyValue,
  boolean: renderBoolean,
};

/**
 * Look up a single FieldDef by `name` in a manifest. Used by ManifestField so a
 * live editor can render ONE manifest-driven field in place (keeping its
 * surrounding bespoke layout) instead of swapping a whole section.
 */
export function getManifestField(
  manifest: ProductManifest,
  name: string,
): FieldDef | undefined {
  return manifest.fields.find((f) => f.name === name);
}

export interface ManifestFieldProps {
  /** The manifest to resolve the field from. */
  manifest: ProductManifest;
  /** The FieldDef.name to render (must exist in the manifest). */
  name: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  control: Control<FieldValues>;
}

/**
 * Render exactly ONE manifest field (by name) through the kind->renderer registry,
 * using the SAME scaffold as ManifestForm. This is the "migrate a single
 * declarative field in place" entry point a live editor uses to shrink its
 * monolith without disturbing the bespoke layout around each field. Renders
 * nothing (with a DEV warning) if the name is not in the manifest -- a guard
 * against a typo silently dropping a field.
 */
export function ManifestField({ manifest, name, control }: ManifestFieldProps): JSX.Element | null {
  const field = getManifestField(manifest, name);
  if (!field) {
    if (process.env.NODE_ENV !== "production") {
      // eslint-disable-next-line no-console
      console.warn(`[ManifestField] no field named "${name}" in manifest`);
    }
    return null;
  }
  const Renderer = FIELD_KIND_RENDERERS[field.kind];
  return <Renderer field={field} control={control} />;
}
