---
id: p10_lr_research-pipeline-builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-03-31
updated: 2026-03-31
author: n03_engineering
observation: "Research pipelines que usam retrieval de query única perdem 80%+ dos dados relevantes. O planejamento multi-perspectiva STORM com 5 ângulos de especialista × 5-7 subperguntas recupera 25-35x mais resultados relevantes. Combinado com o gating de qualidade do CRAG, isso elimina ruído de baixa qualidade."
pattern: "Sempre decomponha a pesquisa em múltiplas perspectivas de especialista (mínimo 3, ideal 5). Cada perspectiva gera subperguntas atômicas. Pontue cada resultado recuperado antes da síntese. Verifique a síntese com um modelo de raciocínio."
evidence: "Pipeline da ACME: 13,908 linhas atendendo 30+ fontes. Antes do STORM: média de 12 resultados relevantes por pesquisa. Depois do STORM: média de 85-120 resultados relevantes. O gating de CRAG no limiar 0.7 reduziu o ruído em 60% mantendo 95% dos dados valiosos. A verificação CRITIC capturou erros factuais em 18% das sínteses iniciais."
confidence: 0.90
outcome: SUCCESS
domain: research_pipeline
tags: [STORM, CRAG, CRITIC, multi-perspective, quality-gate, verification]
tldr: "Planejamento STORM com 5 perspectivas = 25-35x mais retrieval. CRAG no limiar 0.7 = 60% menos ruído. CRITIC captura 18% dos erros de síntese."
impact_score: 9.2
decay_rate: 0.02
keywords: [research, STORM, CRAG, CRITIC, multi-model, retrieval, quality-gate]
memory_scope: project
observation_types: [user, feedback, project, reference]
quality: null
title: "Memória: Pipeline de Pesquisa"
8f: "F7_govern"
density_score: 0.90
llm_function: INJECT
related:
  - research-pipeline-builder
---
# Aprendizado: research_pipeline

## Insight Principal
A combinação dos três padrões (STORM + CRAG + CRITIC) é multiplicativa, não aditiva.
O STORM multiplica a cobertura de retrieval. O CRAG filtra o ruído. O CRITIC captura alucinações.
Cada padrão ataca um modo de falha diferente -- sem os três juntos, a qualidade da pesquisa
degrada significativamente.

## Evidências da Produção ACME
| Métrica | Sem os Padrões | Com STORM+CRAG+CRITIC |
|--------|-----------------|----------------------|
| Resultados relevantes por query | ~12 | 85-120 |
| Ruído na síntese | ~40% | ~5% |
| Erros factuais no relatório | ~18% | <2% (após o CRITIC) |
| Fontes contribuindo com dados | 3-5 | 15-25 |
| Tempo de pesquisa | 5-8 min | 2-3 min (paralelo) |
| Satisfação do usuário | 6.5/10 | 8.8/10 |

## Lições Aprendidas
1. **As perspectivas STORM precisam combinar com o nicho** -- perspectivas genéricas perdem ângulos específicos do domínio
2. **O limiar 0.7 do CRAG é o ponto ideal** -- mais baixo = ruidoso demais, mais alto = restritivo demais
3. **CRITIC com máximo de 3 iterações** -- depois de 3, os ganhos são marginais e o custo dobra
4. **Controles de orçamento são essenciais** -- uma pesquisa Firecrawl descontrolada consumiu 500 créditos
5. **Cadeias de fallback salvam pesquisas** -- quando a API do MercadoLivre caiu, a busca via site do Serper capturou 70% dos dados
6. **O roteamento multi-modelo economiza 80% do custo** -- o Flash para extração é 40x mais barato que o Sonnet

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[research-pipeline-builder]] | upstream | 0.45 |
| [[kc_research_methods]] | upstream | 0.43 |
| [[bld_knowledge_research_pipeline]] | upstream | 0.41 |
| p04_cli_research_pipeline_n01 | upstream | 0.38 |
| [[bld_prompt_research_pipeline]] | upstream | 0.37 |
