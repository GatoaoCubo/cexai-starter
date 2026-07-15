-- rls_waitlist_intake_denial.sql
-- Mission GO_ONLINE (spec cexai-specs/23_go_online/spec.md), tasks T200/T220 --
-- the SECURITY GATE test for the `waitlist_intake` surface (LGPD-by-design:
-- anon INSERT-only, ZERO anon SELECT). This is the DB-side proof that:
--   (a) an anonymous visitor CAN insert a queue row (the whole point of the
--       /intake "modo-espera" form);
--   (b) an anonymous visitor can NEVER read ANY row back -- not even the one
--       they just inserted (no anon SELECT policy of any shape exists);
--   (c) an anonymous visitor can never UPDATE or DELETE any row;
--   (d) service_role (the only role a founder-side reader would ever use)
--       sees everything.
--
-- MIGRATION UNDER TEST: supabase/migrations/20260711000001_waitlist_intake.sql
--
-- DESIGN NOTE -- every assertion RAISEs on failure, structurally mirroring
-- supabase/tests/rls_tenant_memory_denial.sql. psql with `-v ON_ERROR_STOP=1`
-- (or `--set=ON_ERROR_STOP=1`) turns any RAISE EXCEPTION into a non-zero
-- process exit, so a clean exit code 0 == ALL assertions passed and a
-- non-zero/error exit == FAIL. This file never prints a bare "ok" without
-- having proven it; there is no path that fakes a pass. pgTAP is NOT required
-- (plain DO blocks + RAISE, same as the tenant_memory template).
--
-- SIMPLER THAN THE tenant_memory TEMPLATE, ON PURPOSE: this table has no
-- tenant_id / request.jwt.claims binding at all -- the anon_insert_only policy
-- is `WITH CHECK (true)`, a role-only grant, not a per-row claim match. So
-- there is no pooled-connection claim-leak check here (spec A.5 in the
-- tenant_memory file does not apply -- there is no claim to leak). The
-- role-switch shape (SET LOCAL ROLE ... / RESET ROLE inside a DO block) is
-- copied verbatim from the proven tenant_memory template.
--
-- ============================================================================
-- RUNBOOK (identical 3-tier pattern to rls_tenant_memory_denial.sql)
-- ============================================================================
-- CI (local Postgres via the Supabase CLI -- no live project, no Docker on the
-- author's box but present in CI):
--
--   npx supabase start
--   psql "$(npx supabase status -o env | grep DB_URL | cut -d= -f2-)" \
--        -v ON_ERROR_STOP=1 \
--        -f supabase/migrations/20260711000001_waitlist_intake.sql \
--        -f supabase/tests/rls_waitlist_intake_denial.sql
--   # exit 0 = gate GREEN; any non-zero = gate FAIL (an anon read/write leak).
--
-- The migration is applied FIRST (idempotent: CREATE ... IF NOT EXISTS +
-- CREATE POLICY). This test file assumes `waitlist_intake` + its policies
-- exist on the current search_path; it does NOT re-create them.
--
-- W3-equivalent (staging project):
--   The same two psql -f invocations run against the STAGING Supabase
--   project's pooled connection string (NOT the live brain
--   <supabase-project-ref>). NEVER point this at production data.
--
-- The Python CI runner cexai/tests/governance/data/test_rls_waitlist_denial.py
-- wraps this file: it creates a throwaway schema, applies the migration into
-- it, runs these assertions, drops the schema -- and SKIPS cleanly when no
-- TEST db is reachable (this sandbox today).
-- ============================================================================

-- ASCII-only. All identifiers + literals are 0x00-0x7F.

-- The unique probe marker used throughout (never a real visitor's address --
-- reserved by RFC 2606 .test TLD convention).
-- Probe email: rls-test-probe@example.test

-- --------------------------------------------------------------------------- --
-- PRE-CLEANUP (committed, autocommit -- runs BEFORE the main transaction).     --
-- Neutralizes a stray probe row from any prior aborted run, scoped to our      --
-- unique test marker so no real visitor row is ever touched. On a clean run    --
-- this deletes 0 rows.                                                        --
-- --------------------------------------------------------------------------- --
DO $$
BEGIN
  SET LOCAL ROLE service_role;
  DELETE FROM waitlist_intake WHERE email = 'rls-test-probe@example.test';
  RESET ROLE;
END
$$;

-- Wrap the whole gate in one transaction so a failure leaves no partial seed.
-- ROLLBACK at the very end: this is a read-only PROOF, not a fixture loader --
-- nothing it writes should persist.
BEGIN;

-- --------------------------------------------------------------------------- --
-- 0. Preconditions -- fail loudly if the migration was not applied first.      --
-- --------------------------------------------------------------------------- --
DO $$
BEGIN
  IF to_regclass('waitlist_intake') IS NULL THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL: relation waitlist_intake not found on search_path. '
      'Apply 20260711000001_waitlist_intake.sql BEFORE this test (see RUNBOOK).';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_class
    WHERE oid = 'waitlist_intake'::regclass AND relrowsecurity
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR4): waitlist_intake does not have ROW LEVEL SECURITY '
      'enabled -- rows would be globally readable.';
  END IF;

  -- anon must have a PERMISSIVE INSERT grant (the whole point of the table --
  -- without it the form could never write a waitlist row).
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'waitlist_intake'
      AND cmd = 'INSERT'
      AND permissive = 'PERMISSIVE'
      AND roles @> ARRAY['anon']::name[]
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL: no PERMISSIVE INSERT policy for anon on waitlist_intake -- '
      'the /intake form could never write a waitlist row.';
  END IF;

  -- LGPD-by-design (AR1, STRONGER than public_catalog's published-only anon
  -- SELECT): anon must have NO SELECT policy of ANY shape on this table.
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'waitlist_intake'
      AND cmd = 'SELECT'
      AND roles @> ARRAY['anon']::name[]
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR1): a SELECT policy for anon exists on waitlist_intake -- '
      'the LGPD-by-design contract requires ZERO anon read access.';
  END IF;

  -- The produtos-bypass class -- no PERMISSIVE USING(true) policy granted to
  -- public/authenticated that could accidentally widen access beyond anon
  -- INSERT / service_role ALL.
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = current_schema()
      AND tablename = 'waitlist_intake'
      AND permissive = 'PERMISSIVE'
      AND qual = 'true'
      AND (roles @> ARRAY['public']::name[] OR roles @> ARRAY['authenticated']::name[])
  ) THEN
    RAISE EXCEPTION
      'PRECONDITION FAIL (AR1): a PERMISSIVE USING(true) policy is granted to '
      'public/authenticated on waitlist_intake -- unintended widen of access.';
  END IF;

  RAISE NOTICE 'preconditions OK: waitlist_intake RLS enabled, anon INSERT-only, zero anon SELECT, no public/authenticated USING(true).';
END
$$;

-- --------------------------------------------------------------------------- --
-- 1. anon CAN insert (the whole point of the form). WITH CHECK (true) --      --
--    any shape of row is accepted; the app-side gate (EMAIL_LOOSE_PATTERN) is --
--    the ONLY email-shape enforcement -- the DB does not re-validate it        --
--    beyond the non-empty CHECK constraint on the column itself.               --
--                                                                              --
--    DELIBERATELY NO "RETURNING ... INTO" HERE: Postgres RLS filters a         --
--    RETURNING projection through the caller's SELECT policies (the same       --
--    documented mechanism that makes `INSERT ... RETURNING *` come back EMPTY  --
--    for an anon-INSERT-only Supabase table even though the row really was     --
--    written -- a well-known RLS gotcha). Since anon has ZERO SELECT policy    --
--    here BY DESIGN, RETURNING would give a false negative. GET DIAGNOSTICS    --
--    ROW_COUNT is a write-side count (rows the DML engine actually processed), --
--    NOT a data projection -- it is not subject to SELECT-policy filtering.    --
--    Section 4 below (service_role SELECT) is the DEFINITIVE persistence      --
--    proof; this section proves only that anon's own INSERT did not raise.    --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_inserted integer;
BEGIN
  SET LOCAL ROLE anon;
  INSERT INTO waitlist_intake (email, wtp_band, brand_name, answers)
    VALUES (
      'rls-test-probe@example.test',
      'R$ 29-149',
      'RLS Test Brand',
      '{"probe": true}'::jsonb
    );
  GET DIAGNOSTICS n_inserted = ROW_COUNT;
  RESET ROLE;
  IF n_inserted <> 1 THEN
    RAISE EXCEPTION 'ANON-INSERT FAIL: expected 1 row inserted by anon, got %.', n_inserted;
  END IF;
  RAISE NOTICE 'anon INSERT OK: 1 row inserted (WITH CHECK true accepted it).';
END
$$;

-- --------------------------------------------------------------------------- --
-- 2. anon CANNOT select -- not even the row just inserted (LGPD by design).    --
--    Scoped to our probe email so a shared DB's other rows never affect the    --
--    count either way.                                                        --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_visible integer;
BEGIN
  SET LOCAL ROLE anon;
  SELECT count(*) INTO n_visible
    FROM waitlist_intake
    WHERE email = 'rls-test-probe@example.test';
  RESET ROLE;
  IF n_visible <> 0 THEN
    RAISE EXCEPTION
      'ANON-SELECT FAIL: anon sees % row(s) of its own just-inserted probe -- '
      'zero anon SELECT (LGPD by design) is violated.', n_visible;
  END IF;
  RAISE NOTICE 'anon SELECT OK: 0 rows visible (write-only, cannot read back).';
END
$$;

-- --------------------------------------------------------------------------- --
-- 3. anon CANNOT update or delete any row (no permissive policy for either).   --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_updated integer;
  n_deleted integer;
BEGIN
  SET LOCAL ROLE anon;

  UPDATE waitlist_intake SET brand_name = 'tampered'
    WHERE email = 'rls-test-probe@example.test';
  GET DIAGNOSTICS n_updated = ROW_COUNT;
  IF n_updated <> 0 THEN
    RAISE EXCEPTION 'ANON-UPDATE FAIL: anon UPDATE touched % rows (expected 0).', n_updated;
  END IF;

  DELETE FROM waitlist_intake WHERE email = 'rls-test-probe@example.test';
  GET DIAGNOSTICS n_deleted = ROW_COUNT;
  IF n_deleted <> 0 THEN
    RAISE EXCEPTION 'ANON-DELETE FAIL: anon DELETE removed % rows (expected 0).', n_deleted;
  END IF;

  RESET ROLE;
  RAISE NOTICE 'anon UPDATE/DELETE OK: 0 rows affected by either (write-once, insert-only).';
END
$$;

-- --------------------------------------------------------------------------- --
-- 4. service_role sees + can manage the row (the founder-side read path, once  --
--    a backend reader exists -- see the PROPOSAL comment on                    --
--    ApiClient.listWaitlist(), apps/dashboard_web/lib/api.ts).                 --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE
  n_visible integer;
BEGIN
  SET LOCAL ROLE service_role;
  SELECT count(*) INTO n_visible
    FROM waitlist_intake
    WHERE email = 'rls-test-probe@example.test';
  RESET ROLE;
  IF n_visible <> 1 THEN
    RAISE EXCEPTION
      'SERVICE-ROLE-SELECT FAIL: expected exactly 1 probe row visible to '
      'service_role, got %.', n_visible;
  END IF;
  RAISE NOTICE 'service_role SELECT OK: 1 probe row visible (full read access, as designed).';
END
$$;

-- --------------------------------------------------------------------------- --
-- 5. Cleanup: service_role deletes the probe row (the RLS-exempt writer) so    --
--    the table is left as found even before the outer ROLLBACK. Scoped to the --
--    unique probe email -- can never touch a real visitor's row.              --
-- --------------------------------------------------------------------------- --
DO $$
DECLARE n_probe_deleted integer;
BEGIN
  SET LOCAL ROLE service_role;
  DELETE FROM waitlist_intake WHERE email = 'rls-test-probe@example.test';
  GET DIAGNOSTICS n_probe_deleted = ROW_COUNT;
  RESET ROLE;
  IF n_probe_deleted <> 1 THEN
    RAISE EXCEPTION
      'CLEANUP FAIL: expected to delete exactly 1 probe row, deleted % -- '
      'investigate before re-running on a shared DB.', n_probe_deleted;
  END IF;
  RAISE NOTICE 'cleanup OK: probe row deleted (1 row); table left as found.';
END
$$;

-- Belt-and-braces: this whole gate is read-only by design (PRE-CLEANUP already
-- runs committed/autocommit before the transaction; section 5 above already
-- deletes the probe). ROLLBACK guarantees NOTHING from this transaction
-- persists regardless, so a second run of this file is always idempotent.
ROLLBACK;

-- Final banner. Reaching here means every RAISE EXCEPTION above was avoided.
DO $$
BEGIN
  RAISE NOTICE 'RLS WAITLIST-INTAKE DENIAL GATE: ALL ASSERTIONS PASSED.';
END
$$;
