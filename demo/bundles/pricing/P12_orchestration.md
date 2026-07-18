---
kind: collaboration
id: bld_collaboration_content_monetization
pillar: P12
llm_function: COLLABORATE
purpose: "Como o content-monetization-builder trabalha em crews com outros builders"
pattern: "cada builder precisa saber seu PAPEL, o que RECEBE e o que PRODUZ"
quality: null
title: "Collaboration Content Monetization"
version: "1.0.0"
author: n03_builder
tags: [content_monetization, builder, examples]
tldr: "Exemplos de referencia e antiexemplos para a construcao de content_monetization, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construcao de content_monetization"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [construcao de content_monetization, collaboration content monetization, content_monetization, builder, examples, "### crew: lancamento de infoproduto", "### crew: sistema de creditos saas", meu papel, composicoes de crew, fim da monetizacao de conteudo]
density_score: 0.90
related:
  - bld_architecture_content_monetization
  - content-monetization-builder
---
# Colaboracao: content-monetization-builder

## Meu Papel em Crews
Eu sou um ESPECIALISTA. Eu respondo UMA pergunta: "como precificamos, cobramos,
empacotamos creditos, vendemos cursos, rodamos anuncios e enviamos e-mails
para este negocio de conteudo, de ponta a ponta?"
Eu nao escrevo copy de marketing. Eu nao implemento APIs de pagamento. Eu nao
faco deploy de servicos. Eu produzo a arquitetura de monetizacao + o schema de
config para que builders downstream implementem e façam o deploy.

## Composicoes de Crew

### Crew: "Monetizacao de Conteudo de Ponta a Ponta"
```
1. research-pipeline-builder     → "inteligencia de mercado sobre precificacao + concorrentes"
2. content-monetization-builder  → "config de monetizacao em 9 estagios (precificacao→deploy)"
3. prompt-template-builder       → "templates de e-mail, descricoes de curso, briefings de anuncio"
4. cli-tool-builder              → "orquestrador de checkout + rastreador de creditos em CLI"
5. api-client-builder            → "clientes Stripe/Hotmart/DS24/provedor de e-mail"
6. spawn-config-builder          → "cron: renovacao de creditos, agendador de e-mail, sync de anuncios"
```

### Crew: "Lancamento Multi-Plataforma" (Hotmart BR + DS24 INT)
```
1. research-pipeline-builder     → "pesquisa de plataforma: API Hotmart+DS24, conformidade"
2. content-monetization-builder  → "config dual-plataforma: Hotmart(BR) + DS24(INT)"
3. api-client-builder            → "webhook Hotmart (JSON/sha256) + IPN DS24 (form/sha512)"
4. prompt-template-builder       → "copy (PT-BR + EN/DE), sequencias de e-mail"
5. cli-tool-builder              → "roteador de checkout (geo-deteccao → provedor)"
```

### Crew: "Lancamento de Infoproduto"
```
1. content-monetization-builder → "precificacao + checkout + estrutura de curso"
2. social-publisher-builder     → "posts da campanha de lancamento"
3. prompt-template-builder      → "copy da pagina de vendas + sequencias de e-mail"
```

### Crew: "Sistema de Creditos SaaS"
```
1. content-monetization-builder → "economia de creditos + precificacao por tier"
2. api-client-builder           → "API de medicao de uso"
3. db-connector-builder         → "schema do razao (ledger) de creditos"
4. notifier-builder             → "alertas de credito baixo"
```

## Protocolo de Handoff
| Eu recebo de | Dado | Formato |
|---------------|------|--------|
| Usuario / N07 | Requisitos de monetizacao | Handoff de missao .md |
| research-pipeline-builder | Dados de precificacao de concorrentes | JSON + signal |
| knowledge-card-builder | KCs de plataforma (API Hotmart, API DS24, conformidade) | Artefato KC |
| N01_intelligence | Pesquisa de plataforma (kc_hotmart_*, kc_digistore24_*, kc_content_platform_*) | 8 KCs |

| Eu envio para | Dado | Formato |
|----------|------|--------|
| N02_marketing | Precificacao para copy (nomes de tier, recursos, precos, ambas as moedas) | Config YAML + signal |
| N04_knowledge | Sistema de creditos + docs multi-plataforma para a base de conhecimento | Architecture .md |
| cli-tool-builder | Spec do pipeline de checkout duplo (Hotmart JSON + DS24 form-encoded) | Architecture .md |
| api-client-builder | Specs de API dos provedores: Hotmart REST + DS24 REST + handler de IPN | Tools .md |
| prompt-template-builder | Briefings de sequencia de e-mail + roteiros de curso (PT-BR + EN/DE) | Config YAML |
| spawn-config-builder | Agendamentos de cron (renovacao de credito, e-mail, health check de webhook) | Config .md |

## Roteamento por Nucleus
| Fase | Nucleus | Por que |
|-------|---------|-----|
| Projeto de monetizacao | N03 (engineering) | Trabalho de arquitetura + schema |
| Estrategia de precificacao | N06 (commercial) | Expertise em modelo de negocio |
| Copy de marketing | N02 (marketing) | Copy de anuncio, templates de e-mail, paginas de vendas |
| Implementacao | N05 (operations) | Codigo de checkout, API de creditos, deploy |
| Documentacao de conhecimento | N04 (knowledge) | KCs de plataforma, docs do sistema de creditos |

## Relacao com o Social Publisher
MONETIZAR (isto) → PROMOVER (social-publisher) → CONVERTER (checkout) → RETER (e-mail).

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_architecture_content_monetization]] | upstream | 0.43 |
| [[bld_orchestration_research_pipeline]] | sibling | 0.38 |
| [[content-monetization-builder]] | upstream | 0.38 |
| bld_collaboration_social_publisher | sibling | 0.34 |
| [[bld_knowledge_content_monetization]] | upstream | 0.31 |
