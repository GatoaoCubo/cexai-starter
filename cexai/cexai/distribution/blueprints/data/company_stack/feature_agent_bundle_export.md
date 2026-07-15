---
kind: feature_template
feature_name: agent_bundle_export
vertical: 16_company_stack
round_added: 25
pillars: [P12, P05]
adr_019_packages: [governance/, tools/]
feature_dependencies: [feature_admin_console, feature_secrets, feature_persistent_memory]
brand_niche_constraints: null
related_spec: _revisions/spec_agent_bundle_export.md
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in exported bundles + manifest source_brand."
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
    description: "Bundled into agent's domain context."
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
    description: "Bundled into agent's voice calibration."
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
    description: "Bundle UI + agent response language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: target_platforms
    type: list[str]
    description: "Platforms the deployer wants to support bundles for."
    filler_role: user
    filler_stage: F4_REASON
    allowed_values: ["chatgpt_custom_gpt", "claude_projects", "gemini_gems", "openrouter_agent", "self_hosted"]
    context_hints: [brand_config.target_platforms]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: signing_key_id
    type: str
    description: "ID of the HMAC signing key in feature_secrets.md vault (NEVER the key value)."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.signing_key_id]
    constraints: {pattern: "^[a-z][a-z0-9_]*_v\\d+$"}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: bundle_storage_path
    type: str
    description: "Filesystem path (relative to deployer root) where bundles are written."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.bundle_storage_path]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "./agent_bundles/"
    rebind_allowed: true
---

# Feature Template: Agent Bundle Export

> The orchestrator-to-employee handoff feature: export a self-contained agent bundle that an
> employee can upload to ChatGPT Custom GPT / Claude Projects / Gemini Gems WITHOUT cexai CLI access.
>
> Full spec: `_revisions/spec_agent_bundle_export.md` (this Round R25).

---

## Purpose

The orchestrator (typically the deployer themselves) needs to delegate operational tasks to
employees who use mainstream AI platforms (ChatGPT, Claude, Gemini) but lack cexai CLI access.

This feature provides the **export pipeline**:
- Take a CEXAI agent definition + brand_config + selected feature_templates.
- Produce a 14-file isolated bundle (`instructions.md` + 12 pillar files + `manifest.yaml`).
- Sign for integrity.
- Hand to the employee who uploads to their platform.

The employee uses the agent on their familiar platform; the agent has FULL CEXAI knowledge baked
in but operates ISOLATED from the live cexai repo.

---

## Architecture

```
cexai CLI (orchestrator-side):
  -> read brand_config.yaml (open_vars source)
  -> read selected feature_templates (frozen with brand's open_vars)
  -> read source_nucleus's agent_card (P02 + P08 identity)
  -> read source_blueprint (vertical 16 or 17) for context
  -> distill each pillar's relevant content into single .md per pillar
  -> synthesize instructions.md (system_prompt referencing 12 pillars)
  -> write manifest.yaml with metadata + per-file SHA256 + signature
  -> emit reasoning_trace + audit_event

orchestrator hands bundle.zip to employee
  -> employee uploads to their platform per prepare_for_<platform>.md
  -> agent runs isolated from cexai
```

---

## Bundle file layout (spec'd in detail in spec_agent_bundle_export.md)

```
<bundle_storage_path>/<agent_id>/
├── instructions.md
├── manifest.yaml
└── pillars/
    ├── P01_knowledge.md
    ├── P02_model.md
    ├── P03_prompt.md
    ├── P04_tools.md
    ├── P05_output.md
    ├── P06_schema.md
    ├── P07_evaluation.md
    ├── P08_architecture.md
    ├── P09_config.md
    ├── P10_memory.md
    ├── P11_feedback.md
    └── P12_orchestration.md
```

Plus optional per-platform prepare guides:
```
└── prepare_for_chatgpt_custom_gpt.md
└── prepare_for_claude_projects.md
└── prepare_for_gemini_gems.md
```

---

## Per-pillar content distillation

Each pillar's file is DISTILLED, not copied. Source content per pillar:

| Pillar | Source content (curated for the agent) |
|--------|---------------------------------------|
| P01 Knowledge | Relevant KCs from `N00_genesis/P01/library/kind/` + brand-specific glossary |
| P02 Model | Agent identity + behavioral defaults + (LLM preferences if applicable) |
| P03 Prompt | Selected prompt templates the agent uses |
| P04 Tools | Tool descriptions; if target_platform supports Custom Actions: OpenAPI schemas |
| P05 Output | Output format expectations |
| P06 Schema | Input validation + output schema |
| P07 Evaluation | Self-check rubric (lightweight, agent-side; not the full F7 GOVERN gate) |
| P08 Architecture | Agent card + relevant ADRs (license, brand voice constitutional articles) |
| P09 Config | Runtime defaults; secret NAMES referenced (never values) |
| P10 Memory | KC pointers (which to load on session); brand persistent memory excerpts |
| P11 Feedback | Guardrails, escalation triggers, content policies |
| P12 Orchestration | Workflow for the agent's tasks; escalation paths |

Each pillar file is 100-500 lines.

---

## Secret hygiene (CRITICAL)

The bundle MUST NOT contain any secret VALUES (API keys, tokens, passwords). Only secret NAMES.

Example (correct):
```yaml
# pillars/P09_config.md
secrets_referenced:
  - support_email_api_key
  - knowledge_base_api_key
```

Example (incorrect -- would FAIL the no-secret-leak audit):
```yaml
# pillars/P09_config.md
secrets:
  support_email_api_key: "sk_live_actual_key_value_dont_do_this"
```

The bundle export pipeline includes a pre-emit regex audit that fails the export on detected secret patterns (API key formats, OAuth tokens, etc.).

---

## Reproducibility

Same inputs (brand_config + nucleus + feature_template versions) -> byte-identical bundle (modulo `exported_at` timestamp).

Enforced by:
1. Deterministic per-pillar distillation logic (no LLM randomness; or LLM at temperature=0.0 per ADR 022 D-022-04 patterns).
2. Sorted file order in pillar files.
3. Per-file SHA256 in manifest -- changes detectable.

---

## Audit pattern

Every export emits `audit_event`:
- `event_type: agent_bundle_exported`
- `subject.agent_id`, `subject.bundle_version`, `subject.target_platforms`, `subject.exported_to_employee_id`
- `outcome: success | failure_secret_leak | failure_distillation_error | failure_signature_error`
- `retention_class: long_3y` (governance-relevant)

Every receipt + upload to external platform (logged at export time, since orchestrator doesn't see employee's upload directly):
- `audit_event` of type `agent_bundle_handoff` recording employee identifier.

---

## CLI (deferred R26+ implementation)

```bash
cexai agent export \
  --agent <agent_id> \
  --brand-config ./brand_config.yaml \
  --source-blueprint 16_company_stack \
  --target-platforms chatgpt_custom_gpt,claude_projects \
  --output ./agent_bundles/customer-support/
```

Outputs the 14-file bundle + optional `.zip` for handoff.

Validate:
```bash
cexai agent validate ./agent_bundles/customer-support/
```

Checks: file count, signature, no-secret-leak, manifest schema, pillar file sizes.

---

## Integration contracts

- Consumes from: deployer's brand_config.yaml + selected feature_templates (frozen) + source nucleus's agent_card.
- Consumes signing key from: `feature_secrets.md` vault (via `signing_key_id` open_var).
- Produces bundles to: `bundle_storage_path` (deployer's filesystem).
- Audit via `kc_audit_event.md`.
- Reasoning_trace per ADR 020 D-020-04.

---

## Niche compatibility

Niche-agnostic. Any deployer (e-commerce, SaaS, agency, creator, marketplace) may export agent bundles for their employees.

Particularly useful for:
- E-commerce / retail: customer support agent (orders, returns, product questions).
- SaaS: trial nurturing agent, onboarding helper, technical support tier 1.
- Agency: client interface agent (project status queries, brief intake).
- Creator: superfan engagement agent (newsletter responder, FAQ).
- Marketplace: dispute resolution agent, seller-onboarding helper.

---

## Out of scope

- Real-time chat with the deployed external agent through cexai (the agent runs externally).
- Bidirectional sync between external platform and cexai repo.
- Multi-agent bundles (1 bundle = 1 agent).
- Custom platform-specific UX beyond what each platform natively supports.
- Bundle hot-reload (changes to source require re-export + employee re-upload).
- Agent-to-agent invocation between external agents (cross-platform agent network out of scope).
