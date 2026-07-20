---
id: kc_sso_config
kind: knowledge_card
8f: F3_inject
title: SSO/SAML/OIDC Configuration Guide
version: 1.0.0
quality: null
pillar: P01
tldr: "SSO integration config for SAML and OIDC covering IdP endpoints, credentials, and token handling"
when_to_use: "When integrating single sign-on via SAML or OpenID Connect with an identity provider"
keywords: [single sign-on, saml, oidc, oauth 2.0, identity provider, service provider, security assertion markup language, signature algorithm, encryption algorithm]
tags: [sso, saml, oidc, oauth2, identity-provider, authentication, config]
long_tails:
  - "how do I configure SAML or OIDC single sign-on with an identity provider"
  - "which SSO parameters and security controls must I set for an IdP integration"
density_score: 0.92
related:
  - sso-config-builder
  - bld_knowledge_card_sso_config
  - bld_instruction_sso_config
  - p10_mem_sso_config_builder
  - p09_qg_sso_config
---

**SSO/SAML/OIDC Configuration Overview**

Single Sign-On (SSO) protocols like SAML and OIDC enable secure identity provider (IdP) integration. This guide covers configuration essentials for these standards:

1. **Core Components**
   - Identity Provider (IdP): Authenticates users (e.g., Okta, Azure AD)
   - Service Provider (SP): Receives authentication assertions (your application)
   - Security Assertion Markup Language (SAML)
   - OpenID Connect (OIDC) - OAuth 2.0 extension for identity

2. **Configuration Parameters**
   - `issuer`: IdP's unique identifier (e.g., `https://idp.example.com`)
   - `client_id`: SP's registered identifier with the IdP
   - `client_secret`: Secure credential for SP authentication
   - `redirect_uri`: SP's endpoint for IdP authentication responses
   - `signature_algorithm`: Signing method for SAML assertions (e.g., `RSA-SHA256`)
   - `encryption_algorithm`: Data encryption method (e.g., `AES256-CBC`)
   - `token_endpoint`: OIDC token endpoint URL
   - `authorization_endpoint`: OIDC authorization endpoint URL

3. **Implementation Considerations**
   - Use HTTPS for all communication
   - Validate certificate chains for IdP trust
   - Implement token introspection for OIDC
   - Set appropriate session expiration times
   - Monitor for replay attacks and CSRF vulnerabilities
   - Regularly rotate client secrets
   - Maintain audit logs of authentication events

## How to use
Load this card at F3 INJECT when wiring an application to an external IdP. Act on it as follows:
- Register the SP with the IdP, then set `client_id`, `client_secret`, and `redirect_uri` exactly as the IdP expects.
- Use HTTPS everywhere and validate the IdP certificate chain before trusting any assertion.
- Configure `signature_algorithm` / `encryption_algorithm` (e.g. RSA-SHA256 / AES256-CBC) and verify them on every inbound assertion.
- Always set session expiration, rotate secrets, and guard against replay/CSRF; keep audit logs of authentication events.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[sso-config-builder]] | downstream | 0.53 |
| [[bld_knowledge_card_sso_config]] | sibling | 0.51 |
| [[bld_instruction_sso_config]] | downstream | 0.46 |
| [[p10_mem_sso_config_builder]] | downstream | 0.42 |
| [[p09_qg_sso_config]] | downstream | 0.41 |
