# Bundle de capability CEXAI: Landing Page (`landing`)

O **contrato de 12 pillars** para o kind `landing_page`, mais a config de setup.
Nucleus N03 . kind `landing_page` . pillar P05.

Esta é a forma "12 ISO" da CEXAI -- um arquivo de especificação por pillar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pillar como Knowledge em qualquer assistente, cole a instrução,
e ele vira um agente Landing Page funcional.

## Conteúdo (19 arquivos)

### Núcleo do bundle (15 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pillar (o
  contrato do builder para este kind: uma especificação por pillar, P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução em formato de prompt de
  sistema pronto para colar (para Claude Projects ou qualquer modelo).
- `README.md` -- este arquivo.

### Guias de setup (4 arquivos)
- `SETUP_chatgpt_projects.md` -- setup no ChatGPT (Projects + Custom GPT).
- `SETUP_claude_projects.md` -- setup no Claude Projects.
- `SETUP_gemini_gems.md` -- setup no Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado, visão geral do bundle e comparativo
  entre as 3 plataformas.

## Upload (3 formas)
- **ChatGPT (Custom GPT ou Projects):** veja `SETUP_chatgpt_projects.md`.
  Resumo: Explore GPTs -> Create -> Configure. Suba os 12 arquivos
  `P0X_*.md` como Knowledge. Cole o campo `instructions` de
  `customgpt_instructions.json` na caixa de Instructions.
- **Claude (Project):** veja `SETUP_claude_projects.md`. Resumo: cole
  `system_instruction.md` nas Custom Instructions; anexe os 12 arquivos de
  pillar ao Project Knowledge.
- **Gemini (Gem):** veja `SETUP_gemini_gems.md`. Resumo: cole
  `system_instruction.md` (ou o campo `instructions` do JSON) nas
  Instructions do Gem; suba os 12 arquivos como Knowledge.
- **Qualquer IA:** cole `system_instruction.md` como prompt de sistema.

## Passo a passo rápido (qualquer plataforma)

1. Crie um novo agente/projeto/Gem na plataforma escolhida.
2. Cole as instruções: `system_instruction.md` (ou o campo `instructions`
   de `customgpt_instructions.json`, são o mesmo conteúdo).
3. Suba os 12 arquivos `P01_knowledge.md` até `P12_orchestration.md` como
   Knowledge/Files do agente.
4. Teste com: "Crie uma landing page para <produto/oferta>".
5. O agente deve devolver uma página completa (HTML ou o stack que você
   pedir), pronta para copiar, colar e publicar.

Para o passo a passo detalhado por plataforma, com solução de problemas e
comparativo de capabilities, veja os 4 guias `SETUP_*.md`.

## Procedência / honestidade
Nunca fabricar: qualquer marcador `[fornecer: ...]` é um campo sem input
real -- preencha com a sua própria marca antes de usar. Os 12 ISOs de pillar
são o contrato genérico e público do builder para `landing_page` -- sem
dados de nenhum tenant.
