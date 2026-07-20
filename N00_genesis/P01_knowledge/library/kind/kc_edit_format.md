---
id: kc_edit_format
kind: knowledge_card
8f: F3_inject
title: Edit Format Specification
version: 1.0.0
quality: null
pillar: P01
tldr: "Standardized YAML format for LLM-to-host file change requests with validation rules"
when_to_use: "When an LLM agent needs a structured protocol to request file modifications from the host"
keywords: [change_type, file_path, content, metadata, permissions, utf-8 encoded, iso 8601 format, base64 encoding, normalized paths]
density_score: 1.0
related:
  - tpl_response_format
  - bld_output_template_edit_format
  - edit-format-builder
  - p05_output_validator
  - kc_c2pa_manifest
---

# LLM-to-Host File Change Format Specification

This document defines the standardized format for requesting file modifications to the host system. All change requests must follow this structure:

## 1. Base Structure
```yaml
change_type: [modify|create|delete]
file_path: "/absolute/path/to/file"
content: "new content"
metadata:
  reason: "change justification"
  timestamp: "ISO 8601 format"
```

## 2. Field Requirements
- **change_type** (required): Operation type (modify, create, delete)
- **file_path** (required): Absolute path with proper permissions
- **content** (required for modify/create): String content for modification
- **metadata** (optional): Additional context about the change

## 3. Special Cases
- **Delete Operation**: Omit content field
- **Binary Files**: Use base64 encoding for content
- **Permissions**: Include `permissions` field for file access control

## 4. Validation Rules
- All paths must be normalized
- Content must be UTF-8 encoded
- Metadata must include at least reason field
- Timestamp must be current UTC time

## 5. Example
```yaml
change_type: modify
file_path: "/home/user/config.yaml"
content: |
  format: yaml
  version: 2.1.0
metadata:
  reason: "Update configuration format to YAML"
  timestamp: "2023-10-15T14:48:00Z"
```

## 6. Error Handling
- Invalid format: Return 400 Bad Request
- Permission denied: Return 403 Forbidden
- File not found: Return 404 Not Found

## How to use

You are an LLM agent emitting a file-change request. Conform to this contract at
**F1 CONSTRAIN** so the host can validate and apply your edit deterministically.

- Always set `change_type`, `file_path` (absolute), and a `metadata.reason`.
- Omit `content` for deletes; base64-encode it for binary files.
- Normalize paths and UTF-8 the content before sending.
- Expect 400/403/404 on contract, permission, or missing-target failures.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_edit_format]] | downstream | 0.21 |
| [[edit-format-builder]] | downstream | 0.19 |
| [[kc_c2pa_manifest]] | sibling | 0.18 |
