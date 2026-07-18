---
kind: instruction
id: bld_instruction_roi_calculator
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para roi_calculator
quality: null
title: "Instrução -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, instruction]
tldr: "Processo de produção passo a passo para roi_calculator"
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [construção de roi_calculator, instrução roi calculator, roi_calculator, builder, instruction, lucro líquido, investimento total, related artifacts, parâmetros de entrada, definir fórmula]
density_score: 0.85
related:
  - roi-calculator-builder
  - kc_roi_calculator
---
## Fase 1: PESQUISA
1. Identificar os parâmetros de entrada: investimento inicial, economia anual, custo de implementação, taxas de manutenção e horizonte de tempo.
2. Pesquisar benchmarks do setor para limiares de ROI e componentes de TCO (hardware, software, mão de obra).
3. Definir a fórmula de ROI: (Lucro Líquido / Investimento Total) x 100. Definir a fórmula de TCO: soma de todos os custos recorrentes e únicos.
4. Coletar estudos de caso para cenários de compradores econômicos (ex.: SaaS empresarial, automação industrial).
5. Mapear as dependências entre variáveis (ex.: efeitos de escala sobre o TCO).
6. Validar as fontes de dados quanto a precisão (bases financeiras, cotações de fornecedores).

## Fase 2: COMPOSIÇÃO
1. Definir o schema em bld_schema_roi_calculator.md: especificar tipos de entrada, unidades e restrições.
2. Mapear as entradas para as fórmulas de ROI/TCO usando a estrutura de bld_output_template_roi_calculator.md.
3. Escrever a lógica das fórmulas para cálculos dinâmicos (ex.: taxa de crescimento anual composta).
4. Construir a tabela comparativa de TCO com colunas: categoria de custo, linha de base, alternativa, delta.
5. Preencher o modelo com valores de exemplo para os campos de entrada do usuário.
6. Adicionar exemplos de cenário (ex.: ROI de 3 anos vs. 5 anos).
7. Formatar a saída para clareza: destacar deltas positivos/negativos por cor, incluir gráficos.
8. Fazer revisão por pares da lógica das fórmulas em relação aos benchmarks específicos do domínio.
9. Finalizar o artefato com controle de versão e changelog.

## Fase 3: VALIDAÇÃO
1. [ ] Verificar a precisão das fórmulas com dados de amostra (ex.: 10% de ROI, $50k de TCO).
2. [ ] Testar casos-limite (investimento zero, economia negativa).
3. [ ] Confirmar que a comparação de TCO está alinhada com os parâmetros de entrada.
4. [ ] Garantir que o modelo de saída seja renderizado corretamente em qualquer dispositivo.
5. [ ] Conduzir testes de aceitação com compradores econômicos reais.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[roi-calculator-builder]] | downstream | 0.44 |
| [[kc_roi_calculator]] | upstream | 0.42 |
| [[bld_knowledge_roi_calculator]] | upstream | 0.40 |
