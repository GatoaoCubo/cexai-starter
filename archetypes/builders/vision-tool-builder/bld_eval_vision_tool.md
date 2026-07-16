---
kind: quality_gate
id: p11_qg_vision_tool
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of vision_tool artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: vision_tool"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, vision-tool, P04, image, ocr, confidence-threshold]
tldr: "Pass/fail gate for vision_tool artifacts: input type coverage, capability documentation, provider mapping, confidence thresholds, and output schema."
domain: "visual analysis tool definition — image processrs with declared input types, capabilities, providers, and structured output"
created: "2026-03-28"
updated: "2026-03-28"
8f: "F7_govern"
keywords: [visual analysis tool definition, and structured output, input type coverage, capability documentation, provider mapping, confidence thresholds, and output schema]
density_score: 0.90
related:
  - bld_schema_vision_tool
---
## Quality Gate

# Gate: vision_tool
## Definition
| Field | Value |
|---|---|
| metric | vision_tool artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: vision_tool` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_vision_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, missing prefix, or spaces |
| H03 | ID equals filename stem | `id: p04_vision_ocr` but file is `p04_vision_document.md` |
| H04 | Kind equals literal `vision_tool` | `kind: tool` or `kind: image_tool` or any other value |
| H05 | Quality field is null | `quality: 8.5` or any non-null value |
| H06 | All required fields present | Missing any of: input_types, capabilities, output_format, providers |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Input type coverage | 1.0 | All meaningful input formats documented with encoding details and size limits |
| Capability documentation | 1.5 | Each capability has description, confidence range, and output schema |
| Provider mapping | 1.0 | Each provider listed; capabilities mapped to providers that support them |
| Confidence threshold declared | 1.0 | confidence_threshold present and justified; not left as implicit default |
| Supported formats declared | 1.0 | supported_formats list present; provider-specific format limitations noted |
| Output schema completeness | 1.5 | Output format section shows JSON envelope with field names and types |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Internal prototype used only during provider evaluation, never shipped to production |
| approver | Author self-certification with comment explaining prototype-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — prototypes must be promoted to >= 7.0 or removed from repo |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H10 (unmatched capabilities break validation pipeline) |

## Examples

# Examples: vision-tool-builder
## Golden Example
INPUT: "Create an OCR tool for extracting text from scanned documents"
OUTPUT:
```yaml
id: p04_vision_document_ocr
kind: vision_tool
pillar: P04
version: "1.0.0"
created: "2026-03-28"
updated: "2026-03-28"
author: "builder_agent"
name: "Document OCR Extractor"
```
## Overview
Extracts text content, layout structure, and tabular data from scanned documents and images.
Used by document processing pipelines, data entry automation, and archiving systems.
## Input Types
### base64
Inline image payload encoded as base64 string. Max 10MB decoded.
Encoding: UTF-8 base64 string, optionally prefixed with `data:{mime};base64,`.
### file_path
Absolute or relative path to image file on local filesystem.
Supported formats: png, jpg, jpeg, tiff, pdf, bmp. PDF extracts all pages.
### url
HTTP/HTTPS URL pointing to publicly accessible image or PDF.
Timeout: 30s. Max redirect depth: 3. Requires content-type image/* or application/pdf.
## Capabilities
### text_extraction
Extracts all readable text from the image in reading order.
Confidence range: 0.0–1.0. Results filtered at confidence_threshold (default 0.85).
Output: `{text: string, blocks: [{text, confidence, bbox: {x,y,w,h}, page}]}`
### layout_detection
Detects structural regions: header, footer, paragraph, title, list, figure, table.
Output: `{regions: [{type, bbox, text, confidence}]}`
### table_extraction
Detects and extracts tabular data with row/column structure preserved.
Output: `{tables: [{rows: [\[cell_text\]], headers: [string], bbox, confidence}]}`
## Output Format
All capabilities return JSON. Top-level envelope:
`{capability: string, pages: int, processing_ms: int, results: {…capability_schema}}`
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_vision_ pattern (H02 pass)
- kind: vision_tool (H04 pass)
- input_types, capabilities, output_format, providers all present (H06 pass)
## Anti-Example
INPUT: "Create image analyzer"
BAD OUTPUT:
```yaml
id: image-analyzer
kind: tool
pillar: tools
name: Image Analyzer
capabilities: [analyze]
quality: 9.0
tags: [image]
```
Analyzes images.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
