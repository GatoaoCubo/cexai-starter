---
kind: output_template
id: bld_output_template_knowledge_card
pillar: P05
llm_function: PRODUCE
purpose: Template com {{vars}} para a produção de knowledge_card
pattern: todo campo aqui existe no SCHEMA.md -- o template deriva, nunca inventa
quality: null
title: "Output Template Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e anti-exemplos para a construção de knowledge_card, demonstrando a estrutura ideal e as armadilhas mais comuns."
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
````yaml
id: p01_kc_{{topic_slug}}
kind: knowledge_card
pillar: P01
title: "{{Título 5-100 caracteres}}"
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{agent_group_name}}"
domain: {{domain_name}}
quality: null
tags: [{{tag1}}, {{tag2}}, {{tag3}}, knowledge]
tldr: "{{Denso <=160car, sem autorreferências}}"
when_to_use: "{{Condição de retrieval}}"
keywords: [{{kw1}}, {{kw2}}, {{kw3}}]
long_tails:
  - {{long tail query 1}}
  - {{long tail query 2}}
axioms:
  - {{regra acionável SEMPRE/NUNCA}}
linked_artifacts:
  primary: {{artifact_id_or_null}}
  related: [{{related_id_or_empty}}]
density_score: {{0.80_to_1.00}}
data_source: "{{source_url_or_artifact_ref}}"
# {{Título}}
## Referência Rápida
```yaml
topic: {{topic_name}}
scope: {{scope_description}}
owner: {{owner_agent_group}}
criticality: {{low|medium|high}}
```
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
```text
[{{Entrada}}] -> [{{Processo}}] -> [{{Decidir}}] -> [{{Saída}}]
```
## Comparativo
| {{Dimensão}} | {{Opção A}} | {{Opção B}} |
|---------------|-------------|-------------|
| {{Linha 1}} | {{val}} | {{val}} |
| {{Linha 2}} | {{val}} | {{val}} |
## Referências
- Artefato relacionado: {{artifact_ref}}
- Fonte: {{external_url}}
````
NOTA: Para meta_kc, substitua o corpo por:
Resumo Executivo, Tabela de Especificações, Padrões, Antipadrões, Aplicação, Referências.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_knowledge_card]] | a montante | 0.24 |
| p10_out_knowledge_card | a jusante | 0.22 |
| [[bld_schema_knowledge_card]] | a jusante | 0.21 |
| [[bld_config_knowledge_card]] | a jusante | 0.20 |
| [[bld_knowledge_knowledge_card]] | a montante | 0.18 |
