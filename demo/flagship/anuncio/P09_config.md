---
agent: anuncio
pillar: P09
pillar_name: config
lang: pt-BR
source: records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (Rules by Marketplace, limits); api/v1/anuncios.py (retry config, NCM defaults)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: env_config
cexai_typed_artifacts:
  - cexai/env_config_marketplace_specs.md
  - cexai/enum_def_marketplace.md
  - cexai/enum_def_brand_voice.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P09 -- Configuração (parâmetros, constraints, limites)

Todos os números e defaults que governam a geração. Consulte como tabela de referência.

> **Camada CEXAI:** config tipada em [[cexai/env_config_marketplace_specs]] (MARKETPLACE_SPECS V5 completo: 4 marketplaces + defaults + gates + retry + NCM map). Enums em [[cexai/enum_def_marketplace]] e [[cexai/enum_def_brand_voice]].

## Limites por marketplace (MARKETPLACE_SPECS de produção V5)

| Marketplace | Título | Descrição (chars) | Bullets (count / chars) | Keywords/bloco |
|-------------|--------|-------------------|--------------------------|----------------|
| Mercado Livre | **58-60** (estrito, sem conectores) | **5000-50000** | **10 / 250-299** | 115-120 |
| Shopee | **20-120** (1-2 emojis início) | 500-3000 (texto puro) | 10 / 100-250 | 80-100 |
| Amazon BR | **50-200** (marca 1º, sem emoji) | 500-2000 (A+) | **5** / 100-500 | 50-80 |
| Magalu | 30-150 | 500-4000 | 10 / 100-500 | 50-80 |

> Cada keyword: **< 60 caracteres**. Overlap entre Bloco 1 e Bloco 2: **<= 15%**.

## Contagens fixas
| Item | Valor |
|------|-------|
| Variações de título | **3** |
| Bloco 1 (comercial/transacional) | **115-120** keywords (ML) |
| Bloco 2 (informacional) | **115-120** keywords (ML) |
| Bullets | **10** (Amazon: exatamente **5**) |
| Comprimento por bullet (ML) | **250-299 caracteres** (estrito -- o validador rejeita fora da faixa) |
| Descrição mínima (ML) | **5000 caracteres** |
| FAQs | 5-7 |
| Repetição máx. de keyword | 2 |

## Defaults
| Parâmetro | Default |
|-----------|---------|
| brand_name | "[MARCA]" |
| marketplace | mercadolivre (se não informado, pergunte) |
| brand_voice | professional |
| price_tier | derivado do preço |
| densidade de keyword alvo | 1-3% |
| comprimento da descrição (ML) | >= 5000 chars (alvo 5000-7000) |

## Gates e retry (QUALITY_THRESHOLD + RETRY_CONFIG de produção)
| Parâmetro | Valor |
|-----------|-------|
| Gate global (overall) | **>= 8.0** (escala 0-10) |
| Gate por dimensão (factual) | score >= 0.70 |
| Máx. retries | **2** |
| Escalada por retry | retry 1: +0.1 temp · retry 2: +0.2 temp + modelo mais forte |
| on_failure | partial_output (marca REVISAR + lista validation_issues) |
| Timeouts (geração) | global 180s · titles 45s · keywords 30s · bullets 45s · desc 60s · faqs 30s |

## Tipo de anúncio (Mercado Livre)
- `gold_special` (padrão) ou `gold_pro`.
- Até 10 keywords/tags.

## NCM por categoria (referência para ficha técnica/ERP)
Mapeamento aproximado quando o usuário precisar do código fiscal (lista completa em [[cexai/env_config_marketplace_specs#ncm_map]]):
- brinquedo/pet: 9503.00.99
- eletrônico: 8543.70.99
- cosmético/beleza: 3304.99.90
- roupa/camiseta: 6109.10.00
- sapato/calçado: 6403.99.90
- acessório: 7117.90.00 / bijuteria: 7117.19.00
- ferramenta: 8205.59.00
- casa: 3924.90.00 / cozinha: 3924.10.00
- celular: 8517.12.31 / informática: 8471.30.19
- esporte: 9506.99.00 / livro: 4901.99.00
- fallback (não classificado): 9999.99.99
> NCM é apenas referência -- oriente o usuário a confirmar com o contador. Você não emite nota.

## Tons de voz disponíveis (brand_voice -- ver [[cexai/enum_def_brand_voice]])
professional | friendly | luxurious | casual | technical

## Related CEXAI artifacts

- [[env-config-builder]] -- environment-scoped config
