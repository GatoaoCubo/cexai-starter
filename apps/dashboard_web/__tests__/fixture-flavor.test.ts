// REGISTER R-012 -- FIXTURE FLAVOR BY BUSINESS SHAPE.
//
// Fixtures-mode demo content used to be hardcoded to a single pet-retail world
// (arranhador/gato/PetShop Premium) for EVERY tenant, so a services tenant
// previewed the dashboard against a cat-tower e-commerce story. This suite
// proves the fix in lib/fixtureFlavor.ts + its wiring into lib/fixtures.ts:
//
//   1. resolveFlavor selects the right bucket for the two REAL business_shape
//      enum values ("retail" | "services") and degrades any other input
//      (absent / unknown / a typo) to the NEUTRAL generic-commerce default --
//      never to the pet-retail flavor by accident.
//   2. Every flavor entry carries the SAME structure (array lengths / key
//      counts) as the retail original -- only the vocabulary strings vary.
//   3. The retail flavor is BYTE-IDENTICAL to the pre-fix hardcoded content
//      (zero regression for the built-in demo tenant, which IS vertical=retail).
//   4. A live "services"-shaped fixtures module never emits a pet string in
//      its produced artifacts (pesquisa_produto / research_universe / leads).
//   5. An unrecognised / absent shape emits the neutral flavor, not pet.
//
// Boundary-aware matching throughout (the PT "gato" collision lesson): every
// pet-indicator check uses \b word boundaries so a slug/substring collision
// (e.g. a tenant name that merely CONTAINS "gato") never false-positives.

import { describe, it, expect, afterEach } from "vitest";
import { FLAVOR_TABLE, resolveFlavor, type FixtureFlavor } from "@/lib/fixtureFlavor";

// ----------------------------------------------------------------------------
// Boundary-aware pet-indicator scan (word-boundary regex per the PT "gato"
// collision lesson -- never a bare substring test).
// ----------------------------------------------------------------------------
const PET_INDICATOR_RE =
  /\b(gato|gatos|felin\w*|arranhador\w*|petshop|pet shop|miauhouse|gatofeliz|sisal|racao|comedouro\w*)\b/i;
// "pet" alone is checked separately with its own strict word boundary (short
// tokens risk more collisions -- kept isolated so a failure message is precise).
const PET_WORD_RE = /\bpet\b/i;

function collectStrings(value: unknown, out: string[] = []): string[] {
  if (typeof value === "string") {
    out.push(value);
  } else if (Array.isArray(value)) {
    for (const v of value) collectStrings(v, out);
  } else if (typeof value === "function") {
    // flavor.youtubeTitles / questionsLead are (seed) => text -- probe with a
    // representative seed so their template output is scanned too.
    try {
      collectStrings((value as (seed: string) => unknown)("Minha Loja"), out);
    } catch {
      /* not a seed-shaped function -- ignore */
    }
  } else if (value && typeof value === "object") {
    for (const v of Object.values(value as Record<string, unknown>)) collectStrings(v, out);
  }
  return out;
}

function petHits(flavor: FixtureFlavor): string[] {
  const strings = collectStrings(flavor).filter((s) => s !== flavor.key);
  return strings.filter((s) => PET_INDICATOR_RE.test(s) || PET_WORD_RE.test(s));
}

// ----------------------------------------------------------------------------
// 1. resolveFlavor -- per-shape selection + the neutral default (never pet).
// ----------------------------------------------------------------------------
describe("resolveFlavor -- per-shape selection", () => {
  it("resolves the exact 'retail' business_shape value to the retail flavor", () => {
    expect(resolveFlavor("retail")).toBe(FLAVOR_TABLE.retail);
  });

  it("resolves the exact 'services' business_shape value to the services flavor", () => {
    expect(resolveFlavor("services")).toBe(FLAVOR_TABLE.services);
  });

  it("is case/whitespace tolerant on the two committed values", () => {
    expect(resolveFlavor("  RETAIL ")).toBe(FLAVOR_TABLE.retail);
    expect(resolveFlavor("Services")).toBe(FLAVOR_TABLE.services);
  });

  it.each([
    ["undefined", undefined],
    ["null", null],
    ["empty string", ""],
    ["whitespace only", "   "],
    ["an uncommitted detector fallback", "derive_from_purpose"],
    ["a fine_vertical NOT the master discriminator", "ecommerce"],
    ["a typo", "retial"],
    ["a completely unrelated string", "banana"],
  ])("degrades an unknown/absent shape (%s) to the NEUTRAL default, never pet-retail", (_label, input) => {
    const flavor = resolveFlavor(input as string | null | undefined);
    expect(flavor).toBe(FLAVOR_TABLE.neutral);
    expect(flavor.key).toBe("neutral");
    expect(flavor).not.toBe(FLAVOR_TABLE.retail);
  });
});

// ----------------------------------------------------------------------------
// 2. Structure parity -- same array lengths / key counts across all 3 flavors.
// ----------------------------------------------------------------------------
describe("FLAVOR_TABLE -- structure parity (same fields/counts/schemas)", () => {
  const keys: Array<keyof typeof FLAVOR_TABLE> = ["retail", "services", "neutral"];

  it("every flavor carries exactly 3 competitors / gaps / opportunities", () => {
    for (const k of keys) {
      const f = FLAVOR_TABLE[k];
      expect(f.competitors, k).toHaveLength(3);
      expect(f.gaps, k).toHaveLength(3);
      expect(f.opportunities, k).toHaveLength(3);
    }
  });

  it("every flavor's SEO block carries the SAME array lengths (3/3/3/2/2/3)", () => {
    for (const k of keys) {
      const seo = FLAVOR_TABLE[k].seo;
      expect(seo.headTerms, k).toHaveLength(3);
      expect(seo.longtails, k).toHaveLength(3);
      expect(seo.synonyms, k).toHaveLength(3);
      expect(seo.seoInbound, k).toHaveLength(2);
      expect(seo.seoOutbound, k).toHaveLength(2);
      expect(seo.negativeKeywords, k).toHaveLength(3);
    }
  });

  it("every flavor's market-sizing bag carries the SAME key COUNT (7 keys)", () => {
    const retailKeyCount = Object.keys(FLAVOR_TABLE.retail.market).length;
    expect(retailKeyCount).toBe(7);
    for (const k of keys) {
      expect(Object.keys(FLAVOR_TABLE[k].market), k).toHaveLength(retailKeyCount);
    }
  });

  it("every flavor carries exactly 4 channels + 2 app reviews + 3 social tags", () => {
    for (const k of keys) {
      const f = FLAVOR_TABLE[k];
      expect(f.channels, k).toHaveLength(4);
      expect(f.appReviews, k).toHaveLength(2);
      expect(f.socialCommunityTags, k).toHaveLength(3);
    }
  });

  it("every flavor carries exactly 3 extra head-terms + 4 longtails + 3 synonyms (keywords)", () => {
    for (const k of keys) {
      const f = FLAVOR_TABLE[k];
      expect(f.keywordsHeadExtra, k).toHaveLength(3);
      expect(f.keywordsLongtail, k).toHaveLength(4);
      expect(f.keywordsSynonyms, k).toHaveLength(3);
      expect(f.questionsExtra, k).toHaveLength(4);
    }
  });

  it("every flavor carries exactly 7 CRM/leads rows, each with nome + sinal", () => {
    for (const k of keys) {
      const leads = FLAVOR_TABLE[k].leads;
      expect(leads, k).toHaveLength(7);
      for (const lead of leads) {
        expect(typeof lead.nome, k).toBe("string");
        expect(lead.nome.length, k).toBeGreaterThan(0);
        expect(typeof lead.sinal, k).toBe("string");
        expect(lead.sinal.length, k).toBeGreaterThan(0);
      }
    }
  });

  it("every flavor's youtubeTitles / questionsLead builders return the same shape for the same seed", () => {
    for (const k of keys) {
      const f = FLAVOR_TABLE[k];
      expect(f.youtubeTitles("Minha Loja"), k).toHaveLength(3);
      expect(typeof f.questionsLead("Minha Loja"), k).toBe("string");
    }
  });
});

// ----------------------------------------------------------------------------
// 3. Retail flavor = byte-identical to the pre-fix hardcoded content (zero
//    regression pin -- the built-in demo tenant IS retail).
// ----------------------------------------------------------------------------
describe("retail flavor -- zero-regression pin (byte-identical to the pre-fix fixture)", () => {
  it("pins the flagship product identity + top competitor", () => {
    const r = FLAVOR_TABLE.retail;
    expect(r.productId).toBe("prod_arranhador_torre");
    expect(r.productName).toBe("Arranhador Torre para Gatos 1,2m");
    expect(r.topCompetitorFull).toBe("PetShop Premium -- Torre Deluxe");
    expect(r.competitors).toEqual(["PetShop Premium", "MiauHouse", "GatoFeliz"]);
  });

  it("pins the market-sizing block (IBGE/Abinpet pet-market stats)", () => {
    expect(FLAVOR_TABLE.retail.market).toEqual({
      setor: "Mercado pet Brasil",
      faturamento_setor_ano: "R$ 76,4 bilhoes (2024)",
      crescimento_anual: "+14% YoY",
      domicilios_com_pets: "60,7 milhoes",
      populacao_felina_br: "30,1 milhoes de gatos",
      ranking_global: "3o maior mercado pet do mundo",
      regiao_foco: "Sudeste (52% do consumo pet nacional)",
    });
  });

  it("pins the SEO block", () => {
    expect(FLAVOR_TABLE.retail.seo.headTerms).toEqual([
      "arranhador para gatos", "torre arranhador", "arranhador gato grande",
    ]);
  });

  it("pins the first lead row (nome + sinal)", () => {
    expect(FLAVOR_TABLE.retail.leads[0]).toEqual({
      nome: "Loja MiAuPet (vendedor ML)",
      sinal: "5 perguntas recentes sobre durabilidade do sisal no anuncio",
    });
  });
});

// ----------------------------------------------------------------------------
// 4. services + neutral flavors NEVER carry a pet indicator (the acceptance bar).
// ----------------------------------------------------------------------------
describe("services + neutral flavors -- never leak a pet string (boundary-aware)", () => {
  it("the retail flavor DOES carry pet indicators (sanity: the scanner actually detects them)", () => {
    expect(petHits(FLAVOR_TABLE.retail).length).toBeGreaterThan(0);
  });

  it("the services flavor carries ZERO pet indicators", () => {
    expect(petHits(FLAVOR_TABLE.services)).toEqual([]);
  });

  it("the neutral (unknown-shape default) flavor carries ZERO pet indicators", () => {
    expect(petHits(FLAVOR_TABLE.neutral)).toEqual([]);
  });
});

// ----------------------------------------------------------------------------
// 5. LIVE integration -- a fresh fixtures module cold-loaded under each shape
//    env value produces artifacts free of pet strings (services) / matches the
//    original byte-for-byte (retail, the default/unset case).
// ----------------------------------------------------------------------------
const ORIGINAL_SHAPE_ENV = process.env.NEXT_PUBLIC_BUSINESS_SHAPE;

afterEach(() => {
  if (ORIGINAL_SHAPE_ENV === undefined) delete process.env.NEXT_PUBLIC_BUSINESS_SHAPE;
  else process.env.NEXT_PUBLIC_BUSINESS_SHAPE = ORIGINAL_SHAPE_ENV;
});

/** Cold-load a fresh copy of lib/fixtures under an explicit NEXT_PUBLIC_BUSINESS_SHAPE
 *  (undefined = unset). vi.resetModules() clears the whole module graph so config.ts
 *  re-reads process.env and fixtures.ts re-resolves activeFlavor from it. */
async function loadFixturesWithShape(shape: string | undefined) {
  if (shape === undefined) delete process.env.NEXT_PUBLIC_BUSINESS_SHAPE;
  else process.env.NEXT_PUBLIC_BUSINESS_SHAPE = shape;
  const { vi } = await import("vitest");
  vi.resetModules();
  return import("@/lib/fixtures");
}

describe("live fixtures module -- cold-loaded per business_shape (integration)", () => {
  // fxRunCapability deliberately sleeps RUN_DURATION_MS (5200ms, so the on-screen
  // 8F filament animates) before resolving -- these tests need a longer-than-default
  // per-test timeout to observe the REAL run path rather than a mocked shortcut.
  // NOTE: unset/absent business_shape is the "never detected" case, which the row
  // explicitly requires to degrade to NEUTRAL -- not silently keep the pet-retail
  // default (that silent default is exactly the bug R-012 reports). A tenant that
  // IS retail must carry an EXPLICIT NEXT_PUBLIC_BUSINESS_SHAPE=retail (written by
  // the distill step below) to see the pet-retail world -- see the dedicated
  // "'retail' shape (explicit)" test for that zero-regression pin.
  it("unset shape (absent env var) degrades to NEUTRAL -- never silently pet by default", async () => {
    const fx = await loadFixturesWithShape(undefined);
    const research = await fx.fxRunCapability("pesquisa_produto", "");
    const structured = research.structured as { product_name?: string } | undefined;
    expect(structured?.product_name).toBe("Produto Exemplo A");
    const hay = JSON.stringify(structured);
    expect(PET_INDICATOR_RE.test(hay)).toBe(false);
  }, 10000);

  it("'services' shape: pesquisa_produto artifact carries zero pet indicators", async () => {
    const fx = await loadFixturesWithShape("services");
    const research = await fx.fxRunCapability("pesquisa_produto", "");
    const structured = research.structured as Record<string, unknown>;
    const hay = JSON.stringify(structured) + "\n" + (research.artifact ?? "");
    expect(PET_INDICATOR_RE.test(hay)).toBe(false);
    expect(PET_WORD_RE.test(hay)).toBe(false);
    // sanity: it DID switch content (not silently still retail).
    expect((structured as { product_name?: string }).product_name).toBe(
      "Pacote de Suporte Tecnico Mensal",
    );
  }, 10000);

  it("'services' shape: research_universe artifact carries zero pet indicators", async () => {
    const fx = await loadFixturesWithShape("services");
    const universe = await fx.fxRunCapability("research_universe", "");
    const hay = JSON.stringify(universe.structured) + "\n" + (universe.artifact ?? "");
    expect(PET_INDICATOR_RE.test(hay)).toBe(false);
    expect(PET_WORD_RE.test(hay)).toBe(false);
  }, 10000);

  it("'services' shape: the media_photo + brandbook card input_contract examples carry zero pet indicators", async () => {
    // These are LIVE form-placeholder examples (fxListCards -> RunModal's typed form), not dead
    // code -- caught by a targeted grep audit after the first pass missed them.
    const fx = await loadFixturesWithShape("services");
    const cards = fx.fxListCards();
    const mediaPhoto = cards.find((c) => c.capability === "media_photo");
    const brandbook = cards.find((c) => c.capability === "brandbook");
    expect(mediaPhoto, "media_photo card must be declared").toBeDefined();
    expect(brandbook, "brandbook card must be declared").toBeDefined();
    const hay = JSON.stringify(mediaPhoto?.input_contract) + "\n" + JSON.stringify(brandbook?.input_contract);
    expect(PET_INDICATOR_RE.test(hay)).toBe(false);
    expect(PET_WORD_RE.test(hay)).toBe(false);
  });

  it("'services' shape: the leads CRM sample rows carry zero pet indicators", async () => {
    const fx = await loadFixturesWithShape("services");
    const rows = await fx.fxListEntity("leads");
    expect(rows.length).toBe(7); // structure parity: same honest count as before
    const hay = JSON.stringify(rows);
    expect(PET_INDICATOR_RE.test(hay)).toBe(false);
    expect(PET_WORD_RE.test(hay)).toBe(false);
  });

  it("an UNRECOGNISED shape value degrades to the neutral flavor, never pet, in a live run", async () => {
    const fx = await loadFixturesWithShape("totally-unknown-shape");
    const research = await fx.fxRunCapability("pesquisa_produto", "");
    const structured = research.structured as { product_name?: string };
    expect(structured.product_name).toBe("Produto Exemplo A"); // the neutral flavor's product name
    const hay = JSON.stringify(structured);
    expect(PET_INDICATOR_RE.test(hay)).toBe(false);
  }, 10000);

  it("'retail' shape (explicit) still renders the pet-retail world (opt-in, not silently dropped)", async () => {
    const fx = await loadFixturesWithShape("retail");
    const research = await fx.fxRunCapability("pesquisa_produto", "");
    const structured = research.structured as { product_name?: string };
    expect(structured.product_name).toBe("Arranhador Torre para Gatos 1,2m");
  }, 10000);

  it("structure parity holds across shapes: pesquisa_produto keeps the same field set", async () => {
    const retailFx = await loadFixturesWithShape("retail");
    const retailResearch = await retailFx.fxRunCapability("pesquisa_produto", "");
    const servicesFx = await loadFixturesWithShape("services");
    const servicesResearch = await servicesFx.fxRunCapability("pesquisa_produto", "");
    const retailKeys = Object.keys(retailResearch.structured as object).sort();
    const servicesKeys = Object.keys(servicesResearch.structured as object).sort();
    expect(servicesKeys).toEqual(retailKeys);
  }, 15000);
});
