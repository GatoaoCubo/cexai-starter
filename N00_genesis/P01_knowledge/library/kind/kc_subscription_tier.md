---
id: kc_subscription_tier
kind: knowledge_card
8f: F3_inject
title: Subscription Tier
version: 1.0.0
quality: null
pillar: P01
language: en
tldr: "Predefined pricing levels with distinct feature sets and cost structures for SaaS products"
when_to_use: "When designing tiered pricing models with feature gating and upgrade paths"
keywords: [subscription tier, saas products, per-user licensing, tiered pricing, feature matrix, value propositions, tier upgrades, adoption metrics]
density_score: 1.0
related:
  - bld_tools_subscription_tier
---

**Subscription Tier** refers to predefined pricing levels offering distinct feature sets and cost structures for SaaS products. Tiers typically include:

1. **Free Tier**  
   - Basic features  
   - Limited support  
   - No payment required  

2. **Starter Tier**  
   - Core features  
   - Email support  
   - $9.99/month  

3. **Professional Tier**  
   - Advanced tools  
   - Priority support  
   - $29.99/month  

4. **Enterprise Tier**  
   - Custom solutions  
   - Dedicated account manager  
   - $99.99/month  

**Pricing Models**:  
- Per-user licensing  
- Per-organization licensing  
- Tiered pricing with discounts for annual payments  

**Feature Matrix Example**:  
| Feature         | Free | Starter | Professional | Enterprise |
|-----------------|------|---------|--------------|------------|
| Storage         | 1GB  | 50GB    | 1TB          | Custom     |
| Team Support    | No   | Email   | Priority     | Dedicated   |
| API Access      | No   | Limited | Full         | Full        |
| Custom Reports  | No   | No      | Yes          | Yes         |

**Best Practices**:  
- Align tiers with customer needs  
- Use clear value propositions  
- Offer tier upgrades with incentives  
- Monitor tier adoption metrics

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_subscription_tier]] | downstream | 0.39 |
| bld_instruction_pricing_page | downstream | 0.36 |
| [[bld_tools_subscription_tier]] | downstream | 0.36 |
| [[bld_orchestration_subscription_tier]] | downstream | 0.32 |
