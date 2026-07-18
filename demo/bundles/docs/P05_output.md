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
# Template de Saida: knowledge_card (domain_kc)
````
id: p01_kc_{{topic_slug}}
kind: knowledge_card
pillar: P01
title: "{{Titulo, 5-100 caracteres}}"
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{agent_group_name}}"
domain: {{domain_name}}
quality: null
tags: [{{tag1}}, {{tag2}}, {{tag3}}, knowledge]
tldr: "{{Denso, <=160 caracteres, sem autorreferencias}}"
when_to_use: "{{Condicao de recuperacao}}"
keywords: [{{kw1}}, {{kw2}}, {{kw3}}]
long_tails:
  - {{consulta long tail 1}}
  - {{consulta long tail 2}}
axioms:
  - {{Regra acionavel ALWAYS/NEVER}}
linked_artifacts:
  primary: {{id_artefato_ou_null}}
  related: [{{id_relacionado_ou_vazio}}]
density_score: {{0.80_to_1.00}}
data_source: "{{url_fonte_ou_referencia_artefato}}"

# {{Titulo}}
## Referencia Rapida
```yaml
topic: {{topic_name}}
scope: {{scope_description}}
owner: {{owner_agent_group}}
criticality: {{baixa|media|alta}}
```
## Conceitos-Chave
- **{{Conceito 1}}**: {{detalhe concreto com exemplo}}
- **{{Conceito 2}}**: {{detalhe concreto com exemplo}}
- **{{Conceito 3}}**: {{detalhe concreto com exemplo}}
## Fases da Estrategia
1. **{{Fase 1}}**: {{acao com resultado mensuravel}}
2. **{{Fase 2}}**: {{acao com resultado mensuravel}}
3. **{{Fase 3}}**: {{acao com resultado mensuravel}}
## Regras de Ouro
- {{REGRA 1 -- acionavel, concreta}}
- {{REGRA 2 -- acionavel, concreta}}
- {{REGRA 3 -- acionavel, concreta}}
## Fluxo
```text
[{{Entrada}}] -> [{{Processo}}] -> [{{Decisao}}] -> [{{Saida}}]
```
## Comparativo
| {{Dimensao}} | {{Opcao A}} | {{Opcao B}} |
|---------------|-------------|-------------|
| {{Linha 1}} | {{valor}} | {{valor}} |
| {{Linha 2}} | {{valor}} | {{valor}} |
## Referencias
- Artefato relacionado: {{artifact_ref}}
- Fonte: {{external_url}}
````
NOTA: Para meta_kc, substitua o corpo por:
Resumo Executivo, Tabela de Especificacao, Padroes, Antipadroes, Aplicacao, Referencias.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_prompt_knowledge_card]] | a montante | 0.24 |
| p10_out_knowledge_card | a jusante | 0.22 |
| [[bld_schema_knowledge_card]] | a jusante | 0.21 |
| [[bld_config_knowledge_card]] | a jusante | 0.20 |
| [[bld_knowledge_knowledge_card]] | a montante | 0.18 |
