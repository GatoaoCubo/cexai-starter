---
kind: feature_template
feature_name: messaging
vertical: 16_company_stack
round_added: 23
pillars: [P03, P11]
adr_019_packages: [tools/, foundation/]
feature_dependencies: [feature_crm]
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display name in outgoing messages."
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
    description: "Drives message tone bias."
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
    description: "Default audience descriptor; per-message override possible."
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
    description: "Default message language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: composition_strategy
    type: enum
    description: "How messages are composed for outbound."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["template_substitution", "llm_personalized", "hybrid"]
    context_hints: [brand_config.composition_strategy]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "template_substitution"
    rebind_allowed: true
  - name: llm_model_class
    type: str
    description: "Model class for LLM-personalized composition (resolved via cexai.foundation.invocation.router)."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.llm_model_class]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "composer"
    rebind_allowed: true
  - name: rate_limit_per_minute
    type: int
    description: "Outbound rate cap to avoid provider throttling."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.rate_limit_per_minute]
    constraints: {minimum: 1, maximum: 1000}
    default_filler_strategy: use_default_value
    required: false
    default_value: 30
    rebind_allowed: true
---

# Feature Template: Messaging

**Purpose**: outbound message composition + dispatch across channels (email, WhatsApp, SMS, etc.) with template-substitution (free, fast) AND LLM-personalized (rich, costed) modes.

---

## Architecture

```
trigger (CRM event | scheduled campaign | manual operator)
  -> resolve recipient (crm_contact id)
  -> select template (sales_message_templates)
  -> compose:
     - if composition_strategy == template_substitution: regex replace placeholders
     - if composition_strategy == llm_personalized: router.dispatch(prompt, model_class)
     - if composition_strategy == hybrid: substitute first, LLM polishes
  -> rate-limit gate (rate_limit_per_minute)
  -> dispatch via channel-specific provider
  -> log sales_messages row + emit audit_event
```

---

## Composition modes

| Mode | Cost | Latency | Personalization | When to use |
|------|------|---------|----------------|-------------|
| `template_substitution` | Free | < 50ms | Low (placeholder fills only) | Bulk campaigns; high volume |
| `llm_personalized` | LLM cost per message | ~2-5s | High (full re-write per contact) | High-stakes outreach; sales pitches |
| `hybrid` | LLM cost only on polish | ~1-3s | Medium (substitute + LLM polish) | Balance volume + personalization |

The deployer selects per campaign. The Sales Assistant UI (`feature_admin_console.md` `sales` module) lets operators choose.

---

## Template substitution

Templates in `sales_message_templates` use `{{placeholder}}` syntax. Substitution is REGEX REPLACE -- no LLM call. Fast + free.

Standard placeholders:
- `{{display_name}}` -- contact display name (company OR person; NEVER assume person)
- `{{first_name}}` -- ONLY if explicitly populated; otherwise NEVER use
- `{{city}}`, `{{region}}`, `{{segment}}` -- contact attributes
- `{{brand_name}}` -- from open_var
- `{{product_url}}`, `{{kit_url}}` -- when promoting catalog
- `{{cta_url}}` -- campaign-specific CTA

Missing placeholder values default to `""` (silent) OR skip the recipient (deployer config). Recommendation: skip; sending malformed messages erodes trust.

---

## LLM-personalized composition

When `composition_strategy: llm_personalized`, the message body is generated per recipient:

```python
# Pseudo (spec only)
prompt = build_prompt(
    contact=contact,
    template_intent=template.title,
    products_referenced=[...],
    pricing_summary=pricing_summary_for(contact),
    brand_voice=brand_voice_open_var,
    primary_language=primary_language_open_var,
)
final_body = router.dispatch(prompt, model_class=llm_model_class, temperature=0.3)
```

Provider-agnostic via `cexai.foundation.invocation.router`. Deployer choses temperature; default 0.3 (some variation per recipient, but consistent voice).

---

## Rate limiting

Outbound rate is capped per `rate_limit_per_minute` open_var. Default 30/min. Providers (email, WhatsApp) typically tolerate 30-60/min for transactional traffic; higher rates trigger spam classification.

Implementation: token-bucket per channel + per project. Crossing the bucket pauses dispatch (queue persists; re-tries on next tick).

---

## Channel dispatch

Channel-specific providers (per `feature_crm.md` outreach_channels):

| Channel | Provider examples | Notes |
|---------|-------------------|-------|
| email | Resend, SendGrid, Postmark, Mailgun | Configure SPF/DKIM/DMARC externally |
| whatsapp | WhatsApp Business API, Twilio, Zenvia | Requires WhatsApp Business approval flow |
| sms | Twilio, Zenvia | Country-specific compliance (e.g., Brazilian ANATEL rules) |
| telegram | Telegram Bot API | Bot creation per deployer |
| custom | Deployer-implemented | Adapter must conform to `MessageDispatchAdapter` interface |

---

## Audit + log

Every dispatch emits:
- `sales_messages` row (per `feature_crm.md` schema) with final_body, channel, sent_at
- `audit_event` with event_type: `message_dispatch_attempt | message_dispatch_success | message_dispatch_failure`

Failed dispatches: do NOT auto-retry by default. Some failures (invalid email format, opt-out) are PERMANENT; retry would spam. Operator manually re-tries via `/admin/vendas`.

---

## Integration contracts

- Consumes from: `feature_crm.md` (contacts + sales_message_templates).
- Provides to: `feature_admin_console.md` (sales module renders campaigns + history).
- LLM dispatch via `cexai.foundation.invocation.router`.
- Provider integration via deployer-chosen adapters.
- Audit via `kc_audit_event.md` (R23 proposal).

---

## Out of scope

- Inbound message handling (responses to outbound) -- requires a separate `feature_inbox.md` (deferred).
- Email open / click tracking (deployer integrates a tracking service).
- Multi-language A/B testing (deferred R24+).
- AI-powered response classification (deferred R24+).
