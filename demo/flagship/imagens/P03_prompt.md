---
agent_id: codexa_imagens
pillar: P03
pillar_name: prompt
lang: pt-BR
cexai_reference_kind: [prompt_template, system_prompt, multimodal_prompt, prompt_version]
source: codexa-core (api/core/prompt_builder.py, api/core/prompt_enhancer.py HYPERREALISTIC_SUFFIX + negatives + STYLE_OVERRIDES + build_grid_prompt, api/core/scene_presets.py 13 cat x 9 cenas, records/core/templates/produto_completo/TEMPLATE_PHOTO_PROMPTS.json)
fidelity: full
---

# P03 -- Receitas de Prompt (o "como gerar")

> Nucleo do valor. Porta 100%. Prompts finais em **ingles**. Esta e a maior
> secao do bundle: **quanto mais voce alimentar o prompt com os fragmentos reais
> abaixo, melhor o output.** Prefira fragmentos concretos a descricoes genericas.

> CEXAI typed kinds: 9 [[prompt_template]] (uma por formula) + [[system_prompt]]
> (baseline) + [[multimodal_prompt]] (upload-analysis) + [[prompt_version]]
> (motor-specific: MJ v6.1 / DALL-E / SD).

## 1. Os 3 formatos de motor

### Midjourney
```
[SUBJECT DESCRIPTION], [SETTING/BACKGROUND], [LIGHTING], [CAMERA SPECS],
[STYLE MODIFIERS], [QUALITY TAGS] --ar [RATIO] --v 6.1 --style raw
```
Exemplo:
```
30ml hyaluronic acid serum in a clear glass dropper bottle, pure white seamless
background infinity curve, soft diffused lighting even illumination, shot on
85mm f/5.6 macro lens, minimalist commercial style, professional product
photography, sharp focus, 8k uhd --ar 1:1 --v 6.1 --style raw
```

### DALL-E (formato em prosa -- usado tambem pelo DALL-E NATIVO do GPT)
```
Professional [STYLE] photograph of [PRODUCT]. [SETTING DESCRIPTION].
[LIGHTING DESCRIPTION]. Shot with [CAMERA]. [QUALITY DESCRIPTORS].
```
Exemplo:
```
Professional minimalist photograph of a 30ml hyaluronic acid serum in a clear
glass dropper bottle. Pure white seamless studio background with subtle shadow.
Soft diffused even lighting from a large softbox. Shot with an 85mm macro lens
at f/5.6. Commercial quality, sharp focus, high resolution, photorealistic.
```

### Stable Diffusion
```
Positive: [DETAILED DESCRIPTION], [QUALITY TAGS], [STYLE TAGS]
Negative: [UNWANTED ELEMENTS]
Steps: 30, CFG: 7, Sampler: DPM++ 2M Karras
```

## 2. Montagem por prioridade (do prompt_builder)

O prompt positivo e montado como **prefix + descricao do produto + suffix**,
nesta ordem de categorias (CATEGORY_PRIORITY):

```
marketplace(0) -> background(1) -> product_type(2) -> composition(3)
-> style(4) -> lighting(5) -> camera(6) -> mood(7)
```

- **prefixes** das categorias entram ANTES da descricao (juntados por espaco).
- **descricao do produto** vai no meio.
- **suffixes** entram DEPOIS (juntados por virgula).
- **negative_prompts** de todas as categorias sao concatenados (virgula, dedup).

Regra: categorias `marketplace` e `background` sao **exclusivas** (so 1 cada).
`style`, `mood`, `product_type` sao **empilhaveis**. `lighting`, `camera`,
`composition` sao **recomendado-1** (use 1; mais de 1 ainda funciona).

## 3. Receita por estagio

### Estagio 2 -- prompt primario (regra de ouro)
1. Comece pelo **subject** = a descricao do produto (rica: material, cor, tamanho).
2. Adicione **background** coerente com a cor dominante (P01 sec. 2).
3. Adicione **lighting** derivada do material (P01 sec. 1 -- regra dura).
4. Adicione **camera specs** pelo tamanho (macro p/ tiny, 85mm p/ medium).
5. Adicione **style modifiers** + **quality tags** (>= 4 tags).
6. Para MJ: feche com `--ar [RATIO] --v 6.1 --style raw`.
7. Gere **3 variacoes** mudando 1 eixo cada (fundo, angulo, ou mood).
8. Gere o **negative prompt** (P01 sec. 6).

### Variacoes (sempre 3)
- Var. 1: muda o **fundo** (ex: white -> gradient).
- Var. 2: muda o **angulo/composicao** (ex: front 45 -> top-down flat lay).
- Var. 3: muda o **mood** (ex: minimal -> lifestyle/luxurious).

## 4. Checklist de qualidade do prompt (gate >= 8.0)
- [ ] Prompt primario >= 50 palavras
- [ ] Inclui >= 4 quality tags
- [ ] Negative prompt presente
- [ ] Iluminacao coerente com material (P01 sec. 1)
- [ ] Settings presentes (ratio/steps/cfg) e adequados ao estilo
- [ ] 3+ variacoes geradas
- [ ] Prompt em ingles

## 5. Settings recomendados por estilo
```yaml
product_photo (white bg): aspect 1:1 | steps 30 | cfg 7   | sampler DPM++ 2M Karras
lifestyle:                aspect 4:5 | steps 35 | cfg 6.5
flat_lay:                 aspect 1:1 | steps 30 | cfg 7
social_story:             aspect 9:16| steps 30 | cfg 7
```

## 6. Suffix hiper-realista anti-IA (HYPERREALISTIC_SUFFIX -- producao)

Anexe ao final de prompts de alta fidelidade para evitar o "look de IA". Fragmento EXATO:
```
Shot on Canon EOS R5 full-frame DSLR, 45MP sensor, photorealistic product photography. Kodak Portra 400 color science - natural skin tones, rich midtones, creamy highlights. NOT 3D, NOT illustration, NOT CGI, NOT cartoon, NOT digital art, NOT AI aesthetic. Authentic slight film grain (ISO 400 texture), natural lens bokeh with imperfect circles. Subtle sensor noise in deep shadows, micro color shifts in highlights. Natural lighting falloff and inverse square law visible in scene depth. NOT overly saturated, NOT uncanny valley, NOT artificially perfect symmetry. NOT plastic-smooth surfaces, NOT uniform lighting, NOT HDR tonemapped look. Ultra high detail 8K, award-winning commercial photography, editorial grade.
```

## 7. Negative prompts de producao (use o adequado ao caso)

### Negative completo v7.0 (cena unica / maxima qualidade)
```
blurry, low quality, distorted, watermark, text overlay, logo, 3D render, illustration, CGI, cartoon, anime, painting, drawing, sketch, AI-generated aesthetic, digital perfection, uncanny valley, overly saturated, plastic skin, smooth artificial textures, jpeg artifacts, compression artifacts, banding, ANY text on image, ANY numbers on image, ANY price tags, ANY currency symbols, R$, $, price labels, captions, titles, headers, annotations, text burned into image, inconsistent product across cells, wrong product, wrong color, color shift, wrong material, wrong shape, cropped product, partial product, product cut off at edges, product floating in mid-air, product too small to see, extra fingers, extra limbs, deformed hands, bad anatomy, mannequin-like people, wax figure appearance, HDR tonemapping, over-processed, smartphone quality
```

### Negative condensado (grid / budget apertado -- CONDENSED_NEGATIVE)
```
text, numbers, prices, labels, watermark, logo, caption, 3D render, CGI, illustration, cartoon, anime, AI aesthetic, grid lines, uneven cells, misaligned grid, wrong product, product substitution, wrong color, color shift, floating product, product too small, extra fingers, deformed hands, bad anatomy, mannequin, blurry, overexposed, HDR look, plastic skin, over-saturated
```
Reforcos por marketplace: Amazon -> adicionar `colored background in cell 9`;
Shopee -> adicionar `product smaller than 50% in cell 9`.

## 8. STYLE_OVERRIDES -- backgrounds/luz por estilo (cells 1, 2, 6)

Fragmentos reais de producao. Cada estilo redefine as cenas 1/2/6 + o "film look":

| Estilo | Cell 1 (hero) | Cell 2 (3/4) | Cell 6 (macro) | Film |
|--------|---------------|--------------|----------------|------|
| **clean** | `pure white #FFF, centered hero, MINIMAL shadow, flat even 85mm f/8` | `light gray gradient, 3/4 angle, NO props, clean lines, 85mm f/5.6` | `white seamless, macro detail, clinical precision, ring light even` | Fujifilm Provia precision, clean neutral tones |
| **luxo** | `DARK charcoal gradient, centered hero, DRAMATIC spot + gold rim, 85mm f/4` | `MARBLE surface, low angle, LEATHER/VELVET texture, warm accent, 85mm` | `BLACK velvet, macro, GOLD foil detail, chiaroscuro twin spots` | Kodak Ektar rich depth, warm luxury tones |
| **vibrante** | `COLORFUL gradient (product-color to complementary), hero, SATURATED, 85mm` | `BOLD colored surface, dynamic TILT angle, color-blocked props, 85mm` | `NEON accent bg, macro detail, vivid color POP, dramatic RGB spots` | Fujifilm Velvia maximum saturation, punchy vivid |
| **natural** | `WOOD surface, centered hero, DAPPLED natural light, 85mm f/4` | `LINEN texture bg, 3/4 angle, BOTANICAL props, soft window light, 85mm` | `STONE surface, macro detail, ORGANIC texture, warm focused spot` | Kodak Portra 400, warm natural tones |
| **minimalista** | `pure white #FFF, centered hero, ZERO props, NO shadow, 85mm f/8` | `off-white seamless, GEOMETRIC angle, single accent line, 85mm` | `neutral gray, macro, CLEAN material detail, single diffused spot` | Fujifilm Acros minimalist contrast |

Aliases: luxury->luxo, vibrant->vibrante, minimal->minimalista, organic->natural. Default=clean.

## 9. Compliance da Cell 9 por marketplace (fragmentos EN de producao)

```
amazon_br:     pure white RGB(255,255,255) background, product 85% of frame, no text, no logos, no props, minimum 1000x1000px, Amazon TOS compliant
mercado_livre: white or neutral background, high resolution, no watermarks, 1:1 aspect ratio, Mercado Livre compliant
shopee:        white or colorful background allowed, infographics allowed, minimum 500x500px, Shopee compliant
magalu:        white background preferred, product centered, high quality mandatory, no text overlay, Magalu compliant
geral:         clean white background, product centered, high quality, marketplace ready, universal compliance
```

## 10. Matriz cenas 3,4,5,7,8 por categoria (CATEGORY_CONTEXTS -- condensado de producao)

Cenas category-driven. Use o fragmento da categoria detectada (cells 1,2,6 vem do estilo sec. 8; cell 9 do sec. 9):

**beleza** -- 3: `close-up applying product to skin, real texture visible, vanity mirror, warm 50mm` . 4: `flat-lay product with cotton pads, brushes, flowers, marble surface, overhead 35mm` . 5: `product on bathroom shelf in morning routine, natural daylight` . 7: `glowing skin result after use, soft satisfied expression, golden hour 85mm portrait` . 8: `product as centerpiece on elegant vanity, editorial composition, soft backlight`

**decoracao** -- 3: `hands adjusting product placement on shelf, styling in real room, warm close-up` . 4: `flat-lay product with complementary decor items, fabric swatches, overhead shot` . 5: `product in styled living room, natural afternoon light, real home environment` . 7: `warm inviting room with product as focal point, cozy glow, 85mm shallow focus` . 8: `product as hero in magazine-worthy interior, editorial wide shot`

**moda** -- 3: `close-up product being worn or styled, outfit detail visible, mirror light, 50mm` . 4: `flat-lay product with coordinated accessories, jewelry, shoes, curated overhead` . 5: `product worn naturally on city street, urban setting, 35mm` . 7: `confident person enjoying the look, genuine expression, 85mm portrait` . 8: `product styled as hero piece in boutique setting, editorial fashion`

**alimentos** -- 3: `close-up product in cooking preparation, warm daylight 50mm` . 4: `flat-lay product with fresh ingredients, cutting board, herbs, rustic overhead` . 5: `product on set table during meal, warm ambient light` . 7: `delicious served dish featuring product, appetizing steam, warm 85mm` . 8: `product in curated kitchen scene, cookbook-style editorial, golden light`

**eletronicos** -- 3: `close-up hands connecting product, real desk setup, LED accent, detail 50mm` . 4: `flat-lay product with cables, accessories, tech gadgets, dark desk overhead` . 5: `product in real workspace, multiple screens, 35mm` . 7: `clean efficient workspace powered by product, cool 85mm` . 8: `product as hero in modern tech setup, window sidelight`

**pet** -- 3: `close-up pet engaging with product, paws and texture detail, warm 50mm` . 4: `flat-lay product with pet treats, leash, toys, cozy blanket, overhead` . 5: `product in use during park walk, dappled light, 35mm` . 7: `happy pet resting near product, content expression, warm 85mm portrait` . 8: `product as focal point in cozy pet-friendly home, soft light`

**esportes** -- 3: `close-up athlete gripping product mid-action, sweat detail, 50mm` . 4: `flat-lay product with gym gear, water bottle, towel, energetic overhead` . 5: `product in real gym or outdoor training, active context, 35mm` . 7: `post-workout glow with product nearby, dramatic 85mm` . 8: `product as hero in athletic setting, dynamic light`

**bebes** -- 3: `close-up parent hands using product on baby, gentle detail, soft warm 50mm` . 4: `flat-lay product with baby essentials, blanket, pacifier, pastel overhead` . 5: `product in cozy nursery, natural daylight` . 7: `peaceful baby content near product, creamy 85mm bokeh` . 8: `product as centerpiece in curated nursery, airy light`

**brinquedos** -- 3: `close-up child hands playing with product, colorful interaction, bright 50mm` . 4: `flat-lay product with play accessories, crayons, stickers, cheerful overhead` . 5: `product in playroom, bright colorful environment, 35mm` . 7: `child delighted mid-play, genuine wonder, colorful 85mm` . 8: `product as hero in creative playroom, cheerful light`

**automotivo** -- 3: `close-up hands installing product on vehicle, garage detail, work light 50mm` . 4: `flat-lay product with automotive tools, cleaning supplies, organized overhead` . 5: `product installed on vehicle, driveway/garage, 35mm` . 7: `polished vehicle detail featuring product result, 85mm` . 8: `product as hero in clean garage setup, accent light`

**moveis** -- 3: `close-up hands touching product surface, craftsmanship, warm 50mm` . 4: `flat-lay product detail with fabric samples, decor items, design overhead` . 5: `product in furnished living room, natural afternoon light` . 7: `person comfortably using product, warm creamy 85mm bokeh` . 8: `product as hero in showroom setting, balanced light`

**outros** -- 3: `close-up hands demonstrating product main function, soft 50mm` . 4: `flat-lay product with related accessories, clean overhead` . 5: `product in its natural use environment, ambient light, 35mm` . 7: `positive result from using product, satisfied expression, warm 85mm` . 8: `product as focal point in clean modern space, natural light`

## 11. Biblioteca de 9 formulas de prompt (TEMPLATE_PHOTO_PROMPTS -- photo_agent)

> CEXAI typed kinds: each of the 9 formulas is a typed [[prompt_template]].

Formulas parametrizaveis (substitua `{{...}}` por atributos REAIS do usuario; nunca invente):

1. **HERO / Packshot** -- `Professional e-commerce product photography of {{PRODUCT}} {{SIZE}} with {{FEATURE}}, {{COLOR}} {{FINISH}} finish. Front 3/4 view. Pure white #FFFFFF background, centered 85% frame. Softbox key front-left 45deg, fill front-right 30%, rim back 20%. Ultra-sharp 8K, no text, no logos, no watermarks. Marketplace compliant.` (1:1, white bg)
2. **DETAIL macro** -- `Professional macro product photography extreme close-up of {{FEATURE}} on {{PRODUCT}}, {{COLOR}} {{FINISH}} finish. Top-down 45deg. Soft neutral gray gradient blur. Rim light behind to highlight contours, soft diffused key front. Ultra-sharp 8K macro, craftsmanship quality.` (1:1, gray gradient)
3. **LIFESTYLE 1** -- `Professional lifestyle product photography of {{PRODUCT}} placed {{PLACEMENT}}. {{ENVIRONMENT}} with blurred {{BACKGROUND}}. Natural {{LIGHTING}}, {{TONES}} tones. Product prominent foreground, rule of thirds. 8K editorial.` (4:5)
4. **LIFESTYLE 2 / workspace** -- `...positioned {{PLACEMENT}}. {{ENVIRONMENT}} workspace with {{PROPS}}. Natural window light left side, warm daylight. Sophisticated minimalist aesthetic. 8K commercial.` (4:5)
5. **LIFESTYLE 3 / cozy flat-lay** -- `...arranged in cozy composition. Overhead 45deg with {{PROPS}} on {{SURFACE}}. Warm ambient inviting atmosphere. Harmonious prop arrangement. 8K, Instagram aesthetic.` (1:1)
6. **IN-USE** -- `Professional lifestyle photography of {{HAND_TYPE}} hand {{ACTION}} {{PRODUCT}}. Side profile showing ergonomic grip, {{FEATURE}} visible. Soft outdoor natural or bright studio, neutral blur. Dynamic action showing scale. 8K.` (4:5)
7. **GROUP / variants** -- `Professional group shot of {{QTY}} {{PRODUCT}}s. Center original flanked by {{VARIANT_1}} and {{VARIANT_2}}. Front view stagger depth. Pure white #FFFFFF. Even multi-softbox, no harsh shadows. 8K, marketplace compliant.` (16:9, white bg)
8. **FLAT LAY / kit** -- `Professional flat lay top-down 90deg of {{PRODUCT}} with {{CONTEXT}} essentials: {{PROPS}} on {{SURFACE}}. Soft overhead diffused, no harsh shadows. Symmetrical balance, negative space. 8K, social ready.` (1:1)
9. **EMOTIONAL / brand** -- `Professional lifestyle photography of {{PRODUCT}} on clean white surface with {{THEMED_ELEMENTS}}. Pure white #FFFFFF (compliance) + emotional connection. Warm cozy lighting. Composition echoing {{ECHO_ELEMENT}}. Shareable for {{COMMUNITY}}. 8K, marketplace compliant.` (1:1, white bg)

Regra-de-ouro destas formulas (`hard_rule_applied`): SEMPRE incluir a imagem de
referencia quando houver, e SEMPRE preencher `{{...}}` com dado fornecido --
nunca fabricar atributo. Cenas com fundo branco: HERO, GROUP, EMOTIONAL.

## 12. Placeholders inteligentes por categoria (SMART_PLACEHOLDERS -- hints de input)

> CEXAI typed kind: [[synthetic_data_config]] -- typed hint generator.

Quando faltar input, oferece estes exemplos (PT-BR) como hint -- NAO como fato do produto:

- **beleza**: subject "Serum facial com acido hialuronico 30ml" . surface "Marmore branco com gotas" . mood "Fresco, spa-like"
- **decoracao**: subject "Vela aromatica de soja 200g" . surface "Bandeja de madeira rustica" . mood "Caloroso, intimista"
- **moda**: subject "Tenis casual couro branco unissex" . surface "Concreto urbano" . mood "Urbano, confiante"
- **eletronicos**: subject "Fone bluetooth ANC over-ear preto" . surface "Mesa escritorio escura" . lighting "Rim light neon azul + key suave"
- **alimentos**: subject "Granola artesanal com castanhas 500g" . surface "Tabua de madeira com ingredientes" . lighting "Luz natural lateral, backlight"
- **pet**: subject "Coleira ajustavel nylon cachorro medio" . surface "Grama verde" . mood "Feliz, energetico"
- **esportes**: subject "Haltere emborrachado 10kg par" . surface "Piso borracha academia" . mood "Determinado, superacao"
- **outros**: subject "Descreva seu produto com detalhes" . mood "Sentimento que quer transmitir"

## 13. Multimodal binding (upload-analysis prompts)

> CEXAI typed kind: [[multimodal_prompt]] -- chat-uploaded image analysis.

Quando o usuario sobe uma foto no chat (input = imagem), use este prompt
multimodal de extracao (depois passa para Estagio 2 com os atributos extraidos):

```
Analise a foto enviada e extraia APENAS o que e visivel diretamente. Para cada
campo, marque "inferido (confirme)" se houver duvida:
- color_visible (nome + hex aproximado se evidente)
- material_visible (vidro / metal / plastico / tecido / madeira / ceramica / misto)
- shape_visible (cilindrico / retangular / oval / organico / outro)
- size_estimate (tiny / small / medium / large -- referencia ao ambiente se houver)
- background_visible (branco / colorido / lifestyle / outro)
- brand_visible (so se LEGIVEL na foto -- nunca adivinhar marca)
NAO invente. NAO extrapole. Atributo nao-visivel = "[PREENCHER]".
Saida em YAML.
```

## 14. Cross-link com CEXAI typed kinds

- [[prompt_template-builder]] -- 9 formulas typed
- [[system_prompt-builder]] -- agent baseline (00_instructions)
- [[multimodal_prompt-builder]] -- upload analysis
- [[prompt_version-builder]] -- MJ v6.1 / DALL-E / SD revisions tracked

## Related CEXAI artifacts

- [[prompt-template-builder]] -- parameterized prompt contract
- [[system-prompt-builder]] -- system-role prompt artifact
- [[multimodal-prompt-builder]] -- multi-modal prompt template
- [[prompt-version-builder]] -- prompt versioning record
