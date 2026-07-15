-- 20260616000004_tenant_vault_storage.sql
-- Multi-tenant secrets (Vault) + FT corpora (Storage) surfaces.
-- Mission MULTITENANT_DATA_PLANE (codename tenant-zero), Wave 2 task T7 -- secrets
-- and FT artifacts do NOT graduate to a tenant table; they go to Supabase Vault
-- (behind a SECURITY DEFINER RPC) and Supabase Storage (tenant-prefixed objects
-- under a RESTRICTIVE storage.objects policy). Built by N03; NOT applied (no db
-- push) in this task.
--
-- OPERATIONALIZES: N03_engineering/P08_architecture/p08_adr_multitenant_data_plane.md
--   D3 -- the tenant boundary holds on every surface; the only privilege escape is
--         scoped (Vault EXECUTE -> service_role ONLY; Storage policy RESTRICTIVE).
-- SPEC: _docs/compiled/spec_multitenant_data_plane_v1.md
--   B.4 (Vault SECURITY DEFINER RPC tenant_vault_upsert, copied verbatim -- the
--        prod org_vault_* pattern), B.5 (Storage tenant-prefix RLS policy on
--        storage.objects, mirroring B.2 on the first path segment).
--
-- CORRECTION 2026-06-16 (RESTRICTIVE-only -> PERMISSIVE tenant-prefix match):
--   The prior Storage boundary declared TWO `AS RESTRICTIVE` policies on
--   storage.objects for role authenticated and NO permissive policy for
--   authenticated. PostgreSQL RLS shows a row iff (>=1 PERMISSIVE passes) AND
--   (every RESTRICTIVE passes); with an EMPTY permissive set the AND denies every
--   object -> an authenticated user saw 0 objects ALWAYS, even its own tenant
--   prefix. Mirrors the tenant-table fix (correction logic validated 2026-06-16
--   against the live `produtos` bug; live RLS denial proven on STAGING 2026-06-20,
--   W3, as authenticated, cross-tenant denied): replaced with ONE PERMISSIVE
--   `tenant_boundary` policy that BOTH grants AND filters on the first path segment. Anti-bypass = no SECOND permissive
--   USING(true) on public/authenticated (AR1) -- NOT a RESTRICTIVE wrapper.
--
-- ANTI-RULES SATISFIED (spec B.3 -- secrets/storage variants):
--   AR1 -- NO SECOND permissive USING(true) on public/authenticated. The ONLY
--          USING(true) Storage policy is service_role_all, scoped TO service_role;
--          the Vault RPC EXECUTE is REVOKEd from public + authenticated and
--          GRANTed to service_role ONLY (no public-read bucket).
--   AR2 -- the Storage tenant boundary IS a permissive tenant-prefix-match policy
--          (NOT RESTRICTIVE-only, which with no permissive grant is a 0-rows trap).
--   AR3 -- the Storage write path (the FOR ALL boundary policy) carries WITH CHECK.
--   AR4 -- storage.objects RLS is ASSERTED, not assumed: a DEFENSIVE, idempotent
--          ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY (step 0 below)
--          guarantees the boundary is enforced even on a project that shipped it
--          OFF. FORCE is moot for this platform-owned catalog table (the tenant
--          `authenticated` role is never its owner, and FORCE only affects the
--          owner); ENABLE is the load-bearing guarantee. The boundary is added,
--          never an unguarded grant.
--   AR5 -- no blanket auth.role()='authenticated' access; the boundary matches the
--          FIRST path segment 'tenant/<tenant_id>' against the JWT claim per-object.
--
-- The boundary expression is a COALESCE that serves BOTH identity planes from
-- ONE policy: the AGENT plane sets a TOP-LEVEL tenant_id via set_config
-- (request.jwt.claims ->> 'tenant_id'); the END-USER Supabase Auth JWT carries
-- tenant_id NESTED under app_metadata (request.jwt.claims -> 'app_metadata' ->>
-- 'tenant_id'). coalesce(top-level, app_metadata) matches EITHER, here against
-- the first object path segment 'tenant/<tenant_id>'. Correction logic validated
-- 2026-06-16; live RLS denial proven on STAGING 2026-06-20 (W3, as authenticated,
-- cross-tenant denied -- tenant #2 real Supabase-Auth login saw only its own
-- rows, 0 of tenant #1's).

-- ============================================================================
-- SURFACE: secrets  (Supabase Vault behind a SECURITY DEFINER RPC -- B.4)
-- Secrets do NOT graduate to a tenant table; they live in Vault. The RPC (not the
-- caller) holds vault access; EXECUTE is granted ONLY to service_role so an
-- end-user/agent JWT can never read raw secrets. Mirrors prod org_vault_upsert.
-- ============================================================================
-- SECURITY DEFINER so the function (not the caller) holds vault access; EXECUTE
-- granted ONLY to service_role so an end-user/agent JWT cannot read raw secrets.
CREATE OR REPLACE FUNCTION tenant_vault_upsert(p_tenant_id uuid, p_name text, p_secret text)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = vault, public
AS $$
DECLARE v_id uuid;
BEGIN
  -- name-marker scoping keeps tenants partitioned inside one vault namespace.
  SELECT vault.create_secret(p_secret, format('tenant:%s:%s', p_tenant_id, p_name))
    INTO v_id;
  RETURN v_id;
END;
$$;
REVOKE ALL ON FUNCTION tenant_vault_upsert(uuid, text, text) FROM public, authenticated;
GRANT EXECUTE ON FUNCTION tenant_vault_upsert(uuid, text, text) TO service_role;

-- ============================================================================
-- SURFACE: ft  (Supabase Storage, tenant-prefixed objects -- B.5)
-- FT corpora/adapters graduate to Storage with a MANDATORY prefix
-- tenant/<tenant_id>/... and a Storage RLS policy mirroring B.2 on
-- storage.objects: RESTRICTIVE, TO authenticated, prefix match on the FIRST path
-- segment against the claim. Contract: NO unprefixed object, NO public-read
-- bucket for tenant FT artifacts.
--
-- storage.objects.name is the object path; storage.foldername(name) returns the
-- FOLDER SEGMENTS as a text[] array. For the path 'tenant/<tenant_id>/<leaf>' it
-- returns {tenant, <tenant_id>} -- so segment [1] is the literal 'tenant' and
-- segment [2] is the tenant id. The boundary therefore requires a TWO-SEGMENT
-- match: [1] = 'tenant' AND [2] = the tenant claim (read from the same
-- request.jwt.claims, coalesce(top-level tenant_id, app_metadata.tenant_id)).
--
-- BUGFIX 2026-06-20 (single-[1] mismatch -> self-DoS, fail-closed):
--   The prior boundary compared (storage.foldername(name))[1] against the literal
--   'tenant/' || <claim>. But foldername SPLITS the path on '/', so segment [1] is
--   just 'tenant' and can NEVER equal the joined string 'tenant/<tenant_id>'. The
--   PERMISSIVE policy thus matched NOTHING: a tenant saw 0 of its OWN objects (a
--   self-inflicted denial -- fail-closed, no data leak, but the FT surface was
--   unusable). The two-element form below ([1]='tenant' AND [2]=<claim>) matches
--   the documented tenant/<tenant_id>/... convention exactly. The two coalesce
--   branches (top-level + app_metadata) are kept VERBATIM from the tenant-table
--   policies so both identity planes resolve identically.
-- ============================================================================

-- 0. DEFENSIVE ENABLE -- assert RLS is ON for storage.objects (AR4). Supabase
--    ships storage.objects RLS-enabled, but a target/self-hosted project could
--    have it OFF; if it is OFF the two policies below are INERT and every
--    tenant's FT objects become globally readable. This is the LOAD-BEARING
--    guarantee, so we assert it rather than assume it. ALTER TABLE ... ENABLE
--    ROW LEVEL SECURITY is itself idempotent: if RLS is already enabled it is a
--    no-op (no error, no catalog change), so this is safe to re-run -- matching
--    the file's idempotent pattern (CREATE OR REPLACE FUNCTION above).
--
--    FORCE is intentionally NOT applied here (unlike the tenant TABLES, which
--    carry both ENABLE + FORCE). FORCE ROW LEVEL SECURITY only changes behavior
--    for the TABLE OWNER (it makes RLS apply even to the owner role, which RLS
--    otherwise exempts). storage.objects is a PLATFORM-owned catalog table; the
--    tenant-facing `authenticated` role is NEVER its owner, and the sanctioned
--    escape (service_role, policy 2 below) is granted explicitly -- not via owner
--    exemption. So FORCE would add nothing for the roles that matter here; ENABLE
--    is the guarantee that the tenant_boundary policy is actually enforced.
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 1. THE tenant-boundary policy on storage.objects -- a SINGLE PERMISSIVE
--    tenant-prefix match (ADR D3). PERMISSIVE => it is the GRANT (a permissive
--    policy must exist or RLS denies every object) AND the FILTER (it matches the
--    object path 'tenant/<tenant_id>/...' against the JWT claim, so an object
--    outside the caller's tenant prefix is invisible / unwritable). FOR ALL covers
--    read + write in one policy. The anti-bypass is NOT a RESTRICTIVE wrapper -- it
--    is the rule that NO second permissive USING(true) policy is granted to
--    public/authenticated (AR1). ONE expression serves BOTH planes via COALESCE:
--    the AGENT plane sets a TOP-LEVEL tenant_id through set_config
--    (request.jwt.claims ->> 'tenant_id', coalesce branch 1); the END-USER
--    Supabase Auth JWT carries tenant_id NESTED under app_metadata
--    (request.jwt.claims -> 'app_metadata' ->> 'tenant_id', coalesce branch 2).
--    coalesce(branch1, branch2) matches EITHER.
--
--    PREDICATE SHAPE (TWO-SEGMENT match -- bugfix 2026-06-20):
--    storage.foldername(name) returns the folder segments as text[]. For
--    'tenant/<tenant_id>/<leaf>' that is {tenant, <tenant_id>}, so:
--      (storage.foldername(name))[1] = 'tenant'        -- the literal first segment
--      (storage.foldername(name))[2] = <tenant_id>     -- matched to the claim
--    The OLD form compared [1] to the JOINED string 'tenant/'||<claim>, which
--    foldername never produces ([1] is just 'tenant'), so the policy matched
--    NOTHING and a tenant saw 0 of its own objects (self-DoS, fail-closed). USING
--    and WITH CHECK carry the IDENTICAL predicate so reads and writes are
--    constrained the same way. Mirrors the tenant-table fix; the coalesce
--    two-plane pattern had its correction logic validated 2026-06-16, with live
--    RLS denial proven on STAGING 2026-06-20 (W3, as authenticated, cross-tenant
--    denied -- tenant #2 real Supabase-Auth login saw only its own rows, 0 of
--    tenant #1's).
--
--    IDEMPOTENT: DROP POLICY IF EXISTS before CREATE so this migration re-applies
--    cleanly on a clean staging (matching the file's CREATE OR REPLACE FUNCTION +
--    ALTER ... ENABLE [no-op if on] pattern). The defensive ENABLE above stays.
DROP POLICY IF EXISTS tenant_boundary ON storage.objects;
CREATE POLICY tenant_boundary ON storage.objects
  AS PERMISSIVE
  FOR ALL                                  -- SELECT + INSERT/UPDATE/DELETE
  TO authenticated
  USING (
    (storage.foldername(name))[1] = 'tenant'
    AND (storage.foldername(name))[2] = coalesce(
          nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
          nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
        )
  )
  WITH CHECK (                             -- D3: writes MUST carry WITH CHECK (same predicate)
    (storage.foldername(name))[1] = 'tenant'
    AND (storage.foldername(name))[2] = coalesce(
          nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
          nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
        )
  );

-- 2. The service_role escape, SCOPED `TO service_role` ONLY (ADR D3).
--    service_role bypasses RLS by Postgres default; this policy is the EXPLICIT,
--    audited grant so the privilege is visible in pg_policies, NOT an implicit
--    superuser hole on role `public`. NO public-read bucket for tenant FT.
--    IDEMPOTENT: DROP POLICY IF EXISTS before CREATE (re-appliable on clean staging).
DROP POLICY IF EXISTS service_role_all ON storage.objects;
CREATE POLICY service_role_all ON storage.objects
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
