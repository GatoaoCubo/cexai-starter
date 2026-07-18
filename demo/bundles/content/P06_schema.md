---
kind: schema
id: bld_schema_knowledge_card
pillar: P06
llm_function: CONSTRAIN
purpose: "Schema formal do knowledge_card -- FONTE UNICA DA VERDADE"
pattern: "o TEMPLATE deriva disto. o CONFIG restringe isto. Nunca o inverso."
source: P01_knowledge/_schema.yaml v4.0 + validate_kc.py v2.0 + 721 KCs reais
quality: null
title: "Schema: knowledge_card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema for knowledge_card"
  - "single source of truth"
  - "knowledge card construction"
  - "schema knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "^p01_kc_[a-z][a-z0-9_]+$"
  - "— yaml: topic"
  - "scope"
  - "owner"
  - "criticality 2."
  - "— bullets >= 3"
  - "concrete examples 3."
density_score: 0.90
related:
  - bld_schema_golden_test
  - bld_schema_retriever_config
  - bld_schema_axiom
  - bld_schema_action_prompt
  - bld_schema_output_validator
---

# Schema: knowledge_card
## Campos de Frontmatter (Obrigatorios -- 14)
| Campo | Tipo | Obrigatorio | Padrao | Validador |
|-------|------|----------|---------|-----------|
| id | string (p01_kc_{slug}) | SIM | -- | H02, H03 |
| kind | literal "knowledge_card" | SIM | -- | H04 |
| pillar | literal "P01" | SIM | -- | H06 |
| title | string, 5-100 caracteres | SIM | -- | H06, S03 |
| version | semver X.Y.Z | SIM | "1.0.0" | H06, S04 |
| created | data AAAA-MM-DD | SIM | -- | H06, S05 |
| updated | data AAAA-MM-DD | SIM | -- | H06, S05 |
| author | string (nao pode ser o orchestrator) | SIM | -- | H06, H10 |
| domain | string | SIM | -- | H06 |
| quality | null | SIM | null | H05 |
| tags | list[string], 3-7 itens | SIM | -- | H07 |
| tldr | string, <= 160 caracteres, precisa conter dado concreto | SIM | -- | S01, S02 |
| when_to_use | string (contexto especifico, nunca "quando necessario") | SIM | -- | H06 |
| axioms | list[string], >= 1 item, forma SEMPRE/NUNCA/SE-ENTAO | SIM | -- | S18 |
## Campos de Frontmatter (Extensao CEX -- 5)
| Campo | Tipo | Obrigatorio | Validador |
|-------|------|----------|-----------|
| keywords | list[string], 2-5 itens (termos que o usuario digitaria literalmente) | REC | S16 |
| long_tails | list[string], 2-3 itens (frases completas em linguagem natural) | REC | S17 |
| linked_artifacts | objeto {primary, related} | REC | S14, S20 |
| density_score | float, 0.80-1.00 | REC | -- |
| data_source | URL ou referencia de artefato | REC | S15 |
## Padrao do ID
Regex: `^p01_kc_[a-z][a-z0-9_]+$`
Regra: o id DEVE ser igual ao stem do nome do arquivo (H02). Somente underscores.
## Convencoes de Nomenclatura (populacoes de nome de arquivo estruturalmente essenciais)
A Regex acima e o portao FORWARD, valido apenas para ids novos -- ela nao rege
retroativamente 6 populacoes ja provadas LOAD-BEARING (estruturalmente essenciais) ou
PATTERN-INADMISSIBLE (inadmissiveis ao padrao) por quebra real durante a varredura de
renomeacao R-307 lane-4 (o commit `af9552aaaf` reverteu 191/383 renomeacoes exatamente
por isso). O `identity_doctor` (`_tools/cex_check_registry.py`) carrega essas MESMAS 6
populacoes na constante `EXEMPT_ID_CONVENTIONS` (R-314): elas saem do total de
descompasso contado, mas continuam sempre visiveis via `exempted_by_convention`.
| Populacao | Contagem | Exemplo | Por que e isenta |
|---|---|---|---|
| `library/kind/kc_{kind}.md` (forma simples) | 156 | `kc_ab_test_config` | `load_kc_library()` faz glob de `kc_*.md` pelo nome do arquivo; ~14 modulos em _tools constroem esse caminho a partir do nome do kind |
| `kc_oss_*` | 26 | `kc_oss_ruff` | `license_doctor` faz glob de `kc_oss_*.md` |
| `kc_lens_*` | 8 | `kc_lens_bible` | o `LENS_DIR` de `cex_teach_lesson.py` constroi `kc_lens_{lens}.md` |
| `kc_*_vocabulary` | 6 | `kc_intelligence_vocabulary` | `cex_distill._carry_vocabulary_kcs()` faz glob por nucleo |
| `kc_competitor_hermes` | 1 | (nome exato) | `cex_hygiene.py` R09 tem esse nome de arquivo fixo no codigo |
| `kc_8f_*` (comeca com digito) | 5 | `kc_8f_mode_a` | PATTERN-INADMISSIBLE: o H02 exige `[a-z]` logo apos o prefixo; "8f" comeca com digito -- nenhuma renomeacao pode admitir isso |
Nenhuma das 6 populacoes e "corrigida" retroativamente aqui -- isso espelha o precedente
do proprio `bld_schema_output_template.md`, "resolvido mas nao abencoado" (R-299). Todo
novo id de knowledge_card ainda deve ser autorado contra a Regex acima; esta e uma lista
de excecao fechada e citada, nao um precedente para novo desvio.
## Objeto linked_artifacts
```yaml
linked_artifacts:
  primary: null            # ou artifact_id
  related: [p01_kc_xxx]   # lista de ids relacionados
```
As chaves `primary` e `related` sao ambas obrigatorias (S20).
## Estrutura do Corpo: domain_kc
1. `## Referencia Rapida` -- yaml: topic, scope, owner, criticality
2. `## Conceitos-Chave` -- bullets >= 3, exemplos concretos
3. `## Fases da Estrategia` -- passos numerados com resultados
4. `## Regras de Ouro` -- regras acionaveis >= 3
5. `## Fluxo` -- diagrama de texto/ascii
6. `## Comparativo` -- tabela comparativa
7. `## Referencias` -- referencias de artefato + URLs
## Estrutura do Corpo: meta_kc
1. `## Resumo Executivo` -- visao geral densa (2-3 frases)
2. `## Tabela de Especificacao` -- especificacoes chave-valor
3. `## Padroes` -- o que funciona
4. `## Anti-Padroes` -- o que falha
5. `## Aplicacao` -- como aplicar
6. `## Referencias` -- referencias de artefato + URLs
Hierarquia de densidade (do que mais informa por token ao que menos informa): tabelas > blocos de codigo > listas de bullets > diagramas ASCII > paragrafos curtos.
## Restricoes
- max_bytes: 5120 (corpo) -- H08. Cobre mais de 97% dos 721 KCs reais (p95=4274B)
- min_bytes: 200 -- KCs abaixo de 200B sao vazios/esboco
- min_bullets: 3
- density_min: 0.80
- bullet_max_chars: 80 -- S10
- naming: p01_kc_{topic_slug}.md
- sem caminhos internos (records/, .claude/, /home/) -- H09
- sem frases de enchimento -- S09
- sem auto-referencia no tldr -- S02

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_schema_golden_test]] | sibling | 0.55 |
| [[bld_schema_retriever_config]] | sibling | 0.54 |
| [[bld_schema_axiom]] | sibling | 0.54 |
| [[bld_schema_action_prompt]] | sibling | 0.53 |
| [[bld_schema_output_validator]] | sibling | 0.53 |
