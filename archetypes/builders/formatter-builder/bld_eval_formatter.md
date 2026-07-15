---
kind: quality_gate
id: p11_qg_formatter
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of formatter artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: formatter"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, formatter, output-format, transformation, P11]
tldr: "Validates formatter artifacts: transform rule completeness, escaping strategy, null-field handling, and output example presence."
domain: "formatter — output transformation rules converting structured data to readable or consumable representations"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.91
related:
  - formatter-builder
  - bld_instruction_formatter
  - bld_collaboration_formatter
  - bld_architecture_formatter
  - p05_fmt_artifact_creation_report
---
## Quality Gate

# Gate: formatter
## Definition
| Field     | Value |
|-----------|-------|
| metric    | composite score across SOFT dimensions |
| threshold | >= 7.0 to publish; >= 9.5 for golden |
| operator  | weighted average after all HARD gates pass |
| scope     | all artifacts where `kind: formatter` |
All HARD gates are AND-logic: one failure rejects the artifact regardless of SOFT score.
## HARD Gates
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Any YAML syntax error |
| H02 | ID matches `^p05_fmt_[a-z][a-z0-9_]+$` | Wrong format or namespace |
| H03 | ID equals filename stem (no extension) | Mismatch between id field and file name |
| H04 | Kind equals literal `formatter` | Any other value |
| H05 | `quality` field is null | Any non-null value |
| H06 | Required fields present: id, kind, pillar, version, created, updated, author, target_format, input_type, rule_count, domain, quality, tags, tldr | Any missing field |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| S01 | `tldr` <= 160 chars, names input type and output format | 0.10 | Accurate=1.0, vague=0.4, absent=0.0 |
| S02 | Tags list len >= 3, includes `formatter` and target format keyword | 0.05 | Both present=1.0, one=0.5 |
| S03 | Transform rules cover all declared input fields | 0.12 | All fields mapped=1.0, partial=0.5, none=0.0 |
| S04 | Input Specification section with structure and example | 0.10 | Present+example=1.0, spec only=0.5, absent=0.0 |
| S05 | Output Specification section with concrete formatted example | 0.12 | Present=1.0, absent=0.0 |
| S06 | Null/missing field behavior explicitly specified per rule | 0.10 | Explicit=1.0, implicit=0.3, absent=0.0 |
**Weight sum: 1.00**
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — reference artifact for formatter calibration |
| >= 8.0 | PUBLISH — pool-eligible; transforms and escaping documented |
| >= 7.0 | REVIEW — usable but missing null-field handling or output example |
| < 7.0  | REJECT — redo; likely missing transform rules or escaping strategy |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Formatter is a thin wrapper; transform logic lives in an external library with public docs |
| approver | Engineer who owns the consuming pipeline |
| audit trail | Required: external library link, pipeline name, approver handle |

## Examples

# Examples: formatter-builder
## Golden Example
INPUT: "Create a formatter to display product comparison data as a Markdown table"
OUTPUT:
```yaml
id: p05_fmt_product_comparison_table
kind: formatter
pillar: P05
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
target_format: "markdown"
input_type: "structured_data"
rule_count: 5
domain: "ecommerce_display"
quality: 8.9
tags: [formatter, markdown, product, P05, table, comparison]
tldr: "Formats product comparison data into Markdown table with price, rating, stock, and seller columns"
template_engine: "string_format"
pretty_print: true
escaping: "none"
encoding: "utf8"
locale: "pt-BR"
streaming: false
keywords: [product-table, comparison, markdown-formatter, ecommerce-display]
density_score: 0.87
```
## Formatting Rules
| Name | Input Field | Transform | Pattern | Options |
|------|-------------|-----------|---------|---------|
| title_col | product_title | stringify | `{value}` | max_length: 40, truncate: ellipsis |
| price_col | product_price | number_format | `R$ {value:,.2f}` | locale: pt-BR, swap_decimal: true |
| rating_col | product_rating | stringify | `{value}/5.0` | pad_right: 7 |
| stock_col | stock_status | stringify | `{value}` | uppercase: true |
| seller_col | seller_name | stringify | `{value}` | max_length: 25, truncate: ellipsis |
## Input Specification
Type: structured_data
Structure: list of product objects with title, price, rating, stock, seller fields.
Example:
```json
[{"product_title": "Kit Decoraction Sala", "product_price": 149.90, "product_rating": 4.7,
  "stock_status": "em estoque", "seller_name": "Loja Casa & Cia"}]
```
## Output Specification
Format: markdown
Example:
```markdown
| Produto | Preco | Avaliaction | Estoque | Vendedor |
|---------|-------|-----------|---------|----------|
| Kit Decoraction Sala | R$ 149,90 | 4.7/5.0 | EM ESTOQUE | Loja Casa & Cia |
```
## Template
Engine: string_format
```text
| Produto | Preco | Avaliaction | Estoque | Vendedor |
|---------|-------|-----------|---------|----------|
{rows}
```
## Edge Cases
- Null values: render as `-` placeholder in table cell
- Empty strings: render as `-` placeholder
- Special characters: pipe `|` escaped as `\|` in Markdown table cells
- Overflow: truncate with ellipsis at max_length per column
WHY THIS IS GOLDEN:
- quality: null (H05 pass) | id p05_fmt_ pattern (H02 pass) | kind: formatter (H04 pass)
- 21 fields present (H06 pass) | rule_count: 5 matches table (H07 pass)
- target_format: markdown valid enum (H08 pass) | input_type: structured_data valid (H08 pass)
- tldr: 89ch (S01 pass) | tags: 6 items (S02 pass) | 5 formatting rules (S03 pass)

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[formatter-builder]] | upstream | 0.42 |
| [[bld_instruction_formatter]] | upstream | 0.39 |
| [[bld_collaboration_formatter]] | downstream | 0.38 |
| [[bld_architecture_formatter]] | upstream | 0.37 |
| p05_fmt_artifact_creation_report | upstream | 0.36 |
