---
agent_id: codexa_imagens
pillar: P01
pillar_name: knowledge
lang: pt-BR
cexai_reference_kind: [knowledge_card, dataset_card, few_shot_example, synthetic_data_config]
source: codexa-core (api/core/compliance_checker.py MARKETPLACE_SPECS, api/core/prompt_enhancer.py PNL triggers + scene labels + STYLE_OVERRIDES, api/core/prompt_quality.py keyword banks)
fidelity: full
---

# P01 -- Base de Conhecimento (Foto de Produto)

Conhecimento que codexa-imagens precisa saber de cor. Tudo aqui PORTA 100% -- e
IP de engenharia de prompt, nao infraestrutura.

> CEXAI typed kind: [[knowledge_card]] -- master KC for the domain.
>
> Companion typed kinds:
> - [[dataset_card]] -- the 13 template fragments as a typed dataset (P09 anchor).
> - [[few_shot_example]] x 9 -- the grid scene formulas (P03 anchor).
> - [[synthetic_data_config]] -- the SMART_PLACEHOLDERS hints (P03 anchor).

## 1. Matriz Material -> Iluminacao (regra dura)

A iluminacao e DERIVADA do material. Nunca contrarie esta tabela.

| Tipo de material | Exemplos | Iluminacao obrigatoria | Por que |
|------------------|----------|------------------------|---------|
| **Reflexivo** | vidro, metal, cromado, espelhado, joias | difusa / softbox grande, sem reflexos duros | hotspots queimam o produto |
| **Transparente** | garrafa de vidro, acrilico, frasco | backlight (luz por tras) + difusa | revela conteudo e forma |
| **Fosco (matte)** | madeira, tecido, ceramica, papel | livre -- qualquer luz funciona | superficie perdoa |
| **Misto** | eletronicos, embalagem | combinacao difusa + acento | partes reflexivas + foscas |

## 2. Matriz de Analise do Produto (Estagio 1)

```yaml
material_type:    reflective | matte | transparent | mixed
size_category:
  tiny:   "joias, acessorios"        -> lente macro, foco em detalhe
  small:  "cosmeticos, capinhas"     -> close-up padrao
  medium: "garrafas, bolsas, tenis"  -> full product shot
  large:  "moveis, eletrodomesticos" -> grande angular, contexto
color_dominant:
  light:    "branco, creme, pastel"  -> fundo escuro p/ contraste
  dark:     "preto, marinho"         -> fundo claro p/ contraste
  colorful: "multicor, estampado"    -> fundo neutro
  neutral:  "cinza, bege, marrom"    -> fundo de acento
texture_type:
  smooth:    "liquido, gel, creme"   -> realcar brilho/sheen
  rough:     "natural, artesanal"    -> realcar textura
  patterned: "tecido, trancado"      -> mostrar detalhe
  none:      "cor solida, plastico"  -> focar na forma
```

## 3. Biblioteca de Quality Tags (universal)

Use SEMPRE pelo menos 4 destas no prompt positivo:
`professional product photography`, `commercial quality`, `sharp focus`,
`high resolution`, `8k uhd`, `studio quality`, `photorealistic`.

## 4. Biblioteca de Iluminacao (frases prontas -- EN)

| Estilo | Frase para o prompt |
|--------|---------------------|
| soft | `soft diffused lighting, even illumination` |
| dramatic | `dramatic side lighting, deep shadows` |
| natural | `natural window light, golden hour` |
| studio | `3-point studio lighting, key fill rim` |
| ring | `ring light, even illumination` |
| backlight | `backlit, rim light highlighting edges` |

## 5. Biblioteca de Fundo (frases prontas -- EN)

| Tipo | Frase |
|------|-------|
| white | `pure white seamless background, infinity curve` |
| lifestyle | `modern living room setting, styled scene` |
| gradient | `smooth gradient background, color transition` |
| contextual | `in-use context, real environment` |
| dark | `dark moody background, dramatic contrast` |

## 6. Negative Prompt (SEMPRE incluir)

`blurry, out of focus, low quality, watermark, text, logo overlay, distorted,
deformed, ugly, oversaturated, overexposed, cartoon, illustration, painting,
cropped, cut off, partial product, extra objects, cluttered`

## 7. Specs de Compliance por Marketplace (imagem principal)

Portado de `compliance_checker.py` (MARKETPLACE_SPECS):

| Marketplace | Min. dimensao | Formatos | Fundo branco? | Preenchimento min. |
|-------------|---------------|----------|---------------|--------------------|
| **Amazon BR** | 2000x2000 | jpeg, png, tiff, gif | sim (tol. 25) | 85% |
| **Mercado Livre** | 1200x1200 | jpeg, png | sim (tol. 30) | 80% |
| **Shopee** | 1200x1200 | jpeg, png | sim (tol. 35) | sem minimo |
| **Magalu** | 1200x1200 | jpeg | nao exige | sem minimo |
| **Generico** | 1080x1080 | jpeg, png, webp | nao exige | sem minimo |

Pontuacao de compliance (peso): dimensoes 30, fundo 30, preenchimento 25,
formato 15. Aprovado = score >= 70 e nenhum check em "fail".

## 8. Specs por Plataforma social

```yaml
instagram_feed:  ratio 1:1 ou 4:5  | 1080x1080 ou 1080x1350 | lifestyle/styled
instagram_story: ratio 9:16        | 1080x1920
reel_cover:      ratio 9:16        | 1080x1920
amazon_zoom:     min 1600px no lado maior (habilita zoom)
```

## 9. Estilos de Referencia (citaveis na direcao)

- "Apple product page minimalism" (limpo, fundo branco, sombra suave)
- "Glossier lifestyle photography" (pastel, maos, contexto intimo)
- "Amazon A+ Content professional" (infografico, comparativo, escala)

## 10. As 9 cenas do grid de producao (GRID_SCENE_LABELS)

O grid 3x3 tem estas 9 cenas FIXAS (ordem real do `prompt_enhancer`):

| # | Label | Proposito | Gatilho PNL |
|---|-------|-----------|-------------|
| 1 | HERO TRUST | 1a impressao, ancora de confianca, main image | trust anchor |
| 2 | SECOND ANGLE | vista alternativa premium, craftsmanship | detail anchor |
| 3 | FEATURE HIGHLIGHT | recurso-chave em acao, uso real | capability anchor |
| 4 | DETAIL ARRANGEMENT | flat-lay com acessorios/complementos | ecosystem anchor |
| 5 | IN CONTEXT | produto no ambiente natural de uso | context anchor |
| 6 | BENEFIT MACRO | prova macro do recurso, evidencia de qualidade | proof anchor |
| 7 | EMOTIONAL PEAK | pico de conexao emocional, prazer | emotional peak |
| 8 | LIFESTYLE DREAM | posicionamento aspiracional | lifestyle aspiration |
| 9 | MARKETPLACE READY | imagem conversao-pronta, fundo branco compliance | purchase anchor |

Cell 9 e IMUTAVEL: `pure white #FFFFFF, product centered, 85% frame fill, 85mm f/8,
high-key soft-even no shadows, marketplace compliant`.

## 11. Arquetipos de cena (PHOTO_BASE -- imagem unica)

Frases-base de producao por tipo de cena (use como abertura do prompt EN):

| Tipo | Frase-base (EN, da producao) |
|------|------------------------------|
| **hero** | `Professional e-commerce product photography, centered, high-key softbox, Canon EOS R5 85mm f/8, photorealistic, 8K marketplace compliant` |
| **lifestyle** | `Lifestyle product photography, natural environment, 35mm f/2.8, warm ambient light, photorealistic, 8K` |
| **macro** | `Macro detail product shot, ring light, 100mm macro f/2.8, extreme detail visible, photorealistic, 8K` |
| **comparison** | `Side-by-side comparison product shot, even lighting, consistent framing, studio setup, photorealistic, 8K` |

## 12. Gatilhos PNL + psicologia de cor por categoria (CATEGORY_PNL_TRIGGERS)

Para cada categoria, gatilhos emocionais + paleta + cenas a enfatizar.

| Categoria | Gatilhos | Psicologia de cor (hex) | Cenas-enfase |
|-----------|----------|-------------------------|--------------|
| beleza | aspiration, transformation, pleasure, self-confidence, radiance | #9B59B6 #F5CBA7 #FFFFFF | 3,6,7 |
| pet | belonging, intimacy, warmth, unconditional love, joy | #F5CBA7 #27AE60 #F4D03F | 5,7,4 |
| eletronicos/tech | trust, innovation, authority, precision, efficiency | #2E86AB #2C3E50 #34495E | 6,8,1 |
| decoracao | belonging, aspiration, comfort, harmony, home pride | #FEF9E7 #D4AC0D #27AE60 | 4,8,5 |
| moda | aspiration, belonging, pleasure, identity, style | #1A1A1A #9B59B6 #E74C3C | 5,7,8 |
| alimentos | pleasure, belonging, warmth, nostalgia, nourishment | #E74C3C #F39C12 #F4D03F | 5,7,3 |
| esportes | energy, achievement, endurance, motivation, vitality | #F39C12 #E74C3C #1A1A1A | 3,7,4 |
| bebes | protection, tenderness, trust, safety, nurturing | #F5B7B1 #AED6F1 #FFFFFF | 4,7,5 |
| brinquedos | joy, imagination, play, discovery, fun | #F4D03F #F39C12 #E74C3C | 5,7,3 |
| automotivo | power, reliability, precision, freedom, performance | #1A1A1A #2E86AB #BDC3C7 | 6,1,8 |
| moveis | comfort, elegance, space, harmony, craftsmanship | #8B6914 #FEF9E7 #27AE60 | 4,8,7 |
| outros | quality, value, satisfaction, reliability, trust | #FFFFFF #F2F4F4 #2E86AB | 1,6,9 |

Use os gatilhos como "Mood" do prompt; use a paleta quando o usuario nao
fornecer brand_colors (mas avise que e SUGESTAO, nao cor confirmada -- P11
anti-alucinacao).

## 13. Deteccao automatica de categoria (keyword banks, PT+EN)

Palavras-chave reais que mapeiam descricao -> categoria (limiar 2.0, da producao):
- **beleza**: creme, hidratante, serum, skincare, maquiagem, batom, shampoo, perfume, protetor solar, cosmetico, makeup, sunscreen
- **decoracao**: vela/candle, joia/jewelry, colar, anel, brinco, decor, vaso, almofada, luminaria, aromatizador, difusor
- **moda**: camiseta/t-shirt, calca, vestido/dress, jaqueta, roupa, tenis/sneaker, sapato, bolsa/bag, mochila, bone, chapeu
- **eletronicos**: fone/headphone, bluetooth, celular/smartphone, tablet, notebook/laptop, monitor, teclado, mouse, smartwatch, drone, console
- **alimentos**: chocolate, cafe/coffee, cha/tea, mel, azeite, granola, whey, suplemento, organico, gourmet, artesanal, vegano
- **pet**: pet, cachorro/dog, gato/cat, racao, coleira, petisco, brinquedo pet, cama pet, aquario
- **esportes**: fitness, academia/gym, yoga, treino/workout, bicicleta/bike, corrida, haltere/dumbbell
- **bebes**: bebe/baby, infantil, fralda, mamadeira, carrinho/stroller, berco/crib, maternidade, chupeta
- **brinquedos**: brinquedo/toy, boneca/doll, lego, puzzle/quebra-cabeca, pelucia/plush, educativo
- **automotivo**: carro/car, pneu/tire, oleo, motor, moto/motorcycle, veiculo, gps
- **moveis**: mesa, cadeira/chair, sofa, estante, armario, cama, movel/furniture, rack, escrivaninha/desk

## 14. Extracao de atributos da descricao (extract_keywords -- so do texto do usuario)

Padroes reais para extrair atributos do que o usuario ESCREVEU (nunca inventar):
- **cor**: branco, preto, rosa, vermelho, azul, verde, dourado, prateado, nude, bordo, vinho... / white, black, gold, silver...
- **material**: madeira, ceramica, vidro, metal, couro, tecido, algodao, seda, bambu, acrilico, silicone, marmore, soja, cera, cristal, aco
- **forma**: redondo, quadrado, retangular, oval, cilindrico, hexagonal, compacto, slim, mini, grande, pequeno
- **beneficio**: hidratante, calmante, relaxante, nutritivo, protetor, antibacteriano, antioxidante, natural, organico, artesanal, vegano
- **publico**: masculino, feminino, unissex, infantil, adulto, jovem, profissional, gestante, atleta

Regra: estes sao gatilhos de LEITURA do input -- se o usuario nao disse a
cor/material, o campo fica vazio e voce PERGUNTA ou marca `[PREENCHER]` (P06/P11).
Nunca preencha por deducao visual de uma foto.

## Cross-link com CEXAI typed kinds

- [[knowledge_card-builder]] -- master KC pattern
- [[dataset_card-builder]] -- 13 template fragments dataset
- [[few_shot_example-builder]] -- 9 grid scene formulas
- [[synthetic_data_config-builder]] -- SMART_PLACEHOLDERS hints

## Related CEXAI artifacts

- [[knowledge-card-builder]] -- typed knowledge unit (KC)
- [[dataset-card-builder]] -- dataset metadata contract
- [[few-shot-example-builder]] -- in-prompt exemplar
- [[synthetic-data-config-builder]] -- synthesis generator config
