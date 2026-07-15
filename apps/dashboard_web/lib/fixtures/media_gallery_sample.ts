// ----------------------------------------------------------------------------
// Media / Photo capability -- the RENDERED PHOTO GALLERY used as the dashboard
// fixture human_html.
//
// THE PRINCIPLE: the dashboard mock MUST reflect the EXPECTED human-facing result
// a supervisor reviews. For the MEDIA / PHOTO capability that is the rendered MEDIA
// the cap produces -- the photo gallery (hero + the shot list as actual images) --
// NOT the typed operator brief (the MOLD_MEDIA_PHOTO output_sections: Brief /
// Iluminacao+camera / Shot list / Brand fit / Negative prompt / Compliance). The
// typed operator brief STAYS on-screen via StructuredResultView; the editable
// media slots (DualOutputFace) carry the per-shot images; and THIS human_html (the
// "Abrir" / dual-output human face) is the rendered gallery page a reviewer signs off.
//
// It is a FULL standalone <!doctype html> document (Minha Loja-themed, the SAME 24 design
// tokens the product_ad mold uses), so DualOutputFace.wrapHtmlDocument passes it
// through untouched. Each shot mirrors the MOLD_MEDIA_PHOTO Shot list (hero / detalhe /
// lifestyle / escala / packshot) with its persuasive intent + aspect, so the gallery
// reads as the brief RENDERED, not a parallel invention.
//
// HONEST-MOCK: the document carries the "amostra -- dados simulados" badge in its
// footer + an "imagem ilustrativa" caption on each frame (the brief's Compliance item).
// Keep that badge intact.
//
// FIXTURE FLAVOR (register R-269 second pass): mirrors lib/molds.ts's module-scope
// activeFlavorKey singleton (SAME resolveFlavor(config.businessShape) call) so this
// sample HTML never shows a services/neutral tenant the retail cat-tower gallery.
// Retail's hotlinked mercadolivre.com.br CAT PRODUCT PHOTOS cannot simply be
// re-captioned for other flavors (the IMAGE ITSELF would still show a cat) -- so
// services/neutral image slots use a neutral inline SVG data-URI placeholder
// (CSP-compliant: the doc's own comment already declares `img-src https: data:`)
// instead of a hotlinked photo. Every flavor keeps the EXACT same DOM structure
// (1 hero figure + 4 grid tiles + 1 empty upload slot) -- only text + img src vary.
//
// .ts file -> PT-BR accents are KEPT (the ASCII-only rule is .py/.ps1/.sh only).
// ----------------------------------------------------------------------------

import { config } from "../config";
import { resolveFlavor, type FixtureFlavorKey } from "../fixtureFlavor";

const activeFlavorKey: FixtureFlavorKey = resolveFlavor(config.businessShape).key;

/** Neutral gray placeholder (inline SVG data-URI) for non-retail image slots --
 *  never a hotlinked photo of an unrelated flavor's product. */
const PLACEHOLDER_IMG =
  "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='800'%20height='800'%3E%3Crect%20width='800'%20height='800'%20fill='%23cbd5e1'/%3E%3Ctext%20x='400'%20y='400'%20font-family='sans-serif'%20font-size='32'%20fill='%23475569'%20text-anchor='middle'%20dominant-baseline='middle'%3EFoto%20ilustrativa%3C/text%3E%3C/svg%3E";

interface GalleryShot {
  img: string;
  alt: string;
  shotLabel: string;
  intent: string;
}

interface MediaGalleryFlavorExt {
  title: string;
  metaDescription: string;
  brandName: string;
  brandTag: string;
  eyebrowH1: string;
  headParagraph: string;
  hero: GalleryShot;
  /** 4 tiles: detalhe / lifestyle / escala / packshot(or retrato). */
  tiles: readonly [GalleryShot, GalleryShot, GalleryShot, GalleryShot];
  footerLine: string;
}

const MEDIA_GALLERY_FLAVOR_EXT: Record<FixtureFlavorKey, MediaGalleryFlavorExt> = {
  retail: {
    title: "Galeria de fotos -- Arranhador Torre 1,2m | Minha Loja",
    metaDescription: "Galeria de midia do Arranhador Torre 1,2m: hero, detalhe, lifestyle, escala e packshot. Amostra ilustrativa.",
    brandName: "Minha Loja",
    brandTag: "O marketplace do tutor de gato",
    eyebrowH1: "Arranhador Torre para Gatos 1,2m",
    headParagraph: "Set de fotos gerado a partir do brief: cena clara de apartamento, gato cinza adulto, registro warm. Hero 4:5 reaproveitado em multiplas superficies.",
    hero: {
      img: "https://http2.mlstatic.com/D_648677-MLB98009076874_112025-O.jpg",
      alt: "Hero: gato no topo da torre, produto inteiro no enquadramento",
      shotLabel: "Hero -- gato no topo da torre",
      intent: 'Produto dominante: "e o item principal desta sala".',
    },
    tiles: [
      {
        img: "https://http2.mlstatic.com/D_677733-MLB83388336596_042025-O.jpg",
        alt: "Detalhe: textura do sisal e base antiderrapante (close)",
        shotLabel: "Detalhe -- textura do sisal",
        intent: 'Durabilidade: quebra "sera que e resistente?" sem texto.',
      },
      {
        img: "https://http2.mlstatic.com/D_918273-MLB83388277478_042025-O.jpg",
        alt: "Lifestyle: gato arranhando, tutor ao fundo desfocado",
        shotLabel: "Lifestyle -- gato + tutor",
        intent: "Conexao emocional: vende o sentimento, nao o objeto.",
      },
      {
        img: "https://http2.mlstatic.com/D_914341-MLB83388336598_042025-O.jpg",
        alt: "Escala: produto ao lado do sofa para dar nocao de tamanho",
        shotLabel: "Escala -- ao lado do sofa",
        intent: 'Reduz incerteza: "cabe no meu apartamento?".',
      },
      {
        img: "https://http2.mlstatic.com/D_818098-MLB83388160666_042025-O.jpg",
        alt: "Packshot: produto em fundo branco, sem props",
        shotLabel: "Packshot -- fundo branco",
        intent: "Requisito de listagem ML / Amazon.",
      },
    ],
    footerLine: "Galeria de Minha Loja -- CEXAI media_photo mold. Imagens ilustrativas, nao sao um resultado real.",
  },
  services: {
    title: "Galeria de fotos -- Pacote de Suporte Tecnico Mensal | Minha Empresa",
    metaDescription: "Galeria de midia do Pacote de Suporte Tecnico Mensal: hero, detalhe, lifestyle, escala e retrato. Amostra ilustrativa.",
    brandName: "Minha Empresa",
    brandTag: "Suporte de TI que sua empresa pode confiar",
    eyebrowH1: "Pacote de Suporte Tecnico Mensal",
    headParagraph: "Set de fotos gerado a partir do brief: sala de reuniao clara, equipe tecnica em atendimento, registro warm. Hero 4:5 reaproveitado em multiplas superficies.",
    hero: {
      img: PLACEHOLDER_IMG,
      alt: "Hero: equipe reunida na sala de reuniao, atendimento completo no enquadramento",
      shotLabel: "Hero -- equipe em reuniao",
      intent: 'Servico dominante: "e o diferencial principal desta empresa".',
    },
    tiles: [
      {
        img: PLACEHOLDER_IMG,
        alt: "Detalhe: tela do dashboard de monitoramento e checklist de SLA (close)",
        shotLabel: "Detalhe -- dashboard de monitoramento",
        intent: 'Confiabilidade: quebra "sera que funciona de verdade?" sem texto.',
      },
      {
        img: PLACEHOLDER_IMG,
        alt: "Lifestyle: tecnico atendendo chamado, cliente ao telefone ao fundo desfocado",
        shotLabel: "Lifestyle -- tecnico + cliente",
        intent: "Conexao emocional: vende a confianca, nao so o servico.",
      },
      {
        img: PLACEHOLDER_IMG,
        alt: "Escala: equipe tecnica ao lado do rack de servidores para dar nocao de porte",
        shotLabel: "Escala -- ao lado do rack",
        intent: 'Reduz incerteza: "atende o tamanho da minha empresa?".',
      },
      {
        img: PLACEHOLDER_IMG,
        alt: "Retrato: time em fundo neutro, sem props",
        shotLabel: "Retrato -- fundo neutro",
        intent: "Requisito de listagem em diretorio (G2 / LinkedIn).",
      },
    ],
    footerLine: "Galeria de Minha Empresa -- CEXAI media_photo mold. Imagens ilustrativas, nao sao um resultado real.",
  },
  neutral: {
    title: "Galeria de fotos -- Produto Exemplo A | Minha Empresa",
    metaDescription: "Galeria de midia do Produto Exemplo A: hero, detalhe, lifestyle, escala e packshot. Amostra ilustrativa.",
    brandName: "Minha Empresa",
    brandTag: "Qualidade premium para clientes exigentes",
    eyebrowH1: "Produto Exemplo A",
    headParagraph: "Set de fotos gerado a partir do brief: cena de estudio clara, produto em destaque, registro warm. Hero 4:5 reaproveitado em multiplas superficies.",
    hero: {
      img: PLACEHOLDER_IMG,
      alt: "Hero: produto centralizado, produto inteiro no enquadramento",
      shotLabel: "Hero -- produto centralizado",
      intent: 'Produto dominante: "e o item principal desta cena".',
    },
    tiles: [
      {
        img: PLACEHOLDER_IMG,
        alt: "Detalhe: textura e acabamento do produto (close)",
        shotLabel: "Detalhe -- textura do produto",
        intent: 'Durabilidade: quebra "sera que e resistente?" sem texto.',
      },
      {
        img: PLACEHOLDER_IMG,
        alt: "Lifestyle: produto em uso, cliente ao fundo desfocado",
        shotLabel: "Lifestyle -- produto + cliente",
        intent: "Conexao emocional: vende o sentimento, nao o objeto.",
      },
      {
        img: PLACEHOLDER_IMG,
        alt: "Escala: produto ao lado de um objeto do dia a dia para dar nocao de tamanho",
        shotLabel: "Escala -- objeto do dia a dia",
        intent: 'Reduz incerteza: "e do tamanho que eu preciso?".',
      },
      {
        img: PLACEHOLDER_IMG,
        alt: "Packshot: produto em fundo branco, sem props",
        shotLabel: "Packshot -- fundo branco",
        intent: "Requisito de listagem ML / Amazon.",
      },
    ],
    footerLine: "Galeria de Minha Empresa -- CEXAI media_photo mold. Imagens ilustrativas, nao sao um resultado real.",
  },
};

const mgExt = MEDIA_GALLERY_FLAVOR_EXT[activeFlavorKey];

export const MEDIA_GALLERY_SAMPLE_HTML = String.raw`<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Content-Security-Policy: serve this doc with a CSP HEADER (not a meta) supplied
     by the caller, e.g.  default-src 'self'; img-src https: data:; style-src
     'unsafe-inline'; script-src 'none'; base-uri 'none' (this page ships NO script). -->
<title>${mgExt.title}</title>
<meta name="description" content="${mgExt.metaDescription}">
<style>
:root{--background:0 0% 100%;--foreground:213 47% 12%;--card:0 0% 98%;--primary:174 68% 50%;--primary-foreground:0 0% 100%;--secondary:213 35% 18%;--secondary-foreground:0 0% 100%;--muted:210 20% 96%;--muted-foreground:213 15% 45%;--border:210 20% 88%;--ring:174 68% 50%;--brand:174 68% 50%;--brand-foreground:0 0% 100%;--brand-muted:174 30% 92%;--highlight:42 100% 50%;--highlight-foreground:0 0% 10%;--radius:0.75rem;--font-family-base:Inter, -apple-system, Segoe UI, sans-serif}
*{box-sizing:border-box}html,body{margin:0;padding:0}body{background:hsl(var(--background));color:hsl(var(--foreground));font-family:var(--font-family-base);line-height:1.55;-webkit-font-smoothing:antialiased}
.mg-doc{max-width:1040px;margin:0 auto;padding:0 0 48px}
img{max-width:100%;height:auto;display:block}
.mg-bar{display:flex;align-items:center;gap:12px;padding:16px 24px;background:hsl(var(--brand));color:hsl(var(--brand-foreground));position:sticky;top:0;z-index:10}
.mg-bar .mg-brand{font-size:1.15rem;font-weight:800;line-height:1.15}.mg-bar .mg-brand small{display:block;font-size:.72rem;opacity:.85;font-weight:400;margin-top:2px}
.mg-head{padding:36px 24px 8px;text-align:center}
.mg-head .mg-eyebrow{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;font-weight:700;color:hsl(var(--brand));margin-bottom:8px}
.mg-head h1{font-size:clamp(1.7rem,4vw,2.6rem);font-weight:800;letter-spacing:-0.02em;margin:0 0 8px}
.mg-head p{color:hsl(var(--muted-foreground));max-width:54ch;margin:0 auto;font-size:1rem}
.mg-hero{padding:18px 24px}
.mg-hero figure{margin:0;position:relative;border-radius:var(--radius);overflow:hidden;border:1px solid hsl(var(--border))}
.mg-hero img{width:100%;aspect-ratio:4/5;object-fit:cover}
.mg-aspect{position:absolute;top:12px;left:12px;background:hsl(var(--secondary) / .85);color:hsl(var(--secondary-foreground));font:600 .72rem/1 ui-monospace,Menlo,Consolas,monospace;padding:5px 9px;border-radius:6px;letter-spacing:.04em}
.mg-cap{padding:10px 4px 0}.mg-cap .mg-shot{font-weight:700;font-size:.98rem}.mg-cap .mg-intent{color:hsl(var(--muted-foreground));font-size:.88rem;margin-top:2px}.mg-cap .mg-illus{color:hsl(var(--muted-foreground));font-size:.74rem;font-style:italic;margin-top:4px}
.mg-grid-wrap{padding:8px 24px 24px}
.mg-grid-wrap h2{font-size:1.2rem;font-weight:700;margin:18px 0 12px;letter-spacing:-0.01em}
.mg-grid{display:grid;grid-template-columns:1fr;gap:22px}
.mg-tile figure{margin:0;border-radius:var(--radius);overflow:hidden;border:1px solid hsl(var(--border));position:relative}
.mg-tile img{width:100%;aspect-ratio:1/1;object-fit:cover}
.mg-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;aspect-ratio:1/1;border:2px dashed hsl(var(--border));border-radius:var(--radius);background:hsl(var(--muted));color:hsl(var(--muted-foreground));text-align:center;padding:18px}
.mg-empty strong{font-size:1rem;margin-bottom:4px}.mg-empty span{font-size:.8rem}
.mg-foot{font:12px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:hsl(var(--muted-foreground));text-align:center;padding:24px}
.mg-foot .mg-badge-sample{display:inline-block;border-radius:6px;padding:3px 12px;color:#fff;margin-bottom:8px;font-size:.78rem;background:#b8860b}
@media(min-width:640px){.mg-grid{grid-template-columns:repeat(2,1fr)}}
@media(min-width:920px){.mg-grid{grid-template-columns:repeat(3,1fr)}}
@media print{.mg-bar{position:static}body{background:#fff;color:#000}@page{margin:1cm}}
</style>
</head>
<body>
<main class="mg-doc">
<header class="mg-bar" role="banner"><div class="mg-brand">${mgExt.brandName}<small>${mgExt.brandTag}</small></div></header>

<div class="mg-head">
<div class="mg-eyebrow">Galeria de midia -- media_photo</div>
<h1>${mgExt.eyebrowH1}</h1>
<p>${mgExt.headParagraph}</p>
</div>

<section class="mg-hero">
<figure>
<span class="mg-aspect">4:5 -- hero / feed</span>
<img src="${mgExt.hero.img}" alt="${mgExt.hero.alt}" data-slot-key="hero" data-kind="image" data-editable="true" data-upload-fallback="true">
</figure>
<div class="mg-cap"><div class="mg-shot">${mgExt.hero.shotLabel}</div><div class="mg-intent">${mgExt.hero.intent}</div><div class="mg-illus">imagem ilustrativa -- amostra, pode diferir do produto final</div></div>
</section>

<div class="mg-grid-wrap">
<h2>Shot list</h2>
<div class="mg-grid">

<div class="mg-tile"><figure><span class="mg-aspect">1:1 -- detalhe</span><img src="${mgExt.tiles[0].img}" alt="${mgExt.tiles[0].alt}" data-slot-key="detalhe" data-kind="image" data-editable="true" data-upload-fallback="true"></figure>
<div class="mg-cap"><div class="mg-shot">${mgExt.tiles[0].shotLabel}</div><div class="mg-intent">${mgExt.tiles[0].intent}</div><div class="mg-illus">imagem ilustrativa -- amostra</div></div></div>

<div class="mg-tile"><figure><span class="mg-aspect">4:5 -- lifestyle</span><img src="${mgExt.tiles[1].img}" alt="${mgExt.tiles[1].alt}" data-slot-key="lifestyle" data-kind="image" data-editable="true" data-upload-fallback="true"></figure>
<div class="mg-cap"><div class="mg-shot">${mgExt.tiles[1].shotLabel}</div><div class="mg-intent">${mgExt.tiles[1].intent}</div><div class="mg-illus">imagem ilustrativa -- amostra</div></div></div>

<div class="mg-tile"><figure><span class="mg-aspect">9:16 -- escala</span><img src="${mgExt.tiles[2].img}" alt="${mgExt.tiles[2].alt}" data-slot-key="escala" data-kind="image" data-editable="true" data-upload-fallback="true"></figure>
<div class="mg-cap"><div class="mg-shot">${mgExt.tiles[2].shotLabel}</div><div class="mg-intent">${mgExt.tiles[2].intent}</div><div class="mg-illus">imagem ilustrativa -- amostra</div></div></div>

<div class="mg-tile"><figure><span class="mg-aspect">1:1 -- packshot</span><img src="${mgExt.tiles[3].img}" alt="${mgExt.tiles[3].alt}" data-slot-key="packshot" data-kind="image" data-editable="true" data-upload-fallback="true"></figure>
<div class="mg-cap"><div class="mg-shot">${mgExt.tiles[3].shotLabel}</div><div class="mg-intent">${mgExt.tiles[3].intent}</div><div class="mg-illus">imagem ilustrativa -- amostra</div></div></div>

<div class="mg-tile"><div class="mg-empty" data-slot-key="foto_real_produto" data-kind="image" data-editable="true" data-upload-fallback="true"><strong>[ + ] Foto real do produto</strong><span>slot vazio -- envie a sua para substituir a amostra</span></div></div>

</div>
</div>

<footer class="mg-foot" role="contentinfo">
<span class="mg-badge-sample">amostra -- dados simulados</span><br>
${mgExt.footerLine}
</footer>
</main>
</body>
</html>
`;
