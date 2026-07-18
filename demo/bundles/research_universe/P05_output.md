---
kind: output_template
id: bld_output_template_research_universe
pillar: P05
llm_function: PRODUCE
purpose: Template com variáveis para produção de research_universe
quality: null
title: "Output Template Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, output_template]
tldr: "Template de relatório unificado multi-fonte: 6 trilhas + tabela de status + procedência consolidada"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F6_produce"
keywords: [output template research universe, relatório unificado, tabela de status, procedência, research_universe, builder, output_template, semente, trilhas]
density_score: 0.88
related:
  - bld_schema_research_universe
---
```yaml
---
id: p01_ru_{{slug}}.md
kind: research_universe
pillar: P01
title: "Universo de Pesquisa: {{seed_label}}"
version: "1.0.0"
author: "{{analyst_name}}"
domain: "{{seed_domain}}"
quality: null
tags: [{{seed_tag}}, research_universe, multi_source]
tldr: "{{seed_label}} ({{seed_type}}) -- {{lanes_ok_count}}/6 trilhas ok, cobertura {{coverage_score}}"
seed: "{{seed_value}}"
seed_type: "{{produto|marca|cnpj|empresa|palavra_chave|store_id}}"
analysis_date: "{{AAAA-MM-DD}}"
coverage_score: {{0.00_a_1.00}}
key_findings: "{{principal_achado_em_uma_frase}}"
lanes:
  - lane: firmographics
    status: "{{ok|blocked|skipped}}"
  - lane: social_signal
    status: "{{ok|blocked|skipped}}"
  - lane: reputation
    status: "{{ok|blocked|skipped}}"
  - lane: pt_sentiment
    status: "{{ok|blocked|skipped}}"
  - lane: seo_keywords
    status: "{{ok|blocked|skipped}}"
  - lane: multi_perspective_questions
    status: "{{ok|blocked|skipped}}"
---
```

## Sumário Executivo
| Campo | Valor |
|-------|-------|
| Semente | `{{seed_value}}` ({{seed_type}}) |
| Data da análise | {{AAAA-MM-DD}} |
| Trilhas `ok` | {{lanes_ok_count}}/6 |
| Cobertura | {{coverage_score}} |
| Principal achado | `{{key_findings}}` |

## 1. Firmografia (CNPJ/IBGE) -- status: `{{ok|blocked|skipped}}`
<!-- Se skipped: uma frase dizendo por que (ex.: "semente é palavra-chave, sem empresa associada") -->
| Campo | Valor | Fonte | Data de acesso |
|-------|-------|-------|-----------------|
| Razão social | `{{razao_social}}` | `{{fonte}}` | {{AAAA-MM-DD}} |
| CNAE (setor) | `{{cnae_codigo_descricao}}` | `{{fonte}}` | {{AAAA-MM-DD}} |
| Porte | `{{mei\|me\|epp\|média\|grande}}` | `{{fonte}}` | {{AAAA-MM-DD}} |
| Situação cadastral | `{{ativa\|suspensa\|baixada}}` | `{{fonte}}` | {{AAAA-MM-DD}} |
| Município/UF | `{{cidade}}/{{uf}}` | `{{fonte}}` | {{AAAA-MM-DD}} |

## 2. Sinal Social (App Store / Reddit / YouTube) -- status: `{{ok|blocked|skipped}}`
| Canal | Nota/Volume | Tom geral | Fonte | Data de acesso |
|-------|-------------|-----------|-------|-----------------|
| Loja de app | `{{nota}}/5 ({{n_reviews}} reviews)` | `{{positivo|misto|negativo}}` | `{{fonte}}` | {{AAAA-MM-DD}} |
| Reddit | `{{n_mencoes}} menções em {{subreddits}}` | `{{tom}}` | `{{fonte}}` | {{AAAA-MM-DD}} |
| YouTube | `{{n_videos}} vídeos, {{n_comentarios}} comentários relevantes` | `{{tom}}` | `{{fonte}}` | {{AAAA-MM-DD}} |

## 3. Reputação (Reclame Aqui) -- status: `{{ok|blocked|skipped}}`
| Métrica | Valor | Fonte | Data de acesso |
|---------|-------|-------|-----------------|
| Índice RA | `{{índice}}` | Reclame Aqui | {{AAAA-MM-DD}} |
| % respondidas | `{{percentual}}` | Reclame Aqui | {{AAAA-MM-DD}} |
| % resolvidas | `{{percentual}}` | Reclame Aqui | {{AAAA-MM-DD}} |
| Nota do consumidor | `{{nota}}/5` | Reclame Aqui | {{AAAA-MM-DD}} |

## 4. Sentimento em PT -- status: `{{ok|blocked|skipped}}`
<!-- SOMENTE sobre texto já coletado nas trilhas 2 e 3. Sem texto-fonte, esta trilha é skipped. -->
| Distribuição | % | Tema recorrente | Trecho-fonte (trilha de origem) |
|--------------|---|------------------|-----------------------------------|
| Positivo | `{{pct}}` | `{{tema}}` | `{{trecho}}` ({{sinal_social\|reputação}}) |
| Neutro | `{{pct}}` | `{{tema}}` | `{{trecho}}` ({{sinal_social\|reputação}}) |
| Negativo | `{{pct}}` | `{{tema}}` | `{{trecho}}` ({{sinal_social\|reputação}}) |

## 5. Palavras-chave de SEO -- status: `{{ok|blocked|skipped}}`
| Termo | Intenção | Volume/tendência | Fonte |
|-------|----------|-------------------|-------|
| `{{termo_1}}` | `{{informacional\|transacional\|navegacional}}` | `{{estimado|validado}}: {{valor}}` | `{{fonte}}` |
| `{{termo_2}}` | `{{intenção}}` | `{{valor}}` | `{{fonte}}` |
| `{{termo_3}}` | `{{intenção}}` | `{{valor}}` | `{{fonte}}` |

## 6. Perguntas Multi-Perspectiva -- status: `{{ok|blocked|skipped}}`
| Papel | Pergunta |
|-------|----------|
| Cliente | `{{pergunta_especifica_a_semente}}` |
| Concorrente | `{{pergunta_especifica_a_semente}}` |
| Investidor/Regulador | `{{pergunta_especifica_a_semente}}` |
| Parceiro | `{{pergunta_especifica_a_semente}}` |

## Tabela de Status por Trilha
| Trilha | Status | Motivo (se `blocked`/`skipped`) |
|--------|--------|-----------------------------------|
| Firmografia | `{{ok|blocked|skipped}}` | `{{motivo_ou_vazio}}` |
| Sinal Social | `{{ok|blocked|skipped}}` | `{{motivo_ou_vazio}}` |
| Reputação | `{{ok|blocked|skipped}}` | `{{motivo_ou_vazio}}` |
| Sentimento em PT | `{{ok|blocked|skipped}}` | `{{motivo_ou_vazio}}` |
| SEO | `{{ok|blocked|skipped}}` | `{{motivo_ou_vazio}}` |
| Perguntas Multi-Perspectiva | `{{ok|blocked|skipped}}` | `{{motivo_ou_vazio}}` |

## Procedência Consolidada
- Fontes usadas: `{{lista_de_fontes}}`
- Método de coleta: `{{colado_pelo_usuario|busca_nativa|misto}}`
- Confiança geral: `{{alta|média|baixa}}` -- baseada em `{{lanes_ok_count}}`/6 trilhas com dado real

## Limitações e Próximos Passos
- `{{limitacao_1}}`
- `{{limitacao_2}}`
- Próximo passo sugerido: `{{acao_recomendada}}`

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_research_universe]] | downstream | 0.35 |
| [[bld_instruction_research_universe]] | upstream | 0.28 |
| [[bld_knowledge_card_research_universe]] | upstream | 0.20 |
