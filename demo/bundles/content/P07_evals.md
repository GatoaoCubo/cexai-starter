---
kind: quality_gate
id: p11_qg_knowledge_card
pillar: P11
llm_function: GOVERN
purpose: "Exemplos-modelo e anti-exemplos de artefatos knowledge_card"
pattern: "aprendizado few-shot -- o LLM le estes exemplos antes de produzir"
quality: null
title: "Portao: knowledge_card"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, knowledge-card, density, fact, distillation, searchability]
tldr: "Portoes que garantem que artefatos knowledge_card tragam fatos atomicos concretos com densidade >= 0.8, frontmatter semantico, e tamanho de arquivo <= 5KB."
domain: "knowledge_card -- fatos atomicos e pesquisaveis com alta densidade de informacao"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.94
related:
  - p06_bp_knowledge_card
  - p11_qg_golden_test
  - p11_qg_quality_gate
  - p11_qg_citation
  - p07_sr_output_quality_density
  - p11_qg_response_format
  - p11_qg_few_shot_example
  - p11_qg_naming_rule
  - p11_qg_prompt_cache
  - knowledge-card-builder
---
## Portao de Qualidade

# Portao: knowledge_card
## Definicao
| Campo     | Valor |
|-----------|-------|
| metrica   | pontuacao soft ponderada + todos os portoes hard aprovados |
| limiar    | 7.0 para publicar; 8.0 para o pool; 9.5 para golden |
| operador  | AND (todos os hard) + media ponderada (soft) |
| escopo    | qualquer artefato com `kind: knowledge_card` |
## Portoes HARD
Todos precisam passar. Qualquer falha = rejeicao imediata.
| ID  | Verificacao | Condicao de Falha |
|-----|-------|----------------|
| H01 | O frontmatter parseia como YAML valido | Erro de parse em qualquer campo |
| H02 | O ID casa com `^KC_[A-Z0-9_]+$` | Minusculo, prefixo KC_ ausente, ou caracteres nao alfanumericos |
| H03 | O ID e igual ao stem do nome do arquivo | `id: KC_REDIS_TTL` no arquivo `KC_CACHE_TTL.md` |
| H04 | O kind e igual ao literal `knowledge_card` | Qualquer outro valor de kind |
| H05 | O campo quality e `null` | Qualquer valor diferente de null |
| H06 | Todos os 19 campos obrigatorios presentes | Faltando: domain, tldr, density_score, sources, ou card_type |
## Pontuacao SOFT
A soma dos pesos totaliza 100%.
| ID  | Dimensao | Peso | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Concretude factual | 1.0 | O card contem valores especificos, numeros, ou fatos verificaveis | Mistura de fatos e afirmacoes vagas | Totalmente vago ou conceitual |
| S02 | Atomicidade | 1.0 | O card cobre exatamente um conceito, sem expansao de escopo | Majoritariamente um conceito; pequenas tangentes | Multiplos conceitos nao relacionados |
| S03 | Pesquisabilidade -- tags | 1.0 | As tags cobrem dominio, subtopico e angulos de caso de uso (4 ou mais tags distintas) | 3 tags | Menos de 3 tags |
| S04 | Atribuicao de fonte | 1.0 | Pelo menos uma fonte especifica (URL, paper, versao de spec, data) | Fonte mencionada mas nao especifica | Nenhuma fonte |
| S05 | Classificacao do tipo de card | 0.5 | `card_type` e `domain_kc` ou `meta_kc`, com a estrutura de corpo correta para o tipo | Tipo presente mas a estrutura de corpo nao bate | Tipo ausente |
| S06 | Disciplina de densidade | 1.0 | Sem enchimento, sem repeticao, sem frases de preenchimento no corpo | Pequeno enchimento presente | Mais de 20% do conteudo e enchimento |
**Pontuacao = soma(pts * peso) / soma(pts_max * peso) * 10**
## Acoes
| Pontuacao | Nivel | Acao |
|-------|------|--------|
| >= 9.5 | Golden | Publicar no pool de conhecimento como card de referencia autoritativo |
| >= 8.0 | Skilled | Publicar no pool + registrar o padrao |
| >= 7.0 | Learning | Usar mas sinalizar para melhoria |
| < 7.0 | Rejected | Devolver ao autor com o relatorio do portao |
## Excecao (Bypass)
| Campo | Valor |
|-------|-------|
| Condicoes | Topico em rapida evolucao, onde as fontes ainda nao estao estabilizadas (ex.: lancamento novo de biblioteca, mudanca de API que quebra compatibilidade) |
| Aprovador | Revisor especialista de dominio |

## Exemplos

# Exemplos: knowledge-card-builder
## Exemplo-Modelo
ENTRADA: "Destile conhecimento sobre prompt caching para otimizar custos de LLM"
SAIDA:
```yaml
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
title: "Padroes de Prompt Caching para Otimizacao de Custos de LLM"
version: "1.0.0"
created: "2026-03-24"
updated: "2026-03-24"
author: "builder"
```
## Referencia Rapida
```yaml
topic: prompt_caching
scope: otimizacao de API de LLM (Anthropic, OpenAI, Google)
owner: builder
criticality: alta
```
## Conceitos-Chave
- **Cache-Control**: Anthropic `cache_control: {kind: "ephemeral"}`; TTL de 5 min
- **Casamento de Prefixo**: acerto de cache (cache hit) quando o prefixo e identico byte a byte
- **Tokens Minimos**: Anthropic >= 1024; OpenAI >= 1024 (automatico)
- **Divisao de Preco**: escrita 1.25x o base, leitura 0.1x (90% de economia no acerto)
## Fases da Estrategia
1. **Auditoria**: identificar prompts com mais de 50% de conteudo estatico
2. **Reordenar**: estatico primeiro (system > few-shot > RAG), dinamico por ultimo
```text
[Requisicao] -> [Hash do Prefixo] -> [Consulta de Cache]
                                   |
                         ACERTO: custo 0.1x, 85% mais rapido
                         ERRO: custo 1.25x, velocidade normal
                                   |
                             [Gerar] -> [Resposta]
```
## Comparativo
| Provider | Tokens Min | Config | Escrita | Leitura | TTL |
|----------|-----------|--------|-------|------|-----|
| Anthropic | 1024 | Explicita | 1.25x | 0.1x | 5 min |
| OpenAI | 1024 | Automatica | 1.0x | 0.5x | 5-60 min |
| Google | 32768 | Explicita | 1.0x | 0.25x | config |

### S_RELATED: Checagem de Referencia Cruzada (SOFT)
- [ ] campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] secao `## Related Artifacts` presente no corpo do artefato
- [ ] pelo menos 1 referencia upstream e 1 downstream
- Penalidade: -0.3 se vazio (nao bloqueia, apenas incentiva o cross-link)
