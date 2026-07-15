---
kind: feature_template
feature_name: secrets
vertical: 16_company_stack
round_added: 23
pillars: [P09, P11]
adr_019_packages: [governance/, foundation/]
feature_dependencies: []
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in secrets audit logs."
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
    description: "Drives compliance posture defaults."
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
    description: "Drives secrets-policy strictness defaults."
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
    description: "UI language for secrets dashboard."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: vault_provider
    type: enum
    description: "Secret vault backend."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["supabase_vault", "aws_secrets_manager", "gcp_secret_manager", "hashicorp_vault", "azure_key_vault", "1password_connect", "doppler"]
    context_hints: [brand_config.vault_provider]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: secret_rotation_days
    type: int
    description: "Default rotation cadence for rotatable secrets."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.secret_rotation_days]
    constraints: {minimum: 7, maximum: 365}
    default_filler_strategy: use_default_value
    required: false
    default_value: 90
    rebind_allowed: true
  - name: secret_audit_retention_days
    type: int
    description: "Retention for secrets-access audit log."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.secret_audit_retention_days]
    constraints: {minimum: 30, maximum: 3650}
    default_filler_strategy: use_default_value
    required: false
    default_value: 365
    rebind_allowed: true
---

# Feature Template: Secrets Management

**Purpose**: a typed wrapper around the deployer's chosen secret vault, providing CEXAI-consistent access patterns + audit + rotation policy. Sits BENEATH every feature that uses external API keys, OAuth tokens, encryption keys.

---

## Architecture

```
CEXAI code -> cexai.foundation.secrets.get(name) -> vault adapter -> deployer's vault backend
```

The wrapper is intentionally thin -- it does NOT re-implement vault logic. It DOES:
1. Centralize the access path (no scattered env-var reads).
2. Audit every read (event_type: `secret_access`).
3. Enforce naming conventions (per-project, per-environment).
4. Handle rotation gracefully (cache invalidation).

---

## Naming convention

Secrets follow the pattern `<project_id>_<environment>_<purpose>`:

```
mybrand_prod_supabase_service_role
mybrand_prod_ayrshare_api_key
mybrand_prod_openai_api_key
mybrand_dev_supabase_service_role
mybrand_staging_stripe_secret_key
```

Deployer enforces via vault-provider conventions (Supabase has flat namespace; HashiCorp Vault has hierarchical paths).

---

## Vault adapters

Each `vault_provider` value has an adapter:

| Provider | Adapter notes |
|----------|--------------|
| `supabase_vault` | Read via `vault.decrypted_secrets` table; requires DB access |
| `aws_secrets_manager` | Read via AWS SDK; IAM-controlled |
| `gcp_secret_manager` | Read via GCP SDK; service account |
| `hashicorp_vault` | Read via HTTP API + token |
| `azure_key_vault` | Read via Azure SDK |
| `1password_connect` | Read via Connect server |
| `doppler` | Read via CLI or API |

Deployer implements adapter under `cexai/foundation/secrets/adapters/<provider>.py`.

---

## Rotation policy

For rotatable secrets (API keys, OAuth tokens), the rotation cron runs at `secret_rotation_days` cadence:

1. Read current secret + metadata.
2. Provision new secret with the external provider.
3. Update secret in vault (CREATE new version; do not overwrite).
4. Invalidate any cached copies in CEXAI processes.
5. Emit `audit_event` (event_type: `secret_rotation_attempt | secret_rotation_success | secret_rotation_failure`).

Non-rotatable secrets (e.g., long-lived enterprise OAuth refresh tokens) are tagged `rotation_strategy: manual` and excluded from the cron.

---

## Audit pattern

Every secret READ emits `audit_event`:
- `event_type: secret_access`
- `subject.secret_name: <name>`
- `subject.caller_module: <module>` -- which CEXAI feature read it
- `outcome: success | failure_not_found | failure_unauthorized | failure_vault_error`
- `retention_class: long_3y` (sensitive; default longer than standard)

Read frequency: avoid logging EVERY read in hot paths (would spam audit). Use sampling for hot reads OR aggregate (log once per minute per (secret_name, caller_module)).

---

## Compliance posture defaults

Driven by `brand_niche`:

| Niche signal | Default secret_audit_retention_days | Default rotation_days |
|--------------|--------------------------------------|-----------------------|
| fintech, healthcare, govtech | 3650 (10y) | 30 |
| ecommerce, retail | 365 | 90 |
| saas, agency | 365 | 90 |
| creator, hobby | 90 | 180 |

Deployer overrides per `brand_config.yaml`. Defaults are starting points, not legal advice.

---

## Anti-patterns (security-critical)

| Anti-pattern | Why fatal |
|--------------|-----------|
| Hardcoding secrets in `.env` checked into git | Secret leak; rotation required immediately |
| Secrets in environment variables on hosted SPA platforms | Exposed in build logs and crash reports |
| Secrets in artifact frontmatter (e.g., template open_vars) | Secrets are NOT open_vars; they go in vault. open_vars reference secret NAMES, not VALUES. |
| Bulk-deleting audit events | Compliance violation; impossible to forensic-trace incidents |
| Sharing the same secret across environments | Compromise in dev contaminates prod |
| Storing secrets in browser localStorage | Browser env is hostile; secrets must be server-side |

---

## Integration contracts

- Provides to: every feature that needs API keys / tokens / encryption keys.
- `feature_publishing.md` reads publishing provider's service-role JWT.
- `feature_erp_integration.md` reads ERP API keys.
- `feature_marketplace_integration.md` reads marketplace OAuth refresh tokens.
- `feature_messaging.md` reads channel-provider API keys.
- `feature_brand_vault.md` MAY use vault for asset-source credentials (e.g., Cloudinary API key).
- Audit via `kc_audit_event.md` with `retention_class: long_3y` (always sensitive).

---

## Out of scope

- HSM integration (deployer adopts directly via vault_provider that supports HSM-backed keys).
- Customer secret storage (this template is INFRA secrets; customer secrets belong to a separate `feature_customer_vault.md` deferred R24+).
- Cross-region secret replication (deployer's vault provider responsibility).
- Secret leak detection in code (deferred R24+; integrate with TruffleHog/gitleaks externally).
