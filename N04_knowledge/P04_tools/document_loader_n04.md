---
id: p04_loader_n04_knowledge
kind: document_loader
8f: F5_call
pillar: P04
nucleus: n04
title: "Document Loader -- N04 Multi-Format Ingestion Pipeline"
version: "1.0.0"
quality: null
tags: [document_loader, n04, ingestion, pdf, markdown, html, docx, repo, P04]
domain: knowledge management
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "Multi-format document loader for N04: handles PDF, Markdown, HTML, DOCX, code repos, and API sources. Each format has a dedicated extraction pipeline, chunking strategy, and metadata enrichment step before embedding and indexing."
keywords: [knowledge management, document loader, multi-format ingestion pipeline, handles pdf, code repos, and api sources, chunking strategy, document_loader, ingestion, markdown]
density_score: null
related:
  - p12_wf_rag_ingestion_n04
  - p06_td_document_types
  - p01_kc_document_loader
  - p09_rl_n04
---

# Document Loader: N04 Multi-Format Ingestion Pipeline

## Overview

N04's Knowledge Gluttony demands that EVERY document format be ingestible.
This loader is the entry point for all external knowledge into the semantic
corpus. It normalizes diverse formats into the `Document` type defined in
`type_def_document_types.md`.

---

## Supported Formats

| Format | Extractor | Chunking | Notes |
|--------|----------|---------|-------|
| Markdown (.md) | native | whole-doc for KC, heading-based for long | Primary format |
| PDF | PyMuPDF or pdfplumber | 512-token sliding, 128-overlap | Check OCR quality >= 0.7 |
| HTML/Web | BeautifulSoup | paragraph-based | Strip nav/footer/ads |
| DOCX | python-docx | heading-based | Preserve heading hierarchy |
| Code repo | tree-sitter | function/class-level | Include docstrings |
| JSONL/CSV | pandas | row-based or fixed 512-token | Flatten to text per row |
| API (REST) | httpx | response-level | Rate-limit aware |

---

## Per-Format Pipeline

### Markdown (Primary)

```python
def load_markdown(path: str) -> Document:
    content = open(path).read()
    frontmatter = parse_yaml_frontmatter(content)

    doc_type = (
        DocumentType.KNOWLEDGE_CARD if frontmatter.get("kind") == "knowledge_card"
        else DocumentType.ARTIFACT
    )

    return Document(
        id=uuid4(),
        type=doc_type,
        content=content,
        metadata={
            "kind": frontmatter.get("kind"),
            "pillar": frontmatter.get("pillar"),
            "nucleus": frontmatter.get("nucleus"),
            "path": path,
            "quality": frontmatter.get("quality"),
        }
    )
```

**Chunking**: whole document if < 8KB; heading-based split for larger docs.

### PDF

```python
def load_pdf(path: str, trust_level: int = 3) -> list[Document]:
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    text = "\n\n".join(pages)

    if count_ocr_artifacts(text) > 0.05:
        raise LowQualityExtractionError(f"OCR quality too low for {path}")

    chunks = sliding_window(text, size=512, overlap=128)

    return [Document(
        id=uuid4(),
        type=DocumentType.CHUNK,
        content=chunk,
        metadata={"source_type": "pdf", "path": path, "trust_level": trust_level}
    ) for chunk in chunks]
```

### Code Repository

```python
def load_repo(repo_path: str, language: str) -> list[Document]:
    parser = get_parser(language)
    files = glob_files(repo_path, f"*.{language}")

    documents = []
    for file in files:
        tree = parser.parse(open(file).read().encode())
        for node in extract_function_nodes(tree):
            documents.append(Document(
                id=uuid4(),
                type=DocumentType.CHUNK,
                content=node.text,
                metadata={
                    "source_type": "code",
                    "language": language,
                    "file": file,
                    "function": node.name
                }
            ))
    return documents
```

---

## Metadata Enrichment

After extraction, every document is enriched with:

| Field | Source | Notes |
|-------|--------|-------|
| `ingestion_date` | now() | ISO 8601 UTC |
| `corpus` | caller-specified | default: `cex_artifacts` |
| `trust_level` | config or caller | 1-5, affects retrieval weight |
| `language` | langdetect | ISO 639-1 code |
| `token_count` | tiktoken | cl100k_base tokenizer |
| `embedding_model` | config | see `embedding_config_knowledge.md` |

---

## Indexing After Load

Loading and indexing are two separate steps. Once documents are normalized
into `Document` objects (per-format pipeline above), the retrieval index is
built or refreshed with the real CLI this repo ships:

```bash
python _tools/cex_retriever.py --build
```

**Rate limits**: batch processor respects the ceilings declared in
`p09_rl_n04.md` (P09) -- separate budgets for embeddings vs. reranking vs.
freshness sweeps.

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|---------|
| `LowQualityExtractionError` | OCR quality < 0.7 | Skip document, log to `P07_evals/` |
| `EmbeddingDimensionMismatch` | Wrong model | Fail fast, check embedding config |
| `RateLimitExceeded` | API throttle | Exponential backoff: 1s, 2s, 4s |
| `DocumentTooLarge` | > 200K tokens | Reject, request chunked version |
| `DuplicateDetected` | Similarity >= 0.97 | Skip upsert, log dedup event |

---

## Integration

| Artifact | Role |
|---------|------|
| `input_schema_knowledge_query.md` | `corpus` field maps to loader target namespaces |
| `type_def_document_types.md` | Document type classification |
| `p09_rl_n04.md` | Rate/budget ceilings this loader must respect |
| `workflow_rag_ingestion.md` | End-to-end orchestration of this loader |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_wf_rag_ingestion_n04]] | downstream | 0.31 |
| [[p06_td_document_types]] | downstream | 0.30 |
| [[p01_kc_document_loader]] | upstream | 0.29 |
| [[p09_rl_n04]] | sibling | 0.27 |
