---
id: build
kind: instruction
pillar: P08
title: "Build"
description: "Build a CEXAI artifact via the 8F pipeline. Usage: /build <intent>"
version: "1.0.0"
author: cexai
quality: null
tags: [command, builder, 8f, lean, solo]
tldr: "Solo-operator build -- resolve intent, run 8F in-session, then compile + doctor. No dispatch, no grid."
domain: "tenant CEXAI"
related:
  - validate
  - guide
---

# /build -- create an artifact (8F)

Run the full 8F pipeline **in-session** to produce one artifact. You are the
solo operator of this tenant -- there is no nucleus dispatch and no grid.

## Steps

1. Parse the intent: `$ARGUMENTS`.
2. Run the 8F pipeline (it resolves the kind, then produces the artifact):
   ```bash
   python _tools/cex_8f_runner.py "$ARGUMENTS" --execute --verbose
   ```
   Optional overrides: `--kind <kind>` to skip classification, `--nucleus N0X`
   to target a nucleus, `--model <model>` to change the LLM.
3. If F7 returns PASS:
   - Compile: `python _tools/cex_compile.py <output_path>`
   - Health check: `python _tools/cex_doctor.py`  (Tier-1, repo-wide)
   - Optional peer score: `python _tools/cex_score.py <output_path> --dry-run`
4. If F7 FAILs after its retries: surface the F7 issues, propose manual fixes,
   then re-run step 2.

## Running an enabled capability

If the intent maps to one of this tenant's enabled capabilities (a dashboard
card or storefront asset), it runs through the headless product runtime
`run_capability(...)` in `_tools/cex_run_capability.py` -- the same entrypoint
the dashboard/API uses. Trigger it from the dashboard, or programmatically:

```python
from cex_run_capability import run_capability, Credential
result = run_capability(tenant_id, "<capability>", "$ARGUMENTS", credential)
```

## Examples
```
/build create a knowledge card about our return policy
/build write product copy for SKU CB3603
```

## Quality
8F enforces the gate (floor 8.0, target 9.0+). Never self-score --
`cex_score.py` assigns quality.
