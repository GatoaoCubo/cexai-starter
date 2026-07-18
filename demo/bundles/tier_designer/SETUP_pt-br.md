# SETUP -- tier_designer (agente Projetista de Planos de Assinatura) -- guia combinado PT-BR

Guia geral do bundle `tier_designer`. Para o passo a passo detalhado por
plataforma, veja os arquivos específicos:

- **ChatGPT** (Projects ou Custom GPT) -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `FULL` em qualquer uma das três plataformas. Este agente
> não depende de Actions, MCP nem browsing -- é um agente de raciocínio +
> conhecimento de domínio (os 12 arquivos `P01`..`P12`). Não há versão
> "reduzida": os mesmos 12 arquivos + o mesmo texto de instruções entregam a
> capacidade completa em qualquer plataforma.

## Arquivos do bundle (visão geral)

```
tier_designer/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files em qualquer plataforma
  system_instruction.md                       <- COLE como Instructions/system prompt (ChatGPT Projects, Claude, Gemini)
  customgpt_instructions.json                 <- config pronta para Custom GPT (campo "instructions" = mesmo texto do system_instruction.md)
  README.md                                   <- visão geral + passo a passo rápido
  SETUP_chatgpt_projects.md                   <- guia ChatGPT (Projects + Custom GPT)
  SETUP_claude_projects.md                    <- guia Claude Projects
  SETUP_gemini_gems.md                        <- guia Gemini Gems
  SETUP_pt-br.md                              <- este arquivo
```

## Qual plataforma escolher?

| Se você já usa | Escolha | Esforço |
|-----------------|---------|---------|
| ChatGPT (com Projects ou Custom GPTs habilitados) | Custom GPT (link fixo, compartilhável) ou Projects (mais rápido) | ~5 min |
| Claude | Claude Projects | ~5 min |
| Google Workspace / Gemini | Gemini Gems | ~5 min |
| Nenhuma das anteriores ainda | Comece pela que você ou seu time já usa no dia a dia -- o resultado é o mesmo | ~5 min |

Não há certo ou errado entre as três: os 12 arquivos + as instruções são
idênticos. Escolha a ferramenta que você ou seu time já usa no dia a dia.

## Resumo por plataforma

1. **Custom GPT / ChatGPT Projects** -> veja `SETUP_chatgpt_projects.md`.
   - Cole o campo `instructions` de `customgpt_instructions.json` (Custom
     GPT) ou o conteúdo de `system_instruction.md` (Projects).
   - Suba os 12 arquivos como Knowledge/Files.
   - Nenhuma capability (web browsing, code interpreter, DALL-E) é
     necessária.
2. **Claude Projects** -> veja `SETUP_claude_projects.md`.
   - Cole `system_instruction.md` nas instruções personalizadas do projeto.
   - Suba os 12 arquivos em Project knowledge.
3. **Gemini Gems** -> veja `SETUP_gemini_gems.md`.
   - Cole `system_instruction.md` nas Instructions do Gem.
   - Suba os 12 arquivos em Knowledge.
   - Nenhuma extension é necessária.

## Por que este bundle não precisa de Actions/MCP/browsing

O agente Projetista de Planos de Assinatura NÃO pesquisa a web nem chama
APIs externas em tempo real -- a tarefa dele é projetar a ARQUITETURA de
precificação (tiers, unidade de monetização, feature matrix, trial e
conversão, grandfathering, expansão de MRR) a partir do que você descreve
mais o conhecimento de domínio já embutido nos 12 arquivos (padrões Stripe
Billing, Chargebee, Recurly, Paddle, Zuora -- ver `P01_knowledge.md` e
`P04_tools.md`). Por isso `customgpt_instructions.json` declara
`web_browsing: false`, `code_interpreter: false` e `dalle: false`: nenhuma
capability extra é necessária para a fidelidade completa.

Se você quiser que o próprio agente EXECUTE a integração (criar o produto e
os preços de fato na Stripe/Chargebee etc.), isso é trabalho de
implementação -- fora do escopo deste bundle de demonstração. O artefato que
ele produz é a especificação completa que um desenvolvedor (ou outro agente
com acesso a essas APIs) usa para implementar.

## Como o agente produz a matriz de planos (fluxo típico)

1. Descreva o produto: nicho, moeda, unidade de monetização preferida (se já
   souber). Exemplo: `Crie os tiers de assinatura para uma ferramenta de
   automação de marketing, modelo per_seat, BR`.
2. O agente segue as regras de `P02_model.md` (Escopo + Qualidade +
   SEMPRE/NUNCA): escolhe monetization_unit, define de 3 a 4 tiers com
   nomes orientados a resultado (Starter/Growth/Business/Enterprise --
   nunca Bronze/Silver/Gold), e monta o feature_matrix em formato tabular.
3. Ele entrega a definição de cada tier (ver o template em
   `P05_output.md`) com:
   - preço no formato canônico do Stripe -- `unit_amount` em centavos
     (nunca ponto flutuante), `currency` ISO 4217, `interval` em
     `{day, week, month, year}`;
   - feature_matrix tabular, nunca lista em prosa;
   - trial_policy e proration_behavior quando aplicável;
   - grandfathering_policy quando o tier substitui um tier ativo;
   - ganchos de expansion_mrr (upgrade_path_to, add_on_catalog,
     seat_expansion_price);
   - qualquer dado que faltar, marcado como `[fornecer: ...]` -- nunca
     inventado.
4. Você revisa contra o gate de qualidade (`P07_evals.md`, gates H01-H11 +
   rubrica D1-D10), preenche os campos `[fornecer: ...]` que restarem, e
   entrega a config para quem for implementar (seu time de dev, ou outro
   agente com acesso às APIs reais de cobrança).

## Solução de problemas (comum às três plataformas)

- **"Ele usou nome de tier em medalha (Bronze/Silver/Gold)"** -> os 12
  arquivos proíbem isso explicitamente (ver `P02_model.md`, seção
  SEMPRE/NUNCA, e `P06_schema.md`, Restrições -- gate H04). Reforce: "use
  nomes de tier orientados a resultado, nunca metáforas de medalha".
- **"Ele inventou um preço em ponto flutuante (9.99)"** -> peça
  explicitamente: "confirme que todo preço está em centavos, como inteiro"
  (ver `P07_evals.md`, gate H06).
- **"Ele esqueceu o grandfathering ao substituir um tier"** -> peça: "esta
  mudança substitui um tier ativo -- documente price_lock_months,
  feature_freeze e migration_offer" (ver `P06_schema.md`, campo
  `grandfathering_policy`).
- **"Quero trocar a unidade de monetização (ex.: flat -> per_seat)"** ->
  peça a matriz novamente informando a nova unidade; o agente reprojeta o
  feature_matrix e os ganchos de expansão em torno dela.
- **"Os placeholders `[fornecer: ...]` não saem"** -> normal, eles só somem
  quando você informa o dado real (nome da marca, tom de voz, valores) nas
  Instructions/system prompt.
- **"Qual arquivo eu edito para trocar só a persona/o tom?"** -> apenas
  `system_instruction.md` (seção VOZ DA MARCA) -- não mexa nos 12 arquivos
  `P0X`, eles são o contrato técnico do kind `subscription_tier`, não a
  personalização de marca.

## Compatibilidade e manutenção

Este bundle é uma cópia pública e autocontida do contrato de 12 pillares do
kind `subscription_tier` da arquitetura CEXAI (300+ kinds, 12 pillares, 8
núcleos). Para atualizar o bundle no futuro, edite os 12 arquivos `P0X` e
`system_instruction.md`/`customgpt_instructions.json` de forma proporcional
-- os três precisam permanecer consistentes entre si (mesma persona, mesmas
regras, mesmo idioma).
