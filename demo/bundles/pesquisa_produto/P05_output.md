---
kind: output_template
id: bld_output_template_knowledge_card
pillar: P05
llm_function: PRODUCE
purpose: Template com {{vars}} para a produção de knowledge_card
pattern: todo campo aqui existe no SCHEMA.md -- o template deriva, nunca inventa
quality: null
title: "Template de Saída: Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e contraexemplos para a construção de knowledge cards, demonstrando estrutura ideal e erros comuns."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
density_score: 0.90
related:
  - bld_schema_knowledge_card
  - bld_config_knowledge_card
---
# Template de Saída: knowledge_card (domain_kc)
```yaml
id: p01_kc_{{topic_slug}}
kind: knowledge_card
pillar: P01
title: "{{Title 5-100 chars}}"
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{agent_group_name}}"
domain: {{domain_name}}
quality: null
tags: [{{tag1}}, {{tag2}}, {{tag3}}, knowledge]
tldr: "{{Dense <=160ch, no self-refs}}"
when_to_use: "{{Retrieval condition}}"
keywords: [{{kw1}}, {{kw2}}, {{kw3}}]
long_tails:
  - {{long tail query 1}}
  - {{long tail query 2}}
axioms:
  - {{ALWAYS/NEVER actionable rule}}
linked_artifacts:
  primary: {{artifact_id_or_null}}
  related: [{{related_id_or_empty}}]
density_score: {{0.80_to_1.00}}
data_source: "{{source_url_or_artifact_ref}}"
# {{Title}}
## Referência Rápida
` ``yaml
topic: {{topic_name}}
scope: {{scope_description}}
owner: {{owner_agent_group}}
criticality: {{low|medium|high}}
` ``
## Conceitos-Chave
- **{{Concept 1}}**: {{concrete detail with example}}
- **{{Concept 2}}**: {{concrete detail with example}}
- **{{Concept 3}}**: {{concrete detail with example}}
## Fases da Estratégia
1. **{{Phase 1}}**: {{action with measurable outcome}}
2. **{{Phase 2}}**: {{action with measurable outcome}}
3. **{{Phase 3}}**: {{action with measurable outcome}}
## Regras de Ouro
- {{RULE 1 — actionable, concrete}}
- {{RULE 2 — actionable, concrete}}
- {{RULE 3 — actionable, concrete}}
## Fluxo
` ``text
[{{Input}}] -> [{{Process}}] -> [{{Decide}}] -> [{{Output}}]
` ``
## Comparativo
| {{Dimension}} | {{Option A}} | {{Option B}} |
|---------------|-------------|-------------|
| {{Row 1}} | {{val}} | {{val}} |
| {{Row 2}} | {{val}} | {{val}} |
## Referências
- Related artifact: {{artifact_ref}}
- Source: {{external_url}}
```
NOTA: Para meta_kc, substitua o corpo por:
Resumo Executivo, Tabela de Especificações, Padrões, Antipadrões, Aplicação, Referências.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_knowledge_card]] | upstream | 0.24 |
| p10_out_knowledge_card | downstream | 0.22 |
| [[bld_schema_knowledge_card]] | downstream | 0.21 |
| [[bld_config_knowledge_card]] | downstream | 0.20 |
| [[bld_knowledge_knowledge_card]] | upstream | 0.18 |
