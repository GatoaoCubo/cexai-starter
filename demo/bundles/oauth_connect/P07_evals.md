---
kind: quality_gate
id: p09_qg_oauth_app_config
pillar: P11
llm_function: GOVERN
purpose: Quality gate com pontuação HARD e SOFT para oauth_app_config
quality: null
title: "Quality Gate Oauth App Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [oauth_app_config, builder, quality_gate]
tldr: "Quality gate com pontuação HARD e SOFT para oauth_app_config"
domain: "construção de oauth_app_config"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [oauth_app_config construction, oauth_app_config, builder, quality_gate, "## anti-example 1: missing redirect uris", quality gate, fail condition, scoring guide, golden example, missing redirect]
density_score: 0.85
related:
  - kc_oauth_app_config
---
## Quality Gate

## Definição
| métrica | limite | operador | escopo |
|---|---|---|---|
| schema_id | ^p09_oauth_[a-z][a-z0-9_]+.yaml$ | corresponde a | H02 |
| required_fields | 7 | >= | config do app |

## Gates HARD
| ID | Checagem | Condição de Falha |
|---|---|---|
| H01 | Frontmatter YAML válido | sintaxe YAML inválida |
| H02 | ID corresponde ao padrão ^p09_oauth_[a-z][a-z0-9_]+.yaml$ | ID de schema inválido |
| H03 | Campo kind corresponde a 'oauth_app_config' | valor de kind incorreto |
| H04 | client_id presente | client_id ausente |
| H05 | redirect_uris são URLs válidas | formato de redirect URI inválido |
| H06 | scopes não vazios | scopes vazios ou ausentes |
| H07 | access_token_lifetime <= 3600 (OAuth BCP recomenda 5-60 min) | tempo de vida do token excede 1h |
| H08 | refresh_token_policy é 'rotating' (OAuth 2.1 / BCP) | refresh tokens estáticos não permitidos |
| H09 | grant_types é subconjunto de {authorization_code, client_credentials, refresh_token} | implicit/ROPC proibidos pela OAuth 2.1 |
| H10 | PKCE (S256) obrigatório para o fluxo authorization_code | code_challenge_method ausente |

## Pontuação SOFT
| Dim | Dimensão | Peso | Guia de Pontuação |
|---|---|---|---|
| D01 | Completude de escopo | 0.15 | 1.0 se todos os escopos obrigatórios presentes |
| D02 | Validade do redirect | 0.15 | 1.0 se todos os URIs são HTTPS e registrados |
| D03 | Tempo de vida do token | 0.15 | 1.0 se <= 24h e alinhado com a política |
| D04 | Política de refresh | 0.15 | 1.0 se 'rolling' ou 'fixed' com regras claras |
| D05 | Práticas de segurança | 0.10 | 1.0 se PKCE aplicado e client secrets rotacionados |
| D06 | Documentação | 0.10 | 1.0 se a config do app inclui exemplos de uso |
| D07 | Conformidade com padrões | 0.20 | 1.0 se alinhado com OAuth 2.1 + RFC 7636 PKCE + RFC 8252 |

## Ações
| Score | Ação |
|---|---|
| GOLDEN | >=9.5 | Auto-aprovar e implantar |
| PUBLISH | >=8.0 | Implantar após revisão |
| REVIEW | >=7.0 | Exige revisão manual |
| REJECT | <7.0 | Bloqueia o deployment |

## Exceção (Bypass)
| condições | aprovador | trilha de auditoria |
|---|---|---|
| Exceção de segurança | CTO | "Bypassed by [nome] on [data] for [motivo]" |

## Exemplos

## Exemplo Golden
```yaml
kind: oauth_app_config
name: github_integration
spec:
  client_id: "ghp_1234567890abcdef1234567890abcdef1234"
  client_secret: "supersecretclientsecret"
  redirect_uris:
    - "https://app.example.com/auth/callback"
  scopes:
    - "repo"
    - "user"
  token_lifetimes:
    access_token_expires_in: 3600
    refresh_token_expires_in: 86400
  refresh_policy: "rotate"
```

## Anti-Exemplo 1: Redirect URIs Ausentes
```yaml
kind: oauth_app_config
name: bad_github_integration
spec:
  client_id: "ghp_0987654321abcdef0987654321abcdef0987"
  client_secret: "anothersecret"
  scopes:
    - "all"
```
## Por que falha
Falta redirect_uris, permitindo qualquer redirect URI, o que cria vulnerabilidades de open redirect. Também usa o escopo "all", concedendo permissões excessivas.

## Anti-Exemplo 2: Tempo de Vida de Token Inseguro
```yaml
kind: oauth_app_config
name: insecure_github_integration
spec:
  client_id: "ghp_1122334455abcdef1122334455abcdef1122"
  client_secret: "insecuresecret"
  redirect_uris:
    - "https://app.example.com/callback"
  scopes:
    - "public_repo"
  token_lifetimes:
    access_token_expires_in: 86400
    refresh_token_expires_in: 31536000
  refresh_policy: "reuse"
```
## Por que falha
Usa refresh tokens de 1 ano (31536000s), o que é excessivo e aumenta o risco de uso indevido do token. A política de refresh "reuse" permite que os tokens sejam usados indefinidamente, violando as boas práticas de segurança.

### H_RELATED: Checagem de Referência Cruzada (HARD)
- [ ] Campo de frontmatter `related:` preenchido (mínimo 3 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJECT se < 3 entradas (auto-preenchido por cex_wikilink.py em F6.5)

### S_RELATED: Checagem de Referência Cruzada (SOFT)
- [ ] Campo de frontmatter `related:` preenchido (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a conexão)
