# -*- coding: ascii -*-
"""CEXAI employee dashboard backend (mission CEXAI_PRODUCT_RUNTIME, Phase 1, T3).

A thin FastAPI service over the headless runtime (``_tools/cex_run_capability.py``) and
the capability catalog (``_tools/cex_capability_registry.py``). Implements section B of
spec_cexai_product_build_v1 (the dashboard<->backend contract).

ENDPOINTS:
  * GET  /capabilities            -> the tenant's ENABLED capability cards (organic,
                                     overlay-derived; from the registry).
  * POST /capability/run          -> verify the Supabase JWT, extract tenant_id from the
                                     VERIFIED claim, build a server-side Credential, call
                                     run_capability(tenant_id, capability, intent, cred),
                                     return the CapabilityResult as JSON.
  * GET  /results?capability=     -> the tenant's recent artifacts from THEIR Supabase,
                                     tenant-scoped via the adapter under the user JWT.
  * GET  /healthz                 -> liveness (no auth; never touches the runtime).

THE #1 SECURITY RULE (spec B.3 INVARIANTS): tenant_id is resolved ONLY from the verified
JWT (``auth.extract_tenant_id``). A client may NOT set tenant_id; a body-supplied
tenant_id is IGNORED. Auth is FAIL-CLOSED: no/invalid token -> 401, no fallback identity.
The Credential is assembled SERVER-SIDE only (the browser never sends one).

CORS: configured for the Next.js frontend on localhost (override via
``CEXAI_DASHBOARD_CORS_ORIGINS``, a comma-separated list).

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. The runtime and
registry are imported LAZILY (deps.py) so the app starts even while they are mid-build.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List, Mapping, Optional

from fastapi import Body, FastAPI, File, Header, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from . import agent_runs as agent_runs_mod
from . import agents_config as agents_config_mod
from . import crews_config as crews_config_mod
from . import deps
from . import entities as entities_mod
from . import entities_config as entities_config_mod
from . import public_routes as public_routes_mod
from . import ratelimit
from . import summary as summary_mod
from .auth import (
    AuthError,
    bearer_token_from_header,
    extract_tenant_id,
    verify_supabase_jwt,
)

__all__ = ["app", "create_app"]

# Default CORS origins for a local Next.js dev server (override via env).
_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)
_ENV_CORS_ORIGINS = "CEXAI_DASHBOARD_CORS_ORIGINS"

# Max recent results returned by /results (defence against accidental large scans).
_DEFAULT_RESULTS_LIMIT = 50
_MAX_RESULTS_LIMIT = 200


# --------------------------------------------------------------------------- #
# Request models (note: NO tenant_id field anywhere -- it comes ONLY from the JWT).
# --------------------------------------------------------------------------- #
class RunRequest(BaseModel):
    """Body for POST /capability/run. Deliberately has NO tenant_id field -- the tenant is
    resolved from the verified JWT, never from the client. ``options`` is an optional,
    free-form passthrough (e.g. a render hint); it MUST NOT carry a tenant or a credential
    (the server overwrites enabled_capabilities + supplies the credential itself).

    ``inputs`` (mission BRANDBOOK, Cell A) is the OPTIONAL typed form payload per a
    capability's input_contract -- the rich any-media seam: a field of type file (an upload
    arriving as a data: URI), url, or text alongside the existing scalars. The runtime
    RESOLVES it (image -> palette, doc/url -> text) and hands it to a structured generator;
    ``intent`` stays the free-text fallback. Omit it and the run is byte-identical to before
    (degrade-never). It MUST NOT carry a tenant or a credential (the server strips them)."""

    capability: str = Field(..., min_length=1, description="capability id, e.g. 'research'")
    intent: str = Field(..., min_length=1, description="the user's request for this run")
    inputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="optional typed form payload per the capability's input_contract "
        "(file/url/text + scalars); intent stays the free-text fallback",
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None, description="optional non-secret run hints (no tenant/credential)"
    )


class PatchCapabilityRequest(BaseModel):
    """Body for PATCH /capabilities/{slug} (mission DASHBOARD_COMPOSITION W2). The slug is
    the path segment; the only body field is the action. There is NO tenant_id field -- the
    tenant is the verified JWT claim, never the client. An action other than attach|detach is
    rejected with a structured 400 by the handler (not a pydantic 422), so the error envelope is
    the SAME ``{"error": {type, reason, detail}}`` shape every other failure uses."""

    action: str = Field(..., min_length=1, description="attach | detach")


class PublishRequest(BaseModel):
    """Body for PATCH /entity/{slug}/{record_id}/publish (spec 10 W1 -- the L2 publish seam).

    The ONLY body field is ``published`` (the gate to flip). There is NO tenant_id field -- the
    tenant is the VERIFIED JWT claim, never the client (the #1 security rule). The path carries
    the slug + record id; the body carries only the desired published state. Setting
    ``published=true`` makes the row eligible for the anon public read (L2); ``false`` retracts it.
    """

    published: bool = Field(
        ..., description="the desired PUBLISHED state of the row (true=public, false=draft)"
    )


class AgentRunRequest(BaseModel):
    """Body for POST /agent/run (ADR adr_agents_sdk_dashboard, Phase B). The single-step agent
    run. Like RunRequest, it has NO tenant_id field -- the tenant is resolved from the verified
    JWT, never from the client.

    ``inputs`` is the TYPED form payload, validated against the agent's Input Schema by the
    frontend (and bound into the assembled contract server-side). An agent with NO Input Schema
    falls back to a single free-text ``intent`` -- which is carried inside ``inputs`` as
    ``{"intent": "..."}`` (the run_agent contract), so this one field serves both the typed and
    the free-text shapes. ``options`` is an optional non-secret passthrough (e.g. a soft budget
    hint); it MUST NOT carry a tenant or a credential (the server strips them + supplies the
    credential + the enabled-agent allowlist itself).
    """

    agent_id: str = Field(..., min_length=1, description="agent id, e.g. 'research_analyst'")
    inputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="typed inputs per the agent's Input Schema, or {'intent': '...'} free-text",
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None, description="optional non-secret run hints (no tenant/credential)"
    )


class AgentRunStartRequest(AgentRunRequest):
    """Body for POST /agent/runs (ADR Phase C -- the ASYNC multi-step run). Same shape as the
    single-step AgentRunRequest (agent_id + typed inputs + non-secret options), with NO
    tenant_id field (the tenant is the verified JWT claim). ``options`` MAY carry a
    team_charter-style ``budget`` ({max_steps, max_tokens}) -- the OQ4 ceiling the loop enforces
    -- and an optional ``irreversible_tools`` list (the OQ8 HITL trigger set). It MUST NOT carry
    a tenant or a credential (the server strips them + supplies the credential itself)."""


# --------------------------------------------------------------------------- #
# Auth helper -- the single chokepoint that yields a trusted tenant_id.
# --------------------------------------------------------------------------- #
def _tenant_from_authorization(authorization: Optional[str]) -> str:
    """Turn an ``Authorization`` header into a VERIFIED tenant_id (or raise AuthError).

    The ONLY place the API derives a tenant. Sequence: parse the bearer token -> verify the
    Supabase JWT -> extract tenant_id (coalesce app_metadata then top-level). Any failure
    raises AuthError, which the app's exception handler maps to 401. No body, query, or
    custom header is ever consulted for the tenant.
    """
    token = bearer_token_from_header(authorization)
    claims = verify_supabase_jwt(token)
    return extract_tenant_id(claims)


# --------------------------------------------------------------------------- #
# App factory.
# --------------------------------------------------------------------------- #
def _cors_origins() -> List[str]:
    """Resolve CORS origins (env override -> localhost defaults)."""
    raw = os.environ.get(_ENV_CORS_ORIGINS, "").strip()
    if raw:
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        if origins:
            return origins
    return list(_DEFAULT_CORS_ORIGINS)


def create_app() -> FastAPI:
    """Build + return the FastAPI app (factory so tests get a fresh instance)."""
    # Live-go seam: register the DbSession factory named by
    # $CEXAI_DASHBOARD_SESSION_FACTORY (if any). UNSET -> no-op -> live reads/writes
    # degrade to empty/local-only (the default fixtures-equivalent state). FAIL-SOFT:
    # a misconfigured target warns to stderr and the app still boots local-only.
    deps.register_session_factory_from_env()

    # Public (anon-role) live-go seam (spec 10 W1-backend): register the SEPARATE public
    # DbSession factory named by $CEXAI_DASHBOARD_PUBLIC_SESSION_FACTORY (if any). UNSET ->
    # no-op -> the unauthenticated public endpoints degrade to local-only (resolve -> 404,
    # catalog -> empty), NEVER disclosing a tenant. A separate factory so the public path
    # mints anon-role sessions (RLS published-only) and NEVER borrows the authenticated one.
    deps.register_public_session_factory_from_env()

    application = FastAPI(
        title="CEXAI Dashboard API",
        version="1.0.0",
        description="Employee dashboard backend: organic capability cards + tenant-scoped runs.",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    _register_exception_handlers(application)
    _register_routes(application)

    # Mount the UNAUTHENTICATED public-site router (spec 10 W1-backend): GET
    # /public/tenant-info + GET /public/catalog. These have NO auth dependency (the public
    # site is browsed anonymously) and read published-only via the anon-role public reader
    # (the no-leak triple-guard: anon RLS + backend published/kind filter + slug->tenant_id
    # public_read gate). Mounted alongside the authenticated routes; the two never share a
    # path (no JWT chokepoint here, claim-free anon reads only).
    application.include_router(public_routes_mod.build_public_router())

    # Per-tenant rate-limit + concurrency guards (multi-tenant Sec 5b HIGH gaps:
    # rate-limit/quota + pool-exhaustion/noisy-neighbor). SAFE-DEFAULT OFF -- a NO-OP
    # unless CEXAI_TENANT_RATE_LIMIT_ENABLED is truthy, so the app is byte-identical when
    # disabled. Keyed on the VERIFIED tenant_id (the same JWT chokepoint the routes use),
    # never a client value. FAIL-OPEN-with-log on the guard's own error (availability over a
    # guard bug); auth stays fail-closed upstream. Installed LAST so its router-level deps +
    # 429 handlers sit on top of the fully-wired app.
    ratelimit.install_tenant_guards(application)
    return application


def _register_exception_handlers(application: FastAPI) -> None:
    """Wire structured JSON error responses for the failure taxonomy.

    Maps:
      * AuthError            -> 401 (fail-closed auth; the #1 rule).
      * CapabilityRefused    -> 400/403 (a deny from the runtime: disabled cap, frozen
                                kind, missing credential, etc.).
      * RuntimeUnavailable   -> 503 (a parallel-built dependency not ready).
    Every body is ``{"error": {"type", "reason", "detail"}}`` -- never a secret/traceback.
    """

    @application.exception_handler(AuthError)
    async def _on_auth_error(_request: Request, exc: AuthError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "type": "auth_error",
                    "reason": exc.reason,
                    "detail": exc.detail,
                }
            },
        )

    @application.exception_handler(deps.RuntimeUnavailable)
    async def _on_runtime_unavailable(
        _request: Request, exc: deps.RuntimeUnavailable
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "type": "runtime_unavailable",
                    "reason": exc.component,
                    "detail": exc.detail,
                }
            },
        )

    # A composition-control-plane mutation error (W2; PATCH /capabilities) -> a precise 4xx/5xx.
    # Registered globally (like RuntimeUnavailable) so any future compose route fails CLOSED with
    # the structured envelope, never a 500 traceback.
    @application.exception_handler(deps.ComposeError)
    async def _on_compose_error(_request: Request, exc: deps.ComposeError) -> JSONResponse:
        return _compose_error_response(exc)

    # A tenant-boundary deny from the audited adapter (cross_tenant / missing_tenant) ->
    # 403. Belt-and-braces: the per-route handlers already map this, but registering it
    # here means a deny raised anywhere (e.g. a future route) fails CLOSED to 403, never
    # leaks a 500 with a traceback.
    @application.exception_handler(entities_mod.TenantDataDenied)
    async def _on_tenant_denied(
        _request: Request, exc: entities_mod.TenantDataDenied
    ) -> JSONResponse:
        return _tenant_denied_response(exc)


def _register_routes(application: FastAPI) -> None:
    """Attach the dashboard endpoints."""

    @application.get("/healthz")
    async def healthz() -> Dict[str, str]:
        """Liveness. No auth, no runtime touch -- always 200 if the process is up."""
        return {"status": "ok", "service": "cexai-dashboard-api"}

    @application.get("/capabilities")
    async def get_capabilities(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /capabilities -> the tenant's enabled capability cards (organic).

        Verifies the JWT, derives tenant_id from the verified claim, and returns
        ``registry.list_capabilities(tenant_id)`` (overlay-derived; spec B.4). The tenant
        is NEVER taken from a query/body. Cards are JSON dicts.
        """
        tenant_id = _tenant_from_authorization(authorization)
        cards = deps.list_capability_cards(tenant_id)
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, "capabilities": cards},
        )

    # ----------------------------------------------------------------------- #
    # Composition control plane (mission DASHBOARD_COMPOSITION W2, spec SS3.3).
    # The WRITE/control surface on top of the W1 read gate: read the tenant's full attach
    # state, and attach/detach a capability module. Both derive tenant_id from the verified
    # JWT (NEVER a body/query). The PATCH performs a guarded YAML write to the tenant's
    # capability_map.yaml (mutating ONLY the capabilities: block). Credential-free.
    # ----------------------------------------------------------------------- #
    @application.get("/capabilities-config")
    async def get_capabilities_config(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /capabilities-config -> the tenant's full ATTACH state (declared/enabled/disabled).

        Verifies the JWT, derives tenant_id from the verified claim, and returns the registry's
        ``attach_state(tenant_id)`` (spec SS3.3). The compose UI (W3) reads this to render every
        declared capability with its on/off toggle. The tenant is NEVER from a query/body.
        READ-ONLY + credential-free. DEGRADE-NEVER: an unavailable registry -> an empty state,
        never a 500.
        """
        tenant_id = _tenant_from_authorization(authorization)
        state = deps.get_capabilities_config(tenant_id)
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, **state},
        )

    @application.patch("/capabilities/{slug}")
    async def patch_capability(
        slug: str,
        body: PatchCapabilityRequest = Body(...),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """PATCH /capabilities/{slug} body {action: attach|detach} -> mutate the attach state.

        Flow (spec SS3.3): verify JWT -> tenant_id (NEVER from body); validate the action; call
        the guarded registry writer (a fail-closed write to the tenant's capability_map.yaml that
        mutates ONLY the ``capabilities:`` block, preserving every other block). Returns the NEW
        attach state. FAIL-CLOSED: an unknown action -> 400; an undeclared slug -> 409 (a
        capability must be DECLARED to be attachable); a registry not ready -> 503; a write
        failure -> 500. The slug is the path segment; the tenant is server-derived. Credential-free.
        """
        tenant_id = _tenant_from_authorization(authorization)
        state = deps.mutate_capability(tenant_id, slug, body.action)
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, **state},
        )

    # ----------------------------------------------------------------------- #
    # Agents catalog + READ surface (ADR adr_agents_sdk_dashboard, Phase A).
    # CLONES GET /capabilities: SAME JWT->tenant_id chokepoint + overlay-gating +
    # secret-free allowlist DTO. READ-ONLY -- NO run_agent (that is Phase B/C),
    # NO new tables, NO frozen-kind touch. The tenant is NEVER from a query/body.
    # ----------------------------------------------------------------------- #
    @application.get("/agents")
    async def get_agents(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /agents -> the tenant's VISIBLE agents (overlay-gated; ADR Phase A).

        Verifies the JWT, derives tenant_id from the verified claim, and returns
        ``agents_config.list_agents(tenant_id)`` -- the agent catalog
        (.cex/config/capability_registry.json) projected to value-free Agent DTOs and
        gated by the tenant overlay ``agents:`` block (exactly as /capabilities gates by
        enabled_capabilities). The tenant is NEVER taken from a query/body. Each DTO is a
        secret-free allowlist (id/name/nucleus/goal/kind/pillar/tools/model/enabled) --
        there is no credential on a catalog record. READ-ONLY: no runtime, no DB, no secret.
        """
        tenant_id = _tenant_from_authorization(authorization)
        agents = agents_config_mod.list_agents(tenant_id)
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, "agents": agents},
        )

    @application.get("/agents/{agent_id}")
    async def get_agent(
        agent_id: str,
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /agents/{id} -> one agent's persona/capabilities/IO-contract/SLA (read-only).

        Verifies the JWT, derives tenant_id from the verified claim, and returns
        ``agents_config.get_agent(tenant_id, id)`` -- the DTO plus detail enriched from the
        agent + agent_card artifact on disk when resolvable (else the registry record). The
        agent is resolved from the SAME overlay-gated visible set /agents uses, so a gated-out
        / unknown id -> 404 (never another tenant's data, never a frozen kind). READ-ONLY:
        no run_agent, no DB, no secret value. The id is the path segment; the tenant is
        server-derived.
        """
        tenant_id = _tenant_from_authorization(authorization)
        agent = agents_config_mod.get_agent(tenant_id, agent_id)
        if agent is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "type": "agent_not_found",
                        "reason": "unknown_agent",
                        "detail": "no such agent for this tenant",
                    }
                },
            )
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, "agent": agent},
        )

    # ----------------------------------------------------------------------- #
    # Crews catalog + READ surface (ADR adr_agents_sdk_dashboard, Phase D).
    # The layer ABOVE single agents: a crew is a multi-role TEAM (crew_template).
    # CLONES GET /agents EXACTLY: SAME JWT->tenant_id chokepoint + overlay-gating
    # (overlay ``crews:`` block) + secret-free allowlist DTO. READ-ONLY -- NO
    # run_crew (that is the founder-gated control-plane step), NO new tables, NO
    # frozen-kind touch. The tenant is NEVER from a query/body.
    # ----------------------------------------------------------------------- #
    @application.get("/crews")
    async def get_crews(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /crews -> the tenant's VISIBLE crews (overlay-gated; ADR Phase D).

        Verifies the JWT, derives tenant_id from the verified claim, and returns
        ``crews_config.list_crews(tenant_id)`` -- the crew catalog (the crew_template
        artifacts on disk) projected to value-free Crew DTOs and gated by the tenant
        overlay ``crews:`` block (exactly as /agents gates by ``agents:``). The tenant is
        NEVER taken from a query/body. Each DTO is a secret-free allowlist
        (id/name/nucleus/process/role_count/roles/goal/enabled) -- a crew_template carries
        no credential. READ-ONLY: no runtime, no DB, no secret.
        """
        tenant_id = _tenant_from_authorization(authorization)
        crews = crews_config_mod.list_crews(tenant_id)
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, "crews": crews},
        )

    @application.get("/crews/{crew_id}")
    async def get_crew(
        crew_id: str,
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /crews/{id} -> one crew's roles/topology/handoff-protocol (read-only).

        Verifies the JWT, derives tenant_id from the verified claim, and returns
        ``crews_config.get_crew(tenant_id, id)`` -- the DTO plus detail parsed from the
        crew_template artifact on disk (the full Roles table + process topology + handoff
        protocol + provenance). The crew is resolved from the SAME overlay-gated visible set
        /crews uses, so a gated-out / unknown id -> 404 (never another tenant's data, never a
        frozen kind). READ-ONLY: no run_crew, no DB, no secret. The id is the path segment;
        the tenant is server-derived.
        """
        tenant_id = _tenant_from_authorization(authorization)
        crew = crews_config_mod.get_crew(tenant_id, crew_id)
        if crew is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "type": "crew_not_found",
                        "reason": "unknown_crew",
                        "detail": "no such crew for this tenant",
                    }
                },
            )
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, "crew": crew},
        )

    @application.post("/capability/run")
    async def run_capability_endpoint(
        body: RunRequest = Body(...),
        render_format: Optional[str] = Query(
            default=None, pattern="^(md|html)$",
            description="optional dual-output projection for a research_universe run: "
            "'md' (canonical) or 'html' (derivative). Absent -> the structured JSON report.",
        ),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """POST /capability/run[?render_format=md|html] -> run one capability for the JWT tenant.

        Flow (spec B.3):
          1. Verify JWT -> tenant_id (NEVER from body; a body tenant_id field does not
             even exist on RunRequest, and any stray key in ``options`` is overwritten).
          2. Build a SERVER-SIDE Credential (mode=byo_api_key) for the tenant.
          3. Resolve the tenant's enabled-capability allowlist (overlay) and inject it as
             ``options['enabled_capabilities']`` so the runtime's deny seam is authoritative.
          4. Call run_capability(tenant_id, capability, intent, credential, options=...).
          5. Return the CapabilityResult as JSON (the api_key is never present on it).

        ``render_format`` (spec_dashboard_roadmap W1, opt-in -- the DEFAULT is UNCHANGED):
          * absent      -> the CapabilityResult as JSON. For a research_universe run this
                           carries ``structured`` (the multi-source report) so the UI renders
                           per-section cards. For an 8F-build capability it carries ``artifact``.
          * ``md``/``html`` -> for a research_universe run (a result carrying ``structured``)
                           the view ADDITIONALLY carries ``render`` = the render_universe MD
                           (canonical) or HTML (derivative) projection of the report. For a
                           non-universe result it is a no-op (the structured report is the
                           universe-only carrier), so the build capabilities are unaffected.
        The client never supplies tenant; same fail-closed auth.

        Errors: AuthError->401, CapabilityRefused->400/403, RuntimeUnavailable->503.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        runtime = deps.load_runtime()

        # Build server-side options: start from the client's non-secret hints, then HARD-SET
        # the enabled allowlist + STRIP any client-supplied tenant/credential keys.
        options: Dict[str, Any] = dict(body.options or {})
        for forbidden in ("tenant_id", "tenant", "credential", "api_key"):
            options.pop(forbidden, None)
        enabled = deps.resolve_enabled_capabilities(tenant_id)
        if enabled is not None:
            options["enabled_capabilities"] = enabled

        # The typed form payload (mission BRANDBOOK, Cell A). Same defense as options: STRIP
        # any tenant/credential key the client tried to smuggle in -- the runtime resolves
        # it (image -> palette, doc/url -> text) and hands it to a structured generator.
        inputs: Dict[str, Any] = dict(body.inputs or {})
        for forbidden in ("tenant_id", "tenant", "credential", "api_key"):
            inputs.pop(forbidden, None)

        credential = deps.build_credential(tenant_id, runtime=runtime)

        # WIRE the runtime->central write-through (roadmap C5 / debt D5): a passed run
        # persists into the tenant's OWN tenant_data through the audited adapter
        # (RuntimeSyncWriter). DEGRADE-NEVER: no central creds -> a LocalOnlyWriter, so the
        # run still completes (persisted=False). A safe, minimal swap on the hot path --
        # db was None (always produced-unpersisted); it is now the real seam.
        db_writer = deps.make_run_writer(tenant_id, token)

        # WIRE the EDIT->REFLECT read seam (arch-council B2): an ad/catalog run hydrates
        # inputs['product_record'] from the tenant's CURRENT product data (tenant_data
        # kind='products') through the audited adapter, so editing a product makes the next ad
        # reflect it. DEGRADE-NEVER: no central creds -> a LocalOnly reader (find_product ->
        # None) -> no hydration, run unchanged. Passed ONLY when the active runtime's
        # run_capability accepts ``db_reader`` (a test fake that predates the param is left
        # byte-identical -- the SAME defensiveness the inputs kwarg uses).
        db_reader = deps.make_run_reader(tenant_id, token)

        try:
            # BRANDBOOK Cell A: forward the typed any-media payload ONLY when the client sent
            # one. Passing it unconditionally would break a runtime that predates the param
            # (e.g. a test fake) -- the conditional kwarg keeps the call byte-identical for
            # every existing (inputs-free) run while the real runtime resolves it when present.
            run_kwargs: Dict[str, Any] = {"db": db_writer, "options": options}
            if inputs:
                run_kwargs["inputs"] = inputs
            if _runtime_accepts_kw(runtime, "run_capability", "db_reader"):
                run_kwargs["db_reader"] = db_reader
            result = runtime.run_capability(
                tenant_id,
                body.capability,
                body.intent,
                credential,
                **run_kwargs,
            )
        except runtime.CapabilityRefused as exc:
            return _capability_refused_response(exc)

        view = _result_to_view(result)
        # spec_dashboard_roadmap W1: a research_universe run carries a ``structured`` report.
        # When ?render_format=md|html is requested, project it via render_universe (NOT the
        # marketplace render) and attach it as ``render``. Default (no render_format) returns
        # the structured report so the UI renders section cards. Non-universe results have no
        # ``structured`` -> this is a no-op (the build capabilities are byte-identical).
        if render_format:
            view["render_format"] = render_format
            view["render"] = _render_universe_view(view.get("structured"), render_format)
        return JSONResponse(status_code=200, content=view)

    # ----------------------------------------------------------------------- #
    # Dual-output UPLOAD-PERSIST (the founder follow-up to SEED-DUALOUTPUT).
    # A human upload for a dual-output media slot is stored (MediaStore seam: base64-
    # inline V1) and persisted into the tenant's OWN tenant_data row -- the slot flips
    # empty->generated and BOTH faces (human media ledger + machine .md the tenant AI
    # reads) are regenerated. read-modify-write, TENANT-SCOPED by RLS. SAME JWT->tenant_id
    # chokepoint; the tenant is NEVER from the path/body. Credential-free.
    # ----------------------------------------------------------------------- #
    @application.patch("/capability/{record_id}/media/{slot_key}")
    async def upload_capability_media(
        record_id: str,
        slot_key: str,
        file: UploadFile = File(...),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """PATCH /capability/{record_id}/media/{slot_key} (multipart ``file``) -> persist a human
        upload into a dual-output media slot.

        Flow: verify JWT -> tenant_id (NEVER from path/body); read the persisted row by record_id
        TENANT-SCOPED (a foreign/unknown id -> 404); locate the slot (-> its declared kind);
        validate + store the bytes via the MediaStore seam (kind/content-type/size fail-closed);
        regenerate the dual_output with the slot flipped empty->generated (machine .md base64-
        elided -- lean AI face); UPDATE the row TENANT-SCOPED. Returns the updated dual_output.

        Errors: AuthError->401; unknown record/slot (or no data plane -> nothing persisted)->404;
        bad file->400/413/415; storage sink gated->503; a lost update (row changed/removed)->409.
        The tenant is server-derived; no credential is ever in scope here.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        media_store_mod, media_persist_mod = deps.load_media_modules()

        def _media_err(reason: str, status: int, detail: str) -> JSONResponse:
            return JSONResponse(
                status_code=status,
                content={"error": {"type": "media_upload_error", "reason": reason,
                                   "detail": detail}},
            )

        writer = deps.make_run_writer(tenant_id, token)
        payload = writer.read_artifact(tenant_id, record_id)
        if not isinstance(payload, dict):
            # no row for THIS tenant (foreign/unknown id) OR no central data plane (local-only).
            return _media_err("not_found", 404,
                              "no persisted result for this tenant + record id")
        meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
        dual = meta.get("dual_output")
        if not isinstance(dual, dict) or not isinstance(dual.get("media_slots"), list):
            return _media_err("no_dual_output", 404,
                              "this result has no dual-output media to update")

        slot = next(
            (s for s in dual["media_slots"]
             if isinstance(s, dict) and str(s.get("key") or "") == slot_key),
            None,
        )
        if slot is None:
            return _media_err("unknown_slot", 404, "no media slot on this asset")
        kind = str(slot.get("kind") or "image")

        # Bounded read (cap + 1) so an over-cap upload is refused without buffering the whole blob.
        cap = media_store_mod.max_upload_bytes()
        data = await file.read(cap + 1)
        if data and len(data) > cap:
            return _media_err("file_too_large", 413, "file exceeds the upload size cap")

        store = media_store_mod.get_media_store()
        try:
            stored = store.put(
                tenant_id, record_id, slot_key, kind,
                file.filename or slot_key, data or b"", file.content_type,
            )
        except media_store_mod.MediaStoreError as exc:
            return _media_err(exc.reason, exc.status, exc.detail)

        capability = str(dual.get("capability") or "")
        structured = meta.get("structured") if isinstance(meta.get("structured"), dict) else None
        try:
            new_dual = media_persist_mod.apply_upload_to_dual_output(
                dual, structured, capability, slot_key, str(stored["src"]), tenant=tenant_id,
            )
        except media_persist_mod.MediaPersistError as exc:
            return _media_err(exc.reason, exc.status, exc.detail)

        meta["dual_output"] = new_dual
        payload["meta"] = meta
        if not writer.update_artifact_payload(tenant_id, record_id, payload):
            return _media_err("persist_failed", 409,
                              "the row could not be updated (it may have changed or been removed)")

        updated_slot = next(
            (s for s in (new_dual.get("media_slots") or [])
             if isinstance(s, dict) and str(s.get("key") or "") == slot_key),
            None,
        )
        return JSONResponse(
            status_code=200,
            content={
                "tenant_id": tenant_id,
                "record_id": record_id,
                "slot_key": slot_key,
                "dual_output": new_dual,
                "slot": updated_slot,
                "stored": {
                    "content_type": stored.get("content_type"),
                    "bytes": stored.get("bytes"),
                    "stored_as": stored.get("stored_as"),
                },
                "persisted": True,
            },
        )

    # ----------------------------------------------------------------------- #
    # Agent RUN -- the single-step agent run (ADR adr_agents_sdk_dashboard, Phase B).
    # CLONES POST /capability/run EXACTLY: the SAME JWT->tenant_id chokepoint, the SAME
    # server-side BYO-key Credential, the SAME frozen guard (inherited via the runtime),
    # the SAME make_run_writer persistence into tenant_data, and the SAME _result_to_view
    # secret-free allowlist. It differs ONLY in: it calls run_agent (the SIBLING) with an
    # agent_id + typed inputs, and gates on the ENABLED-AGENT allowlist (deps.
    # resolve_enabled_agents) instead of enabled_capabilities. SYNCHRONOUS (1 step) -- there
    # is NO run_id/async (that is Phase C). tenant_id is NEVER from the body.
    # ----------------------------------------------------------------------- #
    @application.post("/agent/run")
    async def run_agent_endpoint(
        body: AgentRunRequest = Body(...),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """POST /agent/run -> run ONE agent (single step) for the JWT's tenant.

        Flow (clone of POST /capability/run; ADR Phase B):
          1. Verify JWT -> tenant_id (NEVER from body; AgentRunRequest has no tenant field, and
             any stray key in ``options`` is stripped).
          2. Build a SERVER-SIDE Credential (mode=byo_api_key; OQ2) for the tenant -- the SAME
             build_credential the capability run uses (the browser never sends a credential).
          3. Resolve the tenant's enabled-AGENT allowlist (the visible+enabled overlay set) and
             inject it as ``options['enabled_capabilities']`` so the runtime's deny seam is
             authoritative (a gated-out / disabled / unknown agent is refused).
          4. Validate ``inputs`` against the agent's Input Schema is the FRONTEND's job (the typed
             form); the backend binds whatever typed ``inputs`` arrive (or {'intent': ...}
             free-text) into the assembled contract via run_agent.
          5. Call run_agent(tenant_id, agent_id, inputs, credential, db=writer, options=...).
          6. Return the AgentRunResult as JSON via _result_to_view (the SAME credential-free
             allowlist -- the api_key is never present).

        Errors: AuthError->401, CapabilityRefused->400/403 (same taxonomy as the capability run;
        budget_exceeded -> 400), RuntimeUnavailable->503.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        agent_runtime = deps.load_agent_runtime()

        # Server-side options: client's non-secret hints, then HARD-SET the enabled-AGENT
        # allowlist + STRIP any client-supplied tenant/credential keys (identical posture to
        # the capability run; the allowlist source is the agent visible-set, not capabilities).
        options: Dict[str, Any] = dict(body.options or {})
        for forbidden in ("tenant_id", "tenant", "credential", "api_key"):
            options.pop(forbidden, None)
        # Agents are deny-by-default: resolve_enabled_agents returns the visible+enabled ids
        # (possibly []). Always inject it so the runtime's gate is authoritative -- an empty
        # list denies every agent (fail-closed), never an open gate.
        options["enabled_capabilities"] = deps.resolve_enabled_agents(tenant_id)

        # The typed inputs (or {'intent': ...} free-text). run_agent binds them into the
        # assembled contract; an absent body -> {} (run_agent then derives the intent from the
        # agent goal, or refuses if the agent truly has no actionable contract).
        inputs: Dict[str, Any] = dict(body.inputs or {})

        # The SAME server-side credential + the SAME persistence writer the capability run uses
        # (BYO key, tenant from JWT, audited adapter or local-only) -- REUSED, not forked.
        credential = deps.build_credential(tenant_id, runtime=agent_runtime)
        db_writer = deps.make_run_writer(tenant_id, token)

        try:
            result = agent_runtime.run_agent(
                tenant_id,
                body.agent_id,
                inputs,
                credential,
                db=db_writer,  # persists via the audited adapter (or local-only) into tenant_data
                options=options,
            )
        except agent_runtime.CapabilityRefused as exc:
            return _capability_refused_response(exc)

        return JSONResponse(status_code=200, content=_result_to_view(result))

    # ----------------------------------------------------------------------- #
    # ASYNC MULTI-STEP agent run (ADR adr_agents_sdk_dashboard, Phase C).
    #
    # OLD SYNC /agent/run DISPOSITION (decided + NOTED): POST /agent/run STAYS the
    # SYNCHRONOUS single-step (Phase B) path -- it is the degenerate 1-step run and 16
    # Phase-B tests assert its synchronous AgentRunResult shape. The ASYNC multi-step
    # contract is a NEW sibling route, POST /agent/runs (plural), returning { run_id }
    # immediately. /capability/run also stays synchronous (the single-shot card). So the
    # async run_id + event stream is ADDITIVE -- no existing endpoint's shape changes.
    #
    # All three async routes CLONE the JWT->tenant_id chokepoint + the server-side BYO-key
    # Credential + the enabled-AGENT gate + the audited make_run_writer persistence. The
    # loop persists agent_runs/agent_steps via that SAME adapter (tenant_id EXPLICIT, RLS).
    # tenant_id is NEVER from the body; a run_id is NOT a capability (every read re-checks
    # the run's tenant against the caller -> a foreign run_id is 404, never cross-tenant).
    # ----------------------------------------------------------------------- #
    @application.post("/agent/runs")
    async def start_agent_run_endpoint(
        body: AgentRunStartRequest = Body(...),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """POST /agent/runs -> kick a MULTI-step agent run; return { run_id } at once (ASYNC).

        Flow (clone of POST /agent/run's auth+credential+gate; ADR Phase C):
          1. Verify JWT -> tenant_id (NEVER from body).
          2. Build the SAME server-side BYO-key Credential + the SAME audited make_run_writer.
          3. Gate on the enabled-AGENT allowlist (deny-by-default; an empty list denies all).
          4. Mint a run_key; start the loop on a worker thread (cex_agent_loop.run_agent_multistep
             via agent_runs.start_agent_run); the run_id is the deterministic agent_run_id.
          5. Return { run_id, status: 'running' } immediately -- the client polls GET
             /agent/run/{run_id} or streams GET /agent/run/{run_id}/events.

        A non-positive budget (OQ4) refuses synchronously here (the loop's pre-flight guard runs
        before the thread spawns) -> 400 budget_exceeded. Errors: AuthError->401,
        CapabilityRefused->400/403, RuntimeUnavailable->503.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        loop_runtime = deps.load_agent_loop_runtime()

        options: Dict[str, Any] = dict(body.options or {})
        for forbidden in ("tenant_id", "tenant", "credential", "api_key"):
            options.pop(forbidden, None)
        options["enabled_capabilities"] = deps.resolve_enabled_agents(tenant_id)
        inputs: Dict[str, Any] = dict(body.inputs or {})

        credential = deps.build_credential(tenant_id, runtime=loop_runtime)
        db_writer = deps.make_run_writer(tenant_id, token)

        # Mint the run key. The loop's pre-flight (enabled gate + OQ4 non-positive-budget guard)
        # runs SYNCHRONOUSLY before the thread, so a refusal is a 4xx here, not a silent run.
        import uuid as _uuid

        run_key = _uuid.uuid4().hex
        try:
            # Pre-flight the cheap synchronous guards by attempting the kickoff inline-safe:
            # start_agent_run spawns a thread for the loop body but the guards (gate/budget/
            # resolve) execute on the thread; to surface a refusal as a 4xx we run the guard
            # checks here first via the runtime's helpers (the SAME ones the loop reuses).
            _preflight_agent_run(loop_runtime, tenant_id, body.agent_id, options)
        except loop_runtime.CapabilityRefused as exc:
            return _capability_refused_response(exc)

        run_id = agent_runs_mod.start_agent_run(
            tenant_id=tenant_id,
            agent_id=body.agent_id,
            inputs=inputs,
            credential=credential,
            db=db_writer,
            options=options,
            runtime=loop_runtime,
            run_key=run_key,
            background=True,
        )
        return JSONResponse(
            status_code=202,
            content={"run_id": run_id, "status": "running", "tenant_id": tenant_id},
        )

    @application.get("/agent/run/{run_id}")
    async def get_agent_run(
        run_id: str,
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /agent/run/{run_id} -> status + result + steps so far (the POLL fallback, OQ3).

        TENANT-SCOPED: resolves the run under the verified tenant_id; a run owned by another
        tenant (or unknown) -> 404 (never another tenant's transcript). Returns the full
        snapshot (status/artifact/score/steps_log/cost) any client can poll. The api_key is
        never present (the snapshot is a credential-free allowlist)."""
        tenant_id = _tenant_from_authorization(authorization)
        registry = agent_runs_mod.get_registry()
        rec = registry.get(run_id, tenant_id)
        if rec is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "type": "run_not_found",
                        "reason": "unknown_run",
                        "detail": "no such run for this tenant",
                    }
                },
            )
        return JSONResponse(status_code=200, content=rec.snapshot())

    @application.get("/agent/run/{run_id}/events")
    async def get_agent_run_events(
        run_id: str,
        authorization: Optional[str] = Header(default=None),
    ) -> Any:
        """GET /agent/run/{run_id}/events -> the step stream as Server-Sent Events (OQ3 SSE).

        Streams one ``event: step`` frame per new plan/act/observe/tool step, then a final
        ``event: done`` (or ``event: timeout`` if the run stalls). TENANT-SCOPED: a run not owned
        by the verified tenant yields a single ``event: not_found`` and closes (never another
        tenant's stream). The POLL fallback (GET /agent/run/{run_id}) returns the same data for
        clients without SSE. media_type text/event-stream; no-cache; never buffers a secret."""
        tenant_id = _tenant_from_authorization(authorization)
        registry = agent_runs_mod.get_registry()
        generator = agent_runs_mod.stream_run_events(registry, run_id, tenant_id)
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @application.get("/results")
    async def get_results(
        capability: Optional[str] = Query(default=None),
        limit: int = Query(default=_DEFAULT_RESULTS_LIMIT, ge=1, le=_MAX_RESULTS_LIMIT),
        render_format: Optional[str] = Query(
            default=None, pattern="^(md|html)$",
            description="optional dual-output projection: 'md' (canonical) or 'html' (derivative)",
        ),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /results?capability=[&render_format=md|html] -> the tenant's recent artifacts.

        Reads from the tenant's OWN Supabase THROUGH the SupabaseDataAdapter under the
        user's JWT (spec B.3 PLANE 1: RLS is the authoritative boundary). tenant_id comes
        ONLY from the verified claim (NEVER client-supplied), unchanged by render_format. If
        the data path is not configured in this environment, returns an empty list with a
        ``note`` rather than failing (read path is non-critical for the Phase-1 template gate).

        ``render_format`` (CAPABILITY_LAYER W1, opt-in -- the DEFAULT is UNCHANGED):
          * absent      -> the legacy row summary (id, capability, kind, created_at) only.
          * ``md``      -> each row additionally carries ``render`` = its CANONICAL MD-frontmatter
                           projection (the persisted artifact, or re-rendered from the row's
                           structured payload via cex_output_contract).
          * ``html``    -> each row additionally carries ``render`` = its DERIVATIVE HTML report.
        Mirrors the existing query-param handling; the payload column is fetched only when a
        projection is requested (so the default scan stays light).
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        if render_format:
            rows, note = _read_tenant_results_rendered(
                tenant_id, token, capability, limit, render_format
            )
        else:
            rows, note = _read_tenant_results(tenant_id, token, capability, limit)
        payload: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "capability": capability,
            "results": rows,
        }
        if render_format:
            payload["render_format"] = render_format
        if note:
            payload["note"] = note
        return JSONResponse(status_code=200, content=payload)

    # ----------------------------------------------------------------------- #
    # Dashboard-v2 shells (roadmap C5 / debt D5): /summary + /settings + CRUD.
    # ----------------------------------------------------------------------- #
    @application.get("/summary")
    async def get_summary(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /summary -> the tenant's home shell (stats + recent runs + health).

        READ-ONLY + DERIVED: projects SummaryResponse from the SAME data the cards +
        results read -- the tenant's capability cards (overlay-derived) and its recent
        tenant_data rows (tenant-scoped via the adapter under the verified claim). tenant_id
        comes ONLY from the JWT. Degrades to empty-but-200 when no data plane is wired (the
        health strip then reports the data plane as degraded rather than failing).
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        cards = deps.list_capability_cards(tenant_id)
        rows, note = _read_tenant_results(tenant_id, token, None, _DEFAULT_RESULTS_LIMIT)
        payload = summary_mod.build_summary(
            tenant_id, cards, rows, data_plane_ok=(note == "")
        )
        return JSONResponse(status_code=200, content=payload)

    @application.get("/settings")
    async def get_settings(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /settings -> the tenant shell (context + integrations + secret STATUS).

        SECURE-BY-DEFAULT: the secrets surface reports CONFIGURED STATUS ONLY -- a bool per
        named secret; a VALUE is NEVER read or returned (deps.secret_is_configured is a
        presence probe). tenant_id + operator email come ONLY from the verified claim. The
        data-plane integration state reflects whether a factory is wired.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        operator_email = _operator_email_from_authorization(authorization)
        data_plane_ok = _build_session_factory(tenant_id, token) is not None
        payload = summary_mod.build_settings(
            tenant_id,
            operator_email=operator_email,
            data_plane_ok=data_plane_ok,
            secret_is_configured=lambda name: deps.secret_is_configured(tenant_id, name),
        )
        return JSONResponse(status_code=200, content=payload)

    @application.get("/entities-config")
    async def get_entities_config(
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /entities-config -> the tenant's managed-entity SCHEMAS (EntitySchema[]).

        OVERLAY-DRIVEN (the mold's tenant-generic promise): reads the verified tenant's
        overlay ``managed_entities:`` and returns the schema list the frontend's
        management half renders a <DataManager/> from -- MIRRORS the cards path (overlay
        -> backend -> frontend), one overlay file driving both surfaces.

        TENANT-SCOPED + SECURE: tenant_id comes ONLY from the verified JWT; the overlay
        read is scoped to that tenant via the fail-closed path guard (never another
        tenant's config). Each entry's slug is re-validated against the same allowlist the
        /entity CRUD uses (a malformed entry is dropped, never a broken route). READ-ONLY:
        no DB, no secret. Degrades to an EMPTY list (the management nav then hides) when no
        overlay declares entities -- NEVER a 500, NEVER another tenant's data.
        """
        tenant_id = _tenant_from_authorization(authorization)
        schemas = entities_config_mod.list_entity_schemas(tenant_id)
        return JSONResponse(
            status_code=200,
            content={"tenant_id": tenant_id, "entities": schemas},
        )

    @application.get("/entity/{slug}")
    async def list_entity(
        slug: str,
        limit: int = Query(default=_MAX_RESULTS_LIMIT, ge=1, le=_MAX_RESULTS_LIMIT),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """GET /entity/{slug} -> the tenant's rows for one entity (EntityListResponse).

        Reads tenant_data WHERE kind = <slug> via the audited adapter (tenant-scoped). The
        slug selects the entity; tenant_id is server-derived. Degrades to an empty,
        tenant-scoped list with a ``note`` when no data plane is wired -- NEVER another
        tenant's data.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        manager = _entity_manager(tenant_id, token)
        try:
            records, note = manager.list(tenant_id, slug, limit=limit)
        except entities_mod.EntityError as exc:
            return _entity_error_response(exc)
        except entities_mod.TenantDataDenied as exc:
            return _tenant_denied_response(exc)
        payload: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "entity": slug,
            "records": records,
        }
        if note:
            payload["note"] = note
        return JSONResponse(status_code=200, content=payload)

    @application.post("/entity/{slug}")
    async def create_entity(
        slug: str,
        values: Dict[str, Any] = Body(default_factory=dict),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """POST /entity/{slug} -> create one row, return the EntityRecord.

        Writes through the audited adapter (tenant_id EXPLICIT == the verified claim, the
        WITH CHECK shape). tenant_id/kind/id are NEVER taken from the body. Degrade-never:
        no data plane -> a local-only echo (the run/write is never blocked).
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        manager = _entity_manager(tenant_id, token)
        try:
            record = manager.create(tenant_id, slug, values)
        except entities_mod.EntityError as exc:
            return _entity_error_response(exc)
        except entities_mod.TenantDataDenied as exc:
            return _tenant_denied_response(exc)
        return JSONResponse(status_code=200, content=record)

    @application.patch("/entity/{slug}/{record_id}")
    async def update_entity(
        slug: str,
        record_id: str,
        values: Dict[str, Any] = Body(default_factory=dict),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """PATCH /entity/{slug}/{id} -> merge ``values`` into one row, return the record.

        Tenant-scoped read-then-write through the adapter. A missing id for this tenant ->
        404 (EntityNotFound). tenant_id is server-derived; the id is the path segment.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        manager = _entity_manager(tenant_id, token)
        try:
            record = manager.update(tenant_id, slug, record_id, values)
        except entities_mod.EntityNotFound as exc:
            return _entity_error_response(exc, status_code=404)
        except entities_mod.EntityError as exc:
            return _entity_error_response(exc)
        except entities_mod.TenantDataDenied as exc:
            return _tenant_denied_response(exc)
        return JSONResponse(status_code=200, content=record)

    @application.patch("/entity/{slug}/{record_id}/publish")
    async def publish_entity(
        slug: str,
        record_id: str,
        body: PublishRequest = Body(...),
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """PATCH /entity/{slug}/{id}/publish body {published: bool} -> flip the PUBLISHED gate.

        THE L2 PUBLISH SEAM (spec 10 W1): sets the TOP-LEVEL ``published`` (+ ``published_at``)
        columns on a tenant_data row THE AUTHENTICATED TENANT OWNS, so the L2 anon public site
        (apps/public_site) can serve it (RLS ``public_catalog_read USING (published = true)``).

        Flow (mirrors PATCH /entity/{slug}/{id} EXACTLY): verify JWT -> tenant_id (NEVER from the
        path/body; tenant_id is the verified claim). The COLUMN update routes through the audited
        adapter's bind+guard seam (``EntityManager.set_published`` -> adapter.bind_session_tenant
        + adapter.write): the cross-tenant mirror raises ``TenantDataDenied`` BEFORE the DB, so
        tenant A can NEVER publish tenant B's row, and the UPDATE also carries
        ``WHERE id=%s AND tenant_id=%s`` (RLS + predicate, belt-and-braces). On publish:
        ``published_at = now()`` (the server clock); on unpublish: ``published=false`` and
        ``published_at`` is nulled. A missing id for this tenant -> 404 (EntityNotFound).
        DEGRADE-NEVER: no data plane -> a local-only echo (the flip is never blocked; the founder's
        gated prod path is where a real publish lands). tenant_id is server-derived; the id is the
        path segment. Credential-free.
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        manager = _entity_manager(tenant_id, token)
        try:
            record = manager.set_published(tenant_id, slug, record_id, body.published)
        except entities_mod.EntityNotFound as exc:
            return _entity_error_response(exc, status_code=404)
        except entities_mod.EntityError as exc:
            return _entity_error_response(exc)
        except entities_mod.TenantDataDenied as exc:
            return _tenant_denied_response(exc)
        return JSONResponse(status_code=200, content=record)

    @application.delete("/entity/{slug}/{record_id}")
    async def delete_entity(
        slug: str,
        record_id: str,
        authorization: Optional[str] = Header(default=None),
    ) -> JSONResponse:
        """DELETE /entity/{slug}/{id} -> remove one row (204). Idempotent + tenant-scoped.

        A cross-tenant delete is denied by the adapter mirror (403) before the DB; a
        missing id is a no-op (the row can never belong to another tenant anyway -- RLS +
        the tenant_id predicate).
        """
        tenant_id = _tenant_from_authorization(authorization)
        token = bearer_token_from_header(authorization)
        manager = _entity_manager(tenant_id, token)
        try:
            manager.delete(tenant_id, slug, record_id)
        except entities_mod.EntityError as exc:
            return _entity_error_response(exc)
        except entities_mod.TenantDataDenied as exc:
            return _tenant_denied_response(exc)
        return JSONResponse(status_code=204, content=None)


# --------------------------------------------------------------------------- #
# Response shaping helpers.
# --------------------------------------------------------------------------- #
def _result_to_view(result: Any) -> Dict[str, Any]:
    """Project a CapabilityResult (dataclass) to a JSON-safe dict, EXCLUDING any secret.

    The CapabilityResult contract guarantees no api_key field, but we still build the view
    explicitly (allowlist, not the raw object) so a future field addition can never leak a
    credential through this endpoint. Accepts a dataclass or a plain object/dict.
    """
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        data = dataclasses.asdict(result)
    elif isinstance(result, dict):
        data = dict(result)
    elif hasattr(result, "__dict__"):
        data = dict(vars(result))
    else:
        data = {}
    # Explicit allowlist of the view fields (spec A.2 CapabilityResult + ADR Phase B
    # AgentRunResult), credential-free. The agent fields (agent_id/agent_name/steps) are added
    # so an AgentRunResult serializes through the SAME projection; a CapabilityResult simply
    # lacks them (the ``if k in data`` filter omits absent keys). No secret field is ever here.
    view_fields = (
        "tenant_id",
        "capability",
        "kind",
        "pillar",
        "nucleus",
        "artifact",
        "score",
        "passed",
        "status",
        "model_used",
        "record_id",
        "persisted",
        "trace",
        "errors",
        # --- research-universe addition (spec_dashboard_roadmap W1); None on other kinds ---
        # The structured research_universe_report dict so the UI renders per-section cards.
        # Credential-free by construction (the orchestrator emits a pure data dict).
        "structured",
        # --- dual-output addition (mission DUAL2; founder directive 2026-06-21) ---
        # The dual-surface asset for a structured-generator capability: {machine_md, human_html,
        # media_slots, id, capability, frontmatter, real}. The UI (DualOutputFace) renders from the
        # TYPED ``media_slots`` (real <img>/<video>/<audio> or editable upload-fallback slots), NOT
        # from ``human_html`` -- that export string is forwarded but never injected into the DOM
        # (no dangerouslySetInnerHTML). None on 8F-build / universe / pesquisa kinds. A pure
        # projection -- credential-free.
        "dual_output",
        # --- agent-run additions (ADR Phase B); absent on a CapabilityResult ---
        "agent_id",
        "agent_name",
        "steps",
    )
    view = {k: data.get(k) for k in view_fields if k in data}
    # Belt-and-braces: never echo any key-shaped field even if a future result grows one.
    for secret_field in ("api_key", "credential", "secret", "key"):
        view.pop(secret_field, None)
    return view


def _render_universe_view(structured: Any, render_format: str) -> str:
    """Project a research_universe_report (the result's ``structured``) to MD or HTML.

    spec_dashboard_roadmap W1: delegates to cex_research_universe_contract.render_universe --
    the formal dual-projection that walks the universe contract ONCE (per-section cards +
    endpoint-status table + provenance), NOT the marketplace render. PURE + TOTAL: a
    non-universe / absent ``structured`` -> '' (the build capabilities have no structured
    report); a renderer import failure -> '' (degrade-never -- the run already succeeded, the
    render is an additive projection). NEVER raises, NEVER leaks a secret (the report is a
    pure data dict to begin with).
    """
    if not isinstance(structured, dict) or not structured:
        return ""
    try:
        import importlib

        deps._ensure_tools_on_path()
        contract = importlib.import_module("cex_research_universe_contract")
    except Exception:
        return ""
    try:
        rendered = contract.render_universe(structured)
    except Exception:
        return ""
    if isinstance(rendered, Mapping):
        return str(rendered.get(render_format, "") or "")
    return ""


def _is_universe_report(structured: Mapping[str, Any]) -> bool:
    """True iff a structured payload looks like a research_universe_report (PURE + TOTAL).

    A universe report carries the orchestrator's signature keys (seed_type + sections +
    endpoint_status); a marketplace product result does not. Used to route a persisted row to
    the correct renderer in /results. Conservative: requires the two most distinctive keys so
    a marketplace row is never misclassified."""
    if not isinstance(structured, Mapping):
        return False
    return "seed_type" in structured and "endpoint_status" in structured


def _preflight_agent_run(
    loop_runtime: Any,
    tenant_id: str,
    agent_id: str,
    options: Mapping[str, Any],
) -> None:
    """Run the CHEAP synchronous guards (enabled gate + OQ4 non-positive-budget) so a refusal is
    surfaced as a 4xx at POST /agent/runs time, not a silent background failure.

    REUSES the loop runtime's OWN guards verbatim (the SAME deny seam the loop would hit on the
    thread): the enabled-AGENT allowlist check (_rc._capability_enabled, keyed by agent_id) and
    Phase B's _budget_guard (a non-positive max_steps/budget refuses before any LLM call). These
    are pure + offline (no resolve, no build). A refusal raises CapabilityRefused -> the endpoint
    maps it to 400/403. Anything heavier (agent resolution) stays on the thread (its failure
    becomes the run's status=failed, visible via GET /agent/run/{id})."""
    tid = (tenant_id or "").strip()
    aid = (agent_id or "").strip()
    if not tid:
        raise loop_runtime.CapabilityRefused("missing_tenant", capability=aid)
    if not aid:
        raise loop_runtime.CapabilityRefused(
            "unresolved_capability", tenant_id=tid, detail="empty agent_id"
        )
    # The enabled-AGENT gate (deny-by-default; an empty allowlist denies every agent).
    if not loop_runtime._ra._rc._capability_enabled(tid, aid, options):
        raise loop_runtime.CapabilityRefused("capability_disabled", tenant_id=tid, capability=aid)
    # OQ4: a non-positive declared budget refuses BEFORE the run kicks (Phase B's guard).
    loop_runtime._ra._budget_guard(tid, aid, options)


def _runtime_accepts_kw(runtime: Any, func_name: str, kw: str) -> bool:
    """True iff ``runtime.<func_name>`` accepts the keyword ``kw`` (arch-council B2 guard).

    Lets a NEW kwarg (``db_reader``) be forwarded only to a runtime that supports it, so a
    test fake whose ``run_capability`` predates the param is left byte-identical (the SAME
    defensiveness the conditional ``inputs`` kwarg uses). DEGRADE-NEVER: any introspection
    surprise -> False (do not forward the kwarg). A **kwargs-accepting signature also returns
    True (it can absorb the kwarg)."""
    try:
        import inspect

        fn = getattr(runtime, func_name, None)
        if fn is None:
            return False
        sig = inspect.signature(fn)
        params = sig.parameters
        if kw in params:
            return True
        return any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
        )
    except Exception:
        return False


def _capability_refused_response(exc: Any) -> JSONResponse:
    """Map a runtime CapabilityRefused to a precise 4xx JSON error.

    ``frozen_kind`` and ``capability_disabled`` are authorization denials (403); the rest
    (missing_tenant, missing_credential, unresolved_capability, native_local_*) are client/
    config errors (400). The body is structured + secret-free.
    """
    reason = getattr(exc, "reason", "capability_refused")
    forbidden = reason in ("frozen_kind", "capability_disabled")
    status_code = 403 if forbidden else 400
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": "capability_refused",
                "reason": reason,
                "capability": getattr(exc, "capability", ""),
                "detail": getattr(exc, "detail", ""),
            }
        },
    )


def _compose_error_response(exc: Any) -> JSONResponse:
    """Map a deps.ComposeError (W2; PATCH /capabilities) to a precise status + secret-free body.

    unknown_action -> 400; not_declared -> 409 (FAIL-CLOSED: a capability must be DECLARED to be
    toggled); write_failed -> 500. The envelope is the SAME ``{"error": {type, reason, capability,
    detail}}`` every failure uses, so the frontend's single error path handles it identically.
    """
    reason = getattr(exc, "reason", "compose_error")
    status_code = {"unknown_action": 400, "not_declared": 409, "write_failed": 500}.get(
        reason, 400
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": "compose_error",
                "reason": reason,
                "capability": getattr(exc, "slug", ""),
                "detail": getattr(exc, "detail", ""),
            }
        },
    )


# --------------------------------------------------------------------------- #
# Dashboard-v2 entity + settings helpers.
# --------------------------------------------------------------------------- #
def _entity_manager(tenant_id: str, user_jwt: str) -> Any:
    """Build the tenant-scoped entity manager for this request.

    REUSES the audited adapter via the SAME tenant-session-factory seam the /results read
    uses (``deps.tenant_session_factory`` if registered). Degrade-never: no factory -> a
    LocalOnlyEntityManager (reads empty, writes no-op). The factory is resolved per-request
    so the bind + the query/write share one fresh session/transaction.
    """
    factory_provider = _entity_session_factory(tenant_id, user_jwt)
    return entities_mod.make_entity_manager(factory_provider)


def _entity_session_factory(tenant_id: str, user_jwt: str) -> Optional[Any]:
    """Resolve a ZERO-ARG DbSession factory bound to (tenant_id, user_jwt), or None.

    Same seam + contract as ``_build_session_factory`` (the /results read path): the
    per-environment provider ``deps.tenant_session_factory(tenant_id, user_jwt)`` returns a
    ZERO-ARG factory that mints a fresh DbSession per call (so the bind + the query/write
    share one transaction). We return that factory verbatim. None when unconfigured (->
    local-only). NEVER raises.
    """
    return _build_session_factory(tenant_id, user_jwt)


def _entity_error_response(exc: Any, *, status_code: int = 400) -> JSONResponse:
    """Map an entity EntityError (invalid slug / not found) to a structured 4xx.

    Body is the same ``{"error": {type, reason, detail}}`` envelope every failure uses, so
    the frontend's single error path (ApiClientError) handles it identically.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": "entity_error",
                "reason": getattr(exc, "reason", "entity_error"),
                "detail": getattr(exc, "detail", ""),
            }
        },
    )


def _tenant_denied_response(exc: Any) -> JSONResponse:
    """Map a TenantDataDenied (cross_tenant / missing_tenant) to a 403, secret-free.

    The reason token is surfaced (cross_tenant | missing_tenant | claim_bind_failed); the
    bound/target tenants are NOT echoed to the client (audit-only). A tenant-boundary deny
    is an authorization failure -> 403.
    """
    return JSONResponse(
        status_code=403,
        content={
            "error": {
                "type": "tenant_denied",
                "reason": getattr(exc, "reason", "cross_tenant"),
                "detail": "cross-tenant access denied",
            }
        },
    )


def _operator_email_from_authorization(authorization: Optional[str]) -> str:
    """Best-effort operator email from the VERIFIED claims (provenance copy only).

    Re-verifies the bearer token and reads ``email`` (Supabase Auth carries it). NEVER
    fails the request: a token without an email yields '' (the email is provenance display,
    not an identity decision -- the tenant is the only security-critical claim and is read
    separately, fail-closed). Returns '' on any issue.
    """
    try:
        token = bearer_token_from_header(authorization)
        claims = verify_supabase_jwt(token)
    except AuthError:
        return ""
    email = claims.get("email")
    return str(email).strip() if email else ""


def _read_tenant_results(
    tenant_id: str,
    user_jwt: str,
    capability: Optional[str],
    limit: int,
) -> tuple[List[Dict[str, Any]], str]:
    """Read recent tenant_data rows for this tenant via the SupabaseDataAdapter.

    Tenant-scoped by construction: the adapter binds the verified claim onto the session
    and refuses a cross-tenant read (TenantDataDenied) as defence-in-depth on top of RLS.
    The tenant_id passed to the adapter is the VERIFIED one (never client-supplied).

    Best-effort: if the data plane is not configured in this environment (no session
    factory / adapter import fails), returns ([], note) rather than 500 -- the result-read
    path is non-critical for the Phase-1 template gate. NEVER returns another tenant's data.
    """
    factory = _build_session_factory(tenant_id, user_jwt)
    if factory is None:
        return [], "tenant data plane not configured in this environment"
    try:
        from cexai.governance.data.adapter import SupabaseDataAdapter  # type: ignore
    except Exception as exc:  # adapter not importable here -> degrade, do not leak
        return [], "data adapter unavailable: %s" % str(exc)

    adapter = SupabaseDataAdapter(factory)
    session = factory()
    # Bind the verified claim so RLS applies on the (pooled) connection (spec A.5).
    verified_claims = {"tenant": tenant_id}
    adapter.bind_session_tenant(session, verified_claims)

    where = "WHERE tenant_id = %s"
    params: List[Any] = [tenant_id]
    if capability:
        where += " AND capability = %s"
        params.append(capability)
    sql = (
        "SELECT id, capability, kind, created_at FROM tenant_data "
        + where
        + " ORDER BY created_at DESC LIMIT %s"
    )
    params.append(limit)
    raw = adapter.query(session, tenant_id, sql, params)
    return _normalize_rows(raw), ""


def _read_tenant_results_rendered(
    tenant_id: str,
    user_jwt: str,
    capability: Optional[str],
    limit: int,
    render_format: str,
) -> tuple[List[Dict[str, Any]], str]:
    """Like ``_read_tenant_results`` but ALSO fetches each row's ``payload`` and attaches a
    ``render`` projection (CAPABILITY_LAYER W1; the ?render_format=md|html path).

    SAME tenant scoping as the summary read: the adapter binds the VERIFIED claim and refuses
    a cross-tenant read; tenant_id is the verified one (never client-supplied). The ONLY
    difference is the SELECT carries ``payload`` so each row can be projected to MD (canonical)
    or HTML (derivative). Best-effort + degrade-never: no data plane -> ([], note).
    """
    factory = _build_session_factory(tenant_id, user_jwt)
    if factory is None:
        return [], "tenant data plane not configured in this environment"
    try:
        from cexai.governance.data.adapter import SupabaseDataAdapter  # type: ignore
    except Exception as exc:  # adapter not importable here -> degrade, do not leak
        return [], "data adapter unavailable: %s" % str(exc)

    adapter = SupabaseDataAdapter(factory)
    session = factory()
    adapter.bind_session_tenant(session, {"tenant": tenant_id})

    where = "WHERE tenant_id = %s"
    params: List[Any] = [tenant_id]
    if capability:
        where += " AND capability = %s"
        params.append(capability)
    sql = (
        "SELECT id, capability, kind, created_at, payload FROM tenant_data "
        + where
        + " ORDER BY created_at DESC LIMIT %s"
    )
    params.append(limit)
    raw = adapter.query(session, tenant_id, sql, params)
    return _project_rendered_rows(raw, render_format), ""


def _project_rendered_rows(raw: Any, render_format: str) -> List[Dict[str, Any]]:
    """Project query rows (id, capability, kind, created_at, payload) into result dicts that
    carry a ``render`` field (the MD or HTML projection). PURE + TOTAL: a row without a usable
    payload still returns its summary with ``render: ''`` (never 500s on a shape surprise)."""
    out: List[Dict[str, Any]] = []
    if raw is None:
        return out
    try:
        rows = list(raw)
    except TypeError:
        return out
    for row in rows:
        if isinstance(row, dict):
            base = {
                "id": _jsonable(row.get("id")),
                "capability": _jsonable(row.get("capability")),
                "kind": _jsonable(row.get("kind")),
                "created_at": _jsonable(row.get("created_at")),
            }
            payload = row.get("payload")
        elif isinstance(row, (list, tuple)) and len(row) >= 5:
            base = {
                "id": _jsonable(row[0]),
                "capability": _jsonable(row[1]),
                "kind": _jsonable(row[2]),
                "created_at": _jsonable(row[3]),
            }
            payload = row[4]
        else:
            continue
        base["render"] = _render_payload(payload, render_format)
        out.append(base)
    return out


def _render_payload(payload: Any, render_format: str) -> str:
    """Resolve the MD or HTML projection for one row's payload (PURE + TOTAL).

    Resolution order (cheapest first):
      1. a pre-rendered projection already in the payload: ``payload['html']`` for html, or
         ``payload['artifact']`` (the canonical MD the pipeline persists) for md.
      2. otherwise re-render from ``payload['structured']`` via cex_output_contract.render
         (degrade-never: if the renderer import fails or there is no structured data, '' ).
    Returns '' when nothing projectable is present -- never raises.
    """
    payload = _coerce_payload(payload)
    if not isinstance(payload, dict):
        return ""
    if render_format == "html":
        pre = payload.get("html")
        if isinstance(pre, str) and pre.strip():
            return pre
    else:  # md
        pre = payload.get("artifact")
        if isinstance(pre, str) and pre.lstrip().startswith("---"):
            return pre
    # Fall back to re-rendering from the structured fields.
    structured = payload.get("structured")
    # spec_dashboard_roadmap W1: a persisted research_universe row's structured block is a
    # research_universe_report (carries seed_type + endpoint_status), NOT a marketplace
    # product result. Detect that shape and project it via render_universe (the correct dual
    # renderer) instead of the marketplace render. Degrade-never -> '' on any failure.
    if isinstance(structured, dict) and _is_universe_report(structured):
        return _render_universe_view(structured, render_format)
    if not isinstance(structured, dict) or not structured:
        # A plain {artifact, meta} row with no structured block: surface the raw artifact for
        # md (it is the canonical text), else nothing for html.
        artifact = payload.get("artifact")
        if render_format == "md" and isinstance(artifact, str):
            return artifact
        return ""
    try:
        import importlib

        # The renderer lives in _tools; ensure it is importable (idempotent) the SAME way the
        # runtime/registry imports are resolved (deps._ensure_tools_on_path).
        deps._ensure_tools_on_path()
        oc = importlib.import_module("cex_output_contract")
    except Exception:
        # If the renderer is not importable here, surface the raw artifact for md, nothing for
        # html (degrade-never -- the read path never 500s on a missing optional renderer).
        artifact = payload.get("artifact")
        return artifact if (render_format == "md" and isinstance(artifact, str)) else ""
    contract = getattr(oc, "PESQUISA_PRODUTO_CONTRACT", {})
    rendered = oc.render(structured, contract)
    return str(rendered.get(render_format, "") or "")


def _coerce_payload(payload: Any) -> Any:
    """Coerce a payload that may arrive as a JSON string (driver-dependent) into a dict."""
    if isinstance(payload, str):
        try:
            import json

            return json.loads(payload)
        except Exception:
            return {}
    return payload


def _build_session_factory(tenant_id: str, user_jwt: str) -> Optional[Any]:
    """Resolve a DbSession factory for the tenant's own Supabase, or None if unconfigured.

    Production wires this to a pooled psycopg/asyncpg connection bound to the tenant pooler
    (spec C.2). In this Phase-1 build no concrete driver is shipped here, so this returns
    None unless an environment hook provides one. Kept as a seam so T5 can inject a real
    factory without touching the endpoint logic. NEVER raises.
    """
    # Seam: an environment may register a factory provider on deps for local integration.
    provider = getattr(deps, "tenant_session_factory", None)
    if provider is None:
        return None
    try:
        return provider(tenant_id, user_jwt)
    except Exception:
        return None


def _normalize_rows(raw: Any) -> List[Dict[str, Any]]:
    """Coerce a driver-native query result into a list of plain JSON-able dicts.

    Accepts a list of dicts, a list of (id, capability, kind, created_at) tuples, or an
    iterable thereof. Anything unrecognized yields []. Defensive so the endpoint never
    500s on a driver-shape surprise.
    """
    out: List[Dict[str, Any]] = []
    if raw is None:
        return out
    try:
        rows = list(raw)
    except TypeError:
        return out
    for row in rows:
        if isinstance(row, dict):
            out.append({str(k): _jsonable(v) for k, v in row.items()})
        elif isinstance(row, (list, tuple)) and len(row) >= 4:
            out.append(
                {
                    "id": _jsonable(row[0]),
                    "capability": _jsonable(row[1]),
                    "kind": _jsonable(row[2]),
                    "created_at": _jsonable(row[3]),
                }
            )
    return out


def _jsonable(value: Any) -> Any:
    """Best-effort scalar coercion for JSON (datetimes/UUIDs -> str)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


# The module-level ASGI app uvicorn serves: ``uvicorn apps.dashboard_api.main:app``.
app = create_app()
