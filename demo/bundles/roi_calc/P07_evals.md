---
kind: quality_gate
id: p11_qg_roi_calculator
pillar: P11
llm_function: GOVERN
purpose: Portão de qualidade com pontuação HARD e SOFT para roi_calculator
quality: null
title: "Portão de Qualidade -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, quality_gate]
tldr: "Portão de qualidade com pontuação HARD e SOFT para roi_calculator"
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [construção de roi_calculator, portão de qualidade roi calculator, roi_calculator, builder, quality_gate, portão de qualidade, condição de falha, guia de pontuação, exemplo padrão ouro, migração para nuvem]
density_score: 0.85
related:
  - kc_roi_calculator
  - roi-calculator-builder
---
## Definição
| métrica         | limiar | operador | escopo          |
|----------------|-----------|----------|----------------|
| Precisão       | 95%       | >=       | Compradores econômicos|
| Completude   | 100%      | ==       | Todas as entradas     |

## Gates HARD
| ID             | Verificação                          | Condição de Falha                              |
|----------------|--------------------------------|---------------------------------------------|
| H01            | Frontmatter YAML válido         | Frontmatter ausente ou inválido              |
| H02            | ID corresponde ao padrão             | ID não corresponde a ^p11_roi_[a-z][a-z0-9_]+$ |
| H03            | Campo kind corresponde a 'roi_calculator' | Campo kind inválido                          |
| H04            | Parâmetros de entrada definidos       | Campos de entrada obrigatórios ausentes              |
| H05            | Fórmula de ROI matematicamente válida | Erros de fórmula ou variáveis não definidas       |
| H06            | Comparação de TCO incluida        | Tabela de comparação de TCO ausente            |
| H07            | Unidades de saída especificadas         | Unidades de saída ausentes ou ambíguas          |

## Pontuação SOFT
| Dim        | Dimensão         | Peso | Guia de Pontuação                          |
|------------|-------------------|--------|----------------------------------------|
| D01        | Precisão          | 0.15   | 100% = 1.0, 90% = 0.9                   |
| D02        | Completude      | 0.15   | 100% = 1.0, 80% = 0.8                   |
| D03        | Clareza           | 0.10   | Clara = 1.0, ambígua = 0.5            |
| D04        | Comparação de TCO    | 0.15   | Detalhada = 1.0, parcial = 0.7           |
| D05        | Facilidade de uso | 0.10   | Intuitiva = 1.0, complexa = 0.5          |
| D06        | Consistência       | 0.10   | Sem contradições = 1.0, 1+ erros = 0.5 |
| D07        | Documentação     | 0.15   | Completa = 1.0, parcial = 0.7               |
| D08        | Versionamento        | 0.10   | Versionado = 1.0, sem versão = 0.5      |

## Ações
| Pontuação     | Ação         |
|-----------|----------------|
| GOLDEN    | Aprovar        |
| PUBLISH   | Publicar        |
| REVIEW    | Revisão por pares    |
| REJECT    | Rejeitar        |

## Exceção (Bypass)
| condições                          | aprovador       | trilha de auditoria              |
|------------------------------------|----------------|--------------------------|
| Projeto crítico com aprovação sênior | CTO           | "Exceção aprovada pelo CTO em 2023-10-01" |

## Exemplo Padrão-Ouro
```yaml
title: ROI Calculator for Cloud Migration
author: A. Smith, Financial Analyst
date: 2023-10-15
inputs:
  - Initial Investment: $5,000
  - Monthly Cloud Cost (AWS EC2): $200
  - Monthly Savings (vs. On-Premises): $1,000
  - Time Horizon: 12 months
formulas:
  ROI: ((Monthly Savings × Time Horizon) - Initial Investment) / Initial Investment × 100
  Payback Period: Initial Investment / Monthly Savings
  TCO: Initial Investment + (Monthly Cloud Cost × Time Horizon)
tco_comparison:
  AWS: $7,400
  Azure: $7,500
  GCP: $7,300
```

## Anti-Exemplo 1: Nomes de Placeholder
```yaml
title: ROI Calculator for ProviderA
inputs:
  - Initial Investment: $X
  - Monthly Cost: $Y
formulas:
  ROI: (Y - X) / X
tco_comparison:
  ProviderA: $Z
```
## Por que falha
Usa placeholders genéricos como "ProviderA" e "$X" em vez de nomes reais de fornecedores e valores concretos, o que torna impossível para os compradores econômicos comparar opções ou validar premissas.

## Anti-Exemplo 2: Comparação de TCO Ausente
```yaml
title: ROI Calculator for AWS
inputs:
  - Initial Investment: $5,000
  - Monthly Savings: $1,000
formulas:
  ROI: (1,000 × 12 - 5,000) / 5,000 × 100
```
## Por que falha
Omite a seção de comparação de TCO, que é crítica para os compradores econômicos avaliarem os custos totais entre fornecedores. Sem o TCO, a calculadora carece de insights acionáveis para a tomada de decisão.

### H_RELATED: Verificação de Referência Cruzada (HARD)
- [ ] Campo de frontmatter `related:` preenchido (mínimo de 3 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJECT se < 3 entradas (auto-preenchido por cex_wikilink.py em F6.5)

### S_RELATED: Verificação de Referência Cruzada (SOFT)
- [ ] Campo de frontmatter `related:` preenchido (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a interligação)
