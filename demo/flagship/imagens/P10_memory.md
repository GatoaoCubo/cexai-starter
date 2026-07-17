---
agent_id: codexa_imagens
pillar: P10
pillar_name: memory
lang: pt-BR
cexai_reference_kind: [session_state, session_backend, entity_memory, memory_summary, prompt_cache, c2pa_manifest]
source: codexa-core (FAT_ADW_PHOTO_V2.md stage handoffs, api/v1/listing_images.py preset storage + vision_data_json passthrough)
fidelity: full
---

# P10 -- Contexto e Memoria (estado da conversa + C2PA provenance)

Sem Supabase, a "memoria" e o **contexto da conversa atual**. Rastreie ativamente
o estado entre estagios. CEXAI lift: typed kinds para estado, presets, cache, e
C2PA provenance (NEW value-add).

> CEXAI typed kinds: [[session_state]] (in-conversation schema) +
> [[session_backend]] (per-runtime persistence strategy) + [[entity_memory]]
> (per-product attribute cache) + [[memory_summary]] (3 named presets) +
> [[prompt_cache]] (repeated template lookups) + **[[c2pa_manifest]] (NEW --
> AI-generated image provenance text block, audit section 3.3)**.

## 1. Estado a rastrear (handoff entre estagios)

> CEXAI typed kind: [[session_state]] -- in-conversation state schema.

```yaml
session_state:
  product:
    name: string
    material: string        # do Estagio 1
    size_category: string
    color_dominant: string
    texture: string
  decisions:
    marketplace: string     # confirmado ou default
    platform: string
    style: string
    mood: string
    brand_colors: string[]
  stage_outputs:
    analysis: object        # E1 -> alimenta E2
    prompts: object         # E2 -> alimenta E3
    style_direction: object # E3 -> alimenta E4
  generated_images: []      # se usou primary lane: prompt + descricao + c2pa_manifest
  active_lanes: []          # quais lanes opcionais o usuario opt-in nesta sessao
```

## 2. Handoffs entre estagios (o que cada um passa adiante)
- E1 -> E2: material define lighting; cor define background; tamanho define camera.
- E2 -> E3: o prompt primario e os settings alimentam mood/paleta/camera.
- E3 -> E4: o grid de 9 cenas vira as 9 regras de composicao.
- E4 -> E5 (opcional): prompts + composition feed image-gen lane (primary/L2/L3).
- E5 -> entrega: image + c2pa_manifest text block append.
- Tudo -> entrega: consolidado em P05.

## 3. Session backend (per-runtime persistence)

> CEXAI typed kind: [[session_backend]] -- runtime-specific persistence.

```yaml
session_backend:
  custom_gpt_full:
    persistence: conversation_only
    note:        "ChatGPT does not persist Project memory beyond conversation by default"
  chatgpt_projects_enxuto:
    persistence: project_memory
    note:        "ChatGPT Projects retain context across conversations within the project"
  claude_projects:
    persistence: project_memory
    note:        "Claude Projects retain context + uploaded artifacts"
  gemini_gems:
    persistence: gem_memory
    note:        "Gemini Gems retain context within the Gem"
```

## 4. Presets (memory_summary -- 3 named patterns)

> CEXAI typed kind: [[memory_summary]] -- 3 typed preset patterns.

Quando o usuario disser "use o mesmo estilo de antes", **releia o estado da
conversa** e reaplique as `decisions`. Presets nomeados:

```yaml
memory_summary_clean_marketplace:
  templates: [marketplace_ml_principal, background_white_clean, lighting_studio_soft, camera_product_85mm, style_minimalista]
  style:     clean
  use_for:   "main image marketplace, white bg, conversao"

memory_summary_lifestyle_insta:
  templates: [background_lifestyle_kitchen, lighting_natural_warm, camera_lifestyle_35mm, style_vibrante_pop]
  aspect:    4:5
  use_for:   "Instagram feed lifestyle, organic, contexto"

memory_summary_luxo_escuro:
  templates: [style_premium_luxo, lighting_studio_soft, camera_product_85mm]
  style:     luxo
  note:      "STYLE_OVERRIDES escurece cells 1/2/6 (P03 sec. 8)"
  use_for:   "produto premium, alto ticket, hero shot"
```

## 5. Entity memory (per-product attribute cache)

> CEXAI typed kind: [[entity_memory]] -- product attributes locked for consistency.

Para o grid de 9 cenas parecer o MESMO produto: fixe e repita em TODOS os
prompts os atributos imutaveis -- cor, material, formato, marca, proporcoes.
Varie so fundo/angulo/mood. Isso compensa a ausencia do reference-image do
backend.

```yaml
entity_memory:
  product_attrs_locked:    # fixed across all 9 scene prompts
    color:    "{user_provided}"
    material: "{user_provided}"
    shape:    "{user_provided}"
    finish:   "{user_provided_or_PREENCHER}"
  vary_axes:               # what changes per scene
    - background
    - angle
    - mood
    - lighting_style
```

## 6. Prompt cache (repeated template lookups)

> CEXAI typed kind: [[prompt_cache]] -- cache for the 9 formulas + 13 templates.

```yaml
prompt_cache:
  scope:            current_session
  cached_items:     [9_TEMPLATE_PHOTO_PROMPTS, 13_real_templates, HYPERREALISTIC_SUFFIX, CONDENSED_NEGATIVE]
  invalidation:     conversation_reset
  note:             "Prefer cache hits over re-derivation; reduces variance + cost"
```

## 7. C2PA manifest (NEW CEXAI value-add -- provenance)

> CEXAI typed kind: [[c2pa_manifest]] -- AI-generated image provenance.
> Audit section 3.3 designates this as the NEW value-add.
> **Rendered as a TEXT block in P05 output, never binary embed.**

```yaml
c2pa_manifest:
  ai_generated:   true
  engine:         dalle | midjourney | stable_diffusion | gemini_image | comfyui
  prompt_hash:    sha256:{hash_of_prompt_used}
  agent_id:       codexa_imagens
  agent_version:  2.0.0
  generation_lane: primary_dalle | L2_gemini_grid | L3_comfyui
  disclaimer:     "Geracao de IA -- nao e foto real do produto"
  generated_at:   ISO_8601_timestamp
  marketplace_compliance_intent: amazon | mercado_livre | shopee | magalu | generic
```

**Emit rule:** the c2pa_manifest text block MUST be emitted in P05 output
whenever an image was generated (E5 fired). It is informational disclosure for
the user to copy + paste into marketplace listings as AI-content compliance
evolves (2026+ marketplaces increasingly require AI-disclosure).

**Why text-not-binary:** the bundle ships standalone; no host can embed real
C2PA cryptographic manifests into PNG metadata. Text disclosure is the honest
path -- the user copies it into their listing alongside the image.

## 8. O que NAO persiste
Nada entre sessoes em Custom GPT (FULL). Projects/Gems/Claude Projects retem
contexto mas nao state estruturado entre conversations distintas. Ao iniciar
nova conversa, o estado zera -- peca o produto de novo ou aceite que o usuario
cole o resumo da sessao anterior.

## 9. Cross-link com CEXAI typed kinds

- [[session_state-builder]] -- in-conversation schema
- [[session_backend-builder]] -- per-runtime persistence
- [[entity_memory-builder]] -- product attr cache
- [[memory_summary-builder]] -- 3 named presets
- [[prompt_cache-builder]] -- template cache
- [[c2pa_manifest-builder]] -- AI provenance text block (NEW CEXAI value-add)

## Related CEXAI artifacts

- [[session-state-builder]] -- per-session runtime state
- [[session-backend-builder]] -- session storage backend
- [[entity-memory-builder]] -- persistent entity store
- [[memory-summary-builder]] -- compressed memory rollup
- [[prompt-cache-builder]] -- prompt-response cache layer
- [[c2pa-manifest-builder]] -- C2PA provenance manifest
