# CEXAI capability bundle: Product Match + Catalog Audit (`product_match`)

The **12 pillar contract** for the `product_match` kind, plus the setup config.
Nucleus N03 . kind `product_match` . pillar P04.

This is the CEXAI "12 ISO" form -- one specification file per pillar
(P01-P12), exactly the bundle shown in the course video. Upload the 12
pillar files as Knowledge to any assistant, paste the instruction, and it
becomes a working Product Match + Catalog Audit agent.

## Contents (15 files)
- `P01_knowledge.md` ... `P12_orchestration.md` -- the 12 pillar ISOs (the
  builder contract for this kind: one specification per pillar, P01-P12).
- `customgpt_instructions.json` -- the Custom GPT config: name, description,
  the `instructions` string to paste, and conversation starters.
- `system_instruction.md` -- the same instruction as a paste-ready system
  prompt (for Claude Projects or any model).
- `README.md` -- this file.

## Upload (3 ways)
- **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Upload the
  12 `P0X_*.md` files as Knowledge. Paste the `instructions` field of
  `customgpt_instructions.json` into the Instructions box.
- **Claude (Project):** paste `system_instruction.md` into Custom
  instructions; attach the 12 pillar files to the project knowledge.
- **Any AI:** paste `system_instruction.md` as the system prompt.

## Provenance / honesty
Never-fabricate: any `[fornecer: ...]` marker is a field with no real input
-- fill it in with your own brand before use. The 12 pillar ISOs are the
generic, public builder contract for `product_match` -- no tenant data.
