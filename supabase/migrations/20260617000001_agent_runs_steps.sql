-- 20260617000001_agent_runs_steps.sql
-- Multi-tenant AGENT-RUN ledger: agent_runs (one row per multi-step agent run) +
-- agent_steps (one row per plan/act/observe/tool step) + a SINGLE PERMISSIVE
-- tenant-match RLS boundary on EACH table.
-- ADR adr_agents_sdk_dashboard (Phase C / L2 RUNTIME -- OQ6: "agent_runs/agent_steps
-- schema modeled on agent_grounding_record; founder applies"). The THIRD + FOURTH
-- tenant surfaces, REPLICATING the proven tenant_data (20260616000002) +
-- tenant_runtime (20260616000003) template byte-for-byte.
-- Built by N03; PREPARE-ONLY -- NOT applied (no `supabase db push`) in this task.
-- THE FOUNDER APPLIES THIS MIGRATION (mirrors the W2/W3 data-plane gating).
--
-- WHY THIS SHAPE (RESTRICTIVE-only -> PERMISSIVE tenant-match, carried verbatim):
--   PostgreSQL RLS shows a row iff (>=1 PERMISSIVE passes) AND (every RESTRICTIVE
--   passes). A RESTRICTIVE-only boundary with NO permissive grant denies every row
--   (the produtos 0-rows trap; correction logic validated 2026-06-16, live RLS
--   denial proven on STAGING 2026-06-20, W3, as authenticated, cross-tenant denied).
--   The boundary here is
--   therefore ONE PERMISSIVE `tenant_boundary` policy that GRANTS and FILTERS, +
--   a service_role escape scoped TO service_role. This is a byte-pattern replica of
--   tenant_data / tenant_runtime -- NOT a new boundary design.
--
-- OPERATIONALIZES: N03_engineering/P08_architecture/p08_adr_multitenant_data_plane.md
--   D2 -- tenant_id uuid not null + mandatory index is the canonical tenant key.
--   D3 -- the tenant boundary is a SINGLE PERMISSIVE tenant-match policy (grants AND
--         filters); writes carry WITH CHECK; the service_role escape is a separate
--         PERMISSIVE policy scoped TO service_role ONLY.
--   adr_agents_sdk_dashboard D5 -- agent transcript/step persistence is "more tables
--         through the SAME audited adapter"; agent_grounding_record (P10) is the step
--         schema seed (tool calls + content + tool_io per step).
--
-- ANTI-RULES SATISFIED (spec B.3 -- the produtos bypass, encoded as forbidden):
--   AR1 -- NO SECOND permissive USING(true) policy on role public/authenticated; the
--          ONLY USING(true) policy is service_role_all, scoped TO service_role.
--   AR2 -- the boundary IS a permissive tenant-match policy (NOT RESTRICTIVE-only).
--   AR3 -- every write path (the FOR ALL boundary policy) carries WITH CHECK.
--   AR4 -- ENABLE ROW LEVEL SECURITY + FORCE ROW LEVEL SECURITY are both present.
--   AR5 -- no blanket auth.role()='authenticated' read; the boundary matches
--          tenant_id against the JWT claim per-row, never role-only.
--
-- The boundary expression is the SAME COALESCE that serves BOTH identity planes from
-- ONE policy: the AGENT plane sets a TOP-LEVEL tenant_id via set_config
-- (request.jwt.claims ->> 'tenant_id'); the END-USER Supabase Auth JWT carries
-- tenant_id NESTED under app_metadata (request.jwt.claims -> 'app_metadata' ->>
-- 'tenant_id'). coalesce(top-level, app_metadata) matches EITHER. Correction logic
-- validated 2026-06-16; live RLS denial proven on STAGING 2026-06-20 (W3, as
-- authenticated, cross-tenant denied). The agent runtime's write path binds the TOP-LEVEL claim via the
-- audited adapter (cex_runtime_sync), so branch 1 is the live agent path.
--
-- IDEMPOTENT GUARDS: CREATE TABLE IF NOT EXISTS + CREATE INDEX IF NOT EXISTS +
-- per-policy DROP POLICY IF EXISTS before CREATE POLICY, so re-applying the file is
-- safe (the tenant_data/tenant_runtime templates rely on first-apply only; this file
-- adds the DROP guards so a founder re-run never errors on an existing policy).

-- ============================================================================
-- SURFACE 1: agent_runs  (one row per multi-step agent run -- the run header)
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_runs (
  id          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id   uuid        NOT NULL,                       -- D2 canonical key
  agent_id    text        NOT NULL,
  status      text        NOT NULL DEFAULT 'running',     -- running|completed|failed|refused|budget_exceeded
  inputs      jsonb       NOT NULL DEFAULT '{}'::jsonb,    -- the typed run inputs (no secret)
  result      jsonb       NOT NULL DEFAULT '{}'::jsonb,    -- final artifact ref + score + gate
  cost        jsonb       NOT NULL DEFAULT '{}'::jsonb,    -- steps/tokens spent vs the budget
  started_at  timestamptz NOT NULL DEFAULT now(),
  ended_at    timestamptz                                  -- NULL until terminal
);
CREATE INDEX IF NOT EXISTS idx_agent_runs_tenant ON agent_runs(tenant_id);   -- D2 MANDATORY

ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs FORCE ROW LEVEL SECURITY;

-- THE tenant-boundary policy -- a SINGLE PERMISSIVE tenant-match (ADR D3). Byte
-- replica of tenant_data.tenant_boundary: PERMISSIVE => it is the GRANT (a permissive
-- policy must exist or RLS denies every row) AND the FILTER. FOR ALL covers SELECT +
-- write paths. The anti-bypass is the rule that NO second permissive USING(true)
-- policy is granted to public/authenticated (AR1), NOT a RESTRICTIVE wrapper. ONE
-- expression serves BOTH planes via COALESCE (agent top-level claim; end-user
-- app_metadata claim).
DROP POLICY IF EXISTS tenant_boundary ON agent_runs;
CREATE POLICY tenant_boundary ON agent_runs
  AS PERMISSIVE
  FOR ALL                                  -- SELECT + INSERT/UPDATE/DELETE
  TO authenticated
  USING (
    (tenant_id)::text = coalesce(
      nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
      nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
    )
  )
  WITH CHECK (                             -- D3: writes MUST carry WITH CHECK
    (tenant_id)::text = coalesce(
      nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
      nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
    )
  );

-- The service_role escape, SCOPED `TO service_role` ONLY (ADR D3). service_role
-- bypasses RLS by Postgres default; this policy is the EXPLICIT, audited grant so the
-- privilege is visible in pg_policies, NOT an implicit superuser hole on role public.
DROP POLICY IF EXISTS service_role_all ON agent_runs;
CREATE POLICY service_role_all ON agent_runs
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- SURFACE 2: agent_steps  (one row per plan/act/observe/tool step -- the ledger)
-- ============================================================================
-- Modeled on agent_grounding_record (P10): each step records its kind, content, and
-- (for tool steps) the tool name + tool_io (the call args + result). run_id FKs the
-- header so a run's transcript is one indexed scan. tenant_id is DENORMALIZED onto the
-- step (NOT only via the run) so the SAME single-PERMISSIVE tenant-match boundary
-- applies DIRECTLY to agent_steps -- a step row is tenant-isolated by its OWN
-- tenant_id, never only transitively through agent_runs (defence-in-depth: an
-- attacker who somehow names a foreign run_id still cannot read/write a row whose
-- tenant_id != their claim).
CREATE TABLE IF NOT EXISTS agent_steps (
  id          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  run_id      uuid        NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
  tenant_id   uuid        NOT NULL,                       -- D2 canonical key (denormalized)
  step_index  integer     NOT NULL,                       -- 0-based order within the run
  kind        text        NOT NULL,                       -- plan|act|observe|tool
  content     jsonb       NOT NULL DEFAULT '{}'::jsonb,    -- the step payload (reasoning / output)
  tool        text,                                        -- the tool name (tool steps only)
  tool_io     jsonb       NOT NULL DEFAULT '{}'::jsonb,    -- {args, result} for tool steps
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_agent_steps_tenant ON agent_steps(tenant_id);   -- D2 MANDATORY
CREATE INDEX IF NOT EXISTS idx_agent_steps_run ON agent_steps(run_id);          -- run transcript scan

ALTER TABLE agent_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_steps FORCE ROW LEVEL SECURITY;

-- THE tenant-boundary policy -- a SINGLE PERMISSIVE tenant-match (ADR D3). IDENTICAL
-- shape to agent_runs (and tenant_data / tenant_runtime): the boundary matches the
-- step's OWN tenant_id against the JWT claim, so step isolation does NOT depend on a
-- join to agent_runs. AR1-AR5 satisfied symmetrically.
DROP POLICY IF EXISTS tenant_boundary ON agent_steps;
CREATE POLICY tenant_boundary ON agent_steps
  AS PERMISSIVE
  FOR ALL
  TO authenticated
  USING (
    (tenant_id)::text = coalesce(
      nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
      nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
    )
  )
  WITH CHECK (
    (tenant_id)::text = coalesce(
      nullif(current_setting('request.jwt.claims', true), '')::json ->> 'tenant_id',
      nullif(current_setting('request.jwt.claims', true), '')::json -> 'app_metadata' ->> 'tenant_id'
    )
  );

DROP POLICY IF EXISTS service_role_all ON agent_steps;
CREATE POLICY service_role_all ON agent_steps
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
