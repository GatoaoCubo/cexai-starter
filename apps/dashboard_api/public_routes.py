# -*- coding: ascii -*-
"""UNAUTHENTICATED public-site endpoints (spec 10 W1-backend): the L2 public catalog.

These two routes have NO JWT -- they are browsed anonymously by the public site. They
are SECURITY-CRITICAL: they MUST be structurally incapable of returning an unpublished,
private, or cross-tenant row. They achieve that with defence-in-depth (the no-leak
triple-guard), implemented in the public_reader seam:

  (1) the read runs as the low-privilege `anon` Postgres role (SET LOCAL ROLE anon), so
      the migration's public_catalog_read / public_slug_read RLS policies (TO anon,
      USING published/public_read = true) constrain every SELECT to published / opted-in
      rows ONLY. The public path NEVER uses service_role (which BYPASSES RLS);
  (2) the backend SQL ALSO filters `published = true AND kind = $kind` -- belt on top of
      RLS;
  (3) a client supplies a SLUG, NEVER a raw tenant_id. The slug resolves to a tenant_id
      ONLY via tenant_slugs WHERE public_read = true; a private/unknown slug 404s WITHOUT
      disclosing whether the tenant exists.

CONTRAST WITH THE AUTHENTICATED ROUTES (apps/dashboard_api/main.py): those derive the
tenant from the verified JWT (auth.extract_tenant_id) and read tenant-claim-bound via the
audited SupabaseDataAdapter. This router does NEITHER -- it has no auth dependency and uses
the claim-free anon public reader (deps.make_public_reader). The two never share a path.

ENDPOINTS:
  * GET /public/tenant-info?slug=<slug>
      -> {tenant_id, slug, brand: {name, tagline, logo, tokens}, published_at}
      resolve slug->tenant_id (public_read gated); 404 on unknown/non-public slug.
  * GET /public/catalog?slug=<slug>&kind=<kind>&limit=&offset=
      -> {tenant_id, slug, kind, items: [...], limit, offset}
      published-only rows of `kind` for the slug's tenant; 404 on unknown/non-public slug.

DEGRADE-NEVER: no public data plane configured -> tenant-info 404s (resolve -> None) and
catalog 404s (resolve -> None); a configured plane with no published rows -> an empty
items list. NEVER 500s on a missing plane; NEVER discloses a non-public tenant.

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from . import deps

__all__ = ["router", "build_public_router"]


def _not_found(reason: str, detail: str) -> JSONResponse:
    """A 404 that NEVER discloses whether a non-public tenant exists. The same envelope
    every other failure uses ({"error": {type, reason, detail}}) so a client's single
    error path handles it. Used for an unknown slug, a non-public slug, AND a degraded
    (no data plane) resolve -- all indistinguishable to the caller (no-leak)."""
    return JSONResponse(
        status_code=404,
        content={"error": {"type": "public_not_found", "reason": reason, "detail": detail}},
    )


def build_public_router() -> APIRouter:
    """Build the unauthenticated public-site router (factory so tests get a fresh one)."""
    router = APIRouter(prefix="/public", tags=["public"])

    @router.get("/tenant-info")
    async def get_tenant_info(
        slug: str = Query(..., min_length=1, description="the public tenant slug"),
    ) -> JSONResponse:
        """GET /public/tenant-info?slug=<slug> -> the tenant's PUBLIC brand. Unauthenticated.

        Flow (the no-leak triple-guard, layer 3 first):
          1. resolve slug->tenant_id via the anon reader (tenant_slugs WHERE public_read =
             true). An unknown / non-public slug -> 404 WITHOUT disclosing the tenant exists
             (the same 404 a missing data plane yields).
          2. serialize the tenant's PUBLIC brand (name/tagline/logo + 24 design tokens) via
             deps.resolve_public_brand -- value-free, never a secret, never fabricated.
        Returns {tenant_id, slug, brand, published_at}. The tenant_id is the slug-resolved
        one (never a client value). NEVER 500s on a missing plane."""
        reader = deps.make_public_reader()
        resolved = reader.resolve_public_tenant(slug)
        if resolved is None:
            # Unknown / non-public slug OR no data plane -- indistinguishable to the client.
            return _not_found("unknown_slug", "no public tenant for this slug")
        tenant_id = resolved["tenant_id"]
        brand = deps.resolve_public_brand(tenant_id)
        return JSONResponse(
            status_code=200,
            content={
                "tenant_id": tenant_id,
                "slug": resolved.get("slug", slug),
                "brand": brand,
                # published_at is a per-row concept (a row's go-live time), not a tenant
                # one; the tenant-info shell carries it as null here (the catalog rows carry
                # their own published_at). Kept in the contract for the public site's shell.
                "published_at": None,
            },
        )

    @router.get("/catalog")
    async def get_catalog(
        slug: str = Query(..., min_length=1, description="the public tenant slug"),
        kind: str = Query(..., min_length=1, description="the tenant_data kind to list"),
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
    ) -> JSONResponse:
        """GET /public/catalog?slug=&kind=&limit=&offset= -> published rows of `kind`.
        Unauthenticated.

        Flow (the no-leak triple-guard):
          (3) resolve slug->tenant_id (public_read gated). An unknown/non-public slug ->
              404 WITHOUT disclosing the tenant.
          (1) the read runs as anon so public_catalog_read (USING published = true)
              constrains it;
          (2) the SQL ALSO filters published = true AND kind = <kind> (belt). A private
              kind that is not published is NEVER returned.
        Returns {tenant_id, slug, kind, items, limit, offset}. Each item carries the
        published payload (+ human_html when present). The tenant_id is the slug-resolved
        one; a public read can ONLY ever see THIS tenant's published rows of THIS kind.
        NEVER 500s on a missing plane (an unknown slug 404s; a known slug with no rows ->
        an empty items list)."""
        reader = deps.make_public_reader()
        tenant_id, items = reader.read_public_catalog(
            slug, kind, limit=limit, offset=offset, with_html=True
        )
        if tenant_id is None:
            # Unknown / non-public slug OR no data plane -- indistinguishable to the client.
            return _not_found("unknown_slug", "no public tenant for this slug")
        return JSONResponse(
            status_code=200,
            content={
                "tenant_id": tenant_id,
                "slug": slug,
                "kind": kind,
                "items": items,
                "limit": limit,
                "offset": offset,
            },
        )

    return router


# The module-level router main.py wires in (a fresh build so import order is irrelevant).
router = build_public_router()
