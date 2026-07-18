# [fornecer: nome da marca (brand_config.identity.BRAND_NAME)] -- Diagnóstico de Funil -- pacote de agente exportado

Agente portátil de capacidade única, exportado do CEXAI. Capacidade `funnel_diag` (núcleo N06 . kind `tool_card` . pilar P11), tenant `public`, alvo `customgpt`.

Este é o pacote **contrato de 12 pilares** completo (o formato "12 ISO" do CEXAI: um arquivo de especificação por pilar, P01-P12), o mesmo padrão mostrado no vídeo do curso. Suba os 12 arquivos de pilar como Knowledge em qualquer assistente, cole a instrução, e ele vira um agente de Diagnóstico de Funil funcional.

## Conteúdo (21 arquivos)

### Núcleo do agente (5 arquivos originais)
- `manifest.yaml` -- o manifesto agent_package do CEX (kind=agent_package).
- `system_instruction.md` -- o system prompt independente de plataforma, em PT-BR.
- `agent_card.json` -- um AgentCard A2A (uma skill = esta capacidade).
- `customgpt_instructions.json` -- a renderização customgpt deste agente, em PT-BR.
- `README.md` -- este arquivo.

### Contrato de 12 pilares (P01-P12)
- `P01_knowledge.md` -- conhecimento de domínio: estágios do funil, benchmarks, métodos de priorização.
- `P02_model.md` -- identidade e persona do builder.
- `P03_prompt.md` -- instruções de produção em 3 fases.
- `P04_tools.md` -- fontes de dados e ferramentas de pipeline.
- `P05_output.md` -- template de saída com {{vars}}.
- `P06_schema.md` -- schema formal do artefato tool_card.
- `P07_evals.md` -- gate de qualidade (HARD + SOFT).
- `P08_architecture.md` -- mapa de componentes e dependências.
- `P09_config.md` -- nomenclatura, caminhos, limites.
- `P10_memory.md` -- padrões aprendidos e armadilhas.
- `P11_feedback.md` -- anti-padrões e protocolo de correção.
- `P12_orchestration.md` -- papel em crews e handoffs.

### Guias de setup (4 arquivos)
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT Projects.
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado (visão geral das 4 opções + solução de problemas).

## Upload (passo a passo em qualquer IA)

1. **Escolha sua plataforma** e abra o guia de setup correspondente (veja acima) -- ou siga o resumo abaixo.
2. **Crie o espaço de trabalho**: um Custom GPT (ChatGPT), um Project (ChatGPT ou Claude), ou um Gem (Gemini).
3. **Cole as instruções**: copie o conteúdo de `system_instruction.md` (ou o campo `instructions` de `customgpt_instructions.json`, se for Custom GPT) no campo de instruções da plataforma.
4. **Suba os 12 arquivos de conhecimento**: `P01_knowledge.md` até `P12_orchestration.md`.
5. **Teste**: "Diagnostique o funil de <produto> -- métricas por estágio, encontre o maior vazamento."

Resumo rápido por plataforma:
- **ChatGPT (Custom GPT)**: Explore GPTs -> Create -> Configure. Cole o campo `instructions` de `customgpt_instructions.json`. Suba os 12 `P0X_*.md` como Knowledge.
- **ChatGPT (Projects)**: veja `SETUP_chatgpt_projects.md`.
- **Claude (Project)**: cole `system_instruction.md` nas Custom Instructions; anexe os 12 arquivos de pilar ao Project Knowledge. Veja `SETUP_claude_projects.md`.
- **Gemini (Gems)**: veja `SETUP_gemini_gems.md`.
- **Qualquer IA**: cole `system_instruction.md` como system prompt.

## Proveniência / honestidade
Nunca-fabricar: qualquer marcador `[fornecer: ...]` é um campo sem input real -- preencha antes de usar. Notas:
- `brand_config.yaml` não encontrado para o tenant 'public' -- os campos de marca são placeholders (nunca fabricados).
- Não há `input_contract` tipado declarado para esta capacidade -- o agente recebe uma única entrada de texto livre `intent`.
- Esta capacidade não depende de ferramentas/Actions externas (sem tiers de coleta, sem chaves de API) -- por isso a fidelidade é `full` em qualquer uma das 4 plataformas de setup.

_Gerado originalmente por `_tools/cex_export_agent.py` em 2026-07-17T07:08:24+00:00. Padronizado para PT-BR + expandido para o contrato de 12 pilares por célula N02/N03 em 2026-07-17. Offline, read-only, sem DB/prod._
