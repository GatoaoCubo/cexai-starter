# SETUP -- Gemini Gems

Setup do bundle Diagnóstico de Funil (`funnel_diag`) em Gemini Gems. Sem Actions/extensions necessárias -- fidelidade **full** direto. ~5 minutos.

## Pré-requisitos
- Conta Google + acesso a gemini.google.com.
- Zero extensions ou chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem
1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Diagnóstico de Funil`.
4. Description: `Encontra o vazamento de maior ROI no funil e ranqueia os consertos por impacto/esforço`.

### 2. Cole as Instructions
1. Abra `system_instruction.md` deste bundle.
2. Copie todo o conteúdo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge
Em **Knowledge** do Gem, suba os 12 arquivos `P01_knowledge.md` até `P12_orchestration.md`.

### 4. Extensions
Nenhuma extension é necessária -- esta capacidade não depende de busca, navegação ou ferramentas externas. Deixe todas desativadas, a menos que você queira usar Code execution para calcular os scores ICE/RICE numa planilha auxiliar.

### 5. Teste
Em uma conversa do Gem:

> `Diagnostique o funil de uma assinatura de streaming: 50.000 visitas/mês no site, 8% assina o trial, 22% do trial converte para pago, churn de 4%/mês, quase nenhum upsell.`

O Gem deve:
1. Mapear os 5 estágios com os números fornecidos e sinalizar lacunas.
2. Calcular perda absoluta antes de ranquear.
3. Apontar o vazamento principal com número.
4. Ranquear os fixes com fórmula ICE/RICE visível.
5. Fechar com "Suposições e Dados a Confirmar".

## Fidelidade declarada: full
Diferente de bundles de pesquisa que dependem de scraping/SERP (onde Gemini Gems tem suporte limitado a Actions), esta capacidade é 100% raciocínio + conhecimento injetado. Não há degradação de tier -- os 12 pilares entregam o contrato completo.

## Vantagens do Gemini Gems
- **Janela de contexto grande** (>1M tokens em modelos recentes) -- folga para o usuário colar planilhas inteiras de métricas na conversa.
- **Multi-modal nativo**: se você quer que o agente interprete um print de dashboard de analytics, pode anexar a imagem diretamente.
- **Setup mais rápido**: sem Actions/MCP para configurar, o Gem fica pronto em ~5 minutos.

## Limitações
- Gemini Gems tem suporte mais restrito a Actions/tools que Custom GPT -- irrelevante aqui, já que esta capacidade não usa nenhuma.
- Tamanho máximo de Knowledge pode variar por conta; os 12 arquivos deste bundle são leves (poucos KB cada) e cabem confortavelmente.

## Solução de problemas
- **"Ele inventou uma métrica"** -> reforce: "todo número precisa de origem (fornecido por mim ou benchmark público rotulado); sem dado, marca [A CONFIRMAR]".
- **"Ele ranqueou só por facilidade"** -> peça explicitamente os 3 eixos (Impacto/Confiança/Facilidade) antes da nota final.
- **Quero analisar um print de dashboard** -> anexe a imagem no chat e peça para o Gem extrair os números visíveis antes de diagnosticar.
- **Quero Actions/dados ao vivo** -> fora do escopo deste bundle; use Custom GPT com Actions próprias ou Claude com MCP se quiser automatizar a coleta.
