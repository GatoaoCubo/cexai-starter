-- down_20260616000003_tenant_runtime.sql
-- ROLLBACK (down-migration) for 20260616000003_tenant_runtime.sql.
-- Reverses the `runtime` tenant surface: the tenant_runtime table, its tenant
-- index, and the two RLS policies. Idempotent (every statement is IF EXISTS).
--
-- ############################################################################
-- ##  BLAST RADIUS -- SHARED SCHEMA. READ BEFORE RUNNING.                    ##
-- ##                                                                          ##
-- ##  CENTRALIZED shared-schema multi-tenant DB: ONE `tenant_runtime` table   ##
-- ##  holds the handoff/signal/decision rows of EVERY tenant, isolated only   ##
-- ##  by the tenant_id RLS boundary. DROPPING it destroys the runtime state   ##
-- ##  of ALL TENANTS AT ONCE -- no per-tenant DROP. Blast radius = the whole  ##
-- ##  data plane.                                                             ##
-- ##                                                                          ##
-- ##  DATA LOSS IS PERMANENT unless a backup exists FIRST (Supabase PITR /    ##
-- ##  daily backup, or a manual pg_dump, or per-tenant exports). See          ##
-- ##  _docs/compiled/runbook_backup_restore_rollback.md.                      ##
-- ############################################################################
--
-- NOT APPLIED in this task. PREPARE-ONLY -- authored structurally, NOT run against
-- any live DB. The founder / on-call applies it, and ONLY after a verified backup.
--
-- DEPENDENCY ORDER (reverse of the forward migration): policies -> index -> table.

-- 1. Policies (reverse of forward steps 2 + 3).
DROP POLICY IF EXISTS service_role_all ON tenant_runtime;
DROP POLICY IF EXISTS tenant_boundary ON tenant_runtime;

-- 2. Index (reverse of forward index creation). DROP TABLE below also removes it;
--    explicit + idempotent for self-documentation.
DROP INDEX IF EXISTS idx_tenant_runtime_tenant;

-- 3. The table (reverse of forward step 1). DESTRUCTIVE -- removes ALL tenants'
--    runtime rows. RESTRICT (no CASCADE) so an unexpected dependent ERRORS LOUDLY;
--    investigate before forcing.
DROP TABLE IF EXISTS tenant_runtime;
