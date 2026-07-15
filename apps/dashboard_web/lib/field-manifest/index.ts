// =============================================================================
// field-manifest -- public surface of the schema-to-form mold (the de-dup keystone)
// =============================================================================
//
// ONE declarative ProductManifest -> buildSchema derives the zod schema + the
// publish-gate + the partial update schema; the renderer registry + ManifestForm
// derive the form. App-logic plugs in via the HandlerRegistry. See
// docs/specs/02_products_admin/ for the full contract.

export type {
  FieldKind,
  PublishRule,
  FieldDef,
  SectionDef,
  ProductManifest,
} from "./types";
export {
  buildSchema,
  getMissingPublishRequirements,
} from "./buildSchema";
export type { PublishRequirement, BuiltSchema } from "./buildSchema";
export {
  FIELD_KIND_RENDERERS,
  ManifestField,
  getManifestField,
} from "./renderers";
export type { FieldRendererProps, ManifestFieldProps } from "./renderers";
export { ManifestForm } from "./ManifestForm";
export type { ManifestFormProps } from "./ManifestForm";
export {
  inertHandlerRegistry,
  filterChannelLinkDiffs,
  AI_FORBIDDEN_CHANNEL_FIELDS,
} from "./handlers";
export type {
  HandlerRegistry,
  FieldHandlers,
  TenantCtx,
  AIFieldDiff,
} from "./handlers";
export { productManifest } from "./productManifest";
