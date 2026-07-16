---
id: p01_kc_tailwind_patterns_n02
kind: knowledge_card
primary_8f: F3_inject
8f: F3_inject
pillar: P01
title: "Tailwind CSS Patterns -- Production Design System Recipes"
tags: [tailwind, patterns, design-system, utility-first, responsive, dark-mode, components]
tldr: "Battle-tested Tailwind CSS patterns for N02 output: responsive grid compositions, dark mode token switching, component variant APIs via CVA, animation utilities for micro-interactions, and the 60-30-10 color distribution rule enforced via design tokens."
when_to_use: "Inject at F3 when generating Tailwind HTML/components. Consult for 'what responsive grid / dark-mode / variant pattern should this component use?'"
quality: null
keywords: [utility classes, component-based design, responsive breakpoints, mobile-first approach, custom variants, design system library]
long_tails:
  - "what tailwind pattern should I use for a responsive two-column layout"
  - "how do I switch dark mode and build component variants in tailwind"
density_score: 0.97
---

# Tailwind Patterns

This document outlines best practices for using Tailwind CSS in design systems.

### How to use

```text
ROLE: You are the N02 frontend engineer generating Tailwind markup.
ACT:
- Pick the layout recipe from the Pattern Recipes table for the composition you need.
- Apply dark: variants for every color; switch via the .dark class on a root ancestor.
- Express component variants as a single class list per state (CVA-style), not inline overrides.
- Apply the 60-30-10 color split via tokens (dominant surface / secondary / accent CTA).
```

## Pattern Recipes

| Pattern | Use it for | Class skeleton |
|---------|-----------|----------------|
| Responsive grid | card/benefit stacks | `grid gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3` |
| Dark-mode token switch | theme support | `bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100` |
| Component variant (CVA) | buttons/badges | one class list per `variant` x `size`, composed not overridden |
| Micro-interaction | hover/focus polish | `transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary` |
| 60-30-10 color split | visual balance | 60% surface tokens, 30% secondary, 10% accent on the CTA only |

## Core Principles

### 1. Utility-First Approach
- Use utility classes for styling
- Maintain a consistent class naming convention
- Avoid excessive class nesting

### 2. Component-Based Design
- Create reusable components
- Use component-specific utility classes
- Maintain component state separately

### 3. Responsive Design
- Use responsive breakpoints
- Implement mobile-first approach
- Use utility classes for different screen sizes

## Implementation Guide

```html
<div class="container mx-auto p-4">
  <div class="flex flex-wrap">
    <div class="w-full md:w-1/2 p-2">
      <div class="bg-white rounded shadow">
        <!-- Content -->
      </div>
    </div>
    <div class="w-full md:w-1/2 p-2">
      <div class="bg-white rounded shadow">
        <!-- Content -->
      </div>
    </div>
  </div>
</div>
```

## Best Practices

- Keep utility classes organized
- Use custom variants for specific use cases
- Maintain a design system library

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p05_oval_style_guide_n02 | downstream | 0.52 |
| landing_page_petshop_crm | downstream | 0.51 |
| p01_kc_tailwind_patterns | sibling | 0.50 |
| landing_page_pet-shop-crm | downstream | 0.48 |
| p05_oval_landing_page_template_n02 | downstream | 0.48 |
