---
kind: schema
id: bld_schema_knowledge_card
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal para knowledge_card -- FONTE ÚNICA DA VERDADE
pattern: O TEMPLATE deriva disto. O CONFIG restringe isto. Nunca o inverso.
source: P01_knowledge/_schema.yaml v4.0 + validate_kc.py v2.0 + 721 KCs reais
quality: null
title: "Schema Knowledge Card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Exemplos ideais e anti-exemplos para a construção de knowledge_card, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de knowledge_card"
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
## Campos de Frontmatter (Obrigatórios -- 14)
| Campo | Tipo | Obrigatório | Padrão | Validador |
|-------|------|----------|---------|-----------|
| id | string (p01_kc_{slug}) | SIM | -- | H02, H03 |
| kind | literal "knowledge_card" | SIM | -- | H04 |
| pillar | literal "P01" | SIM | -- | H06 |
| title | string 5-100 caracteres | SIM | -- | H06, S03 |
| version | semver X.Y.Z | SIM | "1.0.0" | H06, S04 |
| created | date YYYY-MM-DD | SIM | -- | H06, S05 |
| updated | date YYYY-MM-DD | SIM | -- | H06, S05 |
| author | string (não o orchestrator) | SIM | -- | H06, H10 |
| domain | string | SIM | -- | H06 |
| quality | null | SIM | null | H05 |
| tags | list[string], len 3-7 | SIM | -- | H07 |
| tldr | string <= 160 caracteres, deve conter dado concreto | SIM | -- | S01, S02 |
| when_to_use | string (contexto específico, não "quando necessário") | SIM | -- | H06 |
| axioms | list[string], len >= 1, forma SEMPRE/NUNCA/SE-ENTÃO | SIM | -- | S18 |
## Campos de Frontmatter (Estendidos do CEX -- 5)
| Campo | Tipo | Obrigatório | Validador |
|-------|------|----------|-----------|
| keywords | list[string], len 2-5 (termos que o usuário literalmente digitaria) | REC | S16 |
| long_tails | list[string], len 2-3 (frases completas em linguagem natural) | REC | S17 |
| linked_artifacts | object {primary, related} | REC | S14, S20 |
| density_score | float 0.80-1.00 | REC | -- |
| data_source | URL ou referência de artefato | REC | S15 |
## Padrão de ID
Regex: `^p01_kc_[a-z][a-z0-9_]+$`
Regra: id DEVE ser igual ao stem do nome do arquivo (H02). Somente underscores.
## Convenções de Nomenclatura (populações de nome de arquivo estruturalmente críticas)
O Regex acima é o gate FORWARD para ids novos -- ele não rege retroativamente as 6 populações
provadas ESTRUTURALMENTE CRÍTICAS ou PATTERN-INADMISSIBLE por quebra real durante o rename sweep
da lane-4 do R-307 (af9552aaaf reverteu 191/383 renomeações exatamente por isso). O `identity_doctor`
(`_tools/cex_check_registry.py`) carrega essas MESMAS 6 na sua constante `EXEMPT_ID_CONVENTIONS`
(R-314): removidas do total de mismatches contados, mas sempre visíveis via `exempted_by_convention`.
| População | Contagem | Exemplo | Por quê é isento |
|---|---|---|---|
| `library/kind/kc_{kind}.md` (sem prefixo) | 156 | `kc_ab_test_config` | `load_kc_library()` faz glob de `kc_*.md` pelo nome do arquivo; ~14 módulos em _tools constroem esse caminho a partir do nome do kind |
| `kc_oss_*` | 26 | `kc_oss_ruff` | `license_doctor` faz glob de `kc_oss_*.md` |
| `kc_lens_*` | 8 | `kc_lens_bible` | `cex_teach_lesson.py` LENS_DIR constrói `kc_lens_{lens}.md` |
| `kc_*_vocabulary` | 6 | `kc_intelligence_vocabulary` | `cex_distill._carry_vocabulary_kcs()` faz glob por núcleo |
| `kc_competitor_hermes` | 1 | (nome exato) | `cex_hygiene.py` R09 fixa esse nome de arquivo diretamente no código |
| `kc_8f_*` (começa com dígito) | 5 | `kc_8f_mode_a` | PATTERN-INADMISSIBLE: H02 exige `[a-z]` depois do prefixo; "8f" começa com dígito -- nenhuma renomeação pode jamais admitir isso |
Nenhuma das 6 é "corrigida" retroativamente aqui -- espelha o precedente "resolved not blessed" do
próprio `bld_schema_output_template.md` (R-299). Novos ids de knowledge_card ainda devem ser
autorados contra o Regex acima; esta é uma lista de exceção fechada e citada, não um precedente
para novo desvio.
## Objeto Linked Artifacts
```yaml
linked_artifacts:
  primary: null            # or artifact_id
  related: [p01_kc_xxx]   # list of related ids
```
As chaves `primary` e `related` são ambas obrigatórias (S20).
## Estrutura de Corpo: domain_kc
1. `## Referência Rápida` -- yaml: topic, scope, owner, criticality
2. `## Conceitos-Chave` -- bullets >= 3, exemplos concretos
3. `## Fases da Estratégia` -- passos numerados com resultados
4. `## Regras de Ouro` -- regras acionáveis >= 3
5. `## Fluxo` -- diagrama em texto/ascii
6. `## Comparativo` -- tabela comparativa
7. `## Referências` -- referências de artefato + URLs
## Estrutura de Corpo: meta_kc
1. `## Resumo Executivo` -- visão geral densa (2-3 frases)
2. `## Tabela de Especificações` -- especificações chave-valor
3. `## Padrões` -- o que funciona
4. `## Antipadrões` -- o que falha
5. `## Aplicação` -- como aplicar
6. `## Referências` -- referências de artefato + URLs
Hierarquia de densidade (do mais para o menos informativo por token): tabelas > blocos de código > listas de bullets > diagramas ASCII > parágrafos curtos.
## Restrições
- max_bytes: 5120 (corpo) -- H08. Cobre 97%+ dos 721 KCs reais (p95=4274B)
- min_bytes: 200 -- KCs abaixo de 200B são vazios/stub
- min_bullets: 3
- density_min: 0.80
- bullet_max_chars: 80 -- S10
- naming: p01_kc_{topic_slug}.md
- sem caminhos internos (records/, .claude/, /home/) -- H09
- sem frases de enchimento -- S09
- sem autorreferências no tldr -- S02

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_golden_test]] | irmão | 0.55 |
| [[bld_schema_retriever_config]] | irmão | 0.54 |
| [[bld_schema_axiom]] | irmão | 0.54 |
| [[bld_schema_action_prompt]] | irmão | 0.53 |
| [[bld_schema_output_validator]] | irmão | 0.53 |
