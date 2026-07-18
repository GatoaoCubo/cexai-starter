# Bundle de capacidade CEXAI: Captação de Leads (Lead-gen / scraping) (`leadgen`)

O **contrato de 12 pillars** do kind `research_pipeline`, mais a config de setup.
Nucleus N01 . kind `research_pipeline` . pillar P04.

Esta é a forma "12 ISO" do CEXAI -- um arquivo de especificação por pillar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pillar como Knowledge em qualquer assistente, cole a instrução,
e ele vira um agente funcional de Captação de Leads (Lead-gen / scraping).

## Conteúdo (15 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pillar (o
  contrato de builder deste kind: uma especificação por pillar, P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descrição,
  a string de `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução como um system prompt
  pronto para colar (para Claude Projects ou qualquer modelo).
- `README.md` -- este arquivo.
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT Projects.
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado PT-BR (visão geral + todas as opções).

## Upload (passo a passo, em qualquer IA)

1. **Escolha a plataforma**: ChatGPT (Custom GPT ou Projects), Claude (Projects)
   ou Gemini (Gems). Veja o guia `SETUP_*.md` específico para o passo a passo
   detalhado, ou siga o resumo abaixo.
2. **Cole as instruções**: copie o conteúdo de `system_instruction.md` (ou o
   campo `instructions` de `customgpt_instructions.json`) e cole no campo de
   instruções/persona da plataforma escolhida (Instructions do Custom GPT,
   Project Instructions do Claude, Instructions do Gem).
3. **Suba os 12 arquivos de pillar**: adicione `P01_knowledge.md` até
   `P12_orchestration.md` como Knowledge/Files/Base de conhecimento do
   projeto ou assistente.
4. **Preencha os placeholders**: qualquer marcador `[fornecer: ...]` precisa
   do dado real da sua marca antes do uso (nome, tom de voz, valores).
5. **Teste**: peça `Encontre leads para <perfil> a partir de <seed> --
   marketplace, CNPJ, social` e confira se o agente responde com uma lista
   tipada de leads e status honesto por fonte (nunca inventando contatos).

### Resumo por plataforma
- **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Suba os
  12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de
  `customgpt_instructions.json` na caixa de Instructions.
- **ChatGPT (Projects):** veja `SETUP_chatgpt_projects.md`.
- **Claude (Project):** cole `system_instruction.md` nas Custom
  Instructions; anexe os 12 arquivos de pillar ao Project Knowledge. Veja
  `SETUP_claude_projects.md`.
- **Gemini (Gems):** veja `SETUP_gemini_gems.md`.
- **Qualquer IA:** cole `system_instruction.md` como system prompt.

## Procedência / honestidade
Nunca-fabricar: todo marcador `[fornecer: ...]` é um campo sem dado real
-- preencha com a sua própria marca antes de usar. Os 12 ISOs de pillar são
o contrato de builder genérico e público do `research_pipeline` -- sem
dado de nenhum tenant.
