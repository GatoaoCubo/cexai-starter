---
id: kc_starter_company
kind: knowledge_card
8f: F3_inject
type: domain
pillar: P01
domain: company_profile
title: "Sua Empresa -- Company Profile"
origin: distill_self_kc_carry
created: "2026-07-15"
quality: null
feeds_kinds:
  - knowledge_card
  - P01
tags: [self-knowledge, company-profile, tenant, starter]
tldr: "Real, cited facts about the tenant itself (name/tagline/shape/links/values) so self-referential 8F builds ground on owned facts instead of refusing to fabricate."
---

# Sua Empresa -- Company Profile
## Identity

- **Name**: Sua Empresa

> Source: `tenant_config.json: brand.name, brand.tagline (fallback brand_config.yaml: identity.BRAND_NAME, identity.BRAND_TAGLINE)`

## Business Shape

- **Vertical**: services
- **Has store**: yes
- **Has blog**: yes
- **Has B2B**: yes
- **B2B mode**: corporate
- **B2B label**: Para Empresas

> Source: `tenant_config.json: shape.vertical, shape.has_store, shape.has_blog, shape.has_b2b, shape.blog_subtitle_category, shape.b2b_mode, shape.b2b_label`
