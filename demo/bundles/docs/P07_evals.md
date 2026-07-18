---
kind: quality_gate
id: p11_qg_knowledge_card
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of knowledge_card artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Knowledge Card"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, knowledge-card, density, fact, distillation, searchability]
tldr: "Gates ensuring knowledge_card artifacts contain concrete atomic facts with density >= 0.8, semantic frontmatter, and file size <= 5KB."
domain: "knowledge_card — atomic searchable facts with high information density"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.94
related:
  - p06_bp_knowledge_card
  - p11_qg_golden_test
  - p11_qg_quality_gate
  - p11_qg_citation
  - p11_qg_kind_manifest
  - p11_qg_response_format
  - p11_qg_prompt_cache
  - p11_qg_naming_rule
  - p11_qg_few_shot_example
  - bld_meta_quality_gates_builder
---
## Gate de Qualidade

# Gate: knowledge_card
## Definicao
| Campo     | Valor |
|-----------|-------|
| metrica    | pontuacao soft ponderada + todos os gates hard aprovados |
| limiar | 7.0 para publicar; 8.0 para o pool; 9.5 para golden |
| operador  | AND (todos os hard) + media ponderada (soft) |
| escopo     | qualquer artefato com `kind: knowledge_card` |
## Gates HARD
Todos devem passar. Qualquer falha = rejeicao imediata.
| ID  | Verificacao | Condicao de Falha |
|-----|-------|----------------|
| H01 | O frontmatter e interpretado como YAML valido | Erro de parse em qualquer campo |
| H02 | O ID corresponde a `^KC_[A-Z0-9_]+$` | Minusculas, prefixo KC_ ausente, ou caracteres nao alfanumericos |
| H03 | O ID e igual ao nome-base do arquivo | `id: KC_REDIS_TTL` no arquivo `KC_CACHE_TTL.md` |
| H04 | O kind e igual ao literal `knowledge_card` | Qualquer outro valor de kind |
| H05 | O campo quality e `null` | Qualquer valor diferente de null |
| H06 | Todos os 19 campos obrigatorios presentes | Faltando: domain, tldr, density_score, sources, ou card_type |
## Pontuacao SOFT
Os pesos totais somam 100%.
| ID  | Dimensao | Peso | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Concretude factual | 1.0 | O card contem valores especificos, numeros ou fatos verificaveis | Mistura de fatos e afirmacoes vagas | Totalmente vago ou conceitual |
| S02 | Atomicidade | 1.0 | O card cobre exatamente um conceito, sem scope creep | Majoritariamente um conceito; pequenas tangentes | Multiplos conceitos nao relacionados |
| S03 | Pesquisabilidade -- tags | 1.0 | As tags cobrem dominio, subtopico e angulos de caso de uso (>= 4 tags distintas) | 3 tags | Menos de 3 tags |
| S04 | Atribuicao de fonte | 1.0 | Pelo menos uma fonte especifica (URL, paper, versao de spec, data) | Fonte mencionada mas nao especifica | Sem fontes |
| S05 | Classificacao do tipo de card | 0.5 | `card_type` e `domain_kc` ou `meta_kc` com a estrutura de corpo correta para o tipo | Tipo presente mas estrutura de corpo incompativel | Tipo ausente |
| S06 | Disciplina de densidade | 1.0 | Sem enchimento, sem repeticoes, sem frases de enchimento no corpo | Pequeno enchimento presente | Mais de 20% de conteudo de enchimento |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Acoes
| Pontuacao | Nivel | Acao |
|-------|------|--------|
| >= 9.5 | Golden | Publicar no pool de conhecimento como card de referencia autoritativo |
| >= 8.0 | Skilled | Publicar no pool + registrar padrao |
| >= 7.0 | Learning | Usar mas sinalizar para melhoria |
| < 7.0 | Rejected | Devolver ao autor com relatorio de gate |
## Bypass
| Campo | Valor |
|-------|-------|
| Condicoes | Topico em rapida evolucao onde as fontes ainda nao estao estabilizadas (ex.: novo lancamento de biblioteca, mudanca de API que quebra compatibilidade) |
| Aprovador | Revisor especialista de dominio |

## Exemplos

# Exemplos: knowledge-card-builder
## Exemplo Golden
ENTRADA: "Destila conhecimento sobre prompt caching pra otimizar custo de LLM"
SAIDA:
```yaml
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
title: "Padroes de Prompt Caching para Otimizacao de Custo de LLM"
version: "1.0.0"
created: "2026-03-24"
updated: "2026-03-24"
author: "builder"
```
## Referencia Rapida
```yaml
topic: prompt_caching
scope: Otimizacao de API de LLM (Anthropic, OpenAI, Google)
owner: builder
criticality: alta
```
## Conceitos-Chave
- **Cache-Control**: Anthropic `cache_control: {kind: "ephemeral"}`; TTL de 5 min
- **Correspondencia de Prefixo**: cache hit quando o prefixo e identico byte a byte
- **Tokens Minimos**: Anthropic >= 1024; OpenAI >= 1024 (automatico)
- **Divisao de Preco**: escrita 1.25x do base, leitura 0.1x (economia de 90% no hit)
## Fases da Estrategia
1. **Auditoria**: identifique prompts com mais de 50% de conteudo estatico
2. **Reordenacao**: estatico primeiro (system > few-shot > RAG), dinamico por ultimo
```text
[Request] -> [Hash Prefix] -> [Cache Lookup]
                                   |
                         HIT: 0.1x cost, 85% faster
                         MISS: 1.25x cost, normal speed
                                   |
                             [Generate] -> [Response]
```
## Comparativo
| Provedor | Tokens Min | Config | Escrita | Leitura | TTL |
|----------|-----------|--------|-------|------|-----|
| Anthropic | 1024 | Explicito | 1.25x | 0.1x | 5 min |
| OpenAI | 1024 | Automatico | 1.0x | 0.5x | 5-60 min |
| Google | 32768 | Explicito | 1.0x | 0.25x | config |

### S_RELATED: Verificacao de Referencia Cruzada (SOFT)
- [ ] campo de frontmatter `related:` preenchido (3-15 entradas)
- [ ] secao `## Artefatos Relacionados` presente no corpo do artefato
- [ ] pelo menos 1 referencia a montante e 1 a jusante
- Penalidade: -0.3 se vazio (nao bloqueia, incentiva o encadeamento)

## Artefatos Relacionados

| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[p06_bp_knowledge_card]] | a montante | 0.28 |
| [[p11_qg_golden_test]] | irmao | 0.27 |
| [[p11_qg_quality_gate]] | irmao | 0.24 |
| [[p11_qg_citation]] | irmao | 0.21 |
| [[p11_qg_kind_manifest]] | irmao | 0.20 |
| [[p11_qg_response_format]] | irmao | 0.20 |
| [[p11_qg_prompt_cache]] | irmao | 0.19 |
| [[p11_qg_naming_rule]] | irmao | 0.19 |
| [[p11_qg_few_shot_example]] | irmao | 0.19 |
| [[bld_meta_quality_gates_builder]] | relacionado | 0.19 |
