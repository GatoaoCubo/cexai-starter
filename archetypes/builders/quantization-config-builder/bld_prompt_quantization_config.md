---
kind: instruction
id: bld_instruction_quantization_config
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for quantization_config
quality: null
title: "Instruction Quantization Config"
version: "1.0.0"
author: wave1_builder_gen
tags: [quantization_config, builder, instruction]
tldr: "Step-by-step production process for quantization_config"
domain: "quantization_config construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F6_produce"
keywords: [quantization_config construction, instruction quantization config, quantization_config, builder, instruction, related artifacts, hard gate, gate confirm, downstream, bld_schema_quantization_config]
density_score: 0.85
related:
  - bld_schema_quantization_config
  - p09_qg_quantization_config
  - bld_knowledge_card_quantization_config
  - quantization-config-builder
  - bld_tools_quantization_config
---
## Phase 1: RESEARCH
1. Analyze target model weight distribution and dynamic range.
2. Evaluate bit-width trade-offs (INT8, FP8, NF4, INT4).
3. Compare compression algorithms (AWQ, GPTQ, bitsandbytes).
4. Assess hardware kernel compatibility (CUDA, ROCm, Triton).
5. Determine perplexity loss tolerance for specific tasks.
6. Identify optimal calibration dataset for scale estimation.

## Phase 2: COMPOSE
1. Initialize artifact structure using bld_output_template_quantization_config.md.
2. Map quantization parameters to types in bld_schema_quantization_config.md.
3. Define 'bits' parameter based on precision research.
4. Configure 'group_size' for weight-clustering density.
5. Specify 'quant_type' (e.g., 'nf4') per bld_schema_quantization_config.md.
6. Implement 'desc_act' settings for activation scaling (GPTQ only).
7. Set 'zero_point' and 'scale' calculation logic.
8. Define 'compute_dtype' for dequantization kernels.
9. Set id following naming convention from bld_config_quantization_config.md (p09_qc_*).

## Phase 3: VALIDATE
- [ ] Verify all keys strictly match bld_schema_quantization_config.md definitions.
- [ ] Check id follows p09_qc_* pattern (HARD gate H02).
- [ ] Confirm quant_type in {GPTQ, AWQ, GGUF, int8, int4, nf4} (HARD gate H04).
- [ ] Confirm bits in {2, 3, 4, 8} (HARD gate H05).
- [ ] Confirm calibration_dataset present for GPTQ/AWQ methods (HARD gate H07).
- [ ] Validate structural integrity against bld_output_template_quantization_config.md.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_quantization_config]] | downstream | 0.38 |
| [[p09_qg_quantization_config]] | downstream | 0.37 |
| [[bld_knowledge_card_quantization_config]] | upstream | 0.36 |
| [[quantization-config-builder]] | downstream | 0.35 |
| [[bld_tools_quantization_config]] | downstream | 0.35 |
