// tenantData.generated.ts -- SELF tenant config literal (cex_distill template-gen).
// The single-tenant collapse codemod (spec 4.I) imports `tenantData` from here.
// IDENTITY region (excluded from G-E byte-identity).
export const tenantData = {
  "slug": "starter",
  "brand": {
    "name": "Sua Empresa",
    "tagline": "",
    "archetype": "",
    "logo": "",
    "tokens": {
      "background": "0 0% 100%",
      "foreground": "222 47% 11%",
      "card": "0 0% 100%",
      "cardForeground": "222 47% 11%",
      "popover": "0 0% 100%",
      "popoverForeground": "222 47% 11%",
      "primary": "239 84% 67%",
      "primaryForeground": "0 0% 100%",
      "secondary": "215 25% 27%",
      "secondaryForeground": "0 0% 100%",
      "muted": "210 40% 96%",
      "mutedForeground": "215 16% 47%",
      "accent": "239 84% 67%",
      "accentForeground": "0 0% 100%",
      "border": "214 32% 91%",
      "input": "214 32% 91%",
      "ring": "239 84% 67%",
      "brand": "239 84% 67%",
      "brandForeground": "0 0% 100%",
      "brandMuted": "239 60% 95%",
      "highlight": "38 92% 50%",
      "highlightForeground": "222 47% 11%",
      "highlightMuted": "38 92% 95%",
      "radius": "0.75rem"
    }
  },
  "shape": {
    "vertical": "services",
    "has_store": true,
    "has_blog": true,
    "has_b2b": true,
    "b2b_mode": "corporate",
    "b2b_label": "Para Empresas",
    "imagery_mode": "brand",
    "public_kinds": [
      {
        "kind": "service",
        "label": "Servico",
        "blurb": "Seu servico principal [preencher] -- descreva aqui o que sua empresa oferece"
      }
    ],
    "blog_subtitle_category": "",
    "confidence": 0.0,
    "committed": true,
    "matched_signals": [],
    "rationale": "STARTER template default (NAO uma deteccao real -- confidence=0.0, matched_signals=[]) -- shape espelha o template full-featured (store+blog+b2b) para que toda secao fique visivel com placeholders [preencher]. committed=true aqui e uma CONFIRMACAO DO OPERADOR (fabricar o template completo de proposito, GDP rule 4), nao uma deteccao por sinais; rode cex_tenant_bootstrap.py / o bootstrap sobre a SUA marca para derivar e confirmar o SEU business_shape real.",
    "notes": [
      "STARTER nao preenchido -- zero sinais reais; isto e um default de template operador-confirmado, nao uma deteccao.",
      "Rode o bootstrap sobre sua fonte de marca (site URL, PDF ou logo) para substituir cada [preencher] e derivar o SEU business_shape real."
    ],
    "fine_vertical": "derive_from_purpose",
    "feature_scores": {
      "store": 0,
      "services": 0,
      "blog": 0,
      "b2b_wholesale": 0,
      "b2b_corporate": 0,
      "vertical_detect_confidence": 0.0,
      "layer1_confidence": 0.0,
      "layer2_confidence": 0.0
    }
  },
  "links": {},
  "content": {
    "heroSubline": "",
    "ctaLabel": "Fale conosco",
    "contact": {
      "phone": "",
      "email": "",
      "address": "",
      "whatsapp": "",
      "instagram": ""
    }
  },
  "imagery": null,
  "blog": {
    "categories": [],
    "posts": []
  },
  "b2b": {
    "mode": "corporate",
    "eyebrow": "Para empresas",
    "heroTitle": "Sua Empresa para Empresas",
    "heroSubline": "",
    "offers": [],
    "whoWeServe": "",
    "ctaLabel": "Fale conosco",
    "ctaWhatsapp": ""
  },
  "catalog": {},
  "partner_logo_urls": [],
  "tenant_id": "starter",
  "_demo_note": "Este e o STARTER SOBERANO (sovereign) da CEXAI: um molde NEUTRO e NAO PREENCHIDO. Toda a marca, paleta, textos e o business_shape aqui sao placeholders [preencher] ou um default de demonstracao -- nao ha nenhuma historia de empresa real ou ficticia. Para usar: rode o bootstrap (python _tools/cex_bootstrap.py, ou python _tools/cex_tenant_bootstrap.py --source <sua-URL-ou-PDF-ou-logo> --tenant <seu-slug> --execute --persist-config) sobre a SUA marca -- isso substitui cada [preencher] pelos seus dados reais e deriva o seu business_shape de verdade."
} as const;
export default tenantData;
