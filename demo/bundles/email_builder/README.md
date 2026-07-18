# Bundle de capacidade CEXAI: Construtor de Email (`email_builder`)

O **contrato de 12 pillars** para o kind `prompt_template`, mais a configuração de setup.
Nucleus N02 . kind `prompt_template` . pillar P03.

Esta é a forma "12 ISO" da CEXAI -- um arquivo de especificação por pillar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pillar como Knowledge em qualquer assistente, cole a instrução, e ele
vira um agente Construtor de Email funcional.

## Conteúdo (19 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pillar (o
  contrato de builder para este kind: uma especificação por pillar, P01-P12).
- `customgpt_instructions.json` -- a configuração do Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução em formato de system prompt
  pronto para colar (para Claude Projects ou qualquer modelo).
- `README.md` -- este arquivo.
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT Projects (plano free).
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia geral combinado (visão de todos os runtimes).

## Como fazer upload (3 formas)
- **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Suba os
  12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de
  `customgpt_instructions.json` na caixa de Instructions.
- **Claude (Project):** cole `system_instruction.md` em Custom
  Instructions; anexe os 12 arquivos de pillar ao knowledge do projeto.
- **Qualquer IA:** cole `system_instruction.md` como system prompt.

Para o passo a passo detalhado por runtime -- incluindo capabilities
recomendadas, teste guiado e solução de problemas -- veja os guias
`SETUP_*.md` deste bundle (índice completo em `SETUP_pt-br.md`).

## Proveniência / honestidade
Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem dado real de
entrada -- preencha com a sua própria marca antes de usar. Os 12 ISOs de pillar
são o contrato de builder genérico e público para `prompt_template` -- sem
dado de tenant.
