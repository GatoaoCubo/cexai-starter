# SETUP -- Diagnóstico de Funil (funnel_diag) -- guia combinado PT-BR

Guia geral do bundle. Para o passo a passo detalhado por plataforma, veja os arquivos específicos:

- **ChatGPT Projects** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`
- **ChatGPT Custom GPT** -> use `customgpt_instructions.json` diretamente (ver "Opção A" abaixo).

> **Fidelidade deste bundle**: `full` em qualquer uma das 4 plataformas. Diferente de
> bundles que dependem de scraping/Actions (com tiers e degradação), o Diagnóstico
> de Funil é uma capacidade de raciocínio + conhecimento injetado sobre os dados
> que você mesmo fornece -- por isso não há versão "enxuta": os 12 pilares completos
> cabem em qualquer plano, inclusive os planos free de ChatGPT e Claude.

## Arquivos do bundle (visão geral)

```
funnel_diag/
  manifest.yaml                  <- metadados do pacote (nao precisa subir)
  system_instruction.md          <- COLE nas Instructions/system prompt de qualquer plataforma
  agent_card.json                <- AgentCard A2A (referencia de interoperabilidade, nao precisa subir)
  customgpt_instructions.json    <- config pronta para Custom GPT (campo "instructions" + starters)
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files
  SETUP_*.md                     <- guias de setup (este + 3 especificos)
  README.md                      <- visao geral + passo a passo rapido
```

## Opção A -- ChatGPT Custom GPT (recomendado se você tem ChatGPT Plus)

1. Acesse **chatgpt.com** -> Explore GPTs -> Create -> aba **Configure**.
2. Copie o campo `instructions` de `customgpt_instructions.json` e cole em Instructions.
3. Preencha Name/Description com os campos `name`/`description` do mesmo JSON.
4. Adicione o `conversation_starters` como prompt de exemplo.
5. Em Knowledge, suba os 12 arquivos `P01_knowledge.md` até `P12_orchestration.md`.
6. Capabilities: nenhuma é obrigatória (Web Browsing e Code Interpreter são opcionais).
7. Teste com: `Diagnostique o funil de uma assinatura de streaming: 50.000 visitas/mês, 8% assina trial, 22% do trial converte, churn 4%/mês.`

## Opção B -- ChatGPT Projects (free)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo. Resumo: crie um Project, cole `system_instruction.md` nas Instructions, suba os 12 arquivos como Files. Sem Actions, sem chaves -- funciona no plano free.

## Opção C -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo. Resumo: crie um Project, cole `system_instruction.md` nas Project Instructions, anexe os 12 arquivos ao Project Knowledge.

## Opção D -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo. Resumo: crie um Gem, cole `system_instruction.md` nas Instructions, suba os 12 arquivos como Knowledge.

## Capabilities recomendadas por plataforma

| Capability | Custom GPT | ChatGPT Projects | Claude Projects | Gemini Gems |
|---|---|---|---|---|
| Obrigatória para esta capacidade | Nenhuma | Nenhuma | Nenhuma | Nenhuma |
| Web Browsing | opcional, sem uso real aqui | opcional | não aplicável | opcional |
| Code Interpreter / execution | opcional (para calcular scores) | opcional | nativo | parcial |
| Actions/MCP/Extensions | não usado por esta capacidade | não disponível no plano free | não usado por esta capacidade | não usado por esta capacidade |

## Como o agente funciona (sem tiers de coleta)

Diferente de bundles de pesquisa de mercado (que têm TIER 1 paste / TIER 2 browsing / TIER 3 Actions), o Diagnóstico de Funil **não coleta dado nenhum sozinho**. Ele:
1. Lê os dados de funil que você cola na conversa (métricas por estágio, de qualquer fonte -- GA4, Mixpanel, RD Station, Stripe, planilha própria).
2. Mapeia os 5 estágios (atrair, engajar, converter, reter, expandir) e sinaliza qualquer estágio sem dado.
3. Calcula a perda absoluta por estágio (não só o percentual) e aponta o vazamento principal.
4. Ranqueia os consertos possíveis por ICE (Impacto/Confiança/Facilidade) ou RICE, com a fórmula visível.
5. Entrega o diagnóstico + a lista "Suposições e Dados a Confirmar".

## Como usar (fluxo típico)

1. Descreva seu funil e os números que você tem: `Diagnostique o funil de <produto>: <numeros por estagio>`.
2. O agente mapeia os 5 estágios, sinaliza lacunas.
3. Ele calcula a perda absoluta e aponta o vazamento principal com justificativa numérica.
4. Ele entrega os fixes ranqueados por ICE/RICE, com a fórmula visível por fix.
5. Ele fecha com o bloco "Suposições e Dados a Confirmar" -- todo número que você não confirmou fica marcado, nunca escondido.

## Solução de problemas

- **"Ele inventou uma métrica ou um benchmark"** -> P06/P07/P11 proíbem. Reforce: "todo número precisa de origem (fornecido por mim ou benchmark público rotulado); o que faltar, marca [A CONFIRMAR]".
- **"Ele ranqueou os fixes só por facilidade"** -> peça os 3 eixos (Impacto/Confiança/Facilidade) explícitos, não só a ordem final.
- **"Ele misturou diagnóstico com cálculo financeiro"** -> lembre que esta capacidade só diagnostica e prioriza; payback/NPV detalhado é a capacidade irmã `roi_calculator`.
- **"Só tenho dado de 2-3 estágios"** -> normal; o agente ainda mapeia os 5, marcando os que faltam como lacuna, e ranqueia com o que você tem.
- **Qual método de priorização usar, ICE ou RICE?** -> ICE é o padrão (mais simples); peça RICE explicitamente se você tem dado de alcance (reach) por fix.

## Compatibilidade e proveniência

Este bundle é um agente **standalone**, exportado do CEXAI (`_tools/cex_export_agent.py`) para o tenant `public`. Ele não tem:
- Acesso live a nenhuma ferramenta de analytics/CRM (você sempre cola o dado).
- Persistência entre conversas (cada diagnóstico é uma sessão nova).

Mas tem, em qualquer uma das 4 plataformas:
- O contrato completo de 12 pilares (P01-P12).
- O gate anti-fabricação (P07/P11): toda métrica com origem, toda lacuna marcada.
- O método de priorização transparente (ICE/RICE com fórmula visível).

## Arquitetura -- crédito

Este bundle faz parte da família de capacidades CEXAI do núcleo N06 (comercial), ao lado de `roi_calc` (cálculo financeiro de ROI/TCO) e outras capacidades de growth/pricing. Todos são tipados usando a taxonomia de 300+ kinds do CEXAI, com a mesma convenção fractal de 12 pilares.

Saiba mais: o repositório CEXAI documenta a arquitetura completa (300+ kinds, 12 pilares, 8 núcleos, pipeline de raciocínio 8F).
