# Pacote de capacidade CEXAI: Pesquisa de Produto (Produto -> Anúncio) (`pesquisa_produto`)

O **contrato de 12 pillars** para o kind `knowledge_card`, mais a configuração de setup.
Nucleus N01 . kind `knowledge_card` . pillar P01.

Este é o formato "12 ISO" da CEXAI -- um arquivo de especificação por pillar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pillar como Knowledge para qualquer assistente, cole a
instrução, e ele se torna um agente de Pesquisa de Produto (Produto ->
Anúncio) funcional.

## Conteúdo (19 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pillar (o
  contrato de builder para este kind: uma especificação por pillar, P01-P12).
- `customgpt_instructions.json` -- a configuração do Custom GPT: nome,
  descrição, a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução em formato de prompt de
  sistema pronto para colar (para Claude Projects, Gemini, ou qualquer modelo).
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT (Custom GPT e Projects).
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado, visão geral de todas as formas de upload.
- `README.md` -- este arquivo.

## Upload (4 formas)
- **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Suba os
  12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de
  `customgpt_instructions.json` na caixa Instructions. Passo a passo
  completo (Custom GPT + Projects): `SETUP_chatgpt_projects.md`.
- **Claude (Project):** cole `system_instruction.md` em Custom instructions;
  anexe os 12 arquivos de pillar ao project knowledge. Passo a passo
  completo: `SETUP_claude_projects.md`.
- **Gemini (Gem):** crie um Gem, cole `system_instruction.md` no campo
  Instructions do Gem, e suba os 12 arquivos de pillar como knowledge do
  Gem. Passo a passo completo: `SETUP_gemini_gems.md`.
- **Qualquer IA:** cole `system_instruction.md` como o prompt de sistema.

Prefere um guia único com as 3 opções lado a lado? Veja `SETUP_pt-br.md`.

## Procedência / Honestidade
Nunca fabricar: qualquer marcador `[fornecer: ...]` é um campo sem input
real -- preencha com os dados da sua marca antes de usar. Os 12 ISOs de
pillar são o contrato de builder genérico e público para `knowledge_card`
-- sem dado de tenant.
