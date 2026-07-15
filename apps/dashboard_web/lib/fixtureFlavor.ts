// ----------------------------------------------------------------------------
// FIXTURE FLAVOR -- demo-content vocabulary keyed by the tenant's BUSINESS SHAPE.
//
// THE PROBLEM (register R-012): FIXTURES mode content was hardcoded to a single
// pet-retail demo world (arranhador/gato/PetShop Premium) for EVERY tenant, so a
// services tenant (e.g. an IT-support company) previews the dashboard against a
// cat-tower e-commerce story that has nothing to do with their business.
//
// THE FIX: a small FLAVOR_TABLE keyed by the tenant's business shape -- the SAME
// master discriminator the backend already carries end-to-end:
//   _tools/cex_business_shape.py   detect_business_shape(...).vertical  (Python)
//   apps/public_site/lib/tenantConfig.ts  TenantShape.vertical           (frozen TS contract)
// Both emit exactly two committed values: "retail" | "services". This module
// does NOT invent a third real shape -- it adds ONE honest fallback bucket
// ("neutral") for the absent/uncommitted/unrecognised case, because a fixture
// MUST render something even when no shape was ever detected.
//
//   retail   -> the ORIGINAL pet-retail vocabulary, BYTE-IDENTICAL to the demo
//               content that shipped before this fix (zero regression -- the
//               built-in demo tenant IS vertical=retail today).
//   services -> a generic professional/IT-services vocabulary, tonally aligned
//               with the OTHER fictitious services tenant already sampled in this
//               codebase (lib/brandTheme.ts ORBIT_BRAND_SAMPLE, "Solucoes em
//               Tecnologia"). Template-domain words only -- never a real client
//               claim (never-fabricate discipline).
//   neutral  -> the DEFAULT for an unknown/absent/uncommitted shape. Generic
//               commerce vocabulary -- deliberately NOT pet-specific, so a
//               tenant the detector could not classify never silently inherits
//               the pet-retail demo world.
//
// resolveFlavor(shape) never invents a 4th bucket: any value other than the
// literal "retail" / "services" strings (undefined, "", "ecommerce", a typo, an
// uncommitted detector output) degrades to "neutral".
//
// STRUCTURE PARITY: every flavor entry below carries the SAME shape (same
// array lengths, same object key counts) as the retail original it replaces --
// see fixture-flavor.test.ts. Only the vocabulary STRINGS vary; the markdown
// tables / section counts / field counts the consuming code builds around them
// are untouched.
// ----------------------------------------------------------------------------

export type FixtureFlavorKey = "retail" | "services" | "neutral";

export interface FixtureSeoBlock {
  /** 3 items. */
  headTerms: readonly [string, string, string];
  /** 3 items. */
  longtails: readonly [string, string, string];
  /** 3 items. */
  synonyms: readonly [string, string, string];
  /** 2 items. */
  seoInbound: readonly [string, string];
  /** 2 items. */
  seoOutbound: readonly [string, string];
  /** 3 items. */
  negativeKeywords: readonly [string, string, string];
}

/** One CRM/leads sample row's flavor-owned fields (the rest -- tipo/canal/fonte/
 *  contato/score/status -- are structural and stay identical across flavors). */
export interface FixtureLeadFlavor {
  readonly nome: string;
  readonly sinal: string;
}

export interface FixtureFlavor {
  readonly key: FixtureFlavorKey;
  /** the vertical TAG word stamped on generated artifacts (replaces the old
   *  hardcoded "pet" tag literal). */
  readonly tag: string;
  /** the generic brand/store label used as the default research seed ("Minha Loja"). */
  readonly storeLabel: string;
  readonly productId: string;
  readonly productName: string;
  /** 3 short competitor names (table columns / benchmark rivals). */
  readonly competitors: readonly [string, string, string];
  /** the top competitor's full descriptive name ("X -- Y line"). */
  readonly topCompetitorFull: string;
  /** 3 marketplace/category taxonomy paths (mercadolivre/amazon/magalu-shaped slots). */
  readonly categoryPaths: { readonly a: string; readonly b: string; readonly c: string };
  /** 3 items. */
  readonly gaps: readonly [string, string, string];
  /** 3 items. */
  readonly opportunities: readonly [string, string, string];
  readonly differentiationAngle: string;
  readonly recommendedPositioning: string;
  readonly seo: FixtureSeoBlock;
  // --- research_universe firmographics / market -----------------------------
  readonly legalName: string;
  readonly activityDescription: string;
  readonly segment: string;
  /** 4 items. */
  readonly channels: readonly [string, string, string, string];
  /** the market-sizing bag: SAME key count as the retail original (7 keys).
   *  Both keys and values are flavor vocabulary here (this bag is rendered as
   *  raw label/value pairs -- see universeReportSections -- so the key names
   *  are user-facing demo text, not a code-consumed schema field). */
  readonly market: Readonly<Record<string, string>>;
  readonly appName: string;
  /** 2 items. */
  readonly appReviews: readonly [string, string];
  /** 3 items (subreddit-shaped community tags). */
  readonly socialCommunityTags: readonly [string, string, string];
  readonly socialTopThread: string;
  /** builds the 3 seed-interpolated YouTube-style titles. */
  readonly youtubeTitles: (seed: string) => readonly [string, string, string];
  /** 3 extra head terms (the leading item is the live seed, added by the caller). */
  readonly keywordsHeadExtra: readonly [string, string, string];
  /** 4 items. */
  readonly keywordsLongtail: readonly [string, string, string, string];
  /** 3 items. */
  readonly keywordsSynonyms: readonly [string, string, string];
  /** 4 extra questions (the leading seed-based question is built by questionsLead). */
  readonly questionsExtra: readonly [string, string, string, string];
  readonly questionsLead: (seed: string) => string;
  /** the media_photo dual-output hero sub-caption. */
  readonly heroMediaCaption: string;
  /** the media_photo capability card's "subject" input_contract example (a form placeholder). */
  readonly photoSubjectExample: string;
  /** the brandbook capability card's "brand_essence" input_contract example (a form placeholder). */
  readonly brandEssenceExample: string;
  /** 7 CRM/leads sample rows (nome + sinal only -- see FixtureLeadFlavor). */
  readonly leads: readonly [
    FixtureLeadFlavor, FixtureLeadFlavor, FixtureLeadFlavor, FixtureLeadFlavor,
    FixtureLeadFlavor, FixtureLeadFlavor, FixtureLeadFlavor,
  ];
}

// ----------------------------------------------------------------------------
// RETAIL -- the ORIGINAL pet-retail vocabulary (byte-identical to pre-fix fixtures.ts).
// ----------------------------------------------------------------------------
const RETAIL: FixtureFlavor = {
  key: "retail",
  tag: "pet",
  storeLabel: "Minha Loja",
  productId: "prod_arranhador_torre",
  productName: "Arranhador Torre para Gatos 1,2m",
  competitors: ["PetShop Premium", "MiauHouse", "GatoFeliz"],
  topCompetitorFull: "PetShop Premium -- Torre Deluxe",
  categoryPaths: {
    a: "Animais > Gatos > Arranhadores",
    b: "Pet > Gatos > Moveis e Arranhadores",
    c: "Pet Shop > Gatos > Arranhadores",
  },
  gaps: [
    "Nenhum concorrente oferece base antiderrapante reforcada.",
    "Faltam fotos de gatos grandes (>6kg) usando o produto.",
    "Frete free acima de R$ 250 raramente destacado.",
  ],
  opportunities: [
    "Kit com 2 brinquedos inclusos diferencia na faixa R$ 199.",
    "Video curto de montagem reduz objecao de instalacao.",
    "Bundle B2B para pet shops (caixa com 4 unidades).",
  ],
  differentiationAngle:
    "Base reforcada antiderrapante + sisal substituivel -- durabilidade acima da media.",
  recommendedPositioning:
    "Torre robusta para gatos adultos e grandes, com custo-beneficio na faixa intermediaria.",
  seo: {
    headTerms: ["arranhador para gatos", "torre arranhador", "arranhador gato grande"],
    longtails: [
      "arranhador torre para gatos grandes resistente",
      "arranhador de sisal com base reforcada",
      "torre arranhador 1.2m com casinha",
    ],
    synonyms: ["poste arranhador", "brinquedo arranhador", "sisal para gatos"],
    seoInbound: ["melhor arranhador para gatos", "arranhador resistente"],
    seoOutbound: ["arranhador torre 1.2m", "arranhador gato grande premium"],
    negativeKeywords: ["arranhador parede", "arranhador papelao", "usado"],
  },
  legalName: "Comercio Exemplo LTDA",
  activityDescription:
    "4789-0/04 - Comercio varejista de animais vivos e de artigos e alimentos para animais de estimacao",
  segment: "Pet / e-commerce de acessorios e alimentacao felina",
  channels: ["loja propria", "mercado livre", "amazon", "instagram shop"],
  market: {
    setor: "Mercado pet Brasil",
    faturamento_setor_ano: "R$ 76,4 bilhoes (2024)",
    crescimento_anual: "+14% YoY",
    domicilios_com_pets: "60,7 milhoes",
    populacao_felina_br: "30,1 milhoes de gatos",
    ranking_global: "3o maior mercado pet do mundo",
    regiao_foco: "Sudeste (52% do consumo pet nacional)",
  },
  appName: "Clube Exemplo",
  appReviews: [
    "App pratico pra assinar racao, entrega sempre no prazo",
    "Faltou integrar com o comedouro wifi, mas o resto e otimo",
  ],
  socialCommunityTags: ["r/gatos", "r/petbr", "r/BrasilLivros"],
  socialTopThread: "Alguem usa os comedouros automaticos da loja? Valeu muito a pena",
  youtubeTitles: (seed) => [
    `${seed}: review completo do comedouro automatico`,
    `Unboxing ${seed} - vale a pena em 2026?`,
    `Testei a racao da ${seed} por 30 dias`,
  ],
  keywordsHeadExtra: ["comedouro gato automatico", "fonte de agua para gato", "racao premium gato"],
  keywordsLongtail: [
    "comedouro automatico gato wifi programavel",
    "fonte de agua silenciosa para gatos",
    "comedouro gato antiformiga aco inox",
    "racao natural para gato castrado",
  ],
  keywordsSynonyms: ["alimentador automatico felino", "dispenser de racao", "bebedouro para gatos"],
  questionsExtra: [
    "Qual o melhor comedouro automatico para gato?",
    "Comedouro automatico funciona com racao umida?",
    "Como limpar uma fonte de agua para gato?",
    "A racao premium faz diferenca para gato castrado?",
  ],
  questionsLead: (seed) => `Os produtos da ${seed} valem a pena?`,
  heroMediaCaption: "gato no topo da torre -- exemplo, nao e foto real",
  photoSubjectExample: "Gato cinza adulto no arranhador torre",
  brandEssenceExample: "Conforto premium para gatos exigentes",
  leads: [
    {
      nome: "Loja MiAuPet (vendedor ML)",
      sinal: "5 perguntas recentes sobre durabilidade do sisal no anuncio",
    },
    {
      nome: "@gata.frajola (tutora)",
      sinal: "post: 'terceiro arranhador que desmonta esse ano' (sinal de dor)",
    },
    {
      nome: "Pet Shop Exemplo Ltda",
      sinal: "CNAE varejo de artigos para pet + atua em SP capital (firmografia)",
    },
    {
      nome: "Comprador ML (apelido oculto)",
      sinal: "pergunta no anuncio concorrente: 'aguenta gato de 8kg?'",
    },
    {
      nome: "Canal Gatos & Cia (YouTube)",
      sinal: "video recente review de arranhadores (12k views) -- audiencia alvo",
    },
    {
      nome: "@lar.dos.tres.gatos",
      sinal: "comentario: 'queria um que durasse' (sinal fraco, 1 fonte)",
    },
    {
      nome: "Vendedor sem dados (anonimo)",
      sinal: "1 visita ao anuncio -- sinal abaixo do piso, marcado como fraco",
    },
  ],
};

// ----------------------------------------------------------------------------
// SERVICES -- generic professional/IT-services vocabulary (NEW).
// ----------------------------------------------------------------------------
const SERVICES: FixtureFlavor = {
  key: "services",
  tag: "services",
  storeLabel: "Minha Empresa",
  productId: "svc_suporte_ti_mensal",
  productName: "Pacote de Suporte Tecnico Mensal",
  competitors: ["TechCare Solucoes", "InfraJa Suporte", "NuvemCerta TI"],
  topCompetitorFull: "TechCare Solucoes -- Plano Corporate",
  categoryPaths: {
    a: "Servicos > TI > Suporte Tecnico",
    b: "Servicos > Tecnologia > Consultoria",
    c: "B2B > TI > Suporte Gerenciado",
  },
  gaps: [
    "Nenhum concorrente publica SLA de atendimento por escrito.",
    "Faltam depoimentos de clientes de porte medio (11-50 funcionarios).",
    "Onboarding gratuito raramente destacado na pagina de vendas.",
  ],
  opportunities: [
    "Auditoria de seguranca gratuita na primeira reuniao diferencia a proposta.",
    "Video curto explicando o SLA reduz objecao de contratacao.",
    "Pacote anual com desconto para clientes com 2+ filiais.",
  ],
  differentiationAngle:
    "SLA por escrito + suporte remoto 24/7 -- resposta acima da media do setor.",
  recommendedPositioning:
    "Suporte de TI robusto para empresas de pequeno e medio porte, com custo-beneficio na faixa intermediaria.",
  seo: {
    headTerms: ["suporte de ti para empresas", "suporte tecnico remoto", "consultoria de ti terceirizada"],
    longtails: [
      "suporte de ti para pequenas empresas com sla",
      "consultoria de ti remota com resposta rapida",
      "terceirizacao de suporte tecnico corporativo",
    ],
    synonyms: ["outsourcing de ti", "helpdesk corporativo", "suporte tecnico gerenciado"],
    seoInbound: ["melhor suporte de ti para empresas", "suporte tecnico confiavel"],
    seoOutbound: ["suporte de ti mensal", "consultoria de ti premium"],
    negativeKeywords: ["suporte de ti gratis", "curso de informatica", "concurso"],
  },
  legalName: "Servicos Exemplo LTDA",
  activityDescription:
    "6209-1/00 - Suporte tecnico, manutencao e outros servicos em tecnologia da informacao",
  segment: "TI / servicos de suporte e consultoria tecnica para empresas",
  channels: ["site proprio", "indicacao de clientes", "linkedin", "eventos do setor"],
  market: {
    setor: "Mercado de servicos de TI Brasil",
    faturamento_setor_ano: "R$ 45,2 bilhoes (2024)",
    crescimento_anual: "+9% YoY",
    empresas_terceirizam_ti: "38,4% das PMEs brasileiras",
    chamados_resolvidos_remoto: "78% dos chamados de TI",
    ranking_global: "5o maior mercado de servicos de TI da America Latina",
    regiao_foco: "Sudeste (49% da demanda por suporte de TI)",
  },
  appName: "Portal Exemplo",
  appReviews: [
    "App pratico pra abrir chamado, resposta sempre dentro do SLA",
    "Faltou integrar com o sistema interno, mas o resto e otimo",
  ],
  socialCommunityTags: ["r/sysadmin", "r/ti_brasil", "r/empreendedorismo"],
  socialTopThread: "Alguem usa o suporte de TI terceirizado dessa empresa? Valeu muito a pena",
  youtubeTitles: (seed) => [
    `${seed}: review completo do suporte de TI`,
    `Contratei ${seed} - vale a pena em 2026?`,
    `Testei o suporte da ${seed} por 30 dias`,
  ],
  keywordsHeadExtra: ["suporte de ti corporativo", "helpdesk remoto para empresas", "consultoria de ti mensal"],
  keywordsLongtail: [
    "suporte de ti remoto com sla garantido",
    "helpdesk terceirizado para pequenas empresas",
    "consultoria de ti mensal com resposta rapida",
    "suporte tecnico corporativo 24 horas",
  ],
  keywordsSynonyms: ["outsourcing de ti", "suporte tecnico gerenciado", "helpdesk corporativo"],
  questionsExtra: [
    "Qual o melhor suporte de TI para pequenas empresas?",
    "Suporte remoto funciona para sistemas legados?",
    "Como migrar o suporte de TI sem parar a operacao?",
    "O plano mensal compensa para uma empresa pequena?",
  ],
  questionsLead: (seed) => `Os servicos da ${seed} valem a pena?`,
  heroMediaCaption: "equipe em reuniao de suporte -- exemplo, nao e foto real",
  photoSubjectExample: "Equipe tecnica em reuniao de atendimento ao cliente",
  brandEssenceExample: "Suporte tecnico premium para empresas exigentes",
  leads: [
    {
      nome: "TechFix Servicos (parceiro indicado)",
      sinal: "5 perguntas recentes sobre SLA de atendimento no site",
    },
    {
      nome: "@ana.ti.consultora (consultora)",
      sinal: "post: 'terceiro fornecedor de suporte que atrasa esse ano' (sinal de dor)",
    },
    {
      nome: "Servicos Exemplo Ltda",
      sinal: "CNAE suporte tecnico + atua em SP capital (firmografia)",
    },
    {
      nome: "Lead LinkedIn (perfil oculto)",
      sinal: "pergunta no post concorrente: 'atende empresa com 50 funcionarios?'",
    },
    {
      nome: "Canal TI & Negocios (YouTube)",
      sinal: "video recente review de suporte terceirizado (12k views) -- audiencia alvo",
    },
    {
      nome: "@escritorio.de.tres.socios",
      sinal: "comentario: 'queria um que durasse' (sinal fraco, 1 fonte)",
    },
    {
      nome: "Vendedor sem dados (anonimo)",
      sinal: "1 visita ao anuncio -- sinal abaixo do piso, marcado como fraco",
    },
  ],
};

// ----------------------------------------------------------------------------
// NEUTRAL -- generic commerce vocabulary (the DEFAULT for unknown/absent shape).
// Deliberately NOT pet-specific and NOT IT-specific -- the honest degrade bucket.
// ----------------------------------------------------------------------------
const NEUTRAL: FixtureFlavor = {
  key: "neutral",
  tag: "demo",
  storeLabel: "Minha Empresa",
  productId: "prod_exemplo_a",
  productName: "Produto Exemplo A",
  competitors: ["Concorrente A", "Concorrente B", "Concorrente C"],
  topCompetitorFull: "Concorrente A -- Linha Premium",
  categoryPaths: {
    a: "Produtos > Categoria > Subcategoria",
    b: "Geral > Categoria > Item",
    c: "Loja > Categoria > Item",
  },
  gaps: [
    "Nenhum concorrente publica a garantia de forma clara.",
    "Faltam fotos reais de uso do produto.",
    "Frete gratis acima de um valor minimo raramente destacado.",
  ],
  opportunities: [
    "Kit com item extra incluso diferencia na faixa de preco intermediaria.",
    "Video curto de demonstracao reduz objecao de compra.",
    "Bundle B2B para revendedores (caixa com multiplas unidades).",
  ],
  differentiationAngle: "Garantia estendida + suporte pos-venda -- diferencial acima da media.",
  recommendedPositioning:
    "Produto robusto para o publico geral, com custo-beneficio na faixa intermediaria.",
  seo: {
    headTerms: ["produto exemplo", "categoria exemplo", "produto exemplo premium"],
    longtails: [
      "produto exemplo com garantia estendida",
      "produto exemplo custo beneficio",
      "categoria exemplo com frete gratis",
    ],
    synonyms: ["item exemplo", "produto similar", "alternativa exemplo"],
    seoInbound: ["melhor produto exemplo", "produto exemplo confiavel"],
    seoOutbound: ["produto exemplo premium", "produto exemplo custo beneficio"],
    negativeKeywords: ["produto exemplo gratis", "produto exemplo usado", "reclamacao"],
  },
  legalName: "Comercio Exemplo LTDA",
  activityDescription:
    "4789-0/99 - Comercio varejista de outros produtos nao especificados anteriormente",
  segment: "Comercio / varejo generalista",
  channels: ["site proprio", "marketplace", "redes sociais", "loja fisica"],
  market: {
    setor: "Mercado de varejo Brasil",
    faturamento_setor_ano: "R$ 50 bilhoes (2024)",
    crescimento_anual: "+6% YoY",
    participacao_online: "22% das vendas do setor",
    ticket_medio_setor: "R$ 180",
    ranking_global: "n/d (sem shape comprometido)",
    regiao_foco: "Sudeste (48% do consumo nacional)",
  },
  appName: "App Exemplo",
  appReviews: [
    "App pratico pra comprar, entrega sempre no prazo",
    "Faltou um recurso especifico, mas o resto e otimo",
  ],
  socialCommunityTags: ["r/brasil", "r/empreendedorismo", "r/promocoes"],
  socialTopThread: "Alguem ja comprou dessa empresa? Valeu muito a pena",
  youtubeTitles: (seed) => [
    `${seed}: review completo do produto`,
    `Comprei ${seed} - vale a pena em 2026?`,
    `Testei o produto da ${seed} por 30 dias`,
  ],
  keywordsHeadExtra: ["produto exemplo automatico", "produto exemplo premium", "produto exemplo custo beneficio"],
  keywordsLongtail: [
    "produto exemplo com garantia estendida",
    "produto exemplo entrega rapida",
    "produto exemplo bem avaliado",
    "produto exemplo para uso diario",
  ],
  keywordsSynonyms: ["item alternativo", "produto similar", "opcao equivalente"],
  questionsExtra: [
    "Qual o melhor produto exemplo?",
    "O produto funciona para uso diario?",
    "Como faco a manutencao do produto?",
    "O plano mensal compensa?",
  ],
  questionsLead: (seed) => `Os produtos da ${seed} valem a pena?`,
  heroMediaCaption: "produto em cena de estudio -- exemplo, nao e foto real",
  photoSubjectExample: "Produto em cena de estudio, fundo neutro",
  brandEssenceExample: "Qualidade premium para clientes exigentes",
  leads: [
    {
      nome: "Loja Exemplo (vendedor ML)",
      sinal: "5 perguntas recentes sobre garantia no anuncio",
    },
    {
      nome: "@cliente.satisfeito (comprador)",
      sinal: "post: 'terceiro produto que veio com defeito esse ano' (sinal de dor)",
    },
    {
      nome: "Comercio Exemplo Ltda",
      sinal: "CNAE varejo generalista + atua em SP capital (firmografia)",
    },
    {
      nome: "Comprador ML (apelido oculto)",
      sinal: "pergunta no anuncio concorrente: 'tem garantia estendida?'",
    },
    {
      nome: "Canal Resenhas & Cia (YouTube)",
      sinal: "video recente review de produtos similares (12k views) -- audiencia alvo",
    },
    {
      nome: "@familia.exemplo",
      sinal: "comentario: 'queria um que durasse' (sinal fraco, 1 fonte)",
    },
    {
      nome: "Vendedor sem dados (anonimo)",
      sinal: "1 visita ao anuncio -- sinal abaixo do piso, marcado como fraco",
    },
  ],
};

/** The small FLAVOR_TABLE: shape key -> demo domain vocabulary. Exported for direct
 *  inspection (tests iterate every entry to assert structure parity). */
export const FLAVOR_TABLE: Readonly<Record<FixtureFlavorKey, FixtureFlavor>> = {
  retail: RETAIL,
  services: SERVICES,
  neutral: NEUTRAL,
};

/**
 * Resolve a tenant's business-shape vertical (the backend cex_business_shape /
 * TenantShape.vertical value: "retail" | "services") to its FixtureFlavor.
 *
 * NEVER invents a shape: anything other than the two literal committed values
 * (undefined, "", whitespace, a typo, an uncommitted "derive_from_purpose", any
 * other fine-vertical string) degrades to "neutral" -- the honest generic-commerce
 * default. "retail" never silently becomes the fallback FOR an unrecognised value
 * (that would keep shipping pet content by accident); only an EXPLICIT "retail"
 * routes to the pet-retail flavor. PURE + TOTAL.
 */
export function resolveFlavor(shapeVertical?: string | null): FixtureFlavor {
  const v = (shapeVertical || "").trim().toLowerCase();
  if (v === "retail") return FLAVOR_TABLE.retail;
  if (v === "services") return FLAVOR_TABLE.services;
  return FLAVOR_TABLE.neutral;
}
