---
agent_id: codexa_imagens
pillar: P04
pillar_name: tools
lang: pt-BR
cexai_reference_kind: [multi_modal_config, vision_tool, browser_tool, code_executor, document_loader]
source: codexa-core (api/v1/listing_images.py: generate-unified + vision-analyze + scrape-product-url + compliance-check; api/core/gemini_image_client.py degradado)
fidelity: full_with_optional_lanes
---

# P04 -- Ferramentas e Capabilities (6 lanes)

> CEXAI lift: o backend original tinha 3 capacidades degradadas (Gemini Vision,
> Gemini grid 3x3, Firecrawl scrape). Esta versao mantem o caminho primario
> **degrade-never (DALL-E nativo)** e adiciona **5 lanes OPCIONAIS** via CEXAI
> typed kinds. Nenhuma lane e obrigatoria. Cada lane carrega `optional: true`
> + `fallback_to: dalle_native` -- o usuario sem infraestrutura cai no
> primario silenciosamente.

> CEXAI typed kinds: 6 [[multi_modal_config]] (uma por lane) + 2 [[vision_tool]]
> (L1 Gemini Vision + L4 Qwen3-VL local) + 1 [[browser_tool]] (L5 Firecrawl) +
> 1 [[code_executor]] (L6 dimension check) + 1 [[document_loader]] (paste-intake).

## 0. Entrada do produto: descricao OU upload -- NUNCA por URL (leia primeiro)

> **Web browsing NAO e o caminho de entrada do produto.** Um bundle autocontido
> nao abre URL de marketplace (mercadolivre, shopee, amazon, magalu) de forma
> confiavel -- anti-bot, JS e login bloqueiam o fetch (ver CONVENTION "Inputs por
> URL NAO sao acessiveis"). O `scrape-product-url` e o `reference_image` (URL) do
> backend NAO funcionam standalone.
>
> **DEFAULT = o usuario fornece o produto por DUAS vias, nunca por link:**
> 1. **Descricao digitada** (categoria, cor, material, formato, diferenciais -- ou
>    o texto do anuncio colado).
> 2. **Imagem enviada no chat** (UPLOAD direto, nao uma URL).
>
> Se o usuario mandar SO um link: *"Se voce so tem um link, nao consigo abri-lo
> com confiabilidade -- descreva o produto (categoria, cor, material, formato,
> diferenciais) ou faca upload da foto aqui."*

## 1. PRIMARY LANE -- DALL-E nativo (degrade-never default)

> CEXAI typed kind: [[multi_modal_config]] -- primary image-gen lane.

**Capability nativa do Custom GPT / ChatGPT / Gemini Imagen 3.** E o que
substitui o motor de geracao do backend.

```yaml
lane_id:      primary
kind:         multi_modal_config
name:         dalle_native
optional:     false
fallback_to:  null   # this IS the fallback
trigger:      "user explicitly asks 'gera a imagem' / 'cria a foto' / 'quero ver'"
env:          []     # native runtime capability, no env needed
runtime_availability:
  custom_gpt_full:        true   # DALL-E
  chatgpt_projects_enxuto: true   # DALL-E (if plan allows)
  claude_projects:         false  # no native image gen -- user runs DALL-E externally OR uses L3
  gemini_gems:             true   # Imagen 3 native
limitations_honest:
  - "1 image per call -- NOT the 3x3 grid 9-em-1 of original Gemini backend"
  - "DALL-E does not honor --ar/--v (Midjourney) nor Steps/CFG (Stable Diffusion)"
  - "Pure white RGB 255,255,255 NOT guaranteed -- guide user to remove bg in post"
  - "DALL-E may rewrite/adorn prompt internally; output varies"
```

## 2. UPGRADE LANES (declared OPTIONAL per runtime)

### LANE L1 -- Gemini Pro Vision (closes `vision-analyze` gap)

> CEXAI typed kind: [[vision_tool]] -- upload analysis via Gemini Pro Vision.

```yaml
lane_id:      L1
kind:         vision_tool
name:         gemini_pro_vision
optional:     true
fallback_to:  dalle_native   # if missing GEMINI_API_KEY -> fall back to text extraction
trigger:      "user uploads product photo AND opts in via GEMINI_API_KEY env"
env:
  required: [GEMINI_API_KEY]
  optional: [GEMINI_MODEL]   # default "gemini-2.5-pro"
runtime_availability:
  gemini_gems:           native_no_env_needed
  claude_projects:       via_mcp_server   # claude/.mcp.json wiring
  custom_gpt_full:       false
  chatgpt_projects_enxuto: false
extracted_fields:
  - color_hex
  - color_name
  - material
  - shape
  - brand_visible
  - category_guess
  - key_features
  - background_color
confidence_marker_required: true   # any inference -> "(confirme)"
```

### LANE L2 -- Gemini 2.5 Flash Image grid (closes `generate-unified` gap)

> CEXAI typed kind: [[multi_modal_config]] -- 9-scene grid in one call.

```yaml
lane_id:      L2
kind:         multi_modal_config
name:         gemini_flash_image_grid
optional:     true
fallback_to:  dalle_native   # if env missing -> fall back to 9x sequential DALL-E calls
trigger:      "user explicitly asks 'gera o grid completo de 9 cenas em uma chamada'"
env:
  required: [GEMINI_API_KEY]
  optional: [GEMINI_IMAGE_MODEL]   # default "gemini-2.5-flash-image"
runtime_availability:
  gemini_gems:           native_no_env_needed
  claude_projects:       via_mcp_server
  custom_gpt_full:       false
  chatgpt_projects_enxuto: false
chained_prompt: prompt_template_v9_grid   # ver P03 sec. 11 + audit section 3.2
char_budget_grid: 2300   # build_grid_prompt v9.0 limit
```

### LANE L3 -- ComfyUI local pipeline (CEXAI factory parity)

> CEXAI typed kind: [[multi_modal_config]] -- local ComfyUI workflow.

```yaml
lane_id:      L3
kind:         multi_modal_config
name:         comfyui_local
optional:     true
fallback_to:  dalle_native
trigger:      "user opts in via env COMFYUI_HOST AND runtime supports tool-call to local"
env:
  required: [COMFYUI_HOST]      # ex: "http://localhost:8188"
  optional: [COMFYUI_WORKFLOW_FILE]   # default "imagens_grid_v1.json"
runtime_availability:
  claude_projects:       via_mcp_server_only
  gemini_gems:           false
  custom_gpt_full:       false
  chatgpt_projects_enxuto: false
reference: ".claude/skills/cexai-factory.md (stage Motion bucket + Image gen)"
note: "Requires local ComfyUI install (Tools/ComfyUI_windows_portable equivalent)"
```

### LANE L4 -- Qwen3-VL local vision (free, no API key)

> CEXAI typed kind: [[vision_tool]] -- local Ollama-hosted vision-language model.

```yaml
lane_id:      L4
kind:         vision_tool
name:         qwen3_vl_ollama
optional:     true
fallback_to:  dalle_native
trigger:      "user has Ollama running + 'qwen2.5vl' model pulled"
env:
  required: [OLLAMA_HOST]   # ex: "http://localhost:11434"
  optional: [OLLAMA_VISION_MODEL]   # default "qwen2.5vl"
runtime_availability:
  claude_projects:       via_mcp_server
  custom_gpt_full:       false
  chatgpt_projects_enxuto: false
  gemini_gems:           false
cost: free   # local inference, no API quota
note: "Equivalent to L1 but local + free; same extracted_fields contract"
```

### LANE L5 -- Firecrawl product-URL mining (closes `scrape-product-url` gap)

> CEXAI typed kind: [[browser_tool]] -- style-calibration only, never source of product attrs.

```yaml
lane_id:      L5
kind:         browser_tool
name:         firecrawl_browser
optional:     true
fallback_to:  paste_intake   # if missing FIRECRAWL_API_KEY -> ask user to paste content
trigger:      "user opts in AND input is public marketplace URL AND FIRECRAWL_API_KEY set"
env:
  required: [FIRECRAWL_API_KEY]
  optional: [FIRECRAWL_TIMEOUT]   # default 60
runtime_availability:
  all_4_runtimes: via_firecrawl_http_api   # no native binding needed
usage_constraint: "STYLE CALIBRATION ONLY -- never the source of product attributes"
note: "Per CONVENTION rule: GPTs cannot reliably open marketplace URLs. Firecrawl is the canonical scrape gateway when explicit-opt-in + key present."
```

### LANE L6 -- Code interpreter dimension/format check (ports verbatim)

> CEXAI typed kind: [[code_executor]] -- dimension/format compliance check.

```yaml
lane_id:      L6
kind:         code_executor
name:         dimension_format_check
optional:     true
fallback_to:  prose_advice   # if no code exec, agent gives manual advice
trigger:      "user uploads a file AND asks 'esta foto serve para Amazon main?'"
env:          []
runtime_availability:
  custom_gpt_full:        true
  chatgpt_projects_enxuto: true
  claude_projects:         sandboxed_code_exec
  gemini_gems:             true
checks:
  - width_height_minimum
  - format_compatibility
  - aspect_ratio
```

## 3. Paste-intake helper

> CEXAI typed kind: [[document_loader]] -- structured paste-intake.

When the user pastes a long product description, structure it via paste-intake:
extract category, color, material, shape, finish, dimensions, features. Output
as structured `product_attrs` block (P06 schema).

## 4. Fallback rule (degrade-never)

Any L1-L5 lane that fails (missing env, API error, runtime cannot tool-call)
silently falls back to the primary path with a one-line note:
`[CEXAI lane unavailable -- using DALL-E native fallback]`. The user ALWAYS
gets a deliverable.

## 5. Tabela de decisao (qual ferramenta, quando)

| Situacao | Lane / Ferramenta |
|----------|-------------------|
| Usuario quer so o prompt/direcao | nenhuma (texto) |
| Usuario pede "gera a imagem" | Primary -- DALL-E nativo (1 imagem, prompt DALL-E) |
| Usuario pede grid de 9 cenas em 1 chamada | L2 se env set; else 9x DALL-E sequencial |
| Entrada do produto | descricao digitada OU upload no chat (NUNCA abrir URL) |
| Usuario mandou so um link | L5 se opt-in + key; else peca descricao/upload (sec. 0) |
| Calibrar estilo com concorrentes | L5 best-effort; else paste manual |
| Analise visual de foto enviada | L1 (Gemini Vision) ou L4 (Qwen3-VL Ollama) se opt-in; else text extraction (P11) |
| Checar dimensao/formato de imagem enviada | L6 (code interpreter) |

## 6. O que NAO porta como obrigatorio (so via lanes opcionais)
- Grid 3x3 9-em-1 -- L2 opcional; default = 9x sequencial DALL-E.
- Vision analysis -- L1 / L4 opcionais; default = atributos da descricao.
- Live URL scrape -- L5 opcional; default = paste-intake.
- Supabase storage -- N/A (usuario salva local).
- Strategy planner / prompt rewriter automatico -- manual (este e o core IP do agente).

## 7. Cross-link com CEXAI typed kinds

- [[multi_modal_config-builder]] -- 6 lanes typed
- [[vision_tool-builder]] -- L1 + L4
- [[browser_tool-builder]] -- L5 Firecrawl
- [[code_executor-builder]] -- L6 dimension check
- [[document_loader-builder]] -- paste-intake

## Related CEXAI artifacts

- [[multi-modal-config-builder]] -- modality routing config
- [[vision-tool-builder]] -- vision/image tool binding
- [[browser-tool-builder]] -- headless browser capability
- [[code-executor-builder]] -- sandboxed code-exec tool
- [[document-loader-builder]] -- doc ingestion adapter
