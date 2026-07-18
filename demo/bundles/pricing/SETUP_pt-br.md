# SETUP -- pricing (agente de Precificacao) -- guia combinado PT-BR

Guia geral do bundle `pricing`. Para o passo a passo detalhado por
plataforma, veja os arquivos especificos:

- **ChatGPT** (Projects ou Custom GPT) -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `FULL` em qualquer uma das tres plataformas. Este agente
> nao depende de Actions, MCP nem browsing -- e um agente de raciocinio +
> conhecimento de dominio (os 12 arquivos `P01`..`P12`). Nao ha versao
> "reduzida": os mesmos 12 arquivos + o mesmo texto de instrucoes entregam a
> capacidade completa em qualquer plataforma.

## Arquivos do bundle (visao geral)

```
pricing/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files em qualquer plataforma
  system_instruction.md                       <- COLE como Instructions/system prompt (ChatGPT Projects, Claude, Gemini)
  customgpt_instructions.json                 <- config pronta para Custom GPT (campo "instructions" = mesmo texto do system_instruction.md)
  README.md                                   <- visao geral + passo a passo rapido
  SETUP_chatgpt_projects.md                   <- guia ChatGPT (Projects + Custom GPT)
  SETUP_claude_projects.md                    <- guia Claude Projects
  SETUP_gemini_gems.md                        <- guia Gemini Gems
  SETUP_pt-br.md                              <- este arquivo
```

## Qual plataforma escolher?

| Se voce ja usa | Escolha | Esforco |
|-----------------|---------|---------|
| ChatGPT (com Projects ou Custom GPTs habilitados) | Custom GPT (link fixo, compartilhavel) ou Projects (mais rapido) | ~5 min |
| Claude | Claude Projects | ~5 min |
| Google Workspace / Gemini | Gemini Gems | ~5 min |
| Nenhuma das anteriores ainda | Comece pela que voce ou seu time ja usa no dia a dia -- o resultado e o mesmo | ~5 min |

Nao ha certo ou errado entre as tres: os 12 arquivos + as instrucoes sao
identicos. Escolha a ferramenta que voce ou seu time ja usa no dia a dia.

## Resumo por plataforma

1. **Custom GPT / ChatGPT Projects** -> veja `SETUP_chatgpt_projects.md`.
   - Cole o campo `instructions` de `customgpt_instructions.json` (Custom
     GPT) ou o conteudo de `system_instruction.md` (Projects).
   - Suba os 12 arquivos como Knowledge/Files.
   - Nenhuma capability (web browsing, code interpreter, DALL-E) e
     necessaria.
2. **Claude Projects** -> veja `SETUP_claude_projects.md`.
   - Cole `system_instruction.md` nas instrucoes personalizadas do projeto.
   - Suba os 12 arquivos em Project knowledge.
3. **Gemini Gems** -> veja `SETUP_gemini_gems.md`.
   - Cole `system_instruction.md` nas Instructions do Gem.
   - Suba os 12 arquivos em Knowledge.
   - Nenhuma extension e necessaria.

## Por que este bundle nao precisa de Actions/MCP/browsing

O agente de Precificacao NAO pesquisa a web nem chama APIs externas em
tempo real -- a tarefa dele e projetar a ARQUITETURA de monetizacao (tiers,
creditos, checkout, cursos, anuncios, e-mail) a partir do que voce descreve
mais o conhecimento de dominio ja embutido nos 12 arquivos (padroes
Hotmart, Digistore24, Stripe, Kiwify, Monetizze, Eduzz, Resend, SendGrid,
Meta/Google Ads, entre outros -- ver `P04_tools.md`). Por isso
`customgpt_instructions.json` declara `web_browsing: false`,
`code_interpreter: false` e `dalle: false`: nenhuma capability extra e
necessaria para a fidelidade completa.

Se voce quiser que o proprio agente EXECUTE a integracao (chamar a API real
da Hotmart, criar o produto na Stripe etc.), isso e trabalho de
implementacao -- fora do escopo deste bundle de demonstracao. O artefato
que ele produz e a especificacao completa que um desenvolvedor (ou outro
agente com acesso a essas APIs) usa para implementar.

## Como o agente produz a config (fluxo tipico)

1. Descreva o negocio: nicho, pais/moeda, tipo de conteudo, provedor de
   pagamento preferido (se ja souber). Exemplo: `Crie a precificacao para
   uma escola de idiomas online, BR, cobranca em BRL via Hotmart`.
2. O agente segue o pipeline de 9 estagios (ver `P08_architecture.md`):
   PARSE -> PRICING -> CREDITS -> CHECKOUT -> COURSES -> ADS -> EMAILS ->
   VALIDATE -> DEPLOY -- aplicando so os estagios relevantes ao seu caso
   (nem todo negocio precisa de creditos ou de cursos, por exemplo).
3. Ele entrega a config em YAML (ver o template em `P05_output.md`) com:
   - tiers com precos em centavos (nunca em float) e margem minima >= 30%
     explicita;
   - sistema de creditos (se aplicavel) com politica de saldo negativo
     definida;
   - integracao de checkout com o provedor escolhido, sempre com
     `mock_mode: true` ate voce validar;
   - qualquer dado que faltar, marcado como `[fornecer: ...]` -- nunca
     inventado.
4. Voce revisa, preenche os campos `[fornecer: ...]` que restarem, e
   entrega a config para quem for implementar (seu time de dev, ou outro
   agente com acesso as APIs reais).

## Solucao de problemas (comum as tres plataformas)

- **"Ele inventou um preco ou uma taxa"** -> os 12 arquivos proibem isso
  explicitamente (ver `P02_model.md`, secao Regras, e `P11_feedback.md`,
  secao Antipadroes). Reforce: "todo numero sem origem real precisa vir
  marcado como `[fornecer: ...]` ou `[A CONFIRMAR]`".
- **"Ele esqueceu a margem minima"** -> peca explicitamente: "confirme que
  `floor_margin_pct >= 0.30` para todos os tiers antes de finalizar" (ver
  `P07_evals.md`, Gates HARD, H2).
- **"Quero trocar de provedor de pagamento (ex.: Hotmart -> Stripe)"** ->
  peca a config novamente informando o novo provedor; o agente reprojeta so
  o estagio CHECKOUT (ver `P06_schema.md`, blocos `checkout_ds24` /
  `checkout_hotmart`).
- **"Os placeholders `[fornecer: ...]` nao saem"** -> normal, eles so somem
  quando voce informa o dado real (nome da marca, tom de voz, valores) nas
  Instructions/system prompt.
- **"Qual arquivo eu edito para trocar so a persona/o tom?"** -> apenas
  `system_instruction.md` (secao VOZ DA MARCA) -- nao mexa nos 12 arquivos
  `P0X`, eles sao o contrato tecnico do kind `content_monetization`, nao a
  personalizacao de marca.

## Compatibilidade e manutencao

Este bundle e uma copia publica e autocontida do contrato de 12 pillares do
kind `content_monetization` da arquitetura CEXAI (300+ kinds, 12 pillares, 8
nucleos). Para atualizar o bundle no futuro, edite os 12 arquivos `P0X` e
`system_instruction.md`/`customgpt_instructions.json` de forma proporcional
-- os tres precisam permanecer consistentes entre si (mesma persona, mesmas
regras, mesmo idioma).
