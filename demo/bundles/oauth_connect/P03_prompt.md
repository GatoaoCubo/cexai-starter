---
kind: instruction
id: bld_instruction_oauth_app_config
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para oauth_app_config
quality: null
title: "Instruction Oauth App Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [oauth_app_config, builder, instruction]
tldr: "Processo de produção passo a passo para oauth_app_config"
domain: "construção de oauth_app_config"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [oauth_app_config construction, instruction oauth app config, oauth_app_config, builder, instruction, client_id, client_secret, scopes, scope, redirect_uris]
density_score: 0.85
related:
  - kc_oauth_app_config
---
## Fase 1: PESQUISA
1. Identificar os requisitos de integração do parceiro (escopos, redirect URIs).
2. Documentar as variantes de fluxo OAuth2/PKCE exigidas (implicit, authorization code).
3. Determinar as restrições de tempo de vida do token (duração de access/refresh token).
4. Analisar a conformidade do parceiro com as especificações OIDC ou OAuth2.0.
5. Mapear as regras de política de refresh (ex.: expiração deslizante, rotação de token).
6. Verificar os formatos de redirect URI (HTTPS, domínios registrados).

## Fase 2: COMPOSIÇÃO
1. Definir `client_id` e `client_secret` por parceiro.
2. Enumerar `scopes` usando os valores enum de `scope` do SCHEMA.md.
3. Especificar o array `redirect_uris` com as strings de URI exatas.
4. Definir `access_token_lifetime` em segundos (mín 300, máx 86400).
5. Configurar `refresh_token_lifetime` (mín 604800, máx 2592000).
6. Atribuir `refresh_policy` a partir do enum `refresh_policy` do SCHEMA.md.
7. Incluir a flag booleana `pkce_required` (true para exigir PKCE).
8. Adicionar o campo `audience` para identificar a API alvo.
9. Finalizar usando a estrutura do OUTPUT_TEMPLATE.md com formatação YAML.

## Fase 3: VALIDAÇÃO
- [ ] Conformidade de schema verificada via validador `jsonschema`.
- [ ] Todos os campos obrigatórios (`client_id`, `scopes`, etc.) presentes.
- [ ] Redirect URIs correspondem aos domínios registrados e usam HTTPS.
- [ ] Tempo de vida do token dentro dos limites mín/máx configurados.
- [ ] Política de refresh alinhada aos valores do enum e às necessidades do parceiro.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_oauth_app_config]] | upstream | 0.40 |
| [[bld_knowledge_oauth_app_config]] | upstream | 0.30 |
