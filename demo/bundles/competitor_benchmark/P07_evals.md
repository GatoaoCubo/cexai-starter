---
kind: quality_gate
id: p01_qg_competitive_matrix
pillar: P11
llm_function: GOVERN
purpose: Gate de qualidade com pontuação HARD e SOFT para competitive_matrix
quality: null
title: "Quality Gate Competitive Matrix"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, quality_gate]
tldr: "Gate de qualidade com pontuação HARD e SOFT para artefatos competitive_matrix"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [competitive_matrix construction, quality gate competitive matrix, competitive_matrix, builder, quality_gate, "## anti-example 1: vague vendor names", quality gate, fail condition, scoring guide, golden example]
density_score: 0.85
related:
  - competitive-matrix-builder
---
## Gate de Qualidade

## Definição
| métrica | limiar | operador | escopo |
|--------|-----------|----------|-------|
| Padrão de ID | ^p01_cm_[a-z][a-z0-9_]+\\.md$ | corresponde | todos os arquivos competitive_matrix |

## Gates HARD
| ID | Verificação | Condição de Falha |
|----|-------|----------------|
| H01 | Frontmatter YAML válido | sintaxe YAML inválida |
| H02 | ID corresponde ao padrão ^p01_cm_[a-z][a-z0-9_]+\\.md$ | ID não corresponde ao padrão |
| H03 | Campo kind igual a "competitive_matrix" | kind != "competitive_matrix" |
| H04 | Feature parity grid presente com 3+ concorrentes | menos de 3 concorrentes na matriz |
| H05 | Todas as fontes de dados citadas com data de acesso | dado não verificado ou sem data |
| H06 | Seção de battle card presente para o concorrente primário | ausência de comparação nos-vs-eles |
| H07 | Nenhuma linguagem subjetiva sem suporte de dados | alegações não comprovadas (ex.: "melhor", "líder") |

## Pontuação SOFT
| Dim | Dimensão | Peso | Guia de Pontuação |
|-----|-----------|--------|---------------|
| D1 | Completude | 0.20 | Todas as funcionalidades mapeadas para todos os concorrentes = 1.0; lacunas = proporcional |
| D2 | Precisão dos dados | 0.20 | Fontes primárias citadas, datadas nos últimos 12 meses = 1.0; desatualizadas/secundárias = 0.5 |
| D3 | Clareza da diferenciação | 0.15 | Razões de vitória explícitas por capacidade = 1.0; vago = 0.0 |
| D4 | Usabilidade do battle card | 0.15 | Objeção + contra-argumento presentes para o concorrente primário = 1.0; ausente = 0.0 |
| D5 | Posicionamento MQ | 0.15 | Posicionamento em quadrante estilo Gartner com justificativa = 1.0; ausente = 0.0 |
| D6 | Cobertura anti-FUD | 0.15 | Pelo menos 3 contra-argumentos factuais com fontes = 1.0; nenhum = 0.0 |

## Ações
| Pontuação | Ação |
|-------|--------|
| >= 9.5 | Publicação automática no portal de vendas |
| >= 8.0 | Revisão pelo PM e depois publicação |
| >= 7.0 | Sinalizar para revisão de QA |
| < 7.0 | Revisar e reenviar |

## Bypass
| condições | aprovador | trilha de auditoria |
|------------|----------|-------------|
| Prazo de RFP urgente com dados de concorrentes incompletos | CTO | Registro de e-mail com referência do RFP e prazo |

## Exemplos

## Exemplo de Referência
```markdown
---
title: "Competitive Matrix: CRM Solutions"
date: 2023-10-15
author: Sales Strategy Team
version: 1.2
---

| Feature                | Salesforce       | HubSpot          | Pipedrive        |
|-----------------------|------------------|------------------|------------------|
| Lead Scoring          | Advanced (AI)    | Basic            | Customizable     |
| Automation            | Full workflow    | Limited          | Mid-level        |
| Integration (API)     | 500+ apps        | 300+ apps        | 150+ apps        |
| Pricing Model         | Tiered (per user)| Flat fee         | Per deal         |
| Support               | 24/7 premium     | Business hours   | Email only       |
| Strengths             | Enterprise scale | Marketing focus  | Sales simplicity |
| Weaknesses            | Complex UI       | Limited AI       | No marketing tools |
```

## Anti-Exemplo 1: Nomes de Fornecedores Vagos
```markdown
| Feature       | ProviderA | ProviderB |
|---------------|-----------|-----------|
| Speed         | Fast      | Slow      |
| Cost          | High      | Low       |
| Ease of Use   | Easy      | Hard      |
```
## Por que falha: Usa nomes de placeholder genéricos (ProviderA/ProviderB) em vez de nomes reais de fornecedores, tornando a matriz inacionável para times de vendas que precisam de insights competitivos específicos.

## Anti-Exemplo 2: Dimensões Competitivas Ausentes
```markdown
| Feature       | Salesforce | HubSpot |
|---------------|------------|---------|
| Pricing       | $150/user  | $50/user|
| UI            | Complex    | Simple  |
```
## Por que falha: Inclui apenas funcionalidades básicas sem dimensões competitivas críticas como capacidades de automação, profundidade de integração ou modelos de suporte, que são essenciais para avaliações de procurement.

### H_RELATED: Verificação de Referência Cruzada (HARD)
- [ ] Campo `related:` do frontmatter preenchido (mínimo 3 entradas)
- [ ] Seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJEITAR se < 3 entradas (auto-preenchido por cex_wikilink.py em F6.5)

### S_RELATED: Verificação de Referência Cruzada (SOFT)
- [ ] Campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] Seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a conexão)
