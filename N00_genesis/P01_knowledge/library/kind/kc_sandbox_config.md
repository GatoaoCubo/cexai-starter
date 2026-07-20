---
id: kc_sandbox_config
kind: knowledge_card
8f: F3_inject
title: Sandbox Configuration
version: 1.0.0
quality: null
pillar: P01
tldr: "Isolated code execution environment config with resource limits, security restrictions, and audit logging"
when_to_use: "When setting up a sandboxed runtime for secure, resource-bounded code execution and testing"
keywords: [runtime, sandboxed, networking, allowed_modules, safe_mode, audit_log, log_level, output_format]
density_score: 1.0
related:
  - sandbox-config-builder
  - kc_playground_config
  - playground-config-builder
  - bld_collaboration_sandbox_config
  - code-executor-builder
---

# Sandbox Configuration

Configures isolated code execution environments for secure testing. Key parameters:

## Environment Isolation
- `runtime`: Specify execution environment (e.g., `python3`, `node`)
- `sandboxed`: Boolean to enable/disable isolation
- `networking`: Control network access (none/readonly/readwrite)

## Resource Limits
- `cpu`: CPU allocation percentage (0-100)
- `memory`: Memory limit in MB
- `timeout`: Maximum execution time in seconds

## Security Settings
- `allowed_modules`: Whitelist of permitted modules/packages
- `safe_mode`: Enable strict security restrictions
- `audit_log`: Enable execution activity logging

## Logging
- `log_level`: Set logging verbosity (debug/info/warning/error)
- `output_format`: Specify output format (text/json)
- `max_log_size`: Maximum log file size in MB

Configuration ensures safe execution while maintaining performance and security boundaries.

## How to use this card

```text
Role: you are N05 configuring an isolated runtime for untrusted code execution.
Action: set the four groups in order -- pick the runtime + isolation + networking
mode, cap CPU/memory/timeout, whitelist allowed_modules under safe_mode, and turn
on audit_log + log_level. Default to networking:none and the tightest limits that
still let the workload run; widen only on a demonstrated need. Use this card to
FRAME a sandbox_config artifact for a code-executor or playground.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[sandbox-config-builder]] | downstream | 0.36 |
| [[kc_playground_config]] | sibling | 0.32 |
| [[playground-config-builder]] | downstream | 0.28 |
| [[bld_collaboration_sandbox_config]] | downstream | 0.27 |
| [[code-executor-builder]] | downstream | 0.27 |
