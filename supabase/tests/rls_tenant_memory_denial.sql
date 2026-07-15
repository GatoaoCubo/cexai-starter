-- rls_tenant_memory_denial.sql
-- Mission MULTITENANT_DATA_PLANE (codename tenant-zero), Wave 2 task T3 -- the
-- SECURITY GATE test for the `memory` surface. This is the DB-side layer of the
-- cross-tenant-denial gate (spec C.1): it proves the PERMISSIVE tenant-match RLS
-- policy (corrected 2026-06-16 -- see B.2 below, NOT a RESTRICTIVE-only set) in
-- 20260616000001_tenant_memory.sql actually denies a tenant-A session any read,
-- insert, update, or delete of tenant-B rows -- AND that a transaction-local
-- claim does NOT leak to the next borrower of a pooled connection (spec A.5).
--
-- SPEC: _docs/compiled/spec_multitenant_data_plane_v1.md
--   C.1  -- the exact GIVEN/WHEN/THEN this file encodes (seed A=3 rows + B=2 rows
--           as service_role; bind A; assert count==3, B-count==0, B-INSERT
--           rejected by WITH CHECK, B-UPDATE/DELETE affect 0 rows; symmetric for
--           B). The DB-side half of the two-layer gate -- the framework-side half
--           (_deny_cross_tenant_equality raises) lives in the cexai unit suite.
--   A.5  -- the pooled-conn leak check: a fresh transaction on the SAME session
--           with NO set_config sees 0 rows (proves is_local := true).
--   B.2  -- the policy under test (the SINGLE PERMISSIVE tenant_boundary policy
--           + service_role_all PERMISSIVE TO service_role). CORRECTED 2026-06-16:
--           the boundary is ONE PERMISSIVE tenant-match policy, NOT two RESTRICTIVE
--           policies -- a RESTRICTIVE-only set with no permissive grant denies every
--           row (the 0-rows trap; see spec "## Correction 2026-06-16"). The count
--           assertions below (own-tenant count==3 / ==2) only pass BECAUSE the
--           boundary is permissive; under the old RESTRICTIVE-only policies they
--           would have FAILED with 0 rows.
--           TWO-PLANE COALESCE (2026-06-16): the boundary USING/WITH CHECK is a
--           coalesce of the TOP-LEVEL claim (request.jwt.claims ->> 'tenant_id',
--           the AGENT set_config plane -- branch 1) and the NESTED app_metadata
--           claim (request.jwt.claims -> 'app_metadata' ->> 'tenant_id', the
--           END-USER Supabase-Auth plane -- branch 2). Sections 2/3 below bind
--           the TOP-LEVEL claim (branch 1, the adapter plane); section 3b proves
--           branch 2 (the end-user app_metadata plane) isolates symmetrically.
--           This does NOT weaken the denial matrix -- it adds the second plane.
--
-- MIGRATION UNDER TEST: supabase/migrations/20260616000001_tenant_memory.sql
--
-- DESIGN NOTE -- every assertion RAISEs on failure. psql with `-v ON_ERROR_STOP=1`
-- (or `--set=ON_ERROR_STOP=1`) turns any RAISE EXCEPTION into a non-zero process
-- exit, so a clean exit code 0 == ALL assertions passed and a non-zero/error exit
-- == FAIL. This file NEVER prints a bare "ok" without having proven it; there is
-- no path that fakes a pass. pgTAP is NOT required (plain DO blocks + RAISE).
--
-- ============================================================================
-- RUNBOOK
-- ============================================================================
-- CI (local Postgres via the Supabase CLI -- no live project, no Docker on the
-- author's box but present in CI):
--
--   npx supabase start                      # boots a local Postgres + roles
--   psql "$(npx supabase status -o env | grep DB_URL | cut -d= -f2-)" \
--        -v ON_ERROR_STOP=1 \
--        -f supabase/migrations/20260616000001_tenant_memory.sql \
--        -f supabase/tests/rls_tenant_memory_denial.sql
--   # exit 0 = gate GREEN; any non-zero = gate FAIL (cross-tenant leak).
--
-- The migration is applied FIRST (idempotent: it is CREATE ... IF NOT EXISTS +
-- CREATE POLICY). This test file assumes `tenant_memory` + its policies exist on
-- the current search_path; it does NOT re-create them. If your harness applies
-- the migration some other way (e.g. `supabase db reset`), just run THIS file
-- against the same database afterward.
--
-- W3 (staging project, spec E.3 live denial proof):
--   The same two psql -f invocations run against the STAGING Supabase project's
--   pooled connection string (NOT the live brain at <prod-ref>). The
--   service_role-scoped seeds + the `authenticated` role binding behave the same
--   on a real pooler; the A.5 leak check is the one that matters most on a real
--   Supavisor transaction-mode connection. Drive it from the W3 acceptance gate
--   (cexai/tests CI runner with SUPABASE_DB_URL pointed at staging) so the founder
--   sees the green denial proof. NEVER point this at production data.
--
-- The Python CI runner cexai/tests/governance/data/test_rls_denial.py wraps this
-- file: it creates a throwaway schema, applies the migration into it, runs these
-- assertions, drops the schema -- and SKIPS cleanly when no TEST db is reachable.
-- ============================================================================

-- ASCII-only. All identifiers + literals are 0x00-0x7F.

-- Canonical fixture tenants (spec C.1).
--   A = 11111111-1111-1111-1111-111111111111  (3 rows)
--   B = 22222222-2222-2222-2222-222222222222  (2 rows)
--
-- SHARED-DB ROBUSTNESS (2026-06-20): every assertion below is SCOPED to the
-- test's OWN tenant UUIDs (A and B). It NEVER asserts a GLOBAL count(*) over
-- tenant_memory, because a shared staging project already holds rows for OTHER
-- real tenants -- a global count would read 12 where a clean CI Postgres
-- reads 5 and fail the precondition even though isolation is intact. The seed
-- total, the own-tenant visibility counts, the cross-tenant invisibility counts,
-- and the pooled-conn leak check all filter by `tenant_id IN (A, B)`. As a
-- result this file runs GREEN on BOTH a clean ephemeral CI Postgres AND a dirty
-- shared staging, and re-running it twice both pass (no row accumulation -- see
-- the cleanup notes in sections 1 and 4).

-- --------------------------------------------------------------------------- --
-- PRE-CLEANUP (COMMITTED, autocommit -- runs BEFORE the main transaction).     --
-- Section 4 COMMITs a leak-probe row; if a PRIOR invocation aborted between    --
-- that COMMIT and its cleanup DELETE, a stray persisted probe row for tenant A --
-- would survive and inflate this run's A counts. Neutralize it up front,       --
-- scoped to our two test tenants only, so NO row from any other tenant is      --
-- touched. On a clean CI Postgres this deletes 0 rows. This statement is its   --
-- OWN autocommitted transaction (no surrounding BEGIN yet), so it persists --   --
-- that is what makes re-running the whole file twice idempotent.               --
-- --------------------------------------------------------------------------- --
DO $$
BEGIN
  SET LOCAL ROLE service_role;
  DELETE FROM tenant_memory
    WHERE tenant_id IN (
      '11111111-1111-1111-1111-111111111111',
      '22222222-2222-2222-2222-222222222222'
    );
  RESET ROLE;
END
$$;

-- Wrap the whole gate in one transaction so a failure leaves no partial seed and
-- the ROLE/claim changes are scoped. ON_ERROR_STOP makes any RAISE abort + exit
-- non-zero. We ROLLBACK at the very end: this is a read-only PROOF, not a fixture
-- loader -- nothing it writes should persist.
BEGIN;

-- --------------------------------------------------------------------------- --
-- 0. Preconditions -- fail loudly if the migration was not applied first.      --
-- --------------------------------------------------------------------------- --
DO $$
BEGIN
  IF to_regclass('tenant_memory') IS NULL THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL: relation tenant_memory not found on search_path. '
      'Apply 20260616000001_tenant_memory.sql BEFORE this test (see RUNBOOK).';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_class
    WHERE oid = 'tenant_memory'::regclass AND relrowsecurity
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR4): tenant_memory does not have ROW LEVEL SECURITY '
      'enabled -- rows would be globally readable.';
  END IF;
  -- The boundary MUST be a SINGLE PERMISSIVE tenant-match policy (spec B.2 / AR2,
  -- corrected 2026-06-16). pg_policies.permissive is the text 'PERMISSIVE' /
  -- 'RESTRICTIVE'. A PERMISSIVE policy is REQUIRED: in PG RLS a row is visible iff
  -- (>=1 PERMISSIVE passes) AND (all RESTRICTIVE pass), so without a permissive
  -- grant for `authenticated` the boundary denies EVERY row -- even the caller's
  -- own tenant (the RESTRICTIVE-only 0-rows trap).
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'tenant_memory'
      AND policyname = 'tenant_boundary'
      AND permissive = 'PERMISSIVE'
      AND roles @> ARRAY['authenticated']::name[]
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR2): the PERMISSIVE tenant_boundary policy for '
      'authenticated is missing -- a RESTRICTIVE-only boundary (no permissive '
      'grant) denies every row, even the caller''s own tenant.';
  END IF;
  -- AR2 (the 0-rows trap, explicit): there must be NO RESTRICTIVE policy for
  -- authenticated WITHOUT an accompanying PERMISSIVE grant. The boundary must be
  -- permissive, not RESTRICTIVE-only.
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'tenant_memory'
      AND permissive = 'RESTRICTIVE'
      AND roles @> ARRAY['authenticated']::name[]
  ) AND NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'tenant_memory'
      AND permissive = 'PERMISSIVE'
      AND roles @> ARRAY['authenticated']::name[]
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR2): tenant_memory has RESTRICTIVE policy(ies) for '
      'authenticated but NO permissive grant -- the 0-rows trap.';
  END IF;
  -- AR1 -- there must be NO permissive USING(true) policy on public/authenticated.
  -- The only USING(true) allowed is service_role_all, scoped TO {service_role}.
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'tenant_memory'
      AND permissive = 'PERMISSIVE'
      AND qual = 'true'
      AND (roles @> ARRAY['public']::name[] OR roles @> ARRAY['authenticated']::name[])
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR1): a PERMISSIVE USING(true) policy is granted to '
      'public/authenticated -- this is the produtos bypass; it OR-nullifies the '
      'tenant boundary.';
  END IF;
  RAISE NOTICE 'preconditions OK: tenant_memory RLS enabled, PERMISSIVE tenant_boundary present, no public USING(true).';
END
$$;

-- --------------------------------------------------------------------------- --
-- 1. Seed as service_role (the explicit B.2 escape, NOT as an RLS-exempt owner --
--    -- spec Open Q7). service_role_all PERMISSIVE TO service_role lets these   --
--    inserts through regardless of any claim.                                  --
-- --------------------------------------------------------------------------- --
SET LOCAL ROLE service_role;

-- DEFENSIVE BASELINE (within this txn's snapshot): clear any A/B rows so the
-- seed counts in sections 2/3/3b reflect EXACTLY the fixtures seeded here, even
-- if real A/B-UUID rows already exist on a shared DB. The committed PRE-CLEANUP
-- above already removed any persisted stray; this repeats it inside the rolled-
-- back seed txn so the in-txn snapshot the assertions read is known-empty first.
-- On a clean CI Postgres this deletes 0 rows.
DELETE FROM tenant_memory
  WHERE tenant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222'
  );

-- Tenant A: 3 rows.
INSERT INTO tenant_memory (tenant_id, namespace, content) VALUES
  ('11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111/', 'A-1'),
  ('11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111/', 'A-2'),
  ('11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111/', 'A-3');

-- Tenant B: 2 rows.
INSERT INTO tenant_memory (tenant_id, namespace, content) VALUES
  ('22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222/', 'B-1'),
  ('22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222/', 'B-2');

RESET ROLE;

-- Sanity: as service_role (bypassing the boundary) the seed total for OUR TWO
-- test tenants is exactly 5. SCOPED to (A, B) -- a shared DB holds other tenants'
-- rows that service_role can also see, so a global count(*) would over-count.
DO $$
DECLARE n integer;
BEGIN
  SET LOCAL ROLE service_role;
  SELECT count(*) INTO n
    FROM tenant_memory
    WHERE tenant_id IN (
      '11111111-1111-1111-1111-111111111111',
      '22222222-2222-2222-2222-222222222222'
    );
  RESET ROLE;
  IF n <> 5 THEN
    RAISE EXCEPTION
      'SEED FAIL: expected 5 seeded rows for test tenants (A,B) as service_role, got %. '
      '(If >5 on a shared DB, a prior run left rows behind -- this test ROLLBACKs its '
      'seed so that should not happen; investigate stray A/B rows.)', n;
  END IF;
  RAISE NOTICE 'seed OK: 5 rows (A=3, B=2) for test tenants visible to service_role.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 2. Bind tenant A and assert the full denial matrix (spec C.1, A side).       --
--    set_config(..., is_local := true) mirrors the adapter's bind_session_tenant --
--    -- transaction-scoped. SET LOCAL ROLE authenticated makes the PERMISSIVE   --
--    tenant_boundary policy apply (service_role would bypass it).               --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_total      integer;
  n_b_visible  integer;
  n_updated    integer;
  n_deleted    integer;
  insert_blocked boolean := false;
BEGIN
  PERFORM set_config(
    'request.jwt.claims',
    json_build_object('tenant_id', '11111111-1111-1111-1111-111111111111')::text,
    true   -- is_local => scoped to THIS transaction (pooled-conn safe, spec A.5)
  );
  SET LOCAL ROLE authenticated;

  -- THEN: A's 3 seeded rows are visible. SCOPED to A's UUID so a shared DB that
  -- already holds A-tenant rows (or any visible-via-claim rows) cannot change the
  -- count -- we assert exactly the rows THIS test seeded for A. (The boundary
  -- already filters to A's claim; this WHERE pins it to the seeded fixture.)
  SELECT count(*) INTO n_total
    FROM tenant_memory
    WHERE tenant_id = '11111111-1111-1111-1111-111111111111';
  IF n_total <> 3 THEN
    RAISE EXCEPTION 'A-SELECT FAIL: bound to A, expected 3 visible A rows, got %', n_total;
  END IF;

  -- THEN: B is invisible (0 rows match the B filter under A's claim).
  SELECT count(*) INTO n_b_visible
    FROM tenant_memory
    WHERE tenant_id = '22222222-2222-2222-2222-222222222222';
  IF n_b_visible <> 0 THEN
    RAISE EXCEPTION 'A-ISOLATION FAIL: B rows visible while bound to A (got %)', n_b_visible;
  END IF;

  -- THEN: inserting a B-tagged row is REJECTED by WITH CHECK (AR3). The policy
  -- violation raises SQLSTATE 42501 (insufficient_privilege) -- catch ONLY that,
  -- so an unrelated error still fails the gate.
  BEGIN
    INSERT INTO tenant_memory (tenant_id, namespace, content)
      VALUES ('22222222-2222-2222-2222-222222222222', 'x/', 'A-writes-into-B');
  EXCEPTION
    WHEN insufficient_privilege THEN
      insert_blocked := true;
  END;
  IF NOT insert_blocked THEN
    RAISE EXCEPTION
      'A-INSERT FAIL: bound to A, an INSERT of a B-tagged row was NOT rejected '
      'by WITH CHECK (cross-tenant write leak).';
  END IF;

  -- THEN: UPDATE of B rows affects 0 rows (they are not visible to the USING clause).
  UPDATE tenant_memory SET content = 'tampered'
    WHERE tenant_id = '22222222-2222-2222-2222-222222222222';
  GET DIAGNOSTICS n_updated = ROW_COUNT;
  IF n_updated <> 0 THEN
    RAISE EXCEPTION 'A-UPDATE FAIL: bound to A, UPDATE of B rows touched % rows', n_updated;
  END IF;

  -- THEN: DELETE of B rows affects 0 rows.
  DELETE FROM tenant_memory
    WHERE tenant_id = '22222222-2222-2222-2222-222222222222';
  GET DIAGNOSTICS n_deleted = ROW_COUNT;
  IF n_deleted <> 0 THEN
    RAISE EXCEPTION 'A-DELETE FAIL: bound to A, DELETE of B rows removed % rows', n_deleted;
  END IF;

  RESET ROLE;
  RAISE NOTICE 'A-bound denial matrix OK: see=3, B-visible=0, B-insert blocked, B-update=0, B-delete=0.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 3. Symmetric: bind tenant B and assert the mirror matrix (spec C.1, B side). --
--    B has 2 rows; A (3 rows) must be invisible / unwritable.                  --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_total      integer;
  n_a_visible  integer;
  n_updated    integer;
  n_deleted    integer;
  insert_blocked boolean := false;
BEGIN
  PERFORM set_config(
    'request.jwt.claims',
    json_build_object('tenant_id', '22222222-2222-2222-2222-222222222222')::text,
    true
  );
  SET LOCAL ROLE authenticated;

  -- THEN: B's 2 seeded rows are visible. SCOPED to B's UUID (shared-DB safe).
  SELECT count(*) INTO n_total
    FROM tenant_memory
    WHERE tenant_id = '22222222-2222-2222-2222-222222222222';
  IF n_total <> 2 THEN
    RAISE EXCEPTION 'B-SELECT FAIL: bound to B, expected 2 visible B rows, got %', n_total;
  END IF;

  SELECT count(*) INTO n_a_visible
    FROM tenant_memory
    WHERE tenant_id = '11111111-1111-1111-1111-111111111111';
  IF n_a_visible <> 0 THEN
    RAISE EXCEPTION 'B-ISOLATION FAIL: A rows visible while bound to B (got %)', n_a_visible;
  END IF;

  BEGIN
    INSERT INTO tenant_memory (tenant_id, namespace, content)
      VALUES ('11111111-1111-1111-1111-111111111111', 'x/', 'B-writes-into-A');
  EXCEPTION
    WHEN insufficient_privilege THEN
      insert_blocked := true;
  END;
  IF NOT insert_blocked THEN
    RAISE EXCEPTION
      'B-INSERT FAIL: bound to B, an INSERT of an A-tagged row was NOT rejected '
      'by WITH CHECK (cross-tenant write leak).';
  END IF;

  UPDATE tenant_memory SET content = 'tampered'
    WHERE tenant_id = '11111111-1111-1111-1111-111111111111';
  GET DIAGNOSTICS n_updated = ROW_COUNT;
  IF n_updated <> 0 THEN
    RAISE EXCEPTION 'B-UPDATE FAIL: bound to B, UPDATE of A rows touched % rows', n_updated;
  END IF;

  DELETE FROM tenant_memory
    WHERE tenant_id = '11111111-1111-1111-1111-111111111111';
  GET DIAGNOSTICS n_deleted = ROW_COUNT;
  IF n_deleted <> 0 THEN
    RAISE EXCEPTION 'B-DELETE FAIL: bound to B, DELETE of A rows removed % rows', n_deleted;
  END IF;

  RESET ROLE;
  RAISE NOTICE 'B-bound denial matrix OK: see=2, A-visible=0, A-insert blocked, A-update=0, A-delete=0.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 3b. END-USER PLANE (coalesce branch 2): bind tenant A via the NESTED         --
--     app_metadata claim instead of the top-level one. A Supabase Auth JWT     --
--     carries tenant_id under app_metadata, NOT at the top level. The boundary --
--     coalesce(top-level, app_metadata) must therefore isolate identically     --
--     when ONLY app_metadata.tenant_id is present (top-level absent). This is   --
--     the end-user plane the adapter does NOT drive (the adapter sets a         --
--     top-level claim -- branch 1); it proves the SAME single policy serves     --
--     BOTH planes. Strengthens the gate; weakens nothing.                       --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_total      integer;
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
    true   -- is_local => transaction-scoped (pooled-conn safe, spec A.5)
  );
  SET LOCAL ROLE authenticated;

  -- THEN: A's 3 seeded rows are visible via the app_metadata branch. SCOPED to
  -- A's UUID (shared-DB safe) so only the rows THIS test seeded are counted.
  SELECT count(*) INTO n_total
    FROM tenant_memory
    WHERE tenant_id = '11111111-1111-1111-1111-111111111111';
  IF n_total <> 3 THEN
    RAISE EXCEPTION
      'APPMETA-SELECT FAIL: bound to A via app_metadata, expected 3 visible A rows, got %. '
      'The coalesce app_metadata branch (end-user plane) is not matching.', n_total;
  END IF;

  -- THEN: B is invisible under A's app_metadata claim.
  SELECT count(*) INTO n_b_visible
    FROM tenant_memory
    WHERE tenant_id = '22222222-2222-2222-2222-222222222222';
  IF n_b_visible <> 0 THEN
    RAISE EXCEPTION 'APPMETA-ISOLATION FAIL: B rows visible via A app_metadata claim (got %)', n_b_visible;
  END IF;

  -- THEN: inserting a B-tagged row is REJECTED by WITH CHECK via the same branch.
  BEGIN
    INSERT INTO tenant_memory (tenant_id, namespace, content)
      VALUES ('22222222-2222-2222-2222-222222222222', 'x/', 'appmeta-A-writes-into-B');
  EXCEPTION
    WHEN insufficient_privilege THEN
      insert_blocked := true;
  END;
  IF NOT insert_blocked THEN
    RAISE EXCEPTION
      'APPMETA-INSERT FAIL: bound to A via app_metadata, an INSERT of a B-tagged row '
      'was NOT rejected by WITH CHECK (cross-tenant write leak on the end-user plane).';
  END IF;

  RESET ROLE;
  RAISE NOTICE 'app_metadata (end-user) plane OK: see=3, B-visible=0, B-insert blocked -- coalesce branch 2 isolates.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 4. Pooled-connection leak check (spec A.5 -- the load-bearing one).          --
--    A FRESH transaction on the SAME session with NO set_config must see 0 of  --
--    OUR test rows. The prior claims were set with is_local := true, so they   --
--    did NOT survive into this transaction. If a claim had leaked (is_local := --
--    false -- the bug), `authenticated` would still see tenant A's probe row   --
--    here. Seeing 0 proves the claim did not leak to the next borrower.        --
--                                                                              --
--    SHARED-DB NOTE: the visibility count is SCOPED to our test tenants (A,B). --
--    On a clean CI Postgres a no-claim authenticated connection sees 0 rows    --
--    globally; on a shared staging it also sees 0 (no permissive grant matches --
--    without a claim) -- but we assert the SCOPED count so the proof is about  --
--    OUR committed probe row, never coupled to other tenants' data.            --
--                                                                              --
--    NOTE: we ROLLBACK the seed transaction first so this runs as a genuinely  --
--    separate transaction on the same psql session/connection -- exactly the   --
--    "next borrower" shape. We COMMIT one uniquely-marked probe row (tenant A, --
--    namespace 'leakprobe-A/') so there is a row that WOULD be visible IF a    --
--    claim had leaked, then prove the claim is empty AND that probe is unseen, --
--    then DELETE the probe (scoped to A + its unique namespace) so nothing     --
--    accumulates on a shared DB. Re-running the whole file twice both pass.    --
-- --------------------------------------------------------------------------- --
ROLLBACK;  -- end the seed transaction; nothing it wrote persists (read-only proof).

-- Re-seed minimally in a NEW transaction so there is at least one row that WOULD
-- be visible IF a claim had leaked. Then, in yet another fresh transaction with
-- no set_config, prove the claim is empty and 0 of our test rows are visible.
-- The probe uses a UNIQUE namespace ('leakprobe-A/') so the final cleanup DELETE
-- can target exactly this row and never a real row on a shared DB.
BEGIN;
SET LOCAL ROLE service_role;
INSERT INTO tenant_memory (tenant_id, namespace, content)
  VALUES ('11111111-1111-1111-1111-111111111111', 'leakprobe-A/', 'leak-probe-A');
RESET ROLE;
COMMIT;   -- this row persists across the txn boundary so the next txn could see it.

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
  -- SCOPED to our test tenants: a no-claim connection must see 0 of A's/B's rows
  -- (the committed probe is tenant A). A global count would be shared-DB-fragile;
  -- this asserts the exact thing A.5 protects -- no inherited claim reveals OUR row.
  SELECT count(*) INTO n_visible
    FROM tenant_memory
    WHERE tenant_id IN (
      '11111111-1111-1111-1111-111111111111',
      '22222222-2222-2222-2222-222222222222'
    );
  RESET ROLE;
  IF n_visible <> 0 THEN
    RAISE EXCEPTION
      'A.5 LEAK FAIL: a new transaction with NO claim sees % test-tenant rows -- a '
      'prior tenant claim leaked to the next borrower of the pooled connection.', n_visible;
  END IF;
  RAISE NOTICE 'A.5 pooled-conn leak check OK: no inherited claim, 0 test-tenant rows visible without a bind.';
END
$$;

-- --------------------------------------------------------------------------- --
-- 4b. EMPTY-CLAIM graceful-deny check (the nullif fix, 2026-06-20).            --
--     A no-claim borrower's GUC is usually UNSET (NULL) -- covered by section  --
--     4. But on some connection / no-claim paths the GUC is the EMPTY STRING   --
--     '' rather than NULL (a fresh unset claim is NULL; a cleared one can be    --
--     ''). Under the OLD boundary expression ''::json RAISES                    --
--     'invalid input syntax for type json' -- so the SELECT below would have    --
--     ERRORED (aborting this gate with ON_ERROR_STOP) instead of denying        --
--     gracefully. The fix wraps the claim read in                              --
--     nullif(current_setting('request.jwt.claims', true), '') so '' (and       --
--     unset) coalesce to NULL -> the tenant match is NULL -> the row is denied  --
--     (the borrower sees 0 rows), never an error. This block sets the claim to  --
--     EXACTLY '' and proves the committed leakprobe-A row stays invisible,      --
--     locking in the nullif behavior. SCOPED to the test tenants (A,B);         --
--     RAISE-on-failure like every other assertion. Runs BEFORE the probe        --
--     cleanup below so the probe row still exists to be (not) seen.            --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_visible integer;
BEGIN
  -- Bind the EMPTY-STRING claim explicitly (the '' path, not unset/NULL).
  -- is_local => transaction-scoped (pooled-conn safe, spec A.5).
  PERFORM set_config('request.jwt.claims', '', true);
  SET LOCAL ROLE authenticated;

  -- Under the OLD policy this SELECT would RAISE 22P02 (invalid json) because
  -- ''::json is illegal; the nullif wrap turns '' into NULL so the boundary
  -- denies gracefully and this returns 0 (NOT an error). SCOPED to A,B so a
  -- shared DB cannot change the count.
  SELECT count(*) INTO n_visible
    FROM tenant_memory
    WHERE tenant_id IN (
      '11111111-1111-1111-1111-111111111111',
      '22222222-2222-2222-2222-222222222222'
    );
  RESET ROLE;
  IF n_visible <> 0 THEN
    RAISE EXCEPTION
      'EMPTY-CLAIM FAIL: an empty-string ('''') claim borrower sees % test-tenant '
      'rows -- the nullif graceful-deny is not in effect (the boundary must treat '
      '''''/unset as NULL and deny).', n_visible;
  END IF;
  RAISE NOTICE 'empty-claim graceful-deny OK: '''' claim -> 0 test-tenant rows (no json error -- nullif fix).';
END
$$;

-- Clean up the leak-probe row so the test leaves the table as it found it. SCOPED
-- to tenant A + the unique probe namespace so it can NEVER delete a real row on a
-- shared DB. This is what keeps the file idempotent: after this, the COMMITted
-- probe is gone and a second run starts clean.
DO $$
DECLARE n_probe_deleted integer;
BEGIN
  SET LOCAL ROLE service_role;
  DELETE FROM tenant_memory
    WHERE tenant_id = '11111111-1111-1111-1111-111111111111'
      AND namespace = 'leakprobe-A/';
  GET DIAGNOSTICS n_probe_deleted = ROW_COUNT;
  RESET ROLE;
  IF n_probe_deleted <> 1 THEN
    RAISE EXCEPTION
      'CLEANUP FAIL: expected to delete exactly 1 leak-probe row (tenant A, '
      'namespace leakprobe-A/), deleted % -- the probe may have leaked or '
      'accumulated; investigate before re-running on a shared DB.', n_probe_deleted;
  END IF;
  RAISE NOTICE 'cleanup OK: leak-probe row deleted (1 row); table left as found.';
END
$$;

-- Final banner. Reaching here means every RAISE EXCEPTION above was avoided.
DO $$
BEGIN
  RAISE NOTICE 'RLS TENANT-MEMORY DENIAL GATE: ALL ASSERTIONS PASSED.';
END
$$;
