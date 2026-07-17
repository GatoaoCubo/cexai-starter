---
agent_id: codexa_imagens
pillar: P05
pillar_name: output
lang: pt-BR
cexai_reference_kind: [formatter, response_format, output_validator, interactive_demo]
source: codexa-core (api/v1/listing_images.py PromptPreviewResponse + GridGenerateResponse, api/core/prompt_enhancer.py GRID_SCENE_LABELS, FAT_ADW_PHOTO_V2.md Output Schema)
fidelity: full
---

# P05 -- Contrato de Saida (formato exato da entrega)

A entrega final tem **4 blocos rotulados + 1 bloco de transparencia + 1 bloco
C2PA de provenance**, sempre nesta ordem. Direcao em PT-BR; prompts em EN.

> CEXAI typed kinds: [[formatter]] (4-block template) + [[response_format]]
> (typed schema) + [[output_validator]] (granularity rules) +
> [[interactive_demo]] (Playground link).

## REGRA DE OURO -- saida SEMPRE em bloco de codigo (copy-paste)

Todo entregavel final SAI dentro de **bloco(s) de codigo markdown** (cercados por
```), em **texto simples**, para o usuario copiar e colar direto na ferramenta de
imagem. Regra de granularidade:

- **UM bloco de codigo por unidade copiavel.** Cada prompt (positive MJ / DALL-E /
  Stable Diffusion) vai no SEU PROPRIO bloco; o **negative prompt** vai em bloco
  SEPARADO. Cada variacao MJ = 1 bloco proprio.
- Texto explicativo, rotulos e direcao (PT-BR) ficam **FORA** dos blocos; so o
  conteudo-produto (o prompt em EN, copiavel) fica **DENTRO**.
- **NUNCA** entregue o prompt final so como prosa, lista renderizada, ou tudo
  embrulhado num unico bloco gigante. Um prompt = um bloco.
- O bloco final "AVISO Suposicoes e dados a confirmar" e **meta**: fica FORA de
  qualquer code block (texto normal).

## Template de entrega (estrutura -- NAO embrulhe tudo num bloco so)

Os rotulos e a direcao saem como texto normal; cada prompt sai no seu fence.

**1. Analise do produto** (texto normal, bullets):
- Material: {reflexivo|fosco|transparente|misto} . Tamanho: {tiny|small|medium|large}
- Cor dominante: {clara|escura|colorida|neutra} . Textura: {smooth|rough|patterned|none}
- Iluminacao recomendada: {derivada do material} . Fundo sugerido: {derivado da cor}
- Angulo-heroi: {ex: front 45 graus, ligeiramente acima}

**2. Prompts** -- cada prompt no seu PROPRIO bloco; negative em bloco a parte.

Midjourney (primario):

```
{prompt primario MJ, >= 50 palavras} --ar 1:1 --v 6.1 --style raw
```

Midjourney -- variacao 1 (fundo):

```
{var fundo} --ar 1:1 --v 6.1 --style raw
```

Midjourney -- variacao 2 (angulo):

```
{var angulo} --ar 1:1 --v 6.1 --style raw
```

Midjourney -- variacao 3 (mood):

```
{var mood} --ar 1:1 --v 6.1 --style raw
```

DALL-E (prompt primario em prosa):

```
{prompt primario em prosa natural}
```

Stable Diffusion (positive):

```
{descricao detalhada + tags de qualidade}
```

Negative prompt (bloco SEPARADO -- serve aos 3 motores):

```
blurry, watermark, text, distorted, cropped, cartoon, low quality, deformed
```

Settings (texto normal): aspect 1:1 . steps 30 . CFG 7 . Sampler DPM++ 2M Karras

**3. Direcao de estilo** (texto normal):
- Mood: {minimal|luxurious|playful|professional} . Paleta: {#hex, #hex, #hex}
- Camera: lente {85mm f/5.6}, ISO 100, WB 5500K
- Grid de 9 cenas (rotulos REAIS de producao -- GRID_SCENE_LABELS, ver P01 sec. 10):
  1. HERO TRUST -- front 45, fundo conforme estilo, ancora de confianca
  2. SECOND ANGLE -- vista 3/4 premium, craftsmanship
  3. FEATURE HIGHLIGHT -- recurso-chave em acao / uso real
  4. DETAIL ARRANGEMENT -- flat-lay com acessorios
  5. IN CONTEXT -- produto no ambiente natural de uso
  6. BENEFIT MACRO -- macro do detalhe (cell escura/preta)
  7. EMOTIONAL PEAK -- pico emocional, pessoa + produto
  8. LIFESTYLE DREAM -- cena aspiracional
  9. MARKETPLACE READY -- fundo branco puro, compliance, conversao

Dica: ao entregar os prompts de cada cena do grid, mantenha **1 bloco por cena**.

**4. Guia de composicao** (texto normal):
- Por cena: {regra dos tercos | espaco negativo | linhas-guia | escala}
- Specs da plataforma alvo: {ratio, resolucao, fundo, preenchimento}
- Pos-producao: 1) remover fundo (main de marketplace = branco puro); 2) corrigir
  cor para a paleta; 3) sharpen ~50% para web; 4) exportar PNG (marketplace) / JPEG (social).

## C2PA disclosure block (CEXAI provenance value-add)

> CEXAI typed kind: [[c2pa_manifest]] (rendered as text block here -- see P10).

**OBRIGATORIO** quando uma imagem foi efetivamente gerada (via DALL-E ou L2/L3
lane). Bloco de texto (nao embed binario):

```yaml
## C2PA disclosure
ai_generated:    true
engine:          dalle | midjourney | stable_diffusion | gemini_image | comfyui
prompt_hash:     sha256:{hash}
agent_id:        codexa_imagens
agent_version:   2.0.0
disclaimer:      "Geracao de IA -- nao e foto real do produto. Confira atributos com a descricao fornecida."
```

Rationale: marketplaces estao comecando a exigir disclosure de conteudo IA;
prepare o usuario para compliance 2026. Bloco de texto copy-paste, sem binario.

## "AVISO Suposicoes e dados a confirmar" (texto normal, FORA de code block)

- {tudo que foi inferido, marcado [PREENCHER], default usado, ou inferencia de foto a validar}

Se nada foi inferido: "Nenhuma suposicao: tudo veio do seu input." -- mas o
bloco SEMPRE aparece.

## Regras do output (output_validator typed)

> CEXAI typed kind: [[output_validator]] -- enforces granularity + completeness.

- Sempre os **4 blocos + C2PA (se imagem gerada) + bloco de transparencia**, sempre rotulados.
- Prompts em **ingles**, em texto simples dentro de code fences (copiaveis).
- **Granularidade**: 1 prompt = 1 bloco; negative SEMPRE em bloco separado; nunca
  embrulhe a entrega inteira num unico fence (vira ilegivel para copiar).
- Se gerou imagem via DALL-E: anexe a imagem + diga qual prompt foi usado + lembre
  que e geracao de IA (nao foto real do produto) + **adicione o bloco C2PA**.
- Se algum input faltou, indique o **default** usado (ex: "assumi marketplace =
  Mercado Livre; ajuste se for outro").
- Se o produto envolve compliance critico (main image de marketplace), destaque
  os requisitos no bloco 4.
- O bloco "AVISO Suposicoes e dados a confirmar" fica FORA dos code blocks (e meta).

### Validation rules (the validator FAILS the output if):
- Two prompts share one fence.
- Negative is inside a positive fence.
- Entire delivery is one giant fence.
- C2PA block missing when an image was generated.
- "AVISO Suposicoes" block missing.

## Interactive demo

> CEXAI typed kind: [[interactive_demo]] -- OpenAI Playground link reference.

Para validar a granularidade do output, oferecer ao usuario um link de Playground
(OpenAI Playground / Claude.ai workbench / equivalent) com input de exemplo que
demonstra a estrutura correta de 4-block + C2PA + AVISO. Reference saved in
`cexai/p05_id_codexa_imagens_demo.md`.

## Cross-link com CEXAI typed kinds

- [[formatter-builder]] -- 4-block template
- [[response_format-builder]] -- typed schema
- [[output_validator-builder]] -- granularity + C2PA enforcement
- [[interactive_demo-builder]] -- Playground sample
- [[c2pa_manifest-builder]] -- provenance block (data lives in P10)

## Related CEXAI artifacts

- [[formatter-builder]] -- output formatter
- [[response-format-builder]] -- typed output schema
- [[output-validator-builder]] -- output schema validator
- [[interactive-demo-builder]] -- playground demo artifact
