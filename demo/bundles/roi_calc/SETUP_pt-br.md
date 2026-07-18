# SETUP -- Calculadora de ROI (`roi_calc`) -- guia combinado PT-BR

Guia geral do bundle. Para o passo a passo detalhado por runtime, veja os
arquivos específicos:

- **ChatGPT Projects** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`
- **ChatGPT (Custom GPT)** -> resumo abaixo (não precisa de arquivo separado)

> **Fidelidade**: `full` em qualquer runtime. Este bundle não tem Actions,
> não tem MCP e não coleta dados externos -- é um raciocinador puro sobre
> os dados que você fornece na conversa (`web_browsing`, `code_interpreter`
> e `dalle` são todos `false` no catálogo). Os 12 arquivos de pilar + a
> instrução entregam 100% da capacidade em qualquer assistente.

## Arquivos do bundle (overview)

```
roi_calc/
  P01_knowledge.md ... P12_orchestration.md   <- os 12 pilares (SUBA como Knowledge/Files)
  system_instruction.md                       <- COLE como Instructions/system prompt
  customgpt_instructions.json                 <- config pronta para Custom GPT (name/description/instructions/starters)
  README.md                                   <- visão geral + passo a passo por runtime
  SETUP_chatgpt_projects.md                   <- guia detalhado: ChatGPT Projects
  SETUP_claude_projects.md                    <- guia detalhado: Claude Projects
  SETUP_gemini_gems.md                        <- guia detalhado: Gemini Gems
  SETUP_pt-br.md                              <- este arquivo (visão combinada)
```

## Opção A -- ChatGPT (Custom GPT) -- recomendado se você tem ChatGPT Plus

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **+ Create** -> aba **Configure**.
2. Preencha **Name** e **Description** com os valores de
   `customgpt_instructions.json` (campos `name` e `description`) -- ou cole
   o próprio JSON como referência.
3. Copie o campo `instructions` de `customgpt_instructions.json` (ou o
   conteúdo de `system_instruction.md`, e o mesmo texto) para o campo
   **Instructions**.
4. Suba os 12 arquivos `P0X_*.md` como Knowledge.
5. Capabilities: deixe **Web Browsing**, **Code Interpreter** e **DALL-E**
   todos desligados -- nenhum é usado por este agente.
6. Teste com o `conversation_starter` do JSON: "Monte um caso de ROI para
   `<comprador/segmento>` -- tamanho da equipe, valor da hora, esforço atual".

## Opção B -- ChatGPT Projects

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo. Resumo:
cole `system_instruction.md` nas Instructions do Project, suba os 12
arquivos como Files, sem capabilities adicionais.

## Opção C -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo. Resumo:
cole `system_instruction.md` nas Custom Instructions, suba os 12 arquivos
ao Project knowledge, sem MCP nem tools adicionais.

## Opção D -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo. Resumo: cole
`system_instruction.md` nas Instructions do Gem, suba os 12 arquivos como
Knowledge, sem extensions adicionais.

## Opção E -- Qualquer outra IA (fallback universal)

Qualquer assistente que aceite (a) um system prompt/instructions e (b)
anexos de texto funciona:

1. Cole `system_instruction.md` como system prompt / instrução inicial.
2. Anexe (ou cole no contexto) os 12 arquivos `P0X_*.md`.
3. Converse normalmente -- o agente já sabe seu papel, suas entradas, suas
   saidas e suas salvaguardas (GUARDRAILS).

## Capabilities recomendadas por runtime

| Capability | Custom GPT | Projects (ChatGPT) | Claude | Gemini |
|------------|-----------|----------|--------|--------|
| Web Browsing | NÃO usado | NÃO usado | NÃO usado | NÃO usado |
| Code Interpreter | NÃO usado | NÃO usado | NÃO usado | NÃO usado |
| DALL-E / geração de imagem | NÃO usado | NÃO usado | NÃO usado | NÃO usado |
| MCP / Actions | NÃO usado | NÃO usado | NÃO usado | NÃO usado |

Este agente é deliberadamente enxuto: toda a capacidade vem do raciocínio
sobre os 12 arquivos de conhecimento + os dados que você fornece na
conversa -- não há chamadas externas em nenhum runtime.

## Como o agente funciona (fluxo típico)

1. Você descreve o cenário: comprador/segmento, tamanho da equipe, valor da
   hora, esforço atual no processo manual (ou outros parâmetros --
   investimento inicial, economia anual, custo de implementação, horizonte
   de tempo, taxa de desconto, manutenção anual -- ver `P05_output.md`).
2. O agente confirma quais parâmetros tem e quais faltam.
3. Ele aplica as fórmulas de `P05_output.md` / `P06_schema.md`: ROI % =
   (Lucro Líquido / Investimento Total) x 100; Prazo de Retorno =
   Investimento Total / Economia Anual; NPV = Soma(Economia / (1+r)^t) -
   Investimento; Redução de TCO = TCO da Linha de Base - Novo TCO.
4. Ele entrega o modelo completo: parâmetros de entrada, métricas de saída,
   comparação de cenários (conservador / base / otimista) e premissas
   explícitas.
5. Qualquer dado que você não forneceu aparece como `[fornecer: ...]` --
   nunca como um número inventado (ver `P11_feedback.md` e as GUARDRAILS de
   `system_instruction.md`).

## Solução de problemas

- **"Ele inventou um preço, uma economia ou um nome de cliente"** -> as
  GUARDRAILS proibem isso. Reforce: "todo número precisa vir da minha
  entrada; o que eu não informei, marque como `[fornecer: ...]`".
- **Faltam arquivos de Knowledge** -> confirme que os 12 `P0X_*.md` foram
  todos anexados (alguns runtimes não avisam se faltar um).
- **Os placeholders `[fornecer: ...]` continuam aparecendo na saída final**
  -> isso é esperado até você preencher `system_instruction.md` /
  `customgpt_instructions.json` com o nome, tom de voz e valores reais da
  sua marca antes de publicar o agente.
- **Quero adaptar para outra métrica além de ROI** -> os 12 arquivos deste
  bundle são o contrato "12 ISO" do CEXAI para o kind `roi_calculator`;
  outros kinds (ex.: `pricing_page`, `sales_playbook`) seguem a mesma
  estrutura de 12 pilares em outros bundles.

## Provenance / honestidade

Nunca fabricar: qualquer marcador `[fornecer: ...]` é um campo sem entrada
real -- preencha com os dados da sua marca antes de usar. Os 12 ISOs de
pilar são o contrato de construção genérico e público do `roi_calculator`
-- nenhum dado de cliente/tenant.
