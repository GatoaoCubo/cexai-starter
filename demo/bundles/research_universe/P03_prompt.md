---
kind: instruction
id: bld_instruction_research_universe
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para research_universe
quality: null
title: "Instruction Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, instruction]
tldr: "Processo de produção passo a passo para research_universe -- 3 fases, 6 trilhas"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F6_produce"
keywords: [processo de produção, research_universe, instruction research universe, builder, instruction, fase pesquisa, fase composição, fase validação, semente, trilhas]
density_score: 0.88
related:
  - research-universe-builder
---
## Fase 1: INTAKE + CLASSIFICAÇÃO DA SEMENTE
1. Peça a semente (obrigatório): produto, marca, CNPJ, empresa, palavra-chave ou `store:id`. Sem semente, não há pesquisa.
2. Classifique o `seed_type`: `produto`, `marca`, `cnpj`, `empresa`, `palavra_chave` ou `store_id`.
3. Decida, por tipo de semente, quais das 6 trilhas se aplicam (ver P06_schema.md, tabela "Semente x Trilhas Aplicáveis") -- uma semente do tipo `palavra_chave` normalmente pula firmografia; uma semente do tipo `cnpj`/`empresa` normalmente aplica todas as 6.
4. Confirme com o usuário quais trilhas ele quer priorizar, se o pedido não especificar (ex.: "só reputação e sentimento" é um recorte legítimo).
5. Pergunte que dado o usuário já tem em mãos (print de app store, página do Reclame Aqui, resultado de consulta de CNPJ) -- isso evita depender só de busca nativa.

## Fase 2: COLETA + COMPOSIÇÃO POR TRILHA
1. **Firmografia**: se há CNPJ ou razão social, estruture razão social, CNAE (setor), porte, situação cadastral, município/UF. Sem CNPJ localizável -> trilha `skipped`.
2. **Sinal social**: procure avaliação média e volume de reviews na loja de app relevante, menções em Reddit, menções em YouTube. Cada fonte sem acesso vira `blocked`, não `skipped`.
3. **Reputação**: procure o índice público do Reclame Aqui (nota, % respondidas, % resolvidas). Sem página localizável para a empresa -> `skipped` (não existe) vs `blocked` (existe, mas o acesso falhou) -- distinga sempre.
4. **Sentimento em PT**: classifique positivo/neutro/negativo APENAS sobre o texto já coletado nas trilhas 2 e 3. Sem texto coletado -> trilha `skipped`, nunca uma impressão vaga.
5. **SEO**: gere termos de busca relacionados a semente com intenção (informacional/transacional/navegacional); use busca nativa (se disponível) para validar volume aproximado; sem validação -> rotule como estimativa.
6. **Perguntas multi-perspectiva**: gere no mínimo 3 perguntas, cada uma de um papel distinto -- cliente, concorrente, investidor/regulador, parceiro -- específicas a semente, nunca genéricas.
7. Preencha o `OUTPUT_TEMPLATE.md` (P05) na ordem: Sumário -> 6 trilhas -> Tabela de Status -> Procedência Consolidada -> Limitações.
8. Alinhe cada campo ao SCHEMA.md (P06) -- nomes de campo exatos, enum de status exato (`ok`/`blocked`/`skipped`).

## Fase 3: VALIDAÇÃO
- [ ] As 6 trilhas aparecem na tabela final, cada uma com status explícito.
- [ ] Toda trilha `ok` cita fonte + data de acesso.
- [ ] Nenhum número (CNPJ, índice de reputação, volume de busca) aparece sem fonte -- caso contrário, a trilha deveria ser `blocked`.
- [ ] Sentimento em PT só aparece se há texto-fonte citado.
- [ ] Perguntas multi-perspectiva cobrem >= 3 papéis distintos.
- [ ] `coverage_score` (fração de trilhas `ok`) bate com a contagem real da tabela de status.
- [ ] Se `coverage_score` < 0.5: destaque isso na síntese executiva -- não venda o relatório como completo.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[research-universe-builder]] | upstream | 0.40 |
| [[bld_output_template_research_universe]] | downstream | 0.36 |
| [[bld_schema_research_universe]] | sibling | 0.33 |
| [[bld_tools_research_universe]] | sibling | 0.27 |
