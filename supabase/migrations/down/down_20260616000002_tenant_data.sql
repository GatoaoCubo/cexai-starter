-- down_20260616000002_tenant_data.sql
-- ROLLBACK (down-migration) for 20260616000002_tenant_data.sql.
-- Reverses the `data` tenant surface: the tenant_data table, its tenant index, and
-- the two RLS policies. Idempotent (every statement is IF EXISTS).
--
-- ############################################################################
-- ##  BLAST RADIUS -- SHARED SCHEMA. READ BEFORE RUNNING.                    ##
-- ##                                                                          ##
-- ##  CENTRALIZED shared-schema multi-tenant DB: ONE `tenant_data` table      ##
-- ##  holds the business rows of EVERY tenant, isolated only by the           ##
-- ##  tenant_id RLS boundary. DROPPING it destroys the data of ALL TENANTS    ##
-- ##  AT ONCE -- there is no per-tenant DROP. Blast radius = the whole plane. ##
-- ##                                                                          ##
-- ##  DATA LOSS IS PERMANENT unless a backup exists FIRST (Supabase PITR /    ##
-- ##  daily backup, or a manual pg_dump, or per-tenant exports). See          ##
-- ##  _docs/compiled/runbook_backup_restore_rollback.md.                      ##
-- ############################################################################
--
-- NOT APPLIED in this task. PREPARE-ONLY -- authored structurally, NOT run against
-- any live DB. The founder / on-call applies it, and ONLY after a verified backup.
--
-- IMPORTANT ORDERING CAVEAT -- the `capability` column add-on:
--   The LATER migration 20260618000001_tenant_data_capability_col.sql ALTERs THIS
--   SAME table (ADD COLUMN capability + a partial index). DROP TABLE tenant_data
--   here removes that column and index along with the table, so rolling back this
--   base migration IMPLICITLY rolls back the capability add-on too. If you intend
--   to keep tenant_data and only undo the capability column, run
--   down_20260618000001_tenant_data_capability_col.sql INSTEAD -- do NOT run this
--   file. Run THIS file only to tear down the tenant_data surface entirely.
--   (Forward-migration order is .._00002 then .._00018; reverse order is therefore
--   .._00018 then .._00002 -- undo the column add BEFORE the table drop if you are
--   doing a full staged rollback, though the table DROP makes the column undo moot.)
--
-- DEPENDENCY ORDER (reverse of the forward migration): policies -> index -> table.

-- 1. Policies (reverse of forward steps 2 + 3).
DROP POLICY IF EXISTS service_role_all ON tenant_data;
DROP POLICY IF EXISTS tenant_boundary ON tenant_data;

-- 2. Indexes. The base migration created idx_tenant_data_tenant. The capability
--    add-on created idx_tenant_data_capability -- dropped here too (idempotent) so
--    this file fully reverses the table regardless of whether the add-on ran.
DROP INDEX IF EXISTS idx_tenant_data_capability;
DROP INDEX IF EXISTS idx_tenant_data_tenant;

-- 3. The table (reverse of forward step 1). DESTRUCTIVE -- removes ALL tenants'
--    rows AND the capability column. RESTRICT (no CASCADE) so an unexpected
--    dependent ERRORS LOUDLY instead of silently cascading; investigate before
--    forcing.
DROP TABLE IF EXISTS tenant_data;
