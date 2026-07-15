// ----------------------------------------------------------------------------
// Ads capability -- the CATALOG AD (product_ad buyer page) used as the dashboard
// fixture human_html.
//
// THE PRINCIPLE: the dashboard mock MUST reflect the EXPECTED human-facing result
// a supervisor reviews. For the ADS capability that is the CATALOG AD (the buyer
// page: brandbar + hero + galeria + sobre + caracteristicas + oferta + ficha +
// FAQ), NOT the typed operator report (Variantes / A-B / Compliance / Keywords).
// In the LIVE backend run path cex_run_capability._render_ad_mold_html already
// swaps human_html -> the product_ad mold; this fixture mirrors that so
// DualOutputFace ("Abrir" / "Exportar HTML") renders the catalog ad, not the report.
//
// SOURCE: _output/real_ad_CB3603_MAXED.html (the maxed product_ad mold -- 12
// sections, real catalog images, ficha, R$ 68,42, Minha Loja-themed). It is a FULL
// standalone <!doctype html> document, so DualOutputFace.wrapHtmlDocument passes
// it through untouched.
//
// HONEST-MOCK: the document already carries the "amostra -- dados simulados" badge
// in its footer (it is a demo, never "resultado real"). Keep that badge intact.
//
// FIXTURE FLAVOR (register R-269 second pass): mirrors lib/molds.ts's module-scope
// activeFlavorKey singleton. Retail's hotlinked mercadolivre.com.br cat-product
// photos cannot simply be re-captioned for other flavors (the IMAGE ITSELF would
// still show a cat bed) -- services/neutral swap every image slot for a neutral
// inline SVG data-URI placeholder (CSP-compliant: `img-src https: data:` is
// already declared). services mirrors the SAME "Pacote de Suporte Tecnico
// Mensal" narrative MOLD_ADS's services branch uses (lib/molds.ts) -- the exact
// same 12-section DOM skeleton (brandbar/hero/galeria/sobre/caracteristicas/
// valor/prova/oferta/ficha/faq/cta2/footer), same figure/li/table-row counts,
// only the copy differs.
// ----------------------------------------------------------------------------

import { config } from "../config";
import { resolveFlavor, type FixtureFlavorKey } from "../fixtureFlavor";

const activeFlavorKey: FixtureFlavorKey = resolveFlavor(config.businessShape).key;

/** Neutral gray placeholder (inline SVG data-URI) for non-retail image slots. */
const PLACEHOLDER_IMG =
  "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='800'%20height='800'%3E%3Crect%20width='800'%20height='800'%20fill='%23cbd5e1'/%3E%3Ctext%20x='400'%20y='400'%20font-family='sans-serif'%20font-size='32'%20fill='%23475569'%20text-anchor='middle'%20dominant-baseline='middle'%3EFoto%20ilustrativa%3C/text%3E%3C/svg%3E";

interface AdCatalogFlavorExt {
  title: string;
  metaDescription: string;
  brandName: string;
  brandTag: string;
  heroEyebrow: string;
  heroH1: string;
  heroImg: string;
  /** 5 gallery images. */
  galleryImgs: readonly [string, string, string, string, string];
  bodyLead: string;
  bodySecond: string;
  /** 6 items. */
  features: readonly [string, string, string, string, string, string];
  whyText: string;
  /** 6 titles ("O que entrega"). */
  entregaCards: readonly [string, string, string, string, string, string];
  /** 3 titles ("Por que voce vai amar"). */
  amarCards: readonly [string, string, string];
  /** 2 title+body cards. */
  amarDetailCards: readonly [{ title: string; body: string }, { title: string; body: string }];
  /** 5 rows -- Especificacoes table. */
  specsRows: readonly [
    readonly [string, string],
    readonly [string, string],
    readonly [string, string],
    readonly [string, string],
    readonly [string, string],
  ];
  /** 3 FAQ pairs. */
  faq: readonly [{ q: string; a: string }, { q: string; a: string }, { q: string; a: string }];
  price: string;
  footerBrandLine: string;
  footerSourcesLine: string;
}

const AD_CATALOG_FLAVOR_EXT: Record<FixtureFlavorKey, AdCatalogFlavorExt> = {
  retail: {
    title: "Donut Gato 3 Em 1 Toca Cama Tunel Dobrável Zíper Casa Feltro | Minha Loja",
    metaDescription: "Donut Premium 3 em 1: o ninho dobravel com ziper que combina com a casa. R$ 68,42.",
    brandName: "Minha Loja",
    brandTag: "O marketplace do tutor de gato",
    heroEyebrow: "Donut Gato 3 Em 1 Toca Cama Tunel Dobrável Zíper Casa Feltro",
    heroH1: "Refugio, tunel e cama numa peca so",
    heroImg: "https://http2.mlstatic.com/D_648677-MLB98009076874_112025-O.jpg",
    galleryImgs: [
      "https://http2.mlstatic.com/D_677733-MLB83388336596_042025-O.jpg",
      "https://http2.mlstatic.com/D_918273-MLB83388277478_042025-O.jpg",
      "https://http2.mlstatic.com/D_914341-MLB83388336598_042025-O.jpg",
      "https://http2.mlstatic.com/D_821870-MLB83680438149_042025-O.jpg",
      "https://http2.mlstatic.com/D_818098-MLB83388160666_042025-O.jpg",
    ],
    bodyLead:
      "Cama túnel para gatos Donut Premium — conforto 3 em 1 Refúgio, túnel e cama em uma peça dobrável, com zíper perimetral, toque macio em algodão e poliéster e design neutro que harmoniza com a casa. A cama túnel para gatos em formato donut cria um ninho protegido que respeita o instinto felino de controlar luz, cheiros e ruídos. Resultado prático: fácil de limpar, resistente à água no dia a dia, leve para mover e compacta para guardar. Dimensões 50×50×20 cm, ideal para gatos de pequeno e médio porte, nas cores cinza claro e cinza escuro. Uso realista: resistente à água não significa à prova d’água. Evite imersão; limpe com pano úmido e sabão neutro e seque à sombra. Por que funciona: gatos gostam de toca e esconderijo. O corpo circular limita estímulos, traz sensação de privacidade, ajuda no relaxamento e no bem-estar. A base estável e acolchoada convida ao descanso, soneca e cochilo, enquanto o zíper facilita a higiene e a ventilação, mantendo o ambiente organizado. Benefícios funcionais e emocionais: * Produto 3 em 1, funcionando como toca, túnel e cama. * Zíper perimetral que abre por completo para limpeza fácil, montagem e desmontagem sem esforço. * Estrutura dobrável e leve para guardar em kitnet, loft ou apartamento. * Resistência a respingos de água, ajudando a controlar odores e pelos soltos. * Design minimalista em cores neutras que combina com sala, quarto e escritório. * Conforto com maciez, ergonomia e acolhimento para filhote, adulto e sênior. * Durabilidade com costura reforçada e materiais respiráveis que permitem boa circulação de ar. Especificações técnicas: Formato circular tipo donut, redondo. Materiais: algodão e poliéster de toque suave e antialérgico. Fechamento por zíper perimetral com fecho protegido. Estrutura dobrável, empilhável e estável. Dimensões: 50×50×20 cm. Peso aproximado: 900 g. Cores: cinza claro e cinza escuro. Indicação: gatos domésticos de pequeno e médio porte, como persa, siamês e SRD. Como usar: monte unindo as partes pelo zíper até o fechamento completo. Posicione em canto tranquilo, perto da janela sem sol direto ou ao lado do sofá. Convide o gato com manta favorita ou petisco para transferência de cheiro e adaptação. Cuidados e limpeza: use pano úmido com sabão neutro; para lavagem manual utilize água fria, molho leve e enxágue rápido. Evite alvejantes, solventes, secador quente e imersão total. Retire pelos com rolinho ou aspirador leve. Seque à sombra em varal e guarde dobrado em local seco e arejado. O que vem na caixa: 1 cama túnel para gatos Donut Premium na cor escolhida. FAQ: Serve para gatos grandes? Indicada para pequeno e médio porte. Compare as medidas 50×50×20 cm com o seu felino. Posso lavar na máquina? Prefira limpeza manual. Ela desliza no piso? Em piso seco ou sobre tapete a base tende a não escorregar. Ajuda em ansiedade e timidez? O formato em toca e a privacidade favorecem adaptação e reduzem estresse. É barulhenta? A estrutura é silenciosa e as costuras firmes evitam ruídos. Tem troca e devolução? Sim, conforme políticas do marketplace e garantia do vendedor. Sobre o vendedor: loja especialista em acessórios para felinos, com envio rápido, rastreio e embalagem reforçada para garantir a integridade do produto. Atendimento humano para suporte antes e depois da compra. Políticas essenciais: envio em até 24 a 48 horas úteis após confirmação. Devolução por arrependimento em até 7 dias com nota fiscal, embalagem original e produto sem uso. Garantia de 30 dias contra defeitos de fabricação. Atendimento via chat do marketplace e e-mail em horário comercial. CTA: dê ao seu felino um refúgio acolhedor sem poluir a decoração. Escolha a cor que combina com sua casa e garanta a cama túnel para gatos Donut Premium agora. Buscas relacionadas: cama túnel para gatos, toca para gato, cama donut gato, casa de gato dobrável, cama para gato com zíper, cama para felinos, toca felina 3 em 1, abrigo para gato redondo, casinha para gato resistente à água, cama de gato cinza, donut gato, cama pet circular, ninho para gato, cama para gato fácil de limpar, túnel de descanso felino, cama túnel para gatos 3 em 1 com zíper, cama para gato dobrável resistente à água, toca para gatos formato donut cinza, casa de gato dobrável para apartamento, cama de gato fácil de limpar pano úmido, cama para felino pequeno 50x50x20, refúgio felino para reduzir estresse, cama túnel para gato com design clean, casinha de gato que combina com sala, toca de gato compacta para guardar, cama de gato com zíper perimetral, ninho para gatos com tecido macio, túnel felino para brincar e dormir, cama donut gato confortável e leve, cama de gato para clima frio e quente, abrigo de gato com montagem rápida, cama para gato resistente a respingos, toca de gato para filhotes e adultos, cama de gato ideal para espaços pequenos, cama para gato decoração minimalista, cama túnel felina fácil de higienizar, casinha de gato que dobra e guarda, cama para gato com garantia 30 dias, cama donut para gatos com duas cores, cama para gato confortável preço justo, toca e cama para gatos em uma peça. Vocabulário adicional: abrigo, felino, ninho, toca, casinha, refúgio, esconderijo, descanso, soneca, cochilo, relaxamento, bem-estar, aconchego, maciez, acolchoado, espuma, recheio, algodão, poliéster, durável, robusto, leveza, ergonomia, antiderrapante, lavável, higiênico, fecho, costura, reforçada, circulação, ventilação, respirável, isolamento, silencioso, privacidade, segurança, calmante, antiestresse, brincadeira, exploração, curiosidade, caixa, caverna, redondo, circular, geometria, design, moderno, minimalista, neutro, decorativo, sofisticado, ambiente, sala, quarto, home, escritório, kitnet, varanda, cantinho, tapete, piso, madeira, cerâmica, laminado, antialérgico, pet, bichano, felpudo, filhote, adulto, sênior, porte, pequeno, médio, confortável, suave, quente, acolhedor, inverno, verão, autonomia, território, cheiro, adaptação, rotina, hábito, uso, cotidiano, praticidade, organização, compactação, armazenamento, empilhável, montagem, desmontagem, manual, higiene, pano, sabão, discreto, secagem, rápida, garantia, qualidade, custo-benefício, presente, tutor, família, decoração, cinza, grafite, claro, escuro, medidas, 50x50x20, leve, medida, dimensão, diâmetro, altura, largura, peso, capacidade, raça, persa, siamês, doméstico, comportamento, territorial, ansiedade, timidez, sociável, interação, sensorial, olfato, textura, trama, acabamento, forração, acolhimento, toque, mimo, carinho, vínculo, conexão, dormitório, canto, organizador, arrumação, harmonia, visual, minimalismo, escandinavo, decor, apartamento, loft, cobertura, janela, sofá, estante, manta, almofada, raspador, arranhador, brinquedo, varinha, bolinha, catnip, petisco, comedouro, bebedouro, transporte, higienizador, desinfetante, multiuso, odores, pelagem, pelos, aspirador, vassoura, paninho, esponja, balde, bacia, lavagem, enxágue, cuidado, secador, varal, iluminação, luz, sombra, fotografia, presenteáveis, aniversário, natal, adoção, resgate, veterinário, consulta, pós-operatório, recuperação, logística, envio, rastreio, embalagem, proteção, integridade, prazo, suporte, atendimento, troca, devolução, garantia estendida, nota, fiscal, código, sku, gtin, origem, importado, nacional",
    bodySecond:
      "Todo gato procura um esconderijo: um lugar fechado onde ele decide quem entra, quanta luz chega e que barulho passa. A cama túnel Donut entrega exatamente esse refúgio, em três formatos numa única peça: toca, túnel e cama. O corpo circular limita os estímulos e traz sensação de privacidade, que ajuda no relaxamento e no bem-estar. O toque é macio, em algodão e poliéster, e o zíper perimetral abre por completo para limpar, montar e desmontar sem esforço. A estrutura é dobrável e leve, fácil de guardar em apartamento, kitnet ou loft. Mede 50 x 50 x 20 cm e atende gatos de pequeno e médio porte. Uso realista: resistente à água não significa à prova d&#x27;água. Evite imersão, limpe com pano úmido e sabão neutro e seque à sombra. Em cinza claro ou cinza escuro, o design minimalista combina com sala, quarto e escritório. Produto é meio: o refúgio acolhe, e a rotina tranquila faz o resto.",
    features: [
      "Formato circular tipo donut",
      "Fechamento por zíper perimetral",
      "Estrutura dobrável e empilhável",
      "Dimensões: 50 x 50 x 20 cm",
      "Cores: cinza claro e cinza escuro",
      "Para gatos de pequeno e médio porte",
    ],
    whyText: "O formato em toca limita os estímulos ao redor e traz privacidade, o que favorece o relaxamento do gato. A base acolchoada convida ao descanso e o zíper facilita a higiene.",
    entregaCards: [
      "Três usos em uma peça: toca, túnel e cama",
      "Zíper perimetral que abre por completo para limpeza fácil",
      "Dobrável e leve para guardar em apartamento ou kitnet",
      "Resistente a respingos, ajuda a controlar odores e pelos",
      "Mede 50 x 50 x 20 cm, para gatos de pequeno e médio porte",
      "Cores neutras (cinza claro e cinza escuro) que combinam com a casa",
    ],
    amarCards: [
      "Cria um refúgio só dele, que acolhe e traz privacidade",
      "Um cantinho que ajuda o gato a relaxar e se sentir seguro",
      "Conforto que combina com a decoração, sem poluir o ambiente",
    ],
    amarDetailCards: [
      { title: "Tres usos, um lugar so do seu gato", body: "Toca + tunel + cama dobravel, com ziper perimetral para limpeza facil." },
      { title: "Um cantinho que respeita o instinto felino", body: "O corpo circular traz privacidade e ajuda o gato a relaxar de verdade." },
    ],
    specsRows: [
      ["Dimensoes", "50 x 50 x 20 cm"],
      ["Peso", "450 g"],
      ["Materiais", "Algodão, Poliéster"],
      ["Marca", "Minha Loja"],
      ["SKU", "CB3603"],
    ],
    faq: [
      { q: "Serve para gatos grandes?", a: "É indicada para pequeno e médio porte. Compare as medidas 50 x 50 x 20 cm com o seu felino antes de escolher." },
      { q: "É à prova d&#x27;água?", a: "Não. Ela é resistente a respingos no dia a dia, mas resistente à água não significa à prova d&#x27;água. Evite imersão e prefira limpar com pano úmido." },
      { q: "Ajuda em ansiedade e timidez?", a: "O formato em toca e a privacidade favorecem a adaptação e ajudam a reduzir o estresse." },
    ],
    price: "R$ 68,42",
    footerBrandLine: "Anuncio de Minha Loja - CEXAI product_ad mold",
    footerSourcesLine: "Fontes: catalogo da loja (read-only)",
  },
  services: {
    title: "Pacote de Suporte Tecnico Mensal -- SLA por Escrito e Atendimento 24/7 | Minha Empresa",
    metaDescription: "Suporte de TI mensal com SLA por escrito e atendimento remoto 24/7. R$ 397/mes.",
    brandName: "Minha Empresa",
    brandTag: "Suporte de TI que sua empresa pode confiar",
    heroEyebrow: "Pacote de Suporte Tecnico Mensal -- SLA por Escrito e Atendimento 24/7",
    heroH1: "Suporte que sua equipe de TI vai confiar",
    heroImg: PLACEHOLDER_IMG,
    galleryImgs: [PLACEHOLDER_IMG, PLACEHOLDER_IMG, PLACEHOLDER_IMG, PLACEHOLDER_IMG, PLACEHOLDER_IMG],
    bodyLead:
      "Pacote de Suporte Tecnico Mensal -- confiança 3 em 1: monitoramento, atendimento e prevenção numa única assinatura, com SLA por escrito, onboarding guiado em 48h e um relatório executivo que mostra o que foi resolvido. O pacote mensal cria uma rede de segurança que respeita o ritmo real de uma empresa pequena ou média: sem TI interno, sem chamado perdido, sem surpresa na fatura. Resultado prático: chamado crítico respondido em 2h, auditoria de segurança gratis na primeira reunião, e um time que conhece a sua operação antes do primeiro incidente. Dimensionado para empresas de 10 a 200 funcionários, com opção de escalar conforme o crescimento. Uso realista: SLA por escrito não significa zero incidente -- significa resposta garantida e escalonamento automático quando o problema aparece. Por que funciona: toda empresa pequena teme o chamado que ninguém responde. O SLA por escrito remove essa incerteza, o onboarding guiado elimina a curva de aprendizado, e o relatório executivo mensal mantem a liderança no controle sem precisar entender de TI. Benefícios funcionais e estratégicos: * Pacote 3 em 1, funcionando como monitoramento, atendimento e prevenção. * SLA por escrito com escalonamento automático para chamado crítico. * Onboarding guiado e leve, pronto em 48 horas uteis. * Auditoria de segurança gratuita que identifica risco antes do incidente. * Relatório executivo mensal que traduz TI em decisão de negócio. * Confiabilidade com equipe fixa e canal de atendimento único. Especificações técnicas: Modelo de contrato mensal, renovável. Cobertura: estações, servidores e rede corporativa. Ativação por agente de monitoramento remoto (RMM) com heartbeat contínuo. Estrutura escalável, com upgrade de plano sem interrupção. SLA: crítico 2h, alto 8h, normal 24h uteis. Onboarding: ate 48 horas uteis. Cores/identidade: relatório com a marca do cliente. Indicação: empresas de pequeno e médio porte, de qualquer setor, sem TI interno dedicado. Como começar: agende a reunião de kickoff, confirme o escopo do contrato e receba o token de ativação do agente por e-mail. Posicione o suporte como parceiro, não fornecedor -- envolva o time desde a primeira semana. Cuidados e acompanhamento: revise o relatório executivo mensalmente; audite os chamados abertos semanalmente; atualize o escopo do contrato a cada renovação anual. Evite postergar a auditoria de segurança -- o risco cresce com o tempo sem revisão. O que vem incluso: onboarding completo, agente de monitoramento, SLA por escrito e relatório executivo mensal. FAQ: Atende empresa pequena? Dimensionado para 10 a 50 funcionários, com opção de escalar. O SLA é mesmo garantido? Sim, por escrito, com escalonamento automático. Ajuda com auditoria de segurança? Sim, gratuita na primeira reunião. Tem troca ou cancelamento? Sim, conforme o contrato e a política de fidelidade. Sobre a empresa: especialista em suporte de TI terceirizado, com atendimento remoto e presencial quando necessário. Atendimento humano para suporte antes e depois da contratação. Políticas essenciais: ativação em ate 48 horas uteis após a confirmação do contrato. Cancelamento conforme aviso previo contratual. Garantia de SLA por escrito durante toda a vigência. Atendimento via portal do cliente e telefone em horário comercial estendido. CTA: de a sua empresa um suporte de TI que responde de verdade. Fale com um especialista e garanta o Pacote de Suporte Tecnico Mensal agora. Buscas relacionadas: suporte de ti para empresas, suporte técnico remoto, consultoria de ti terceirizada, suporte de ti com sla, helpdesk corporativo pme, suporte de ti mensal, monitoramento remoto de servidores, suporte técnico 24 horas, suporte de ti para pequenas empresas, outsourcing de ti, gestão de infraestrutura de ti, suporte remoto para escritório, plano de suporte técnico empresarial, contrato de suporte de ti mensal, suporte de ti com onboarding rápido, auditoria de segurança da informação, suporte de ti confiável, helpdesk terceirizado, suporte técnico corporativo com sla, gestão de chamados de ti, suporte remoto para pme, suporte de ti com relatório executivo, terceirização de suporte técnico. Vocabulário adicional: confiabilidade, disponibilidade, monitoramento, prevenção, escalonamento, atendimento, chamado, incidente, severidade, criticidade, resposta, resolução, onboarding, ativação, contrato, renovação, escopo, portal, dashboard, indicador, relatório, executivo, segurança, auditoria, risco, vulnerabilidade, patch, atualização, backup, restauração, continuidade, operação, infraestrutura, rede, servidor, estação, dispositivo, agente, heartbeat, telemetria, alerta, notificação, plantão, equipe, time, especialista, técnico, consultor, gestor, liderança, decisão, negócio, operacional, estratégico, terceirização, outsourcing, parceria, confiança, transparencia, previsibilidade, custo, investimento, retorno, produtividade, eficiência, escalabilidade, crescimento, expansão, filial, matriz, sede, escritório, corporativo, empresarial, PME, porte, setor, indústria, comércio, serviço",
    bodySecond:
      "Toda empresa pequena teme o chamado que ninguém responde a tempo. O Pacote de Suporte Tecnico Mensal entrega exatamente essa confiança, em três frentes numa única assinatura: monitoramento, atendimento e prevenção. O SLA por escrito remove a incerteza e traz escalonamento automático, o que ajuda no planejamento e na tranquilidade da liderança. O atendimento é remoto 24/7, com onboarding guiado pronto em 48 horas úteis. A estrutura é escalável, fácil de ajustar conforme a empresa cresce. Cobre estações, servidores e rede corporativa, e atende empresas de 10 a 200 funcionários. Uso realista: SLA por escrito não elimina todo incidente -- garante resposta e escalonamento quando o problema aparece. Com relatório executivo mensal, o pacote se adapta a rotina real de qualquer empresa pequena ou média. Serviço é meio: o suporte acolhe, e a operação estável faz o resto.",
    features: [
      "SLA por escrito com resposta garantida",
      "Atendimento remoto 24 horas por dia",
      "Onboarding guiado em ate 48 horas",
      "Auditoria de segurança gratuita na 1a reunião",
      "Relatório executivo mensal de indicadores",
      "Dimensionado para 10 a 200 funcionários",
    ],
    whyText: "O SLA por escrito remove a incerteza do atendimento e a auditoria de segurança identifica riscos antes que virem incidente. O relatório executivo mantem a liderança no controle.",
    entregaCards: [
      "Três frentes em um pacote: monitoramento, atendimento e prevenção",
      "SLA por escrito com escalonamento automático para chamado crítico",
      "Onboarding guiado, pronto em 48 horas uteis",
      "Auditoria de segurança gratuita que identifica risco cedo",
      "Dimensionado para empresas de 10 a 200 funcionários",
      "Relatório executivo mensal que traduz TI em decisão de negócio",
    ],
    amarCards: [
      "Cria uma rede de segurança que a sua equipe confia",
      "Um parceiro que responde antes do problema crescer",
      "Confiabilidade que combina com o ritmo do seu negócio",
    ],
    amarDetailCards: [
      { title: "Três frentes, um só parceiro de TI", body: "Monitoramento + atendimento + prevenção, com SLA por escrito para resposta garantida." },
      { title: "Um time que conhece a sua operação", body: "O onboarding guiado e o relatório mensal ajudam sua equipe a confiar de verdade." },
    ],
    specsRows: [
      ["Tempo de resposta (crítico)", "2 horas"],
      ["Disponibilidade", "24/7"],
      ["Onboarding", "48 horas uteis"],
      ["Marca", "Minha Empresa"],
      ["Código do contrato", "SUP-TEC-0397"],
    ],
    faq: [
      { q: "Atende empresa pequena?", a: "E dimensionado para empresas de 10 a 50 funcionários, com opção de escalar conforme o crescimento." },
      { q: "O SLA é mesmo garantido?", a: "Sim, por escrito. Chamado crítico tem resposta em 2h; se estourar, escalona automaticamente." },
      { q: "Ajuda com auditoria de segurança?", a: "Sim. A auditoria de segurança gratuita acontece ja na primeira reunião de onboarding." },
    ],
    price: "R$ 397/mes",
    footerBrandLine: "Anuncio de Minha Empresa - CEXAI product_ad mold",
    footerSourcesLine: "Fontes: catalogo de serviços (read-only)",
  },
  neutral: {
    title: "Produto Exemplo A -- Garantia Estendida e Suporte Pos-Venda | Minha Empresa",
    metaDescription: "Produto Exemplo A com garantia estendida e suporte pos-venda. R$ 99.",
    brandName: "Minha Empresa",
    brandTag: "Qualidade premium para clientes exigentes",
    heroEyebrow: "Produto Exemplo A -- Garantia Estendida e Suporte Pos-Venda",
    heroH1: "O produto que seu dia a dia precisa",
    heroImg: PLACEHOLDER_IMG,
    galleryImgs: [PLACEHOLDER_IMG, PLACEHOLDER_IMG, PLACEHOLDER_IMG, PLACEHOLDER_IMG, PLACEHOLDER_IMG],
    bodyLead:
      "Produto Exemplo A -- qualidade 3 em 1: durabilidade, suporte e conveniência numa única compra, com garantia estendida, entrega rápida e um acabamento pensado para o uso diário. O produto cria uma rotina confiável que respeita o ritmo real de quem compra: sem defeito recorrente, sem demora na entrega, sem letra miuda na garantia. Resultado prático: fácil de usar, resistente ao uso diário, leve para transportar e compacto para guardar. Dimensões 50x50x20 cm, ideal para uso doméstico ou profissional, nas cores cinza claro e cinza escuro. Uso realista: garantia estendida não significa produto indestrutível -- significa cobertura real contra defeito de fabricação. Por que funciona: todo cliente teme o produto que quebra cedo demais. A garantia estendida remove essa incerteza, o suporte pos-venda resolve dúvidas sem enrolação, e o acabamento reforçado aguenta o uso diário sem perder qualidade. Benefícios funcionais e emocionais: * Produto 3 em 1, funcionando como item principal, reposição e upgrade. * Acabamento reforçado que aguenta o uso diário sem desgastar cedo. * Estrutura leve e compacta para guardar em qualquer ambiente. * Resistência a uso intenso, ajudando a evitar substituição frequente. * Design neutro em cores discretas que combina com qualquer decoração. * Durabilidade com materiais testados que garantem uso prolongado. Especificações técnicas: Formato compacto e ergonomico. Materiais duráveis e testados, com acabamento antialérgico. Fechamento resistente que facilita manutenção e limpeza. Estrutura empilhável e estável. Dimensões: 50x50x20 cm. Peso aproximado: 450 g. Cores: cinza claro e cinza escuro. Indicação: uso doméstico ou profissional, para clientes que buscam durabilidade. Como usar: siga o manual de instruções ate a montagem completa. Posicione em local adequado ao uso pretendido. Cuidados e limpeza: use pano úmido com sabão neutro; evite produtos abrasivos e imersão total. Retire sujeira com pano seco. Guarde em local seco e arejado. O que vem na caixa: 1 unidade do Produto Exemplo A na cor escolhida. FAQ: Serve para uso intenso? Indicado para uso diário doméstico ou profissional. Compare as especificações com a sua necessidade. Tem garantia? Sim, garantia estendida de 30 dias contra defeito de fabricação. Ele é fácil de limpar? Sim, basta pano úmido com sabão neutro. Ajuda a durar mais? O acabamento reforçado favorece a durabilidade e reduz substituição frequente. É difícil de montar? A estrutura é simples e as instruções evitam dúvidas. Tem troca e devolução? Sim, conforme políticas do marketplace e garantia do vendedor. Sobre a empresa: especialista em produtos duráveis, com envio rápido, rastreio e embalagem reforçada para garantir a integridade do produto. Atendimento humano para suporte antes e depois da compra. Políticas essenciais: envio em ate 24 a 48 horas uteis após confirmação. Devolução por arrependimento em ate 7 dias com nota fiscal, embalagem original e produto sem uso. Garantia de 30 dias contra defeitos de fabricação. Atendimento via chat e e-mail em horário comercial. CTA: garanta um produto que aguenta o seu dia a dia sem perder qualidade. Escolha a cor que combina com você e garanta o Produto Exemplo A agora. Buscas relacionadas: produto exemplo, produto durável, produto com garantia estendida, produto fácil de limpar, produto compacto para guardar, produto para uso diário, produto com entrega rápida, produto resistente ao uso intenso, produto com acabamento reforçado, produto neutro para qualquer ambiente, produto com suporte pos-venda, produto confiável custo benefício. Vocabulário adicional: durabilidade, qualidade, garantia, suporte, conveniência, resistência, acabamento, robusto, leveza, ergonomia, antiderrapante, lavável, higiênico, fecho, costura, reforçada, circulação, isolamento, silencioso, segurança, praticidade, organização, compactação, armazenamento, empilhável, montagem, desmontagem, manual, higiene, pano, sabão, discreto, secagem, rápida, qualidade, custo-benefício, presente, família, decoração, cinza, claro, escuro, medidas, leve, medida, dimensão, altura, largura, peso, capacidade, doméstico, uso, cotidiano, adaptação, rotina, hábito, textura, acabamento, toque, conexão, organizador, arrumação, harmonia, visual, minimalismo, decor, apartamento, envio, rastreio, embalagem, proteção, integridade, prazo, atendimento, troca, devolução, garantia estendida, nota, fiscal, código, sku, origem, nacional",
    bodySecond:
      "Todo cliente teme o produto que quebra cedo demais. O Produto Exemplo A entrega exatamente essa confiança, em três frentes numa única compra: durabilidade, suporte e conveniência. O acabamento reforçado limita o desgaste e traz sensação de qualidade, que ajuda na decisão de compra e na satisfação pos-venda. O toque é agradável, em materiais testados, e a estrutura facilita a limpeza e manutenção no dia a dia. A estrutura é compacta e leve, fácil de guardar em qualquer ambiente. Mede 50 x 50 x 20 cm e atende uso doméstico ou profissional. Uso realista: garantia estendida não elimina todo desgaste -- garante cobertura real contra defeito de fabricação. Em cinza claro ou cinza escuro, o design neutro combina com qualquer decoração. Produto é meio: a qualidade acolhe, e o uso diário tranquilo faz o resto.",
    features: [
      "Garantia estendida de 30 dias",
      "Suporte pos-venda incluso",
      "Entrega rápida em ate 24 a 48h",
      "Frete gratis acima de um valor mínimo",
      "Materiais duráveis e testados",
      "Feito para uso diário intenso",
    ],
    whyText: "O acabamento reforçado limita o desgaste no uso diário e traz sensação de qualidade. A garantia estendida cobre defeito real de fabricação e o suporte pos-venda facilita a manutenção.",
    entregaCards: [
      "Três frentes em um produto: durabilidade, suporte e conveniência",
      "Garantia estendida que cobre defeito real de fabricação",
      "Entrega rápida, fácil de receber e usar no mesmo dia",
      "Resistente a uso intenso, ajuda a evitar substituição frequente",
      "Mede 50 x 50 x 20 cm, para uso doméstico ou profissional",
      "Cores neutras (cinza claro e cinza escuro) que combinam com qualquer ambiente",
    ],
    amarCards: [
      "Cria uma rotina confiável para o seu dia a dia",
      "Um produto que aguenta o uso intenso sem perder qualidade",
      "Conforto que combina com qualquer decoração, sem poluir o ambiente",
    ],
    amarDetailCards: [
      { title: "Três frentes, um só produto", body: "Durabilidade + suporte + conveniência, com garantia estendida para uso tranquilo." },
      { title: "Um produto que respeita o seu uso diário", body: "O acabamento reforçado traz confiança e ajuda a evitar substituição frequente." },
    ],
    specsRows: [
      ["Dimensões", "50 x 50 x 20 cm"],
      ["Peso", "450 g"],
      ["Materiais", "Materiais duráveis testados"],
      ["Marca", "Minha Empresa"],
      ["SKU", "PEX-A-0099"],
    ],
    faq: [
      { q: "Serve para uso intenso?", a: "Indicado para uso diário doméstico ou profissional. Compare as especificações com a sua necessidade antes de escolher." },
      { q: "Tem garantia?", a: "Sim. Garantia estendida de 30 dias contra defeito de fabricação, além da garantia legal." },
      { q: "Ele é fácil de limpar?", a: "Sim. Basta pano úmido com sabão neutro; evite produtos abrasivos e imersão total." },
    ],
    price: "R$ 99",
    footerBrandLine: "Anuncio de Minha Empresa - CEXAI product_ad mold",
    footerSourcesLine: "Fontes: catalogo da loja (read-only)",
  },
};

const acExt = AD_CATALOG_FLAVOR_EXT[activeFlavorKey];

export const AD_CATALOG_SAMPLE_HTML = String.raw`<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index, follow">
<!-- Content-Security-Policy: serve this doc with a CSP HEADER (not a meta) supplied
     by the caller, e.g.  default-src 'self'; img-src https: data:; style-src
     'unsafe-inline'; script-src 'none'; base-uri 'none'; form-action 'self'
     (this mold ships NO executable script; the JSON-LD below is inert data). -->
<title>${acExt.title}</title>
<meta name="description" content="${acExt.metaDescription}">
<link rel="canonical" href="https://example.com">
<meta property="og:type" content="product">
<meta property="og:title" content="${acExt.title}">
<meta property="og:description" content="${acExt.metaDescription}">
<meta property="og:site_name" content="${acExt.brandName}">
<meta property="og:url" content="https://example.com">
<meta property="og:image" content="${acExt.heroImg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${acExt.title}">
<meta name="twitter:description" content="${acExt.metaDescription}">
<meta name="twitter:image" content="${acExt.heroImg}">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product","name":"${acExt.heroEyebrow}","description":"${acExt.metaDescription}","image":["${acExt.heroImg}"],"brand":{"@type":"Brand","name":"${acExt.brandName}"},"offers":{"@type":"Offer","priceCurrency":"BRL","price":"${acExt.price.replace(/[^0-9,]/g, "").replace(",", ".")}","availability":"https://schema.org/InStock"}}</script>
<style>
:root{--background:0 0% 100%;--foreground:213 47% 12%;--card:0 0% 98%;--card-foreground:213 47% 12%;--popover:0 0% 100%;--popover-foreground:213 47% 12%;--primary:174 68% 50%;--primary-foreground:0 0% 100%;--secondary:213 35% 18%;--secondary-foreground:0 0% 100%;--muted:210 20% 96%;--muted-foreground:213 15% 45%;--accent:174 68% 50%;--accent-foreground:0 0% 100%;--border:210 20% 88%;--input:210 20% 88%;--ring:174 68% 50%;--brand:174 68% 50%;--brand-foreground:0 0% 100%;--brand-muted:174 30% 92%;--highlight:42 100% 50%;--highlight-foreground:0 0% 10%;--highlight-muted:42 80% 93%;--radius:0.75rem;--font-family-base:Inter, -apple-system, Segoe UI, sans-serif}
*{box-sizing:border-box}html,body{margin:0;padding:0}body{background:hsl(var(--background,0 0% 100%));color:hsl(var(--foreground,213 47% 12%));font-family:var(--font-family-base,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif);line-height:1.55;-webkit-font-smoothing:antialiased}.ad-doc{max-width:720px;margin:0 auto;padding:0 0 32px}section{padding:28px 20px;border-bottom:1px solid hsl(var(--border,210 20% 88%))}section:last-child{border-bottom:0}h1,h2,h3{margin:0 0 12px;line-height:1.2}h1{font-size:1.9rem;letter-spacing:-0.01em}h2{font-size:1.3rem}p{margin:0 0 12px}img{max-width:100%;height:auto;display:block}.ad-brandbar{display:flex;align-items:center;gap:12px;padding:14px 20px;background:hsl(var(--brand,174 68% 40%));color:hsl(var(--brand-foreground,0 0% 100%));position:sticky;top:0;z-index:10}.ad-brandbar img{height:34px;max-width:160px;object-fit:contain;border-radius:6px}.ad-brandbar .ad-bname{font-size:1.15rem;font-weight:700;line-height:1.15}.ad-brandbar .ad-btag{display:block;font-size:.72rem;opacity:.85;margin-top:2px;font-weight:400}.ad-hero{text-align:center}.ad-hero .ad-sub{font-size:1.05rem;color:hsl(var(--muted-foreground,213 15% 45%));max-width:46ch;margin:0 auto 18px}.ad-hero .ad-media{margin:18px 0}.ad-discount-badge{display:inline-block;background:hsl(var(--highlight,42 100% 50%));color:hsl(var(--highlight-foreground,0 0% 10%));font-weight:700;font-size:.85rem;padding:5px 12px;border-radius:999px;margin-bottom:14px}.ad-cta{display:inline-block;width:100%;max-width:360px;text-align:center;background:hsl(var(--primary,174 68% 40%));color:hsl(var(--primary-foreground,0 0% 100%));font-size:1.1rem;font-weight:700;text-decoration:none;padding:15px 26px;border-radius:var(--radius,0.625rem);border:0;cursor:pointer;box-shadow:0 6px 18px -6px hsl(var(--primary,174 68% 40%) / .55)}.ad-cta:hover{filter:brightness(1.06)}.ad-cta:focus-visible{outline:3px solid hsl(var(--ring,174 68% 40%));outline-offset:3px}.ad-cta-sub{display:block;font-size:.8rem;color:hsl(var(--muted-foreground,213 15% 45%));margin-top:8px}.ad-value-grid{display:grid;grid-template-columns:1fr;gap:14px;margin-top:6px}.ad-vcard{display:flex;gap:12px;align-items:flex-start;background:hsl(var(--card,0 0% 98%));border:1px solid hsl(var(--border,210 20% 88%));border-radius:var(--radius,0.625rem);padding:14px 16px}.ad-vcard .ad-vchk{flex:0 0 auto;width:26px;height:26px;border-radius:999px;background:hsl(var(--brand,174 68% 40%));color:hsl(var(--brand-foreground,0 0% 100%));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9rem}.ad-vcard .ad-vbody{flex:1}.ad-vcard .ad-vtitle{font-weight:700;margin:0 0 3px}.ad-vcard p{margin:0;font-size:.92rem;color:hsl(var(--muted-foreground,213 15% 45%))}.ad-proof{text-align:center;background:hsl(var(--muted,0 0% 98%))}.ad-rating{font-size:1.6rem;font-weight:800;letter-spacing:.04em;color:hsl(var(--highlight-foreground,213 47% 12%))}.ad-stars{color:hsl(var(--highlight,42 100% 50%));font-size:1.3rem;letter-spacing:.1em}.ad-testi{display:grid;grid-template-columns:1fr;gap:12px;margin-top:16px;text-align:left}.ad-quote{background:hsl(var(--card,0 0% 98%));border-left:4px solid hsl(var(--brand,174 68% 40%));border-radius:8px;padding:12px 14px}.ad-quote blockquote{margin:0 0 6px;font-style:italic}.ad-quote cite{font-size:.82rem;color:hsl(var(--muted-foreground,213 15% 45%));font-style:normal}.ad-offer{text-align:center;background:hsl(var(--secondary,213 35% 18%));color:hsl(var(--secondary-foreground,0 0% 100%))}.ad-offer h2{color:inherit}.ad-price{font-size:2.4rem;font-weight:800;line-height:1}.ad-price-old{font-size:1.1rem;text-decoration:line-through;opacity:.7;margin-left:8px;font-weight:500}.ad-install{font-size:.95rem;opacity:.9;margin-top:6px}.ad-offer-meta{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0}.ad-chip{font-size:.82rem;background:hsl(var(--card,0 0% 98%) / .15);border:1px solid currentColor;border-radius:999px;padding:5px 12px}.ad-urgency{font-weight:700;color:hsl(var(--highlight,42 100% 50%));margin-top:6px}.ad-specs table{border-collapse:collapse;width:100%;font-size:.92rem}.ad-specs td{padding:9px 10px;border-bottom:1px solid hsl(var(--border,210 20% 88%));vertical-align:top}.ad-specs td:first-child{font-weight:600;width:42%;color:hsl(var(--muted-foreground,213 15% 45%))}.ad-faq details{border:1px solid hsl(var(--border,210 20% 88%));border-radius:var(--radius,0.625rem);padding:2px 14px;margin-bottom:10px;background:hsl(var(--card,0 0% 98%))}.ad-faq summary{cursor:pointer;font-weight:600;padding:11px 0;list-style:revert}.ad-faq details p{margin:0 0 12px;font-size:.92rem;color:hsl(var(--muted-foreground,213 15% 45%))}.ad-ph{display:inline-block;color:hsl(var(--muted-foreground,213 15% 45%));background:hsl(var(--muted,0 0% 98%));border:1px dashed hsl(var(--border,210 20% 88%));border-radius:6px;padding:1px 8px;font-style:italic;font-size:.92em}.ad-slot-empty{border:2px dashed hsl(var(--border,210 20% 88%));border-radius:var(--radius,0.625rem);background:hsl(var(--muted,0 0% 98%));color:hsl(var(--muted-foreground,213 15% 45%));text-align:center;padding:30px 18px;margin:0 auto}.ad-slot-empty strong{display:block;font-size:1rem;margin-bottom:4px}.ad-slot-empty span{font-size:.82rem}.ad-gallery{display:grid;grid-template-columns:1fr 1fr;gap:12px}.ad-gallery figure{margin:0}.ad-gallery img{border-radius:var(--radius,0.625rem);border:1px solid hsl(var(--border,210 20% 88%))}.ad-foot{font:12px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:hsl(var(--muted-foreground,213 15% 45%));text-align:center}.ad-foot .ad-badge{display:inline-block;border-radius:6px;padding:2px 10px;color:#fff;margin-bottom:8px;font-size:.78rem}.ad-foot .ad-badge-real{background:#2e7d32}.ad-foot .ad-badge-sample{background:#b8860b}.ad-cta-wrap{margin-top:6px}@media(min-width:560px){.ad-value-grid{grid-template-columns:1fr 1fr}.ad-testi{grid-template-columns:1fr 1fr}}
.text-display{font-size:clamp(2rem,5vw,4rem);line-height:1.2;letter-spacing:-0.025em;font-weight:800}.text-h1{font-size:clamp(1.75rem,4vw,3rem);line-height:1.2;letter-spacing:-0.025em;font-weight:700}.text-h2{font-size:clamp(1.5rem,3vw,2.25rem);line-height:1.2;letter-spacing:-0.025em;font-weight:600}.text-h3{font-size:clamp(1.25rem,2vw,1.75rem);line-height:1.5;font-weight:600}.text-eyebrow{font-size:.75rem;letter-spacing:.025em;text-transform:uppercase;font-weight:600;color:hsl(var(--brand))}.text-muted-foreground{color:hsl(var(--muted-foreground))}.text-lg{font-size:1.05rem;line-height:1.6}.ad-why{max-width:60ch;margin:0 auto 18px;font-size:1.05rem;line-height:1.6;color:hsl(var(--muted-foreground))}.ad-body p{max-width:62ch}.ad-body .ad-body-lead{font-weight:500;color:hsl(var(--foreground))}.ad-feature-list{margin:6px 0 0;padding:0;list-style:none;display:grid;grid-template-columns:1fr;gap:10px}.ad-feature-list li{position:relative;padding-left:30px;line-height:1.5}.ad-feature-list li::before{content:'+';position:absolute;left:0;top:1px;width:21px;height:21px;border-radius:999px;background:hsl(var(--brand));color:hsl(var(--brand-foreground));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem}.ad-bgroup-title{font-size:1rem;font-weight:700;margin:18px 0 10px;color:hsl(var(--foreground))}@media(min-width:560px){.ad-feature-list{grid-template-columns:1fr 1fr}}.ad-foot-inner{border:0;padding-top:20px}.ad-foot-sources{margin-top:6px}@media print{body{background:#fff;color:#000}.ad-brandbar{position:static;box-shadow:none}.ad-cta,.ad-cta-wrap,.ad-cta-sub,.ad-slot-empty{display:none !important}.ad-discount-badge,.ad-urgency{color:#000}section{border-bottom:1px solid #ccc;break-inside:avoid;page-break-inside:avoid}.ad-hero .ad-media img,.ad-gallery img{max-width:55%;margin:0 auto}.ad-gallery{grid-template-columns:1fr 1fr}@page{margin:1.5cm}}
</style>
</head>
<body>
<main class="ad-doc">
<header class="ad-brandbar" role="banner"><div><span class="ad-bname">${acExt.brandName}</span><span class="ad-btag">${acExt.brandTag}</span></div></header>
<section class="ad-hero"><div class="text-eyebrow">${acExt.heroEyebrow}</div><h1 class="text-display">${acExt.heroH1}</h1><p class="ad-sub text-lg">${acExt.metaDescription}</p><div class="ad-media"><img src="${acExt.heroImg}" alt="${acExt.heroEyebrow} -- foto 1" data-slot-key="hero" data-kind="image" data-editable="true" data-upload-fallback="true"></div><div class="ad-cta-wrap"><a class="ad-cta" href="#comprar" role="button" data-cta-slot="hero">Comprar agora</a></div></section>
<section class="ad-gallery-sec"><h2 class="text-h2">Galeria</h2><div class="ad-gallery"><figure><img src="${acExt.galleryImgs[0]}" alt="${acExt.heroEyebrow} -- foto 2" data-slot-key="gallery_1" data-kind="image" data-editable="true" data-upload-fallback="true"></figure><figure><img src="${acExt.galleryImgs[1]}" alt="${acExt.heroEyebrow} -- foto 3" data-slot-key="gallery_2" data-kind="image" data-editable="true" data-upload-fallback="true"></figure><figure><img src="${acExt.galleryImgs[2]}" alt="${acExt.heroEyebrow} -- foto 4" data-slot-key="gallery_3" data-kind="image" data-editable="true" data-upload-fallback="true"></figure><figure><img src="${acExt.galleryImgs[3]}" alt="${acExt.heroEyebrow} -- foto 5" data-slot-key="gallery_4" data-kind="image" data-editable="true" data-upload-fallback="true"></figure><figure><img src="${acExt.galleryImgs[4]}" alt="${acExt.heroEyebrow} -- foto 6" data-slot-key="gallery_5" data-kind="image" data-editable="true" data-upload-fallback="true"></figure></div></section>
<section class="ad-body"><h2 class="text-h2">Sobre o produto</h2><p class="ad-body-lead text-lg">${acExt.bodyLead}</p><p>${acExt.bodySecond}</p></section>
<section class="ad-features"><h2 class="text-h2">Caracteristicas principais</h2><ul class="ad-feature-list"><li>${acExt.features[0]}</li><li>${acExt.features[1]}</li><li>${acExt.features[2]}</li><li>${acExt.features[3]}</li><li>${acExt.features[4]}</li><li>${acExt.features[5]}</li></ul></section>
<section class="ad-value"><h2 class="text-h2">Por que escolher</h2><p class="ad-why">${acExt.whyText}</p><h3 class="ad-bgroup-title">O que entrega</h3><div class="ad-value-grid"><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.entregaCards[0]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.entregaCards[1]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.entregaCards[2]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.entregaCards[3]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.entregaCards[4]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.entregaCards[5]}</div></div></div></div><h3 class="ad-bgroup-title">Por que voce vai amar</h3><div class="ad-value-grid"><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.amarCards[0]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.amarCards[1]}</div></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.amarCards[2]}</div></div></div></div><div class="ad-value-grid"><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.amarDetailCards[0].title}</div><p>${acExt.amarDetailCards[0].body}</p></div></div><div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span><div class="ad-vbody"><div class="ad-vtitle">${acExt.amarDetailCards[1].title}</div><p>${acExt.amarDetailCards[1].body}</p></div></div></div></section>
<section class="ad-proof"><h2 class="text-h2">Quem comprou aprova</h2><div class="ad-rating"><span class="ad-ph">[preencher: nota media + n de avaliacoes]</span></div><div class="ad-testi"><div class="ad-quote"><blockquote><span class="ad-ph">[preencher: depoimento real de cliente]</span></blockquote></div></div></section>
<section class="ad-offer"><h2 class="text-h2">A oferta</h2><div class="ad-price">${acExt.price}</div><div class="ad-offer-meta"><span class="ad-chip"><span class="ad-ph">[preencher: frete / garantia]</span></span></div><div class="ad-cta-wrap"><a class="ad-cta" href="#comprar" role="button" data-cta-slot="offer">Comprar agora</a></div></section>
<section class="ad-specs"><h2 class="text-h2">Especificacoes</h2><table><tbody><tr><td>${acExt.specsRows[0][0]}</td><td>${acExt.specsRows[0][1]}</td></tr><tr><td>${acExt.specsRows[1][0]}</td><td>${acExt.specsRows[1][1]}</td></tr><tr><td>${acExt.specsRows[2][0]}</td><td>${acExt.specsRows[2][1]}</td></tr><tr><td>${acExt.specsRows[3][0]}</td><td>${acExt.specsRows[3][1]}</td></tr><tr><td>${acExt.specsRows[4][0]}</td><td>${acExt.specsRows[4][1]}</td></tr></tbody></table></section>
<section class="ad-faq"><h2 class="text-h2">Perguntas frequentes</h2><details><summary>${acExt.faq[0].q}</summary><p>${acExt.faq[0].a}</p></details><details><summary>${acExt.faq[1].q}</summary><p>${acExt.faq[1].a}</p></details><details><summary>${acExt.faq[2].q}</summary><p>${acExt.faq[2].a}</p></details></section>
<section class="ad-hero ad-cta2"><h2 class="text-h2">Pronto para comecar?</h2><div class="ad-cta-wrap"><a class="ad-cta" href="#comprar" role="button" data-cta-slot="cta2">Comprar agora</a></div></section>
<footer class="ad-foot" role="contentinfo"><section class="ad-foot-inner"><span class="ad-badge ad-badge-sample">amostra -- dados simulados</span><br>${acExt.footerBrandLine}<div class="ad-foot-sources">${acExt.footerSourcesLine}</div></section></footer>
</main>
</body>
</html>
`;
