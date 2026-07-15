---
name: bootstrap-on-first-run
description: Run interactive cex_bootstrap when brand_config.yaml is missing so a new clone never produces generic output before a brand identity is defined.
when:
  - `.cex/brand/brand_config.yaml` is missing or shows the unbootstrapped sentinel.
  - SessionStart fires in a fresh clone or a template-instantiated repo.
  - The user is about to invoke /build, /mission, or /grid in an unbootstrapped repo.
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.85
tags: [skill, autofire, bootstrap, brand, first-run, autowire, layer1]
related:
  - cex_bootstrap
  - brand-bootstrap
  - cex_template_init
  - p03_sp_brand_nucleus
  - p01_kc_cex_as_digital_asset
---

# Bootstrap on First Run

## When this fires
- `python _tools/cex_bootstrap.py --check` exits non-zero (brand not configured).
- A new clone, fork, or template instantiation has no `.cex/brand/brand_config.yaml`.
- The user is about to invoke build/mission/grid against an unbootstrapped repo.

## What to do
1. STOP before running the user's request. Generic output without brand context is wasted work.
2. Run `python _tools/cex_bootstrap.py --check` to confirm the unbootstrapped state.
3. If this is a dev repo (CEX itself), respect the existing `feedback_dev_repo_no_brand` memory and skip the prompts.
4. Otherwise ask the minimum 6 brand questions in natural conversation: brand name, one-sentence mission, 3 core values, voice/tone, ideal customer, monetization model.
5. Write answers to `/tmp/brand_init.yaml` (or `${TMP}/brand_init.yaml` on Windows) and run `python _tools/cex_bootstrap.py --from-file /tmp/brand_init.yaml`.
6. Confirm completion: "Brand X configured. CEX is ready." Then resume the original user request.
7. After bootstrap, the brand_config is auto-injected into all prompts via SessionStart hooks; do not re-prompt.

## Example
- User clones the CEX template, opens VSCode, types `build me a landing page`. SessionStart fires; bootstrap check fails. Skill takes over: 6 questions in 2 minutes capture brand identity. `cex_bootstrap --from-file` writes the config. THEN the landing-page-builder runs with the user's brand voice baked in.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| cex_bootstrap | downstream | 0.90 |
| brand-bootstrap | upstream | 0.85 |
| cex_template_init | sibling | 0.70 |
| p03_sp_brand_nucleus | upstream | 0.60 |
| p01_kc_cex_as_digital_asset | upstream | 0.55 |
