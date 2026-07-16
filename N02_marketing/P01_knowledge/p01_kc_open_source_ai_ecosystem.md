---
id: p01_kc_open_source_ai_ecosystem
kind: knowledge_card
primary_8f: F3_inject
8f: F3_inject
title: "Open Source AI Ecosystem 2026"
version: 1.0.0
quality: null
pillar: P01
nucleus: N02
tldr: "The 2026 open-source LLM-runtime landscape -- maps Ollama/vLLM/llama.cpp/HuggingFace/Together/Groq by hosting + pricing -- so a build can pick a runtime fast."
when_to_use: "Load when choosing a self-host vs cloud inference runtime, or sizing free-tier limits. Consult for 'which open-source LLM host fits this nucleus?'"
keywords: [ollama, vllm, llama.cpp, hugging-face, docker, wasm, inference-api, webassembly, model-hosting, self-hosted, groq, together-ai]
long_tails:
  - "which open-source LLM runtime should I self-host"
  - "compare Ollama vs vLLM vs llama.cpp for inference"
  - "what are the free-tier token limits for open inference APIs"
tags: [open_source, llm_runtime, ollama, vllm, llama_cpp, hugging_face, groq, inference, self_hosted, n02]
density_score: 1.0
updated: "2026-04-13"
related:
  - kc_subscription_tier
  - p01_kc_ai_saas_monetization
---

# Open Source AI Ecosystem 2026

The open source AI ecosystem in 2026 is characterized by rapid innovation and
diverse platforms. The six runtimes below cover the self-host -> cloud spectrum.

## Major Platforms (focus + hosting + pricing)

| Platform | Focus | Hosting | Pricing |
|----------|-------|---------|---------|
| **Ollama** | Lightweight, easy-to-deploy models | Cloud (Ollama Cloud), Self-hosted (Server) | Free tier (limited models); paid enterprise |
| **vLLM** | High-throughput inference optimization | Self-hosted (Docker), Cloud (AWS/GCP) | Open source + optional commercial support |
| **llama.cpp** | Portable, efficient execution | Self-hosted (Linux/macOS), WebAssembly | Completely free and open source |
| **Hugging Face** | Model sharing + collaboration | Cloud (Inference API), Self-hosted (Docker) | Free 100k tokens/mo; paid for higher limits |
| **Together.ai** | Enterprise-grade model hosting | Cloud (Together API), Self-hosted (custom) | Free 100k tokens/mo; business plans |
| **Groq** | Low-latency, high-throughput inference | Cloud (Groq API), Self-hosted (experimental) | Free 100k tokens/mo; production plans |

## How to use

You are a build agent sizing an inference runtime. To act on this card:

- Read the comparison table; shortlist by hosting mode (cloud vs self-hosted vs WASM).
- For edge/local nuclei, prefer `llama.cpp` or `ollama` (portable, free).
- For high-throughput batch inference, pick `vLLM`; for low-latency serving, `Groq`.
- Cross-reference n06_api_access_pricing before committing a paid tier.
- Never treat this card as config -- copy a runtime choice into a `model_provider` artifact (P02).

## Boundary

Conhecimento destilado, estatico, versionado. NAO eh instrucao, template, ou configuracao.


## 8F Pipeline Function

Primary function: **INJECT**

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_subscription_tier]] | sibling | 0.24 |
| n06_api_access_pricing | downstream | 0.21 |
| [[p01_kc_ai_saas_monetization]] | sibling | 0.20 |
