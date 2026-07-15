-- 20260618000001_tenant_data_capability_col.sql
-- Mission LEVTEST / CAPABILITY_LAYER Wave 1 -- the bug-fix migration.
-- Built by the capability-layer W1 build; NOT applied (no db push) in this task.
-- The FOUNDER applies it against the live Supabase (PREPARE-ONLY here).
--
-- WHY (the real production bug this closes):
--   apps/dashboard_api/main.py::_read_tenant_results (~line 1047) runs
--       SELECT id, capability, kind, created_at FROM tenant_data WHERE ...
--   but the `capability` column was NEVER created -- the base surface migration
--   20260616000002_tenant_data.sql defines only (id, tenant_id, kind, payload,
--   created_at). Against a live Supabase that SELECT raises
--   `column "capability" does not exist` (a 42703 SQL error) -> /results 500s.
--   This migration adds the missing column, ADDITIVE + IDEMPOTENT, so the read
--   path resolves. It also lets the capability-layer write path stamp the
--   capability slug (e.g. pesquisa_produto) as a first-class, WHERE-filterable
--   column (the dashboard's ?capability= filter), not only inside payload jsonb.
--
-- IDEMPOTENT + ADDITIVE (safe to re-run, never destructive):
--   * ADD COLUMN IF NOT EXISTS -- a re-run is a no-op; no existing row is touched.
--   * NOT NULL DEFAULT '' -- backfills every existing row to the empty string in
--     one statement (so the column is immediately NOT NULL without a separate
--     UPDATE), and a writer that omits capability still satisfies the constraint.
--   * CREATE INDEX IF NOT EXISTS ... WHERE capability <> '' -- a PARTIAL index so
--     the empty-string backfill rows do not bloat it; only real capability slugs
--     are indexed, matching the (tenant_id, capability) filter the read path uses.
--
-- RLS UNAFFECTED: the tenant_boundary PERMISSIVE policy + FORCE ROW LEVEL SECURITY
--   from 20260616000002 already cover this table column-agnostically (RLS filters
--   ROWS by tenant_id, never by which columns exist). Adding a column changes no
--   policy. No new policy, no GRANT, no service_role change is needed here.

-- 1. Add the missing column (additive + idempotent). The DEFAULT '' backfills all
--    existing rows so the NOT NULL holds immediately without a separate UPDATE.
ALTER TABLE tenant_data ADD COLUMN IF NOT EXISTS capability text NOT NULL DEFAULT '';

-- 2. A partial composite index for the (tenant_id, capability) read filter. WHERE
--    capability <> '' keeps the empty-string backfill rows out of the index.
CREATE INDEX IF NOT EXISTS idx_tenant_data_capability
  ON tenant_data(tenant_id, capability)
  WHERE capability <> '';
