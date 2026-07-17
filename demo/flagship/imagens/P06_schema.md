---
agent_id: codexa_imagens
pillar: P06
pillar_name: schema
lang: pt-BR
cexai_reference_kind: [input_schema, validation_schema]
source: codexa-core (api/v1/listing_images.py PromptPreviewRequest/Response + ComplianceCheckRequest/Response + generate_unified Form fields + VisionAnalysisResponse, FAT_ADW_PHOTO_V2.md Input Schema)
fidelity: full
---

# P06 -- Schemas de Entrada e Saida

> CEXAI typed kinds: [[input_schema]] (runtime input contract) + [[validation_schema]]
> (field-level rules with attribute_source: required: user_provided).

## 0. Origem do input -- descricao OU upload, NUNCA URL

> O backend original recebia `scrape-product-url` e `reference_image` (URL) e
> abria a pagina/imagem. **Um bundle autocontido NAO abre URL externa de
> forma confiavel** (anti-bot, JS, login). Portanto o input do produto vem por
> **DUAS vias, nunca por link**:
>
> 1. **Descricao TYPED**: o usuario escreve categoria, cor, material, formato,
>    diferenciais (texto colado do anuncio tambem serve).
> 2. **Imagem UPLOADED**: o usuario sobe a foto DIRETO no chat (nao uma URL).
>
> Se o usuario fornecer SO um link, o agente responde:
> *"Se voce so tem um link, nao consigo abri-lo com confiabilidade -- descreva o
> produto (categoria, cor, material, formato, diferenciais) ou faca upload da
> foto aqui."*

## 1. Input -- obrigatorio

```yaml
required:
  product_name: string   # ex: "serum de acido hialuronico 30ml, frasco de vidro"
  # entrada do produto via UMA das vias abaixo (nunca URL para fetch):
  product_description: string   # texto digitado/colado pelo usuario, OU
  uploaded_image:      file     # foto subida direto no chat (nao URL)
```
Se faltar o nome do produto E nao houver descricao nem upload, **peca** (unica
coisa que trava o fluxo). NUNCA aceite uma URL como se fosse algo que voce abre.

Reject rule: if `product_url:` is the only field provided, return typed error:
`error: "URL fetch unavailable -- provide product_description OR upload an image"`.

## 2. Input -- opcional (com defaults inteligentes)

```yaml
optional:
  style:           product_photo | lifestyle | flat_lay | mockup | infographic
  background:      "white studio" | "lifestyle scene" | "gradient" | "dark"
  lighting:        "soft natural" | "dramatic" | "ring light" | "studio"
  angle:           "front 45" | "top down" | "eye level" | "macro detail"
  props:           ["plant", "fabric", "hands", ...]
  brand_colors:    ["#1a1a2e", "#e94560"]   # hex
  target_platform: instagram | marketplace | website
  marketplace:     amazon | mercado_livre | shopee | magalu | generic
  mood:            minimal | luxurious | playful | professional
  # atributos do produto (substituem a Vision analysis se L1/L4 nao ativa)
  product_color:    string
  product_material: string
  product_shape:    string
```

Defaults quando omitido (ver P09): style=product_photo, marketplace=mercado_livre,
background derivado da cor, lighting derivada do material, mood=professional,
platform=marketplace.

## 3. Campos de atributo do produto (ex-Vision)

O backend extraia isto da foto via Gemini Vision (`VisionAnalysisResponse`).
Sem L1/L4 ativa, o agente extrai os MESMOS campos da **descricao digitada**:

```yaml
color_hex:        string   # se o usuario disser; senao deduza nome da cor
color_name:       string
material:         string   # vidro, metal, plastico, tecido, madeira...
shape:            string   # cilindrico, retangular, organico...
brand_visible:    string   # marca, se mencionada
category_guess:   string
key_features:     string[]
background_color: string
```

## 4. Output schema (resumo -- detalhe em P05)

```yaml
photo_output:
  product_analysis:   object   # material, size, color, texture, lighting, angle
  prompts:
    primary:          string   # MJ
    dalle:            string
    stable_diffusion: object   # positive, negative, settings
    variations:       string[] # 3
    negative_prompt:  string
    recommended_settings: object  # aspect, steps, cfg, sampler
  style_direction:
    mood:             string
    color_palette:    string[]
    camera_settings:  object
    photo_angles:     object[]  # 9 cenas
  composition_guide:
    per_scene:        object[]
    platform_specs:   object
    post_production:  string[]
  c2pa_manifest:      object?   # only if image was generated; see P10
```

## 5. Contratos reais de I/O do backend (listing_images.py -- para fidelidade)

### PromptPreviewRequest -> PromptPreviewResponse
```yaml
# request
product_description: string  # 3..2000 chars (obrigatorio)
template_ids:        string[]
marketplace:         string?  # id de template
background:          string?
styles:              string[] # empilhavel
lighting:            string?
camera:              string?
mood:                string?
# response
positive_prompt:     string
negative_prompt:     string
output_spec:         object   # width/height/format/background_color/quality
compliance_tags:     string[]
template_ids_used:   string[]
valid:               bool
validation_error:    string?  # ex: "Category 'marketplace' is exclusive"
```

### ComplianceCheckRequest -> ComplianceCheckResponse
```yaml
# request
image_url:   string
marketplace: amazon | mercado_livre | shopee | magalu | generic
# response
score:       int 0-100
marketplace: string
passed:      bool          # score>=70 E nenhum check "fail"
checks:      [{name, status: pass|warn|fail, message}]
error:       string?
```

### generate-unified (Form fields reais)
```yaml
product_description, category(default outros), marketplace(default geral),
style(default clean), quality(default high), product_color, product_material,
product_shape, product_benefit, product_audience, brand_colors,
creative_direction, competitor_insights, seed, vision_data_json, reference_image
# DEGRADADO no bundle (lanes opcionais cobrem):
#   reference_image: era URL de imagem -> usuario faz UPLOAD da foto (P04 sec. 0).
#   vision_data_json: vinha do Gemini Vision -> L1/L4 opcionais OU extracao do texto.
```

### VisionAnalysisResponse (degradado por default; L1/L4 lanes restauram)
```yaml
color_hex, color_name, material, shape, brand_visible, category_guess,
key_features: string[], background_color, confidence: float
```

## 6. Validacao (regras duras)

> CEXAI typed kind: [[validation_schema]] -- field-level rules.

- `product_name`/`product_description` nao-vazio (senao peca).
- `prompt primario` >= 50 palavras; grid <= 2300 chars.
- `negative_prompt` presente.
- combinacao de templates: `marketplace` e `background` exclusivos (max. 1 cada).
- `brand_colors`: formato hex `#RRGGBB`.
- iluminacao coerente com material (P01 sec. 1) -- senao corrija.
- `attribute_source: required: user_provided` -- nunca preencher de fonte inferida.

## 7. Anti-alucinacao -- atributos do produto (OBRIGATORIO)

> Fonte de verdade = input do usuario. Especializado para imagens.

1. **So use atributos que o usuario FORNECEU** -- cor, material, tamanho, forma,
   acabamento, composicao, certificacoes, compatibilidades. Nunca preencha um
   `{{...}}` da formula (P03 sec. 11) com suposicao.
2. **PROIBIDO fabricar para "enriquecer o prompt"**: cor/material/dimensao que o
   usuario nao disse, numeros (peso, volume, voltagem), certificacoes
   (INMETRO/ANVISA), claims ("antibacteriano", "premium"), marca, origem, preco.
3. **Lacuna de campo do schema -> pergunte OU marque `[PREENCHER: <campo>]`**,
   nunca invente.
4. **A foto enviada NAO e fonte confiavel de atributo por DEFAULT** (sem L1/L4):
   se inferir algo da imagem do chat, marque "(confirme)" e peca validacao.
5. **Sugestoes de paleta/estilo (P01 sec. 12) sao sugestao, nao fato do produto**.
6. Os SMART_PLACEHOLDERS (P03 sec. 12) sao HINTS de exemplo -- jamais trate o
   exemplo como se fosse o produto real do usuario.
7. **NUNCA finja ter aberto uma URL.** Se o usuario so mandou um link, peca
   descricao ou upload.

## 8. Cross-link com CEXAI typed kinds

- [[input_schema-builder]] -- runtime input contract
- [[validation_schema-builder]] -- field-level rules + attribute_source

## Related CEXAI artifacts

- [[input-schema-builder]] -- typed input contract
- [[validation-schema-builder]] -- JSON-Schema validation
