-- 20260619000001_marketplace_observation.sql
-- Time-series store for marketplace catalog observations -- the longitudinal
-- foundation (the Keepa / Nubimetrics moat). ONE row per tracked candidate PER
-- capture; velocity / price-history / seasonality are computed AT READ from the
-- rows (never stored), so a schema change never invalidates history.
-- Spec: _docs/compiled/spec_extraction_depth_v1.md Section 4 (the table DDL) + W4.
-- Built by N03 (WAVE 4); NOT applied (no db push) in this task -- the live-DB
-- apply is FOUNDER-GATED (spec W4 + Section 8 "Live-DB apply"); N07 may apply to
-- a clean STAGING project separately for the RLS denial proof.
--
-- RLS PATTERN: a BYTE-PATTERN-IDENTICAL copy of the tenant_data boundary
-- (20260616000002_tenant_data.sql) -- a SINGLE PERMISSIVE tenant-match policy
-- (grants AND filters) + WITH CHECK + the service_role escape scoped TO
-- service_role ONLY + ENABLE/FORCE RLS. The boundary block below is copied
-- verbatim from tenant_data; only the table name differs. Do NOT invent a new
-- boundary -- replication is the security guarantee.
--
-- OPERATIONALIZES: N03_engineering/P08_architecture/p08_adr_multitenant_data_plane.md
--   D2 -- tenant_id uuid not null + mandatory index is the canonical tenant key.
--   D3 -- the tenant boundary is a SINGLE PERMISSIVE tenant-match policy (grants
--         AND filters); writes carry WITH CHECK; the service_role escape is a
--         separate PERMISSIVE policy scoped TO service_role ONLY.
--
-- ANTI-RULES SATISFIED (the produtos bypass, encoded as forbidden -- the
-- cex_rls_drift_check linter MUST pass on this table):
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
-- 'tenant_id'). coalesce(top-level, app_metadata) matches EITHER -- identical to
-- tenant_data; correction logic validated 2026-06-16, live RLS denial proven on
-- STAGING 2026-06-20 (W3, as authenticated, cross-tenant denied).

-- ============================================================================
-- SURFACE: marketplace_observation  (tenant-scoped time-series capture rows)
-- ============================================================================
CREATE TABLE IF NOT EXISTS marketplace_observation (
  id              uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id       uuid        NOT NULL,                       -- D2 canonical key
  marketplace     text        NOT NULL,                       -- 'mercado_livre' | 'amazon_br' | 'shopee'
  item_id         text,                                       -- MLBxxx / ASIN / itemid
  catalog_id      text,                                       -- catalog_product_id / ASIN parent
  captured_at     timestamptz NOT NULL DEFAULT now(),         -- the capture instant (the TS axis)
  price           numeric,                                    -- BRL, cents-correct (Section 3 fix)
  sold            integer,                                    -- exact (ML) or bucket-floor (honest)
  sold_bucket     text,                                       -- the raw ML bucket label when bucketed
  bsr_rank        integer,                                    -- Amazon BSR / category rank (null on ML)
  buy_box_seller  text,                                       -- price_to_win winner (null off-ML)
  num_offers      integer,                                    -- products/items paging.total
  rating          numeric,                                    -- avg stars
  reviews         integer,                                    -- review count
  source          text        NOT NULL DEFAULT 'meli_api',    -- provenance of THIS row
  created_at      timestamptz NOT NULL DEFAULT now()
);
-- D2 MANDATORY: the tenant index. Plus the series index (the read path scans by
-- tenant + marketplace + item ordered by captured_at to compute velocity/history).
CREATE INDEX IF NOT EXISTS idx_mktobs_tenant ON marketplace_observation(tenant_id);
CREATE INDEX IF NOT EXISTS idx_mktobs_series ON marketplace_observation(tenant_id, marketplace, item_id, captured_at);

-- 1. Enable RLS (and FORCE so even the table owner is subject to it).
ALTER TABLE marketplace_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_observation FORCE ROW LEVEL SECURITY;

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
--    Copied verbatim from 20260616000002_tenant_data.sql (the proven boundary).
DROP POLICY IF EXISTS tenant_boundary ON marketplace_observation;
CREATE POLICY tenant_boundary ON marketplace_observation
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
DROP POLICY IF EXISTS service_role_all ON marketplace_observation;
CREATE POLICY service_role_all ON marketplace_observation
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
