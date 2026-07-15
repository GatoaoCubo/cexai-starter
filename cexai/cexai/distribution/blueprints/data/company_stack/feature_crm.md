---
kind: feature_template
feature_name: crm
vertical: 16_company_stack
round_added: 22
pillars: [P01, P10]
adr_019_packages: [tools/web/, memory/]
feature_dependencies: [feature_admin_console]
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display name in CRM outreach templates."
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
    description: "Drives outreach copy bias."
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
    description: "Default audience descriptor for outreach campaigns."
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
    description: "Default outreach language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: crm_lifecycle_stages
    type: list[str]
    description: "Ordered list of pipeline stages (e.g., ['new', 'contacted', 'negotiating', 'won', 'lost'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.crm_lifecycle_stages]
    constraints: {min_items: 2, max_items: 12}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["new", "contacted", "negotiating", "won", "lost"]
    rebind_allowed: true
  - name: outreach_channels
    type: list[str]
    description: "Channels available for outreach (e.g., ['email', 'whatsapp', 'phone'])."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.outreach_channels]
    constraints: {min_items: 1}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["email"]
    rebind_allowed: true
---

# Feature Template: CRM

**Purpose**: a contacts database with lifecycle pipeline (kanban + table views), outreach log, and template-based message composition. Designed for both B2B/B2C lead pipelines and SaaS subscriber lifecycle.

---

## Data schema (recommended)

```yaml
# Contact schema
table: crm_contacts
columns:
  - name: id                       # uuid PK
  - name: display_name             # company name OR person name; not assumed
  - name: email                    # nullable
  - name: phone                    # nullable (with country code if international)
  - name: whatsapp                 # nullable (canonical E.164 format)
  - name: city                     # nullable
  - name: region                   # state/province; nullable
  - name: country                  # ISO 3166 code; default from brand_config
  - name: segment                  # deployer-defined classification
  - name: status                   # enum from crm_lifecycle_stages open_var
  - name: tags                     # text[] for flexible tagging
  - name: last_contact_at          # timestamp
  - name: next_followup_at         # timestamp; drives reminder queries
  - name: notes                    # markdown long-form
  - name: custom_fields            # jsonb for per-deployer extensions
  - name: created_at
  - name: updated_at

# Outreach log
table: sales_messages
columns:
  - name: id                       # uuid PK
  - name: contact_id               # FK to crm_contacts
  - name: strategy                 # campaign / one-off / followup
  - name: channel                  # from outreach_channels open_var
  - name: subject                  # for email; nullable for chat
  - name: final_body               # rendered message text
  - name: variables                # jsonb of substitution values used
  - name: sent_at                  # timestamp
  - name: response_received_at     # nullable; populated when contact replies
  - name: opened_at                # nullable; for email tracking
  - name: created_at

# Reusable message templates
table: sales_message_templates
columns:
  - name: id                       # uuid PK
  - name: strategy                 # matches sales_messages.strategy
  - name: channel                  # matches sales_messages.channel
  - name: title                    # internal label
  - name: body                     # template with {{placeholders}}
  - name: variables                # jsonb declaring placeholder names + descriptions
  - name: status                   # enum: draft | active | archived
  - name: created_at
```

---

## Admin pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/admin/crm` (or `/admin/contacts`) | CRMPage | Tabs: Kanban (by status), Table (filterable), Map (if `city` populated) |
| `/admin/crm/:id` | ContactDetail | Single contact view + outreach history |
| `/admin/vendas` (or `/admin/sales`) | SalesAssistant | Tabs: Bulk campaign, New message, History |

The Sales Assistant Bulk Campaign defaults to filtering by status in `{'new', 'contacted'}` -- deployer adjusts.

---

## Lifecycle pipeline

The `crm_lifecycle_stages` open_var defines the pipeline. The kanban view renders one column per stage; the table view filters by status.

Recommended defaults (deployer overrides):
- B2B sales: `['new', 'contacted', 'negotiating', 'won', 'lost']`
- SaaS: `['trial', 'active', 'at_risk', 'churned', 'reactivated']`
- Agency: `['prospect', 'pitch', 'engaged', 'delivered', 'maintenance']`

---

## Message composition

Two modes:

1. **Template substitution (fast, free)**: `final_body = template.body.replace(placeholders, variables)`. No LLM call.
2. **LLM-personalized (rich, costed)**: `final_body = router.dispatch(prompt=build_prompt(contact, template, products), model_class="composer")`. Uses `cexai.foundation.invocation.router` (provider-agnostic per ADR 022).

The deployer chooses per-strategy. Bulk campaigns default to template substitution (free + fast); high-stakes outreach uses LLM personalization.

---

## Placeholder convention

Templates use `{{variable_name}}` syntax. Common placeholders:
- `{{display_name}}` -- contact's display name (company OR person; NEVER assume person)
- `{{city}}`, `{{region}}`, `{{segment}}` -- contact attributes
- `{{product_url}}`, `{{kit_url}}` -- when promoting catalog (`feature_catalog.md`)
- `{{brand_name}}` -- from open_var

**Critical**: when display_name represents a company (e.g., B2B), NEVER use templates that say "Oi {{first_name}}". The schema does NOT assume a person-name field. Recommended phrasing: `"Oi pessoal da {{display_name}}"` or culturally-neutral equivalent.

---

## Channel-specific behavior

| Channel | Resolution rule |
|---------|----------------|
| `email` | Required: `email` populated. |
| `whatsapp` | Required: `whatsapp` populated. Fall back to `phone` if `whatsapp` null; prepend country code if missing. |
| `phone` | Required: `phone` populated. |
| Custom (sms, telegram, etc.) | Deployer extends. |

---

## Integration contracts

- Receives auth from `feature_admin_console.md` (protected routes).
- Provides outreach history feed to `feature_publishing.md` (cross-channel campaign coordination).
- Provides contact-list seed to `feature_publishing.md` (audience segmentation for content distribution).
- Optionally consumes from `feature_catalog.md` (product references in outreach templates).
- Provides `b2b_orders` upgrade path (negotiating contacts who convert become orders -- handled in `feature_pricing_engine.md`).

---

## Out of scope

- Email deliverability tuning (deployer concern; recommend SPF/DKIM/DMARC setup external).
- Phone-system integration (twilio, etc.) -- deployer choice.
- Compliance reporting (GDPR, LGPD) -- deployer responsibility; templates respect "do not contact" via status `'opted_out'` extension.
- Advanced segmentation DSL -- v1 uses simple filter on status + tags; advanced filtering deferred to R23.
