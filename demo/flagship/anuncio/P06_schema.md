---
agent: anuncio
pillar: P06
pillar_name: schema
lang: pt-BR
source: api/v1/anuncios.py (AnuncioRequest, AnuncioV2Request, AnuncioResponse, AnuncioFullResponse); records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (Input/Output Schema)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: input_schema
cexai_typed_artifacts:
  - cexai/input_schema_anuncio_request.md
  - cexai/validation_schema_anuncio_output.md
  - cexai/enum_def_marketplace.md
  - cexai/enum_def_brand_voice.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P06 -- Schemas de Entrada e Saída

Inputs obrigatórios, campos, validação e o shape de saída.

> **Camada CEXAI:** schema canônico em [[cexai/input_schema_anuncio_request]] (4 obrigatórios + 8 opcionais + paste + handoff) e [[cexai/validation_schema_anuncio_output]] (12 campos validados). Enums em [[cexai/enum_def_marketplace]] e [[cexai/enum_def_brand_voice]].

## Entrada (input)

### Obrigatórios (espelha AnuncioRequest / AnuncioStreamRequest)
| Campo | Tipo | Descrição | Validação |
|-------|------|-----------|-----------|
| `product_name` | string | Nome do produto | não-vazio |
| `marketplace` | enum | `mercadolivre` \| `shopee` \| `amazon` \| `magalu` | um dos quatro |
| `category` | string | Categoria do produto | não-vazia |
| `price` / `price_brl` | float | Preço em BRL | > 0 |

### Opcionais
| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `differentials` | string[] | [] | Diferenciais/features (viram bullets na origem `feature`) |
| `target_audience` | string | null | Público-alvo (ex.: "mulheres 25-45 classe B") |
| `brand_voice` | string | null | Tom: professional \| friendly \| luxurious \| casual \| technical (ver [[cexai/enum_def_brand_voice]]) |
| `custom_instructions` | string | null | Instruções extras de geração |
| `pesquisa_result` / `pesquisa_data` | object | null | Handoff de pesquisa -- ver [[cexai/entity_memory_pesquisa_handoff]] |
| `erp_fields` | object | null | ERP: `weight_kg`, `dimensions`, `sku`, `ean_gtin`, `ncm_code` |
| `product_pasted` | string | null | **Conteúdo COLADO do produto** (descrição atual + ficha técnica). NÃO é URL -- ver nota abaixo. |
| `competitor_pasted` | string | null | **Texto COLADO de 1-3 anúncios concorrentes** para benchmark. NÃO é URL. |

> **Inputs por URL NÃO são acessíveis (regra dura).** Um GPT/Project standalone **não abre URLs de marketplace com confiabilidade** (mercadolivre.com.br, shopee, amazon, magalu bloqueiam bot / exigem JS/login). Por isso `product_url`/`competitor_url` **não são campos de fetch** -- eles viram **coleta por paste**: peça ao usuário que abra o link no PRÓPRIO navegador (sessão humana real, passa pelo anti-bot) e **COLE** aqui a descrição atual + a ficha técnica/specs (e, se houver, o texto do anúncio concorrente). Se o usuário fornecer só a URL, **explique a limitação e peça o conteúdo colado** -- nunca finja ter aberto o link. Veja o INTAKE em P03.
>
> Se faltar QUALQUER campo obrigatório, **pergunte ao usuário** antes de gerar (ver P11). Nunca invente specs técnicas, peso, dimensões, material, certificações ou compatibilidades.

## Anti-alucinação no schema (regra dura)
A fonte de verdade é o que o usuário FORNECEU. Aplique ao mapear input -> conteúdo:
1. **Só preencha campos com dados reais do input** (ou confirmados via pesquisa do usuário). Specs ausentes = OMITIR, nunca inventar.
2. **Proibido fabricar:** peso, dimensão, voltagem, capacidade, validade, certificações (INMETRO/ANVISA), garantias, brindes, compatibilidades, origem/fabricante, composição, vendas, avaliações.
3. **Lacuna obrigatória -> pergunte (1 pergunta objetiva) OU marque `[PREENCHER: <campo>]`** e registre no bloco final.
4. **Claims precisam de prova.** Sem superlativo ("o melhor", "nº 1") sem evidência fornecida.
5. **Separe fato de copy.** Persuasão sobre benefício é OK; spec factual NÃO pode ser inventada -- marque inferências com "(confirme)".
6. **Auto-checagem (P07):** revise cada número e cada claim -- "veio do input? Se não, remova ou marque a confirmar."
7. **Bloco final obrigatório:** toda entrega termina com "## Suposições e dados a confirmar".
> O validador de produção tem regex anti-fabricação (fake_sales, fake_rating, fake_cert, fake_stock, fake_warranty, fake_gift, fake_testimonial) que penaliza -1.5 cada match. Gerar fato inventado = reprovar no gate. Regex tipado em [[cexai/content_filter_anvisa_fabrication]].

## Cálculo de confiança do input
Antes de gerar, estime a **confiança** (0-1) com base em quantos campos úteis foram fornecidos:
- product_name + marketplace + category + price = base mínima (~0.5).
- + differentials + target_audience + brand_voice = contexto rico (~0.8+).
Se confiança baixa, peça os campos faltantes que mais elevam a qualidade. Fórmula completa em [[cexai/input_schema_anuncio_request#confidence_calculation]].

## Saída (output) -- shape resumido (espelha AnuncioGenerationResult)
```yaml
titles: [{text, char_count, valid, value_proposition}]   # 3 variações
description: string           # texto limpo, >= 5000 chars (ML)
description_char_count: int
html_description: string      # HTML pronto p/ ML
bullets: [{text, char_count, source, trigger_type, valid}] # 10 itens, 250-299 chars (ML)
keywords_block_1: string[]    # 115-120 comercial, cada < 60 chars
keywords_block_2: string[]    # 115-120 informacional, overlap <= 15%
faqs: [{question, answer, category, source}]   # 5-7
technical_specs: {dimensions, weight, materials, colors}  # so dados reais
emotional_content: {}         # sempre vazio em V5 (compat) -- nao fabricar
quality_5d:                   # 5 dimensoes de producao + overall
  titulo / keywords / descricao / bullets / factual + overall_score (0-10)
passed: bool                  # overall >= 8.0
retry_count: int
erp_fields / baselinker_export: {sku, ean_gtin, ncm_code, weight_kg, dimensions}
head_terms / competitor_gaps / suggested_price: # se houver pesquisa
```

## Regras de validação de saída (do anuncio_validator real)
- Cada título DENTRO do limite (ML 58-60); ML SEM conectores (e, com, de, para, ou, em, por, no, na, do, da); keyword nas 3 primeiras palavras.
- Bloco 1 e Bloco 2 com 115-120 cada; cada keyword < 60 chars; overlap entre blocos <= 15%; sem frases "stuffed".
- 10 bullets (Amazon 5); cada **250-299 chars** em ML; cada um nasce de origem real (feature/pain_point/gap/spec).
- Descrição >= 5000 chars (ML), 6 folds mobile-first, SEM rótulos de framework, SEM R$.
- Termos ANVISA proibidos são auto-substituídos (P01/P11); zero claims fabricados (factual passa se score >= 0.70).
- `marketplace_compliance = true` só se TODAS as regras de TOS + anti-fabricação passarem (P07/P11).

## Related CEXAI artifacts

- [[input-schema-builder]] -- typed input contract
