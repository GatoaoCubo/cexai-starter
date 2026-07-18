# Bundle de capacidade CEXAI: Projetista de Planos de Assinatura (`tier_designer`)

O **contrato de 12 pillares** para o kind `subscription_tier`, mais a
config de setup. Nucleus N06 . kind `subscription_tier` . pillar P11.

Esta é a forma "12 ISO" da CEXAI -- um arquivo de especificação por pillar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pillar como Knowledge para qualquer assistente, cole a
instrução, e ele vira um agente Projetista de Planos de Assinatura funcional.

## Conteúdo (19 arquivos)

- `P01_knowledge.md` ... `P12_orchestration.md` -- as 12 ISOs de pillar (o
  contrato de builder para este kind: uma especificação por pillar,
  P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução como system prompt pronto
  para colar (para Claude Projects, Gemini Gems ou qualquer outro modelo).
- `SETUP_chatgpt_projects.md` -- guia de setup no ChatGPT (Projects + Custom GPT).
- `SETUP_claude_projects.md` -- guia de setup no Claude Projects.
- `SETUP_gemini_gems.md` -- guia de setup no Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado: visão geral das 3 plataformas, fluxo
  de uso típico e solução de problemas.
- `README.md` -- este arquivo.

## Upload (passo a passo, em qualquer IA)

1. Escolha a plataforma e abra o guia correspondente -- `SETUP_chatgpt_projects.md`,
   `SETUP_claude_projects.md` ou `SETUP_gemini_gems.md` -- ou comece por
   `SETUP_pt-br.md` para a visão geral combinada.
2. Crie um Project (ChatGPT/Claude), um Gem (Gemini) ou um Custom GPT (se
   preferir essa rota no ChatGPT).
3. Cole o texto de instruções:
   - **Claude Projects / Gemini Gems / qualquer outro modelo**: cole o
     conteúdo de `system_instruction.md`.
   - **Custom GPT**: cole o campo `instructions` de
     `customgpt_instructions.json`.
4. Suba os 12 arquivos `P01_knowledge.md` ... `P12_orchestration.md` como
   Knowledge/Files.
5. Substitua os placeholders `[fornecer: ...]` nas instruções pelos dados
   reais da sua marca (nome, tom de voz, valores) -- ou deixe como estão e
   o agente vai perguntar antes de produzir qualquer coisa, em vez de
   inventar.
6. Teste com um pedido real, por exemplo: `Projete os planos de assinatura
   para <seu produto>`.

Nenhuma chave de API, Action ou extension é necessária -- este agente é
puramente de raciocínio + conhecimento de domínio (ver `SETUP_pt-br.md`,
seção "Por que este bundle não precisa de Actions/MCP/browsing").

## Proveniência / honestidade
Nunca-fabricar: qualquer marcador `[fornecer: ...]` é um campo sem dado real
de entrada -- preencha com os dados da sua própria marca antes de usar. As
12 ISOs de pillar são o contrato de builder genérico e público para
`subscription_tier` -- nenhum dado de tenant.
