---
kind: instruction
id: bld_instruction_multimodal_prompt
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para multimodal_prompt
quality: null
title: "Instruction Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, instruction]
tldr: "Processo de produção passo a passo para multimodal_prompt"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [construção de multimodal_prompt, instruction multimodal prompt, multimodal_prompt, builder, instruction, modalidades, visão, áudio, texto, cross_ref]
density_score: 0.85
related:
  - multimodal-prompt-builder
---
## Fase 1: PESQUISA
1. Identificar as modalidades-alvo (visão/áudio/texto) e suas interdependências.
2. Analisar datasets específicos do domínio em busca de correlações cross-modais.
3. Revisar benchmarks multimodais existentes para checar consistência de padrão.
4. Mapear restrições técnicas (ex.: limites de resolução, taxas de amostragem).
5. Documentar casos de uso que exigem injeção simultânea de modalidades.
6. Avaliar templates de prompt anteriores quanto à adaptabilidade.

## Fase 2: COMPOSIÇÃO
1. Inicializar o schema com o array `modalities` (ref.: bld_schema_multimodal_prompt.md).
2. Definir parâmetros de `vision`: resolução, rótulos de objeto, relações espaciais.
3. Definir parâmetros de `audio`: duração, faixas de frequência, tags semânticas.
4. Definir parâmetros de `text`: idioma, sentimento, referências de entidade.
5. Alinhar modalidades via chaves `cross_ref` (ex.: `vision.id == audio.object_id`).
6. Estruturar o prompt usando a sintaxe `INJECT` (ref.: bld_output_template_multimodal_prompt.md).
7. Incorporar triplas de exemplo: `<modality>:<value>:<context>`.
8. Validar a conformidade do schema com as regras de validação de bld_schema_multimodal_prompt.md.
9. Finalizar com placeholders específicos de modalidade para injeção em runtime.

## Fase 3: VALIDAÇÃO
[ ] Todas as modalidades presentes no array `modalities`
[ ] Referências cross-modais resolvem de forma consistente
[ ] Restrições técnicas compatíveis com as capacidades do dataset
[ ] Triplas de exemplo alinhadas aos casos de uso do domínio
[ ] Saída em conformidade com a estrutura de bld_output_template_multimodal_prompt.md

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[multimodal-prompt-builder]] | related | 0.44 |
| [[bld_knowledge_multimodal_prompt]] | upstream | 0.39 |
| bld_instruction_multi_modal_config | sibling | 0.38 |
| bld_collaboration_multi_modal_config | downstream | 0.37 |
