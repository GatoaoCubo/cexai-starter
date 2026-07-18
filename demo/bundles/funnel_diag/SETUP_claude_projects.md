# SETUP -- Claude Projects

Setup do bundle Diagnóstico de Funil (`funnel_diag`) em Claude Projects. Sem dependência de ferramentas externas -- fidelidade **full** direto, sem wiring de MCP necessário (diferente de bundles que dependem de scraping). ~5 minutos.

## Pré-requisitos
- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- Zero chaves de API ou MCP servers necessários.

## Passo a passo

### 1. Crie o Project no Claude
1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Diagnóstico de Funil`.

### 2. Cole as Project Instructions
1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie todo o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge
Em **Knowledge** do projeto, suba os 12 arquivos `P01_knowledge.md` até `P12_orchestration.md`.
Claude Projects não tem limite de contagem de arquivos (o limite é por tamanho total do projeto).

### 4. Teste
Em uma conversa do Project:

> `Diagnostique o funil de uma assinatura de streaming: 50.000 visitas/mês no site, 8% assina o trial, 22% do trial converte para pago, churn de 4%/mês, quase nenhum upsell.`

O agente deve:
1. Mapear os 5 estágios com os números fornecidos e sinalizar as lacunas.
2. Calcular perda absoluta, não só percentual, antes de ranquear.
3. Apontar o vazamento principal com número.
4. Ranquear os fixes com a fórmula ICE/RICE visível.
5. Fechar com "Suposições e Dados a Confirmar".

## Fidelidade declarada: full
Sem tiers, sem Actions, sem MCP -- a capacidade inteira é raciocínio + conhecimento injetado sobre o dado que você fornece na conversa. Os 12 pilares cobrem 100% do contrato em qualquer plano do Claude com Projects.

## Vantagens do Claude Projects
| Aspecto | Custom GPT | Claude Projects |
|---|---|---|
| Chamadas de ferramenta em paralelo | Sequencial | Nativo via tool_use (não usado por esta capacidade, mas disponível para expansão) |
| Janela de contexto | 128K (GPT-4o) | 200K+ |
| Limite de Knowledge | 20 arquivos | Sem limite por contagem (limite por tamanho total, ~30MB) |
| Custo | Plus ($20/mês) | Free funciona; Pro ($20/mês) dá mais uso |

## Solução de problemas
- **"Ele inventou uma métrica"** -> reforce no próprio prompt: "todo número precisa de origem; sem dado, marca [A CONFIRMAR]".
- **"Ele misturou o diagnóstico com cálculo financeiro detalhado"** -> lembre: "esta capacidade só diagnostica e prioriza; payback/NPV é outra capacidade (roi_calculator)."
- **"Quero anexar uma planilha"** -> cole os dados como texto ou tabela markdown na conversa; Claude lê tabelas nativamente.
- **Quero MCP para puxar dados de analytics ao vivo** -> fora do escopo deste bundle standalone; conecte seu próprio MCP server de analytics como uma capacidade adicional do Project, se desejar.
