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
  - p11_qg_golden_test
  - p06_bp_knowledge_card
  - p11_qg_quality_gate
  - p11_qg_citation
  - p11_qg_response_format
  - p11_qg_naming_rule
  - knowledge-card-builder
  - p11_qg_prompt_cache
  - p11_qg_few_shot_example
  - p11_qg_kind_manifest
---
## Gate de Qualidade

# Gate: Knowledge Card
## Definição
| Campo     | Valor |
|-----------|-------|
| métrica   | score soft ponderado + todos os gates hard aprovados |
| limiar    | 7.0 para publicar; 8.0 para o pool; 9.5 para golden |
| operador  | AND (todos os hard) + média ponderada (soft) |
| escopo    | qualquer artefato com `kind: knowledge_card` |
## Gates HARD
Todos precisam passar. Qualquer falha = rejeição imediata.
| ID  | Verificação | Condição de Falha |
|-----|-------|----------------|
| H01 | O frontmatter faz parse como YAML válido | Erro de parse em qualquer campo |
| H02 | O ID corresponde a `^KC_[A-Z0-9_]+$` | Minúsculas, prefixo KC_ ausente, ou caracteres não alfanuméricos |
| H03 | O ID é igual ao stem do nome do arquivo | `id: KC_REDIS_TTL` no arquivo `KC_CACHE_TTL.md` |
| H04 | O kind é igual ao literal `knowledge_card` | Qualquer outro valor de kind |
| H05 | O campo quality é `null` | Qualquer valor não nulo |
| H06 | Todos os 19 campos obrigatórios presentes | Faltando: domain, tldr, density_score, sources, ou card_type |
## Pontuação SOFT
Os pesos totais somam 100%.
| ID  | Dimensão | Peso | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Concretude factual | 1.0 | O card contém valores específicos, números ou fatos verificáveis | Mistura de fatos e afirmações vagas | Inteiramente vago ou conceitual |
| S02 | Atomicidade | 1.0 | O card cobre exatamente um conceito, sem fuga de escopo | Majoritariamente um conceito; pequenas tangentes | Múltiplos conceitos não relacionados |
| S03 | Pesquisabilidade — tags | 1.0 | As tags cobrem ângulos de domínio, subtópico e caso de uso (>= 4 tags distintas) | 3 tags | Menos de 3 tags |
| S04 | Atribuição de fonte | 1.0 | Ao menos uma fonte específica (URL, paper, versão de spec, data) | Fonte mencionada mas não específica | Nenhuma fonte |
| S05 | Classificação do tipo de card | 0.5 | `card_type` é `domain_kc` ou `meta_kc` com a estrutura de corpo correta para o tipo | Tipo presente mas a estrutura de corpo não corresponde | Tipo ausente |
| S06 | Disciplina de densidade | 1.0 | Sem enchimento, sem repetição, sem frases de preenchimento no corpo | Enchimento leve presente | Mais de 20% de conteúdo de enchimento |
**Score = soma(pts * peso) / soma(pts_max * peso) * 10**
## Ações
| Score | Nível | Ação |
|-------|------|--------|
| >= 9.5 | Golden | Publicar no pool de conhecimento como card de referência autoritativo |
| >= 8.0 | Skilled | Publicar no pool + registrar o padrão |
| >= 7.0 | Learning | Usar, mas sinalizar para melhoria |
| < 7.0 | Rejected | Devolver ao autor com o relatório do gate |
## Bypass
| Campo | Valor |
|-------|-------|
| Condições | Tópico em rápida evolução, com fontes ainda não estabilizadas (ex.: novo release de biblioteca, mudança de API que quebra compatibilidade) |
| Aprovador | Revisor especialista de domínio |

## Exemplos

# Exemplos: knowledge-card-builder
## Exemplo Golden
ENTRADA: "Destile conhecimento sobre prompt caching para otimizar custos de LLM"
SAÍDA:
```yaml
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
title: "Prompt Caching Patterns for LLM Cost Optimization"
version: "1.0.0"
created: "2026-03-24"
updated: "2026-03-24"
author: "builder"
```
```yaml
topic: prompt_caching
scope: LLM API optimization (Anthropic, OpenAI, Google)
owner: builder
criticality: high
```
## Conceitos-Chave
- **Cache-Control**: Anthropic `cache_control: {kind: "ephemeral"}`; TTL de 5 min
- **Correspondência de Prefixo**: cache hit quando o prefixo é idêntico byte a byte
- **Tokens Mínimos**: Anthropic >= 1024; OpenAI >= 1024 (automático)
- **Divisão de Preço**: escrita 1.25x da base, leitura 0.1x (90% de economia no hit)
## Fases da Estratégia
1. **Auditoria**: identifique prompts com mais de 50% de conteúdo estático
2. **Reordenação**: estático primeiro (system > few-shot > RAG), dinâmico por último
```text
[Request] -> [Hash Prefix] -> [Cache Lookup]
                                   |
                         HIT: custo 0.1x, 85% mais rápido
                         MISS: custo 1.25x, velocidade normal
                                   |
                             [Generate] -> [Response]
```
## Comparativo
| Provider | Tokens Mín. | Config | Escrita | Leitura | TTL |
|----------|-----------|--------|-------|------|-----|
| Anthropic | 1024 | Explícito | 1.25x | 0.1x | 5 min |
| OpenAI | 1024 | Automático | 1.0x | 0.5x | 5-60 min |
| Google | 32768 | Explícito | 1.0x | 0.25x | config |

### S_RELATED: Checagem de Referência Cruzada (SOFT)
- [ ] Campo de frontmatter `related:` populado (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Ao menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, apenas incentiva a interligação)
