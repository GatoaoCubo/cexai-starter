---
kind: tools
id: bld_tools_research_universe
pillar: P04
llm_function: CALL
purpose: Ferramentas e fontes disponíveis para produção de research_universe
quality: null
title: "Tools Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, tools]
tldr: "6 trilhas de coleta pública + ferramentas CEX de validação interna -- este pacote público não usa Actions nem chaves de API"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F5_call"
keywords: [ferramentas research_universe, fontes públicas, cnpj, ibge, reclame aqui, app store, reddit, youtube, seo, tools research universe, builder]
density_score: 0.88
related:
  - bld_tools_competitive_matrix
  - bld_tools_knowledge_card
---
## Como este pacote coleta dado (sem Actions, sem chaves de API)
O `customgpt_instructions.json` deste bundle declara `web_browsing: false`,
`code_interpreter: false`, `dalle: false` -- este é um pacote **100%
Knowledge + Instructions**, sem Actions externas. A coleta real de dado por
trilha acontece de duas formas, e o agente é sempre transparente sobre qual
delas usou:
1. **Você cola o dado na conversa** (print de app store, texto da página do
   Reclame Aqui, resultado de consulta de CNPJ, resultado de busca). Caminho
   padrão, funciona em qualquer runtime, sempre disponível.
2. **Busca/navegação nativa do runtime**, quando habilitada (Web Browsing no
   ChatGPT, Search extension no Gemini). Best-effort; fontes com proteção
   anti-bot ou exigência de login podem falhar -- nesse caso a trilha correspondente
   fica `blocked`, e o agente pede para você colar o dado manualmente.

## Trilhas de Coleta (fonte pública de referência por trilha)
| Trilha | Fonte pública de referência | Dado típico | Status quando indisponível |
|--------|------------------------------|-------------|------------------------------|
| Firmografia | Consulta pública de CNPJ (Receita Federal) + tabela CNAE (IBGE) | Razão social, CNAE, porte, situação cadastral, município/UF | `skipped` se não há CNPJ/empresa identificável; `blocked` se a consulta existe mas falhou |
| Sinal social | Google Play / App Store (página do app), Reddit (busca por marca/produto), YouTube (busca de vídeo + comentários) | Nota média, volume de reviews, menções, tom geral | `blocked` por fonte individual que não respondeu; `skipped` se a semente não tem presença nessas plataformas |
| Reputação | Reclame Aqui (página pública da empresa) | Índice RA, % respondidas, % resolvidas, nota do consumidor | `skipped` se a empresa não tem página no Reclame Aqui; `blocked` se a página existe mas não foi acessada |
| Sentimento em PT | Texto já coletado nas trilhas Sinal Social e Reputação (não é fonte própria) | Positivo / neutro / negativo + temas recorrentes | `skipped` se nenhuma das duas trilhas-fonte tem texto coletado |
| Palavras-chave de SEO | Autocomplete e "pesquisas relacionadas" do Google, Google Trends | Termos, intenção (informacional/transacional/navegacional), tendência | `blocked` se a busca nativa não está disponível neste runtime; caso raro `skipped` se a semente é um CNPJ sem termo de busca associado |
| Perguntas multi-perspectiva | Nenhuma -- síntese do próprio agente sobre as trilhas anteriores | >= 3 perguntas, uma por papel (cliente, concorrente, investidor/regulador, parceiro) | Nunca `blocked`/`skipped` por falta de fonte externa -- só fica incompleta se as demais trilhas vieram vazias |

## Ferramentas de Produção (validação interna CEX do artefato)
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_compile.py | Compila o artefato .md para o sidecar .yaml | Após a escrita |
| cex_score.py | Pontua o relatório contra as dimensões do gate de qualidade (P07) | Antes da publicação |
| cex_retriever.py | Encontra relatórios `research_universe` existentes para a mesma semente | Durante a fase de intake, para evitar duplicidade |
| cex_doctor.py | Valida frontmatter, padrão de ID e conformidade de kind | Antes da publicação |

## Referências Externas (metodologia, não endpoint)
- Receita Federal do Brasil -- consulta pública de CNPJ (situação cadastral, razão social).
- IBGE -- CNAE (Classificação Nacional de Atividades Econômicas).
- Reclame Aqui -- metodologia de índice de reputação de consumidor no Brasil.
- Google Play / Apple App Store -- sistemas de avaliação e review de aplicativos.
- Google Keyword Planner / Google Trends -- metodologia de keyword research e sinal de tendência.
- Modelo de mapeamento por stakeholder (cliente / concorrente / investidor-regulador / parceiro) para geração de perguntas multi-perspectiva.

## Permissões de Ferramenta (para este pacote público)
| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Web Browsing nativo do runtime (se disponível), leitura do que o usuário colar na conversa | Uso opcional, best-effort |
| NÃO INCLUIDO neste pacote | Actions/API keys (firecrawl, CNPJ API paga, SERP API) | Fora do escopo do export público -- ver `README.md` |
| VALIDAÇÃO (uso do autor do artefato, não do runtime do comprador) | cex_compile.py, cex_score.py, cex_retriever.py, cex_doctor.py | Ferramentas internas CEX, não exportadas neste bundle |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_research_universe]] | sibling | 0.45 |
| [[bld_knowledge_card_research_universe]] | upstream | 0.40 |
| bld_tools_competitive_matrix | sibling | 0.30 |
| bld_tools_knowledge_card | sibling | 0.27 |
