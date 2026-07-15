import { describe, it, expect } from "vitest";
import {
  buildBrandAbout,
  buildHomeCopy,
  descriptionOf,
  galleryCandidates,
  priceOf,
  specRows,
  summaryOf,
  titleOf,
} from "@/lib/brandText";
import type { PublicCatalogItem } from "@/lib/types";

// ----------------------------------------------------------------------------
// brandText -- the PURE display pickers + the honest about model. These assert:
//   * the pickers tolerate an OPEN payload (an absent field never throws);
//   * galleryCandidates returns RAW candidates (the security boundary is the render
//     gate, not this picker) -- it must NOT silently drop an unsafe scheme here, so
//     the renderer (MediaGallery) is the single point that enforces isSafeMediaSrc;
//   * buildBrandAbout is HONEST: it surfaces only what the brand published (name +
//     tagline + palette) and never fabricates a story the tenant did not provide.
// ----------------------------------------------------------------------------

function item(over: Partial<PublicCatalogItem> = {}): PublicCatalogItem {
  return { id: "x1", kind: "marketplace_listing", published_at: null, ...over };
}

describe("brandText pickers", () => {
  it("titleOf picks the first present title-like key, else the id", () => {
    expect(titleOf(item({ title: "  A title " }))).toBe("A title");
    expect(titleOf(item({ name: "By name" }))).toBe("By name");
    expect(titleOf(item({ nome: "Por nome" }))).toBe("Por nome");
    expect(titleOf(item({ id: "rec_42" }))).toBe("rec_42"); // no title -> id
  });

  it("priceOf accepts a string or a finite number; '' otherwise", () => {
    expect(priceOf(item({ price: "R$ 10,00" }))).toBe("R$ 10,00");
    expect(priceOf(item({ preco: 49 }))).toBe("49");
    expect(priceOf(item({ price: Number.NaN }))).toBe("");
    expect(priceOf(item())).toBe("");
  });

  it("summaryOf / descriptionOf tolerate an absent field (no throw)", () => {
    expect(summaryOf(item())).toBe("");
    expect(descriptionOf(item())).toBe("");
    expect(summaryOf(item({ summary: "s" }))).toBe("s");
    expect(descriptionOf(item({ description: "d", summary: "s" }))).toBe("d");
  });

  it("specRows reads a scalar object OR an array of {label,value}; skips nested values", () => {
    const fromObj = specRows(item({ specs: { Altura: "1,2 m", Peso: 8, Ativo: true, Nested: { a: 1 } } }));
    expect(fromObj).toEqual([
      { label: "Altura", value: "1,2 m" },
      { label: "Peso", value: "8" },
      { label: "Ativo", value: "sim" },
    ]); // the nested object value is skipped

    const fromArr = specRows(item({ attributes: [{ label: "Cor", value: "Bege" }, { name: "SKU", value: "AB-1" }] }));
    expect(fromArr).toEqual([
      { label: "Cor", value: "Bege" },
      { label: "SKU", value: "AB-1" },
    ]);

    expect(specRows(item())).toEqual([]); // no specs -> empty
  });

  it("galleryCandidates collects array + single keys, de-duped, and does NOT pre-filter scheme", () => {
    const cands = galleryCandidates(
      item({
        images: ["https://cdn/a.jpg", "javascript:alert(1)", "https://cdn/a.jpg"],
        image: "data:image/png;base64,AAAA",
      }),
    );
    // de-duplicated; preserves order; the UNSAFE candidate is STILL present here -- the
    // render gate (MediaGallery/isSafeMediaSrc) is the security boundary, not this picker.
    expect(cands).toEqual([
      "https://cdn/a.jpg",
      "javascript:alert(1)",
      "data:image/png;base64,AAAA",
    ]);
    expect(galleryCandidates(item())).toEqual([]);
  });
});

describe("buildBrandAbout -- honest, never fabricated", () => {
  it("surfaces the tagline as a block ONLY when the brand published one", () => {
    const withTag = buildBrandAbout({ name: "Acme", tagline: "We make things" });
    expect(withTag.name).toBe("Acme");
    expect(withTag.tagline).toBe("We make things");
    expect(withTag.paragraphs.some((p) => p.body === "We make things")).toBe(true);

    const noTag = buildBrandAbout({ name: "Acme" });
    expect(noTag.tagline).toBe("");
    // no tagline -> no tagline-derived block, but the catalog + transparency blocks remain.
    expect(noTag.paragraphs.length).toBeGreaterThanOrEqual(2);
    expect(noTag.paragraphs.some((p) => p.heading === "Transparencia")).toBe(true);
  });

  it("degrades to a neutral name + blocks for an empty brand (no crash, no invention)", () => {
    const about = buildBrandAbout(undefined);
    expect(about.name).toBe("Esta marca");
    expect(about.paragraphs.length).toBeGreaterThan(0);
    expect(about.swatches).toEqual([]); // no tokens -> no swatches
  });

  it("builds palette swatches ONLY from published token triplets", () => {
    const about = buildBrandAbout({ name: "Acme", tokens: { primary: "174 68% 50%", accent: "" } });
    // primary is published -> a swatch; the empty accent is dropped.
    expect(about.swatches).toEqual([{ label: "Primaria", hsl: "174 68% 50%" }]);
  });
});

describe("buildHomeCopy -- white-label, brand-agnostic", () => {
  it("weaves the brand NAME into the pillars (not the vertical)", () => {
    const copy = buildHomeCopy({ name: "Acme Tools" });
    expect(copy.pillars).toHaveLength(3);
    const joined = copy.pillars.map((p) => p.body).join(" ");
    expect(joined).toContain("Acme Tools");
  });

  it("is BRAND-AGNOSTIC: a non-cat tenant never shows cat copy", () => {
    const copy = buildHomeCopy({ name: "Acme Tools" });
    const all =
      copy.eyebrow +
      " " +
      copy.heroFallbackTagline +
      " " +
      copy.ctaBody +
      " " +
      copy.pillars.map((p) => p.title + " " + p.body).join(" ");
    const lower = all.toLowerCase();
    // no vertical leak (the old static copy said "gato"/"felino")
    expect(lower).not.toContain("gato");
    expect(lower).not.toContain("felin");
  });

  it("degrades to a neutral name for an empty brand (no crash)", () => {
    const copy = buildHomeCopy(undefined);
    expect(copy.pillars).toHaveLength(3);
    // the neutral fallback name is woven in (never a vertical, never empty)
    expect(copy.pillars.some((p) => p.body.includes("esta marca"))).toBe(true);
  });

  it("3rd-pillar icon is VERTICAL-AWARE: retail default = 'cat', services = 'heart' (no cat-face leak)", () => {
    // RETAIL default (demo-acme + unknown slug): the 3rd pillar restores the 'cat' glyph
    // (zero-regression for the retail vitrine). The icon vocabulary is the closed set.
    const retail = buildHomeCopy({ name: "Acme" });
    for (const p of retail.pillars) {
      expect(["sparkle", "shield", "heart", "headset", "cat"]).toContain(p.icon);
    }
    // the "Feito com cuidado" pillar is the cat glyph for retail.
    const retailCare = retail.pillars.find((p) => p.title === "Feito com cuidado");
    expect(retailCare?.icon).toBe("cat");

    // SERVICES tenant: the SAME pillar uses the brand-NEUTRAL 'heart' glyph -- never a
    // cat-face leak into a non-cat vertical.
    const services = buildHomeCopy({ name: "Acme" }, { isService: true });
    const svcCare = services.pillars.find((p) => p.title === "Feito com cuidado");
    expect(svcCare?.icon).toBe("heart");
    expect(services.pillars.some((p) => (p.icon as string) === "cat")).toBe(false);
  });

  it("is VERTICAL-AWARE: a RETAIL tenant gets the PIX/compra pillar (default)", () => {
    const copy = buildHomeCopy({ name: "Acme" });
    const joined = copy.pillars.map((p) => p.body).join(" ");
    // retail (default) keeps the commerce trust pillar.
    expect(joined).toContain("PIX");
    expect(copy.pillars.some((p) => p.icon === "shield")).toBe(true);
  });

  it("is VERTICAL-AWARE: a SERVICES tenant shows NO PIX/parcelamento/compra claim", () => {
    const copy = buildHomeCopy({ name: "Acme" }, { isService: true });
    const joined = (copy.pillars.map((p) => p.title + " " + p.body).join(" ") + " " + copy.ctaBody);
    // a services tenant must not claim a checkout it does not have.
    expect(joined).not.toContain("PIX");
    expect(joined).not.toContain("parcelamento");
    expect(joined.toLowerCase()).not.toContain("da compra");
    // it gets the support/atendimento pillar instead.
    expect(copy.pillars.some((p) => p.icon === "headset")).toBe(true);
    expect(joined).toContain("Atendimento humanizado");
  });
});
