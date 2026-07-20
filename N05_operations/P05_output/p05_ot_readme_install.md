---
id: p05_ot_readme_install
kind: output_template
pillar: P05
quality: null
title: "Output Template: Readme Install"
version: 1.0.0
author: N05
tags: [output_template, operations, output]
tldr: "Installation guide template: system requirements, install steps, model presets, verify command."
domain: operations
created: "2026-07-20"
updated: "2026-07-20"
related:
  - bld_tools_model_provider
  - p01_kc_ollama_deployment_guide
  - p01_kc_cex_distribution_model
  - bld_sp_tools_software_project
---

# Installation & Requirements

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.9+ | 3.11+ |
| **RAM** | 8GB | 16GB+ |
| **VRAM** (local models) | 4GB | 8GB+ |
| **OS** | Windows 10, macOS 11, Linux | Latest |
| **Git** | 2.30+ | Latest |

## Installation

1. **Clone repository**
   ```bash
   git clone {{repo_url}}
   cd {{repo_dir}}
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   # OR if no requirements.txt:
   pip install anthropic google-generativeai openai ollama pyyaml
   ```

3. **Install a local model runtime** (optional, for offline models)
   ```bash
   # Windows: download the installer from the provider's site
   # macOS: brew install {{local_runtime}}
   # Linux: curl -fsSL {{local_runtime_install_url}} | sh
   ```

4. **Configure the system**
   ```bash
   python _tools/cex_bootstrap.py --interactive
   ```

5. **Initialize your brand**
   ```bash
   # In session:
   /init
   ```

## Model Presets

| Preset | Description | Services Required | Cost |
|--------|-------------|------------------|------|
| **Premium** | All cloud models | {{premium_providers}} | {{premium_cost}} |
| **Mid** | Single cloud provider | {{mid_provider}} | {{mid_cost}} |
| **Local** | Offline models | Local runtime (free) | $0 |
| **Fine-tuned** | Custom-trained | {{ft_provider}} | {{ft_cost}} |

## Verify Installation

```bash
python _tools/cex_doctor.py
```

Should show: `[OK] Health Check: All systems operational`

Ready to build knowledge systems with typed AI agents.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_model_provider]] | upstream | 0.35 |
| [[p01_kc_ollama_deployment_guide]] | upstream | 0.33 |
| [[p01_kc_cex_distribution_model]] | upstream | 0.26 |
| [[bld_sp_tools_software_project]] | upstream | 0.25 |
