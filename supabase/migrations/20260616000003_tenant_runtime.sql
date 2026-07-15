-- 20260616000003_tenant_runtime.sql
-- Multi-tenant runtime surface: tenant_runtime (handoffs/signals/decisions analog)
-- + a SINGLE PERMISSIVE tenant-match RLS boundary.
-- Mission MULTITENANT_DATA_PLANE (codename tenant-zero), Wave 2 task T6 -- the
-- second surface to REPLICATE the template-first memory pattern (20260616000001).
-- Built by N03; NOT applied (no db push) in this task.
--
-- CORRECTION 2026-06-16 (RESTRICTIVE-only -> PERMISSIVE tenant-match):
--   The prior template declared the boundary as TWO `AS RESTRICTIVE` policies for
--   role authenticated and NO permissive policy for authenticated. PostgreSQL RLS
--   shows a row iff (>=1 PERMISSIVE passes) AND (every RESTRICTIVE passes); with an
--   EMPTY permissive set the AND denies every row -> authenticated saw 0 rows
--   ALWAYS, even its OWN tenant. Correction logic validated 2026-06-16 (against
--   the live `produtos` bug); live RLS denial proven on STAGING 2026-06-20 (W3,
--   as authenticated, cross-tenant denied) -- a SINGLE PERMISSIVE tenant-match
--   policy isolates correctly (own-tenant visible, other tenants invisible).
--   The fix is ONE PERMISSIVE `tenant_boundary` policy
--   that grants AND filters. Anti-bypass = no SECOND permissive USING(true) on
--   public/authenticated (AR1, drift-check enforced) -- NOT a RESTRICTIVE wrapper.
--
-- OPERATIONALIZES: N03_engineering/P08_architecture/p08_adr_multitenant_data_plane.md
--   D2 -- tenant_id uuid not null + mandatory index is the canonical tenant key.
--   D3 -- the tenant boundary is a SINGLE PERMISSIVE tenant-match policy (grants
--         AND filters); writes carry WITH CHECK; the service_role escape is a
--         separate PERMISSIVE policy scoped TO service_role ONLY.
-- SPEC: _docs/compiled/spec_multitenant_data_plane_v1.md
--   B.1 (tenant_runtime table + index, copied verbatim), B.2 (PERMISSIVE
--   tenant-match boundary, byte-pattern replica of tenant_memory), C.1 (the
--   cross-tenant-denial gate this file must satisfy symmetrically with memory).
--
-- ANTI-RULES SATISFIED (spec B.3 -- the produtos bypass, encoded as forbidden):
--   AR1 -- NO SECOND permissive USING(true) policy on role public/authenticated;
--          the ONLY USING(true) policy is service_role_all, scoped TO service_role.
--   AR2 -- the boundary IS a permissive tenant-match policy (NOT RESTRICTIVE-only,
--          which with no permissive grant is a 0-rows trap).
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
-- SURFACE: runtime  (tenant runtime state -- handoffs/signals/decisions analog)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenant_runtime (
  id          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id   uuid        NOT NULL,                       -- D2 canonical key
  scope       text        NOT NULL,                       -- handoff | signal | decision
  state       jsonb       NOT NULL DEFAULT '{}'::jsonb,
  updated_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_tenant_runtime_tenant ON tenant_runtime(tenant_id);   -- D2 MANDATORY

-- 1. Enable RLS (and FORCE so even the table owner is subject to it).
ALTER TABLE tenant_runtime ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_runtime FORCE ROW LEVEL SECURITY;

-- 2. THE tenant-boundary policy -- a SINGLE PERMISSIVE tenant-match (ADR D3).
--    PERMISSIVE => it is the GRANT (a permissive policy must exist or RLS denies
--    every row) AND the FILTER (USING/WITH CHECK match tenant_id to the claim).
--    FOR ALL covers SELECT + write paths in one policy. The anti-bypass is NOT a
--    RESTRICTIVE wrapper -- it is the rule that NO second permissive USING(true)
--    policy is granted to public/authenticated (the produtos bug = AR1,
--    drift-check enforced). ONE expression serves BOTH planes via COALESCE: the
--    AGENT plane sets a TOP-LEVEL tenant_id through set_config (request.jwt.claims
--    ->> 'tenant_id', coalesce branch 1); the END-USER Supabase Auth JWT carries
--    tenant_id NESTED under app_metadata (request.jwt.claims -> 'app_metadata' ->>
--    'tenant_id', coalesce branch 2). coalesce(branch1, branch2) matches EITHER.
--    Correction logic validated 2026-06-16; live RLS denial proven on STAGING
--    2026-06-20 (W3, as authenticated, cross-tenant denied -- tenant #2 real
--    Supabase-Auth login saw only its own rows, 0 of tenant #1's).
DROP POLICY IF EXISTS tenant_boundary ON tenant_runtime;
CREATE POLICY tenant_boundary ON tenant_runtime
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
DROP POLICY IF EXISTS service_role_all ON tenant_runtime;
CREATE POLICY service_role_all ON tenant_runtime
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
