---
kind: output_template
id: bld_output_template_knowledge_card
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} for knowledge_card production
pattern: every field here exists in SCHEMA.md — template derives, never invents
quality: null
title: "Output Template Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
density_score: 0.90
related:
  - bld_schema_knowledge_card
  - bld_config_knowledge_card
---
# Modelo de Saída: knowledge_card (domain_kc)
```yaml
id: p01_kc_{{topic_slug}}
kind: knowledge_card
pillar: P01
title: "{{Título de 5-100 caracteres}}"
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{agent_group_name}}"
domain: {{domain_name}}
quality: null
tags: [{{tag1}}, {{tag2}}, {{tag3}}, knowledge]
tldr: "{{Denso, <=160 caract., sem autorreferência}}"
when_to_use: "{{Condição de recuperação}}"
keywords: [{{kw1}}, {{kw2}}, {{kw3}}]
long_tails:
  - {{consulta long tail 1}}
  - {{consulta long tail 2}}
axioms:
  - {{regra acionável SEMPRE/NUNCA}}
linked_artifacts:
  primary: {{artifact_id_or_null}}
  related: [{{related_id_or_empty}}]
density_score: {{0.80_to_1.00}}
data_source: "{{source_url_or_artifact_ref}}"
# {{Título}}
## Referência Rápida
` ``yaml
topic: {{topic_name}}
scope: {{scope_description}}
owner: {{owner_agent_group}}
criticality: {{low|medium|high}}
` ``
## Conceitos-Chave
- **{{Conceito 1}}**: {{detalhe concreto com exemplo}}
- **{{Conceito 2}}**: {{detalhe concreto com exemplo}}
- **{{Conceito 3}}**: {{detalhe concreto com exemplo}}
## Fases da Estratégia
1. **{{Fase 1}}**: {{ação com resultado mensurável}}
2. **{{Fase 2}}**: {{ação com resultado mensurável}}
3. **{{Fase 3}}**: {{ação com resultado mensurável}}
## Regras de Ouro
- {{REGRA 1 -- acionável, concreta}}
- {{REGRA 2 -- acionável, concreta}}
- {{REGRA 3 -- acionável, concreta}}
## Fluxo
` ``text
[{{Entrada}}] -> [{{Processo}}] -> [{{Decisão}}] -> [{{Saída}}]
` ``
## Comparativo
| {{Dimensão}} | {{Opção A}} | {{Opção B}} |
|---------------|-------------|-------------|
| {{Linha 1}} | {{val}} | {{val}} |
| {{Linha 2}} | {{val}} | {{val}} |
## Referências
- Artefato relacionado: {{artifact_ref}}
- Fonte: {{external_url}}
```
NOTA: Para meta_kc, substitua o corpo por:
Resumo Executivo, Tabela de Especificação, Padrões, Anti-Padrões, Aplicação, Referências.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_knowledge_card]] | upstream | 0.24 |
| p10_out_knowledge_card | downstream | 0.22 |
| [[bld_schema_knowledge_card]] | downstream | 0.21 |
| [[bld_config_knowledge_card]] | downstream | 0.20 |
| [[bld_knowledge_knowledge_card]] | upstream | 0.18 |
