---
id: kc_terminal_backend
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n00
title: "Knowledge Card: terminal_backend"
version: 1.0
quality: null
tags: [terminal_backend, p09, execution_environment, backend, runtime]
tldr: "P09 config declaring the execution environment for agent terminal sessions across 6 backends"
when_to_use: "When selecting where agent code runs -- local, Docker, SSH, Daytona, Modal, or Singularity"
keywords: [p09 config artifact, yaml file, runc/gvisor, ssh_key, api_token, hibernation, serverless, hpc quota]
density_score: 0.95
upstream_source: null
related:
  - n00_terminal_backend_manifest
  - bld_schema_terminal_backend
  - terminal-backend-builder
  - bld_instruction_terminal_backend
  - p09_qg_terminal_backend
---

## Definition

`terminal_backend` is a P09 config artifact that declares the execution environment where
agent-invoked terminal sessions, CLI tools, and code runs. It abstracts over six supported
backends so nucleus operators switch execution targets by swapping a YAML file, not patching code.

## Six Supported Backends

| Backend | Type | Auth | Serverless | Hibernation | Billing |
|---------|------|------|------------|-------------|---------|
| `local` | Bare metal / host OS | none | no | no | free |
| `docker` | Container (runc/gVisor) | none | no | no | free/infra |
| `ssh` | Remote host via SSH | ssh_key | no | no | infra |
| `daytona` | Cloud dev environment | api_token | yes | yes | per_task |
| `modal` | Serverless GPU/CPU | api_token | yes | no | per_second |
| `singularity` | HPC container (Apptainer) | none/ssh | no | no | HPC quota |

## Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| `backend_type` | enum | Selects from 6 supported backends |
| `serverless` | bool | Whether backend spawns on demand (no persistent VM) |
| `hibernation_capable` | bool | Whether idle backend can hibernate to cut cost |
| `auth.method` | enum | none, ssh_key, api_token, oauth |
| `auth.secret_ref` | string | Pointer to `secret_config` artifact |
| `limits.timeout_seconds` | int | Max session lifetime before forced teardown |
| `cost_model.billing` | enum | free, per_second, per_task, subscription |

## Boundaries

| Confused with | Why it is different |
|---------------|---------------------|
| `sandbox_config` | sandbox_config = security isolation (seccomp, namespaces, capabilities); terminal_backend = WHERE code runs (execution target selection) |
| `env_config` | env_config = environment variables injected into the session; terminal_backend = the execution target itself |
| `deployment_manifest` | deployment_manifest = production ship spec; terminal_backend = dev/runtime execution layer |
| `runtime_rule` | runtime_rule = timeout/retry/limit rules applied during execution; terminal_backend = the backend those rules apply to |

## Dialectic: sandbox_config + terminal_backend

The two kinds are complementary, not interchangeable:
- `terminal_backend` answers: WHERE does the code run? (local, docker, modal...)
- `sandbox_config` answers: HOW is that run isolated? (namespaces, seccomp, capabilities)

A fully governed execution pipeline uses BOTH: terminal_backend selects the target;
sandbox_config wraps the execution in security isolation.

## Builder

`archetypes/builders/terminal-backend-builder/` (13 ISOs)

```bash
python _tools/cex_8f_runner.py "configure modal serverless backend" \
  --kind terminal_backend --execute
```

## Examples

### Local (dev default)
```yaml
id: p09_tb_local
kind: terminal_backend
backend_type: local
serverless: false
hibernation_capable: false
auth:
  method: none
limits:
  timeout_seconds: 3600
cost_model:
  billing: free
```

### Modal (GPU serverless)
```yaml
id: p09_tb_modal
kind: terminal_backend
backend_type: modal
serverless: true
hibernation_capable: false
auth:
  method: api_token
  secret_ref: p09_secret_modal_api
limits:
  cpu_cores: 8
  memory_gb: 16
  timeout_seconds: 900
cost_model:
  billing: per_second
  estimated_usd_per_hour: 0.72
```

### SSH (private cluster)
```yaml
id: p09_tb_ssh_gpu_cluster
kind: terminal_backend
backend_type: ssh
serverless: false
hibernation_capable: false
auth:
  method: ssh_key
  secret_ref: p09_secret_ssh_cluster_key
limits:
  cpu_cores: 32
  memory_gb: 128
  timeout_seconds: 86400
cost_model:
  billing: subscription
  estimated_usd_per_hour: 0.0
```

## Integration Points

- `secret_config` (P09): `auth.secret_ref` points to a secret_config artifact
- `sandbox_config` (P09): wraps terminal_backend session for security isolation
- `env_config` (P09): environment variables injected into the backend session
- `runtime_rule` (P09): timeout/retry rules governing session behavior
- `hibernation_policy` (P09): controls auto-hibernate for cost savings on idle backends

## Configuration Convention

Backends are configured in the `environments/` directory of the agent workspace.
No code changes are required to switch backends -- only YAML swap.

```
environments/
  local.yaml        -> terminal_backend (backend_type: local)
  docker.yaml       -> terminal_backend (backend_type: docker)
  modal.yaml        -> terminal_backend (backend_type: modal)
  daytona.yaml      -> terminal_backend (backend_type: daytona)
  ssh_cluster.yaml  -> terminal_backend (backend_type: ssh)
  singularity.yaml  -> terminal_backend (backend_type: singularity)
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_terminal_backend]] | downstream | 0.61 |
| [[terminal-backend-builder]] | downstream | 0.61 |
| [[bld_instruction_terminal_backend]] | downstream | 0.57 |
| [[p09_qg_terminal_backend]] | downstream | 0.55 |
