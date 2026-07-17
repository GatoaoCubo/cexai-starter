---
agent_id: codexa_imagens
pillar: P08
pillar_name: architecture
lang: pt-BR
cexai_reference_kind: [diagram, agent_card]
source: codexa-core (api/v1/listing_images.py generate_unified flow + real endpoints, api/core/prompt_enhancer.py build_grid_prompt v9.0, api/core/prompt_builder.py assembly, FAT_ADW_PHOTO_V2.md 4-stage didatico)
fidelity: full
---

# P08 -- Arquitetura do Pipeline

> Merge-to-live: o pipeline DIDATICO de 4 estagios (FAT) e a forma como o agente
> raciocina e entrega. O pipeline de PRODUCAO (sec. 6) e o que o backend Railway
> rodava -- exposto aqui para fidelidade. O agente reproduz o raciocinio sem o
> backend (Gemini/Supabase) por default; lanes opcionais cobrem o resto.

> CEXAI typed kinds: [[diagram]] (pipeline visual) + [[agent_card]] (capability
> declaration -- the A2A-style surface).

## 1. Pipeline de 4 estagios (FAT ADW PHOTO V2)

> CEXAI typed kind: [[diagram]] -- typed pipeline diagram.

```
INPUT -> [1. analyze_product] -> [2. generate_prompt] -> [3. style_direction]
      -> [4. composition_guide] -> OUTPUT
```

Cada estagio tem objetivo, gate >= 8.0 (P07) e alimenta o proximo. O agente
raciocina estagio a estagio; nao pula etapas.

### Estagio 1 -- ANALYZE PRODUCT
Determina as caracteristicas visuais do produto. Entrada: descricao. Saida:
`{material, size_category, color_dominant, texture, recommended_style,
lighting_needs, background_suggestion, hero_angle}`. Usa a matriz de P01 sec. 1-2.

### Estagio 2 -- GENERATE PROMPT
Gera prompts otimizados para MJ/DALL-E/SD. Aplica a montagem
`prefix + descricao + suffix` por prioridade (P03 sec. 2). Saida: primario + 3
variacoes + negative + settings.

### Estagio 3 -- STYLE DIRECTION
Define a direcao visual completa: mood, paleta, settings de camera e o **grid de
9 cenas/angulos** (hero, 2 detail, 2 lifestyle, flat_lay, scale, packaging, group).

### Estagio 4 -- COMPOSITION GUIDE
Regras acionaveis de composicao por cena + specs por plataforma + pos-producao.

## 2. Logica de decisao (como o agente raciocina)

```
material reflexivo/transparente?  -> forca lighting difusa/backlight (P01 sec. 1)
cor clara?  -> fundo escuro ;  cor escura? -> fundo claro  (P01 sec. 2)
tamanho tiny? -> lente macro ;  large? -> grande angular
plataforma = marketplace main? -> fundo branco + 80-85% fill + sem texto (P09)
plataforma = instagram? -> ratio 4:5 ou 9:16, estilo lifestyle
usuario pediu imagem? -> primary lane (DALL-E nativo) com prompt DALL-E primario (P04)
usuario pediu grid 9-em-1? -> L2 if env set; else 9x DALL-E sequencial (P04)
```

## 3. Logica de montagem do prompt (do prompt_builder)

Ordem de prioridade das categorias (CATEGORY_PRIORITY):
```
0 marketplace | 1 background | 2 product_type | 3 composition
4 style | 5 lighting | 6 camera | 7 mood
```
- prefixes (por espaco) + descricao + suffixes (por virgula).
- negatives concatenados e deduplicados.
- exclusivas: marketplace, background. empilhaveis: style, mood, product_type.
- output_spec herdado do template de maior prioridade.

## 4. Mapa de degradacao -> CEXAI lifts (backend -> bundle)

```
backend FastAPI (Railway)                bundle codexa-v2 (CEXAI 12P)
-------------------------                ----------------------------
POST /generate-unified (Gemini grid 3x3) -> DALL-E nativo (primary) + L2 opcional (Gemini grid)
POST /vision-analyze (Gemini Vision)     -> atributos da descricao + L1 / L4 opcionais (vision lanes)
grid_splitter (9 PNGs)                   -> 9 cenas 1-a-1 (default) or L2 native grid
Supabase Storage (URLs)                  -> usuario salva local
template JSON registry (13 arquivos)     -> catalogo embutido em P09 (fragmentos reais)
prompt_builder/compliance_checker        -> regras embutidas em P01/P03/P07
prompt_enhancer (grid v9.0 + presets)    -> bibliotecas em P03 (cenas, estilos, negatives)
scrape-product-url (Firecrawl/Serper)    -> L5 opcional (Firecrawl HTTP API)
no provenance                            -> NEW CEXAI value-add: c2pa_manifest text block (P05/P10)
```

## 5. Fluxo de ponta a ponta (resumo)
1. Recebe produto -> 2. Analisa (E1) -> 3. Monta prompts (E2) ->
4. Direcao (E3) -> 5. Composicao (E4) -> 6. Entrega (P05) ->
7. [opcional] Gera via primary lane DALL-E (P04) -> 8. C2PA disclosure block.
Estado entre estagios em P10.

## 6. Pipeline REAL de producao (listing_images.py -- para fidelidade)

O endpoint `POST /listing-images/generate-unified` rodava esta cadeia no backend
original. O bundle codexa-v2 raciocina sobre cada passo:

```
[input: product_description, category, marketplace, style, quality,
        product_color/material/shape/benefit/audience, brand_colors,
        creative_direction, competitor_insights, seed, vision_data_json, reference_image]
  |
  1. credit_guard (deduz credito "foto")                  -- N/A bundle
  2. strategy_planner.plan_strategy() -- agente faz manual em E3
  3. build_grid_prompt() (baseline)   -- regras embutidas em P03
  4. rewrite_scene_cells() -- agente faz manual em E3
  5. build_grid_prompt(rewritten) -- prompts saem em P05
  6. gemini_image_client.generate_from_product() -- L2 opcional; else DALL-E primary
  7. grid_to_scenes_base64() -- L2 opcional; else 9x DALL-E sequencial
  8. image_qa_checker.check_grid() -- self-check de P07 / L6 opcional
  9. supabase upload -- N/A; usuario salva local
  10. retorna GridGenerateResponse -- mapeado para P05 4-block output
```

Modelo de grid de producao: `gemini-2.5-flash-image` (nao DALL-E). Os 9 rotulos
de cena estao em P01 sec. 10.

### Montagem v9.0 do build_grid_prompt (4 chunks + negative)
```
Chunk A (~200): Product identity + grid contract
  "3x3 GRID, 9 scenes in ONE image, equal cells, no borders.
   Product: {desc}. Color: {color}. Material: {material}. Shape: {shape}.
   [Attached photo = EXACT product, fidelity 5/5 -- se houver ref/vision]"
Chunk B (~700): 9 Cell lines
  cells 1,2,6 = STYLE_OVERRIDES (P03 sec. 8) | 3,4,5,7,8 = CATEGORY_CONTEXTS (P03 sec. 10) | 9 = white compliance
Chunk C (~150): Mood + film + creative direction
Chunk D (~200): Technical essentials
  "Canon R5, {film}. CRITICAL: product visible in ALL 9 cells, min 25% frame.
   5 fingers on hands. Each cell DISTINCT background. Cell 1=white, Cell 6=dark.
   No text/numbers/prices/arrows/annotations."
Negative: CONDENSED_NEGATIVE (P03 sec. 7) + reforco por marketplace
```

## 7. Agent card (A2A-style capability declaration)

> CEXAI typed kind: [[agent_card]] -- machine-readable capability surface.

```yaml
agent_card:
  agent_id:        codexa_imagens
  version:         2.0.0
  capabilities:
    primary:
      - dalle_image_generation   # via primary multi_modal_config lane
      - prompt_engineering_mj_dalle_sd
      - art_direction_full
      - marketplace_compliance_check
    optional_lanes:
      - L1_gemini_vision         # via vision_tool
      - L2_gemini_image_grid     # via multi_modal_config
      - L3_comfyui_local         # via multi_modal_config
      - L4_qwen3_vl_ollama       # via vision_tool
      - L5_firecrawl_browser     # via browser_tool
      - L6_code_dimension_check  # via code_executor
  runtime_targets: [custom_gpt_full, chatgpt_projects_enxuto, claude_projects, gemini_gems]
  provenance:      c2pa_manifest (text block, not binary)
  fallback_chain:  see manifest.yaml
```

## 8. Cross-link com CEXAI typed kinds

- [[diagram-builder]] -- typed pipeline visual
- [[agent_card-builder]] -- capability surface declaration

## Related CEXAI artifacts

- [[diagram-builder]] -- architecture diagram artifact
- [[agent-card-builder]] -- capability declaration (A2A)
