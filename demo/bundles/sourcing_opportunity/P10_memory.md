---
kind: memory
id: p10_mem_opportunity_matrix_builder
pillar: P10
llm_function: INJECT
purpose: Padrões aprendidos e armadilhas para a construção de opportunity_matrix
quality: null
title: "Memória -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, memory]
tldr: "Padrões aprendidos e armadilhas para a construção de opportunity_matrix"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F3_inject"
keywords: [construção de opportunity_matrix, memória opportunity matrix builder, opportunity_matrix, builder, memory, observação, padrão, evidência, disciplina honest-null, condições do gate]
density_score: 0.85
related:
  - opportunity-matrix-builder
---
## Observação
A primeira superfície de produção do gerador (W3 CAPGEN, `sourcing_opportunity.py`) foi lançada SOMENTE-OFFLINE: nenhuma chamada de rede ou LLM ao vivo neste nível, então todo artefato construído nos primeiros dias contra ele vai mostrar um scaffold offline (gate BLOQUEADO, células de demanda honest-null) a menos que uma credencial + `demand_sources` sejam fornecidas. Builders que pulam a leitura do código-fonte do gerador primeiro tendem a rascunhar um exemplo com "aparência ao vivo" que a saída real nunca consegue produzir.

## Padrão
Artefatos bem-sucedidos transcrevem títulos/colunas de seção byte a byte de `MOLD_SOURCING_OPPORTUNITY` (`apps/dashboard_web/lib/molds.ts`) em vez de parafraseá-los -- tanto o renderizador quanto `test_capgen_sourcing.py` afirmam igualdade exata de string em títulos, layouts e arrays de coluna.

## Evidência
`_tools/tests/test_capgen_sourcing.py` (516 linhas, referência somente-leitura) trava a contagem de seções em 8, os títulos/layouts de seção numa lista fixa, e os arrays de coluna por tabela para Matriz/Leitura/Verificacao/Match -- qualquer exemplo rascunhado que reordene ou renomeie uma seção falharia esses testes se algum dia fosse usado como dado de teste do gerador (não é; é documentação, mas a mesma disciplina de forma se aplica).

## Recomendações
- Leia `_tools/capability_generators/sourcing_opportunity.py` antes de rascunhar qualquer exemplo -- é a fonte única da verdade, não `capability_contracts_v1.0.md` (que o resume) nem este arquivo de memória.
- Mantenha o bucket manual ("manual / sem preco") e as contagens de cauda-longa visíveis em Cobertura -- um builder que só mostra as linhas ranqueadas do top-N sem contabilizar o resto falha a disciplina S5 de honest-null / sem-descarte-silencioso.
- Declare as 4 condições booleanas do gate `sourcing_confiavel` textualmente, não só o true/false resultante.
- Não importe o pacote de seção LTV/CAC de `n06_unit_econ` para a saída deste kind -- esse aspecto é voltado só a `content_monetization`/`subscription_tier`; opportunity_matrix calcula sua própria margem bruta/líquida diretamente.
- Não construa o builder irmão `product_match` como parte de uma tarefa de opportunity_matrix -- é um kind folha separado, aprovado por ADR (P04/N03), com seu próprio trabalho de scaffolding subsequente.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | upstream | 0.47 |
| [[opportunity-matrix-builder]] | downstream | 0.41 |
| [[bld_knowledge_opportunity_matrix]] | upstream | 0.32 |
| p08_adr_opportunity_matrix_kind | upstream | 0.30 |
