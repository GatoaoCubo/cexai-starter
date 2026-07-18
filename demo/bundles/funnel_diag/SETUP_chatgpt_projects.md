# SETUP -- ChatGPT Projects

Setup do bundle Diagnóstico de Funil (`funnel_diag`) em ChatGPT Projects. Como esta capacidade não depende de Actions/ferramentas externas (é raciocínio + conhecimento injetado sobre os dados que você fornece), a fidelidade é **full** mesmo no plano free. ~5 minutos.

## Pré-requisitos
- Conta ChatGPT (plano free é suficiente -- Projects está disponível nele).
- Zero chaves de API necessárias (este agente não chama nenhuma ferramenta externa).

## Passo a passo

### 1. Crie o Project
1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Diagnóstico de Funil`.

### 2. Cole as Instructions
1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie todo o conteúdo de `system_instruction.md` deste bundle.
3. Cole no campo Instructions do projeto.

### 3. Suba os 12 arquivos de Files
Em **Files** do projeto, suba os 12 arquivos `P01_knowledge.md` até `P12_orchestration.md`.

### 4. Capabilities
Nenhuma capability especial é necessária -- esta é uma capacidade de raciocínio puro sobre o que você fornece na conversa. Code Interpreter é opcional, caso queira que o agente calcule os scores ICE/RICE em uma planilha auxiliar.

### 5. Teste
Inicie uma conversa dentro do project:

> `Diagnostique o funil de uma assinatura de streaming: 50.000 visitas/mês no site, 8% assina o trial, 22% do trial converte para pago, churn de 4%/mês, quase nenhum upsell.`

O agente deve:
1. Mapear os 5 estágios (atrair, engajar, converter, reter, expandir) com os números fornecidos.
2. Sinalizar como lacuna qualquer estágio sem dado (ex.: "atrair" sem custo de aquisição).
3. Calcular a perda absoluta por estágio, não só o percentual.
4. Apontar o vazamento principal com justificativa numérica.
5. Entregar os fixes ranqueados por ICE/RICE, com a fórmula visível.
6. Fechar com o bloco "Suposições e Dados a Confirmar".

## Fidelidade declarada: full

| Motivo | Detalhe |
|---|---|
| Sem Actions necessárias | O agente não depende de scraping/API externa -- só raciocina sobre o dado fornecido |
| Sem tiers de coleta | Diferente de bundles de pesquisa de mercado, aqui não há TIER 1/2/3 -- é uma única capacidade de diagnóstico |
| 12 pilares completos | Nenhum pilar foi cortado para caber no plano free |

## Vantagens do ChatGPT Projects
| Aspecto | Custom GPT | ChatGPT Projects |
|---|---|---|
| Plano mínimo | Plus (Actions exigem Plus) | Free |
| Compartilhamento | Publicável no GPT Store | Privado ao workspace/conta |
| Limite de arquivos de Knowledge | 20 arquivos | Sem limite rígido de contagem (limite por tamanho total) |
| Setup | ~10 min (Configure + Knowledge + Actions) | ~5 min (Instructions + Files) |

## Solução de problemas
- **"Ele inventou uma métrica"** -> reforce: "todo número precisa vir de dado que eu forneci ou de benchmark público rotulado; o que faltar, marque [A CONFIRMAR]."
- **"Ele só ranqueou por facilidade"** -> peça explicitamente: "mostra o Impacto, a Confiança e a Facilidade de cada fix, não só a ordem final."
- **"Quero anexar uma planilha de métricas"** -> cole os números como texto na conversa ou ative Code Interpreter e suba um CSV.
- **Quero o Custom GPT publicável (GPT Store)** -> use `customgpt_instructions.json` com um Custom GPT (ChatGPT Plus), não o Project.
