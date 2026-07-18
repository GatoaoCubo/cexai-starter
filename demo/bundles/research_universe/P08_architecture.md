---
kind: architecture
id: bld_architecture_research_universe
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes de research_universe -- inventário, dependências
quality: null
title: "Architecture Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, architecture]
tldr: "Mapa de componentes de research_universe -- 6 trilhas fan-out + síntese, inventário e dependências"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F1_constrain"
keywords: [architecture research universe, mapa de componentes, trilhas fan-out, síntese, research_universe, builder, architecture, dependências, posição arquitetural]
density_score: 0.88
related:
  - bld_architecture_competitive_matrix
  - bld_architecture_knowledge_card
---

## Inventário de Componentes
| Nome do ISO | Papel | Pilar | Status |
|----------------------|-------------------------------------------|--------|---------|
| bld_knowledge_card_research_universe | Conhecimento de domínio: 6 trilhas, conceitos, padrões | P01 | Ativo |
| research-universe-builder | Identidade do builder, capacidades, roteamento, persona | P02 | Ativo |
| bld_instruction_research_universe | Processo de 3 fases: intake -> coleta por trilha -> validação | P03 | Ativo |
| bld_tools_research_universe | Fontes públicas por trilha + ferramentas internas de validação | P04 | Ativo |
| bld_output_template_research_universe | Template do relatório unificado com 10 seções | P05 | Ativo |
| bld_schema_research_universe | Schema formal: semente, 6 trilhas, enum de status, restrições | P06 | Ativo |
| p01_qg_research_universe | Gate de qualidade: 7 HARD + 6 SOFT + exemplos | P11 | Ativo |
| bld_architecture_research_universe | Este arquivo -- inventário e dependências | P08 | Ativo |
| bld_config_research_universe | Nomenclatura, caminhos, limites, casos de borda | P09 | Ativo |
| p10_mem_research_universe_builder | Padrões aprendidos e armadilhas de produção | P10 | Ativo |
| p11_fb_research_universe | Antipadrões e protocolo de correção | P11 | Ativo |
| bld_collaboration_research_universe | Papel em crews, handoffs, dependências entre builders | P12 | Ativo |

## Fan-Out das 6 Trilhas
```
                         +-> Firmografia (CNPJ/IBGE)
                         +-> Sinal Social (App Store/Reddit/YouTube)
Semente -> Classificação +-> Reputação (Reclame Aqui)          +-> Síntese -> Relatório Unificado
   (seed_type)           +-> Sentimento em PT  (deriva de 2+3)          (status por trilha
                         +-> Palavras-chave de SEO                       + procedência)
                         +-> Perguntas Multi-Perspectiva (deriva de 1-5)
```
As 6 trilhas rodam de forma **independente** -- a falha de uma (`blocked`) nunca impede as demais de fechar como `ok`. Sentimento em PT e Perguntas Multi-Perspectiva são trilhas DERIVADAS (consomem o texto/dado das outras 4), não coletam de fonte externa própria.

## Dependências
| De | Para | Tipo |
|------|----|------|
| Classificação de semente | Trilhas aplicáveis (P06, tabela Semente x Trilhas) | Configuração |
| Sinal Social + Reputação | Sentimento em PT | Dado (texto-fonte) |
| Firmografia + Sinal Social + Reputação + SEO | Perguntas Multi-Perspectiva | Síntese |
| Tabela de Status por Trilha | Procedência Consolidada | Agregação |
| bld_schema_research_universe | p01_qg_research_universe | Validação |

## Posição Arquitetural
`research_universe` atua como o agregador de entrada do pillar P01 para due diligence e discovery de negócios brasileiros: recebe UMA semente, executa 6 trilhas independentes e devolve um artefato único. Ele antecede, mas não substitui, builders de decisão mais especializados -- `competitive_matrix` (análise comparativa formal) e `opportunity_matrix` (avaliação de oportunidade de sourcing) tipicamente CONSOMEM um `research_universe` como insumo de contexto, não o contrário.

## Fronteira (IS / IS NOT)
| research_universe IS | research_universe IS NOT |
|-----------------------|----------------------------|
| Agregador multi-fonte de UMA semente em 6 trilhas | Uma única fonte de dado ao vivo (não substitui a Receita Federal ou o Reclame Aqui) |
| Honesto por construção: `ok`/`blocked`/`skipped` sempre explícitos | Uma ferramenta de scraping automático -- o pacote público não tem Actions |
| Um relatório de contexto para decisão posterior | Uma matriz competitiva formal (isso é `competitive_matrix`) |
| Reprodutível: mesma semente + mesmas fontes = mesmo relatório | Um veredicto de "boa" ou "má" oportunidade (isso é `opportunity_matrix`) |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_architecture_competitive_matrix]] | sibling | 0.40 |
| [[bld_architecture_knowledge_card]] | sibling | 0.34 |
| [[bld_schema_research_universe]] | downstream | 0.31 |
| [[bld_collaboration_research_universe]] | sibling | 0.28 |
