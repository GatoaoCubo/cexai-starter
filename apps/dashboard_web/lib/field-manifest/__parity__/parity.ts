// =============================================================================
// PARITY / REGRESSION GATE -- buildSchema(productManifest) behavior PINNED to GOLD
// =============================================================================
//
// The HARD gate for the field-manifest mold. It asserts that the manifest-derived
// schema + publish-gate produce EXACTLY the expected pass/fail outcome AND the
// EXACT error field-path set across a battery of representative inputs + boundary
// probes. The EXPECTED values are hard-coded GOLD (the pinned behavior from the
// reference implementation). If a future change to the manifest, buildSchema, or the
// atoms alters publish gating or base validation, THIS gate fails (exit 1).
//
// ADAPTATION vs the reference (lib/field-manifest/__parity__/parity.ts):
// the reference battery imported the LIVE hand-written productSchema /
// PUBLISH_REQUIREMENTS from @/lib/validations/product and cross-checked them vs
// buildSchema(productManifest). The CENTRAL dashboard has NO hand-written product
// schema -- the manifest + buildSchema IS the single source of truth -- so this
// battery is SELF-CONTAINED: every assertion runs against buildSchema(productManifest)
// directly. The reference HYBRID-OVERRIDE atom cases (margem/custo/quantity integer /
// preco_b2c non-coerce / media_kit_url) are intentionally OMITTED here: they pinned
// the reference hand-written override layer, which does NOT exist centrally yet (spec
// FR-015 hybrid-override is a per-tenant ProductForm-wiring follow-up). Every GOLD
// assertion the generic buildSchema CAN satisfy is kept -- this is an honest
// adaptation, not a weakening.
//
// Run via the esbuild runner (no new test-runner dep):
//   node lib/field-manifest/__parity__/run.mjs
// Exit 0 = PASS, exit 1 = FAIL.

import {
  buildSchema,
  getMissingPublishRequirements,
  type PublishRequirement,
} from "@/lib/field-manifest/buildSchema";
import { productManifest } from "@/lib/field-manifest/productManifest";

type AnyData = Record<string, unknown>;

// ---------------------------------------------------------------------------
// Build the schema ONCE from the manifest -- the single source under test.
// ---------------------------------------------------------------------------
const built = buildSchema(productManifest);
const SCHEMA = built.schema;
const UPDATE_SCHEMA = built.updateSchema;
const PUBLISH_REQUIREMENTS = built.publishRequirements;

// ---------------------------------------------------------------------------
// Test harness
// ---------------------------------------------------------------------------
let failures = 0;
const log = (s: string) => process.stdout.write(s + "\n");

function check(name: string, cond: boolean, detail = ""): void {
  if (cond) {
    log(`  [PASS] ${name}`);
  } else {
    failures += 1;
    log(`  [FAIL] ${name}${detail ? "  -- " + detail : ""}`);
  }
}

// Run schema.safeParse and return "<<OK>>" on success, else the sorted,
// de-duplicated set of top-level error field names (what drives the form's
// section highlight). This is the canonical behavior signature each GOLD case asserts.
function outcome(
  schema: {
    safeParse: (d: unknown) => {
      success: boolean;
      error?: { issues: Array<{ path: (string | number)[] }> };
    };
  },
  data: AnyData,
): string {
  const res = schema.safeParse(data);
  if (res.success) return "<<OK>>";
  const fields = (res.error?.issues ?? []).map((i) => String(i.path[0] ?? "<root>")).sort();
  return [...new Set(fields)].join(",") || "<<INVALID>>";
}

// ---------------------------------------------------------------------------
// A valid, fully-publishable base product. Variants mutate this.
// ---------------------------------------------------------------------------
const VALID: AnyData = {
  slug: "produto-exemplo",
  name: "Produto Exemplo",
  price: 149.9,
  description: "Cama redonda super macia para gatos dormirem com seguranca e conforto.",
  images: ["https://cdn.example.com/img1.jpg"],
  seo_title: "Cama Donut para Gatos",
  seo_description:
    "Cama donut premium para gatos: macia, antiderrapante e lavavel. Conforto e seguranca para o seu felino.",
  status: "published",
  _wasPublished: false,
  quantity: 5,
  benefits_functional: ["Suporta ate 8kg", "Impermeavel", "Lavavel a maquina"],
  usage_guide: ["Desembale o produto", "Posicione em local calmo", "Deixe o gato explorar"],
  faq: [
    { question: "Pode lavar na maquina?", answer: "Sim, em ciclo delicado a frio." },
    { question: "Qual o tamanho ideal?", answer: "Medimos 50cm de diametro, serve a maioria." },
    { question: "Tem garantia?", answer: "Sim, 30 dias contra defeitos de fabricacao." },
  ],
  long_description:
    "A Cama Donut foi desenhada a partir da etologia felina: as bordas elevadas dao sensacao de protecao e o enchimento macio acolhe o gato como um ninho. Material impermeavel por baixo e lavavel por cima.",
  dim_length_cm: 50,
  dim_width_cm: 50,
  dim_height_cm: 20,
  weight_grams: 900,
};

function variant(patch: AnyData): AnyData {
  return { ...JSON.parse(JSON.stringify(VALID)), ...patch };
}

// ---------------------------------------------------------------------------
// (A) GOLD: full-schema validation outcomes -- the derived schema must produce
//     EXACTLY these field-paths (or <<OK>>) for each representative input.
// ---------------------------------------------------------------------------
log("\n== (A) derived schema outcomes pinned to GOLD ==");

const GOLD_CASES: Array<{ label: string; data: AnyData; expect: string }> = [
  { label: "valid published product", data: VALID, expect: "<<OK>>" },
  { label: "valid draft (gate off)", data: variant({ status: "draft" }), expect: "<<OK>>" },
  { label: "valid archived (gate off)", data: variant({ status: "archived" }), expect: "<<OK>>" },
  {
    label: "re-save of already-published, underfilled (gate off via _wasPublished)",
    data: variant({
      _wasPublished: true,
      benefits_functional: [],
      usage_guide: [],
      faq: [],
      long_description: "",
      dim_length_cm: undefined,
      dim_width_cm: undefined,
      dim_height_cm: undefined,
      weight_grams: undefined,
    }),
    expect: "<<OK>>",
  },
  // Publish-gate single-field misses -> error mapped to that field path.
  {
    label: "publish missing benefits",
    data: variant({ benefits_functional: ["only one"] }),
    expect: "benefits_functional",
  },
  { label: "publish missing usage_guide", data: variant({ usage_guide: [] }), expect: "usage_guide" },
  { label: "publish missing faq", data: variant({ faq: [] }), expect: "faq" },
  {
    label: "publish short long_description",
    data: variant({ long_description: "too short" }),
    expect: "long_description",
  },
  {
    label: "publish missing dims (width null)",
    data: variant({ dim_width_cm: undefined }),
    expect: "dim_length_cm",
  },
  { label: "publish zero height", data: variant({ dim_height_cm: 0 }), expect: "dim_length_cm" },
  { label: "publish missing weight_grams", data: variant({ weight_grams: undefined }), expect: "weight_grams" },
  {
    label: "publish missing EVERYTHING gated",
    data: variant({
      benefits_functional: [],
      usage_guide: [],
      faq: [],
      long_description: "",
      dim_length_cm: undefined,
      dim_width_cm: undefined,
      dim_height_cm: undefined,
      weight_grams: undefined,
    }),
    // all six gate fields, sorted (the gate maps the dims error to dim_length_cm).
    expect: "benefits_functional,dim_length_cm,faq,long_description,usage_guide,weight_grams",
  },
  // Base-field (non-gate) validation -- must fail identically regardless of status.
  { label: "draft with too-short name", data: variant({ status: "draft", name: "ab" }), expect: "name" },
  {
    label: "draft with bad slug (spaces)",
    data: variant({ status: "draft", slug: "Bad Slug Here" }),
    expect: "slug",
  },
  { label: "draft with no images", data: variant({ status: "draft", images: [] }), expect: "images" },
  {
    label: "draft with short seo_title",
    data: variant({ status: "draft", seo_title: "short" }),
    expect: "seo_title",
  },
  { label: "draft with negative price", data: variant({ status: "draft", price: -5 }), expect: "price" },
  {
    label: "published AND base-invalid (mix of gate + base errors)",
    data: variant({ name: "ab", benefits_functional: [] }),
    expect: "benefits_functional,name",
  },
];

for (const c of GOLD_CASES) {
  const got = outcome(SCHEMA, c.data);
  check(`${c.label}  =>  ${c.expect}`, got === c.expect, `expected=[${c.expect}] got=[${got}]`);
}

// ---------------------------------------------------------------------------
// (B) GOLD: publish-requirement field SET + per-field isSatisfied at thresholds.
// ---------------------------------------------------------------------------
log("\n== (B) publishRequirements field set + threshold behavior pinned to GOLD ==");

const GOLD_PUBLISH_FIELDS = [
  "benefits_functional",
  "dim_length_cm",
  "faq",
  "long_description",
  "usage_guide",
  "weight_grams",
].sort();

const liveFields = (PUBLISH_REQUIREMENTS as PublishRequirement[]).map((r) => String(r.field)).sort();

check(
  "publish requirement field SET matches GOLD",
  JSON.stringify(liveFields) === JSON.stringify(GOLD_PUBLISH_FIELDS),
  `gold=[${GOLD_PUBLISH_FIELDS}] live=[${liveFields}]`,
);

// getMissingPublishRequirements on a fully-valid product -> none missing.
check(
  "getMissingPublishRequirements(VALID) is empty",
  getMissingPublishRequirements(PUBLISH_REQUIREMENTS, VALID).length === 0,
);

// Boundary behavior per gated field (count/length/positive) pinned to GOLD.
const reqByField = (f: string) =>
  (PUBLISH_REQUIREMENTS as PublishRequirement[]).find((r) => String(r.field) === f)!;

const BOUNDARY: Array<{ field: string; data: AnyData; sat: boolean; label: string }> = [
  { field: "benefits_functional", data: variant({ benefits_functional: ["a", "b"] }), sat: false, label: "benefits=2 below 3" },
  { field: "benefits_functional", data: variant({ benefits_functional: ["a", "b", "c"] }), sat: true, label: "benefits=3 at 3" },
  { field: "usage_guide", data: variant({ usage_guide: ["a", "b"] }), sat: false, label: "usage=2 below 3" },
  { field: "usage_guide", data: variant({ usage_guide: ["a", "b", "c"] }), sat: true, label: "usage=3 at 3" },
  {
    field: "faq",
    data: variant({
      faq: [
        { question: "qqqqq", answer: "aaaaaaaaaa" },
        { question: "wwwww", answer: "bbbbbbbbbb" },
        { question: "eeeee", answer: "" },
      ],
    }),
    sat: false,
    label: "faq=3 but one missing answer counts 2",
  },
  { field: "long_description", data: variant({ long_description: "x".repeat(119) }), sat: false, label: "long_desc 119 below 120" },
  { field: "long_description", data: variant({ long_description: "x".repeat(120) }), sat: true, label: "long_desc 120 at 120" },
  { field: "dim_length_cm", data: variant({ dim_width_cm: 0 }), sat: false, label: "dims width 0 not all positive" },
  { field: "dim_length_cm", data: VALID, sat: true, label: "dims all positive" },
  { field: "weight_grams", data: variant({ weight_grams: 0 }), sat: false, label: "weight 0 not positive" },
  { field: "weight_grams", data: VALID, sat: true, label: "weight 900 positive" },
];

for (const b of BOUNDARY) {
  const got = reqByField(b.field).isSatisfied(b.data);
  check(`isSatisfied("${b.field}") @ [${b.label}] === ${b.sat}`, got === b.sat, `expected=${b.sat} got=${got}`);
}

// ---------------------------------------------------------------------------
// (C) Base/refined split integrity (the superRefine landmine)
// ---------------------------------------------------------------------------
log("\n== (C) Base/refined split integrity ==");
// baseSchema must be a ZodObject (so .partial()/.extend() work).
check(
  "baseSchema is a ZodObject (supports .partial()/.extend())",
  typeof (built.baseSchema as { partial?: unknown }).partial === "function" &&
    typeof (built.baseSchema as { extend?: unknown }).extend === "function",
);
check(
  "updateSchema parses a partial (status-only) update",
  UPDATE_SCHEMA.safeParse({ status: "draft" }).success,
);
check(
  "updateSchema does NOT apply the publish gate (partial published, underfilled => OK)",
  UPDATE_SCHEMA.safeParse({ status: "published" }).success,
);

// ---------------------------------------------------------------------------
// (D) Exhaustiveness + field-set self-agreement
//     (the central analogue of the reference core<->product.ts cross-check).
// ---------------------------------------------------------------------------
log("\n== (D) field-set agreement + exhaustiveness guard ==");
// The generated publish field set equals the GOLD set (re-derived from the manifest).
const genFields = built.publishRequirements.map((r) => r.field).sort();
check(
  "generated publish field set === GOLD field set",
  JSON.stringify(genFields) === JSON.stringify(GOLD_PUBLISH_FIELDS),
  `generated=[${genFields}] gold=[${GOLD_PUBLISH_FIELDS}]`,
);
// The all-gated-missing case maps the dims error to dim_length_cm (companions).
const allMissing = variant({
  benefits_functional: [],
  usage_guide: [],
  faq: [],
  long_description: "",
  dim_length_cm: undefined,
  dim_width_cm: undefined,
  dim_height_cm: undefined,
  weight_grams: undefined,
});
check(
  "all-gated-missing error set === GOLD all-missing set",
  outcome(SCHEMA, allMissing) ===
    "benefits_functional,dim_length_cm,faq,long_description,usage_guide,weight_grams",
  `got=[${outcome(SCHEMA, allMissing)}]`,
);
// The exhaustiveness guard THROWS on an unmapped FieldKind (no silent drop).
let threw = false;
try {
  buildSchema({
    sections: [{ id: "s", title: "S" }],
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    fields: [{ name: "x", label: "X", kind: "not_a_real_kind" as any, section: "s" }],
  });
} catch (e) {
  threw = /unmapped FieldKind/.test(String((e as Error).message));
}
check("buildSchema throws on an unmapped FieldKind (exhaustiveness guard)", threw);

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------
log("\n=============================================");
if (failures === 0) {
  log("REGRESSION RESULT: PASS  (manifest-derived schema/gate matches GOLD)");
  log("=============================================");
  process.exit(0);
} else {
  log(`REGRESSION RESULT: FAIL  (${failures} mismatch${failures === 1 ? "" : "es"})`);
  log("=============================================");
  process.exit(1);
}
