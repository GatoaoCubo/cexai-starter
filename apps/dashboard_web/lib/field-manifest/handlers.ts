// =============================================================================
// handlers.ts -- the app-logic boundary (the ONE piece NOT declarative)
// =============================================================================
//
// The manifest carries WHAT a field is (kind, gate, label). It NEVER carries HOW
// a field behaves. Real per-tenant behavior -- storage upload + orphan cleanup,
// price auto-calc from cost x margin, "fill with AI" human-in-the-loop -- is
// injected through THIS registry, keyed by (field_kind, tenant). The generic core
// (types/buildSchema/renderers/ManifestForm) stays tenant-agnostic; behavior plugs
// in here.
//
// Spec: docs/specs/02_products_admin/{spec,plan}.md (FR-011, plan 1.5, Article III).
// With NO registry bound: declarative fields still render + validate, and the
// behavioral controls degrade to INERT no-ops (file-select is a no-op, computed
// fields show stored values, no crash; a DEV-only warning on a missing needed
// handler). This file holds ZERO tenant literals.

import type { FieldKind } from "./types";

/**
 * Per-tenant context threaded into every handler. The generic core treats it as
 * opaque -- a tenant binds whatever its handlers need (tenant id, a data-layer
 * client, a storage bucket handle, an AI client). `tenant` is the only field the
 * core itself reads (for the registry key); everything else is tenant-defined.
 */
export interface TenantCtx {
  /** The tenant identifier (the registry key). */
  tenant: string;
  /** Opaque tenant-supplied bag (data-layer client, bucket handle, AI client...). */
  [key: string]: unknown;
}

/** A single staged field change proposed by the AI-assist (HITL) handler. */
export interface AIFieldDiff {
  /** The FieldDef.name the proposal targets. */
  field: string;
  /** The current value (for the review diff). */
  current: unknown;
  /** The proposed value (applied only on explicit per-field accept). */
  proposed: unknown;
  /** Optional rationale shown in the review UI. */
  rationale?: string;
}

/**
 * The behavior set for a (field_kind, tenant) pair. Every member is OPTIONAL --
 * an unset member means "no behavior" (the control degrades to inert). The core
 * calls these; it never implements them.
 */
export interface FieldHandlers {
  /**
   * Storage upload for images / mediaKit. Receives the selected files + the
   * tenant ctx, returns the stored URLs. The reference impl binds this to a Supabase bucket;
   * the core never hard-codes a connection.
   */
  upload?: (files: File[], ctx: TenantCtx) => Promise<string[]>;
  /**
   * Orphan-image cleanup when URLs are removed from an images / mediaKit field.
   * Best-effort; failures must not corrupt the field value.
   */
  cleanupOrphans?: (removedUrls: string[], ctx: TenantCtx) => Promise<void>;
  /**
   * Auto-calc on a watched field change (e.g. recompute preco_b2c / preco_b2b
   * from custo x margem). The manifest carries the FIELD; this carries the
   * COMPUTATION. Returns a partial patch merged into the form values.
   */
  autoCalc?: (
    changed: { name: string; value: unknown },
    all: Record<string, unknown>,
    ctx: TenantCtx,
  ) => Partial<Record<string, unknown>>;
  /**
   * AI-assisted authoring (HITL): "fill with AI" stages a per-field diff for
   * review/apply (NOT a blind overwrite). It MUST honor the grounding contract --
   * it must NOT inject channel links (purchase_link / whatsapp_link /
   * mercadolivre_link). Triggers tenant_voice_profile / output_validator molds.
   */
  aiAssist?: (current: Record<string, unknown>, ctx: TenantCtx) => Promise<AIFieldDiff[]>;
}

/**
 * The registry: resolve the behavior set for a (field_kind, tenant) pair, or
 * `undefined` when no behavior is bound. Injected per tenant at the dashboard
 * page (via context / props / capability-hooks).
 */
export type HandlerRegistry = (kind: FieldKind, tenant: string) => FieldHandlers | undefined;

/**
 * The INERT default registry. Returns `undefined` for every (kind, tenant) pair,
 * so the generated editor renders + validates with all behavioral controls inert.
 * This is what makes the generic core safe to mount with NO tenant behavior bound.
 */
export const inertHandlerRegistry: HandlerRegistry = () => undefined;

/**
 * Channel-link field names the AI-HITL handler MUST NOT inject (the grounding
 * contract). Exposed so a tenant's aiAssist implementation -- or a guard wrapping
 * it -- can filter these out of a staged diff. The core surfaces it; tenants honor it.
 */
export const AI_FORBIDDEN_CHANNEL_FIELDS: readonly string[] = [
  "purchase_link",
  "whatsapp_link",
  "mercadolivre_link",
];

/**
 * Helper a tenant (or the page wiring) can use to strip forbidden channel-link
 * proposals out of an AI diff before staging it for review. Pure + total; never
 * throws. Keeps the grounding contract enforceable at the seam without baking
 * tenant policy into the manifest.
 */
export function filterChannelLinkDiffs(diffs: AIFieldDiff[]): AIFieldDiff[] {
  return (diffs ?? []).filter((d) => !AI_FORBIDDEN_CHANNEL_FIELDS.includes(d.field));
}
