---
kind: quality_gate
id: p11_qg_opportunity_matrix
pillar: P11
llm_function: GOVERN
purpose: Gate de qualidade com pontuação HARD e SOFT para opportunity_matrix
quality: null
title: "Gate -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, quality_gate]
tldr: "Gate de qualidade com pontuação HARD e SOFT para opportunity_matrix"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F7_govern"
keywords: [construção de opportunity_matrix, gate de qualidade opportunity matrix, opportunity_matrix, builder, quality_gate, sourcing_confiavel, honest-null, exemplo golden, anti-exemplo, gates hard]
density_score: 0.85
related:
  - opportunity-matrix-builder
---
## Gate de Qualidade

## Definição
| métrica | limiar | operador | escopo |
|--------|-----------|----------|-------|
| Fidelidade da forma de seção | 8/8 | == | vs MOLD_SOURCING_OPPORTUNITY |
| Drift de célula de tabela | 0 | == | toda linha de tabela vs a contagem de colunas |

## Gates HARD
| ID | Verificação | Condição de Falha |
|----|-------|-----------------|
| H01 | Frontmatter YAML válido | Frontmatter ausente ou inválido |
| H02 | ID casa com o padrão | ID não casa com ^p11_om_[a-z][a-z0-9_]+$ |
| H03 | Campo kind casa com 'opportunity_matrix' | Campo kind inválido |
| H04 | As 8 seções presentes, ordem congelada | Seção ausente/reordenada/renomeada vs MOLD_SOURCING_OPPORTUNITY |
| H05 | Colunas de tabela casam com os conjuntos congelados | Divergência em Matriz (9 cols) / Leitura (5) / Verificacao (5) / Match (4) |
| H06 | Gate nomeado presente | Seção 8 sem `sourcing_confiavel` + suas condições |
| H07 | Nenhum dado de mercado fabricado | Um preço de venda/nível de demanda mostrado como real quando a fonte está offline/bloqueada (deve ser honest-null) |
| H08 | EAN/GTIN/código de barras excluídos do join | Qualquer referência de chave de join a ean/gtin/barcode |

## Pontuação SOFT
| Dim | Dimensão | Peso | Guia de Pontuação |
|-----|-----------|--------|---------------|
| D01 | Fidelidade de seção | 0.20 | 8/8 byte-idêntico = 1.0, 1 drift = 0.6 |
| D02 | Completude de proveniência | 0.15 | Fontes consultadas + sem dado + status + banda = 1.0, parcial = 0.6 |
| D03 | Clareza do gate | 0.15 | Condições explicitadas + avaliadas = 1.0, só o valor do gate = 0.4 |
| D04 | Disciplina honest-null | 0.15 | Zero células fabricadas = 1.0, 1+ fabricada = 0.0 (também falha H07) |
| D05 | Transparência de Cobertura | 0.10 | Bucket manual + cauda-longa contados, não descartados = 1.0 |
| D06 | Rastreabilidade da matemática de margem | 0.10 | Modelo de fee/frete + BRUTA/LIQUIDA rotulados = 1.0 |
| D07 | Documentação | 0.10 | Completa = 1.0, parcial = 0.7 |
| D08 | Versionamento | 0.05 | Versionado = 1.0, sem versão = 0.5 |

## Ações
| Pontuação | Ação |
|-------|--------|
| GOLDEN | Aprovar |
| PUBLISH | Publicar |
| REVIEW | Peer review |
| REJECT | Rejeitar |

## Bypass
| condições | aprovador | trilha de auditoria |
|-----------|----------|-------------|
| Deploy de tenant aprovado pelo founder apesar de um scaffold offline (sem credencial de demanda ao vivo) | Líder N06 | "Bypass aprovado pelo líder N06 em <data> -- scaffold offline aceito para revisão estrutural" |

## Exemplos

## Exemplo Golden (trecho -- scaffold offline, honesto)
```markdown
## Veredito + proximos passos
| Campo | Valor |
|-------|-------|
| sourcing_confiavel | false |
| Condicoes do gate | margem_bruta_top >= 25% AND top-N verificado AND nenhum item critico sem preco AND frescor != RED |
| Avaliacao das condicoes | BLOQUEADO: offline -- demanda blocked: offline, sem preco de mercado para avaliar margem |
| Acoes ranqueadas | 1) Executar com credencial + demand_sources; 2) verificar top-10 (preco web = teto); 3) recodificar os itens do bucket "manual / sem preco" |
| Proximo passo encadeavel | N/A (gate BLOQUEADO) |
```
Por que passa: nomeia o gate, explicita as 4 condições, avalia-as honestamente contra o estado offline, e nunca inventa um preço de mercado.

## Anti-Exemplo 1: Preço de Mercado Fabricado
```markdown
| # | Produto | Fornecedor (desc%) | Custo | Preco mercado | Margem | Demanda | Relevancia | Score |
|---|---------|--------------------|-------|--------------|--------|---------|------------|------|
| 1 | Furadeira 650W | FerragensBR (32%) | R$ 142,80 | R$ 299,90 | 52% | ALTA | ALTA | 0.91 |
```
## Por que falha
A linha mostra um preço de mercado e um nível de demanda com aparência real, sem nenhuma `credential`/`demand_sources` declarada e sem entrada correspondente em Proveniencia -- H07 falha: um valor plausível mas inventado, onde o caminho offline do gerador exige `"nao pesquisado"` (S5 honest-null).

## Anti-Exemplo 2: Condições de Gate Ausentes
```markdown
## Veredito + proximos passos
sourcing_confiavel: true
```
## Por que falha
Declara o valor do gate sem condições booleanas e sem linha de avaliação -- falha H06 (S4 exige as condições explicitadas, não só o veredito) e não dá a uma capability downstream nada para encadear.

### H_RELATED: Checagem de Referência Cruzada (HARD)
- [ ] Campo `related:` do frontmatter preenchido (mínimo 3 entradas)
- [ ] Seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJECT se < 3 entradas (auto-populado por cex_wikilink.py no F6.5)

### S_RELATED: Checagem de Referência Cruzada (SOFT)
- [ ] Campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] Seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, apenas incentiva a fiação)

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | related | 0.45 |
| [[opportunity-matrix-builder]] | related | 0.42 |
| [[bld_knowledge_opportunity_matrix]] | related | 0.35 |
| p08_adr_opportunity_matrix_kind | upstream | 0.33 |
