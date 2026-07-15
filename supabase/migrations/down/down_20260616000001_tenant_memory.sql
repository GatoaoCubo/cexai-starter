-- down_20260616000001_tenant_memory.sql
-- ROLLBACK (down-migration) for 20260616000001_tenant_memory.sql.
-- Reverses the `memory` tenant surface: the tenant_memory table, its two indexes,
-- and the two RLS policies. Idempotent (every statement is IF EXISTS).
--
-- ############################################################################
-- ##  BLAST RADIUS -- SHARED SCHEMA. READ BEFORE RUNNING.                    ##
-- ##                                                                          ##
-- ##  This is a CENTRALIZED, SHARED-SCHEMA multi-tenant database: one         ##
-- ##  `tenant_memory` table holds the rows of EVERY tenant, isolated only by  ##
-- ##  the tenant_id RLS boundary. DROPPING this table destroys the memory     ##
-- ##  rows of ALL TENANTS AT ONCE, not one tenant. There is NO per-tenant     ##
-- ##  granularity in a DROP -- the blast radius is the entire data plane.     ##
-- ##                                                                          ##
-- ##  DATA LOSS IS PERMANENT unless a backup was taken FIRST. Postgres DROP   ##
-- ##  TABLE is not recoverable from within the database. Before running this  ##
-- ##  file you MUST have either (a) a Supabase PITR window / automated daily  ##
-- ##  backup covering now, or (b) a manual logical dump (pg_dump) of          ##
-- ##  tenant_memory, or (c) per-tenant exports. See the runbook:              ##
-- ##  _docs/compiled/runbook_backup_restore_rollback.md.                      ##
-- ############################################################################
--
-- NOT APPLIED in this task. PREPARE-ONLY. This file was authored structurally and
-- was NOT run against any live database. The founder / on-call applies it (mirrors
-- the forward-migration gating), and ONLY after a verified backup.
--
-- DEPENDENCY ORDER (reverse of the forward migration):
--   1. DROP the two POLICIES first (they depend on the table). Dropping the table
--      would drop its policies implicitly, but dropping policies explicitly first
--      keeps the rollback readable and lets you stop after step 1 if you only want
--      to strip RLS without losing data (NOT recommended -- that exposes rows).
--   2. DROP the two INDEXES (they depend on the table; DROP TABLE drops them too,
--      but explicit DROP INDEX IF EXISTS is harmless and self-documenting).
--   3. DROP the TABLE last.
--
-- THE `vector` EXTENSION IS DELIBERATELY NOT DROPPED.
--   The forward migration ran `CREATE EXTENSION IF NOT EXISTS vector`. We do NOT
--   `DROP EXTENSION vector` here: the extension is SHARED infrastructure -- other
--   tables / migrations (and the prod brain's existing pgvector columns, e.g.
--   kc_embeddings) may depend on it, and DROP EXTENSION vector CASCADE would
--   silently drop every vector column and index in the database. Leaving the
--   extension installed is harmless (an unused extension costs nothing) and is the
--   safe default. If you have CONFIRMED nothing else uses pgvector and you want a
--   truly pristine teardown, drop it MANUALLY and deliberately, out of band:
--     -- DROP EXTENSION IF EXISTS vector;   -- DO NOT uncomment without auditing deps.

-- 1. Policies (reverse of forward steps 2 + 3).
DROP POLICY IF EXISTS service_role_all ON tenant_memory;
DROP POLICY IF EXISTS tenant_boundary ON tenant_memory;

-- 2. Indexes (reverse of forward index creation). Explicit + idempotent; DROP TABLE
--    below also removes them, but this documents the full reversal.
DROP INDEX IF EXISTS idx_tenant_memory_vec;
DROP INDEX IF EXISTS idx_tenant_memory_tenant;

-- 3. The table (reverse of forward step 1). This is the DESTRUCTIVE statement --
--    it removes ALL tenants' memory rows. RESTRICT (the default, i.e. no CASCADE)
--    so that if anything unexpectedly depends on this table the DROP ERRORS LOUDLY
--    instead of silently cascading. If the error names a real dependent you did
--    not expect, STOP and investigate before forcing it.
DROP TABLE IF EXISTS tenant_memory;

-- NOTE: `vector` extension intentionally left installed (see header). No DROP EXTENSION.
