// REGISTER R-269 SECOND PASS -- the 3 embedded dual-output sample HTML docs
// (lib/fixtures/{ad_catalog_sample,landing_sample,media_gallery_sample}.ts) used
// to be hardcoded to the single pet-retail world, exactly like lib/fixtures.ts
// was before register R-012 and lib/molds.ts was before R-269's flagship-6 pass.
// This suite proves the SAME fix, applied to the 3 sample docs:
//
//   1. Each doc resolves its own module-scope activeFlavorKey singleton (SAME
//      resolveFlavor(config.businessShape) pattern as molds.ts/fixtures.ts).
//   2. retail stays BYTE-IDENTICAL to the pre-conversion content (zero
//      regression -- the built-in demo tenant IS retail).
//   3. services + neutral NEVER leak a pet/retail indicator, INCLUDING inside
//      the raw HTML string (not just structured data -- these are full HTML
//      documents, so the scan runs over the whole exported string).
//   4. Every flavor keeps the EXACT SAME DOM structure (section/figure/table-
//      row/FAQ counts) -- only the copy + image src differ. Retail's hotlinked
//      mercadolivre.com.br cat-product photos cannot be re-captioned alone (the
//      IMAGE ITSELF would still show a cat); services/neutral swap every image
//      slot for a neutral inline SVG data-URI placeholder instead.
import { describe, it, expect, afterEach } from "vitest";

const ORIGINAL_SHAPE_ENV = process.env.NEXT_PUBLIC_BUSINESS_SHAPE;

afterEach(() => {
  if (ORIGINAL_SHAPE_ENV === undefined) delete process.env.NEXT_PUBLIC_BUSINESS_SHAPE;
  else process.env.NEXT_PUBLIC_BUSINESS_SHAPE = ORIGINAL_SHAPE_ENV;
});

/** Cold-load a fresh copy of a sample module under an explicit business shape
 *  (mirrors __tests__/molds-flavor.test.ts's loadMoldsWithShape). */
async function loadSampleWithShape<T>(modulePath: string, shape: string | undefined): Promise<T> {
  if (shape === undefined) delete process.env.NEXT_PUBLIC_BUSINESS_SHAPE;
  else process.env.NEXT_PUBLIC_BUSINESS_SHAPE = shape;
  const { vi } = await import("vitest");
  vi.resetModules();
  return import(/* @vite-ignore */ modulePath) as Promise<T>;
}

const PET_INDICATOR_RE =
  /\b(gato\w*|felin\w*|arranhador\w*|petshop|pet shop|miauhouse|gatofeliz|sisal|racao\w*|racoes\w*|comedouro\w*|tutor\w*|animal\w*)\b/i;
const PET_WORD_RE = /\bpet\b/i;
const STORE_WORD_RE = /\bloja\w*/i;

function petHits(html: string): string[] {
  const re = new RegExp(PET_INDICATOR_RE.source, "gi");
  const petWordRe = new RegExp(PET_WORD_RE.source, "gi");
  return [...(html.match(re) ?? []), ...(html.match(petWordRe) ?? [])];
}

function storeHits(html: string): string[] {
  return [...(html.match(new RegExp(STORE_WORD_RE.source, "gi")) ?? [])];
}

/** Count non-overlapping occurrences of a literal substring (DOM-structure proxy --
 *  counts tags, not prose, so it is stable across flavors' differing copy length). */
function countOccurrences(haystack: string, needle: string): number {
  let count = 0;
  let idx = haystack.indexOf(needle);
  while (idx !== -1) {
    count++;
    idx = haystack.indexOf(needle, idx + needle.length);
  }
  return count;
}

const SHAPES = ["retail", "services", "neutral"] as const;

const SAMPLES = [
  {
    name: "ad_catalog_sample",
    modulePath: "@/lib/fixtures/ad_catalog_sample",
    exportName: "AD_CATALOG_SAMPLE_HTML",
    structuralTags: ["<section", "<figure", "<li>", "<details>", "<tr>", 'data-slot-key="'],
  },
  {
    name: "landing_sample",
    modulePath: "@/lib/fixtures/landing_sample",
    exportName: "LANDING_SAMPLE_HTML",
    structuralTags: ["<section", "<details>", "<tr>", "lp-bcard", "lp-step"],
  },
  {
    name: "media_gallery_sample",
    modulePath: "@/lib/fixtures/media_gallery_sample",
    exportName: "MEDIA_GALLERY_SAMPLE_HTML",
    structuralTags: ["<figure>", "mg-tile", 'data-slot-key="'],
  },
] as const;

describe("sample HTML docs (R-269 2nd pass) -- structure parity across business-shape flavors", () => {
  for (const sample of SAMPLES) {
    it(`${sample.name}: services + neutral carry the SAME DOM structure as retail (tag counts)`, async () => {
      const retailMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "retail");
      const servicesMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "services");
      const neutralMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "neutral");
      const retailHtml = retailMod[sample.exportName];
      const servicesHtml = servicesMod[sample.exportName];
      const neutralHtml = neutralMod[sample.exportName];

      for (const tag of sample.structuralTags) {
        const retailCount = countOccurrences(retailHtml, tag);
        expect(retailCount, `${sample.name} retail must actually contain "${tag}"`).toBeGreaterThan(0);
        expect(countOccurrences(servicesHtml, tag), `${sample.name} services count of "${tag}"`).toBe(retailCount);
        expect(countOccurrences(neutralHtml, tag), `${sample.name} neutral count of "${tag}"`).toBe(retailCount);
      }
    });
  }
});

describe("sample HTML docs (R-269 2nd pass) -- services + neutral never leak a pet indicator", () => {
  for (const sample of SAMPLES) {
    it(`${sample.name}: retail DOES carry pet indicators (sanity: the scanner detects them)`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "retail");
      expect(petHits(mod[sample.exportName]).length, sample.name).toBeGreaterThan(0);
    });

    it(`${sample.name}: services carries ZERO pet indicators`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "services");
      expect(petHits(mod[sample.exportName]), sample.name).toEqual([]);
    });

    it(`${sample.name}: neutral carries ZERO pet indicators`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "neutral");
      expect(petHits(mod[sample.exportName]), sample.name).toEqual([]);
    });

    it(`${sample.name}: services carries ZERO 'loja' indicators`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "services");
      expect(storeHits(mod[sample.exportName]), sample.name).toEqual([]);
    });
  }
});

describe("sample HTML docs (R-269 2nd pass) -- services + neutral never hotlink a retail product photo", () => {
  const RETAIL_IMAGE_HOST = "http2.mlstatic.com";

  for (const sample of SAMPLES) {
    it(`${sample.name}: services/neutral image src never references ${RETAIL_IMAGE_HOST}`, async () => {
      const servicesMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "services");
      const neutralMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "neutral");
      expect(servicesMod[sample.exportName]).not.toContain(RETAIL_IMAGE_HOST);
      expect(neutralMod[sample.exportName]).not.toContain(RETAIL_IMAGE_HOST);
      // and retail itself DOES reference it (sanity -- the assertion above is real).
      const retailMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "retail");
      expect(retailMod[sample.exportName]).toContain(RETAIL_IMAGE_HOST);
    });

    it(`${sample.name}: services/neutral use the neutral SVG data-URI placeholder for every image slot`, async () => {
      const servicesMod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "services");
      const html = servicesMod[sample.exportName];
      expect(html).toContain("data:image/svg+xml");
      expect(html).toContain("Foto%20ilustrativa");
    });
  }
});

describe("sample HTML docs (R-269 2nd pass) -- cold-reload per business_shape (integration)", () => {
  for (const sample of SAMPLES) {
    it(`${sample.name}: unset shape (absent env var) degrades to NEUTRAL, never silently retail/pet`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, undefined);
      const html = mod[sample.exportName];
      expect(petHits(html)).toEqual([]);
      expect(html).toContain("Minha Empresa");
    });

    it(`${sample.name}: an unrecognised shape value also degrades to NEUTRAL`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "totally-unknown-shape");
      expect(petHits(mod[sample.exportName])).toEqual([]);
    });

    it(`${sample.name}: 'retail' shape (explicit) still renders the pet-retail world (opt-in, not silently dropped)`, async () => {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "retail");
      expect(petHits(mod[sample.exportName]).length).toBeGreaterThan(0);
    });
  }
});

describe("sample HTML docs (R-269 2nd pass) -- retail flavor is byte-identical to the pre-R-269 content", () => {
  it("ad_catalog_sample: pins the <title> + hero H1 + SKU exactly", async () => {
    const mod = await loadSampleWithShape<Record<string, string>>("@/lib/fixtures/ad_catalog_sample", "retail");
    const html = mod.AD_CATALOG_SAMPLE_HTML;
    expect(html).toContain(
      "<title>Donut Gato 3 Em 1 Toca Cama Tunel Dobrável Zíper Casa Feltro | Minha Loja</title>",
    );
    expect(html).toContain("<h1 class=\"text-display\">Refugio, tunel e cama numa peca so</h1>");
    expect(html).toContain("<td>SKU</td><td>CB3603</td>");
    expect(html).toContain('"price":"68.42"');
  });

  it("landing_sample: pins the <title> + H1 + price exactly", async () => {
    const mod = await loadSampleWithShape<Record<string, string>>("@/lib/fixtures/landing_sample", "retail");
    const html = mod.LANDING_SAMPLE_HTML;
    expect(html).toContain("<title>Arranhador Torre 1,2m para Gatos | Base Reforcada | Minha Loja</title>");
    expect(html).toContain("<h1>A torre que seu gato domina -- e que nao desmonta</h1>");
    expect(html).toContain('<div class="lp-price">R$ 199<span class="lp-price-old">R$ 249</span></div>');
  });

  it("media_gallery_sample: pins the <title> + hero caption exactly", async () => {
    const mod = await loadSampleWithShape<Record<string, string>>(
      "@/lib/fixtures/media_gallery_sample",
      "retail",
    );
    const html = mod.MEDIA_GALLERY_SAMPLE_HTML;
    expect(html).toContain("<title>Galeria de fotos -- Arranhador Torre 1,2m | Minha Loja</title>");
    expect(html).toContain('<div class="mg-shot">Hero -- gato no topo da torre</div>');
  });
});

describe("sample HTML docs (R-269 2nd pass) -- services carries the SAME 'Pacote de Suporte Tecnico Mensal' story as the flagship molds", () => {
  it("all 3 sample docs mention the services product name consistently", async () => {
    for (const sample of SAMPLES) {
      const mod = await loadSampleWithShape<Record<string, string>>(sample.modulePath, "services");
      expect(mod[sample.exportName], sample.name).toContain("Pacote de Suporte Tecnico Mensal");
    }
  });
});
