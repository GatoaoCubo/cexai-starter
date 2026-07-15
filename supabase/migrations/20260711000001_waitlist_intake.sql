-- 20260711000001_waitlist_intake.sql
-- Mission GO_ONLINE (spec cexai-specs/23_go_online/spec.md), User Story P1b +
-- FR-003, tasks T200/T210. The "modo-espera" (waitlist mode) capture surface:
-- every /intake public submission while the tenant is in waitlist mode lands
-- ONE row here -- anon INSERT-only, ZERO anon SELECT (LGPD by design: a
-- visitor can join the queue but can never read it back, and can never see who
-- else is on it).
--
-- ============================================================================
-- THIS IS A FILE ONLY -- APPLYING IT IS GATED (FOUNDER).
--   This migration is NOT applied here (no `supabase db push`, no live DB call).
--   The FOUNDER applies it against the live/staging Supabase. Like every other
--   migration in this dir (20260616000002_tenant_data.sql, 20260625000001_
--   public_catalog.sql, ...) it is PREPARE-ONLY: authored + tested offline
--   (throwaway-schema pytest, see cexai/tests/governance/data/
--   test_rls_waitlist_denial.py), but the prod apply is a deliberate, gated
--   human step.
-- ============================================================================
--
-- WHY (the gap this closes):
--   /intake (apps/public_site/app/intake/page.tsx) is a PURE CLIENT with no
--   server-side secrets (next.config.mjs). Before this table existed, the ONLY
--   persistence path for a waitlist visitor was the client-side answers-YAML
--   download -- nothing landed anywhere the founder could see without the
--   visitor mailing the file back. This migration gives the browser exactly
--   ONE privileged action (INSERT a queue row) while keeping every READ behind
--   service_role, so the founder's dashboard (once its backend reader is
--   BUILT -- see the PROPOSAL comment on ApiClient.listWaitlist(),
--   apps/dashboard_web/lib/api.ts) is the only surface that can ever list the
--   queue.
--
-- RLS POSTURE -- anon INSERT-only, NO anon SELECT (the load-bearing choice):
--   A public lead-capture form has no auth and no tenant claim -- the ONLY
--   identity is "anonymous visitor". Unlike public_catalog.sql (anon reads
--   PUBLISHED rows), this surface never lets anon read ANYTHING back: LGPD-by-
--   design, a visitor's e-mail is personal data and other visitors' rows must
--   never be enumerable from the browser. The single anon grant is a
--   PERMISSIVE INSERT WITH CHECK (true) -- there is no SELECT/UPDATE/DELETE
--   policy for anon of ANY shape, so even a client bug that tried to SELECT
--   would return zero rows (RLS default-denies any action with no matching
--   PERMISSIVE policy). See supabase/tests/rls_waitlist_intake_denial.sql for
--   the executable proof.
--
-- ANTI-RULES SATISFIED:
--   AR1 -- anon gets NO SELECT policy of any shape (not even a narrow one) --
--          STRONGER than public_catalog's published-only anon SELECT.
--   AR2 -- the anon policy is PERMISSIVE (a grant), scoped to INSERT only.
--   AR3 -- the service_role escape is a single PERMISSIVE FOR ALL policy,
--          scoped TO service_role ONLY (byte-shape from
--          marketplace_observation.sql / public_catalog.sql's tenant_slugs
--          service_role_all).
--   AR4 -- ENABLE + FORCE ROW LEVEL SECURITY (the table owner is subject to
--          RLS too).
--   AR5 -- no tenant_id column: this table is deliberately NOT tenant-scoped
--          (pre-launch, effectively one tenant on this dashboard -- DECISIONS,
--          GO_ONLINE A2 handoff) -- tenant_boundary does not apply here,
--          matching marketplace_observation.sql's own precedent for a
--          no-tenant-id table.

-- ============================================================================
-- SURFACE: waitlist_intake (anon-writable, service_role-readable lead queue)
-- ============================================================================
CREATE TABLE IF NOT EXISTS waitlist_intake (
  id          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  email       text        NOT NULL CHECK (length(btrim(email)) > 0),
  wtp_band    text,                                     -- audience.wtp_band, dashboard sort key (T212)
  brand_name  text,                                     -- identity.brand_name, best-effort display
  answers     jsonb       NOT NULL DEFAULT '{}'::jsonb,  -- full buildAnswers(state) snapshot (best-effort)
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- The dashboard queue view sorts by wtp_band (T212 -- "founder sees the queue
-- sortable by wtp_band"); created_at is the natural freshness order. Both
-- indexed for that read path (service_role only -- see the RLS posture above).
CREATE INDEX IF NOT EXISTS idx_waitlist_intake_wtp_band ON waitlist_intake(wtp_band);
CREATE INDEX IF NOT EXISTS idx_waitlist_intake_created_at ON waitlist_intake(created_at);

-- 1. Enable RLS (and FORCE so even the table owner is subject to it -- AR4).
ALTER TABLE waitlist_intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist_intake FORCE ROW LEVEL SECURITY;

-- 2. THE anon INSERT-only policy (the ONLY anon grant on this table -- AR1/AR2).
--    PERMISSIVE INSERT WITH CHECK (true): any anonymous visitor may ADD a row;
--    there is no anon SELECT/UPDATE/DELETE policy of any shape, so RLS's
--    default deny covers all three (a permissive policy must exist for an
--    action to be allowed at all -- proven in rls_waitlist_intake_denial.sql).
DROP POLICY IF EXISTS anon_insert_only ON waitlist_intake;
CREATE POLICY anon_insert_only ON waitlist_intake
  AS PERMISSIVE
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- 3. The service_role escape, SCOPED `TO service_role` ONLY (byte-shape from
--    marketplace_observation.sql / public_catalog.sql's tenant_slugs
--    service_role_all). This is the ONLY role that can ever read the queue --
--    the founder's dashboard reader (PROPOSED, not built this cycle -- see
--    apps/dashboard_web/lib/api.ts's listWaitlist() comment) would connect as
--    service_role, exactly the same SET LOCAL ROLE mechanic
--    apps/dashboard_api/public_reader.py already uses for anon
--    (pg_session_factory.PgSession.set_config).
DROP POLICY IF EXISTS service_role_all ON waitlist_intake;
CREATE POLICY service_role_all ON waitlist_intake
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
