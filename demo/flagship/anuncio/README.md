# Anuncio (Codexa v2)

> Gerador de anuncios de marketplace BR (Mercado Livre, Shopee, Amazon BR, Magalu) -- pronto para Custom GPT, ChatGPT Projects, Claude Projects e Gemini Gems.

**Powered by CEXAI architecture** (300+ kinds, 12 pillars, 8 nuclei) -- github.com/GatoaoCubo/cex

## O que este bundle gera
Para cada produto do usuario:
- **3 titulos** otimizados (ML 58-60 chars sem conectores; Shopee 100-120 com 1-2 emojis; Amazon 150-200 marca-primeiro; Magalu 30-150).
- **Descricao mobile-first** em 6 folds (>= 5000 chars em ML, texto puro em Shopee, A+ em Amazon).
- **2 blocos de keywords** (115-120 cada em ML; cada keyword < 60 chars; overlap <= 15%).
- **10 bullets** com origem rastreavel (feature/pain_point/gap/spec); cada um 250-299 chars em ML; Amazon usa **5** bullets.
- **5-7 FAQs** assertivas (sem hedge tipo "depende").
- **Ficha tecnica** so com dados reais do input.
- **Self-check 5D** (titulo / keywords / descricao / bullets / factual) com gate >= 8.0; retry max 2.
- **Bloco "Suposicoes e dados a confirmar"** em toda entrega.

## Estrutura do bundle

```
anuncio/
  00_instructions.md                # Custom GPT instructions (<=8000 chars)
  manifest.yaml                     # contrato completo (architecture: cexai_12p_v1)
  CONVENTION.md                     # convencao fractal CoC (12 pilares + 3 universal rules)
  CONVENTION_CEXAI_DELTA.md         # o que CEXAI adiciona sobre a CONVENTION
  README.md                         # voce esta aqui
  knowledge/                        # 12 P files (FULL Custom GPT upload)
    P01_knowledge.md ... P12_orchestration.md
  cexai/                            # 32 typed CEXAI artifacts (SOURCE OF TRUTH)
    personality, agent_card, role_assignments x3, prompt_templates x6,
    scoring_rubric, llm_judge, guardrail, content_filter, revision_loop_policy,
    input_schema, validation_schema, response_format, workflow, crew_template,
    team_charter, mcp_server, search_tool, entity_memory, working_memory,
    enum_defs x2, env_config, decision_record, diagram, few_shot_example
  projects_free/                    # 5 ENXUTO files (ChatGPT Projects free tier)
    00_instructions.md + P01..P05
  claude/                           # Claude Projects variant
    Project_instructions.md + knowledge/ tree + cexai_crew_setup.md + .mcp.json
  gemini/                           # Gemini Gems variant
    Gem_instructions.md + retrieval/ tree
  SETUP_pt-br.md                    # setup Custom GPT detalhado
  SETUP_chatgpt_projects.md         # setup ENXUTO no Projects free
  SETUP_claude_projects.md          # setup Claude Projects + opcional MCP
  SETUP_gemini_gems.md              # setup Gemini Gems
```

## Quick start por runtime

| Plataforma | Setup file | Tempo |
|------------|------------|-------|
| Custom GPT (ChatGPT Plus) | [SETUP_pt-br.md](SETUP_pt-br.md) | ~5 min |
| ChatGPT Projects (free) | [SETUP_chatgpt_projects.md](SETUP_chatgpt_projects.md) | ~3 min |
| Claude Projects | [SETUP_claude_projects.md](SETUP_claude_projects.md) | ~7 min (com MCP opcional) |
| Gemini Gems | [SETUP_gemini_gems.md](SETUP_gemini_gems.md) | ~5 min |

## O que e diferente da v1 (codexa-gpt-bundles original)

1. **Satellite names dropados.** Nao tem mais nome-satelite pre-v2 -- agora e simplesmente "anuncio" agent (decisao do founder 2026-05-30).
2. **Subpasta `cexai/`** com 32 contratos tipados que substituem prosa por kind YAML+markdown auditavel. A camada original (12 P) preservada como REFERENCIA narrativa.
3. **Crew composable** (writer + critic + compliance) -- 3 papeis IN-PROMPT no Custom GPT, dispatchavel no Claude/Gemini.
4. **4 runtimes paralelos** com paridade de identidade, regras e fidelity claims.
5. **Upgrade lanes** (MCP firecrawl, search providers, LLM judge council) opcionais -- nunca quebram Custom GPT.

Detalhes em [CONVENTION_CEXAI_DELTA.md](CONVENTION_CEXAI_DELTA.md).

## Compliance & anti-fabricacao

3 regras universais embedded em TODOS os runtimes:
1. **Anti-alucinacao 7-point** -- fonte de verdade = input; proibido fabricar specs/claims; lacuna -> pergunte OU marque `[PREENCHER]`; toda entrega traz bloco "Suposicoes e dados a confirmar".
2. **Paste-intake** -- URLs de marketplace NAO sao acessiveis (anti-bot/JS); usuario cola o conteudo.
3. **Code-block output** -- conteudo-produto SEMPRE em ```, 4 blocos (titulo / descricao / keywords / bullets); meta fora dos blocos.

## Verificacao rapida (smoke test)
Peca ao agente em qualquer runtime:
> "Gere um anuncio de Mercado Livre para garrafa termica inox 1L, categoria Casa > Cozinha > Garrafas, preco R$ 89,90, diferenciais: 12h gelado, a prova de vazamento."

Confira na resposta:
- [ ] 3 titulos, cada um com 58-60 chars, sem conectores (de/para/com/e).
- [ ] Descricao 6 folds sem rotulos visiveis (HEROI/GUIA/CTA), sem R$.
- [ ] 10 bullets etiquetados por origem (FEATURE/PAIN_POINT/GAP/SPEC), cada 250-299 chars.
- [ ] 2 blocos de keywords com 115-120 termos cada.
- [ ] Tabela 5D + status APROVADO/REVISAR.
- [ ] Bloco "## Suposicoes e dados a confirmar" presente.

## Credit
**Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei).**
Bundle group: codexa-v2 (lineage from codexa, 2026 originals).
Re-authored by N03 (Inventive Pride) on 2026-05-30 from CODEXA_V2 mission.
