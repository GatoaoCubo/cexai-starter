---
kind: config
id: bld_config_research_pipeline
pillar: P09
llm_function: CONSTRAIN
purpose: Convenções de nomenclatura, caminhos de arquivo, limites de tamanho, restrições operacionais
pattern: CONFIG restringe SCHEMA, nunca o contradiz
effort: high
max_turns: 25
disallowed_tools: [Write, Edit]
fork_context: fork
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Configuração: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags: [research_pipeline, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, research pipeline construction, config research pipeline, research_pipeline, builder, examples, "research_pipeline_config_{empresa}.yaml"]
density_score: 0.90
related:
  - bld_config_content_monetization
---
# Config: Regras de Produção do research_pipeline

## Convenção de Nomenclatura
| Escopo | Convenção | Exemplo |
|-------|-----------|---------|
| Arquivo de config | `research_pipeline_config_{empresa}.yaml` | `research_pipeline_config_acme.yaml` |
| Template | `tpl_research_pipeline.md` | P04_tools/templates/ |
| Exemplos | `ex_research_pipeline_{niche}.md` | `ex_research_pipeline_ecommerce_br.md` |
| Instância | `research_pipeline_config.md` | _instances/{co}/N01_intelligence/ |
| ID do frontmatter | `p04_cli_research_pipeline_{slug}` | `p04_cli_research_pipeline_acme` |

## Limites de Tamanho
| Artefato | Tamanho Máximo | Motivo |
|----------|---------|-----------|
| Config YAML | 4096 bytes | Config densa, editável por humanos |
| Template | 4096 bytes | Limite do ISO do builder |
| Exemplo | 4096 bytes | Limite do ISO do builder |
| KC | 4096 bytes | Tamanho padrão de KC |

## Categorias de Fonte (referência)
| Categoria | Descrição | Fontes Comuns |
|----------|------------|----------------|
| inbound | Dados de produto/listagem de marketplaces | mercadolivre, shopee, amazon, magalu, g2, capterra |
| outbound | Inteligência social, reviews, comunidade | youtube, reddit, reclameaqui, hackernews, twitter |
| search | Motores de busca web | serper, exa, gemini_search, openai_search, brave, tavily |
| trends | Rastreamento de preço, análise de tendência | pytrends, keepa, semrush |
| rag | Base de conhecimento interna | local_docs, supabase_embeddings, confluence |

## Referência de Custo de API
| Fonte | Custo | Rate Limit | Autenticação |
|--------|------|-----------|------|
| Serper | $0.30/1K queries | 100/min | SERPER_API_KEY |
| Firecrawl | $19/mês (3K créditos) | 10/min | FIRECRAWL_API_KEY |
| Exa | $0.10/query | 60/min | EXA_API_KEY |
| YouTube | Grátis (10K/dia) | 10K/dia | YOUTUBE_API_KEY |
| Keepa | €19/mês (5K tokens) | 5/min | KEEPA_API_KEY |
| pytrends | Grátis | 1/3s (não oficial) | nenhuma |
| Reddit | Grátis (OAuth) | 60/min | REDDIT_CLIENT_ID |

## Regras de Posicionamento de Arquivos
| Tipo de Artefato | Diretório | Pillar |
|--------------|-----------|--------|
| Template | P04_tools/templates/ | P04 |
| Exemplos | P04_tools/examples/ | P04 |
| Compilado | P04_tools/compiled/ | P04 |
| Ferramenta do nucleus | N01_intelligence/P04_tools/ | P04 |
| KCs do nucleus | N01_intelligence/P01_knowledge/ | P01 |
| Regra de dispatch | N01_intelligence/P12_orchestration/ | P12 |
| Config da empresa | _instances/{co}/N01_intelligence/ | instância |

## Regras de Segurança
1. Chaves de API: NUNCA em texto plano → sempre ENV_VAR (SCREAMING_SNAKE_CASE)
2. URLs de fonte: parametrize as URLs base sempre que possível
3. Arquivos de config: NUNCA fazer commit com segredos reais → padrão `.env.example`
4. Schemas de marketplace: seguro fazer commit (nomes de campo de extração, não autenticação)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_social_publisher | sibling | 0.44 |
| [[kc_source_catalog]] | upstream | 0.32 |
| [[bld_config_content_monetization]] | sibling | 0.27 |
| p04_cli_research_pipeline_n01 | upstream | 0.26 |
| tpl_research_pipeline | upstream | 0.23 |
