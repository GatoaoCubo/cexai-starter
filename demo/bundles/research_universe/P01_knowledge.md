---
kind: knowledge_card
id: bld_knowledge_card_research_universe
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para produção de research_universe -- pesquisa multi-fonte a partir de UMA semente
quality: null
title: "Knowledge Card Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, knowledge_card]
tldr: "6 trilhas (firmografia, sinal social, reputação, sentimento PT, SEO, perguntas multi-perspectiva) fundidas em um relatório único com status honesto por trilha"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F3_inject"
keywords: [research_universe, firmografia, cnpj, ibge, sinal social, reclame aqui, sentimento pt, seo, perguntas multi-perspectiva, trilha, procedência]
density_score: 0.88
related:
  - research-universe-builder
  - bld_schema_research_universe
  - bld_tools_research_universe
---
## Visão Geral do Domínio
`research_universe` (nucleus N01 . pillar P01 . verb `analyze`) é a capacidade CEXAI que recebe UMA semente -- um produto, uma marca, um CNPJ, uma empresa, uma palavra-chave, ou um `store:id` -- e a executa através de 6 trilhas de pesquisa independentes, devolvendo UM relatório unificado multi-fonte. A diferença central em relação a uma busca genérica é o **status honesto por trilha**: cada uma das 6 trilhas reporta `ok` (dado real coletado), `blocked` (fonte existe mas não foi acessível neste ambiente) ou `skipped` (trilha não se aplica a este tipo de semente), nunca preenchendo uma lacuna com um número inventado. Toda alegação carrega procedência (fonte + data de acesso).

Isso posiciona `research_universe` como um agregador de OSINT (open-source intelligence) de negócios brasileiros: ele não substitui uma fonte primária, ele **consolida** o que várias fontes públicas dizem sobre a mesma semente em um único artefato rastreável.

## Conceitos-Chave
| Conceito | Definição | Fonte/Nota |
|---------|-----------|--------|
| Semente (seed) | O ponto de entrada único da pesquisa: produto, marca, CNPJ, empresa, palavra-chave ou `store:id` | Determina quais das 6 trilhas se aplicam |
| Firmografia | Dados registrais de uma pessoa jurídica: razão social, CNAE, porte, situação cadastral | Receita Federal (CNPJ) + IBGE (CNAE) |
| CNAE | Classificação Nacional de Atividades Econômicas -- o "setor" oficial de uma empresa no Brasil | Metodologia IBGE |
| Sinal social | Menções e avaliações em plataformas públicas: loja de apps, Reddit, YouTube | Proxy de percepção pública, não pesquisa fechada |
| Reputação | Índice público de atendimento ao consumidor (Reclame Aqui): % respondida, % resolvida, nota | Metodologia Reclame Aqui |
| Sentimento em PT | Classificação positivo/neutro/negativo aplicada sobre o TEXTO já coletado nas trilhas 2 e 3 | Não é uma fonte própria -- é uma análise derivada |
| Palavra-chave de SEO | Termo de busca relevante para a semente, com intenção (informacional/transacional/navegacional) | Metodologia de keyword research |
| Pergunta multi-perspectiva | Pergunta gerada a partir de UM stakeholder específico (cliente, concorrente, investidor, regulador) sobre a semente | Não depende de fonte externa -- é síntese do agente |
| Status honesto por trilha | Classificação `ok` / `blocked` / `skipped` que cada trilha reporta sobre si mesma | Mecanismo anti-alucinação central do kind |
| Procedência (provenance) | Registro de origem + data de acesso para cada dado individual, não apenas por trilha | Obrigatório em toda trilha `ok` |
| Cobertura (coverage_score) | Fração das 6 trilhas que fecharam com status `ok` | Métrica de completude do relatório, não de qualidade |

## Padrões da Indústria
- OSINT (Open-Source Intelligence) -- coleta e correlação de dados publicamente disponíveis, disciplina de origem militar/jornalística adaptada a due diligence de negócios.
- Firmographic data (padrão Dun & Bradstreet / Serasa Experian) -- perfil de empresa por porte, setor, situação cadastral, tempo de mercado.
- Social listening (padrão Brandwatch / Sprinklr) -- monitoramento de menções e sentimento em canais públicos.
- Reputation scoring público (Reclame Aqui no Brasil; equivalente a Trustpilot/BBB em outros mercados).
- Keyword research (padrão Google Keyword Planner / Ubersuggest) -- volume, dificuldade e intenção de busca.
- Stakeholder question mapping -- técnica de múltiplas lentes (cliente, concorrente, regulador, investidor) usada em pre-mortems e discovery de produto.

## Padrões Comuns
1. Classificar a semente primeiro: identificar se é produto, marca, CNPJ, empresa, palavra-chave ou `store:id` antes de decidir quais trilhas se aplicam.
2. Rodar as 6 trilhas de forma independente -- a falha ou ausência de uma trilha NUNCA bloqueia as demais.
3. Toda trilha fechada como `ok` carrega pelo menos 1 fonte com data de acesso em `provenance`.
4. Sentimento em PT é derivado do texto já coletado (trilhas sinal social e reputação) -- nunca é uma trilha isolada com fonte própria.
5. Perguntas multi-perspectiva cobrem no mínimo 3 papéis distintos (ex.: cliente, concorrente, regulador) -- uma única pergunta genérica não conta.
6. O relatório final sempre inclui uma tabela de status por trilha (`ok`/`blocked`/`skipped`) antes da síntese executiva.

## Armadilhas
| Armadilha | Por que falha |
|-----------|---------------|
| Inventar um número de CNPJ, índice de reputação ou volume de busca sem fonte | Viola o gate anti-alucinação (H06); a trilha deveria ser `blocked`, não preenchida |
| Confundir `blocked` com `skipped` | `blocked` = a fonte existe mas não foi acessível agora; `skipped` = a trilha não se aplica a esta semente. São causas diferentes e pedem ações diferentes do usuário |
| Sentimento sem texto-fonte | Sentimento em PT só pode ser classificado sobre texto real coletado -- nunca "no geral parece positivo" sem citar de onde veio o texto |
| Perguntas multi-perspectiva genéricas | "O que os clientes acham?" não é uma pergunta multi-perspectiva -- precisa ser específica ao papel e a semente |
| Dado de reputação sem data | Índice do Reclame Aqui muda; toda leitura de reputação carrega data de acesso, sinalizada como potencialmente desatualizada após ~90 dias |
| Tratar `research_universe` como scraper ao vivo | Este agente, quando exportado como pacote público (ChatGPT/Claude/Gemini), não tem Actions nem chaves de API -- ele estrutura o que o usuário cola ou o que a busca nativa do runtime encontra |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[research-universe-builder]] | upstream | 0.44 |
| [[bld_schema_research_universe]] | downstream | 0.39 |
| [[bld_tools_research_universe]] | sibling | 0.35 |
| competitive_matrix (bundle `competitor_benchmark`) | sibling | 0.28 |
| opportunity_matrix (bundle `sourcing_opportunity`) | sibling | 0.24 |
