---
kind: quality_gate
id: p09_qg_sandbox_config
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for sandbox_config
quality: null
title: "Quality Gate Sandbox Config"
version: "1.1.0"
author: n05_ops
tags:
  - "sandbox_config"
  - "builder"
  - "quality_gate"
tldr: "Quality gate for sandbox_config: 8 HARD gates (isolation, limits, timeout, network), 5D SOFT scoring sum=1.0"
domain: "sandbox_config construction"
created: "2026-04-13"
updated: "2026-04-13"
last_reviewed: "2026-04-18"
8f: "F7_govern"
keywords:
  - "sandbox_config construction"
  - "quality gate sandbox config"
  - "quality gate for sandbox_config"
  - "hard gates"
  - "d soft scoring sum"
  - "sandbox_config"
  - "builder"
density_score: 0.90
---
## Quality Gate
## Definition
| metric | threshold | operator | scope |
|--------|-----------|----------|-------|
| Isolation Level | High | >= | Sandbox Environment |
| Resource Limits | Defined | required | CPU + RAM + disk + timeout |
| Quality Score | 8.0 | >= | Publish threshold |
## HARD Gates
| ID | Check | Fail Condition |
|----|-------|---------------|
| H01 | YAML valid | Invalid YAML syntax |
| H02 | ID matches pattern | ID does not match `^p09_sb_[a-zA-Z0-9_-]+$` (schema pattern) |
| H03 | kind matches | kind != `sandbox_config` |
| H04 | Resource limits present | Missing any of: cpu, memory, disk, timeout |
| H05 | Network policy defined | No network isolation policy specified |
| H06 | Filesystem scope defined | No filesystem root or read/write boundaries specified |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D1 | Resource Completeness | 0.25 | CPU+RAM+disk+timeout all defined=1.0; missing 1=0.7; missing 2+=0.3 |
| D2 | Isolation Strength | 0.25 | Namespace+seccomp+MAC=1.0; namespace only=0.7; none=0.2 |
| D3 | Network Policy | 0.20 | Air-gapped or whitelist=1.0; partial restrict=0.6; unrestricted=0.0 |
| D4 | Filesystem Scope | 0.15 | Read-only root+ephemeral scratch=1.0; read-only only=0.7; writable root=0.3 |
| D5 | Auditability | 0.15 | Audit log + timeout enforcement=1.0; partial=0.6; none=0.2 |
**Weight sum: 0.25+0.25+0.20+0.15+0.15 = 1.00**
## Actions
| Score | Action |
|-------|--------|
| GOLDEN >=9.5 | Auto-approve, production-ready |
| PUBLISH >=8.0 | Manual review, staging deploy |
| REVIEW >=7.0 | Peer review required, no deployment |
| REJECT <7.0 | Block deployment, fix required |
## Bypass
| conditions | approver | audit trail |
|------------|----------|-------------|
| Security exception with compensating controls | Security Lead | SEC ticket required |
| Critical hotfix with temporary relaxed limits | SRE Lead | Incident ticket required |
| Compliance override (regulatory requirement) | Legal + CISO | Signed waiver required |
## Examples
## Golden Example 1: E2B Cloud Sandbox (AI Code Execution)
```yaml
---
id: p09_sb_ai_code_runner
kind: sandbox_config
pillar: P09
title: "AI Code Runner -- E2B Firecracker Sandbox"
version: "1.0.0"
platform: e2b
sandbox_type: isolated
```
**Why it passes:** CPU+RAM+disk+timeout all defined. Air-gapped network. Read-only root + ephemeral
scratch. Firecracker microVM provides VM-level isolation. All capabilities dropped. Seccomp enabled.
---
## Golden Example 2: Docker + gVisor Sandbox (Untrusted Code)
```yaml
---
id: p09_sb_untrusted_exec
kind: sandbox_config
pillar: P09
title: "Untrusted Code Execution -- Docker + gVisor"
platform: gvisor
sandbox_type: isolated
---
```
**Why it passes:** gVisor intercepts all syscalls via user-space kernel (strongest isolation).
Egress whitelist restricts outbound. Timeout enforced. All caps dropped.
---
## Anti-Example 1: Missing Timeout + Open Network
```yaml
---
id: p09_sb_broken
kind: sandbox_config
platform: docker
---
resource_limits:
  cpu: 4
```
**Why it fails:** H04 FAIL (missing timeout). H05 FAIL (network unrestricted). H06 FAIL
(writable root filesystem). H07 FAIL (no seccomp, no MAC). Resource limits too large.
---
## Anti-Example 2: nsjail Without Seccomp (Incomplete Isolation)
```yaml
---
id: p09_sb_incomplete_nsjail
kind: sandbox_config
platform: nsjail
---
resource_limits:
  cpu: 1
```
**Why it fails:** H07 FAIL -- nsjail without seccomp leaves full kernel syscall surface exposed.
Even with namespace isolation, unprivileged syscalls can exploit kernel vulnerabilities.
Fix: add `seccomp_profile: default` or custom nsjail `seccomp_string` policy.
---
## Golden Example 3: Daytona Cloud Sandbox (Remote Dev Environment)
```yaml
---
id: p09_sb_daytona_dev
kind: sandbox_config
pillar: P09
title: "Cloud Dev Environment -- Daytona Cloud Workspace"
version: "1.0.0"
backend_type: daytona
sandbox_type: isolated
```
**Why it passes:** Daytona provides VM-level workspace isolation with built-in auto-hibernate.
`backend_type: daytona` is a cloud runtime. Egress whitelist restricts to known registries.
Timeout enforced at 3600s with 10-minute idle hibernate (integrates with `hibernation_policy` kind).
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
