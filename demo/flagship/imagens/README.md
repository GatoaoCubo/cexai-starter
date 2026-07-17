# codexa-imagens (CODEXA_V2)

> **Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei).**
>
> Multi-runtime bundle: Custom GPT FULL + ChatGPT Projects ENXUTO + Claude
> Projects + Gemini Gems. Same agent identity, same 3 universal rules, same
> 4-block output -- tool surfaces differ by runtime.

## What this is

`codexa-imagens` is a standalone product-photo prompt engineering agent. It
transforms a typed product description (or chat-uploaded photo) into:

- Primary positive prompt + 3 variations + negative prompt in 3 engines:
  Midjourney, DALL-E, Stable Diffusion (always EN).
- A 9-scene grid (HERO TRUST, SECOND ANGLE, FEATURE HIGHLIGHT, DETAIL
  ARRANGEMENT, IN CONTEXT, BENEFIT MACRO, EMOTIONAL PEAK, LIFESTYLE DREAM,
  MARKETPLACE READY).
- Brazilian marketplace TOS compliance scoring (Mercado Livre, Amazon BR,
  Shopee, Magalu, generic).
- **NEW (CEXAI value-add)**: C2PA AI-content provenance disclosure block
  for marketplace AI-disclosure compliance.

## Runtime variants

| Variant | Folder | When |
|---|---|---|
| **Custom GPT FULL** | `knowledge/` + `00_instructions.md` + `SETUP_pt-br.md` | ChatGPT Plus/Team/Enterprise; full 12 pillars; DALL-E native |
| **ChatGPT Projects ENXUTO** | `projects_free/` + `SETUP_chatgpt_projects.md` | ChatGPT Free; 5 pillars (P06-P12 folded); DALL-E if plan allows |
| **Claude Projects** | `claude/` + `claude/.mcp.json` + `SETUP_claude_projects.md` | Strongest -- all 5 upgrade lanes via MCP (L1-L5) |
| **Gemini Gems** | `gemini/` + `SETUP_gemini_gems.md` | Strongest native -- L1+L2 ship by default, Imagen 3 primary |

## Per-runtime fidelity (manifest.yaml)

```yaml
fidelity:
  bundle_level: full
  custom_gpt_full: "full (DALL-E native, no vision lane, no grid lane)"
  chatgpt_projects_enxuto: "full (same as Custom GPT, 5-file format)"
  claude_projects: "full (all 5 upgrade lanes available via MCP)"
  gemini_gems: "full (L1+L2 native, no MCP needed)"
```

See `manifest.yaml` for the complete per-runtime capability table.

## 6 lanes (P04 -- audit section 3)

- **Primary** (DALL-E nativo / Imagen 3 / external) -- degrade-never default.
- **L1 Gemini Pro Vision** -- visao confiavel da foto enviada. Native in Gemini Gems; via MCP in Claude Projects.
- **L2 Gemini 2.5 Flash Image grid** -- grid 3x3 9-em-1 em 1 chamada. Native in Gemini Gems; via MCP in Claude Projects.
- **L3 ComfyUI local** -- pipeline local com workflow custom (CEXAI factory parity). Only Claude Projects via MCP.
- **L4 Qwen3-VL Ollama** -- visao local free (no API key). Only Claude Projects via MCP.
- **L5 Firecrawl** -- scrape product URL for **style calibration only**, never as source of product attributes. All runtimes via HTTP API.
- **L6 Code interpreter** -- dimension/format compliance check. Native in Custom GPT / ChatGPT Projects / Gemini Gems / Claude Projects sandbox.

ALL lanes carry `optional: true` + `fallback_to: dalle_native` (or
`text_extraction` / `paste_intake` for non-image lanes). Degrade-never:
missing env = silent fallback. User always gets a deliverable.

## 24 CEXAI typed kinds

This bundle ships 24 distinct typed CEXAI builder kinds across 12 pillars (see
`manifest.yaml#cexai_typed_kinds`). Highlights:

- **P10 `c2pa_manifest`** -- NEW CEXAI value-add. AI-generated image provenance
  text block in output. Not in original codexa-core. Compliance-ready for 2026+
  marketplace AI-disclosure requirements.
- **P09 `marketplace_app_manifest`** -- 4-runtime distribution declaration.
- **P03 `multimodal_prompt`** -- typed binding for upload-analysis prompts.
- **P11 3x `guardrail` + `content_filter` + `safety_policy`** -- typed
  anti-hallucination + IP/copyright protection.
- **P12 `dag` + `crew_template`** -- typed DAG + optional 3-role crew variant.

## 3 universal rules (CONVENTION.md verbatim)

1. **Anti-hallucination 7-point** -- source of truth = user input; never
   fabricate product attribute; gap = ask OR `[PREENCHER]`.
2. **Paste-intake (no URL fetch)** -- bundle does NOT open marketplace URLs;
   user describes + uploads; L5 Firecrawl optional ONLY for style calibration.
3. **Code-block output granularity** -- 1 prompt = 1 fence; negative in
   separate fence; never one giant fence. `output_validator` (P05) enforces.

## Acceptance gate (per spec section 6 + audit section 12)

See `manifest.yaml` for the full per-runtime fidelity table and the typed
artifact inventory. All gates marked in audit section 12 are satisfied.

## Source lineage

Ported from `codexa-core` (FastAPI backend). The original satellite-name
(EDISON, dropped per CODEXA_V2 D2) is fully replaced with pure CEXAI agent
identity (`codexa_imagens`). See `CONVENTION.md` for the original wave-style
fractal protocol and `CONVENTION_CEXAI_DELTA.md` for the CEXAI-specific
additions.

## Cross-references

- Founder's media pipeline: `.claude/skills/cexai-factory.md` (canonical
  reference for L3 ComfyUI workflow + L4 Qwen3-VL specs).
- Audit (Wave A by N04): `.cex/runtime/handoffs/CODEXA_V2_audit_imagens.md`.

---

Built by N03 (Inventive Pride). Audit by N04 (Knowledge Gluttony). Dispatched
by N07. Powered by CEXAI 12P.
