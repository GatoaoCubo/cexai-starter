---
id: validate
kind: instruction
pillar: P08
title: "Validate"
description: "Tier-1 health check of your CEXAI brain. Usage: /validate"
version: "1.0.0"
author: cexai
quality: null
tags: [command, validation, doctor, lean, solo]
tldr: "Tier-1 validation = cex_doctor only. Structure, density, frontmatter and wiring across the tenant."
domain: "tenant CEXAI"
related:
  - build
  - simplify
---

# /validate -- Tier-1 health check (doctor)

Run the builder health check across your tenant's artifacts. This is the
**only** validation tier in a lean tenant -- it is `cex_doctor`, nothing else.

## Usage
```bash
python _tools/cex_doctor.py            # diagnose (default: check)
python _tools/cex_doctor.py summary    # condensed report
python _tools/cex_doctor.py --fix      # diagnose + auto-fix naming issues
```

`cex_doctor` is repo-wide: it scans every artifact in the tenant rather than a
single file. It checks size, density, frontmatter, naming and wiring, and exits
non-zero when a hard gate fails.

## Steps
1. Run `python _tools/cex_doctor.py`.
2. Report the summary: FAIL count (blocking), WARN count (advisory), and any
   flagged files.
3. If there are naming FAILs, offer `--fix` to auto-correct them.
4. Re-run until doctor is 0 FAIL before you commit.

## Severity
| Doctor state | Meaning | Action |
|--------------|---------|--------|
| FAIL | hard gate violated | block -- must fix |
| WARN | soft cap / low density | log, fix when convenient |
| PASS | healthy | done |
