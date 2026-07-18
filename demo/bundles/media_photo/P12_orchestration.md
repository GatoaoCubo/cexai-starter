---
kind: collaboration
id: bld_collaboration_multimodal_prompt
pillar: P12
llm_function: COLLABORATE
purpose: Como o multimodal_prompt-builder trabalha em crews com outros builders
quality: null
title: "Collaboration Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, collaboration]
tldr: "Como o multimodal_prompt-builder trabalha em crews com outros builders"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [construção de multimodal_prompt, collaboration multimodal prompt, multimodal_prompt, builder, collaboration, multi_modal_config, prompt_technique, papel na crew, recebe de, produz para]
density_score: 0.85
related:
  - multimodal-prompt-builder
  - bld_tools_multimodal_prompt
---
## Papel na Crew
Sintetiza prompts multimodais integrando entradas de texto, imagem e áudio em instruções coesas para modelos de IA. Atua como ponte entre criadores de conteúdo e equipes técnicas.

## Recebe De
| Builder             | O quê                              | Formato   |
|---------------------|-----------------------------------|----------|
| multi_modal_config  | Restrições e configurações de modalidade | YAML     |
| knowledge_card      | Contexto de domínio para grounding      | Markdown |
| embedding_config    | Especificações de token embedding    | YAML     |

## Produz Para
| Builder             | O quê                              | Formato   |
|---------------------|-----------------------------------|----------|
| prompt_template     | Estruturas de prompt multimodal      | Markdown |
| llm_judge           | Casos de teste para avaliação cross-modal   | Markdown |
| benchmark           | Cenários de avaliação com entradas  | Markdown |

## Fronteira
NÃO trata de configuração específica de modelo (tratada por `multi_modal_config`) nem de otimização de prompt somente-texto (tratada por `prompt_technique`).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_collaboration_llm_evaluation_scenario | sibling | 0.29 |
| [[multimodal-prompt-builder]] | upstream | 0.29 |
| [[bld_tools_multimodal_prompt]] | upstream | 0.27 |
| bld_collaboration_prompt_technique | sibling | 0.27 |
| bld_collaboration_self_improvement_loop | sibling | 0.25 |
