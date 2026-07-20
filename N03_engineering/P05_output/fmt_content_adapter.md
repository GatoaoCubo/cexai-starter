---
id: p05_fmt_content_adapter
kind: formatter
8f: F6_produce
pillar: P05
version: "1.0.0"
created: "2026-04-08"
updated: "2026-04-08"
author: "n03_builder"
target_format: "multi"
input_type: "structured_data"
rule_count: 12
domain: "content_factory"
quality: null
title: "Content Adapter -- Multi-Format Formatter"
tags: [formatter, content-factory, multi-format, adapter, publishing]
tldr: "Universal adapter: CEX artifact (md+frontmatter) -> 5 publishable formats (clean md, HTML, PPTX outline, video script, podcast script)"
template_engine: "mustache"
pretty_print: true
escaping: "html"
encoding: "utf8"
streaming: false
keywords: [content-adapter, multi-format, publishing, conversion, pandoc, marp, typst]
density_score: 0.90
related:
  - p11_qg_response_format
  - bld_output_template_kind
  - bld_quality_gate_landing_page
  - bld_knowledge_card_knowledge_card
  - knowledge-card-builder
---

## Formatting Rules

| Name | Input Field | Transform | Pattern | Options |
|------|-------------|-----------|---------|---------|
| strip_frontmatter | raw_artifact | regex_remove | `^---[\s\S]*?---\n` | Remove YAML frontmatter block |
| normalize_headers | body_markdown | regex_replace | `^(#{1,6})\s+` -> normalized levels | Ensure H1 = title, H2 = sections |
| inject_brand_vars | body_markdown | template_expand | `{{BRAND_*}}` -> brand_config values | Resolve all mustache brand variables |
| extract_sections | body_markdown | split_by_header | `^## (.+)$` | Returns ordered list of {title, content} |
| to_clean_markdown | sections[] | reassemble | `# {title}\n\n{content}` per section | Strip internal refs, tables of quality scores |
| to_html | clean_markdown | pandoc_convert | `pandoc -f markdown -t html5 --standalone` | Add brand CSS inline, responsive meta |
| to_pptx_outline | sections[] | slide_transform | 1 section = 1 slide, bullets from paragraphs | Max 5 bullets/slide, speaker notes from detail |
| to_video_script | sections[] | temporal_map | section -> segment(duration, narration, visual_cue) | 90s total, hook/build/benefit/proof/CTA structure |
| to_podcast_script | sections[] | dialogue_map | section -> talking_point(host_a, host_b, duration) | 15-25 min, intro/body/outro, 2-host format |
| apply_brand_colors | html_output | css_inject | `--primary: {BRAND_COLORS.primary}` | Inject CSS custom properties from brand_config |
| sanitize_emojis | all_outputs | regex_replace | Unicode emoji -> ASCII tags | `[OK]`, `[WARN]`, `[!!]` per ascii-code-rule |
| validate_length | all_outputs | length_check | per-format max bytes | video: 2KB, podcast: 5KB, slides: 10KB, html: 50KB |

## Input Specification

Type: structured_data (CEX artifact)

Structure: Markdown file with YAML frontmatter. Expected fields in frontmatter: `id`, `kind`, `title`, `domain`, `tags`. Body is structured Markdown with H2 sections. Artifacts may contain mustache variables (`{{BRAND_*}}`), internal cross-references, quality tables, and Properties sections that should be stripped for publication.

Example:
```markdown
---
id: kc_example
kind: knowledge_card
title: "Example Knowledge Card"
domain: "meta"
tags: [example]
---

## Introduction
Content about the topic with {{BRAND_NAME}} references.

## Core Concepts
Detailed explanation with tables and examples.
```

## Output Specification

Format: multi (5 target formats from single input)

### Clean Markdown
```markdown
# Example Knowledge Card

## Introduction
Content about the topic with the brand name resolved.
```

### HTML
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Example Knowledge Card</title>
  <style>:root{--primary:#0D1117;--accent:#58A6FF}</style>
</head>
<body>
  <article><h1>Example Knowledge Card</h1></article>
</body>
</html>
```

### PPTX Outline
```yaml
slides:
  - title: "Example Knowledge Card"
    bullets: []
    speaker_notes: "Title slide -- introduce topic"
  - title: "Introduction"
    bullets: ["Content about the topic"]
    speaker_notes: "Expand on the introduction..."
```

### Video Script
```yaml
total_duration: 90
segments:
  - phase: hook
    duration: 5
    narration: "Did you know...?"
    visual_cue: "Title card with brand logo"
```

### Podcast Script
```yaml
total_duration: 1200
format: two_host
segments:
  - phase: intro
    duration: 60
    host_a: "Welcome to the show. Today we are covering..."
```

## Edge Cases

1. **Null values**: If a frontmatter field is missing, use empty string for template vars; log warning
2. **Empty strings**: Skip empty sections entirely (do not produce blank slides or script segments)
3. **Special characters**: HTML-escape `<>&"'` for HTML output; shell-escape backticks for script formats; preserve Markdown formatting in clean-md output
4. **Overflow**: If input exceeds 50KB, truncate at nearest section boundary and append "[truncated]" marker; video script enforces 90s hard cap by dropping lowest-priority segments

## Tool Chain

| Output Format | Primary Tool | Fallback | Config |
|---------------|-------------|----------|--------|
| Clean Markdown | built-in (regex + template) | -- | -- |
| HTML | Pandoc (`pandoc -f markdown -t html5`) | WeasyPrint (for PDF from HTML) | `--standalone --css brand.css` |
| PPTX | Marp CLI (`marp --pptx`) | Slide-design API | `--theme brand-theme` |
| Video Script | built-in (temporal mapper) | -- | content-factory video constraints |
| Podcast Script | built-in (dialogue mapper) | -- | content-factory podcast constraints |

## References

1. Format requirements + tool stack: content factory spec (this nucleus's P04_tools skills)
2. Brand variables for template expansion: `.cex/brand/brand_config.yaml`
3. Emoji sanitization rules: `.claude/rules/ascii-code-rule.md`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_response_format]] | downstream | 0.23 |
| [[bld_output_template_kind]] | related | 0.22 |
| [[bld_quality_gate_landing_page]] | downstream | 0.22 |
| [[bld_knowledge_card_knowledge_card]] | upstream | 0.21 |
| [[knowledge-card-builder]] | upstream | 0.21 |
