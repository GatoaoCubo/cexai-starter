---
id: bld_feedback_marketplace_listing
kind: reward_signal
pillar: P11
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Feedback: sinais de recompensa + regressão do marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, feedback, signals, P11]
tldr: "O que recompensar e o que sinalizar nas construções de marketplace_listing: completo-na-primeira-tentativa, auto-injeção correta, lacunas honestas, e a divergência conhecida de https/estoque vs. a camada de nível mais baixo."
density_score: 0.88
related:
  - bld_eval_marketplace_listing
  - bld_memory_marketplace_listing
  - bld_knowledge_marketplace_listing
  - output-validator-builder
  - bld_architecture_marketplace_listing
---

# Feedback: sinais do marketplace_listing
## Sinais de recompensa (reforçar)
| Sinal | Significado |
|--------|---------|
| complete_first_try | os 3 campos do gate (titulo_ml/categoria_ml/preco) presentes -> score 1.0, passed=true, zero retentativas |
| brand_sku_injected_clean | BRAND + SELLER_SKU aparecem em attributes[] exatamente uma vez, nunca duplicados quando atributos já declarava um |
| condition_mapped_correctly | novo/usado/recondicionado mapeiam para new/used/refurbished sem nenhum 4º valor inventado |
| honest_gap_noted | um campo opcional ausente (fotos/marca/descricao) renderiza sua nota `[WARN]` exata, nunca um descarte silencioso |
| dual_output_ready | o frontmatter do artefato carrega score/passed/notes/real para que `cex_dual_output.to_dual_output` não precise adivinhar nada |

## Sinais de regressão (sinalizar)
| Sinal | Significado |
|--------|---------|
| section_retitled_or_reordered | quebra o contrato CONGELADO de 6 seções -> falha do gate forçado H05 |
| fabricated_photo_url | violação de clean-room -> rejeitar + reconstruir somente a partir da linha G1 real |
| category_id_silently_empty | nenhuma nota `[FAIL]` anexada -- a resolução de categoria é um TODO CONHECIDO (precisa de um token ML ao vivo, conforme o comentário `category_source` de `cex_channel_adapter.py`) |
| https_filter_assumed | o generator EM PRODUÇÃO NÃO filtra URLs de foto não-https (diferente da camada de nível mais baixo `cex_channel_adapter.py`) -- não afirme que ele faz isso |
| stock_zero_assumed_blocking | o generator EM PRODUÇÃO NÃO bloqueia de forma forçada quando `available_quantity<=0` (somente o `buyability()` da outra camada faz isso) -- não invente um bloqueio que não existe |
| quality_score_conflated | escrever um número em `quality:` em vez de `null`, ou escrever o `score` de prontidão dentro de `quality:` -- são dois campos distintos |

## Gancho do laço de aprendizado
Aprovações/rejeições da revisão por pares alimentam construções futuras; uma rejeição em
`category_id_silently_empty` ou `https_filter_assumed` deve atualizar
[[bld_knowledge_marketplace_listing]] antes da próxima construção, não somente esta instância.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_eval_marketplace_listing]] | upstream | 0.48 |
| [[bld_memory_marketplace_listing]] | sibling | 0.42 |
| [[bld_knowledge_marketplace_listing]] | related | 0.42 |
| [[output-validator-builder]] | related | 0.38 |
| [[bld_architecture_marketplace_listing]] | related | 0.36 |
