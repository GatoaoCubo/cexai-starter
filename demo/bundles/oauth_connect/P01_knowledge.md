---
kind: knowledge_card
id: bld_knowledge_card_oauth_app_config
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para a produção de oauth_app_config
quality: null
title: "Knowledge Card Oauth App Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [oauth_app_config, builder, knowledge_card]
tldr: "Conhecimento de domínio para a produção de oauth_app_config"
domain: "construção de oauth_app_config"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [oauth_app_config construction, oauth_app_config, builder, knowledge_card, read_user, write_orders, domain overview, key concepts, token lifetime, bearer token]
density_score: 0.85
related:
  - kc_oauth_app_config
---
## Visão Geral do Domínio
A configuração de app OAuth2/PKCE define os parâmetros seguros de integração para aplicações de terceiros que acessam APIs protegidas. Ela governa permissões de escopo, endpoints de redirecionamento, tempo de vida dos tokens e políticas de refresh para garantir conformidade com padrões de segurança e privacidade. Uma configuração adequada previne uso indevido de tokens, vulnerabilidades de redirecionamento e acesso não autorizado, especialmente em ecossistemas de parceiros onde os apps podem ter níveis de confiança variados. Isso difere de SSO (identidade corporativa) e de gestão de segredos (credenciais brutas) por focar em controle de acesso a API e gestão do ciclo de vida do token.

## Conceitos-Chave
| Conceito                 | Definição                                                                   | Fonte                       |
|---------------------------|------------------------------------------------------------------------------|-----------------------------|
| Scopes                   | Permissões concedidas a um app (ex.: `read_user`, `write_orders`).           | RFC 6749 §3.3               |
| Redirect URIs            | URLs para onde o authorization server redireciona após o consentimento do usuário. | RFC 8252 §2.2                |
| Client ID/Secret         | Credenciais para identificação do app (clientes públicos vs. confidenciais). | RFC 6749 §2.1               |
| Token Lifetime           | Duração até o access token expirar (tipicamente 1-120 minutos).             | OAuth 2.0 Bearer Token      |
| Refresh Token            | Token de longa duração para obter novos access tokens sem reautenticar.     | RFC 6749 §6                 |
| PKCE Code Challenge      | Proof Key for Code Exchange (PKCE) para proteger fluxos de clientes públicos. | RFC 7636                    |
| Authorization Grant Type | Tipo de fluxo (ex.: Authorization Code, Implicit) que define a emissão do token. | RFC 6749 §1.3                |
| Token Endpoint Auth      | Método para autenticar o client no token endpoint (ex.: client_secret_post). | RFC 6749 §2.3.1              |
| Consent Scope            | Escopo de permissões concedidas pelo usuário durante a autorização.          | OpenID Connect Core 1.0     |
| Token Introspection      | Mecanismo para checar validade e escopo do token.                            | RFC 7662                    |
| Refresh Policy           | Regras para rotação, expiração e limites de reuso do refresh token.          | OAuth 2.0 Security Best Practices |
| Token Rotation           | Substituição periódica de refresh tokens para mitigar exposição de longo prazo. | NIST SP 800-63B              |

## Padrões da Indústria
- RFC 6749: OAuth 2.0 Authorization Framework
- RFC 7636: OAuth 2.0 Proof Key for Code Exchange by OAuth Public Clients (PKCE)
- RFC 8252: OAuth 2.0 for Native Apps
- OAuth 2.0 Bearer Token Usage (RFC 6750)
- OAuth 2.0 Token Introspection (RFC 7662)
- OAuth 2.0 Token Revocation (RFC 7009)
- OpenID Connect Core 1.0 (OpenID Foundation, não é uma RFC IETF)
- OpenID Connect Discovery 1.0 (.well-known/openid-configuration)
- OAuth 2.0 Security Best Current Practice (draft-ietf-oauth-security-topics, BCP)
- OAuth 2.1 (draft-ietf-oauth-v2-1: PKCE obrigatório, sem implicit, sem ROPC)
- JWT (RFC 7519) e JWT Profile for OAuth 2.0 Access Tokens (RFC 9068)
- NIST SP 800-63B: Digital Identity Guidelines

## Padrões Comuns
1. Usar controle de acesso baseado em escopo para permissões granulares.
2. Exigir HTTPS em todos os redirect URIs para evitar interceptação.
3. Definir access tokens de vida curta com refresh tokens de vida longa.
4. Implementar PKCE para clientes públicos, prevenindo interceptação do authorization code.
5. Usar rotação de refresh token para limitar a exposição.
6. Definir políticas de refresh com expiração e limites de reuso.

## Armadilhas
- Escopos excessivamente amplos, concedendo permissões demais.
- Permitir redirect URIs em HTTP (vulnerável a ataques MITM).
- Não limitar o tempo de vida dos tokens, aumentando o risco de replay.
- Políticas de refresh malconfiguradas que permitem reuso de token.
- Pular o PKCE em fluxos de clientes públicos (expõe authorization codes).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_oauth_app_config]] | sibling | 0.50 |
| hybrid_review7_n03 | downstream | 0.48 |
| ex_oauth_app_config_meli | downstream | 0.44 |
| ex_oauth_app_config_bling | downstream | 0.42 |
