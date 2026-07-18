---
kind: quality_gate
id: p01_qg_research_universe
pillar: P11
llm_function: GOVERN
purpose: Gate de qualidade com pontuação HARD e SOFT para research_universe
quality: null
title: "Quality Gate Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, quality_gate]
tldr: "Gate de qualidade com pontuação HARD e SOFT para artefatos research_universe -- foco no mecanismo ok/blocked/skipped"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F7_govern"
keywords: [research_universe construction, quality gate research universe, status honesto, fabricação de dados, research_universe, builder, quality_gate, golden example, anti-example]
density_score: 0.88
related:
  - research-universe-builder
---
## Gate de Qualidade

## Definição
| métrica | limiar | operador | escopo |
|--------|-----------|----------|-------|
| Padrão de ID | `^p01_ru_[a-z][a-z0-9_]+\.md$` | corresponde | todos os arquivos research_universe |

## Gates HARD
| ID | Verificação | Condição de Falha |
|----|-------|----------------|
| H01 | Frontmatter YAML válido | sintaxe YAML inválida |
| H02 | ID corresponde ao padrão `^p01_ru_[a-z][a-z0-9_]+\.md$` | ID não corresponde ao padrão |
| H03 | Campo kind igual a "research_universe" | kind != "research_universe" |
| H04 | Lista `lanes` com exatamente 6 entradas, uma por trilha canônica | trilha ausente, duplicada, ou fora das 6 canônicas |
| H05 | Toda trilha com status `ok` cita >= 1 fonte com data de acesso | dado `ok` sem fonte ou sem data |
| H06 | Nenhum número de CNPJ, índice de reputação ou volume de busca sem fonte citada | valor numérico presente sem procedência associada |
| H07 | Trilhas `blocked` ou `skipped` tem motivo explícito (não apenas o rótulo) | motivo ausente na Tabela de Status por Trilha |

## Pontuação SOFT
| Dim | Dimensão | Peso | Guia de Pontuação |
|-----|-----------|--------|---------------|
| D1 | Cobertura honesta das 6 trilhas | 0.20 | Todas tentadas e reportadas com precisão = 1.0; trilhas omitidas da tabela final = 0.0 |
| D2 | Atualidade da procedência | 0.20 | Reputação/sentimento datados <= 90 dias, firmografia <= 12 meses = 1.0; sem data ou muito antigo = 0.0 |
| D3 | Distinção `blocked` vs `skipped` | 0.20 | Sempre correta e justificada = 1.0; rótulos trocados ou sem motivo = 0.0 |
| D4 | Profundidade multi-perspectiva | 0.15 | >= 3 papéis distintos, perguntas específicas a semente = 1.0; genérico ou < 3 papéis = 0.0 |
| D5 | Utilidade da trilha SEO | 0.10 | Termos + intenção + volume/estimativa rotulada = 1.0; termos genéricos sem intenção = 0.0 |
| D6 | Síntese executiva acionável | 0.15 | 1 achado concreto por trilha `ok`, `coverage_score` bate com a tabela = 1.0; síntese vaga ou número de cobertura incorreto = 0.0 |

**Pontuação = soma(pts * peso) / soma(pts_max * peso) * 10**

## Ações
| Pontuação | Ação |
|-------|--------|
| >= 9.5 | Publicação automática no repositório de pesquisa |
| >= 8.0 | Revisão por um analista sênior e depois publicação |
| >= 7.0 | Sinalizar para revisão antes de compartilhar com o solicitante |
| < 7.0 | Revisar e reenviar -- geralmente falha de procedência ou de honestidade `ok`/`blocked`/`skipped` |

## Bypass
| condições | aprovador | trilha de auditoria |
|------------|----------|-------------|
| Prazo urgente com poucas trilhas acessíveis (ex.: due diligence rápida) | Analista sênior | Registro no próprio relatório, seção "Limitações e Próximos Passos", com justificativa e prazo |

## Exemplos

## Exemplo de Referência (trecho -- Tabela de Status por Trilha)
```markdown
| Trilha | Status | Motivo (se blocked/skipped) |
|--------|--------|-------------------------------|
| Firmografia | ok | -- (CNPJ localizado, consulta pública em 2026-07-15) |
| Sinal Social | ok | -- (loja de app + Reddit acessados em 2026-07-15) |
| Reputação | blocked | Página do Reclame Aqui exigiu verificação adicional; não acessada nesta sessão |
| Sentimento em PT | ok | Classificado sobre o texto coletado na trilha Sinal Social |
| SEO | ok | Termos validados via busca nativa em 2026-07-15 |
| Perguntas Multi-Perspectiva | ok | 4 papéis cobertos |
```
Cobertura: 5/6 = 0.83. A trilha `blocked` fica explícita, com motivo -- não é escondida nem preenchida com um número estimado.

## Anti-Exemplo 1: Número Sem Procedência
```markdown
| Reputação | Valor |
|-----------|-------|
| Índice Reclame Aqui | 7.8 |
```
## Por que falha: apresenta um índice de reputação como se fosse dado real sem citar fonte nem data de acesso -- viola H05 e H06. Se o índice não foi de fato consultado, a trilha deveria estar `blocked`, com o campo de valor vazio.

## Anti-Exemplo 2: Confundir `blocked` com `skipped`
```markdown
| Trilha | Status |
|--------|--------|
| Firmografia | skipped |
```
com a nota do agente: "não consegui acessar a Receita Federal agora."
## Por que falha: a justificativa descreve uma falha de ACESSO (`blocked`), mas o status registrado é `skipped` (que deveria significar "esta trilha não se aplica a esta semente"). Rotular errado esconde do usuário que a fonte existe e vale tentar de novo -- viola H07 e a Dimensão D3.

### H_RELATED: Verificação de Referência Cruzada (HARD)
- [ ] Campo `related:` do frontmatter preenchido (mínimo 3 entradas)
- [ ] Seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJEITAR se < 3 entradas

### S_RELATED: Verificação de Referência Cruzada (SOFT)
- [ ] Campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] Seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a conexão)
