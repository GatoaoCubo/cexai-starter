---
id: p05_pp_pricing_page_n06
kind: pricing_page
pillar: P05
nucleus: n06
title: "Pricing Page -- Responsive HTML Template"
version: 1.0.0
quality: null
tags: [output, pricing_page, html, responsive, n06]
tldr: "Responsive HTML pricing page, 3 tiers, brand_config-driven colors/fonts. PIX + parcelamento FAQ shown as one localized-market example, not a hardcoded assumption. Every value is a {{BRAND_*}} / {{TIER_*}} placeholder -- fill from brand_config.yaml before publishing."
axioms:
  - "ALWAYS highlight the middle tier as 'most popular' -- anchoring lifts the hero tier's conversion."
  - "NEVER show more than 4 tiers -- choice paralysis kills conversion."
  - "Localize the FAQ (PIX/installments here) to your OWN market's payment norms; do not ship this file's example verbatim into a market where it does not apply."
density_score: 0.9
related:
  - kc_brand_monetization_models
  - p06_enum_pricing_tiers_n06
  - subscription_tier_n06
updated: "2026-07-20"
---

# Pricing Page -- {{BRAND_NAME}}

## Template Structure

```html
<!DOCTYPE html>
<html lang="{{BRAND_LANGUAGE}}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{BRAND_NAME}} -- Pricing</title>
  <style>
    :root {
      --primary: {{PRIMARY_HEX}};
      --secondary: {{SECONDARY_HEX}};
      --accent: {{ACCENT_HEX}};
      --bg: {{BG_HEX}};
      --fg: {{FG_HEX}};
      --surface: {{SURFACE_HEX}};
      --font-heading: '{{HEADING_FONT}}', sans-serif;
      --font-body: '{{BODY_FONT}}', sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--fg);
      line-height: 1.6;
    }

    .pricing-header {
      text-align: center;
      padding: 4rem 1rem 2rem;
    }
    .pricing-header h1 {
      font-family: var(--font-heading);
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }
    .pricing-header p {
      font-size: 1.2rem;
      opacity: 0.8;
      max-width: 600px;
      margin: 0 auto;
    }

    .pricing-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 2rem;
      padding: 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .pricing-card {
      background: var(--surface);
      border-radius: 12px;
      padding: 2rem;
      text-align: center;
      position: relative;
      border: 1px solid rgba(255,255,255,0.1);
    }
    .pricing-card.featured {
      border-color: var(--accent);
      transform: scale(1.05);
    }
    .pricing-card.featured::before {
      content: '{{FEATURED_BADGE}}';
      position: absolute;
      top: -12px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--accent);
      color: var(--bg);
      padding: 4px 16px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
    }

    .tier-name {
      font-family: var(--font-heading);
      font-size: 1.5rem;
      margin-bottom: 0.5rem;
    }
    .tier-price {
      font-size: 3rem;
      font-weight: 700;
      color: var(--accent);
    }
    .tier-price small {
      font-size: 1rem;
      opacity: 0.7;
    }
    .tier-installment {
      font-size: 0.9rem;
      opacity: 0.7;
      margin-top: 0.25rem;
    }

    .tier-features {
      list-style: none;
      padding: 1.5rem 0;
      text-align: left;
    }
    .tier-features li {
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .tier-features li::before { content: '[x] '; }
    .tier-features li.no::before { content: '[ ] '; opacity: 0.4; }

    .cta-btn {
      display: block;
      background: var(--accent);
      color: var(--bg);
      text-decoration: none;
      padding: 1rem 2rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 1.1rem;
      margin-top: 1rem;
      transition: opacity 0.2s;
    }
    .cta-btn:hover { opacity: 0.9; }

    .social-proof {
      text-align: center;
      padding: 3rem 1rem;
      font-size: 1.1rem;
      opacity: 0.8;
    }

    .faq {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }
    .faq details {
      background: var(--surface);
      border-radius: 8px;
      margin-bottom: 0.5rem;
      padding: 1rem;
    }
    .faq summary {
      cursor: pointer;
      font-weight: 600;
    }

    @media (max-width: 768px) {
      .pricing-card.featured { transform: scale(1); }
      .pricing-header h1 { font-size: 1.8rem; }
      .tier-price { font-size: 2.2rem; }
    }
  </style>
</head>
<body>

  <section class="pricing-header">
    <h1>{{PRICING_HEADLINE}}</h1>
    <p>{{PRICING_SUBHEADLINE}}</p>
  </section>

  <section class="pricing-grid">
    <!-- TIER 1 -->
    <div class="pricing-card">
      <div class="tier-name">{{TIER_1_NAME}}</div>
      <div class="tier-price">{{BRAND_CURRENCY}} {{TIER_1_PRICE}}<small>/mo</small></div>
      <div class="tier-installment">or {{TIER_1_ANNUAL}} /yr ({{TIER_1_DISCOUNT}}% off)</div>
      <ul class="tier-features">
        <li>{{TIER_1_FEAT_1}}</li>
        <li>{{TIER_1_FEAT_2}}</li>
        <li>{{TIER_1_FEAT_3}}</li>
        <li class="no">{{TIER_1_NO_1}}</li>
      </ul>
      <a href="{{TIER_1_URL}}" class="cta-btn">{{TIER_1_CTA}}</a>
    </div>

    <!-- TIER 2 (Featured) -->
    <div class="pricing-card featured">
      <div class="tier-name">{{TIER_2_NAME}}</div>
      <div class="tier-price">{{BRAND_CURRENCY}} {{TIER_2_PRICE}}<small>/mo</small></div>
      <div class="tier-installment">or {{TIER_2_ANNUAL}} /yr ({{TIER_2_DISCOUNT}}% off)</div>
      <ul class="tier-features">
        <li>{{TIER_2_FEAT_1}}</li>
        <li>{{TIER_2_FEAT_2}}</li>
        <li>{{TIER_2_FEAT_3}}</li>
        <li>{{TIER_2_FEAT_4}}</li>
      </ul>
      <a href="{{TIER_2_URL}}" class="cta-btn">{{TIER_2_CTA}}</a>
    </div>

    <!-- TIER 3 (Anchor) -->
    <div class="pricing-card">
      <div class="tier-name">{{TIER_3_NAME}}</div>
      <div class="tier-price">{{BRAND_CURRENCY}} {{TIER_3_PRICE}}<small>/mo</small></div>
      <div class="tier-installment">or {{TIER_3_ANNUAL}} /yr ({{TIER_3_DISCOUNT}}% off)</div>
      <ul class="tier-features">
        <li>{{TIER_3_FEAT_1}}</li>
        <li>{{TIER_3_FEAT_2}}</li>
        <li>{{TIER_3_FEAT_3}}</li>
        <li>{{TIER_3_FEAT_4}}</li>
        <li>{{TIER_3_FEAT_5}}</li>
      </ul>
      <a href="{{TIER_3_URL}}" class="cta-btn">{{TIER_3_CTA}}</a>
    </div>
  </section>

  <section class="social-proof">
    <p>{{SOCIAL_PROOF_TEXT}}</p>
  </section>

  <section class="faq">
    <h2>Frequently Asked Questions</h2>
    <details><summary>{{FAQ_1_Q}}</summary><p>{{FAQ_1_A}}</p></details>
    <details><summary>{{FAQ_2_Q}}</summary><p>{{FAQ_2_A}}</p></details>
    <details><summary>{{FAQ_3_Q}}</summary><p>{{FAQ_3_A}}</p></details>
    <!-- Localized payment-method example -- replace with your own market's norm -->
    <details><summary>{{LOCAL_PAYMENT_FAQ_Q}}</summary><p>{{LOCAL_PAYMENT_FAQ_A}}</p></details>
    <details><summary>{{INSTALLMENT_FAQ_Q}}</summary><p>{{INSTALLMENT_FAQ_A}}</p></details>
  </section>

</body>
</html>
```

## Usage Notes

1. All `{{BRAND_*}}` variables come from `brand_config.yaml`.
2. Tier-specific variables are filled by whichever role or agent owns pricing for this instance.
3. Responsive: mobile-first, breakpoint at 768px.
4. The FAQ block includes one localized-payment-method example slot -- fill it for your OWN market (installments, regional instant-payment rails, etc.); do not assume a specific country's payment culture applies globally.
5. Anchoring: Tier 3's price makes Tier 2 look affordable; the featured badge draws the eye to the recommended tier.

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[kc_brand_monetization_models]] | upstream |
| [[p06_enum_pricing_tiers_n06]] | upstream (tier names/prices bound here originate from that enum) |
| [[subscription_tier_n06]] | related |
