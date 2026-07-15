-- down_20260619000001_marketplace_observation.sql
-- ROLLBACK (down-migration) for 20260619000001_marketplace_observation.sql.
-- Reverses the marketplace_observation time-series surface: the table, its two
-- indexes (tenant + series), and the two RLS policies. Idempotent (every statement
-- is IF EXISTS).
--
-- ############################################################################
-- ##  BLAST RADIUS -- SHARED SCHEMA. READ BEFORE RUNNING.                    ##
-- ##                                                                          ##
-- ##  CENTRALIZED shared-schema multi-tenant DB: ONE                          ##
-- ##  `marketplace_observation` table holds the longitudinal capture rows of  ##
-- ##  EVERY tenant, isolated only by the tenant_id RLS boundary. DROPPING it  ##
-- ##  destroys the ENTIRE price/sales/BSR history of ALL TENANTS AT ONCE --   ##
-- ##  no per-tenant DROP. This is the time-series moat (Keepa/Nubimetrics      ##
-- ##  analog): velocity, price-history + seasonality are computed AT READ      ##
-- ##  from these rows, so once the rows are gone the history is              ##
-- ##  UNRECOVERABLE -- it cannot be re-derived, only re-collected over time.  ##
-- ##                                                                          ##
-- ##  DATA LOSS IS PERMANENT unless a backup exists FIRST (Supabase PITR /    ##
-- ##  daily backup, or a manual pg_dump, or per-tenant exports). This surface ##
-- ##  is the MOST EXPENSIVE to lose -- back it up before any rollback. See    ##
-- ##  _docs/compiled/runbook_backup_restore_rollback.md.                      ##
-- ############################################################################
--
-- NOT APPLIED in this task. PREPARE-ONLY -- authored structurally, NOT run against
-- any live DB. The founder / on-call applies it, and ONLY after a verified backup.
--
-- DEPENDENCY ORDER (reverse of the forward migration): policies -> indexes -> table.

-- 1. Policies (reverse of forward steps 2 + 3).
DROP POLICY IF EXISTS service_role_all ON marketplace_observation;
DROP POLICY IF EXISTS tenant_boundary ON marketplace_observation;

-- 2. Indexes (reverse of forward index creation). DROP TABLE below also removes
--    them; explicit + idempotent for self-documentation.
DROP INDEX IF EXISTS idx_mktobs_series;
DROP INDEX IF EXISTS idx_mktobs_tenant;

-- 3. The table (reverse of forward step 1). DESTRUCTIVE -- removes ALL tenants'
--    marketplace history rows (unrecoverable; re-collect-only). RESTRICT (no
--    CASCADE) so an unexpected dependent ERRORS LOUDLY; investigate before forcing.
DROP TABLE IF EXISTS marketplace_observation;
