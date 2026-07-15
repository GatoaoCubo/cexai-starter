"""CEXAI security assets -- redaction defaults and (future) auth material.

Home for cross-cutting security configuration that is data, not code. v0.3-W3b
ships ``default_redaction.yaml`` here: the documentation/override mirror of the
v1 span-attribute redaction pattern set (05_agno FR-009). The in-code tuple in
``cexai.governance.tracing.redaction`` (``DEFAULT_REDACTION_PATTERNS``) remains
the SOURCE OF TRUTH; the yaml is loaded LAZILY (PyYAML is not a hard dependency,
Article XIV offline) only when an operator points the loader at it.

This package registers ZERO kinds and adds no runtime dependency.

absorbs: 05_agno/observability-otel
"""
