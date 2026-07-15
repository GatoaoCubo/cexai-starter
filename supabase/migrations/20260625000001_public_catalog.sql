-- 20260625000001_public_catalog.sql
-- Spec 10 (Multi-Tenant to 100%) Wave 1 -- the L2 PUBLIC SITE published-gate.
-- Built by N03/N05 (spec docs/specs/10_multitenant_100/spec.md, W1-backend); the
-- public-catalog schema half of W1: a published flag + an anon-readable RLS policy +
-- a slug->tenant_id lookup table so an UNAUTHENTICATED public site can serve
-- published-only, RLS-safe rows for a tenant resolved by SLUG.
--
-- ============================================================================
-- THIS IS A FILE ONLY -- APPLYING IT IS GATED (FOUNDER).
--   This migration is NOT applied here (no `supabase db push`, no live DB call). The
--   FOUNDER applies it against the live/staging Supabase. Like every other migration
--   in this dir (see 20260616000002_tenant_data.sql, 20260618000001_*) it is
--   PREPARE-ONLY: authored, reviewed, and tested offline (FakeDbSession), but the
--   prod apply is a deliberate, gated human step (spec 10 GATED list).
-- ============================================================================
--
-- WHY (the L2 gap this closes):
--   The dashboard backend serves tenant_data ONLY behind a verified JWT (every read
--   is tenant-claim-bound via SupabaseDataAdapter + the tenant_boundary RLS policy
--   from 20260616000002). A PUBLIC storefront/catalog has NO JWT -- it is browsed
--   anonymously. So an unauthenticated reader must be STRUCTURALLY incapable of
--   seeing anything but PUBLISHED rows of a tenant that has OPTED its slug in. This
--   migration adds exactly that, with defence-in-depth so a backend bug alone can
--   never leak a private/unpublished/cross-tenant row.
--
-- THE DEFENCE-IN-DEPTH MODEL (all three layers; the keystone):
--   (1) RLS at the DB: a PERMISSIVE SELECT policy `public_catalog_read` granted ONLY
--       TO the `anon` role, USING (published = true). The public backend connects as
--       `anon` (SET LOCAL ROLE anon), so even a SELECT * the anon role issues returns
--       published rows ONLY. anon NEVER bypasses RLS (only the table owner /
--       service_role do, and the public path NEVER uses those).
--   (2) Backend filter (in apps/dashboard_api/public_routes.py): the SQL ALSO carries
--       `published = true AND kind = $kind` -- belt-and-braces on top of RLS.
--   (3) slug->tenant_id gating: a public reader supplies a SLUG, never a raw
--       tenant_id. The slug resolves to a tenant_id ONLY via tenant_slugs WHERE
--       public_read = true. A tenant that has not opted in is INVISIBLE (the lookup
--       returns nothing -> the endpoint 404s WITHOUT disclosing existence).
--
-- RLS POSTURE -- WHY anon AND NOT service_role (the load-bearing choice):
--   service_role BYPASSES RLS by Postgres default. If the public path read as
--   service_role, the `public_catalog_read` policy would NEVER apply and an
--   unpublished row could leak through a single missing backend filter. So the
--   public path connects as `anon` (a low-privilege Supabase role that is SUBJECT to
--   RLS), and this file GRANTS anon the precise, published-only SELECT it needs --
--   nothing more (no INSERT/UPDATE/DELETE for anon; writes stay service_role-only).
--
-- ANTI-RULES (mirrors 20260616000002's AR set; the produtos-bypass lessons):
--   AR1 -- anon gets NO `USING (true)` policy: its ONLY grant is the published-gated
--          SELECT. There is no anon write policy at all.
--   AR2 -- the anon policy is PERMISSIVE (a grant) with a NON-trivial USING
--          (published = true), never a blanket allow.
--   AR3 -- tenant_slugs writes are service_role-only (a single PERMISSIVE FOR ALL
--          policy TO service_role); anon SELECT is gated by public_read = true.
--   AR4 -- ENABLE + FORCE ROW LEVEL SECURITY on tenant_slugs (the table owner is
--          subject to RLS too).
--   AR5 -- the existing tenant_boundary policy on tenant_data (TO authenticated) is
--          left UNTOUCHED: authenticated reads stay tenant-scoped exactly as before;
--          this file only ADDS the anon published-read lane.

-- ============================================================================
-- PART A: tenant_data -- the published gate (publish flag + anon published-read RLS)
-- ============================================================================

-- A.1 The publish flag. ADDITIVE + IDEMPOTENT (safe to re-run; no existing row is
--     touched). DEFAULT false => every existing row is UNPUBLISHED until a tenant
--     explicitly publishes it (fail-closed: nothing is public by default). published_at
--     records WHEN a row went public (nullable; set by the publish action, W1-frontend).
ALTER TABLE tenant_data ADD COLUMN IF NOT EXISTS published boolean NOT NULL DEFAULT false;
ALTER TABLE tenant_data ADD COLUMN IF NOT EXISTS published_at timestamptz;

-- A.2 A PARTIAL index for the public read filter: only published rows are indexed
--     (the false-default backfill rows never bloat it), matching the
--     (tenant_id, published) lookup the public catalog read uses.
CREATE INDEX IF NOT EXISTS idx_tenant_data_published
  ON tenant_data(tenant_id, published)
  WHERE published = true;

-- A.3 THE anon published-read policy (defence-in-depth layer 1).
--     PERMISSIVE SELECT, granted ONLY TO `anon` (the unauthenticated Supabase role),
--     USING (published = true). So an anon connection sees published rows ONLY -- a
--     SELECT it issues can NEVER return an unpublished row, regardless of the backend
--     SQL. This does NOT touch the tenant_boundary policy (TO authenticated): an
--     authenticated session is governed by tenant_boundary as before; an anon session
--     is governed by THIS policy. There is no anon write policy (AR1) -- anon can read
--     published rows and nothing else.
DROP POLICY IF EXISTS public_catalog_read ON tenant_data;
CREATE POLICY public_catalog_read ON tenant_data
  AS PERMISSIVE
  FOR SELECT
  TO anon
  USING (published = true);

-- ============================================================================
-- PART B: tenant_slugs -- the slug->tenant_id public-read lookup (defence layer 3)
-- ============================================================================
-- A public reader NEVER supplies a tenant_id; it supplies a SLUG. The slug resolves
-- to a tenant_id ONLY through this table, and ONLY when public_read = true. A tenant
-- with no row here (or public_read = false) is INVISIBLE to the public path -- its
-- existence is never disclosed (the endpoint 404s on an unknown/non-public slug).
CREATE TABLE IF NOT EXISTS tenant_slugs (
  id          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id   uuid        NOT NULL UNIQUE,            -- one slug row per tenant
  slug        text        NOT NULL UNIQUE,            -- the public URL slug (e.g. sample-tenant)
  public_read boolean     NOT NULL DEFAULT false,     -- fail-closed: opted-out by default
  created_at  timestamptz NOT NULL DEFAULT now()
);
-- A partial index for the public slug lookup: only public-read slugs are indexed
-- (the slug column is already UNIQUE; this narrows the public resolve to opted-in rows).
CREATE INDEX IF NOT EXISTS idx_tenant_slugs_public
  ON tenant_slugs(slug)
  WHERE public_read = true;

-- B.1 Enable RLS (and FORCE so even the table owner is subject to it -- AR4).
ALTER TABLE tenant_slugs ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_slugs FORCE ROW LEVEL SECURITY;

-- B.2 The anon public-read policy: anon may SELECT a slug row ONLY WHERE
--     public_read = true. So the public resolve sees opted-in slugs ONLY; a private
--     (public_read = false) or absent slug returns no row -> the endpoint 404s WITHOUT
--     disclosing the tenant exists. anon gets NO write policy (AR1/AR3).
DROP POLICY IF EXISTS public_slug_read ON tenant_slugs;
CREATE POLICY public_slug_read ON tenant_slugs
  AS PERMISSIVE
  FOR SELECT
  TO anon
  USING (public_read = true);

-- B.3 The service_role escape, SCOPED `TO service_role` ONLY (the audited admin grant).
--     Slug rows are MANAGED (created / opted in/out) by the backend under service_role
--     (e.g. cex_prod_activate / a publish action), NEVER by anon. This explicit policy
--     makes the privilege visible in pg_policies (not an implicit superuser hole on
--     role public). FOR ALL covers the management read + write paths.
DROP POLICY IF EXISTS service_role_all ON tenant_slugs;
CREATE POLICY service_role_all ON tenant_slugs
  AS PERMISSIVE
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
