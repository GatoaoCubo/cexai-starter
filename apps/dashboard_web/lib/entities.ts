// ----------------------------------------------------------------------------
// Tenant entity registry -- the loader that DRIVES the management/CRUD half.
//
// The mold's "management" primitive (<DataManager/>) is entity-agnostic: it
// renders a table + edit form purely from an EntitySchema. THIS module is the
// seam that supplies WHICH entities a tenant manages and their schema -- and it
// is now OVERLAY-DRIVEN, not a static map. Nothing here is hardcoded to a brand.
//
//   * Source of truth: the TENANT OVERLAY (capability_map.yaml ->
//     ``managed_entities``). The backend GET /entities-config reads it for the
//     verified tenant and returns EntitySchema[]; FIXTURES mode mirrors it with
//     the brand-neutral demo schema. Either way the schemas arrive THROUGH the
//     ApiClient (fixtures vs live is entirely inside the client) -- this is the
//     EXACT path ApiClient.listCards() uses for capability cards.
//   * A tenant adds its own entities (products, contacts, leads, ...) by
//     declaring them in its overlay -- it does NOT touch DataManager or this
//     file. A tenant with no declared entities yields an empty list and the
//     management half hides itself.
//
// Because the data is loaded (async, tenant-scoped via the JWT), these helpers
// take an ApiClient and return Promises. The consumers (the management index,
// the [entity] route, and the nav gate) await them.
// ----------------------------------------------------------------------------

import type { ApiClient } from "./api";
import type { EntitySchema } from "./types";

/**
 * All entity schemas this tenant manages, loaded from the tenant overlay via
 * the ApiClient (GET /entities-config in live mode, fixtures in fixtures mode).
 * The management nav + routes are built from this list -- a tenant with no
 * declared entities yields ``[]`` and the management half hides itself.
 *
 * Errors propagate to the caller (the consuming component renders its own error
 * state), matching how the other ApiClient reads (cards / summary) behave.
 */
export async function getEntitySchemas(
  client: ApiClient,
): Promise<EntitySchema[]> {
  return client.listEntitySchemas();
}

/**
 * One schema by slug, or null. Used by the dynamic /dashboard/data/[entity]
 * route. Resolves against the SAME overlay-driven list (no separate fetch path),
 * so a slug that is not a managed entity for this tenant returns null and the
 * route renders its "unknown entity" state.
 */
export async function getEntitySchema(
  client: ApiClient,
  slug: string,
): Promise<EntitySchema | null> {
  const schemas = await client.listEntitySchemas();
  const match = schemas.find((s) => s.entity === slug);
  return match ? { ...match } : null;
}
