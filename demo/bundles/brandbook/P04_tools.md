---
id: bld_tools_brandbook
kind: toolkit
pillar: P04
builder: brandbook-builder
version: 1.0.0
quality: null
title: Tools -- brandbook
author: n06_commercial
tags: [toolkit, brandbook, P04]
llm_function: CALL
created: 2026-06-22
updated: 2026-06-22
related:
  - bld_schema_brandbook
  - bld_prompt_brandbook
  - ap01_starter_roteiro
  - agent_card_n02
  - p01_kc_tool_ecosystem_audit
  - bld_tools_personality
  - agent_card_n06
  - shokunin_second_house_2026_07_03
  - p02_agent_builder_nucleus
  - p01_dv_vocabulario_venda_pme
---

## Ferramentas Disponíveis para o brandbook-builder

### Do N06 (infraestrutura de marca)
| Ferramenta | Finalidade |
|------------|------------|
| `brand_audit.py` | Pontua a consistência de marca em 6 dimensões |
| `brand_ingest.py` | Varre a pasta bagunçada do usuário -> extrai sinais de marca |
| `brand_inject.py` | Substitui tokens `{{BRAND_*}}` nos templates |
| `brand_propagate.py` | Propaga o contexto de marca para os 7 núcleos |
| `brand_validate.py` | Valida o brand_config.yaml (13 campos obrigatórios) |

### Do Sistema
| Ferramenta | Finalidade |
|------------|------------|
| `cex_compile.py` | Compila .md para .yaml |
| `cex_doctor.py` | Checagem do gate de qualidade |
| `cex_crew.py run brand_discovery` | Dispara a crew de marca de 3 papéis |

### MCP (pré-compilado pelo N07 via preflight)
| MCP | Finalidade |
|-----|------------|
| `fetch` | Faz scraping da URL do site da marca em busca de materiais |
| `markitdown` | Converte PDF/documento de marca para markdown |
| `canva` | Exporta assets visuais de marca |

### Pipeline de Mídia (dual-output)
| Hook | Finalidade |
|------|------------|
| `media_requests(inputs)` | Declara os slots de logotipo + paleta + imagem de capa |
| `produced_media(inputs)` | Mapeia o data-uri do logotipo enviado para o slot logo_primary |

### Nota de Portabilidade (bundle exportado)
As tabelas acima descrevem as ferramentas do CEXAI **interno** (o repositório
completo) que constroem e mantêm a capacidade brandbook. O agente standalone
deste bundle (rodando em ChatGPT / Claude / Gemini) **não** tem acesso a
nenhuma delas -- não há chamada MCP a `fetch` / `markitdown` / `canva`, não há
`brand_propagate.py` cross-nucleus, não há a crew de 3 papéis. O que o agente
exportado TEM: a lógica completa de geração das 8 seções + a regra
Nunca-Fabricar + o schema de entrada -- suficiente para produzir o manual de
marca em uma única conversa. Se você colar uma URL como material de marca, o
agente dependerá da navegação web nativa da plataforma escolhida (se
habilitada) para lê-la; caso contrário, cole o texto ou a paleta manualmente.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_brandbook]] | downstream | 0.23 |
| [[bld_prompt_brandbook]] | upstream | 0.19 |
| [[ap01_starter_roteiro]] | downstream | 0.18 |
| [[agent_card_n02]] | downstream | 0.18 |
| [[p01_kc_tool_ecosystem_audit]] | upstream | 0.18 |
| [[bld_tools_personality]] | related | 0.17 |
| [[agent_card_n06]] | upstream | 0.17 |
| [[shokunin_second_house_2026_07_03]] | downstream | 0.16 |
| [[p02_agent_builder_nucleus]] | upstream | 0.16 |
| [[p01_dv_vocabulario_venda_pme]] | upstream | 0.16 |
