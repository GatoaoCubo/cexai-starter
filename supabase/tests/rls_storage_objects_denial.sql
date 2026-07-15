-- rls_storage_objects_denial.sql
-- Mission MULTITENANT_DATA_PLANE (codename tenant-zero), Wave 2 task T7 -- the
-- SECURITY GATE test for the `ft` (FT corpora / adapters) surface, which graduates
-- to Supabase Storage as tenant-prefixed objects under storage.objects. This is the
-- DB-side layer that proves the tenant_boundary PREFIX-MATCH RLS policy in
-- 20260616000004_tenant_vault_storage.sql actually denies a tenant-A session any
-- read of tenant-B objects, rejects a cross-tenant write by WITH CHECK, and does NOT
-- leak a transaction-local claim to the next borrower of a pooled connection.
--
-- It is the storage sibling of rls_tenant_memory_denial.sql (the tenant TABLE gate).
-- The storage boundary is the MOST DIFFERENT boundary expression in the data plane:
-- a path-PREFIX match on storage.objects.name, not a tenant_id column equality. This
-- file is the only test that exercises that prefix-match expression directly.
--
-- ============================================================================
-- !! PLATFORM REQUIREMENT -- THIS TEST NEEDS A SUPABASE-SCHEMA POSTGRES !!
-- ============================================================================
-- storage.objects and storage.foldername(text) are NOT part of a vanilla Postgres
-- install -- they are created by Supabase's `storage` schema (the supabase/storage
-- service migrations). On a plain `postgres:16` image this test ABORTS at the
-- precondition (relation storage.objects not found) by design -- it never silently
-- passes. Run it ONLY against a Supabase-schema Postgres:
--   - the `supabase/postgres` Docker image, OR
--   - a database brought up by the Supabase CLI (`npx supabase start`), OR
--   - a (staging, NEVER production) Supabase project's pooled connection.
-- CI author: route this file to the supabase/postgres job, NOT the vanilla-PG job.
-- (The sibling rls_tenant_memory_denial.sql runs on either; this one does not.)
--
-- SPEC: _docs/compiled/spec_multitenant_data_plane_v1.md
--   B.5  -- the Storage tenant-prefix RLS policy under test (a SINGLE PERMISSIVE
--           tenant_boundary FOR ALL TO authenticated, USING + WITH CHECK = a
--           two-segment match: (foldername(name))[1]='tenant' AND [2]=<tenant_id>
--           matched against the claim, coalesce(top-level, app_metadata)).
--   A.5  -- the pooled-conn leak check: a fresh transaction on the SAME session with
--           NO set_config sees 0 objects (proves is_local := true on the bind).
--   D3   -- the boundary holds on every surface; the only escape is service_role,
--           scoped via the service_role_all PERMISSIVE policy.
--
-- MIGRATION UNDER TEST: supabase/migrations/20260616000004_tenant_vault_storage.sql
--
-- DESIGN NOTE -- every assertion RAISEs on failure. psql with `-v ON_ERROR_STOP=1`
-- (or `--set=ON_ERROR_STOP=1`) turns any RAISE EXCEPTION into a non-zero process
-- exit, so a clean exit code 0 == ALL assertions passed and a non-zero/error exit
-- == FAIL. There is NO path that fakes a pass; pgTAP is not required (plain DO
-- blocks + RAISE).
--
-- NOTE on the boundary expression + object naming (HONESTY GATE) -- the policy
-- matches storage.foldername(name) on TWO segments: [1] = 'tenant' AND
-- [2] = <tenant_id> (the claim). storage.foldername(text) returns the folder
-- segments of an object path; for 'tenant/<id>/<leaf>' it returns {tenant, <id>}.
-- The seed object names below are built so that segment [1] equals exactly
-- 'tenant' and segment [2] equals exactly '<id>' (see section 0b, which
-- EMPIRICALLY verifies the constructed name matches the boundary for tenant A and
-- RAISEs if it does not -- so a foldername-semantics mismatch between the
-- migration's expression and this naming convention fails the gate LOUDLY instead
-- of silently passing). Every seed/probe name is derived from
-- _seed_name(tenant_id, leaf) so the test and the migration agree by construction.
-- (Corrected 2026-06-20: the prior gate expected segment [1] == 'tenant/<id>', the
-- same single-[1] mismatch the migration carried; foldername splits on '/', so [1]
-- is 'tenant' and [2] is '<id>'.)
--
-- ============================================================================
-- RUNBOOK
-- ============================================================================
-- CI (Supabase-schema Postgres -- see PLATFORM REQUIREMENT above):
--
--   npx supabase start                      # boots Postgres WITH the storage schema
--   psql "$(npx supabase status -o env | grep DB_URL | cut -d= -f2-)" \
--        -v ON_ERROR_STOP=1 \
--        -f supabase/migrations/20260616000004_tenant_vault_storage.sql \
--        -f supabase/tests/rls_storage_objects_denial.sql
--   # exit 0 = gate GREEN; any non-zero = gate FAIL (cross-tenant FT leak).
--
-- The migration is applied FIRST (idempotent: CREATE OR REPLACE FUNCTION +
-- ALTER ... ENABLE [no-op if already on] + CREATE POLICY). This test assumes the
-- tenant_boundary + service_role_all policies on storage.objects exist; it does NOT
-- re-create them.
--
-- W3 (staging project, spec E.3 live denial proof): run the SAME two psql -f
-- invocations against the STAGING Supabase project's pooled connection string (NOT
-- the live brain at <prod-ref>). NEVER point this at production data.
-- ============================================================================

-- ASCII-only. All identifiers + literals are 0x00-0x7F.

-- Canonical fixture tenants (mirrors rls_tenant_memory_denial.sql C.1).
--   A = 11111111-1111-1111-1111-111111111111  (2 objects: tenant/<A>/adapter.bin, tenant/<A>/corpus.jsonl)
--   B = 22222222-2222-2222-2222-222222222222  (2 objects: tenant/<B>/adapter.bin, tenant/<B>/corpus.jsonl)
-- Bucket: 'ft' (a private bucket for tenant FT artifacts; no public-read).

-- Wrap the whole gate in one transaction so a failure leaves no partial seed and
-- the ROLE/claim changes are scoped. ON_ERROR_STOP makes any RAISE abort + exit
-- non-zero. We ROLLBACK before the pooled-conn section (a separate connection-level
-- proof) and clean up at the end: this is a read-only PROOF, not a fixture loader.
BEGIN;

-- --------------------------------------------------------------------------- --
-- 0. Preconditions -- fail loudly if the platform/migration is not in place.   --
--    Mirrors rls_tenant_memory_denial.sql section 0 (RLS-enabled + PERMISSIVE  --
--    boundary present + no public USING(true)), adapted to storage.objects.    --
-- --------------------------------------------------------------------------- --
DO $$
BEGIN
  -- Platform: the storage schema must exist (this is the Supabase-only dependency).
  IF to_regclass('storage.objects') IS NULL THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL: relation storage.objects not found. This test REQUIRES a '
      'Supabase-schema Postgres (supabase/postgres image or `npx supabase start`); '
      'it does NOT run on a vanilla Postgres. See PLATFORM REQUIREMENT in the header.';
  END IF;
  IF to_regprocedure('storage.foldername(text)') IS NULL THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL: function storage.foldername(text) not found -- the storage '
      'schema is incomplete. Use the supabase/postgres image (see header).';
  END IF;

  -- AR4: storage.objects MUST have ROW LEVEL SECURITY enabled, else the boundary is
  -- INERT and every tenant''s FT objects are globally readable.
  IF NOT EXISTS (
    SELECT 1 FROM pg_class
    WHERE oid = 'storage.objects'::regclass AND relrowsecurity
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR4): storage.objects does not have ROW LEVEL SECURITY '
      'enabled -- the tenant_boundary policy is inert; FT objects are globally '
      'readable. Apply 20260616000004_tenant_vault_storage.sql (its defensive '
      'ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY) BEFORE this test.';
  END IF;

  -- AR2: the boundary MUST be a SINGLE PERMISSIVE tenant-match policy for
  -- authenticated. A PERMISSIVE policy is REQUIRED: in PG RLS a row is visible iff
  -- (>=1 PERMISSIVE passes) AND (all RESTRICTIVE pass); without a permissive grant
  -- the boundary denies EVERY object -- even the caller''s own tenant prefix (the
  -- RESTRICTIVE-only 0-rows trap that bit the prior storage policy, corrected
  -- 2026-06-16). pg_policies for storage.objects use schemaname='storage'.
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'storage'
      AND tablename = 'objects'
      AND policyname = 'tenant_boundary'
      AND permissive = 'PERMISSIVE'
      AND roles @> ARRAY['authenticated']::name[]
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR2): the PERMISSIVE tenant_boundary policy on '
      'storage.objects for authenticated is missing -- a RESTRICTIVE-only boundary '
      '(no permissive grant) denies every object, even the caller''s own prefix.';
  END IF;
  -- AR2 (explicit): NO RESTRICTIVE policy for authenticated without an accompanying
  -- PERMISSIVE grant. The boundary must be permissive, not RESTRICTIVE-only.
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'storage' AND tablename = 'objects'
      AND permissive = 'RESTRICTIVE'
      AND roles @> ARRAY['authenticated']::name[]
  ) AND NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'storage' AND tablename = 'objects'
      AND permissive = 'PERMISSIVE'
      AND roles @> ARRAY['authenticated']::name[]
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR2): storage.objects has RESTRICTIVE policy(ies) for '
      'authenticated but NO permissive grant -- the 0-rows trap.';
  END IF;

  -- AR1: NO permissive USING(true) policy on public/authenticated. The only
  -- USING(true) allowed is service_role_all, scoped TO {service_role}. Such a 2nd
  -- permissive grant on a broad role would OR-nullify the tenant boundary (the
  -- produtos bypass class).
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'storage' AND tablename = 'objects'
      AND permissive = 'PERMISSIVE'
      AND qual = 'true'
      AND (roles @> ARRAY['public']::name[] OR roles @> ARRAY['authenticated']::name[])
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR1): a PERMISSIVE USING(true) policy is granted to '
      'public/authenticated on storage.objects -- this OR-nullifies the tenant '
      'boundary (the produtos bypass). Scope the service_role escape TO service_role.';
  END IF;

  RAISE NOTICE 'preconditions OK: storage.objects RLS enabled, PERMISSIVE tenant_boundary present, no public USING(true).';
END
$$;

-- A deterministic seed-name helper: 'tenant/<tenant_id>/<leaf>'. Both the seed
-- objects and the boundary derive the tenant prefix the same way, so the test and
-- the migration agree by construction (the boundary checks (foldername(name))[1] =
-- 'tenant' AND [2] = <tenant_id>). Transaction-local (pg_temp), dropped on COMMIT/ABORT.
CREATE OR REPLACE FUNCTION pg_temp._seed_name(p_tenant uuid, p_leaf text)
RETURNS text LANGUAGE sql IMMUTABLE AS $$
  SELECT 'tenant/' || p_tenant::text || '/' || p_leaf
$$;

-- --------------------------------------------------------------------------- --
-- 0b. HONESTY GATE -- prove the boundary expression matches the constructed     --
--     name for tenant A. The tenant_boundary policy is a TWO-SEGMENT match:      --
--     (foldername(<A name>))[1] MUST equal 'tenant' AND [2] MUST equal '<A>'. If --
--     storage.foldername splits the path differently than this naming convention --
--     assumes, the boundary could never match A''s own objects and the count     --
--     assertions below would be meaningless -- so we RAISE here LOUDLY rather     --
--     than let the gate pass on a mismatched assumption. (This gate is keyed to   --
--     the CORRECTED 2-segment predicate; the old single-[1]='tenant/<id>' form    --
--     was the bug, since foldername returns {tenant, <id>}.)                      --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  a_name     text := pg_temp._seed_name('11111111-1111-1111-1111-111111111111', 'probe.bin');
  segs       text[];
  seg1       text;
  seg2       text;
  expected2  text := '11111111-1111-1111-1111-111111111111';
BEGIN
  segs := storage.foldername(a_name);
  seg1 := segs[1];
  seg2 := segs[2];
  -- Segment [1] must be the literal 'tenant' (the boundary's first conjunct).
  IF seg1 IS DISTINCT FROM 'tenant' THEN
    RAISE EXCEPTION
      'BOUNDARY/NAMING MISMATCH: (storage.foldername(%))[1] = % but the tenant_boundary '
      'policy requires segment [1] = ''tenant''. The migration boundary expression and '
      'this test''s object-naming convention disagree on this Postgres -- fix one so '
      'segment [1] of a seeded object equals ''tenant''. (Refusing to report a pass on a '
      'boundary that cannot match its own tenant.)', a_name, seg1;
  END IF;
  -- Segment [2] must be A''s tenant_id (the boundary's second conjunct, vs the claim).
  IF seg2 IS DISTINCT FROM expected2 THEN
    RAISE EXCEPTION
      'BOUNDARY/NAMING MISMATCH: (storage.foldername(%))[2] = % but the tenant_boundary '
      'policy matches segment [2] against the tenant claim % . The migration boundary '
      'expression and this test''s object-naming convention disagree on this Postgres -- '
      'fix one so segment [2] of a seeded object equals ''<tenant_id>''. (Refusing to '
      'report a pass on a boundary that cannot match its own tenant.)', a_name, seg2, expected2;
  END IF;
  RAISE NOTICE 'honesty gate OK: (foldername)[1] = % and [2] = % of a seeded A object (matches the 2-segment boundary).', seg1, seg2;
END
$$;

-- --------------------------------------------------------------------------- --
-- 1. Seed as service_role (the explicit B.5 escape via service_role_all         --
--    PERMISSIVE TO service_role -- lets these inserts through regardless of any  --
--    claim). 2 objects per tenant under tenant/<id>/... in the private 'ft'      --
--    bucket. We set owner = NULL (object owner is irrelevant to the prefix       --
--    boundary; the boundary keys on name, not owner).                           --
-- --------------------------------------------------------------------------- --
SET LOCAL ROLE service_role;

INSERT INTO storage.objects (bucket_id, name, owner) VALUES
  ('ft', pg_temp._seed_name('11111111-1111-1111-1111-111111111111', 'adapter.bin'),   NULL),
  ('ft', pg_temp._seed_name('11111111-1111-1111-1111-111111111111', 'corpus.jsonl'),  NULL),
  ('ft', pg_temp._seed_name('22222222-2222-2222-2222-222222222222', 'adapter.bin'),   NULL),
  ('ft', pg_temp._seed_name('22222222-2222-2222-2222-222222222222', 'corpus.jsonl'),  NULL);

RESET ROLE;

-- Sanity: as service_role (bypassing the boundary) exactly our 4 seeded objects in
-- the 'ft' bucket under a tenant/ prefix are present.
DO $$
DECLARE n integer;
BEGIN
  SET LOCAL ROLE service_role;
  SELECT count(*) INTO n
    FROM storage.objects
    WHERE bucket_id = 'ft' AND name LIKE 'tenant/%';
  RESET ROLE;
  IF n <> 4 THEN
    RAISE EXCEPTION 'SEED FAIL: expected 4 seeded ft objects as service_role, got %', n;
  END IF;
  RAISE NOTICE 'seed OK: 4 ft objects (A=2, B=2) visible to service_role.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 2. Bind tenant A (TOP-LEVEL claim -- the AGENT/adapter plane, coalesce        --
--    branch 1) and assert the storage denial matrix (spec B.5, A side).         --
--    set_config(..., is_local := true) mirrors bind_session_tenant. SET LOCAL   --
--    ROLE authenticated makes the boundary apply (service_role would bypass).   --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_a_total    integer;
  n_b_visible  integer;
  insert_blocked boolean := false;
BEGIN
  PERFORM set_config(
    'request.jwt.claims',
    json_build_object('tenant_id', '11111111-1111-1111-1111-111111111111')::text,
    true   -- is_local => scoped to THIS transaction (pooled-conn safe, spec A.5)
  );
  SET LOCAL ROLE authenticated;

  -- THEN: only A's 2 objects are visible (bucket scoping kept tight to our seed).
  SELECT count(*) INTO n_a_total
    FROM storage.objects
    WHERE bucket_id = 'ft' AND name LIKE 'tenant/%';
  IF n_a_total <> 2 THEN
    RAISE EXCEPTION 'A-SELECT FAIL: bound to A, expected 2 visible ft objects, got %', n_a_total;
  END IF;

  -- THEN: B's objects are invisible (0 of B's seeded under A's claim).
  SELECT count(*) INTO n_b_visible
    FROM storage.objects
    WHERE bucket_id = 'ft'
      AND name LIKE 'tenant/' || '22222222-2222-2222-2222-222222222222' || '/%';
  IF n_b_visible <> 0 THEN
    RAISE EXCEPTION 'A-ISOLATION FAIL: B ft objects visible while bound to A (got %)', n_b_visible;
  END IF;

  -- THEN: inserting an object under tenant/<B>/... is REJECTED by WITH CHECK (D3).
  -- The policy violation raises SQLSTATE 42501 (insufficient_privilege) -- catch
  -- ONLY that, so an unrelated error still fails the gate.
  BEGIN
    INSERT INTO storage.objects (bucket_id, name, owner)
      VALUES ('ft', pg_temp._seed_name('22222222-2222-2222-2222-222222222222', 'A-writes-into-B.bin'), NULL);
  EXCEPTION
    WHEN insufficient_privilege THEN
      insert_blocked := true;
  END;
  IF NOT insert_blocked THEN
    RAISE EXCEPTION
      'A-INSERT FAIL: bound to A, an INSERT of an object under tenant/<B>/ was NOT '
      'rejected by WITH CHECK (cross-tenant FT write leak).';
  END IF;

  RESET ROLE;
  RAISE NOTICE 'A-bound storage denial matrix OK: see=2, B-visible=0, B-prefix insert blocked.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 3. Symmetric: bind tenant B and assert the mirror matrix (spec B.5, B side).  --
--    B has 2 objects; A (2 objects) must be invisible / unwritable.            --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_b_total    integer;
  n_a_visible  integer;
  insert_blocked boolean := false;
BEGIN
  PERFORM set_config(
    'request.jwt.claims',
    json_build_object('tenant_id', '22222222-2222-2222-2222-222222222222')::text,
    true
  );
  SET LOCAL ROLE authenticated;

  SELECT count(*) INTO n_b_total
    FROM storage.objects
    WHERE bucket_id = 'ft' AND name LIKE 'tenant/%';
  IF n_b_total <> 2 THEN
    RAISE EXCEPTION 'B-SELECT FAIL: bound to B, expected 2 visible ft objects, got %', n_b_total;
  END IF;

  SELECT count(*) INTO n_a_visible
    FROM storage.objects
    WHERE bucket_id = 'ft'
      AND name LIKE 'tenant/' || '11111111-1111-1111-1111-111111111111' || '/%';
  IF n_a_visible <> 0 THEN
    RAISE EXCEPTION 'B-ISOLATION FAIL: A ft objects visible while bound to B (got %)', n_a_visible;
  END IF;

  BEGIN
    INSERT INTO storage.objects (bucket_id, name, owner)
      VALUES ('ft', pg_temp._seed_name('11111111-1111-1111-1111-111111111111', 'B-writes-into-A.bin'), NULL);
  EXCEPTION
    WHEN insufficient_privilege THEN
      insert_blocked := true;
  END;
  IF NOT insert_blocked THEN
    RAISE EXCEPTION
      'B-INSERT FAIL: bound to B, an INSERT of an object under tenant/<A>/ was NOT '
      'rejected by WITH CHECK (cross-tenant FT write leak).';
  END IF;

  RESET ROLE;
  RAISE NOTICE 'B-bound storage denial matrix OK: see=2, A-visible=0, A-prefix insert blocked.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 3b. END-USER PLANE (coalesce branch 2): bind tenant A via the NESTED          --
--     app_metadata claim instead of the top-level one. A Supabase Auth JWT      --
--     carries tenant_id under app_metadata, NOT at the top level. The boundary  --
--     coalesce(top-level, app_metadata) must isolate identically when ONLY      --
--     app_metadata.tenant_id is present. This is the end-user plane the adapter --
--     does NOT drive; it proves the SAME single policy serves BOTH planes.       --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_a_total    integer;
  n_b_visible  integer;
  insert_blocked boolean := false;
BEGIN
  -- Claim shaped like a real Supabase Auth JWT: tenant_id ONLY under app_metadata,
  -- NO top-level tenant_id. coalesce branch 1 (top-level) is NULL here -> branch 2
  -- (app_metadata) must supply the tenant.
  PERFORM set_config(
    'request.jwt.claims',
    json_build_object(
      'app_metadata',
      json_build_object('tenant_id', '11111111-1111-1111-1111-111111111111')
    )::text,
    true
  );
  SET LOCAL ROLE authenticated;

  SELECT count(*) INTO n_a_total
    FROM storage.objects
    WHERE bucket_id = 'ft' AND name LIKE 'tenant/%';
  IF n_a_total <> 2 THEN
    RAISE EXCEPTION
      'APPMETA-SELECT FAIL: bound to A via app_metadata, expected 2 visible ft objects, '
      'got %. The coalesce app_metadata branch (end-user plane) is not matching.', n_a_total;
  END IF;

  SELECT count(*) INTO n_b_visible
    FROM storage.objects
    WHERE bucket_id = 'ft'
      AND name LIKE 'tenant/' || '22222222-2222-2222-2222-222222222222' || '/%';
  IF n_b_visible <> 0 THEN
    RAISE EXCEPTION 'APPMETA-ISOLATION FAIL: B ft objects visible via A app_metadata claim (got %)', n_b_visible;
  END IF;

  BEGIN
    INSERT INTO storage.objects (bucket_id, name, owner)
      VALUES ('ft', pg_temp._seed_name('22222222-2222-2222-2222-222222222222', 'appmeta-A-writes-into-B.bin'), NULL);
  EXCEPTION
    WHEN insufficient_privilege THEN
      insert_blocked := true;
  END;
  IF NOT insert_blocked THEN
    RAISE EXCEPTION
      'APPMETA-INSERT FAIL: bound to A via app_metadata, an INSERT under tenant/<B>/ was '
      'NOT rejected by WITH CHECK (cross-tenant FT write leak on the end-user plane).';
  END IF;

  RESET ROLE;
  RAISE NOTICE 'app_metadata (end-user) plane OK: see=2, B-visible=0, B-prefix insert blocked -- coalesce branch 2 isolates.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 4. Pooled-connection leak check (spec A.5 -- the load-bearing one).          --
--    A FRESH transaction on the SAME session with NO set_config must see 0      --
--    objects. The prior claims were set with is_local := true, so they did NOT  --
--    survive into this transaction. If a claim had leaked (is_local := false    --
--    -- the bug), `authenticated` would still see a tenant's objects here.      --
--                                                                              --
--    We ROLLBACK the seed transaction first so this runs as a genuinely        --
--    separate transaction on the same psql session/connection -- the "next     --
--    borrower" shape. We then re-seed ONE object that WOULD be visible IF a     --
--    claim had leaked, and prove the claim is empty and 0 objects are visible.  --
-- --------------------------------------------------------------------------- --
ROLLBACK;  -- end the seed transaction; nothing it wrote persists (read-only proof).

-- Re-seed minimally in a NEW transaction so there is at least one object that WOULD
-- be visible IF a claim had leaked. Then, in yet another fresh transaction with no
-- set_config, prove the claim is empty and 0 objects are visible.
BEGIN;
SET LOCAL ROLE service_role;
INSERT INTO storage.objects (bucket_id, name, owner)
  VALUES ('ft', 'tenant/' || '11111111-1111-1111-1111-111111111111' || '/leakprobe/leak-probe-A.bin', NULL);
RESET ROLE;
COMMIT;   -- this object persists across the txn boundary so the next txn could see it.

DO $$
DECLARE
  leaked_claim text;
  n_visible    integer;
BEGIN
  -- Fresh transaction (this DO block), SAME session/connection, NO set_config.
  leaked_claim := current_setting('request.jwt.claims', true);  -- true => no error if unset
  IF leaked_claim IS NOT NULL AND leaked_claim <> '' THEN
    RAISE EXCEPTION
      'A.5 LEAK FAIL: request.jwt.claims survived into a new transaction (= %). '
      'is_local must be true so the claim is transaction-scoped.', leaked_claim;
  END IF;

  SET LOCAL ROLE authenticated;
  SELECT count(*) INTO n_visible
    FROM storage.objects
    WHERE bucket_id = 'ft' AND name LIKE 'tenant/%';
  RESET ROLE;
  IF n_visible <> 0 THEN
    RAISE EXCEPTION
      'A.5 LEAK FAIL: a new transaction with NO claim sees % ft objects -- a prior '
      'tenant claim leaked to the next borrower of the pooled connection.', n_visible;
  END IF;
  RAISE NOTICE 'A.5 pooled-conn leak check OK: no inherited claim, 0 ft objects visible without a bind.';
END
$$;

-- Clean up the leak-probe object so the test leaves storage.objects as it found it.
DO $$
BEGIN
  SET LOCAL ROLE service_role;
  DELETE FROM storage.objects
    WHERE bucket_id = 'ft'
      AND name = 'tenant/' || '11111111-1111-1111-1111-111111111111' || '/leakprobe/leak-probe-A.bin';
  RESET ROLE;
END
$$;

-- Final banner. Reaching here means every RAISE EXCEPTION above was avoided.
DO $$
BEGIN
  RAISE NOTICE 'RLS STORAGE-OBJECTS DENIAL GATE: ALL ASSERTIONS PASSED.';
END
$$;
