---
kind: tools
id: bld_tools_multimodal_prompt
pillar: P04
llm_function: CALL
purpose: Ferramentas disponíveis para a produção de multimodal_prompt
quality: null
title: "Tools Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, tools]
tldr: "Ferramentas disponíveis para a produção de multimodal_prompt"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [construção de multimodal_prompt, tools multimodal prompt, multimodal_prompt, builder, tools, ferramentas de produção, ferramentas de validação, modelos de referência da indústria, gemini pro vision, haotian liu]
density_score: 0.85
related:
  - bld_tools_prompt_optimizer
  - bld_tools_visual_workflow
---
## Ferramentas de Produção
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_compile.py | Compila o artefato multimodal prompt para saída YAML | Após F6 PRODUCE |
| cex_score.py | Pontua o prompt segundo as 5 dimensões de qualidade | Após a geração inicial |
| cex_retriever.py | Recupera exemplos similares de multimodal prompt para o F3 INJECT | Durante a montagem de contexto |
| cex_doctor.py | Valida a completude do builder ISO e a conformidade do frontmatter | Durante o F7 GOVERN |

## Ferramentas de Validação
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_hooks.py | Validação pre-commit: checagem ASCII, frontmatter, schema | Antes do F8 COLLABORATE |
| cex_wave_validator.py | Valida os 12 ISOs do pacote do builder | Durante ciclos de auditoria |

## Modelos de Referência da Indústria
| Modelo | Papel no design de multimodal_prompt |
|-------|----------------------------------|
| GPT-4V (OpenAI) | Fusão imagem+texto, prompts de raciocínio espacial |
| Claude 3 vision (Anthropic) | Padrões de prompt para entendimento de gráficos/documentos |
| Gemini Pro Vision (Google) | Grounding cross-modal e conteúdo intercalado |
| LLaVA (Haotian Liu 2023) | Formato de prompt para ajuste de instrução visual |
| Florence-2 (Microsoft) | Arquitetura de prompt unificada imagem+texto |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_prompt_version]] | downstream | 0.38 |
| [[bld_orchestration_action_prompt]] | downstream | 0.35 |
| bld_tools_prompt_optimizer | sibling | 0.33 |
| bld_knowledge_card_prompt_optimizer | upstream | 0.29 |
| bld_tools_visual_workflow | sibling | 0.28 |
