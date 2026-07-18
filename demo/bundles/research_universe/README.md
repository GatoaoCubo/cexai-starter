# Pacote de capacidade CEXAI: Universo de Pesquisa (Cérebro Multi-Fonte) (`research_universe`)

O **contrato de 12 pilares** para o kind `research_universe`, mais a
configuração de setup. Nucleus N01 . kind `research_universe` . pillar P01.

Esta é a forma "12 ISO" da CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o pacote mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução,
e ele se torna um agente funcional de pesquisa multi-fonte: uma semente
entra (produto, marca, CNPJ, empresa, palavra-chave ou `store:id`), um
relatório unificado sai -- firmografia, sinal social, reputação, sentimento
em PT, SEO e perguntas multi-perspectiva, cada trilha com status honesto
(`ok`/`blocked`/`skipped`) e procedência.

## Conteúdo (19 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato de builder para este kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução como system prompt pronto
  para colar (para Claude Projects ou qualquer modelo).
- `README.md` -- este arquivo.
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT Projects.
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia geral combinado (visão de todos os runtimes).

## As 6 trilhas (o que este agente pesquisa)
| Trilha | Cobre |
|--------|-------|
| Firmografia (CNPJ/IBGE) | Razão social, CNAE, porte, situação cadastral |
| Sinal Social (App Store / Reddit / YouTube) | Avaliações, menções, tom geral |
| Reputação (Reclame Aqui) | Índice de reputação, % respondidas/resolvidas |
| Sentimento em PT | Positivo/neutro/negativo sobre texto já coletado |
| Palavras-chave de SEO | Termos + intenção de busca relacionados a semente |
| Perguntas Multi-Perspectiva | Perguntas por papel: cliente, concorrente, investidor/regulador, parceiro |

Cada trilha fecha com status `ok` (dado real + fonte), `blocked` (fonte
existe, não acessada agora) ou `skipped` (não se aplica a esta semente) --
nunca com um número inventado. Detalhe completo em `P06_schema.md` e
`P07_evals.md`.

## Upload (funciona em qualquer IA)

1. **Crie o container**: um Custom GPT (ChatGPT), um Project (ChatGPT ou
   Claude) ou um Gem (Gemini). Veja o guia específico do seu runtime na
   tabela abaixo.
2. **Cole a instrução**: use o campo `instructions` de
   `customgpt_instructions.json` (ou o conteúdo integral de
   `system_instruction.md`, são equivalentes) no campo de instruções/system
   prompt do seu runtime.
3. **Suba os 12 arquivos de conhecimento**: `P01_knowledge.md` até
   `P12_orchestration.md`, como Knowledge/Files/context do seu runtime.
4. **Teste** com o conversation starter: "Pesquise `<produto/marca/CNPJ>`
   -- firmografia, social, reputação, SEO e perguntas".

| Runtime | Guia dedicado | Esforço |
|---------|----------------|--------|
| **ChatGPT (Custom GPT)** | Explore GPTs -> Create -> Configure. Suba os 12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de `customgpt_instructions.json` na caixa de Instructions. | ~10 min |
| **ChatGPT (Projects, plano free)** | `SETUP_chatgpt_projects.md` | ~5 min |
| **Claude (Project)** | `SETUP_claude_projects.md` | ~10 min |
| **Gemini (Gems)** | `SETUP_gemini_gems.md` | ~5 min |
| **Qualquer IA (fallback universal)** | Cole `system_instruction.md` como system prompt; anexe os 12 arquivos como contexto/arquivos se o runtime suportar. | ~5 min |

Para uma visão combinada dos 4 caminhos acima, veja `SETUP_pt-br.md`.

## Procedência / honestidade
Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem entrada real
-- preencha com a sua própria marca antes de usar. Os 12 ISOs de pilar são
o contrato de builder genérico e público para `research_universe` -- sem
dados de nenhum tenant. Este pacote não usa Actions, MCP nem chaves de API:
a coleta de dado por trilha é sempre paste do usuário ou busca nativa do
runtime (quando disponível) -- nunca inventada.
