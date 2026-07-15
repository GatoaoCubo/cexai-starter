import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  ARCHETYPES,
  DESIGN_STYLES,
  LOGO_STATUSES,
  PRICING_MODELS,
  buildAnswers,
  buildAnswersFile,
  bootstrapCommand,
  deriveColorsFromDescription,
  emptyIntakeState,
  isHttpsUrl,
  parseDraft,
  parseResolveOutput,
  serializeDraft,
  splitList,
  validateIntake,
  INTAKE_DRAFT_STORAGE_KEY,
  type IntakeState,
} from "@/lib/intake";
import { POST as intakePost } from "@/app/api/intake/route";

// ----------------------------------------------------------------------------
// intake -- the PURE core of the /intake form (R-283). These tests assert the
// VALIDATION PARITY with the Python gate (_tools/brand_validate.py E1-E6 +
// W1-W4, plus the resolver's drop rules from _tools/cex_ingest_registry.py),
// the answers emission shape (structural mirror of
// examples/10_intake_form_v1/form_answers_borealis_cafe.yaml), the golden
// answers-file bytes (the committed fixture the Python side resolves in the
// cross-language proof), and the DEV gate's prod refusal at the route level.
// ----------------------------------------------------------------------------

/** A Borealis-equivalent form state -- the SAME invented tenant as the
 *  committed example fixture, typed the way a human would type it into the
 *  form (lists one-per-line, formality as the select's string value). */
function borealisState(): IntakeState {
  const s = emptyIntakeState();
  s["tenant.slug"] = "borealis-cafe";
  s["identity.brand_name"] = "Cafe Borealis";
  s["identity.brand_tagline"] =
    "Cafes especiais do cerrado, torrados na semana do envio";
  s["identity.brand_mission"] =
    "Levar cafe especial rastreavel do produtor do cerrado ao metodo de quem prepara em casa";
  s["identity.brand_values"] =
    "rastreabilidade\nfrescor\nparceria com produtores\nsimplicidade";
  s["identity.brand_story"] =
    "A Borealis nasceu em 2024 em Patrocinio-MG comprando microlotes direto de tres " +
    "familias produtoras. A loja propria vive em loja.borealis-cafe.example.com.br " +
    "e o atacado atende cafeterias da regiao.";
  s["archetype.brand_archetype"] = "everyman";
  s["archetype.brand_personality"] = "proximo\ncurioso\ntransparente";
  s["voice.tone"] = "proximo, direto, sem jargao de barista";
  s["voice.formality"] = "2";
  s["voice.language"] = "pt-BR";
  s["voice.do"] =
    "explicar a origem em uma frase\nfalar de frescor com datas reais\nconvidar para provar";
  s["voice.dont"] =
    "prometer notas sensoriais miraculosas\nusar jargao sem explicar\npressionar a compra";
  s["audience.icp"] =
    "Quem prepara cafe coado ou espresso em casa no Brasil e quer regularidade e " +
    "frescor sem virar especialista";
  s["audience.transformation"] =
    "From cafe de mercado sem data de torra to xicara fresca e rastreavel through " +
    "assinatura direta do produtor";
  s["visual.colors.primary"] = "#3B2A20";
  s["visual.colors.secondary"] = "#F4EDE3";
  s["visual.colors.accent"] = "#C97B3D";
  s["visual.logo"] = "https://borealis-cafe.example.com.br/logo.svg";
  s["visual.fonts.heading"] = "Fraunces";
  s["visual.fonts.body"] = "Inter";
  s["positioning.category"] = "cafe especial em assinatura (D2C)";
  s["positioning.uvp"] =
    "Assinatura de cafe especial do cerrado com torra na semana do envio e origem " +
    "rastreavel em cada pacote";
  s["positioning.content_pillars"] =
    "origem e produtores\nmetodos de preparo\nfrescor e torra";
  s["monetization.pricing_model"] = "hybrid";
  s["monetization.currency"] = "BRL";
  s["monetization.tiers"] = "b2c-assinatura\nb2c-avulso\nb2b-cafeterias\nmarketplace-ml";
  s["location.channels"] =
    "loja propria: https://loja.borealis-cafe.example.com.br\ninstagram\nmercado livre";
  s["shape_confirm.vertical"] = "retail";
  s["shape_confirm.has_store"] = "sim";
  s["shape_confirm.has_blog"] = "sim";
  s["shape_confirm.has_b2b"] = "sim";
  s["shape_confirm.b2b_mode"] = "wholesale";
  s["links.website"] = "https://borealis-cafe.example.com.br";
  s["links.store"] = "https://loja.borealis-cafe.example.com.br";
  s["links.instagram"] = "https://instagram.com/borealiscafe.fake";
  s["links.whatsapp"] = "https://wa.me/5500000000000";
  s["sources.site_url"] = "https://borealis-cafe.example.com.br";
  return s;
}

describe("validateIntake -- parity with brand_validate.py ERRORS (blocking)", () => {
  it("passes a fully valid submission with ZERO errors and ZERO warnings", () => {
    const { errors, warnings } = validateIntake(borealisState());
    expect(errors).toEqual({});
    expect(warnings).toEqual({});
  });

  it("E1: an empty form is missing all 16 required form fields (= the 14 validator fields; colors count as 1 with 3 subkeys)", () => {
    const { errors } = validateIntake(emptyIntakeState());
    expect(Object.keys(errors)).toHaveLength(16);
    expect(errors["identity.brand_name"]).toMatch(/obrigatorio/);
    expect(errors["visual.colors.accent"]).toMatch(/obrigatorio/);
    expect(errors["monetization.currency"]).toMatch(/obrigatorio/);
  });

  it("E2: fewer than 3 brand values is an ERROR (brand_validate.py:82-83)", () => {
    const s = borealisState();
    s["identity.brand_values"] = "frescor\nsimplicidade";
    const { errors } = validateIntake(s);
    expect(errors["identity.brand_values"]).toMatch(/3\+ itens/);
  });

  it("E3: an unknown archetype is an ERROR; case is forgiven like arch.lower() (:88-92)", () => {
    const s = borealisState();
    s["archetype.brand_archetype"] = "wizard";
    expect(validateIntake(s).errors["archetype.brand_archetype"]).toMatch(
      /arquetipo invalido/,
    );
    s["archetype.brand_archetype"] = "Everyman"; // validator lowercases before the enum check
    expect(validateIntake(s).errors["archetype.brand_archetype"]).toBeUndefined();
    expect(ARCHETYPES).toHaveLength(12);
  });

  it("E4: formality must be an integer 1-5 (:97-102; int('3') passes via the resolver coercion)", () => {
    const s = borealisState();
    for (const bad of ["0", "6", "abc", "2.5", "-1"]) {
      s["voice.formality"] = bad;
      expect(validateIntake(s).errors["voice.formality"], bad).toMatch(/inteiro de 1 a 5/);
    }
    for (const good of ["1", "3", "5", " 2 "]) {
      s["voice.formality"] = good;
      expect(validateIntake(s).errors["voice.formality"], good).toBeUndefined();
    }
  });

  it("E5: each color must match ^#[0-9a-fA-F]{6}$ (:121-129)", () => {
    const s = borealisState();
    for (const bad of ["#GGGGGG", "#3B2A2", "3B2A20", "#3B2A200", "red"]) {
      s["visual.colors.primary"] = bad;
      expect(validateIntake(s).errors["visual.colors.primary"], bad).toMatch(/HEX invalido/);
    }
    s["visual.colors.primary"] = "#aB3f9C"; // mixed case is valid per the pattern
    expect(validateIntake(s).errors["visual.colors.primary"]).toBeUndefined();
  });

  it("E6: pricing model is an EXACT enum-6 match (:139-143 -- the validator does NOT lowercase)", () => {
    const s = borealisState();
    s["monetization.pricing_model"] = "Hybrid";
    expect(validateIntake(s).errors["monetization.pricing_model"]).toMatch(/modelo invalido/);
    s["monetization.pricing_model"] = "one-time";
    expect(validateIntake(s).errors["monetization.pricing_model"]).toBeUndefined();
    expect(PRICING_MODELS).toHaveLength(6);
  });
});

describe("validateIntake -- parity with brand_validate.py WARNINGS (never blocking)", () => {
  it("W1: more than 7 values WARNS, never errors (:84-85)", () => {
    const s = borealisState();
    s["identity.brand_values"] = "a\nb\nc\nd\ne\nf\ng\nh";
    const { errors, warnings } = validateIntake(s);
    expect(errors["identity.brand_values"]).toBeUndefined();
    expect(warnings["identity.brand_values"]).toMatch(/8 itens/);
  });

  it("W2: language not matching xx-XX WARNS (:103-105)", () => {
    const s = borealisState();
    s["voice.language"] = "pt_br";
    const { errors, warnings } = validateIntake(s);
    expect(errors["voice.language"]).toBeUndefined();
    expect(warnings["voice.language"]).toMatch(/xx-XX/);
  });

  it("W3: transformation warning is START-anchored like Python re.match (:116-118)", () => {
    const s = borealisState();
    s["audience.transformation"] = "Sai de X para Y por Z";
    expect(validateIntake(s).warnings["audience.transformation"]).toMatch(/From X to Y/);
    // a prefix before 'From' breaks Python's re.match too -- mirror exactly.
    s["audience.transformation"] = "nota: From a to b through c";
    expect(validateIntake(s).warnings["audience.transformation"]).toMatch(/From X to Y/);
    s["audience.transformation"] = "from a to b through c"; // IGNORECASE parity
    expect(validateIntake(s).warnings["audience.transformation"]).toBeUndefined();
  });

  it("W4: a UVP under 20 chars WARNS, never errors (:134-136)", () => {
    const s = borealisState();
    s["positioning.uvp"] = "curta demais";
    const { errors, warnings } = validateIntake(s);
    expect(errors["positioning.uvp"]).toBeUndefined();
    expect(warnings["positioning.uvp"]).toMatch(/20\+/);
  });
});

describe("validateIntake -- resolver-side drop pre-validation (cex_ingest_registry.py)", () => {
  it("slug outside ^[a-z0-9][a-z0-9_-]{0,63}$ is flagged (the resolver would IGNORE it)", () => {
    const s = borealisState();
    s["tenant.slug"] = "Bad Slug";
    expect(validateIntake(s).errors["tenant.slug"]).toMatch(/slug invalido/);
    s["tenant.slug"] = ""; // optional: clearing it is always a valid way forward
    expect(validateIntake(s).errors["tenant.slug"]).toBeUndefined();
  });

  it("non-https links are flagged (normalize_links drops http:/protocol-relative)", () => {
    const s = borealisState();
    s["links.website"] = "http://borealis-cafe.example.com.br";
    expect(validateIntake(s).errors["links.website"]).toMatch(/https/);
    s["links.website"] = "//cdn.example.com/x";
    expect(validateIntake(s).errors["links.website"]).toMatch(/https/);
    expect(isHttpsUrl("https://ok.example.com")).toBe(true);
    expect(isHttpsUrl("javascript:alert(1)")).toBe(false);
  });

  it("credentials.crm_ref must be an env-var REF NAME, never a literal secret (R-276)", () => {
    const s = borealisState();
    s["credentials.crm_ref"] = "sk-live-1234567890";
    expect(validateIntake(s).errors["credentials.crm_ref"]).toMatch(/segredo literal/);
    s["credentials.crm_ref"] = "BOREALIS_CRM_KEY";
    expect(validateIntake(s).errors["credentials.crm_ref"]).toBeUndefined();
  });
});

describe("buildAnswers -- the form_v1 answers object", () => {
  it("structurally mirrors examples/10_intake_form_v1/form_answers_borealis_cafe.yaml (sections + keys, non-empty tier)", () => {
    const answers = buildAnswers(borealisState()) as unknown as Record<
      string,
      Record<string, unknown>
    >;
    // The example's catalog/credentials carry EMPTY refs (documentation); the
    // resolver skips empties, and the form OMITS empty optionals entirely.
    expect(Object.keys(answers)).toEqual([
      "form_version",
      "tenant",
      "identity",
      "archetype",
      "voice",
      "audience",
      "visual",
      "positioning",
      "monetization",
      "location",
      "shape_confirm",
      "links",
      "sources",
    ]);
    expect(Object.keys(answers.identity)).toEqual([
      "brand_name",
      "brand_tagline",
      "brand_mission",
      "brand_values",
      "brand_story",
    ]);
    expect(Object.keys(answers.archetype)).toEqual([
      "brand_archetype",
      "brand_personality",
    ]);
    expect(Object.keys(answers.voice)).toEqual([
      "tone",
      "formality",
      "language",
      "do",
      "dont",
    ]);
    expect(Object.keys(answers.audience)).toEqual(["icp", "transformation"]);
    expect(Object.keys(answers.visual)).toEqual(["colors", "logo", "fonts"]);
    expect(Object.keys(answers.visual.colors as object)).toEqual([
      "primary",
      "secondary",
      "accent",
    ]);
    expect(Object.keys(answers.positioning)).toEqual([
      "category",
      "uvp",
      "content_pillars",
    ]);
    expect(Object.keys(answers.monetization)).toEqual([
      "pricing_model",
      "currency",
      "tiers",
    ]);
    expect(Object.keys(answers.location)).toEqual(["channels"]);
    expect(Object.keys(answers.shape_confirm)).toEqual([
      "vertical",
      "has_store",
      "has_blog",
      "has_b2b",
      "b2b_mode",
    ]);
    expect(Object.keys(answers.links)).toEqual([
      "website",
      "store",
      "instagram",
      "whatsapp",
    ]);
    expect(Object.keys(answers.sources)).toEqual(["site_url"]);
  });

  it("emits typed values: int formality, real arrays, booleans for shape confirms", () => {
    const answers = buildAnswers(borealisState());
    expect(answers.form_version).toBe(1);
    expect(answers.voice?.formality).toBe(2); // number, not "2"
    expect(answers.identity?.brand_values).toEqual([
      "rastreabilidade",
      "frescor",
      "parceria com produtores",
      "simplicidade",
    ]);
    expect(answers.shape_confirm?.has_store).toBe(true);
  });

  it("applies the resolver's coercions: archetype lowercased, currency uppercased", () => {
    const s = borealisState();
    s["archetype.brand_archetype"] = "Everyman";
    s["monetization.currency"] = "brl";
    const answers = buildAnswers(s);
    expect(answers.archetype?.brand_archetype).toBe("everyman");
    expect(answers.monetization?.currency).toBe("BRL");
  });

  it("keeps a human 'nao' as boolean false (never pruned -- a no IS an answer)", () => {
    const s = borealisState();
    s["shape_confirm.has_blog"] = "nao";
    expect(buildAnswers(s).shape_confirm?.has_blog).toBe(false);
  });

  it("omits empty optional sections entirely (an empty form is just form_version)", () => {
    expect(buildAnswers(emptyIntakeState())).toEqual({ form_version: 1 });
  });

  it("splitList accepts one-per-line AND comma-separated (the resolver's own comma split)", () => {
    expect(splitList("a, b, c")).toEqual(["a", "b", "c"]);
    expect(splitList("a\nb\n\n c ")).toEqual(["a", "b", "c"]);
    expect(splitList(undefined)).toEqual([]);
  });
});

// The committed golden fixture: the EXACT answers file the form's download
// emits for the Borealis-equivalent state. The Python side of the proof runs
//   python _tools/cex_ingest_registry.py --resolve <this fixture> ...
//   python _tools/brand_validate.py --config <emitted brand_init> --json
// Regenerate deliberately with: INTAKE_WRITE_FIXTURE=1 npx vitest run __tests__/intake.test.ts
// (path is cwd-based: vitest's root IS apps/public_site -- the npm test contract.
//  import.meta.url is http-scheme under the jsdom environment, so it cannot be used.)
const FIXTURE_PATH = join(
  process.cwd(),
  "__tests__",
  "fixtures",
  "intake_form_answers_emitted.yaml",
);

describe("buildAnswersFile -- the downloadable answers YAML", () => {
  it("is byte-identical to the committed cross-language fixture", () => {
    const text = buildAnswersFile(borealisState());
    if (process.env.INTAKE_WRITE_FIXTURE === "1") {
      mkdirSync(dirname(FIXTURE_PATH), { recursive: true });
      writeFileSync(FIXTURE_PATH, text, "utf8");
    }
    const committed = readFileSync(FIXTURE_PATH, "utf8").replace(/\r\n/g, "\n");
    expect(text).toBe(committed);
  });

  it("carries a '#' comment header and a JSON body (JSON is a YAML subset -> PyYAML-parseable)", () => {
    const text = buildAnswersFile(borealisState());
    expect(text.startsWith("# R-149 form_v1 answers")).toBe(true);
    const body = text
      .split("\n")
      .filter((l) => !l.startsWith("#"))
      .join("\n");
    const parsed = JSON.parse(body) as { form_version: number };
    expect(parsed.form_version).toBe(1);
    expect(text.endsWith("\n")).toBe(true);
  });
});

describe("parseResolveOutput -- the resolver CLI's stable ASCII contract", () => {
  it("parses the OK summary + indented [WARN] lines", () => {
    const stdout =
      "[OK] resolved form_v1: 28 field(s) emitted, 2 warning(s), 0 deferred, 0 unmapped\n" +
      "  [WARN] links dropped by the https-only sanitizer: x\n" +
      "  [WARN] links.store folded into location.BRAND_CHANNELS (store-domain lift)\n" +
      "[OK] brand_init written: .cex/runtime/intake/x_brand_init.yaml\n";
    const r = parseResolveOutput(stdout, 0);
    expect(r.ok).toBe(true);
    expect(r.summary).toMatch(/28 field\(s\) emitted/);
    expect(r.warnings).toHaveLength(2);
    expect(r.warnings[0]).toMatch(/https-only sanitizer/);
    expect(r.failures).toEqual([]);
  });

  it("parses a fail-closed [FAIL] refusal", () => {
    const r = parseResolveOutput(
      "[FAIL] unsupported form_version 2 (this resolver speaks 1)\n",
      1,
    );
    expect(r.ok).toBe(false);
    expect(r.failures[0]).toMatch(/unsupported form_version/);
    expect(r.summary).toBeNull();
  });

  it("is TOTAL on empty / non-string stdout", () => {
    expect(parseResolveOutput(undefined, null)).toEqual({
      ok: false,
      summary: null,
      warnings: [],
      failures: [],
    });
  });
});

describe("bootstrapCommand", () => {
  it("mirrors the resolver's own --out header consume line", () => {
    expect(bootstrapCommand("borealis-cafe", "brand_init.yaml")).toBe(
      "python _tools/cex_bootstrap.py --tenant borealis-cafe --from-file brand_init.yaml",
    );
    expect(bootstrapCommand(null, "x.yaml")).toBe(
      "python _tools/cex_bootstrap.py --from-file x.yaml",
    );
  });
});

// ----------------------------------------------------------------------------
// v2 (2026-07-07, decision_manifest_intake_v2_2026_07_07.yaml): 17 new
// OPTIONAL fields (docs/PROPOSAL_INTAKE_FORM_V2_2026_07_07.md). Every check
// below asserts the hard manifest constraint: "TODOS os 15 novos =
// OPCIONAIS/soft-warn" -- a malformed v2 field NEVER populates `errors`.
// ----------------------------------------------------------------------------

/** borealisState() extended with ALL v2 fields filled -- a description-colors
 *  case (mirrors examples/10_intake_form_v1/form_answers_estufa_aurora_v2.yaml). */
function v2State(): IntakeState {
  const s = borealisState();
  s["contact.name"] = "Marina Duarte";
  s["contact.email"] = "marina@estufa-aurora.example.com.br";
  s["identity.legal_name"] = "Estufa Aurora Comercio de Plantas LTDA";
  s["identity.vision"] = "Ser a lembranca de quem decide ter uma planta em casa";
  s["audience.wtp_band"] = "R$ 39-159";
  s["audience.demographics"] = "22-40 anos, urbano, primeiro apartamento";
  s["visual.colors_avoid"] = "rosa choque\nneon";
  s["visual.style_avoid"] = "infantil demais\ncorporativo frio";
  s["visual.design_style"] = "organico";
  s["visual.logo_status"] = "primeiro";
  s["visual.references"] = "https://instagram.com/outraestufa.fake";
  s["positioning.offerings"] = "mudas resistentes, kits de primeira planta";
  s["location.city_state"] = "Belo Horizonte - MG";
  s["market.competitors"] = "Estufa Verde Vida";
  s["market.edge_notes"] = "A maioria vende a planta e some";
  s["market.trends"] = "assinaturas de reposicao crescendo";
  s["applications.surfaces"] = "loja online\nredes sociais";
  return s;
}

describe("v2 -- validateIntake: the 17 new fields are ALWAYS optional/soft-warn", () => {
  it("a fully valid v2 submission still has ZERO errors and ZERO warnings", () => {
    const { errors, warnings } = validateIntake(v2State());
    expect(errors).toEqual({});
    expect(warnings).toEqual({});
  });

  it("an empty form's error count is UNCHANGED at 16 -- no v2 field is ever required", () => {
    const { errors } = validateIntake(emptyIntakeState());
    expect(Object.keys(errors)).toHaveLength(16);
  });

  it("wtp_band: fewer than 2 numbers WARNS, never errors", () => {
    const s = v2State();
    s["audience.wtp_band"] = "bem barato";
    const { errors, warnings } = validateIntake(s);
    expect(errors["audience.wtp_band"]).toBeUndefined();
    expect(warnings["audience.wtp_band"]).toMatch(/R\$ MIN-MAX/);
    s["audience.wtp_band"] = "R$ 39-159"; // 2 numbers -> no warning
    expect(validateIntake(s).warnings["audience.wtp_band"]).toBeUndefined();
  });

  it("contact.email: an invalid shape WARNS, never errors", () => {
    const s = v2State();
    s["contact.email"] = "not-an-email";
    const { errors, warnings } = validateIntake(s);
    expect(errors["contact.email"]).toBeUndefined();
    expect(warnings["contact.email"]).toMatch(/invalido/);
  });

  it("visual.design_style: outside the curated list WARNS, never errors", () => {
    const s = v2State();
    s["visual.design_style"] = "cyberpunk-retro-fusion";
    const { errors, warnings } = validateIntake(s);
    expect(errors["visual.design_style"]).toBeUndefined();
    expect(warnings["visual.design_style"]).toMatch(/fora da lista/);
    expect(DESIGN_STYLES).toHaveLength(8);
  });

  it("visual.logo_status: outside primeiro/renovar WARNS, never errors", () => {
    const s = v2State();
    s["visual.logo_status"] = "nao sei";
    const { errors, warnings } = validateIntake(s);
    expect(errors["visual.logo_status"]).toBeUndefined();
    expect(warnings["visual.logo_status"]).toMatch(/primeiro.*renovar/);
    expect(LOGO_STATUSES).toHaveLength(2);
  });

  it("an undecidable colors_description with NO hex given WARNS, never errors", () => {
    const s = emptyIntakeState();
    s["visual.colors_description"] = "so um pouco de verde";
    const { errors, warnings } = validateIntake(s);
    // the 3 color slots are STILL required (undecidable description) --
    // that is E1, not a new v2 error.
    expect(errors["visual.colors.primary"]).toMatch(/obrigatorio/);
    expect(warnings["visual.colors_description"]).toMatch(/nao foi possivel/);
  });
});

describe("v2 -- DP3: visual.colors_description satisfies the required color slots", () => {
  it("a description that derives 3 colors clears the 3 required color errors", () => {
    const s = emptyIntakeState();
    s["visual.colors_description"] =
      "Verde musgo das folhas, marrom quente da terra e um toque dourado";
    const { errors } = validateIntake(s);
    expect(errors["visual.colors.primary"]).toBeUndefined();
    expect(errors["visual.colors.secondary"]).toBeUndefined();
    expect(errors["visual.colors.accent"]).toBeUndefined();
  });

  it("literal HEX (when present) is unaffected by an ALSO-present description", () => {
    const s = borealisState(); // has all 3 hex filled
    s["visual.colors_description"] = "so um pouco de verde"; // undecidable on its own
    const { errors } = validateIntake(s);
    expect(errors["visual.colors.primary"]).toBeUndefined();
  });

  it("an invalid literal HEX is STILL flagged even with a valid description present", () => {
    const s = borealisState();
    s["visual.colors.primary"] = "#GGGGGG";
    s["visual.colors_description"] =
      "Verde musgo das folhas, marrom quente da terra e um toque dourado";
    // E5 (format) is independent of the DP3 alt-path: a non-empty malformed
    // value is still a real mistake to flag, regardless of the description.
    expect(validateIntake(s).errors["visual.colors.primary"]).toMatch(/HEX invalido/);
  });
});

describe("v2 -- deriveColorsFromDescription (mirrors _tools/cex_ingest_registry.py)", () => {
  it("derives 3 distinct colors in reading order", () => {
    expect(
      deriveColorsFromDescription(
        "Verde musgo das folhas, marrom quente da terra e um toque dourado no letreiro",
      ),
    ).toEqual({ primary: "#4A5D23", secondary: "#6F4E37", accent: "#C9A227" });
  });

  it("masks a compound phrase so its generic root never double-counts", () => {
    const derived = deriveColorsFromDescription("verde musgo, marrom e dourado");
    expect(derived && Object.values(derived)).toEqual(["#4A5D23", "#6F4E37", "#C9A227"]);
  });

  it("returns null for fewer than 3 distinct colors", () => {
    expect(deriveColorsFromDescription("so verde e marrom, mais nada")).toBeNull();
  });

  it("returns null for empty/blank text", () => {
    expect(deriveColorsFromDescription("")).toBeNull();
    expect(deriveColorsFromDescription("   ")).toBeNull();
  });

  it("repeating the same color word thrice is not three distinct colors", () => {
    expect(deriveColorsFromDescription("azul, azul, azul")).toBeNull();
  });
});

describe("v2 -- buildAnswers: sparse emission of the 17 new optional fields", () => {
  it("omits ALL v2 sections/keys for the plain v1 borealisState()", () => {
    const answers = buildAnswers(borealisState()) as unknown as Record<string, unknown>;
    expect(answers.contact).toBeUndefined();
    expect(answers.market).toBeUndefined();
    expect(answers.applications).toBeUndefined();
    expect(
      (answers.identity as Record<string, unknown> | undefined)?.legal_name,
    ).toBeUndefined();
    expect(
      (answers.audience as Record<string, unknown> | undefined)?.wtp_band,
    ).toBeUndefined();
  });

  it("emits ONLY the one v2 field that was filled (sparse -- absent key, not empty string)", () => {
    const s = borealisState();
    s["market.competitors"] = "Acme Coffee Co";
    const answers = buildAnswers(s) as unknown as Record<string, unknown>;
    expect(answers.market).toEqual({ competitors: ["Acme Coffee Co"] });
    expect(answers.contact).toBeUndefined();
    expect(answers.applications).toBeUndefined();
    expect(
      (answers.visual as Record<string, unknown> | undefined)?.design_style,
    ).toBeUndefined();
  });

  it("emits the full v2 shape when every new field is filled", () => {
    const answers = buildAnswers(v2State());
    expect(answers.contact).toEqual({
      name: "Marina Duarte",
      email: "marina@estufa-aurora.example.com.br",
    });
    expect(answers.market).toEqual({
      competitors: ["Estufa Verde Vida"],
      edge_notes: "A maioria vende a planta e some",
      trends: "assinaturas de reposicao crescendo",
    });
    expect(answers.applications).toEqual({ surfaces: ["loja online", "redes sociais"] });
    expect(answers.identity?.legal_name).toBe("Estufa Aurora Comercio de Plantas LTDA");
    expect(answers.audience?.wtp_band).toBe("R$ 39-159");
    expect(answers.visual?.design_style).toBe("organico");
    expect(answers.visual?.logo_status).toBe("primeiro");
    expect(answers.location?.city_state).toBe("Belo Horizonte - MG");
  });

  it("emits colors_description sparsely alongside literal colors (both can coexist)", () => {
    const s = borealisState();
    s["visual.colors_description"] = "verde musgo, marrom, dourado";
    const answers = buildAnswers(s);
    expect(answers.visual?.colors_description).toBe("verde musgo, marrom, dourado");
    expect(answers.visual?.colors).toEqual({
      primary: "#3B2A20",
      secondary: "#F4EDE3",
      accent: "#C97B3D",
    });
  });

  it("lowercases design_style/logo_status the same way the resolver coerces them", () => {
    const s = borealisState();
    s["visual.design_style"] = "Organico";
    s["visual.logo_status"] = "Primeiro";
    const answers = buildAnswers(s);
    expect(answers.visual?.design_style).toBe("organico");
    expect(answers.visual?.logo_status).toBe("primeiro");
  });
});

describe("v2 -- draft persistence: serializeDraft / parseDraft (localStorage payload)", () => {
  it("round-trips a filled state exactly", () => {
    const state = v2State();
    const text = serializeDraft(state, () => "2026-07-07T12:00:00.000Z");
    const restored = parseDraft(text);
    expect(restored).toEqual(state);
  });

  it("the serialized payload carries version + savedAt + state", () => {
    const text = serializeDraft(emptyIntakeState(), () => "2026-07-07T12:00:00.000Z");
    const parsed = JSON.parse(text) as { version: number; savedAt: string; state: unknown };
    expect(parsed.version).toBe(1);
    expect(parsed.savedAt).toBe("2026-07-07T12:00:00.000Z");
    expect(parsed.state).toBeTruthy();
  });

  it("returns null for null/undefined/empty input (never throws)", () => {
    expect(parseDraft(null)).toBeNull();
    expect(parseDraft(undefined)).toBeNull();
    expect(parseDraft("")).toBeNull();
  });

  it("returns null for unparseable JSON", () => {
    expect(parseDraft("{not json")).toBeNull();
  });

  it("returns null for a wrong version (future-proofing an incompatible shape change)", () => {
    expect(parseDraft(JSON.stringify({ version: 2, state: {} }))).toBeNull();
  });

  it("returns null for a foreign/unrelated JSON shape", () => {
    expect(parseDraft(JSON.stringify({ hello: "world" }))).toBeNull();
    expect(parseDraft(JSON.stringify(["not", "an", "object"]))).toBeNull();
  });

  it("a partial draft (missing v2 keys, e.g. saved before v2 shipped) restores cleanly", () => {
    const partial = { version: 1, savedAt: "x", state: { "identity.brand_name": "Old Draft" } };
    const restored = parseDraft(JSON.stringify(partial));
    expect(restored?.["identity.brand_name"]).toBe("Old Draft");
    expect(restored?.["market.competitors"]).toBe(""); // absent key defaults empty
  });

  it("ignores non-string values inside state (defensive, never crashes)", () => {
    const foreign = { version: 1, savedAt: "x", state: { "identity.brand_name": 12345 } };
    const restored = parseDraft(JSON.stringify(foreign));
    expect(restored?.["identity.brand_name"]).toBe("");
  });

  it("the storage key is a stable, namespaced constant", () => {
    expect(INTAKE_DRAFT_STORAGE_KEY).toBe("cexai_intake_draft_v1");
  });
});

describe("POST /api/intake -- the HARD DEV GATE (prod-refusal at the route level)", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("returns 403 in a production env even with the opt-in set (NODE_ENV gate)", async () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("CEXAI_ONBOARD_ENABLED", "1");
    const res = await intakePost(
      new Request("http://localhost/api/intake", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ answers: { form_version: 1 } }),
      }),
    );
    expect(res.status).toBe(403);
    const body = (await res.json()) as { ok: boolean; errors?: string[] };
    expect(body.ok).toBe(false);
    expect(body.errors?.[0]).toMatch(/DEV-ONLY/);
  });

  it("returns 403 in this test env too (no opt-in, NODE_ENV != development)", async () => {
    const res = await intakePost(
      new Request("http://localhost/api/intake", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ answers: { form_version: 1 } }),
      }),
    );
    expect(res.status).toBe(403);
  });
});
