// ----------------------------------------------------------------------------
// Landing capability -- the RENDERED LANDING PAGE used as the dashboard fixture
// human_html.
//
// THE PRINCIPLE: the dashboard mock MUST reflect the EXPECTED human-facing result
// a supervisor reviews. For the LANDING capability that is the landing PAGE itself
// (hero + prova social + beneficios + comparativo + como funciona + FAQ + oferta +
// CTA sticky), NOT the typed operator outline (the MOLD_LANDING output_sections:
// Hero A/B / Secoes / CTA / Voz / Compliance). The typed operator sections STAY
// on-screen via StructuredResultView; only this human_html (the "Abrir" / dual-output
// human face) is the rendered landing page a reviewer would publish.
//
// It is a FULL standalone <!doctype html> document (Minha Loja-themed, the SAME 24 design
// tokens the product_ad mold uses), so DualOutputFace.wrapHtmlDocument passes it
// through untouched.
//
// HONEST-MOCK: the document carries the "amostra -- dados simulados" badge in its
// footer (it is a demo, never "resultado real"); ratings / unit counts are clearly
// flagged as sample copy. Keep that badge intact.
//
// FIXTURE FLAVOR (register R-269 second pass): mirrors lib/molds.ts's module-scope
// activeFlavorKey singleton. Retail's hotlinked mercadolivre.com.br cat-tower photo
// cannot simply be re-captioned for other flavors (the IMAGE ITSELF would still show
// a cat) -- services/neutral swap the hero/og/twitter image for a neutral inline SVG
// data-URI placeholder (CSP-compliant: `img-src https: data:` is already declared).
// Content mirrors the SAME "Pacote de Suporte Tecnico Mensal" services narrative and
// SEO fields MOLD_LANDING's services branch uses (lib/molds.ts), so the operator's
// typed outline and this rendered preview tell the same story.
//
// .ts file -> PT-BR accents are KEPT (the ASCII-only rule is .py/.ps1/.sh only).
// ----------------------------------------------------------------------------

import { config } from "../config";
import { resolveFlavor, type FixtureFlavorKey } from "../fixtureFlavor";

const activeFlavorKey: FixtureFlavorKey = resolveFlavor(config.businessShape).key;

/** Neutral gray placeholder (inline SVG data-URI) for non-retail image slots. */
const PLACEHOLDER_IMG =
  "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='800'%20height='800'%3E%3Crect%20width='800'%20height='800'%20fill='%23cbd5e1'/%3E%3Ctext%20x='400'%20y='400'%20font-family='sans-serif'%20font-size='32'%20fill='%23475569'%20text-anchor='middle'%20dominant-baseline='middle'%3EFoto%20ilustrativa%3C/text%3E%3C/svg%3E";

interface LandingCard {
  title: string;
  desc: string;
}
interface LandingFaq {
  q: string;
  a: string;
}

interface LandingSampleFlavorExt {
  title: string;
  metaDescription: string;
  canonicalPath: string;
  ogImage: string;
  /** og:description -- a SHORTER variant, distinct from metaDescription and jsonLdDescription. */
  ogDescription: string;
  jsonLdName: string;
  jsonLdDescription: string;
  jsonLdBrand: string;
  jsonLdPrice: string;
  /** twitter:title -- a DIFFERENT (shorter) variant than <title>. */
  twitterTitle: string;
  /** twitter:description -- the SHORTEST variant (just the H1, no sub). */
  twitterDescription: string;
  brandName: string;
  brandTag: string;
  heroEyebrow: string;
  heroH1: string;
  heroSub: string;
  heroImg: string;
  heroImgAlt: string;
  ctaPrimary: string;
  ctaSecondary: string;
  proofRating: string;
  proofReviews: string;
  /** 4 items. */
  badges: readonly [string, string, string, string];
  benefitsH2: string;
  /** 3 items. */
  benefits: readonly [LandingCard, LandingCard, LandingCard];
  compareH2: string;
  /** 3 headers: Criterio / our-brand column / generic-competitor column. */
  compareHeaders: readonly [string, string, string];
  /** 4 rows: [criterio, our-value, generic-value]. */
  compareRows: readonly [
    readonly [string, string, string],
    readonly [string, string, string],
    readonly [string, string, string],
    readonly [string, string, string],
  ];
  /** 3 items. */
  steps: readonly [LandingCard, LandingCard, LandingCard];
  /** 3 items. */
  faq: readonly [LandingFaq, LandingFaq, LandingFaq];
  price: string;
  priceOld: string;
  /** 3 items. */
  offerChips: readonly [string, string, string];
  urgency: string;
  footerLine: string;
  stickyPriceLabel: string;
}

const LANDING_SAMPLE_FLAVOR_EXT: Record<FixtureFlavorKey, LandingSampleFlavorExt> = {
  retail: {
    title: "Arranhador Torre 1,2m para Gatos | Base Reforcada | Minha Loja",
    metaDescription: "A torre que seu gato domina -- e que nao desmonta. Base reforcada antiderrapante + sisal substituivel. R$ 199, frete gratis acima de R$ 250.",
    canonicalPath: "/arranhador-torre-gatos-1-2m",
    ogImage: "https://http2.mlstatic.com/D_648677-MLB98009076874_112025-O.jpg",
    ogDescription: "A torre que seu gato domina -- e que nao desmonta. Base reforcada + sisal substituivel.",
    jsonLdName: "Arranhador Torre para Gatos 1,2m",
    jsonLdDescription: "A torre que seu gato domina -- e que nao desmonta. Base reforcada antiderrapante + sisal substituivel.",
    jsonLdBrand: "Minha Loja",
    jsonLdPrice: "199.00",
    twitterTitle: "Arranhador Torre 1,2m para Gatos | Minha Loja",
    twitterDescription: "A torre que seu gato domina -- e que nao desmonta.",
    brandName: "Minha Loja",
    brandTag: "O marketplace do tutor de gato",
    heroEyebrow: "Arranhador Torre 1,2m",
    heroH1: "A torre que seu gato domina -- e que nao desmonta",
    heroSub: "Base reforcada antiderrapante + sisal substituivel. Feita para gatos adultos e grandes, sem balancar.",
    heroImg: "https://http2.mlstatic.com/D_648677-MLB98009076874_112025-O.jpg",
    heroImgAlt: "Gato no topo do Arranhador Torre 1,2m -- foto hero",
    ctaPrimary: "Comprar agora",
    ctaSecondary: "Ver video de montagem",
    proofRating: "4,7",
    proofReviews: "2.143 avaliacoes (amostra) -- nota media de clientes verificados",
    badges: ["Frete gratis acima de R$ 250", "Garantia de 30 dias", "Envio em 24h", "RA1000 -- reputacao otima"],
    benefitsH2: "Por que escolher a Torre 1,2m",
    benefits: [
      { title: "Durabilidade real", desc: "Sisal substituivel + costura reforcada: o gato arranha, a torre sobrevive. Troque so o sisal, nao a torre toda." },
      { title: "Seguranca", desc: "Base antiderrapante de 5 kg -- aguenta gato de 8 kg sem balancar, mesmo em piso liso ou carpete." },
      { title: "Montagem em 5 min", desc: "Encaixe simples com chave inclusa. Sem ferramenta extra, sem manual de engenharia." },
    ],
    compareH2: "Minha Loja vs arranhador comum",
    compareHeaders: ["Criterio", "Torre Minha Loja", "Arranhador comum"],
    compareRows: [
      ["Base antiderrapante reforcada", "Sim (5 kg)", "Raro"],
      ["Sisal substituivel", "Sim", "Nao -- descarta a peca"],
      ["Aguenta gato grande (8 kg)", "Sim", "Balanca"],
      ["Garantia", "30 dias", "7 dias"],
    ],
    steps: [
      { title: "Encaixe a base", desc: "Fixe a base reforcada primeiro, em superficie nivelada." },
      { title: "Monte as secoes", desc: "Rosqueie de baixo para cima -- 5 minutos, sem forcar." },
      { title: "Posicione perto da janela", desc: "Aplique catnip no topo na 1a semana para incentivar o uso." },
    ],
    faq: [
      { q: "Aguenta gato grande?", a: "Sim. A base de 5 kg e o sisal reforcado foram dimensionados para gatos de ate 8 kg sem oscilar." },
      { q: "Como troco o sisal?", a: "O sisal e substituivel por secao: voce troca so o tubo desgastado, nao a torre inteira. Refis vendidos a parte." },
      { q: "Qual o prazo de entrega?", a: "Envio em 24h uteis apos a confirmacao. Frete gratis acima de R$ 250 para todo o Brasil (amostra)." },
    ],
    price: "R$ 199",
    priceOld: "R$ 249",
    offerChips: ["Frete gratis acima de R$ 250", "Garantia de 30 dias", "Envio em 24h"],
    urgency: "-15% no lancamento -- Restam 47 unidades (amostra)",
    footerLine: "Landing page de Minha Loja -- CEXAI landing_page mold. Exemplo representativo, nao e um resultado real.",
    stickyPriceLabel: "Torre 1,2m -- R$ 199",
  },
  services: {
    title: "Suporte de TI Mensal para Empresas | SLA por Escrito | Minha Empresa",
    metaDescription: "O suporte que sua equipe de TI vai confiar -- e que nao falha. SLA por escrito + atendimento remoto 24/7. R$ 397/mes, auditoria de seguranca gratis.",
    canonicalPath: "/suporte-de-ti-mensal-para-empresas",
    ogImage: PLACEHOLDER_IMG,
    ogDescription: "O suporte que sua equipe de TI vai confiar -- e que nao falha. SLA por escrito + atendimento remoto.",
    jsonLdName: "Pacote de Suporte Tecnico Mensal",
    jsonLdDescription: "O suporte que sua equipe de TI vai confiar -- e que nao falha. SLA por escrito + atendimento remoto 24/7.",
    jsonLdBrand: "Minha Empresa",
    jsonLdPrice: "397.00",
    twitterTitle: "Pacote de Suporte Tecnico Mensal | Minha Empresa",
    twitterDescription: "O suporte que sua equipe de TI vai confiar -- e que nao falha.",
    brandName: "Minha Empresa",
    brandTag: "Suporte de TI que sua empresa pode confiar",
    heroEyebrow: "Pacote de Suporte Tecnico Mensal",
    heroH1: "O suporte que sua equipe de TI vai confiar -- e que nao falha",
    heroSub: "SLA por escrito + atendimento remoto 24/7. Feito para empresas de pequeno e medio porte, sem TI interno.",
    heroImg: PLACEHOLDER_IMG,
    heroImgAlt: "Equipe em reuniao de suporte -- foto hero",
    ctaPrimary: "Falar com especialista",
    ctaSecondary: "Ver como funciona o onboarding",
    proofRating: "4,8",
    proofReviews: "312 avaliacoes (amostra) -- nota media de clientes verificados",
    badges: ["SLA por escrito", "Onboarding em 48h", "Atendimento 24/7", "ISO 27001 -- certificacao auditavel"],
    benefitsH2: "Por que escolher o Suporte Mensal",
    benefits: [
      { title: "Confiabilidade real", desc: "SLA por escrito + escalonamento automatico: o chamado critico entra, o time responde. Resposta garantida, nao promessa vaga." },
      { title: "Seguranca", desc: "Auditoria de seguranca gratis na 1a reuniao -- identifica riscos antes que virem incidente." },
      { title: "Onboarding em 48h", desc: "Ativacao guiada com checklist inclusa. Sem processo manual, sem semanas de espera." },
    ],
    compareH2: "Minha Empresa vs suporte de TI comum",
    compareHeaders: ["Criterio", "Suporte Minha Empresa", "Suporte comum"],
    compareRows: [
      ["SLA por escrito", "Sim (2h critico)", "Raro"],
      ["Onboarding guiado", "Sim (48h)", "Nao -- por conta propria"],
      ["Atende empresa pequena (< 50 func.)", "Sim", "Poucos atendem"],
      ["Garantia", "30 dias", "7 dias"],
    ],
    steps: [
      { title: "Kickoff", desc: "Reuniao inicial para confirmar escopo e pontos de contato." },
      { title: "Levantamento tecnico", desc: "Mapeamento remoto ou visita -- 3 a 5 dias uteis." },
      { title: "Ativacao", desc: "Agente instalado e SLA configurado -- pronta em 48h." },
    ],
    faq: [
      { q: "Atende empresa pequena?", a: "Sim. O SLA de 2h e o onboarding de 48h foram dimensionados para empresas de 10 a 50 funcionarios." },
      { q: "Como funciona o SLA?", a: "SLA por escrito, por severidade: critico 2h, alto 8h, normal 24h uteis. Escalonamento automatico se estourar." },
      { q: "Qual o prazo de ativacao?", a: "Onboarding completo em ate 48h uteis apos a confirmacao do contrato (amostra)." },
    ],
    price: "R$ 397",
    priceOld: "R$ 497",
    offerChips: ["SLA por escrito", "Onboarding em 48h", "Auditoria de seguranca gratis"],
    urgency: "-15% na contratacao anual -- Restam 12 vagas de onboarding no mes (amostra)",
    footerLine: "Landing page de Minha Empresa -- CEXAI landing_page mold. Exemplo representativo, nao e um resultado real.",
    stickyPriceLabel: "Suporte Mensal -- R$ 397/mes",
  },
  neutral: {
    title: "Produto Exemplo A | Garantia Estendida | Minha Empresa",
    metaDescription: "O produto que seu dia a dia precisa -- e que nao falha. Garantia estendida + suporte pos-venda. R$ 99, frete gratis acima de um valor minimo.",
    canonicalPath: "/produto-exemplo-a",
    ogImage: PLACEHOLDER_IMG,
    ogDescription: "O produto que seu dia a dia precisa -- e que nao falha. Garantia estendida + suporte pos-venda.",
    jsonLdName: "Produto Exemplo A",
    jsonLdDescription: "O produto que seu dia a dia precisa -- e que nao falha. Garantia estendida + suporte pos-venda.",
    jsonLdBrand: "Minha Empresa",
    jsonLdPrice: "99.00",
    twitterTitle: "Produto Exemplo A | Minha Empresa",
    twitterDescription: "O produto que seu dia a dia precisa -- e que nao falha.",
    brandName: "Minha Empresa",
    brandTag: "Qualidade premium para clientes exigentes",
    heroEyebrow: "Produto Exemplo A",
    heroH1: "O produto que seu dia a dia precisa -- e que nao falha",
    heroSub: "Garantia estendida + suporte pos-venda. Feito para uso diario intenso, sem perder qualidade.",
    heroImg: PLACEHOLDER_IMG,
    heroImgAlt: "Produto em cena de estudio -- foto hero",
    ctaPrimary: "Comprar agora",
    ctaSecondary: "Ver como funciona",
    proofRating: "4,7",
    proofReviews: "2.143 avaliacoes (amostra) -- nota media de clientes verificados",
    badges: ["Frete gratis acima de um valor minimo", "Garantia de 30 dias", "Envio em 24h", "RA1000 -- reputacao otima"],
    benefitsH2: "Por que escolher o Produto Exemplo A",
    benefits: [
      { title: "Durabilidade real", desc: "Garantia estendida + acabamento reforcado: o uso diario nao desgasta. Reponha so a peca, nao o produto todo." },
      { title: "Seguranca", desc: "Base estavel -- aguenta uso intenso sem perder qualidade, em qualquer ambiente." },
      { title: "Entrega rapida", desc: "Envio em 24h uteis. Sem processo manual, sem semanas de espera." },
    ],
    compareH2: "Minha Empresa vs produto comum",
    compareHeaders: ["Criterio", "Produto Minha Empresa", "Produto comum"],
    compareRows: [
      ["Garantia estendida", "Sim (30 dias)", "Raro"],
      ["Suporte pos-venda", "Sim", "Nao -- por conta propria"],
      ["Aguenta uso diario intenso", "Sim", "Desgasta rapido"],
      ["Garantia", "30 dias", "7 dias"],
    ],
    steps: [
      { title: "Encomende", desc: "Escolha o produto e finalize a compra em minutos." },
      { title: "Receba", desc: "Envio em 24h uteis, rastreio incluso." },
      { title: "Use no dia a dia", desc: "Garantia estendida cobre uso normal por 30 dias." },
    ],
    faq: [
      { q: "Tem garantia estendida?", a: "Sim. 30 dias contra defeito de fabricacao, alem da garantia legal." },
      { q: "Como funciona a troca?", a: "Troca facil em ate 7 dias corridos, produto sem uso e com nota fiscal." },
      { q: "Qual o prazo de entrega?", a: "Envio em 24h uteis apos a confirmacao. Frete gratis acima de um valor minimo (amostra)." },
    ],
    price: "R$ 99",
    priceOld: "R$ 129",
    offerChips: ["Frete gratis acima de um valor minimo", "Garantia de 30 dias", "Envio em 24h"],
    urgency: "-15% no lancamento -- Restam 47 unidades (amostra)",
    footerLine: "Landing page de Minha Empresa -- CEXAI landing_page mold. Exemplo representativo, nao e um resultado real.",
    stickyPriceLabel: "Produto Exemplo A -- R$ 99",
  },
};

const lsExt = LANDING_SAMPLE_FLAVOR_EXT[activeFlavorKey];

export const LANDING_SAMPLE_HTML = String.raw`<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index, follow">
<!-- Content-Security-Policy: serve this doc with a CSP HEADER (not a meta) supplied
     by the caller, e.g.  default-src 'self'; img-src https: data:; style-src
     'unsafe-inline'; script-src 'none'; base-uri 'none'; form-action 'self'
     (this page ships NO executable script; the JSON-LD below is inert data). -->
<title>${lsExt.title}</title>
<meta name="description" content="${lsExt.metaDescription}">
<link rel="canonical" href="https://example.com${lsExt.canonicalPath}">
<meta property="og:type" content="product">
<meta property="og:title" content="${lsExt.title}">
<meta property="og:description" content="${lsExt.ogDescription}">
<meta property="og:site_name" content="${lsExt.brandName}">
<meta property="og:url" content="https://example.com${lsExt.canonicalPath}">
<meta property="og:image" content="${lsExt.ogImage}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${lsExt.twitterTitle}">
<meta name="twitter:description" content="${lsExt.twitterDescription}">
<meta name="twitter:image" content="${lsExt.ogImage}">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product","name":"${lsExt.jsonLdName}","description":"${lsExt.jsonLdDescription}","image":["${lsExt.ogImage}"],"brand":{"@type":"Brand","name":"${lsExt.jsonLdBrand}"},"offers":{"@type":"Offer","priceCurrency":"BRL","price":"${lsExt.jsonLdPrice}","availability":"https://schema.org/InStock"}}</script>
<style>
:root{--background:0 0% 100%;--foreground:213 47% 12%;--card:0 0% 98%;--card-foreground:213 47% 12%;--popover:0 0% 100%;--popover-foreground:213 47% 12%;--primary:174 68% 50%;--primary-foreground:0 0% 100%;--secondary:213 35% 18%;--secondary-foreground:0 0% 100%;--muted:210 20% 96%;--muted-foreground:213 15% 45%;--accent:174 68% 50%;--accent-foreground:0 0% 100%;--border:210 20% 88%;--input:210 20% 88%;--ring:174 68% 50%;--brand:174 68% 50%;--brand-foreground:0 0% 100%;--brand-muted:174 30% 92%;--highlight:42 100% 50%;--highlight-foreground:0 0% 10%;--highlight-muted:42 80% 93%;--radius:0.75rem;--font-family-base:Inter, -apple-system, Segoe UI, sans-serif}
*{box-sizing:border-box}html,body{margin:0;padding:0}body{background:hsl(var(--background));color:hsl(var(--foreground));font-family:var(--font-family-base);line-height:1.55;-webkit-font-smoothing:antialiased}
.lp-doc{max-width:960px;margin:0 auto;padding:0 0 96px}
section{padding:48px 24px;border-bottom:1px solid hsl(var(--border))}section:last-of-type{border-bottom:0}
h1,h2,h3{margin:0 0 14px;line-height:1.15;letter-spacing:-0.02em}h2{font-size:1.7rem}h3{font-size:1.15rem}p{margin:0 0 14px}
img{max-width:100%;height:auto;display:block}
.lp-nav{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 24px;background:hsl(var(--brand));color:hsl(var(--brand-foreground));position:sticky;top:0;z-index:20}
.lp-nav .lp-brand{font-size:1.2rem;font-weight:800}.lp-nav .lp-brand small{display:block;font-size:.72rem;font-weight:400;opacity:.85;margin-top:2px}
.lp-nav .lp-nav-cta{background:hsl(var(--highlight));color:hsl(var(--highlight-foreground));font-weight:700;font-size:.85rem;text-decoration:none;padding:9px 16px;border-radius:999px}
.lp-hero{text-align:center;background:linear-gradient(180deg,hsl(var(--brand-muted)) 0%,hsl(var(--background)) 100%)}
.lp-hero .lp-eyebrow{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;font-weight:700;color:hsl(var(--brand));margin-bottom:10px}
.lp-hero h1{font-size:clamp(2rem,5vw,3.4rem);font-weight:800}
.lp-hero .lp-sub{font-size:1.15rem;color:hsl(var(--muted-foreground));max-width:48ch;margin:0 auto 24px}
.lp-hero .lp-hero-media{margin:24px auto;max-width:520px}
.lp-cta-row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;align-items:center}
.lp-cta{display:inline-block;background:hsl(var(--primary));color:hsl(var(--primary-foreground));font-size:1.05rem;font-weight:700;text-decoration:none;padding:15px 32px;border-radius:var(--radius);box-shadow:0 8px 22px -8px hsl(var(--primary) / .55)}
.lp-cta:hover{filter:brightness(1.06)}.lp-cta:focus-visible{outline:3px solid hsl(var(--ring));outline-offset:3px}
.lp-cta-ghost{display:inline-block;border:1.5px solid hsl(var(--border));color:hsl(var(--foreground));font-size:1.05rem;font-weight:600;text-decoration:none;padding:13px 26px;border-radius:var(--radius)}
.lp-proof{text-align:center;background:hsl(var(--muted))}
.lp-rating{font-size:2rem;font-weight:800;color:hsl(var(--foreground))}.lp-stars{color:hsl(var(--highlight));font-size:1.5rem;letter-spacing:.12em}
.lp-proof .lp-reviews{color:hsl(var(--muted-foreground));font-size:.95rem;margin-top:4px}
.lp-badges{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:18px}
.lp-badge{font-size:.82rem;background:hsl(var(--card));border:1px solid hsl(var(--border));border-radius:999px;padding:7px 14px;color:hsl(var(--muted-foreground))}
.lp-benefits-grid{display:grid;grid-template-columns:1fr;gap:18px;margin-top:8px}
.lp-bcard{background:hsl(var(--card));border:1px solid hsl(var(--border));border-radius:var(--radius);padding:22px}
.lp-bcard .lp-bicon{width:42px;height:42px;border-radius:12px;background:hsl(var(--brand));color:hsl(var(--brand-foreground));display:flex;align-items:center;justify-content:center;font-size:1.2rem;font-weight:800;margin-bottom:12px}
.lp-bcard h3{margin:0 0 6px}.lp-bcard p{margin:0;font-size:.95rem;color:hsl(var(--muted-foreground))}
.lp-compare table{border-collapse:collapse;width:100%;font-size:.95rem;margin-top:6px}
.lp-compare th,.lp-compare td{padding:12px 14px;border-bottom:1px solid hsl(var(--border));text-align:left}
.lp-compare thead th{background:hsl(var(--muted));font-weight:700}
.lp-compare td.lp-yes{color:hsl(var(--brand));font-weight:700}.lp-compare td.lp-no{color:hsl(var(--muted-foreground))}
.lp-steps{display:grid;grid-template-columns:1fr;gap:18px;margin-top:8px;counter-reset:step}
.lp-step{display:flex;gap:14px;align-items:flex-start}
.lp-step .lp-snum{flex:0 0 auto;width:34px;height:34px;border-radius:999px;background:hsl(var(--secondary));color:hsl(var(--secondary-foreground));display:flex;align-items:center;justify-content:center;font-weight:800}
.lp-step h3{margin:0 0 3px;font-size:1.05rem}.lp-step p{margin:0;font-size:.95rem;color:hsl(var(--muted-foreground))}
.lp-faq details{border:1px solid hsl(var(--border));border-radius:var(--radius);padding:2px 18px;margin-bottom:12px;background:hsl(var(--card))}
.lp-faq summary{cursor:pointer;font-weight:600;padding:14px 0;list-style:revert}
.lp-faq details p{margin:0 0 14px;font-size:.95rem;color:hsl(var(--muted-foreground))}
.lp-offer{text-align:center;background:hsl(var(--secondary));color:hsl(var(--secondary-foreground))}
.lp-offer h2{color:inherit}.lp-price{font-size:2.8rem;font-weight:800;line-height:1}.lp-price-old{font-size:1.1rem;text-decoration:line-through;opacity:.7;margin-left:8px;font-weight:500}
.lp-offer .lp-offer-meta{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:18px 0}
.lp-chip{font-size:.85rem;border:1px solid currentColor;border-radius:999px;padding:6px 14px;opacity:.92}
.lp-urgency{font-weight:700;color:hsl(var(--highlight));margin-top:8px}
.lp-sticky{position:fixed;left:0;right:0;bottom:0;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 18px;background:hsl(var(--secondary));color:hsl(var(--secondary-foreground));box-shadow:0 -6px 18px -8px rgba(0,0,0,.4)}
.lp-sticky .lp-sticky-price{font-weight:800;font-size:1.05rem}.lp-sticky .lp-cta{padding:11px 22px;font-size:.95rem}
.lp-foot{font:12px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:hsl(var(--muted-foreground));text-align:center;padding:28px 24px}
.lp-foot .lp-badge-sample{display:inline-block;border-radius:6px;padding:3px 12px;color:#fff;margin-bottom:8px;font-size:.78rem;background:#b8860b}
@media(min-width:640px){.lp-benefits-grid{grid-template-columns:repeat(3,1fr)}.lp-steps{grid-template-columns:repeat(3,1fr)}}
@media print{.lp-nav,.lp-sticky,.lp-cta,.lp-cta-ghost{display:none !important}body{background:#fff;color:#000}section{border-bottom:1px solid #ccc;break-inside:avoid}@page{margin:1.5cm}}
</style>
</head>
<body>
<main class="lp-doc">
<nav class="lp-nav" role="banner"><div class="lp-brand">${lsExt.brandName}<small>${lsExt.brandTag}</small></div><a class="lp-nav-cta" href="#oferta">${lsExt.ctaPrimary}</a></nav>

<section class="lp-hero">
<div class="lp-eyebrow">${lsExt.heroEyebrow}</div>
<h1>${lsExt.heroH1}</h1>
<p class="lp-sub">${lsExt.heroSub}</p>
<div class="lp-hero-media"><img src="${lsExt.heroImg}" alt="${lsExt.heroImgAlt}" data-slot-key="hero" data-kind="image" data-editable="true" data-upload-fallback="true"></div>
<div class="lp-cta-row"><a class="lp-cta" href="#oferta">${lsExt.ctaPrimary}</a><a class="lp-cta-ghost" href="#como-funciona">${lsExt.ctaSecondary}</a></div>
</section>

<section class="lp-proof">
<div class="lp-rating">${lsExt.proofRating} <span class="lp-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span></div>
<div class="lp-reviews">${lsExt.proofReviews}</div>
<div class="lp-badges"><span class="lp-badge">${lsExt.badges[0]}</span><span class="lp-badge">${lsExt.badges[1]}</span><span class="lp-badge">${lsExt.badges[2]}</span><span class="lp-badge">${lsExt.badges[3]}</span></div>
</section>

<section class="lp-benefits">
<h2>${lsExt.benefitsH2}</h2>
<div class="lp-benefits-grid">
<div class="lp-bcard"><div class="lp-bicon">&#10003;</div><h3>${lsExt.benefits[0].title}</h3><p>${lsExt.benefits[0].desc}</p></div>
<div class="lp-bcard"><div class="lp-bicon">&#9650;</div><h3>${lsExt.benefits[1].title}</h3><p>${lsExt.benefits[1].desc}</p></div>
<div class="lp-bcard"><div class="lp-bicon">&#9881;</div><h3>${lsExt.benefits[2].title}</h3><p>${lsExt.benefits[2].desc}</p></div>
</div>
</section>

<section class="lp-compare">
<h2>${lsExt.compareH2}</h2>
<table><thead><tr><th>${lsExt.compareHeaders[0]}</th><th>${lsExt.compareHeaders[1]}</th><th>${lsExt.compareHeaders[2]}</th></tr></thead>
<tbody>
<tr><td>${lsExt.compareRows[0][0]}</td><td class="lp-yes">${lsExt.compareRows[0][1]}</td><td class="lp-no">${lsExt.compareRows[0][2]}</td></tr>
<tr><td>${lsExt.compareRows[1][0]}</td><td class="lp-yes">${lsExt.compareRows[1][1]}</td><td class="lp-no">${lsExt.compareRows[1][2]}</td></tr>
<tr><td>${lsExt.compareRows[2][0]}</td><td class="lp-yes">${lsExt.compareRows[2][1]}</td><td class="lp-no">${lsExt.compareRows[2][2]}</td></tr>
<tr><td>${lsExt.compareRows[3][0]}</td><td class="lp-yes">${lsExt.compareRows[3][1]}</td><td class="lp-no">${lsExt.compareRows[3][2]}</td></tr>
</tbody></table>
</section>

<section class="lp-how" id="como-funciona">
<h2>Como funciona</h2>
<div class="lp-steps">
<div class="lp-step"><span class="lp-snum">1</span><div><h3>${lsExt.steps[0].title}</h3><p>${lsExt.steps[0].desc}</p></div></div>
<div class="lp-step"><span class="lp-snum">2</span><div><h3>${lsExt.steps[1].title}</h3><p>${lsExt.steps[1].desc}</p></div></div>
<div class="lp-step"><span class="lp-snum">3</span><div><h3>${lsExt.steps[2].title}</h3><p>${lsExt.steps[2].desc}</p></div></div>
</div>
</section>

<section class="lp-faq">
<h2>Perguntas frequentes</h2>
<details><summary>${lsExt.faq[0].q}</summary><p>${lsExt.faq[0].a}</p></details>
<details><summary>${lsExt.faq[1].q}</summary><p>${lsExt.faq[1].a}</p></details>
<details><summary>${lsExt.faq[2].q}</summary><p>${lsExt.faq[2].a}</p></details>
</section>

<section class="lp-offer" id="oferta">
<h2>A oferta</h2>
<div class="lp-price">${lsExt.price}<span class="lp-price-old">${lsExt.priceOld}</span></div>
<div class="lp-offer-meta"><span class="lp-chip">${lsExt.offerChips[0]}</span><span class="lp-chip">${lsExt.offerChips[1]}</span><span class="lp-chip">${lsExt.offerChips[2]}</span></div>
<div class="lp-urgency">${lsExt.urgency}</div>
<div class="lp-cta-row" style="margin-top:18px"><a class="lp-cta" href="#oferta">${lsExt.ctaPrimary}</a></div>
</section>

<footer class="lp-foot" role="contentinfo">
<span class="lp-badge-sample">amostra -- dados simulados</span><br>
${lsExt.footerLine}
</footer>
</main>
<div class="lp-sticky" aria-hidden="false"><span class="lp-sticky-price">${lsExt.stickyPriceLabel}</span><a class="lp-cta" href="#oferta">${lsExt.ctaPrimary}</a></div>
</body>
</html>
`;
