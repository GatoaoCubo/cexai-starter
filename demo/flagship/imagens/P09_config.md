---
agent_id: codexa_imagens
pillar: P09
pillar_name: config
lang: pt-BR
cexai_reference_kind: [env_config, marketplace_app_manifest]
source: codexa-core (api/data/templates/*.json 13 templates reais, api/core/template_registry.py categorias + prioridades + regras de composicao, api/core/compliance_checker.py MARKETPLACE_SPECS)
fidelity: full
---

# P09 -- Configuracao (Catalogo Real de Templates + Limites + Env Contract)

> Os templates JSON do backend codexa-core existem em disco
> (`api/data/templates/*.json` -- 13 arquivos). O catalogo abaixo e portado
> EXATO desses arquivos. **Quanto mais voce alimentar com estes fragmentos
> concretos, melhor o output.**

> CEXAI typed kinds: [[env_config]] (API keys for optional lanes) +
> [[marketplace_app_manifest]] (4-runtime distribution).

## 1. Categorias e regras de composicao (template_registry.py)

| Categoria | Prioridade | Regra | IDs reais em disco |
|-----------|-----------|-------|--------------------|
| **marketplace** | 0 | EXCLUSIVA (max. 1) | marketplace_amazon_main, marketplace_ml_principal, marketplace_shopee_principal, marketplace_magalu_principal |
| **background** | 1 | EXCLUSIVA (max. 1) | background_white_clean, background_lifestyle_kitchen |
| **product_type** | 2 | empilhavel | (sem arquivo em disco -- use atributos do produto) |
| **composition** | 3 | recomendado-1 | (sem arquivo -- use regras de P03/P05) |
| **style** | 4 | empilhavel | style_premium_luxo, style_minimalista, style_vibrante_pop |
| **lighting** | 5 | recomendado-1 | lighting_studio_soft, lighting_natural_warm |
| **camera** | 6 | recomendado-1 | camera_product_85mm, camera_lifestyle_35mm |
| **mood** | 7 | empilhavel | (derivado do estilo / PNL triggers de P01) |

Regras (`validate_combination`): EXCLUSIVE={marketplace, background};
STACKABLE={style, mood, product_type}; SINGLE_RECOMMENDED={lighting, camera, composition}.
Ordem de montagem = ordem de prioridade 0->7 (P03 sec. 2 / P08 sec. 3).

## 2. Catalogo EXATO de templates (fragmentos reais)

### marketplace (prioridade 0, exclusivo)

**marketplace_amazon_main** -- output 2000x2000 PNG #FFFFFF
- prefix: `Professional Amazon product listing photo, pure white background (#FFFFFF), product centered filling 85% of frame,`
- suffix: `ultra-clean white background, no shadows, no props, no text, no logos, no watermarks, photorealistic, 8K quality`
- negative: `colored background, props, text, watermark, logo, shadow, lifestyle setting, human hands`

**marketplace_ml_principal** -- output 1200x1200 JPEG #FFFFFF (prompt em PT)
- prefix: `Foto principal Mercado Livre, fundo branco puro, produto centralizado 80% do quadro,`
- suffix: `fundo branco limpo, sem sombras, sem texto, sem marca dagua, qualidade profissional`
- negative: `fundo colorido, objetos, texto, marca dagua, sombra, cenario, maos`

**marketplace_shopee_principal** -- output 1200x1200 PNG #FFFFFF
- prefix: `Shopee product listing photo, clean white background, product centered,`
- suffix: `white background, no text overlay, no promotional badges, clean product shot`
- negative: `text, badges, stickers, colored background, collage`

**marketplace_magalu_principal** -- output 1200x1200 JPEG #FFFFFF
- prefix: `Magazine Luiza product photo, pure white background, professional lighting,`
- suffix: `clean white background, JPEG compatible, no transparency, sharp product detail`
- negative: `transparent background, PNG artifacts, colored background, text`

### background (prioridade 1, exclusivo)

**background_white_clean** -- compativel com TODOS os marketplaces
- prefix: `On a perfectly clean pure white background (#FFFFFF),`
- suffix: `seamless white background, no shadows, no reflections, studio product photography`
- negative: `colored background, gradient, texture, shadow, reflection`

**background_lifestyle_kitchen** -- compliance: generic (NAO main image)
- prefix: `In a warm modern kitchen setting with natural light, marble countertop,`
- suffix: `lifestyle product photography, warm tones, shallow depth of field, cozy atmosphere`
- negative: `cluttered, dirty, dark, cold lighting, industrial`

### style (prioridade 4, empilhavel)

**style_premium_luxo** -- suffix: `luxury premium aesthetic, rich textures, elegant composition, sophisticated lighting, high-end product photography` -- negative: `cheap, plastic, low quality, amateur`

**style_minimalista** -- suffix: `minimalist design, clean lines, negative space, simple composition, Scandinavian aesthetic` -- negative: `cluttered, busy, ornate, decorative, complex`

**style_vibrante_pop** -- suffix: `vibrant pop colors, energetic composition, bold contrast, eye-catching, Gen-Z aesthetic` -- negative: `muted, dull, dark, boring, corporate`

### lighting (prioridade 5, recomendado-1)

**lighting_studio_soft** -- suffix: `professional studio soft lighting, even illumination, soft shadows, beauty lighting setup` -- negative: `harsh shadows, direct flash, uneven lighting, dark areas`

**lighting_natural_warm** -- suffix: `warm natural golden hour lighting, soft window light, warm color temperature 3200K` -- negative: `cold lighting, blue tones, artificial flash, fluorescent`

### camera (prioridade 6, recomendado-1)

**camera_product_85mm** -- suffix: `shot with 85mm lens, f/2.8, sharp product focus, creamy bokeh background, professional DSLR quality` -- negative: `wide angle distortion, fisheye, blurry product, smartphone quality`

**camera_lifestyle_35mm** -- suffix: `shot with 35mm lens, f/4, environmental context visible, lifestyle perspective, natural framing` -- negative: `tight crop, no context, macro, extreme close-up`

## 3. Output spec padrao (template_registry defaults)

```yaml
width: 1024
height: 1024
format: jpeg
background_color: "#FFFFFF"
quality: high
recommended_model: gpt-image-1   # bundle -> DALL-E nativo / Imagen 3 / etc per runtime
style: natural
```

## 4. Limites por marketplace (compliance_checker.py -- MARKETPLACE_SPECS)

```yaml
amazon:        min 2000x2000 | jpeg/png/tiff/gif | bg branco tol 25 | fill 85%
mercado_livre: min 1200x1200 | jpeg/png          | bg branco tol 30 | fill 80%
shopee:        min 1200x1200 | jpeg/png          | bg branco tol 35 | sem fill
magalu:        min 1200x1200 | jpeg              | sem bg branco    | sem fill
generic:       min 1080x1080 | jpeg/png/webp     | sem bg branco    | sem fill
```

## 5. Defaults inteligentes (quando o input omite)

```yaml
style:        clean
marketplace:  mercado_livre
background:   derivado da cor dominante (P01 sec. 2)
lighting:     derivada do material (P01 sec. 1)
camera:       85mm f/5.6 (medium) | 50mm/100mm macro (tiny)
mood:         professional
platform:     marketplace
aspect_ratio: 1:1
steps:        30
cfg:          7
sampler:      "DPM++ 2M Karras"
```

## 6. Env contract (CEXAI lift)

> CEXAI typed kind: [[env_config]] -- API keys for optional upgrade lanes.

```yaml
env_config:
  required:                  []   # NONE -- bundle works without any env
  optional_for_lanes:
    L1_gemini_pro_vision:
      vars:                 [GEMINI_API_KEY, GEMINI_MODEL]
      fallback_when_absent: dalle_native + text_extraction
    L2_gemini_image_grid:
      vars:                 [GEMINI_API_KEY, GEMINI_IMAGE_MODEL]
      fallback_when_absent: dalle_native + 9x_sequential
    L3_comfyui_local:
      vars:                 [COMFYUI_HOST, COMFYUI_WORKFLOW_FILE]
      fallback_when_absent: dalle_native
    L4_qwen3_vl_ollama:
      vars:                 [OLLAMA_HOST, OLLAMA_VISION_MODEL]
      fallback_when_absent: text_extraction
    L5_firecrawl_browser:
      vars:                 [FIRECRAWL_API_KEY, FIRECRAWL_TIMEOUT]
      fallback_when_absent: paste_intake
  security:                 "all keys via host runtime's secret-store, never in instructions text"
```

## 7. Marketplace app manifest (P09 distribution across 4 runtimes)

> CEXAI typed kind: [[marketplace_app_manifest]] -- runtime distribution.

```yaml
marketplace_app_manifest:
  agent_id:         codexa_imagens
  version:          2.0.0
  distribution_targets:
    - target:       custom_gpt_full
      knowledge_size_limit: 20_files
      instructions_char_limit: 8000
      ship_path:    "knowledge/ + 00_instructions.md + SETUP_pt-br.md"
    - target:       chatgpt_projects_enxuto
      knowledge_size_limit: 5_files
      instructions_char_limit: 8000
      ship_path:    "projects_free/ + SETUP_chatgpt_projects.md"
    - target:       claude_projects
      knowledge_size_limit: unlimited
      instructions_char_limit: unlimited
      mcp_supported: true
      ship_path:    "claude/ + .mcp.json + SETUP_claude_projects.md"
    - target:       gemini_gems
      knowledge_size_limit: unlimited
      instructions_char_limit: unlimited
      native_capabilities: [vision, imagen3, code_exec]
      ship_path:    "gemini/ + SETUP_gemini_gems.md"
```

## 8. Constraints duras

- main image de marketplace: SEM texto/logo/marca d'agua/preco sobreposto.
- brand_colors em hex `#RRGGBB`.
- aspect ratio coerente com a plataforma (P01 sec. 8).
- 1 marketplace e 1 background no maximo por combinacao.
- atributos do produto (cor/material/forma): SO os que o usuario forneceu --
  nunca invente para preencher o template (P06/P11 anti-alucinacao).

## 9. Cross-link com CEXAI typed kinds

- [[env_config-builder]] -- API keys per lane
- [[marketplace_app_manifest-builder]] -- 4-runtime distribution

## Related CEXAI artifacts

- [[env-config-builder]] -- environment-scoped config
- [[marketplace-app-manifest-builder]] -- marketplace listing manifest
