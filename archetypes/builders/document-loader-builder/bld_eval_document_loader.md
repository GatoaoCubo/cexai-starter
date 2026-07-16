---
id: p11_qg_document_loader
kind: quality_gate
pillar: P11
version: "1.0.0"
created: "2026-03-28"
updated: "2026-03-28"
author: "builder_agent"
domain: "file ingestion and chunking — transforms raw files into metadata-rich document chunks for RAG pipelines"
llm_function: GOVERN
quality: null
tags: [quality-gate, document-loader, P04, ingestion, chunking, RAG]
tldr: "Pass/fail gate for document_loader artifacts: format coverage, chunk strategy validity, metadata preservation, and body size limit."
8f: "F7_govern"
keywords: [file ingestion and chunking, format coverage, chunk strategy validity, metadata preservation, and body size limit, quality-gate, document-loader]
density_score: 0.90
title: "Gate: document_loader"
---
## Quality Gate

# Gate: document_loader
## Definition
| Field | Value |
|---|---|
| metric | document_loader artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: document_loader` |

## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_loader_[a-z][a-z0-9_]+$` | Uppercase, missing prefix, invalid chars |
| H03 | ID equals filename stem | id field differs from file name (without .md) |
| H04 | Kind equals literal `document_loader` | kind: loader or kind: ingester or any other value |
| H05 | Quality field is null | quality: 8.0 or any non-null value |
| H06 | All required fields present | Missing formats_supported, chunk_strategy, or output_format |

## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Format coverage | 1.0 | All target formats listed with MIME types; no format described without MIME |
| Chunk strategy documentation | 1.0 | chunk_size, overlap, and boundary rule all specified |
| Metadata extraction | 1.0 | source provenance always present; format-specific fields documented |
| Overlap handling | 0.5 | Overlap value set; boundary split behavior described |
| Encoding support | 0.5 | Encoding field set; non-UTF-8 fallback strategy mentioned |
| Error handling | 1.0 | Corrupt file / parse failure behavior described per format |

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
| conditions | Experimental loader for internal format research, not production RAG |
| approver | Author self-certification with comment explaining experimental scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — experimental loaders must reach >= 7.0 or be removed |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics) |

## Examples

# Examples: document_loader-builder

## Golden Example
**INPUT**: "Create document loader for PDF ingestion with semantic chunking for legal document RAG"

**OUTPUT**:
```yaml
---
id: p04_loader_pdf_legal
kind: document_loader
pillar: P04
version: 1.0.0
created: 2026-03-28
updated: 2026-03-28
author: builder_agent
name: "PDF Legal Document Loader"
formats_supported:
  - application/pdf
chunk_strategy: semantic
output_format: langchain_doc
chunk_size: 512
overlap: 64
encoding: utf-8
quality: null
tags: [document_loader, pdf, legal, RAG, P04]
tldr: "Loads PDF legal documents, semanticslly chunks by topic boundary, preserves page/section metadata for citation."
metadata_fields: [source, page, section, author, created_date]
---

## Overview
Loads PDF files from legal corpora using pdfplumber for layout-aware text extraction.
Applies semantic chunking to split at topic boundaries rather than arbitrary character counts,
preserving citation fidelity. Stage 1 of legal RAG pipeline: feeds langchain_doc chunks to retriever.

## Formats
| Format | MIME Type | Parser | Limitations |
|--------|-----------|--------|-------------|
| PDF (text) | application/pdf | pdfplumber | Scanned PDFs need OCR pre-processing |

## Chunking
- Strategy: semantic (embedding-based topic boundary detection)
- Chunk size: 512 tokens
- Overlap: 64 tokens
- Boundary rule: never split mid-sentence; respect section headings as hard splits

## Metadata
| Field | Type | Source | Notes |
|-------|------|--------|-------|
| source | string | file path | Required provenance for every chunk |
| page | int | pdfplumber page index | 1-based page number |
| section | string | heading detection regex | Nearest preceding heading |
| author | string | PDF metadata dict | May be null for unsigned docs |
| created_date | string | PDF metadata dict | ISO 8601 if available |
```

**WHY THIS IS GOLDEN**:
- H01-H10: all HARD gates pass (valid YAML, correct id pattern, kind literal, quality null, all required fields, MIME types, valid enum values, body under 2048 bytes)
- Specific parser (pdfplumber) with limitation noted (scanned PDFs)
- Semantic strategy justified for legal domain
- overlap: 64 = 12.5% of 512 — within best-forctice range

---

## Anti-Example
**INPUT**: "Create document loader for files"

**BAD OUTPUT**:
```yaml
---
id: loader_files
kind: document_loader
version: 1.0
quality: 7.5
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
