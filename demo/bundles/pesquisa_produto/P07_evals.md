---
kind: quality_gate
id: p11_qg_knowledge_card
pillar: P11
llm_function: GOVERN
purpose: Exemplos ideais e contraexemplos de artifacts knowledge_card
pattern: few-shot learning -- o LLM lê estes antes de produzir
quality: null
title: "Gate: Knowledge Card"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, knowledge-card, density, fact, distillation, searchability]
tldr: "Gates garantindo que artifacts knowledge_card contenham fatos atômicos concretos com densidade >= 0.8, frontmatter semântico, e tamanho de arquivo <= 5KB."
domain: "knowledge_card -- fatos atômicos pesquisáveis com alta densidade de informação"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.94
related:
  - p06_bp_knowledge_card
  - p11_qg_golden_test
  - p11_qg_quality_gate
  - p11_qg_citation
  - knowledge-card-builder
  - p11_qg_naming_rule
  - p11_qg_response_format
  - p11_qg_prompt_cache
  - p11_qg_kind_manifest
  - p06_bp_model_card
---
## Gate de Qualidade

# Gate: Knowledge Card
## Definição
| Campo     | Valor |
|-----------|-------|
| metric    | nota soft ponderada + todos os gates hard aprovados |
| threshold | 7.0 para publicar; 8.0 para o pool; 9.5 para golden |
| operator  | AND (todos os hard) + média ponderada (soft) |
| scope     | qualquer artifact com `kind: knowledge_card` |
## Gates HARD
Todos precisam passar. Qualquer falha = rejeição imediata.
| ID  | Verificação | Condição de Falha |
|-----|-------|----------------|
| H01 | O frontmatter faz parse como YAML válido | Erro de parse em qualquer campo |
| H02 | O ID casa com `^KC_[A-Z0-9_]+$` | Minúsculo, sem o prefixo KC_, ou caracteres não alfanuméricos |
| H03 | O ID é igual ao nome do arquivo sem extensão | `id: KC_REDIS_TTL` no arquivo `KC_CACHE_TTL.md` |
| H04 | O kind é igual ao literal `knowledge_card` | Qualquer outro valor de kind |
| H05 | O campo quality é `null` | Qualquer valor não nulo |
| H06 | Todos os 19 campos obrigatórios presentes | Faltando: domain, tldr, density_score, sources, ou card_type |
## Pontuação SOFT
A soma dos pesos totaliza 100%.
| ID  | Dimensão | Peso | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Concretude factual | 1.0 | O card contém valores específicos, números, ou fatos verificáveis | Mistura de fatos e afirmações vagas | Totalmente vago ou conceitual |
| S02 | Atomicidade | 1.0 | O card cobre exatamente um conceito, sem scope creep | Majoritariamente um conceito; pequenas tangentes | Múltiplos conceitos não relacionados |
| S03 | Pesquisabilidade -- tags | 1.0 | As tags cobrem domínio, subtópico, e ângulos de caso de uso (>= 4 tags distintas) | 3 tags | Menos de 3 tags |
| S04 | Atribuição de fonte | 1.0 | Ao menos uma fonte específica (URL, paper, versão de spec, data) | Fonte mencionada mas não específica | Sem fontes |
| S05 | Classificação do tipo de card | 0.5 | `card_type` é `domain_kc` ou `meta_kc` com a estrutura de corpo correta para o tipo | Tipo presente mas a estrutura de corpo não combina | Tipo ausente |
| S06 | Disciplina de densidade | 1.0 | Sem enchimento, sem repetição, sem frases de enchimento no corpo | Enchimento leve presente | Mais de 20% de conteúdo de enchimento |
**Nota = soma(pts * peso) / soma(max_pts * peso) * 10**
## Ações
| Nota | Nível | Ação |
|-------|------|--------|
| >= 9.5 | Golden | Publica no pool de conhecimento como card de referência autoritativo |
| >= 8.0 | Skilled | Publica no pool + registra o padrão |
| >= 7.0 | Learning | Usa mas sinaliza para melhoria |
| < 7.0 | Rejected | Retorna ao autor com o relatório do gate |
## Exceção
| Campo | Valor |
|-------|-------|
| Conditions | Tópico em rápida evolução onde as fontes ainda não estão estabilizadas (ex.: novo release de biblioteca, breaking change de API) |
| Approver | Revisor especialista de domínio |

## Exemplos

# Exemplos: knowledge-card-builder
## Exemplo Ideal
ENTRADA: "Destile conhecimento sobre prompt caching para otimizar custos de LLM"
SAÍDA:
```yaml
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
title: "Padrões de Prompt Caching para Otimização de Custo em LLM"
version: "1.0.0"
created: "2026-03-24"
updated: "2026-03-24"
author: "builder"
```yaml
topic: prompt_caching
scope: otimização de API de LLM (Anthropic, OpenAI, Google)
owner: builder
criticality: high
```
## Conceitos-Chave
- **Cache-Control**: Anthropic `cache_control: {kind: "ephemeral"}`; TTL de 5 min
- **Correspondência de Prefixo**: cache hit quando o prefixo é idêntico byte a byte
- **Tokens Mínimos**: Anthropic >= 1024; OpenAI >= 1024 (automático)
- **Divisão de Preço**: escrita 1.25x do preço-base, leitura 0.1x (90% de economia no hit)
## Fases da Estratégia
1. **Auditoria**: identifique prompts com >50% de conteúdo estático
2. **Reordenação**: estático primeiro (system > few-shot > RAG), dinâmico por último
```text
[Requisição] -> [Hash do Prefixo] -> [Busca no Cache]
                                   |
                         HIT: custo 0.1x, 85% mais rápido
                         MISS: custo 1.25x, velocidade normal
                                   |
                             [Geração] -> [Resposta]
```
## Comparativo
| Provider | Tokens Mín. | Config | Escrita | Leitura | TTL |
|----------|-----------|--------|-------|------|-----|
| Anthropic | 1024 | Explícito | 1.25x | 0.1x | 5 min |
| OpenAI | 1024 | Automático | 1.0x | 0.5x | 5-60 min |
| Google | 32768 | Explícito | 1.0x | 0.25x | config |

### S_RELATED: Verificação de Referências Cruzadas (SOFT)
- [ ] campo de frontmatter `related:` preenchido (3-15 entradas)
- [ ] seção `## Related Artifacts` presente no corpo do artifact
- [ ] ao menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva o wiring)
