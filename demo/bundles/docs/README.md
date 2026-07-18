# Bundle de capacidade CEXAI: Conhecimento e Documentacao (`docs`)

O contrato de **12 pillars** para o kind `knowledge_card`, mais a config de
setup. Nucleus N04 . kind `knowledge_card` . pillar P01.

Este e o formato "12 ISO" da CEXAI -- um arquivo de especificacao por pillar
(P01-P12), exatamente o bundle mostrado no video do curso. Suba os 12
arquivos de pillar como Knowledge em qualquer assistente, cole a instrucao,
e ele vira um agente funcional de Conhecimento e Documentacao.

## Conteudo (19 arquivos)

- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 pillar ISOs (o
  contrato do builder para este kind: uma especificacao por pillar,
  P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descricao,
  a string de `instructions` para colar, e conversation starters.
- `system_instruction.md` -- a mesma instrucao como um system prompt pronto
  para colar (para Claude Projects, Gemini Gems, ou qualquer modelo).
- `SETUP_chatgpt_projects.md` -- setup detalhado no ChatGPT (Custom GPT e
  ChatGPT Projects).
- `SETUP_claude_projects.md` -- setup detalhado no Claude Projects.
- `SETUP_gemini_gems.md` -- setup detalhado no Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado (overview + comparativo + solucao de
  problemas de todas as plataformas).
- `README.md` -- este arquivo.

## Upload (passo a passo, em qualquer IA)

1. **Cole as instrucoes**: copie o conteudo de `system_instruction.md` (ou,
   no ChatGPT Custom GPT, o campo `instructions` de
   `customgpt_instructions.json`) no campo de instrucoes/system prompt do
   seu assistente.
2. **Suba os 12 arquivos de pillar** (`P01_knowledge.md` ...
   `P12_orchestration.md`) como Knowledge/Files/contexto do seu assistente.
3. **Preencha os placeholders**: troque cada `[fornecer: ...]` pelo dado
   real da sua marca (nome, tom de voz, valores) antes de publicar.
4. **Teste**: peca para o agente documentar um assunto real do seu negocio,
   por exemplo `Capturar politica de trocas e devolucoes como documentacao
   pronta para RAG`.

Guias detalhados por plataforma:

| Plataforma | Guia |
|------------|------|
| ChatGPT (Custom GPT ou Projects) | `SETUP_chatgpt_projects.md` |
| Claude Projects | `SETUP_claude_projects.md` |
| Gemini Gems | `SETUP_gemini_gems.md` |
| Visao geral combinada (todas as plataformas) | `SETUP_pt-br.md` |

## Proveniencia / honestidade

Nunca fabricar: qualquer marcador `[fornecer: ...]` e um campo sem dado
real -- preencha com a sua propria marca antes de usar. Os 12 pillar ISOs
sao o contrato de builder generico e publico para `knowledge_card` -- sem
dado de nenhum tenant.
