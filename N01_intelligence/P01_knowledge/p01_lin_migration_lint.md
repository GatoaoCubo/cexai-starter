---
id: p01_lin_migration_lint
kind: lineage_record
pillar: P01
target_artifact: cex_migration_lint
sources_count: 3
activities_count: 4
derivation_type: wasDerivedFrom
domain: knowledge-provenance
created: "2026-07-03"
updated: "2026-07-03"
author: n01_intelligence
quality: null
tags: [lineage_record, knowledge-provenance, golang-migrate, dbmate, alembic, mit, migration_lint, domain_d4, R-005]
tldr: "Provenance for _tools/cex_migration_lint.py: 3-way MECHANIC-ONLY transplant (golang-migrate pairing, dbmate version-parse, Alembic chain-integrity), all MIT, clean-room re-derivation, no source code copied. Dogfood-verified against real supabase/migrations/ (catches the known missing down_20260625000001_public_catalog.sql)."  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
related:
  - kc_oss_golang_migrate
  - kc_oss_dbmate
  - kc_oss_alembic
  - improvement_register
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_migration_lint, cex_rls_drift_check. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Lineage: cex_migration_lint

## Canonical Provenance Frontmatter Schema

Per the pattern in `p01_lin_graphify` / `p01_lin_open_design`, this record documents a
MULTI-SOURCE mechanic transplant (3 donors, not 1). Each donor's provenance is listed
separately below since each contributes a DIFFERENT mechanic to the same target file.

```yaml
provenance:
  target: "_tools/cex_migration_lint.py"  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
  sources:
    - source: "github.com/golang-migrate/migrate"
      license: "MIT"
      mechanic: "M1 paired up/down file convention"
      lineage_record: "p01_lin_migration_lint"
    - source: "github.com/amacneil/dbmate"
      license: "MIT"
      mechanic: "M2 leading-digit version-parse + version-as-sole-identity"
      lineage_record: "p01_lin_migration_lint"
    - source: "github.com/sqlalchemy/alembic"
      license: "MIT"
      mechanic: "M3 chain/bijection integrity (head detection principle)"
      lineage_record: "p01_lin_migration_lint"
  method: "clean_room_mechanic_transplant"
  derived: "2026-07-03"
```

## Entities

| ID | Type | Location | Retrieved |
|----|------|----------|-----------|
| golang_migrate_docs | prov:Entity | `raw.githubusercontent.com/golang-migrate/migrate/master/{LICENSE,MIGRATIONS.md,README.md,FAQ.md}` | 2026-07-03T00:00:00Z |
| dbmate_docs | prov:Entity | `raw.githubusercontent.com/amacneil/dbmate/main/{LICENSE,README.md}` | 2026-07-03T00:00:00Z |
| alembic_docs | prov:Entity | `raw.githubusercontent.com/sqlalchemy/alembic/main/{LICENSE,docs/build/tutorial.rst}` | 2026-07-03T00:00:00Z |
| supabase_migrations_live | prov:Entity | `supabase/migrations/*.sql` + `supabase/migrations/down/*.sql` (repo, at build time: 8 up, 7 down) | 2026-07-03T00:00:00Z |
| cex_migration_lint_tool | prov:Entity | `_tools/cex_migration_lint.py` | 2026-07-03T00:00:00Z |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| cex_migration_lint_tests | prov:Entity | `_tools/tests/test_cex_migration_lint.py` (11 pytest cases incl. live dogfood) | 2026-07-03T00:00:00Z |

## Activities

| ID | Label | Used | Generated | Agent | Timestamp |
|----|-------|------|-----------|-------|-----------|
| act_license_gate | license_verification | golang_migrate_docs, dbmate_docs, alembic_docs | 3x license_status=GREEN(MIT) | n01_intelligence | 2026-07-03T00:00:00Z |
| act_mechanic_extract | clean_room_mechanic_extraction | golang_migrate_docs, dbmate_docs, alembic_docs | kc_oss_golang_migrate, kc_oss_dbmate, kc_oss_alembic | n01_intelligence | 2026-07-03T00:00:00Z |
| act_transplant_build | mechanic_transplant_build | kc_oss_golang_migrate, kc_oss_dbmate, kc_oss_alembic | cex_migration_lint_tool | n01_intelligence | 2026-07-03T00:00:00Z |
| act_dogfood_verify | live_repo_dogfood | cex_migration_lint_tool, supabase_migrations_live | cex_migration_lint_tests (11/11 pass, catches real gap) | n01_intelligence | 2026-07-03T00:00:00Z |

Method: WebFetch docs (github MCP `get_file_contents` FAILED "Bad credentials," same
failure mode as prior waves, per protocol fell back to `raw.githubusercontent.com`) ->
license-gate-first (3x MIT confirmed BEFORE any mechanic extraction) -> clean-room
mechanic paraphrase into 3 `kc_oss_*` dossiers -> Python re-implementation of the 3
mechanics as static-analysis checks (M1 pairing, M2 duplicate-version, M3
bijection/head, plus a synthesized M4 idempotency lint) -> pytest suite including a
LIVE dogfood test against the real `supabase/migrations/` tree, which asserts the tool
catches the actual, currently-missing `down_20260625000001_public_catalog.sql` (11/11
tests pass). Zero network calls made BY the tool itself; zero DB touched; zero prod.

## Agents

| ID | Type | Role |
|----|------|------|
| n01_intelligence | nucleus | research + clean-room extraction + tool build + test author |
| golang_migrate_tool | tool | MIT donor of the M1 pairing mechanic (mechanics only, not adopted as runtime) |
| dbmate_tool | tool | MIT donor of the M2 version-parse mechanic (mechanics only, not adopted as runtime) |
| alembic_tool | tool | MIT donor of the M3 chain-integrity mechanic (mechanics only, not adopted as runtime) |

## Derivation Relations

- cex_migration_lint_tool wasDerivedFrom golang_migrate_docs (M1 mechanic)
- cex_migration_lint_tool wasDerivedFrom dbmate_docs (M2 mechanic)
- cex_migration_lint_tool wasDerivedFrom alembic_docs (M3 mechanic, principle-level)
- cex_migration_lint_tool wasGeneratedBy act_transplant_build
- cex_migration_lint_tool wasAttributedTo n01_intelligence
- cex_migration_lint_tests wasGeneratedBy act_dogfood_verify
- cex_migration_lint_tests used supabase_migrations_live
- kc_oss_golang_migrate wasGeneratedBy act_mechanic_extract
- kc_oss_dbmate wasGeneratedBy act_mechanic_extract
- kc_oss_alembic wasGeneratedBy act_mechanic_extract

## MIT Attribution

`Mechanic-level transplant (no source code copied) derived from: golang-migrate/migrate
(MIT, Copyright 2016 Matthias Kadenbach, 2018 Dale Hui) -- paired up/down file
convention; amacneil/dbmate (MIT, Copyright Adrian Macneil) -- leading-digit version
parse + version-as-sole-identity; sqlalchemy/alembic (MIT, Copyright 2009-2026 Michael
Bayer) -- down_revision chain-integrity principle (head/branch detection). All three
license texts confirmed GREEN via direct LICENSE-file fetch BEFORE any mechanic
extraction (clean-room protocol, NORTH_STAR sec 11).`

## Reversibility

This transplant is 100% reversible: `_tools/cex_migration_lint.py` and  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
`_tools/tests/test_cex_migration_lint.py` are net-new, additive files. Deleting both
fully undoes the build with zero blast radius on any other tool (it does not modify
`_tools/cex_rls_drift_check.py`, `cex_doctor.py`, `cex_score.py`, `cex_distill.py`, or  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
any file under `supabase/`).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_oss_golang_migrate | upstream | 0.60 |
| kc_oss_dbmate | upstream | 0.60 |
| kc_oss_alembic | upstream | 0.55 |
| improvement_register | related | 0.35 |
