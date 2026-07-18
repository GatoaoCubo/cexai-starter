---
kind: instruction
id: bld_instruction_content_monetization
pillar: P03
llm_function: REASON
purpose: "Processo de producao passo a passo para artefatos content_monetization"
pattern: "pipeline de 3 fases (pesquisa -> composicao -> validacao)"
quality: null
title: "Instruction Content Monetization"
version: "1.0.0"
author: n03_builder
tags: [content_monetization, builder, examples]
tldr: "Exemplos de referencia e antiexemplos para a construcao de content_monetization, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construcao de content_monetization"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords: [construcao de content_monetization, instruction content monetization, content_monetization, builder, examples, para hotmart, para digistore, meta ads, google ads, em anuncios]
density_score: 0.90
related:
  - bld_architecture_content_monetization
  - bld_tools_content_monetization
---
# Instrucoes: Como Produzir um content_monetization

## Fase 1: PESQUISA
1. Identifique o negocio: nicho, pais, moeda, publico-alvo, tipo de conteudo
2. Audite a monetizacao existente: precificacao atual, provedor de pagamento, plataforma de curso
3. Catalogue os ativos de conteudo: o que pode ser monetizado (ferramentas, relatorios, cursos, dados, acesso a API)
4. Mapeie os custos de pipeline: tokens de LLM por operacao, chamadas de API, computacao -- expresse em creditos
5. Pesquise concorrentes: faixas de preco, nomes de tiers, empacotamento de recursos no nicho
6. Identifique os provedores de pagamento disponiveis no mercado-alvo:
   - Global: Stripe (cartoes + assinaturas + cobranca por uso)
   - Infoprodutos BR: Hotmart, Kiwify, Monetizze, Eduzz (paginas de checkout + afiliados)
   - Infoprodutos INT: Digistore24 (lider na UE, Merchant of Record, VAT automatico)
   - Estrategia de par de plataformas: Hotmart (BR/LATAM) + Digistore24 (UE/DACH/INT)
7. Para Hotmart: configure o bearer token OAuth2, webhook com HMAC sha256 (X-Hotmart-Hottok)
8. Para Digistore24: configure a chave de API (header X-DS-API-KEY), IPN com verificacao sha512
   - IPN da DS24: POST form-encoded (NAO JSON), a resposta precisa ser a string exata "OK"
   - Sandbox da DS24: crie um produto de teste, teste o endpoint de IPN, confirme a resposta "OK"
   - Recursos da DS24: 7 idiomas nativos (DE,EN,ES,FR,IT,NL,PL), metodos de pagamento por pais
   - DS24 como Merchant of Record: cuida da cobranca/repasse do VAT da UE automaticamente
9. Defina o provedor de e-mail: Resend (dev-friendly), SendGrid (escala), SES (custo), Mailchimp (no-code)
10. Defina as plataformas de anuncio: Meta Ads (B2C), Google Ads (intencao), LinkedIn Ads (B2B), TikTok Ads (gen-z)
11. Verifique artefatos content_monetization existentes para evitar sobreposicao de config

## Fase 2: COMPOSICAO
1. Leia bld_schema_content_monetization.md -- fonte da verdade para os campos da config
2. Leia bld_output_template_content_monetization.md -- estrutura do template
3. Preencha o frontmatter: id, kind, pillar, title, version, quality: null
4. Escreva o estagio PARSE: inventarie os ativos de conteudo, classifique por potencial de monetizacao
5. Escreva o estagio PRICING: defina a estrategia e os tiers
   - Escolha a estrategia: freemium (gratis + pago), tiered (bom/melhor/otimo), usage (pagamento por uso),
     credit_pack (pacotes pre-pagos), hybrid (tier + creditos excedentes)
   - Defina os tiers: nome, preco mensal (centavos/cents), preco anual, creditos incluidos, recursos
   - Defina floor_margin_pct >= 0.30 -- calcule: (preco - custo_de_pipeline) / preco >= 0.30
   - Opcional: trial_days (7-30), desconto anual (tipicamente 2 meses gratis)
   - Multi-moeda: BRL para Hotmart/BR, EUR para DS24/INT, USD como fallback global
   - PPP: considere a Paridade do Poder de Compra (PPP) -- tiers de preco mais baixos para mercados emergentes
6. Escreva o estagio CREDITS: mapeie as operacoes de pipeline para custos em creditos
   - Cada operacao: nome, custo em creditos, custo subjacente (tokens de LLM, API, computacao)
   - Defina pacotes para usuarios pay-as-you-go: nome, creditos, preco
   - Defina overdraft_policy: block (mais seguro), notify_then_block, allow_negative (arriscado)
7. Escreva o estagio CHECKOUT: integracao com o provedor de pagamento (multi-plataforma)
   - Plataforma A (Hotmart/BR): env var HOTMART_TOKEN, URL de webhook, segredo HOTMART_HOTTOK
     - Webhook: payload JSON, assinatura HMAC sha256, idempotencia via transaction_id
     - Eventos: PURCHASE_COMPLETE, PURCHASE_CANCELED, PURCHASE_REFUNDED, PURCHASE_CHARGEBACK
   - Plataforma B (Digistore24/INT): env var DS24_API_KEY, URL de IPN, DS24_IPN_PASSPHRASE
     - IPN: payload form-encoded (NAO JSON), verificacao de assinatura sha512
     - Resposta: o corpo precisa ser a string exata "OK" -- a DS24 reenvia ate receber "OK"
     - Eventos: on_payment, on_refund, on_chargeback, on_rebill_resumed, on_rebill_cancelled
   - Ambas as plataformas: deduplicacao via idempotency_key, redirects de sucesso/cancelamento, modo mock true por padrao
8. Escreva o estagio COURSES (se aplicavel):
   - Estrutura de modulos: titulo, aulas (titulo + tipo + duracao), drip_days
   - Certificacao: completion_threshold (padrao 0.80), template de certificado
   - Tipos de conteudo: video, texto, quiz, tarefa, sessao ao vivo
9. Escreva o estagio ADS (se aplicavel):
   - Selecao de plataforma: Meta (conscientizacao B2C), Google (captura de intencao), LinkedIn (B2B)
   - Alocacao de orcamento: orcamento mensal em centavos, CPA alvo
   - Rastreio: env vars de pixel/tag, eventos de conversao
10. Escreva o estagio EMAILS:
    - Sequencias: onboarding (pos-cadastro), upsell (pos-trial), prevencao de churn (pre-cancelamento)
    - Gatilhos: comportamental (usou o recurso X), baseado em tempo (dia 3), limiar (creditos < 10%)
    - Config do provedor: env var da chave de API, endereco de remetente, reply-to
11. Escreva o estagio VALIDATE: checagens pre-lancamento
    - Validacao de margem: todo tier precisa passar no floor_margin_pct
    - Teste de webhook: envie um evento de teste, confirme o tratamento idempotente
    - Checkout mock: complete o fluxo inteiro com credenciais de teste
12. Escreva o estagio DEPLOY: checklist de transicao mock→producao

## Fase 3: VALIDACAO
1. Confira se os 9 estagios do pipeline estao documentados com entradas/saidas
2. Verifique a precificacao: todos os valores em centavos/cents (inteiros, nunca float)
3. Verifique as margens: floor_margin_pct >= 0.30 em todo tier
4. Verifique que nao ha chaves de API/segredos em texto puro -- apenas referencias a ENV_VAR
5. Verifique que a idempotencia de webhook esta configurada (idempotency_key + deduplicacao)
6. Verifique que mock_mode e true por padrao
7. Verifique que os custos em creditos cobrem todas as operacoes de pipeline (nenhuma operacao sem rastreio)
8. Verifique que overdraft_policy esta definida explicitamente (nenhum comportamento implicito)
9. Confira que o corpo tem <= 4096 bytes por arquivo (6144 para instruction)

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_architecture_content_monetization]] | downstream | 0.50 |
| [[bld_knowledge_content_monetization]] | upstream | 0.48 |
| [[bld_tools_content_monetization]] | downstream | 0.43 |
| [[bld_orchestration_content_monetization]] | downstream | 0.40 |
