# Bundle de capacidade CEXAI: Content (`content`)

O **contrato de 12 pilares** para o kind `knowledge_card`, mais a
configuracao de setup.
Nucleus N04 . kind `knowledge_card` . pillar P01.

Esta e a forma "12 ISO" da CEXAI -- um arquivo de especificacao por pilar
(P01-P12), exatamente o bundle mostrado no video do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrucao, e
ele vira um agent funcional de Content (captura de conhecimento e
documentacao).

## Conteudo (19 arquivos)

- `P01_knowledge.md` ate `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato do builder para este kind: uma especificacao por pilar, P01-P12).
- `customgpt_instructions.json` -- a configuracao do Custom GPT: nome,
  descricao, a string `instructions` para colar, e os conversation
  starters.
- `system_instruction.md` -- a mesma instrucao em formato de prompt de
  sistema, pronta para colar (Claude Projects, Gemini, ou qualquer modelo).
- `SETUP_chatgpt_projects.md` -- guia de setup para ChatGPT (Custom GPT e
  Projects).
- `SETUP_claude_projects.md` -- guia de setup para Claude Projects.
- `SETUP_gemini_gems.md` -- guia de setup para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado, visao geral de todos os runtimes.
- `README.md` -- este arquivo.

## Como subir (passo a passo, em qualquer IA)

1. Preencha os campos `[fornecer: ...]` de `system_instruction.md` (ou de
   `customgpt_instructions.json`) com o nome, o tom de voz e os valores da
   sua marca -- isso e o que faz o agent falar como voce, e nao de forma
   generica.
2. Suba os 12 arquivos `P0X_*.md` como Knowledge (ou Files, dependendo da
   plataforma).
3. Cole a instrucao de sistema:
   - **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Cole o
     campo `instructions` de `customgpt_instructions.json` na caixa de
     Instructions.
   - **ChatGPT (Projects):** cole `system_instruction.md` nas Instructions
     do projeto.
   - **Claude (Project):** cole `system_instruction.md` nas Custom
     Instructions; anexe os 12 arquivos de pilar a Knowledge do projeto.
   - **Gemini (Gem):** cole `system_instruction.md` no campo Instructions
     do Gem.
   - **Qualquer outra IA:** cole `system_instruction.md` como prompt de
     sistema.
4. Teste com: `Documentar o processo de integracao de novos funcionarios
   como um knowledge card`.

Guias detalhados por runtime, com capturas de tela do fluxo e solucao de
problemas: `SETUP_chatgpt_projects.md`, `SETUP_claude_projects.md`,
`SETUP_gemini_gems.md`, ou o guia combinado `SETUP_pt-br.md`.

## Procedencia / honestidade

Nunca fabricar: todo marcador `[fornecer: ...]` e um campo sem dado real --
preencha com a sua propria marca antes de usar. Os 12 ISOs de pilar sao o
contrato de builder generico e publico para `knowledge_card` -- sem dado de
tenant nenhum.
