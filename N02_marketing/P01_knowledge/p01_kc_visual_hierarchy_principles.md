---
id: p01_kc_visual_hierarchy_principles
kind: knowledge_card
primary_8f: F3_inject
8f: F3_inject
pillar: P01
title: "Visual Hierarchy Principles -- Conversion-Optimized Layout Patterns"
tags: [visual, hierarchy, design, conversion, layout, f-pattern, z-pattern, cta-placement]
tldr: "Visual hierarchy patterns that drive conversion: F-pattern and Z-pattern scanning, Gestalt grouping for benefit stacks, contrast ratios that pull eyes to CTAs, and whitespace as a persuasion tool. The difference between a page that gets read and one that gets scrolled past."
when_to_use: "Inject at F3 when laying out a landing page or component for conversion. Consult for 'where do I put the CTA and how do I guide the eye down the page?'"
quality: null
keywords: [font-size, margin-bottom, padding, typography scales, responsive designs, contrast ratios, visual flow, spacing, consistent scaling]
long_tails:
  - "how do I structure a landing page so the eye lands on the CTA"
  - "when to use F-pattern versus Z-pattern layout for conversion"
density_score: 0.97
---

# Visual Hierarchy Principles

This document outlines the principles for creating effective visual hierarchies
that move the eye toward the conversion action.

### How to use

```text
ROLE: You are the N02 visual frontend engineer laying out a page for conversion.
ACT:
- Pick a scanning pattern (F for text-dense, Z for sparse/hero) from the table below.
- Place the primary CTA on the pattern's terminal point; use contrast to make it the highest-salience element.
- Group benefits with Gestalt proximity; separate sections with whitespace, not borders.
- Apply the Implementation Guide type scale; verify contrast >= 4.5:1 against the page background.
```

## Scanning Patterns (where the eye goes)

| Pattern | Best for | Eye path | Put the CTA |
|---------|----------|----------|-------------|
| F-pattern | text-dense pages, blogs, feeds | top bar -> second line -> down the left edge | end of the first or second horizontal bar |
| Z-pattern | sparse landing/hero pages | top-left -> top-right -> diagonal -> bottom-right | bottom-right terminal of the Z |
| Gestalt grouping | benefit stacks, pricing tiers | clusters read as one unit by proximity | inside the visually dominant cluster |
| Center-stage | single-offer hero | radial from the focal element | directly under the focal headline |

## Core Principles

### 1. Size and Scale
- Use size to indicate importance
- Maintain consistent scaling ratios
- Use relative sizing for responsive designs

### 2. Color and Contrast
- Use color to highlight important elements
- Maintain sufficient contrast ratios
- Use color to create visual flow

### 3. Typography
- Use font size to indicate hierarchy
- Maintain consistent typography scales
- Use typography to guide visual flow

### 4. Spacing
- Use spacing to create visual separation
- Maintain consistent margin/padding ratios
- Use spacing to guide attention

## Implementation Guide

```css
h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

h2 {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

p {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}
```

## Best Practices

- Use a clear visual hierarchy for content
- Maintain consistent spacing and sizing
- Use color and typography to guide attention

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p06_is_responsive_breakpoints_n02 | downstream | 0.29 |
| n06_output_pricing_page | downstream | 0.29 |
| [[kc_responsive_layout_systems]] | sibling | 0.29 |
| p01_kc_typography_web | sibling | 0.28 |
