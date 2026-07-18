# Bundle de capacidade CEXAI: Precificacao (`pricing`)

O **contrato de 12 pillares** para o kind `content_monetization`, mais a
config de setup. Nucleus N06 . kind `content_monetization` . pillar P11.

Esta e a forma "12 ISO" da CEXAI -- um arquivo de especificacao por pillar
(P01-P12), exatamente o bundle mostrado no video do curso. Suba os 12
arquivos de pillar como Knowledge para qualquer assistente, cole a
instrucao, e ele vira um agente de Precificacao funcional.

## Conteudo (19 arquivos)

- `P01_knowledge.md` ... `P12_orchestration.md` -- as 12 ISOs de pillar (o
  contrato de builder para este kind: uma especificacao por pillar,
  P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descricao,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrucao como system prompt pronto
  para colar (para Claude Projects, Gemini Gems ou qualquer outro modelo).
- `SETUP_chatgpt_projects.md` -- guia de setup no ChatGPT (Projects + Custom GPT).
- `SETUP_claude_projects.md` -- guia de setup no Claude Projects.
- `SETUP_gemini_gems.md` -- guia de setup no Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado: visao geral das 3 plataformas, fluxo
  de uso tipico e solucao de problemas.
- `README.md` -- este arquivo.

## Upload (passo a passo, em qualquer IA)

1. Escolha a plataforma e abra o guia correspondente -- `SETUP_chatgpt_projects.md`,
   `SETUP_claude_projects.md` ou `SETUP_gemini_gems.md` -- ou comece por
   `SETUP_pt-br.md` para a visao geral combinada.
2. Crie um Project (ChatGPT/Claude), um Gem (Gemini) ou um Custom GPT (se
   preferir essa rota no ChatGPT).
3. Cole o texto de instrucoes:
   - **Claude Projects / Gemini Gems / qualquer outro modelo**: cole o
     conteudo de `system_instruction.md`.
   - **Custom GPT**: cole o campo `instructions` de
     `customgpt_instructions.json`.
4. Suba os 12 arquivos `P01_knowledge.md` ... `P12_orchestration.md` como
   Knowledge/Files.
5. Substitua os placeholders `[fornecer: ...]` nas instrucoes pelos dados
   reais da sua marca (nome, tom de voz, valores) -- ou deixe como estao e
   o agente vai perguntar antes de produzir qualquer coisa, em vez de
   inventar.
6. Teste com um pedido real, por exemplo: `Crie os niveis de precificacao
   para <seu produto>`.

Nenhuma chave de API, Action ou extension e necessaria -- este agente e
puramente de raciocinio + conhecimento de dominio (ver `SETUP_pt-br.md`,
secao "Por que este bundle nao precisa de Actions/MCP/browsing").

## Proveniencia / honestidade

Nunca-fabricar: qualquer marcador `[fornecer: ...]` e um campo sem dado real
de entrada -- preencha com os dados da sua propria marca antes de usar. As
12 ISOs de pillar sao o contrato de builder generico e publico para
`content_monetization` -- nenhum dado de tenant.
