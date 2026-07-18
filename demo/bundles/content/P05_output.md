---
kind: output_template
id: bld_output_template_knowledge_card
pillar: P05
llm_function: PRODUCE
purpose: "Template com {{vars}} para producao de knowledge_card"
pattern: "todo campo aqui existe no SCHEMA.md -- o template deriva, nunca inventa"
quality: null
title: "Modelo de Saida: knowledge_card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
density_score: 0.90
related:
  - bld_schema_knowledge_card
  - bld_config_knowledge_card
---
# Modelo de Saida: knowledge_card (domain_kc)
```yaml
id: p01_kc_{{topic_slug}}
kind: knowledge_card
pillar: P01
title: "{{Titulo, 5-100 caracteres}}"
version: "1.0.0"
created: "{{AAAA-MM-DD}}"
updated: "{{AAAA-MM-DD}}"
author: "{{nome_do_agent_group}}"
domain: {{nome_do_dominio}}
quality: null
tags: [{{tag1}}, {{tag2}}, {{tag3}}, knowledge]
tldr: "{{Denso, <=160 caracteres, sem auto-referencia}}"
when_to_use: "{{Condicao de recuperacao}}"
keywords: [{{kw1}}, {{kw2}}, {{kw3}}]
long_tails:
  - {{consulta de cauda longa 1}}
  - {{consulta de cauda longa 2}}
axioms:
  - {{regra acionavel SEMPRE/NUNCA}}
linked_artifacts:
  primary: {{id_do_artefato_ou_null}}
  related: [{{id_relacionado_ou_vazio}}]
density_score: {{0.80_a_1.00}}
data_source: "{{url_de_origem_ou_ref_de_artefato}}"
# {{Titulo}}
## Referencia Rapida
` ``yaml
topic: {{nome_do_topico}}
scope: {{descricao_do_escopo}}
owner: {{agent_group_responsavel}}
criticality: {{baixa|media|alta}}
` ``
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
` ``text
[{{Entrada}}] -> [{{Processo}}] -> [{{Decisao}}] -> [{{Saida}}]
` ``
## Comparativo
| {{Dimensao}} | {{Opcao A}} | {{Opcao B}} |
|---------------|-------------|-------------|
| {{Linha 1}} | {{val}} | {{val}} |
| {{Linha 2}} | {{val}} | {{val}} |
## Referencias
- Artefato relacionado: {{ref_do_artefato}}
- Fonte: {{url_externa}}
```
NOTA: para meta_kc, substitua o corpo por: Resumo Executivo, Tabela de Especificacao,
Padroes, Anti-Padroes, Aplicacao, Referencias (ver `P06_schema.md` para a definicao completa).

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_prompt_knowledge_card]] | upstream | 0.24 |
| p10_out_knowledge_card | downstream | 0.22 |
| [[bld_schema_knowledge_card]] | downstream | 0.21 |
| [[bld_config_knowledge_card]] | downstream | 0.20 |
| [[bld_knowledge_knowledge_card]] | upstream | 0.18 |
