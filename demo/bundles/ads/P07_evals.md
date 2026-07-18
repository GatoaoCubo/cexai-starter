---
id: p11_qg_prompt_template
kind: quality_gate
pillar: P11
llm_function: GOVERN
domain: prompt_template
version: 1.0.0
created: '2026-03-27'
updated: '2026-07-04'
author: builder
tags:
- eval
- P11
- quality_gate
- examples
quality: null
title: 'Gate: Prompt Template'
tldr: Quality gate for reusable prompt molds with typed {{variables}}, injection points,
  and composable structure.
8f: "F7_govern"
density_score: 0.85
related:
  - p11_qg_quality_gate
  - p11_qg_response_format
  - bld_knowledge_card_quality_gate
  - p03_ins_prompt_template
  - p11_qg_kind_builder
  - p11_qg_system_prompt
  - p11_qg_guardrail
  - p11_qg_creation_artifacts
  - p11_qg_validator
  - p11_qg_runtime_state
---
## Gate de Qualidade

## Definição
Um prompt template é um molde de texto reutilizável contendo um ou mais placeholders `{{variable}}` preenchidos no momento da invocação. Ele declara onde na conversa é injetado (turno system ou user), documenta o tipo e as restrições de cada variável, e fornece ao menos um exemplo completo de invocação com todos os slots preenchidos.
Escopo: arquivos com `kind: prompt_template`. Não se aplica a system prompts (texto fixo, sem slots) ou a arquivos instruction (regras comportamentais, sem slots de variável).
## Gates HARD
Falha em qualquer gate isolado significa REJECT, independente da nota soft.
> Renumerado em 2026-07-04 (R-262a) para alinhar com a sequência canônica
> H01-H06 em `.claude/rules/8f-reasoning.md` e com a ordem real dos gates em
> `_tools/cex_8f_runner.py` (H02 padrão de id, H03 kind confere, H04 quality
> null, H05 campos obrigatórios, H06 tamanho do corpo). A numeração anterior
> inseria um gate extra "id == stem do arquivo" como seu próprio H03,
> deslocando tudo para baixo e reaproveitando o H06 para a checagem de campos
> obrigatórios em vez do tamanho do corpo -- a mesma classe de desvio que o
> R-259 encontrou em bld_eval_benchmark.md / bld_eval_guardrail.md.
> `id == stem do arquivo` foi incorporado ao H02 abaixo (ambos são questões
> de validade de id).
| ID  | Predicado | Como testar |
|-----|-----------|-------------|
| H01 | Frontmatter parseia como YAML válido | `yaml.safe_load(frontmatter)` não gera erro |
| H02 | `id` corresponde ao namespace `p03_pt_*` E `id` é igual ao stem do arquivo | `id.startswith("p03_pt_")` é verdadeiro E `Path(file).stem == id` |
| H03 | `kind` é igual ao literal `prompt_template` | checagem de igualdade de string |
| H04 | `quality` é null no momento da autoria | `quality is None` |
| H05 | Todos os campos de frontmatter obrigatórios presentes e não vazios | id, kind, pillar, version, quality, tags, created, tldr todos presentes -- ver `bld_schema_prompt_template.md`, tier Recomendado, para os 7 campos soft (title, updated, author, variables, variable_syntax, composable, domain) |
| H06 | Tamanho do corpo dentro do limite | `len(body.encode('utf-8')) <= 8192` (max_bytes conforme Restrições de bld_schema_prompt_template.md) |
## Pontuação SOFT
Pontue cada dimensão de 0 (ausente ou falha) a 1 (presente e aprovada). Pesos são 0.5 ou 1.0.
| #  | Dimensão | Peso |
|----|-----------|--------|
| 1  | Campo `density_score` presente e >= 0.80 | 1.0 |
| 2  | Toda variável tem ao menos uma restrição (enum, regex, max_len ou range) | 1.0 |
| 3  | Sintaxe uniforme em todo o documento (tudo `{{}}` Mustache ou tudo `[]` colchetes, nunca misturado) | 1.0 |
| 4  | Exemplo completo de invocação presente, com todo slot de variável preenchido | 1.0 |
| 5  | Valores default documentados para todas as variáveis opcionais | 0.5 |
| 6  | Lista de tags inclui `prompt-template` | 0.5 |
**Fórmula**: `final_score = (soma de score_i * peso_i) / (soma de peso_i) * 10`
Peso total: 9.0. Cada dimensão contribui proporcionalmente. Faixa de nota: 0.0 a 10.0.
## Ações
| Tier | Limiar | Ação |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publicar no pool como golden; adicionar à biblioteca curada de prompts |
| PUBLISH | >= 8.0 | Publicar no pool; marcar como pronto para produção |
| REVIEW | >= 7.0 | Devolver ao autor com feedback pontuado por dimensão; um ciclo de revisão permitido |
| REJECT | < 7.0 | Bloquear do pool; reescrita completa exigida antes de reavaliar |
## Bypass
| Campo | Valor |
|-------|-------|
| condition | Template é um auxiliar de migração pontual com prazo de vida documentado abaixo de 30 dias |
| approver | O responsável pelo domínio deve aprovar por escrito antes do bypass valer |
| audit_log | Registrar em `artifacts/audits/bypasses.md` com data, aprovador e motivo |
| expiry | 30 dias a partir da concessão do bypass; o template deve ser aposentado ou trazido à conformidade total |

## Exemplos

# Exemplos — prompt-template-builder
## Exemplo Golden
Um artefato `prompt_template` completo e válido, com 19+ campos.
```yaml
id: p03_pt_knowledge_card_production
kind: prompt_template
pillar: P03
title: "Knowledge Card Production Template"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: knowledge-engine
```
```
You are a knowledge synthesis expert. Produce a knowledge card for the following topic.
Topic: `{{topic}}`
Domain: `{{domain}}`
Audience level: `{{audience}}`
Maximum sections: `{{max_sections}}`
Include examples: `{{include_examples}}`
Source references: `{{source_refs}}`
Structure your output as follows:
1. TLDR (1 sentence)
2. Core Definition (2-3 sentences, precise, domain-appropriate)
3. Key Concepts (up to `{{max_sections}}` bullet points)
4. Relationships (how `{{topic}}` connects to adjacent concepts in `{{domain}}`)
5. Common Misconceptions (2-3 items, audience-calibrated for `{{audience}}`)
{{#include_examples}}
6. Concrete Examples (2-3 examples grounded in `{{domain}}`)
{{/include_examples}}
7. References: `{{source_refs}}`
Calibrate terminology and depth for a `{{audience}}`-level reader in `{{domain}}`.
```

### S_RELATED: Checagem de Referências Cruzadas (SOFT)
- [ ] Campo de frontmatter `related:` populado (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Ao menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, apenas incentiva a interligação)
