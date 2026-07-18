---
id: p10_lr_content-monetization-builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-03-31
updated: 2026-03-31
author: n03_engineering
observation: "Configs de monetizacao de conteudo que fixam a precificacao no codigo da aplicacao ficam inviaveis de manter quando se faz teste A/B de tiers, troca de provedor ou expansao para novos mercados. Externalizar todos os parametros de monetizacao em config YAML reduziu o ciclo de mudanca de preco de 2-3 horas de desenvolvimento para 5 minutos."
pattern: "Externalize TODOS os parametros de monetizacao: tiers, precos, custos de credito, config de provedor, gatilhos de e-mail, orcamentos de anuncio. Monetizacao orientada a config permite mudancas de preco sem dev, teste A/B e expansao multi-mercado sem alterar codigo."
evidence: "3 negocios de conteudo analisados: (1) ACME ferramentas de IA -- sistema de creditos com 4 operacoes de pipeline, precificacao hibrida, margem de 35%. (2) PetVida cursos -- checkout Hotmart, conteudo em liberacao gradual, margem de 70%. (3) DigitalPro infoproduto -- funil Kiwify + Meta Ads, margem de 60%. Todos compartilhavam o mesmo problema: precificacao presa no codigo, troca de provedor exigia reescrita, nenhum rastreio de margem."
confidence: 0.85
outcome: SUCCESS
domain: content_monetization
tags: [monetization, pricing, config-driven, credits, checkout, margin-tracking]
tldr: "Monetizacao orientada a config: 2-3 horas de dev → 5 min para mudancas de preco. O rastreio de margem evita a erosao silenciosa do lucro."
impact_score: 8.5
decay_rate: 0.03
keywords: [monetizacao, precificacao, creditos, checkout, config, margem, webhook]
memory_scope: project
observation_types: [user, feedback, project, reference]
quality: null
title: "Memory Content Monetization"
8f: "F7_govern"
density_score: 0.90
llm_function: INJECT
related:
  - content-monetization-builder
  - bld_tools_memory_type
  - bld_config_tagline
---
## Resumo
A monetizacao de conteudo tem duas preocupacoes ortogonais: logica de negocio (o
que cobrar, como funcionam os creditos, o que dispara um e-mail) e integracao
tecnica (qual API de pagamento, qual provedor de e-mail, qual plataforma de
anuncio). Elas evoluem em velocidades muito diferentes -- o negocio muda toda
semana (testar A/B um preco), a integracao muda a cada trimestre (trocar de
Stripe para Hotmart no mercado BR).

O pipeline de 9 estagios reforca essa separacao. De PARSE a VALIDATE sao
estagios de logica de negocio que operam sobre valores de config. CHECKOUT,
ADS e EMAILS sao estagios de integracao que operam sobre APIs especificas de
cada provedor via referencias a ENV_VAR.

## Principais Aprendizados

### Rastreio de Margem Nao e Negociavel
Sem um floor_margin_pct explicito por tier, os custos de pipeline (tokens de
LLM, chamadas de API) corroem o lucro silenciosamente. Um tier "Pro" a
R$99,90/mes com 1000 creditos custa ~R$50 em operacoes de pipeline -- a margem
e 50%. Mas se os custos de credito aumentarem (reajuste de preco do modelo,
nova operacao mais cara), a margem cai sem que ninguem perceba. floor_margin_pct
>= 0.30 com checagem automatizada pega isso antes que vire um problema no P&L.

### Sistemas de Creditos Precisam de Politica de Saldo Negativo
Comportamento de saldo negativo (overdraft) indefinido causa tres problemas:
(1) saldos negativos geram disputas de cobranca, (2) usuarios que zeram o
saldo no meio de uma operacao recebem resultados quebrados, (3) o time de
suporte nao tem uma politica de referencia. Um overdraft_policy explicito
(block, notify_then_block, allow_negative) elimina a ambiguidade.

### Modo Mock Evita Erros Caros
Toda integracao de checkout precisa ter mock_mode: true por padrao. APIs de
pagamento reais em ambientes de desenvolvimento causam: cobrancas reais
(chargebacks), enxurradas de webhook (corrupcao de dados de producao) e
exposicao de chaves de API em logs. Desenvolvimento mock-first pega bugs de
integracao antes que dinheiro real se mova.

## Antipadrao: Checkout Monolitico
Embutir a logica especifica do Stripe espalhada pela aplicacao torna a troca
para Hotmart (para infoprodutos BR) uma reescrita completa. Checkout orientado
a config (provider + webhook_url + webhook_secret_env) permite trocar de
provedor com zero mudanca de codigo -- so atualizacao de config.

## Contexto do Builder

Esta ISO opera dentro do stack `content-monetization-builder`, um dos 125
builders especializados na arquitetura CEX. Cada builder tem 12 ISOs cobrindo
system prompt, instruction, output template, quality gate, examples, schema,
config, tools, memory, manifest, constraints, validation schema e runtime
rules.

O builder carrega as ISOs via `cex_skill_loader.py` no estagio F3 (Compose) do
pipeline, mescla com a memoria relevante via `cex_memory_select.py`, e produz
artefatos que precisam passar pelo quality gate no F7 (Filter).

| Componente | Finalidade |
|-----------|-----------|
| System prompt | Identidade e regras de comportamento |
| Instruction | Procedimento passo a passo |
| Output template | Estrutura/esqueleto |
| Quality gate | Rubrica de pontuacao |
| Examples | Referencias few-shot |

## Checklist

1. Criado via pipeline 8F
2. Pontuado pelo cex_score nas tres camadas
3. Compilado pelo cex_compile para validacao
4. Recuperado pelo cex_retriever para injecao
5. Evoluido pelo cex_evolve quando a qualidade cai

## Referencia

```yaml
id: p10_lr_content-monetization-builder
pipeline: 8F
scoring: hybrid_3_layer
target: 9.0
```

```bash
python _tools/cex_score.py --apply --verbose p10_lr_content-monetization-builder.md
```

## Propriedades

| Propriedade | Valor |
|-----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | content_monetization |
| Pipeline | 8F |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta | 9.0+ |
| Densidade | 0.85+ |

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[content-monetization-builder]] | downstream | 0.34 |
| bld_tools_memory_type | upstream | 0.30 |
| [[bld_config_tagline]] | upstream | 0.29 |
| [[bld_orchestration_content_monetization]] | downstream | 0.28 |
| p10_lr_e2e_eval_builder | sibling | 0.28 |
