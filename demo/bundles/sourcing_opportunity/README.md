# Bundle de capability CEXAI: Sourcing Opportunity Matrix (`sourcing_opportunity`)

O **contrato de 12 pilares** para o kind `opportunity_matrix`, mais a configuração de setup.
Nucleus N06 . kind `opportunity_matrix` . pillar P11.

Esta é a forma "12 ISO" do CEXAI -- um arquivo de especificação por pillar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pillar como Knowledge em qualquer assistente, cole a instrução, e
ele vira um agente Sourcing Opportunity Matrix funcional.

## Conteúdo (19 arquivos)

| Arquivo | O que é |
|---|---|
| `P01_knowledge.md` ... `P12_orchestration.md` | os 12 ISOs de pillar (o contrato do builder para este kind: uma especificação por pillar, P01-P12) |
| `customgpt_instructions.json` | a config do Custom GPT: nome, descrição, a string `instructions` para colar, e os conversation starters |
| `system_instruction.md` | a mesma instrução em formato de system prompt pronto para colar (para Claude Projects ou qualquer modelo) |
| `README.md` | este arquivo |
| `SETUP_chatgpt_projects.md` | passo a passo detalhado para ChatGPT (Custom GPT / Projects) |
| `SETUP_claude_projects.md` | passo a passo detalhado para Claude Projects |
| `SETUP_gemini_gems.md` | passo a passo detalhado para Gemini Gems |
| `SETUP_pt-br.md` | guia combinado -- visão geral de todos os caminhos de setup em um único lugar |

## Passo a passo de upload (em qualquer IA)

Este bundle não depende de nenhuma ferramenta externa, Action, ou credencial de API -- é
puramente Knowledge + instrução. Os 4 passos abaixo funcionam de forma quase idêntica em
qualquer assistente com upload de arquivos e uma caixa de instruções/system prompt:

1. **Crie o espaço do agente**: um Custom GPT (ChatGPT), um Project (ChatGPT ou Claude), ou um
   Gem (Gemini) -- veja o guia específico da sua plataforma na tabela acima.
2. **Cole a instrução**:
   - ChatGPT (Custom GPT): cole o campo `instructions` de `customgpt_instructions.json` na caixa
     Instructions.
   - Claude Projects, Gemini Gems, ou qualquer outra IA: cole o conteúdo de
     `system_instruction.md` no campo de instruções/system prompt.
3. **Suba os 12 arquivos de conhecimento**: `P01_knowledge.md` até `P12_orchestration.md`, como
   Knowledge (ChatGPT), Project Knowledge (Claude) ou Knowledge do Gem (Gemini).
4. **Teste**: peça para o agente ranquear um catálogo de fornecedor de exemplo (custo por SKU)
   contra a demanda de mercado por tipo de produto. Ele deve explicar o contrato de entrada, as
   8 seções de saída na ordem congelada, e o veredito do gate `sourcing_confiavel` -- sem
   fabricar um preço de mercado ou nível de demanda, já que o motor real é offline-determinístico
   e honest-null sem uma credencial de demanda ao vivo (ver `P01_knowledge.md`).

Para o passo a passo completo, com telas e detalhes específicos de cada plataforma, use os guias
`SETUP_*.md` listados acima -- comece por `SETUP_pt-br.md` se quiser a visão consolidada.

## Procedência / honestidade

Nunca fabricar: qualquer marcador `[fornecer: ...]` é um campo sem dado real de entrada --
preencha com a sua própria marca antes de usar. Os 12 ISOs de pillar são o contrato de builder
genérico e público para `opportunity_matrix` -- sem dado de nenhum tenant.
