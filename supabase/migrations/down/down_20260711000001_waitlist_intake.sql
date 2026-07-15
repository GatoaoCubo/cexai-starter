-- down_20260711000001_waitlist_intake.sql
-- ROLLBACK (down-migration) for 20260711000001_waitlist_intake.sql.
-- Reverses the waitlist_intake lead-capture surface: the table, its two
-- indexes, and its two RLS policies. Idempotent (every statement is IF EXISTS).
--
-- ############################################################################
-- ##  BLAST RADIUS -- LEAD QUEUE. READ BEFORE RUNNING.                       ##
-- ##                                                                          ##
-- ##  DROPPING waitlist_intake destroys EVERY waitlist signup collected so    ##
-- ##  far -- e-mails + best-effort brand answers of every visitor who joined  ##
-- ##  the queue from /intake. There is no re-derivation: once gone, those     ##
-- ##  leads are gone.                                                         ##
-- ##                                                                          ##
-- ##  DATA LOSS IS PERMANENT unless a backup exists FIRST (Supabase PITR /    ##
-- ##  daily backup, or a manual pg_dump). Back it up before any rollback. See  ##
-- ##  _docs/compiled/runbook_backup_restore_rollback.md.                      ##
-- ############################################################################
--
-- NOT APPLIED in this task. PREPARE-ONLY -- authored structurally, NOT run
-- against any live DB. The founder / on-call applies it, and ONLY after a
-- verified backup.
--
-- DEPENDENCY ORDER (reverse of the forward migration): policies -> indexes -> table.

-- 1. Policies (reverse of forward steps 2 + 3).
DROP POLICY IF EXISTS service_role_all ON waitlist_intake;
DROP POLICY IF EXISTS anon_insert_only ON waitlist_intake;

-- 2. Indexes (reverse of forward index creation). DROP TABLE below also
--    removes them; explicit + idempotent for self-documentation.
DROP INDEX IF EXISTS idx_waitlist_intake_created_at;
DROP INDEX IF EXISTS idx_waitlist_intake_wtp_band;

-- 3. The table (reverse of forward step 1). DESTRUCTIVE -- removes every
--    collected waitlist signup (unrecoverable). RESTRICT (no CASCADE) so an
--    unexpected dependent ERRORS LOUDLY; investigate before forcing.
DROP TABLE IF EXISTS waitlist_intake;
