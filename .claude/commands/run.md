---
id: run
kind: instruction
pillar: P08
title: "Run"
description: "Bring up this tenant's 3 local apps -- storefront + admin + API. Usage: /run"
version: "1.0.0"
author: cexai
quality: null
tags: [command, run, apps, local, lean, solo]
tldr: "One launcher boots all 3 local apps -- storefront :3000, admin :3001, API :8000. The API auto-skips when Python deps are absent."
domain: "tenant CEXAI"
related:
  - build
  - validate
---

# /run -- bring up the local apps

Boot this tenant's three apps locally with one command -- the storefront, the
admin dashboard, and the API. Use the repo's own launcher; it resolves the repo
root, checks Node is on PATH, installs deps on first run, and starts each app.

## Steps

1. From the repo root, run the launcher for your OS:
   ```bash
   boot/run.ps1     # Windows (PowerShell)
   sh boot/run.sh   # Mac / Linux / WSL
   ```
2. Wait for the dev servers to come up (the first run does `npm install`).
3. Report the URLs -- this is also the last line the launcher prints:
   ```
   Site http://localhost:3000/t/<this tenant>  |  Admin http://localhost:3001  |  API http://localhost:8000
   ```
   The launcher has this tenant's slug baked in, so the `/t/<slug>` it prints is
   already correct -- never hardcode a brand here, read it from the repo.

## The API is optional

`dashboard_api` (:8000) only starts if its Python deps import cleanly. With no
Python environment it is **auto-skipped** and the two web apps still run on
fixtures. To enable the API, install the deps and re-run the launcher:
```bash
pip install -r apps/dashboard_api/requirements.txt
```

## Manual fallback

If the launcher will not run, start the two web apps by hand (one terminal each):
```bash
cd apps/public_site   && NEXT_PUBLIC_FIXTURES=1 npm run dev                           # :3000
cd apps/dashboard_web && NEXT_PUBLIC_FIXTURES=1 NEXT_PUBLIC_TENANT=<slug> npm run dev  # :3001
```
`<slug>` is this tenant's slug (see `brand/brand_config.yaml`). `NEXT_PUBLIC_FIXTURES=1`
serves the bundled sample data, so the apps render with no live backend.

## Notes
- Node.js 18.17+ must be on PATH -- both web apps need it.
- Stop the apps with Ctrl-C (or close the spawned windows on Windows).
