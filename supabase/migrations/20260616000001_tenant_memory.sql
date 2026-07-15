-- 20260616000001_tenant_memory.sql
-- Multi-tenant memory surface: tenant_memory (pgvector) + a SINGLE PERMISSIVE
-- tenant-match RLS boundary.
-- Mission MULTITENANT_DATA_PLANE (codename tenant-zero), Wave 2 task T2 -- the
-- template-first surface. Built by N03; NOT applied (no db push) in this task.
--
-- CORRECTION 2026-06-16 (RESTRICTIVE-only -> PERMISSIVE tenant-match):
--   The prior template declared the boundary as TWO `AS RESTRICTIVE` policies
--   (tenant_boundary_select + tenant_boundary_modify) for role authenticated and
--   NO permissive policy for authenticated. In PostgreSQL RLS a row is visible
--   iff (>=1 PERMISSIVE policy passes) AND (every RESTRICTIVE policy passes). With
--   NO permissive policy for `authenticated`, the permissive set is EMPTY, so the
--   AND short-circuits to deny -> an authenticated user saw 0 rows ALWAYS, even
--   its OWN tenant (a self-DoS, not isolation). Correction logic validated
--   2026-06-16 (against the live `produtos` bug); live RLS denial proven on
--   STAGING 2026-06-20 (W3, as authenticated, cross-tenant denied) -- a SINGLE
--   PERMISSIVE policy doing the tenant match isolates correctly (own-tenant
--   visible, other tenants invisible).
--
--   THE FIX: ONE PERMISSIVE `tenant_boundary` policy that BOTH grants (a permissive
--   policy exists) AND filters (USING/WITH CHECK match tenant_id to the claim).
--   The anti-bypass is NOT "make it RESTRICTIVE" -- it is "never add a SECOND
--   permissive policy (especially USING(true)) for public/authenticated", which is
--   exactly the produtos bug class (AR1) and is enforced by cex_rls_drift_check.py.
--
-- OPERATIONALIZES: N03_engineering/P08_architecture/p08_adr_multitenant_data_plane.md
--   D2 -- tenant_id uuid not null + mandatory index is the canonical tenant key.
--   D3 -- the tenant boundary is a SINGLE PERMISSIVE tenant-match policy (it grants
--         AND filters in one); writes carry WITH CHECK; the service_role escape is
--         a separate PERMISSIVE policy scoped TO service_role ONLY.
-- SPEC: _docs/compiled/spec_multitenant_data_plane_v1.md
--   B.1 (table + both indexes, copied verbatim), B.2 (PERMISSIVE tenant-match
--   boundary, copied verbatim), C.1 (the cross-tenant-denial gate this file must
--   satisfy -- own-tenant rows VISIBLE, other-tenant rows invisible/unwritable).
--
-- ANTI-RULES SATISFIED (spec B.3 -- the produtos bypass, encoded as forbidden):
--   AR1 -- NO SECOND permissive policy with USING(true) on role public/authenticated;
--          the ONLY USING(true) policy is service_role_all, scoped TO service_role.
--          This is THE anti-bypass (a USING(true) sibling would OR-grant everything).
--   AR2 -- the boundary IS a permissive tenant-match policy (NOT RESTRICTIVE-only:
--          a RESTRICTIVE-only set with no permissive grant is a 0-rows trap).
--   AR3 -- every write path (the FOR ALL boundary policy) carries WITH CHECK.
--   AR4 -- ENABLE ROW LEVEL SECURITY + FORCE ROW LEVEL SECURITY are both present.
--   AR5 -- no blanket auth.role()='authenticated' read; the boundary matches
--          tenant_id against the JWT claim per-row, never role-only.
--
-- The boundary expression is a COALESCE that serves BOTH identity planes from
-- ONE policy: the AGENT plane sets a TOP-LEVEL tenant_id via set_config
-- (request.jwt.claims ->> 'tenant_id'); the END-USER Supabase Auth JWT carries
-- tenant_id NESTED under app_metadata (request.jwt.claims -> 'app_metadata' ->>
-- 'tenant_id'). coalesce(top-level, app_metadata) matches EITHER. Correction
-- logic validated 2026-06-16; live RLS denial proven on STAGING 2026-06-20 (W3,
-- as authenticated, cross-tenant denied -- tenant #2 real Supabase-Auth login
-- saw only its own rows, 0 of tenant #1's).

-- ============================================================================
-- SURFACE: memory  (template-first -- built + denial-gate-green FIRST)
-- pgvector store, modeled on kc_embeddings + tenant_id (manifest D5: memory=pilot)
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS tenant_memory (
  id          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id   uuid        NOT NULL,                       -- D2 canonical key
  namespace   text        NOT NULL,                       -- mirrors p10 memory_namespace '<tid>/'
  content     text        NOT NULL,
  embedding   vector(1536),                               -- text-embedding-3-small width
  metadata    jsonb       NOT NULL DEFAULT '{}'::jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_tenant_memory_tenant ON tenant_memory(tenant_id);   -- D2 MANDATORY
CREATE INDEX IF NOT EXISTS idx_tenant_memory_vec
  ON tenant_memory USING hnsw (embedding vector_cosine_ops);                        -- ANN, >1000 rows

-- 1. Enable RLS (and FORCE so even the table owner is subject to it).
ALTER TABLE tenant_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_memory FORCE ROW LEVEL SECURITY;

-- 2. THE tenant-boundary policy -- a SINGLE PERMISSIVE tenant-match (ADR D3).
--    PERMISSIVE => it is the GRANT (a permissive policy must exist or RLS denies
--    every row) AND the FILTER (the USING/WITH CHECK match tenant_id to the claim,
--    so only the caller's own tenant passes). FOR ALL covers SELECT + the write
--    paths in one policy. The anti-bypass is NOT a RESTRICTIVE wrapper -- it is the
--    rule that NO second permissive USING(true) policy is granted to
--    public/authenticated (that produtos bug is AR1, drift-check enforced).
--    ONE expression serves BOTH planes via COALESCE: the AGENT plane sets a
--    TOP-LEVEL tenant_id through set_config (request.jwt.claims ->> 'tenant_id',
--    coalesce branch 1); the END-USER Supabase Auth JWT carries tenant_id NESTED
--    under app_metadata (request.jwt.claims -> 'app_metadata' ->> 'tenant_id',
--    coalesce branch 2). coalesce(branch1, branch2) matches EITHER plane. Proven
--    on staging 2026-06-16 (tenant #2 real Supabase-Auth login -> saw only
--    its own rows, 0 of tenant #1's).
DROP POLICY IF EXISTS tenant_boundary ON tenant_memory;
CREATE POLICY tenant_boundary ON tenant_memory
  AS PERMISSIVE
  FOR ALL                                  -- SELECT + INSERT/UPDATE/DELETE
  TO authenticated
  USING (
    (tenant_id)::text = coalesce(
      nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
      nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
    )
  )
  WITH CHECK (                             -- D3: writes MUST carry WITH CHECK
    (tenant_id)::text = coalesce(
      nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
      nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
    )
  );

-- 3. The service_role escape, SCOPED `TO service_role` ONLY (ADR D3).
--    service_role bypasses RLS by Postgres default; this policy is the EXPLICIT,
--    audited grant so the privilege is visible in pg_policies, NOT an implicit
--    superuser hole on role `public`.
DROP POLICY IF EXISTS service_role_all ON tenant_memory;
CREATE POLICY service_role_all ON tenant_memory
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
