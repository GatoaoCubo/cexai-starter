-- down_20260617000001_agent_runs_steps.sql
-- ROLLBACK (down-migration) for 20260617000001_agent_runs_steps.sql.
-- Reverses the agent-run ledger: the agent_steps + agent_runs tables, their
-- indexes, and the four RLS policies (tenant_boundary + service_role_all on each).
-- Idempotent (every statement is IF EXISTS).
--
-- ############################################################################
-- ##  BLAST RADIUS -- SHARED SCHEMA. READ BEFORE RUNNING.                    ##
-- ##                                                                          ##
-- ##  CENTRALIZED shared-schema multi-tenant DB: `agent_runs` + `agent_steps` ##
-- ##  hold the run headers + step transcripts of EVERY tenant, isolated only  ##
-- ##  by the tenant_id RLS boundary. DROPPING them destroys the agent-run     ##
-- ##  audit ledger of ALL TENANTS AT ONCE -- no per-tenant DROP. Blast radius ##
-- ##  = the whole data plane.                                                 ##
-- ##                                                                          ##
-- ##  DATA LOSS IS PERMANENT unless a backup exists FIRST (Supabase PITR /    ##
-- ##  daily backup, or a manual pg_dump, or per-tenant exports). See          ##
-- ##  _docs/compiled/runbook_backup_restore_rollback.md.                      ##
-- ############################################################################
--
-- NOT APPLIED in this task. PREPARE-ONLY -- authored structurally, NOT run against
-- any live DB. The founder / on-call applies it, and ONLY after a verified backup.
--
-- DEPENDENCY ORDER (reverse of the forward migration). The forward file created
-- agent_runs FIRST, then agent_steps with a FOREIGN KEY:
--     run_id uuid NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE
-- so agent_steps DEPENDS ON agent_runs. The rollback therefore drops the CHILD
-- (agent_steps) BEFORE the PARENT (agent_runs). Dropping agent_steps first means
-- the agent_runs DROP has no inbound FK to block it (no CASCADE needed on the
-- parent). Within each table: policies -> indexes -> table.

-- ==========================================================================
-- A. agent_steps FIRST (the child -- has the FK to agent_runs).
-- ==========================================================================
DROP POLICY IF EXISTS service_role_all ON agent_steps;
DROP POLICY IF EXISTS tenant_boundary ON agent_steps;
DROP INDEX IF EXISTS idx_agent_steps_run;
DROP INDEX IF EXISTS idx_agent_steps_tenant;
-- DESTRUCTIVE: removes ALL tenants' step transcripts. RESTRICT (no CASCADE) -- an
-- unexpected dependent ERRORS LOUDLY; investigate before forcing.
DROP TABLE IF EXISTS agent_steps;

-- ==========================================================================
-- B. agent_runs SECOND (the parent -- safe now that the child table is gone).
-- ==========================================================================
DROP POLICY IF EXISTS service_role_all ON agent_runs;
DROP POLICY IF EXISTS tenant_boundary ON agent_runs;
DROP INDEX IF EXISTS idx_agent_runs_tenant;
-- DESTRUCTIVE: removes ALL tenants' run headers. RESTRICT (no CASCADE). If
-- agent_steps was somehow NOT dropped above (e.g. you edited this file), the FK
-- would make this ERROR -- which is the correct fail-loud behavior. Drop the child
-- first, never CASCADE the parent blindly.
DROP TABLE IF EXISTS agent_runs;
