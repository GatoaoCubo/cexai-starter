---
kind: feature_template
feature_name: publishing
vertical: 16_company_stack
round_added: 22
pillars: [P04, P11, P12]
adr_019_packages: [tools/, governance/]
feature_dependencies: [feature_content_factory]
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in published posts (author tag, page name)."
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
    description: "Informs cross-posting strategy."
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
    description: "Drives platform-specific copy adjustments."
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
    description: "Language for default copy."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: publishing_provider
    type: enum
    description: "Multi-channel publisher provider (e.g., Ayrshare, Buffer, Hootsuite, custom)."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["ayrshare", "buffer", "hootsuite", "publer", "later", "custom"]
    context_hints: [brand_config.publishing_provider]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: enabled_channels
    type: list[str]
    description: "Channels to publish to (e.g., ['ig_feed', 'ig_reels', 'fb', 'tiktok', 'linkedin'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.enabled_channels]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: cron_schedule
    type: str
    description: "Cron expression for the hourly-style publishing job (e.g., '35 * * * *' = every hour at :35)."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.cron_schedule]
    constraints: {pattern: "^[0-9*,-/]+( [0-9*,-/]+){4}$"}
    default_filler_strategy: use_default_value
    required: false
    default_value: "35 * * * *"
    rebind_allowed: true
---

# Feature Template: Publishing

**Purpose**: a multi-channel publisher that reads approved content_library rows and dispatches them to social channels + blog via a configured provider. Includes cron scheduling, retry, audit log.

---

## Architecture

```
content_library (approved=true, publish_status='pending')
  -> cron job (cron_schedule open_var)
  -> publish_due action: fetch ready rows where scheduled_at <= now()
  -> per-row: call publishing_provider API to post
  -> on success: update publish_status='published' + record provider_job_id
  -> on failure: update publish_status='failed' + log error; retry policy configurable
  -> emit audit_event with operator + row + outcome
```

---

## Edge functions / API surface

| Function | Purpose | Notes |
|----------|---------|-------|
| `publish_due` | Cron-triggered; processes ready rows. | The main hourly job. |
| `publish_one` | Manual publish of a single row by ID. | Used from admin UI. |
| `dry_run` | Same as publish_due but does not call provider API; returns plan. | Useful for sanity-check before scaling. |
| `status` | Query provider for the post's live status. | E.g., for engagement-metric backfill. |
| `cancel_jobs` | Batch DELETE published posts from provider. | See provider-specific caveats below. |
| `retry_failed` | Re-run rows with `publish_status='failed'`. | Configurable backoff. |

The deployer implements these as serverless functions (Supabase Edge Functions, AWS Lambda, Cloudflare Workers, etc.).

---

## Cron job

Default schedule: `35 * * * *` (every hour at :35). The schedule is a deployer-config `cron_schedule` open_var; deployers with denser publishing cadences pick `*/10 * * * *` or similar.

Cron job calls the deployer's BaaS HTTP endpoint with a service-role JWT. The JWT is stored in the BaaS's secret vault (e.g., Supabase `vault.decrypted_secrets`).

Each cron firing emits a heartbeat row to `content_cron_heartbeat` with job name, fired_at, request_id, result, error. This is the OBSERVABILITY surface required by Article V.

---

## Channel-specific caveats

Different platforms have different API behaviors. The template encodes universal patterns; deployer adds provider-specific guards.

| Channel | Caveat |
|---------|--------|
| `ig_stories` | Many providers fan STORIES posts as feed reels for unconfigured accounts, producing visible duplicates. Disable this channel until a platform-specific smoke test confirms a Story actually lands in the Story tray. |
| `tiktok` | TikTok API typically does NOT support remote DELETE. A post once published cannot be retracted via provider. Plan accordingly (e.g., approval gate is the LAST chance to revoke). |
| `linkedin` | Personal vs Company page distinction matters. The provider configuration must specify which destination. |
| `facebook` | Page tokens expire periodically (typically 60 days). Deployer refreshes via OAuth flow. |
| `youtube_shorts` | Shorts require vertical 9:16 aspect ratio; horizontal videos auto-cropped or rejected by platform. |

---

## Retry policy

| Failure mode | Action |
|--------------|--------|
| Provider rate-limit (429) | Exponential backoff; retry up to 3 times. |
| Provider auth expired (401) | Mark `publish_status='failed'` with reason; notify admin via audit log; no automatic retry. |
| Provider transient (5xx) | Linear backoff; retry up to 5 times. |
| Caption too long | Mark `publish_status='failed'`; surface in admin for editing. |
| Asset not found (404 on storage_url) | Mark `publish_status='failed'`; admin re-uploads. |

---

## Audit log

Every publishing action emits an `audit_event` (per FR-012 in vertical 15 -- the kind is shared across vertical 15 + 16; PROPOSED for Round 22 kinds_meta registration).

```yaml
audit_event:
  iso_timestamp: <ISO 8601>
  event_type: publish_attempt | publish_success | publish_failure | retry_attempt | cancel_attempt
  content_library_row_id: <uuid>
  channel: <channel>
  provider_response: <jsonb>
  operator_identity: <user_id> | "system_cron"
```

The audit table is append-only. Rotation is deployer concern.

---

## Integration contracts

- Consumes from: `feature_content_factory.md` (approved content_library rows).
- Provides to: deployer's analytics layer (audit_event feed).
- Provider integration via deployer-chosen API (`publishing_provider` open_var).
- Authentication via service-role JWT stored in BaaS secret vault.
- Cron via BaaS-native scheduler (pg_cron for Supabase; equivalent on other BaaS).

---

## Out of scope

- Engagement metrics backfill (use `status` action manually; full analytics in R23 `feature_analytics.md`).
- A/B testing variants at publish time (R23 `feature_experiments.md`).
- Direct image/video upload to provider (assumes assets are already on accessible storage URLs).
- Email newsletter publishing (use a dedicated newsletter provider; R23 `feature_newsletter.md`).
- Affiliate link insertion (deployer extension).
