---
kind: feature_template
feature_name: api_keys_management
vertical: 17_saas_stack
round_added: 25
pillars: [P04, P09, P11]
adr_019_packages: [tools/, governance/]
feature_dependencies: [feature_admin_console, feature_subscription_lifecycle]
brand_niche_constraints:
  - allow: [saas, api_platform, dev_tools, b2b_saas]
  - warn: [b2c_consumer, ecommerce, agency, services]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in API key management UI."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_name]
    constraints: {min_length: 1, max_length: 80}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: brand_niche
    type: str
    description: "Determines scope vocabulary."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_niche]
    constraints: {min_length: 1, max_length: 200}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: target_audience
    type: str
    description: "API audience (developers vs power users vs operators)."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.target_audience]
    constraints: {min_length: 3, max_length: 150}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: primary_language
    type: enum
    description: "API docs + UI language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: key_prefix
    type: str
    description: "API key prefix to identify keys at a glance (e.g., 'sk_live_', 'sb_publishable_', 'gh_pat_')."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.key_prefix]
    constraints: {min_length: 2, max_length: 16, pattern: "^[a-z][a-z0-9_]*_$"}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: max_keys_per_user
    type: int
    description: "Maximum API keys a user can have active simultaneously."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.max_keys_per_user]
    constraints: {minimum: 1, maximum: 100}
    default_filler_strategy: use_default_value
    required: false
    default_value: 5
    rebind_allowed: true
  - name: key_expiry_days_default
    type: int
    description: "Default expiry for new API keys (days)."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.key_expiry_days_default]
    constraints: {minimum: 1, maximum: 3650}
    default_filler_strategy: use_default_value
    required: false
    default_value: 365
    rebind_allowed: true
  - name: supported_scopes
    type: list[str]
    description: "Permission scopes assignable to keys (e.g., ['read', 'write', 'admin', 'billing'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.supported_scopes]
    constraints: {min_items: 1}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["read", "write"]
    rebind_allowed: true
---

# Feature Template: API Keys Management

**Purpose**: developer-facing API access via personal access tokens (PATs). Users create, view, rotate, scope, and revoke keys. Each key is bound to a user + workspace + permission scopes.

---

## Architecture

```
user navigates to /admin/api-keys (or developer portal)
  -> create key flow: pick scopes + expiry -> generate key (irreversible -- shown once)
  -> store key_hash (NEVER plaintext) + metadata in api_keys table
  -> user copies key (or saves to their secret vault)
  -> API request: client sends key in Authorization header
  -> server: hash incoming key + lookup -> if match + not expired + not revoked -> proceed
  -> emit usage event (per feature_usage_metering.md)
  -> emit audit_event with key_id (NEVER key value)
```

---

## Data schema

```yaml
table: api_keys
columns:
  - id (uuid)                         # internal key identifier (safe to log)
  - user_id (FK to users)
  - workspace_id (FK; nullable for user-level keys)
  - name (str)                        # user-provided label, e.g., "production-server"
  - key_prefix (str)                  # first 8 chars of plaintext (e.g., "sk_live_abc12345")
  - key_hash (str)                    # SHA-256 (or argon2) hash of the plaintext key
  - scopes (text[])                   # subset of supported_scopes open_var
  - created_at (iso_datetime)
  - last_used_at (iso_datetime; nullable)
  - expires_at (iso_datetime)
  - revoked_at (iso_datetime; nullable)
  - revoked_by_user_id (FK; nullable)
  - revoked_reason (str; nullable)
```

Critical: `key_hash` MUST be hashed; `key_prefix` is the human-readable identifier for the user to identify keys ("the one starting with sk_live_abc12345..."). The full plaintext key is shown ONLY ONCE at creation.

---

## Key generation

```
plaintext_key = key_prefix + base64url(crypto.randomBytes(32))
key_hash = sha256(plaintext_key)
key_prefix_visible = plaintext_key[:8 + len(key_prefix)]
```

Example output: `sk_live_abc12345def67890ghi...` (40 char total).

The plaintext is returned ONCE in the create-key response. After that, only `key_prefix_visible` is shown in UI.

---

## Authentication flow

```python
# Pseudo-Python (spec only)
def authenticate(request):
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        return 401
    plaintext = header[7:]  # strip "Bearer "
    key_hash = sha256(plaintext)
    key_row = db.api_keys.find_by(key_hash=key_hash)
    if not key_row:
        return 401
    if key_row.revoked_at or now() > key_row.expires_at:
        return 401
    request.user = key_row.user
    request.workspace = key_row.workspace
    request.scopes = key_row.scopes
    db.api_keys.update(id=key_row.id, last_used_at=now())  # async
    return 200
```

---

## Scopes + permission check

Each operation declares required scope. Example:

| Endpoint | Required scope |
|----------|---------------|
| `GET /api/v1/items` | `read` |
| `POST /api/v1/items` | `write` |
| `DELETE /api/v1/items/:id` | `write` (or `admin`) |
| `GET /api/v1/users` | `admin` |
| `GET /api/v1/billing` | `billing` |

A key with `scopes: ["read"]` accessing `POST /api/v1/items` is rejected with 403.

---

## Key rotation

| Pattern | When |
|---------|------|
| **Manual rotation** | User clicks "rotate" in UI; new key generated; old key still valid for `grace_window_hours` (default 24h); after grace, old key revoked automatically. |
| **Auto rotation** | At `expires_at`, key revokes itself; user notified via `feature_messaging.md` ahead of expiry (default 14d + 1d warnings). |
| **Forced rotation** | Admin can revoke any key; user gets notification. |

---

## Revocation

| Reason | Behavior |
|--------|----------|
| User-initiated | Mark `revoked_at` + `revoked_by_user_id` |
| Admin-initiated | Same + `revoked_reason` populated |
| Auto-expiry | Mark `revoked_at = expires_at` |
| Security incident | Admin bulk-revoke via UI / SQL |

Revoked keys remain in DB for audit (NEVER hard-deleted). New requests with revoked keys: 401 + log to audit.

---

## Audit pattern

Every action emits `audit_event`:
- `api_key_created` (subject: key_id; NEVER plaintext)
- `api_key_used` (sampled; 1 in 100 high-frequency keys to avoid spam)
- `api_key_rotated`
- `api_key_revoked` (always)
- `api_key_expired_auto_revoke`

Per ADR 022 + `kc_audit_event.md` -- `retention_class: long_3y` (security-relevant).

---

## Tier gating integration

API key quotas per tier (from `feature_tier_gating.md`):

```yaml
tier_feature_matrix:
  free:
    max_active_keys: 2
    available_scopes: ["read"]
  pro:
    max_active_keys: 10
    available_scopes: ["read", "write"]
  enterprise:
    max_active_keys: unlimited
    available_scopes: ["read", "write", "admin", "billing"]
```

Override the `max_keys_per_user` + `supported_scopes` open_vars per tier.

---

## Integration contracts

- Consumes from: `feature_admin_console.md` (user identity + workspace context).
- Consumes from: `feature_subscription_lifecycle.md` (current tier).
- Consumes from: `feature_tier_gating.md` (per-tier limits + available scopes).
- Provides scopes to: each API endpoint (permission check before action).
- Provides usage events to: `feature_usage_metering.md` (api_call unit).
- Audit via `kc_audit_event.md` with `retention_class: long_3y`.
- Notifications via `feature_messaging.md` (expiry warnings, rotation events).

---

## Out of scope

- OAuth 2.0 client credentials flow (separate from PATs; deferred R26+ if needed for third-party integrations).
- Service account keys (machine-to-machine without user identity) -- deferred.
- IP-restricted keys -- deferred R26+ `feature_ip_allowlist.md`.
- Per-endpoint custom rate limits -- belongs to API gateway layer, not key management.
