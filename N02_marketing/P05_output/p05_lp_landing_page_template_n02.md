---
id: p05_lp_landing_page_template_n02
kind: landing_page
8f: F6_produce
pillar: P05
title: Landing Page Template -- Production Ready
version: 1.0.0
created: 2026-07-20
author: n02_marketing
template_type: landing_page
output_format: html_with_integrated_copy
copy_formulas: [AIDA, PAS, BAB]
layout_patterns: [f_pattern, z_pattern]
sections: [hero, features, testimonials, pricing, faq, cta]
responsive: mobile_first
accessibility: wcag_aa
performance: lighthouse_90_plus
domain: visual_frontend_engineering_and_copywriting
quality: null
tags: [landing_page, dual_mode, html, tailwind, copy_integration, N02]
tldr: Complete landing page template with integrated copy -- hero through CTA sections, responsive design, WCAG AA, persuasion formulas driving the visual hierarchy.
keywords: [html, css, tailwindcss, a11y_compliant, lighthouse_target, f_pattern, pas, seo_description]
density_score: 0.92
related:
  - user_journey_n02
  - p06_vs_content_spec_n02
  - p09_env_brand_override_n02
---

# Landing Page Template — Production Ready

## Purpose

Complete template for generating conversion-focused landing pages that
integrate persuasive copy with visual hierarchy. Follows an F-pattern layout
supporting the PAS copy formula (Problem -> Agitate -> Solution).

## Template Structure

```html
---
component: landing_page_conversion
responsive: true
a11y_compliant: true
dark_mode: true
lighthouse_target: 90
page_type: landing_page
copy_formula: PAS
layout_pattern: f_pattern
breakpoints: [sm, md, lg, xl, 2xl]
color_scheme: "{{BRAND_SLUG}}"
---

<!DOCTYPE html>
<html lang="en" class="h-full scroll-smooth">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta -->
    <title>{{product_name}} — {{key_benefit}}</title>
    <meta name="description" content="{{seo_description}}">
    <meta property="og:title" content="{{product_name}} — {{key_benefit}}">
    <meta property="og:description" content="{{seo_description}}">
    <meta property="og:type" content="website">

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              primary: { DEFAULT: '{{BRAND_PRIMARY_HEX | default: "#50C878"}}', foreground: '#ffffff' },
              background: '#ffffff',
              foreground: '#111827',
              muted: { DEFAULT: '#f3f4f6', foreground: '#6b7280' },
              accent: { DEFAULT: '{{BRAND_PRIMARY_HEX | default: "#50C878"}}', foreground: '#ffffff' },
              border: '#e5e7eb',
            },
            fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
          }
        },
        darkMode: 'class',
      }
    </script>
  </head>

  <body class="min-h-screen bg-background text-foreground font-sans antialiased">
    <nav class="border-b border-border bg-background/95 backdrop-blur sticky top-0 z-50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 items-center justify-between">
          <a href="#" class="text-xl font-bold text-foreground">{{product_name}}</a>
          <button class="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium">
            {{nav_cta_text}}
          </button>
        </div>
      </div>
    </nav>

    <main>
      <!-- Hero — PROBLEM (PAS Formula) -->
      <section class="py-16 sm:py-24 lg:py-32">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid gap-8 lg:grid-cols-2 lg:gap-16 items-center">
            <div class="space-y-6 lg:space-y-8">
              <h1 class="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                {{hero_headline_v1}}
                <span class="text-primary">{{hero_headline_emphasis}}</span>
              </h1>
              <p class="text-xl text-muted-foreground sm:text-2xl leading-relaxed">
                {{hero_subheadline_agitate}}
              </p>
              <p class="text-sm text-muted-foreground font-medium">
                {{social_proof_stat}}  <!-- e.g. "[PROOF NEEDED: N customers]" until a real number is confirmed -->
              </p>
              <div class="flex flex-col gap-4 sm:flex-row">
                <button class="bg-primary text-primary-foreground px-8 py-4 rounded-lg text-lg font-semibold shadow-lg">
                  {{primary_cta_text}}
                </button>
                <button class="border border-border px-8 py-4 rounded-lg text-lg font-medium">
                  {{secondary_cta_text}}
                </button>
              </div>
            </div>
            <div class="lg:order-last">
              <div class="aspect-video rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 border border-border flex items-center justify-center">
                <p class="text-muted-foreground text-sm">{{visual_placeholder_text}}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features — SOLUTION (PAS Formula) -->
      <section id="features" class="py-16 bg-muted">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold sm:text-4xl mb-4">{{features_headline}}</h2>
            <p class="text-xl text-muted-foreground max-w-2xl mx-auto">{{features_subheadline}}</p>
          </div>
          <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div class="bg-background rounded-xl p-6 border border-border shadow-sm">
              <h3 class="text-lg font-semibold mb-2">{{feature_1_title}}</h3>
              <p class="text-muted-foreground">{{feature_1_description}}</p>
            </div>
            <div class="bg-background rounded-xl p-6 border border-border shadow-sm">
              <h3 class="text-lg font-semibold mb-2">{{feature_2_title}}</h3>
              <p class="text-muted-foreground">{{feature_2_description}}</p>
            </div>
            <div class="bg-background rounded-xl p-6 border border-border shadow-sm md:col-span-2 lg:col-span-1">
              <h3 class="text-lg font-semibold mb-2">{{feature_3_title}}</h3>
              <p class="text-muted-foreground">{{feature_3_description}}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Final CTA — ACTION (PAS Formula) -->
      <section class="py-16 bg-primary text-primary-foreground">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center max-w-3xl mx-auto">
            <h2 class="text-3xl font-bold sm:text-4xl mb-4">{{final_cta_headline}}</h2>
            <p class="text-xl mb-8 text-primary-foreground/90">{{final_cta_subheadline}}</p>
            <button class="bg-white text-primary px-8 py-4 rounded-lg text-xl font-semibold shadow-lg">
              {{final_cta_button_text}}
            </button>
            <p class="text-sm text-primary-foreground/75 mt-4">{{final_cta_disclaimer}}</p>
          </div>
        </div>
      </section>
    </main>

    <footer class="bg-muted border-t border-border">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <p class="text-center text-sm text-muted-foreground">
          &copy; {{current_year}} {{product_name}}. All rights reserved.
        </p>
      </div>
    </footer>
  </body>
</html>
```

## Variable Substitution Guide

```yaml
product_name: "{{PRODUCT_NAME}}"
key_benefit: "{{PRIMARY_VALUE_PROP}}"
seo_description: "Meta description for SEO (155 chars max)"
nav_cta_text: "{{NAV_CTA_TEXT | default: 'Get Started'}}"

hero_headline_v1: "Stop Struggling with [Problem]"
hero_headline_emphasis: "That Changes Today"
hero_subheadline_agitate: "Every day you delay costs you [specific consequence]."
social_proof_stat: "{{SOCIAL_PROOF_STAT}}"  # never fabricate -- use [PROOF NEEDED] until verified
primary_cta_text: "{{PRIMARY_CTA_TEXT}}"
secondary_cta_text: "{{SECONDARY_CTA_TEXT | default: 'See How It Works'}}"

features_headline: "Everything You Need to [Achieve Outcome]"
feature_1_title: "Feature Name"
feature_1_description: "Benefit-focused description of what this does for the user"

final_cta_headline: "Ready to [Get Specific Outcome]?"
final_cta_button_text: "Start My [Specific Outcome] Now"
final_cta_disclaimer: "{{TRIAL_DISCLAIMER | default: 'No credit card required'}}"
```

## Copy Formula Integration Example (PAS)

```html
<!-- PROBLEM: name the pain in their words, not yours -->
<h1 class="text-4xl font-bold">
  {{PAIN_HEADLINE}}
</h1>

<!-- AGITATE: stack the cost of inaction -->
<p class="text-xl text-muted-foreground">
  {{AGITATION_PARAGRAPH}}
</p>

<!-- SOLUTION: relief = clear ownership + first-week win -->
<section class="features">
  <!-- One-line owner: {{OWNERSHIP_CLAIM}} -->
  <!-- One-week win: {{FIRST_WEEK_WIN}} -->
</section>
```

## Hero Variant Pattern (fill per audience, do not ship unfilled)

Pick ONE variant per campaign -- mismatched hero copy is the largest
preventable source of bounce on a landing page.

```yaml
variant:
  audience: "{{AUDIENCE_SEGMENT}}"        # e.g. developer, founder, agency owner
  hook: "{{HOOK_LINE}}"                    # names the specific pain or desire for this audience
  proof: "{{PROOF_LINE}}"                  # a real, sourced number -- or [PROOF NEEDED]
  cta_pressure: "low | medium | high"      # information-first vs. decision-first
```

## Accessibility Compliance Checklist

- Semantic HTML5 structure (header, main, section, footer)
- Proper heading hierarchy (h1 -> h2 -> h3)
- Color contrast >= 4.5:1
- Focus indicators on all interactive elements
- Alt text on every image
- Keyboard navigation support
- Touch-friendly button sizes (44px minimum)

This template ensures every landing page generated from it meets a common
bar for performance, accessibility, and conversion structure -- fill the
`{{open_vars}}`, never ship the bracket placeholders.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[user_journey_n02]] | sibling | 0.40 |
| [[p06_vs_content_spec_n02]] | downstream | 0.30 |
| [[p09_env_brand_override_n02]] | upstream | 0.28 |
