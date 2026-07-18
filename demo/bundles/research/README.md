# Bundle de Capacidade CEXAI: Research (`research`)

O **contrato de 12 pilares** para o kind `knowledge_card`, mais a configuração de setup.
Nucleus N01 . kind `knowledge_card` . pillar P01.

Este é o formato "12 ISO" da CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Faça upload dos 12
arquivos de pilar como Knowledge (conhecimento) em qualquer assistente, cole a
instrução, e ele vira um agente funcional de Research.

## Conteúdo (19 arquivos)

### Núcleo do agente (15 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato de builder para este kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a configuração do Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters (sugestões iniciais).
- `system_instruction.md` -- a mesma instrução em formato de system prompt
  pronto para colar (para Claude Projects ou qualquer modelo).
- `README.md` -- este arquivo.

### Guias de setup (4 arquivos)
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT (Custom GPT ou Projects).
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado, runtime-agnóstico, em PT-BR.

## Upload -- passo a passo (qualquer IA)

1. Baixe (ou copie) todos os arquivos deste bundle para uma pasta local.
2. Escolha seu runtime e abra o guia de setup correspondente:
   - **ChatGPT** -> `SETUP_chatgpt_projects.md`
   - **Claude** -> `SETUP_claude_projects.md`
   - **Gemini** -> `SETUP_gemini_gems.md`
   - **Não sabe qual escolher?** -> `SETUP_pt-br.md` (visão geral runtime-agnóstica)
3. Em qualquer plataforma, o padrão geral é o mesmo:
   - Crie um assistente/agente/projeto novo.
   - Cole o conteúdo de `system_instruction.md` (ou o campo `instructions` de
     `customgpt_instructions.json`) como a instrução/persona do assistente.
   - Anexe os 12 arquivos `P0X_*.md` como Knowledge/arquivos de contexto do projeto.
   - Preencha os marcadores `[fornecer: ...]` com os dados reais da sua marca.
   - Teste com o conversation starter: "Pesquise \<tópico\> -- concorrentes, preços e sinais de mercado".

## Formas resumidas de upload (3 runtimes)
- **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Faça upload dos
  12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de
  `customgpt_instructions.json` na caixa de Instructions.
- **Claude (Project):** cole `system_instruction.md` nas Custom
  instructions; anexe os 12 arquivos de pilar ao knowledge do projeto.
- **Qualquer IA:** cole `system_instruction.md` como system prompt.

## Procedência / honestidade
Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem dado real de
entrada -- preencha com a sua própria marca antes de usar. Os 12 ISOs de
pilar são o contrato de builder genérico e público do kind `knowledge_card`
-- sem dado de nenhum tenant.
