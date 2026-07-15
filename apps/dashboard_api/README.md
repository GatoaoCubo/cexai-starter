# CEXAI Dashboard API

The employee dashboard **backend** for the CEXAI hybrid-local product
(mission `CEXAI_PRODUCT_RUNTIME`, Phase 1, task T3). A thin FastAPI service over the
headless runtime (`_tools/cex_run_capability.py`) and the capability catalog
(`_tools/cex_capability_registry.py`). Implements **section B** of
`_docs/compiled/spec_cexai_product_build_v1.md` (the dashboard <-> backend contract).

## What it does

An employee logs in via **Supabase Auth** (the JWT carries `tenant_id` under
`app_metadata`). The frontend (Next.js, built separately) sends that JWT on every
request. This backend:

1. **Verifies** the Supabase JWT and extracts `tenant_id` from the **verified claim**.
2. Lists the tenant's **organic capability cards** (overlay-driven, from the registry).
3. Runs a capability for that tenant via `run_capability(...)` and returns the result.
4. Reads the tenant's recent artifacts from **their** Supabase, tenant-scoped via the
   `SupabaseDataAdapter` (RLS-enforced).

## The #1 security rule

> **`tenant_id` is resolved ONLY from the verified JWT.**

A client **cannot** set `tenant_id`. The `POST /capability/run` body has no `tenant_id`
field at all, and any stray `tenant_id` / `credential` / `api_key` key inside `options`
is **stripped** server-side before the runtime is called. Auth is **fail-closed**: a
missing or invalid token returns `401` with no fallback identity. The LLM credential is
assembled **server-side only** -- the browser never sends one.

Defence-in-depth: result reads go **through the adapter** under the verified tenant, so
RLS remains the authoritative boundary even if the API layer had a bug.

## Endpoints

| Method + path | Auth | Purpose |
|---------------|------|---------|
| `GET /healthz` | none | Liveness (never touches the runtime). |
| `GET /capabilities` | JWT | The tenant's enabled capability cards (organic, overlay-derived). |
| `POST /capability/run` | JWT | Body `{capability, intent, options?}` -> run for the JWT's tenant -> `CapabilityResult` JSON. |
| `GET /results?capability=` | JWT | The tenant's recent artifacts (tenant-scoped via the adapter). |

All authed requests carry `Authorization: Bearer <supabase_jwt>`.

Error envelope (structured, secret-free):
`{"error": {"type", "reason", "detail"}}` -- `401` auth, `400/403` capability refused,
`503` runtime/registry not yet built.

## Run it

Install deps (the repo already ships compatible versions of fastapi/httpx/pyjwt):

```bash
pip install -r apps/dashboard_api/requirements.txt
```

Configure the environment (server-side only -- never expose these to the browser):

```bash
# JWT verification (HS256 with the Supabase project's JWT secret -- the default scheme)
export SUPABASE_JWT_SECRET="<your supabase project jwt secret>"
# Optional: audience (defaults to "authenticated"; set "" to disable the check)
export SUPABASE_JWT_AUD="authenticated"
# Optional: asymmetric verify via the project JWKS instead of the shared secret
# export SUPABASE_JWKS_URL="https://<ref>.supabase.co/auth/v1/.well-known/jwks.json"

# Dev credential for capability runs (a BYO API key used when a tenant has no stored key)
export CEXAI_DASHBOARD_DEV_API_KEY="<an anthropic/openai api key for local dev>"
export CEXAI_DASHBOARD_DEV_PROVIDER="anthropic"   # optional (default: anthropic)

# CORS (defaults to http://localhost:3000 for the Next.js dev server)
# export CEXAI_DASHBOARD_CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

Start the server with **uvicorn** (run from the repo root so the package path resolves):

```bash
uvicorn apps.dashboard_api.main:app --reload --port 8000
```

Then, from the frontend (or `curl`):

```bash
curl -H "Authorization: Bearer $SUPABASE_JWT" http://localhost:8000/capabilities

curl -X POST http://localhost:8000/capability/run \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{"capability": "research", "intent": "scan EdTech pricing"}'
```

## Tests

Offline TestClient tests (no real LLM, no real DB) prove the security contract:

```bash
python -m pytest apps/dashboard_api/tests/ -q
```

They assert:
- `/capability/run` scopes by the **JWT's** `tenant_id`, not the body.
- a body-supplied `tenant_id` is **ignored**.
- **401** without a token (fail-closed).
- `/capabilities` returns the registry cards.
- **cross-tenant is impossible** -- the tenant comes only from the verified JWT.

## Parallel-build note

`run_capability` and `cex_capability_registry` are built **in parallel** with this
service. This backend imports them **lazily** (`deps.py`) and codes against the
build-spec contract only, so the app starts even if either is mid-build (a missing
dependency surfaces as `503`, never a startup `ImportError`).

## Open questions (carried from the spec)

- **OQ1** transport/stack (this is the FastAPI option from the spec OQ1).
- **OQ2** `native_local` headless credential is unresolved; Phase 1 proves the
  `byo_api_key` path. The dashboard run path uses a server-side BYO key.
- **OQ5** key custody: the `service_role` / provider key is held server-side only and
  never reaches the browser.
