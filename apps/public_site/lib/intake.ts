// ----------------------------------------------------------------------------
// intake -- the PURE, testable core of the /intake form (R-283: web UI for the
// R-149 form_v1 intake contract). The page (app/intake/page.tsx) renders the
// fields; the DEV-ONLY route (app/api/intake/route.ts) owns spawn orchestration.
// Everything that can be reasoned about without a DOM or a process lives HERE:
//
//   * validateIntake(state) -- client-side MIRROR of the Python gate
//     _tools/brand_validate.py::validate (:76-143). ERROR tier = the validator's
//     errors (E1 14 required, E2 values>=3, E3 archetype enum-12, E4 formality
//     int 1-5, E5 3x HEX ^#[0-9a-fA-F]{6}$, E6 pricing enum-6) PLUS the
//     resolver-side drops a user should fix before losing data (slug pattern,
//     https-only links, R-276 env-ref-only credentials). WARNING tier = the
//     validator's warnings (W1 values>7, W2 language xx-XX, W3 transformation
//     'From X to Y through Z' start-anchored, W4 UVP<20) -- NEVER blocking,
//     exactly like the CLI. No invented rules: template guidance (tagline
//     10-100, icp 20+) stays a static hint in the page, never validated here.
//   * buildAnswers(state) -- form state -> the form_v1 answers OBJECT, shaped
//     exactly like examples/10_intake_form_v1/form_answers_borealis_cafe.yaml
//     (sections + keys = _tools/cex_ingest_registry.py KNOWN_SECTIONS +
//     FORM_FIELD_MAP). Empty optional keys are OMITTED (the resolver skips
//     empties; omitting keeps the file clean). archetype is lowercased and
//     currency uppercased here (the same coercions the resolver applies).
//   * answersToYamlText(answers) -- '#' header lines + JSON.stringify(...,2).
//     JSON is a YAML subset, so PyYAML safe_load parses the emitted file with
//     ZERO new npm deps and zero quoting bugs. This IS the answers YAML the
//     CLI resolver consumes.
//   * parseResolveOutput(stdout, code) -- parse the resolver CLI's stable
//     ASCII output ('[OK] resolved form_v1: ...', '  [WARN] ...', '[FAIL] ...').
//     The CLI has no --json flag today, so the route reads exit code + text.
//
// PURE + TOTAL: nothing here throws, touches the filesystem, or the network.
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { isValidSlug } from "@/lib/slug";

// ---------------------------------------------------------------------------
// Enums + patterns -- byte-mirrors of _tools/brand_validate.py (:26-37) and
// _tools/cex_ingest_registry.py (:74-76, :117-119).
// ---------------------------------------------------------------------------

/** VALID_ARCHETYPES (brand_validate.py:26-29) in the canonical note order. */
export const ARCHETYPES = [
  "creator",
  "hero",
  "sage",
  "explorer",
  "rebel",
  "magician",
  "lover",
  "caregiver",
  "jester",
  "ruler",
  "innocent",
  "everyman",
] as const;

/** VALID_PRICING_MODELS (brand_validate.py:31-33). The validator checks EXACT
 *  membership (no .lower()), so the form only ever emits these literal values. */
export const PRICING_MODELS = [
  "subscription",
  "one-time",
  "credits",
  "freemium",
  "marketplace",
  "hybrid",
] as const;

/** shape_confirm enums (cex_ingest_registry.py:118-119). */
export const VERTICALS = ["retail", "services"] as const;
export const B2B_MODES = ["wholesale", "corporate"] as const;

/** The 9 canonical link keys (cex_brand_extract.LINK_KEYS:125-128, order kept). */
export const LINK_KEYS = [
  "website",
  "store",
  "instagram",
  "linkedin",
  "facebook",
  "youtube",
  "whatsapp",
  "x",
  "tiktok",
] as const;

/** v2 (2026-07-07): visual.design_style soft-enum (curated hint, never a
 *  brand_validate gate -- an out-of-list value only WARNS, see validateIntake). */
export const DESIGN_STYLES = [
  "minimalista",
  "moderno",
  "classico",
  "vintage",
  "divertido",
  "luxuoso",
  "organico",
  "industrial",
] as const;

/** v2 (2026-07-07): visual.logo_status enum-2, per the proposal's own wording
 *  ("Ja possui logotipo? renovar/primeiro"). Soft-warn only, never blocking. */
export const LOGO_STATUSES = [
  { value: "primeiro", label: "e o primeiro logotipo da marca" },
  { value: "renovar", label: "ja tenho, quero renovar" },
] as const;

/** HEX_PATTERN (brand_validate.py:35). */
export const HEX_PATTERN = /^#[0-9a-fA-F]{6}$/;
/** LANG_PATTERN (brand_validate.py:36). */
export const LANG_PATTERN = /^[a-z]{2}-[A-Z]{2}$/;
/** TRANSFORM_PATTERN (brand_validate.py:37) -- Python uses re.match, which
 *  anchors at the START only; the ^ (and no $) mirrors that exactly. */
export const TRANSFORM_PATTERN = /^From .+ to .+ through .+/i;
/** ENV_REF_PATTERN (cex_ingest_registry.py:76) -- R-276 refs-not-literals. */
export const ENV_REF_PATTERN = /^[A-Z][A-Z0-9_]{2,63}$/;
/** v2 (2026-07-07): a permissive email SHAPE check for contact.email -- soft-
 *  warn only (this field has no gate anywhere; it is not a credential). */
export const EMAIL_LOOSE_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ---------------------------------------------------------------------------
// Form state -- ONE flat string per field (selects included). Lists are typed
// as free text split on newlines/commas; shape booleans are "sim"/"nao"/"".
// ---------------------------------------------------------------------------

export type IntakeKey =
  | "tenant.slug"
  | "identity.brand_name"
  | "identity.brand_tagline"
  | "identity.brand_mission"
  | "identity.brand_values"
  | "identity.brand_story"
  | "archetype.brand_archetype"
  | "archetype.brand_personality"
  | "voice.tone"
  | "voice.formality"
  | "voice.language"
  | "voice.do"
  | "voice.dont"
  | "audience.icp"
  | "audience.transformation"
  | "visual.colors.primary"
  | "visual.colors.secondary"
  | "visual.colors.accent"
  | "visual.logo"
  | "visual.fonts.heading"
  | "visual.fonts.body"
  | "positioning.category"
  | "positioning.uvp"
  | "positioning.content_pillars"
  | "monetization.pricing_model"
  | "monetization.currency"
  | "monetization.tiers"
  | "location.channels"
  | "shape_confirm.vertical"
  | "shape_confirm.has_store"
  | "shape_confirm.has_blog"
  | "shape_confirm.has_b2b"
  | "shape_confirm.b2b_mode"
  | "links.website"
  | "links.store"
  | "links.instagram"
  | "links.linkedin"
  | "links.facebook"
  | "links.youtube"
  | "links.whatsapp"
  | "links.x"
  | "links.tiktok"
  | "sources.site_url"
  | "sources.snapshot"
  | "sources.brandbook"
  | "catalog.source_ref"
  | "credentials.crm_ref"
  // ---- v2 field extension (2026-07-07 GDP) -- ALL optional/soft-warn ------
  | "contact.name"
  | "contact.email"
  | "identity.legal_name"
  | "identity.vision"
  | "audience.wtp_band"
  | "audience.demographics"
  | "visual.colors_description"
  | "visual.colors_avoid"
  | "visual.style_avoid"
  | "visual.design_style"
  | "visual.logo_status"
  | "visual.references"
  | "positioning.offerings"
  | "location.city_state"
  | "market.competitors"
  | "market.edge_notes"
  | "market.trends"
  | "applications.surfaces";

export type IntakeState = Record<IntakeKey, string>;

const ALL_KEYS: IntakeKey[] = [
  "tenant.slug",
  "identity.brand_name",
  "identity.brand_tagline",
  "identity.brand_mission",
  "identity.brand_values",
  "identity.brand_story",
  "archetype.brand_archetype",
  "archetype.brand_personality",
  "voice.tone",
  "voice.formality",
  "voice.language",
  "voice.do",
  "voice.dont",
  "audience.icp",
  "audience.transformation",
  "visual.colors.primary",
  "visual.colors.secondary",
  "visual.colors.accent",
  "visual.logo",
  "visual.fonts.heading",
  "visual.fonts.body",
  "positioning.category",
  "positioning.uvp",
  "positioning.content_pillars",
  "monetization.pricing_model",
  "monetization.currency",
  "monetization.tiers",
  "location.channels",
  "shape_confirm.vertical",
  "shape_confirm.has_store",
  "shape_confirm.has_blog",
  "shape_confirm.has_b2b",
  "shape_confirm.b2b_mode",
  "links.website",
  "links.store",
  "links.instagram",
  "links.linkedin",
  "links.facebook",
  "links.youtube",
  "links.whatsapp",
  "links.x",
  "links.tiktok",
  "sources.site_url",
  "sources.snapshot",
  "sources.brandbook",
  "catalog.source_ref",
  "credentials.crm_ref",
  "contact.name",
  "contact.email",
  "identity.legal_name",
  "identity.vision",
  "audience.wtp_band",
  "audience.demographics",
  "visual.colors_description",
  "visual.colors_avoid",
  "visual.style_avoid",
  "visual.design_style",
  "visual.logo_status",
  "visual.references",
  "positioning.offerings",
  "location.city_state",
  "market.competitors",
  "market.edge_notes",
  "market.trends",
  "applications.surfaces",
];

/** A fresh, all-empty form state. */
export function emptyIntakeState(): IntakeState {
  const out = {} as IntakeState;
  for (const k of ALL_KEYS) out[k] = "";
  return out;
}

/** The template's `*` (required) tier == brand_validate's 14 required fields.
 *  16 form fields because BRAND_COLORS is ONE validator field with 3 subkeys. */
export const REQUIRED_KEYS: IntakeKey[] = [
  "identity.brand_name",
  "identity.brand_tagline",
  "identity.brand_mission",
  "identity.brand_values",
  "archetype.brand_archetype",
  "voice.tone",
  "voice.formality",
  "audience.icp",
  "audience.transformation",
  "visual.colors.primary",
  "visual.colors.secondary",
  "visual.colors.accent",
  "positioning.category",
  "positioning.uvp",
  "monetization.pricing_model",
  "monetization.currency",
];

const COLOR_KEYS: IntakeKey[] = [
  "visual.colors.primary",
  "visual.colors.secondary",
  "visual.colors.accent",
];

const LINK_STATE_KEYS: IntakeKey[] = LINK_KEYS.map(
  (k) => ("links." + k) as IntakeKey,
);

// ---------------------------------------------------------------------------
// Validation -- the client-side mirror of the Python gate. No drift: every
// rule cites its brand_validate.py / cex_ingest_registry.py line.
// ---------------------------------------------------------------------------

export interface IntakeValidation {
  /** Blocking (submit disabled). Mirrors validator ERRORS + resolver DROPS. */
  errors: Partial<Record<IntakeKey, string>>;
  /** Non-blocking, shown inline. Mirrors validator WARNINGS exactly. */
  warnings: Partial<Record<IntakeKey, string>>;
}

/** Split a free-text list field on newlines/commas (the resolver's str_list
 *  coercion splits comma-strings; the form emits real arrays, so this is a
 *  typing affordance, not a contract change). TOTAL. */
export function splitList(value: unknown): string[] {
  if (typeof value !== "string") return [];
  return value
    .split(/[\n,]/)
    .map((t) => t.trim())
    .filter(Boolean);
}

/** Mirror of `new URL` under cex_brand_extract.is_safe_link (:588-599): an
 *  absolute https: URL with a host; protocol-relative (//) and http: rejected. */
export function isHttpsUrl(raw: unknown): boolean {
  if (typeof raw !== "string") return false;
  const s = raw.trim();
  if (!s || s.startsWith("//")) return false;
  try {
    const u = new URL(s);
    return u.protocol === "https:" && !!u.host;
  } catch {
    return false;
  }
}

/** Integer 1-5 (brand_validate.py:97-102 via the resolver's int() coercion at
 *  cex_ingest_registry.py:188-193: "3" -> 3 passes; "2.5"/"abc" never reach a
 *  passing state). TOTAL. */
function isFormalityValid(raw: string): boolean {
  const s = raw.trim();
  if (!/^-?[0-9]+$/.test(s)) return false;
  const n = Number(s);
  return n >= 1 && n <= 5;
}

// ---------------------------------------------------------------------------
// DP3 (v2, 2026-07-07): colors-from-description. Mirrors
// _tools/cex_ingest_registry.py::_derive_colors_from_description LITERAL-BY-
// LITERAL (same PT-BR color-word -> HEX table, same longest-phrase-first
// masking so a compound name's generic root never ALSO matches, same "need 3
// distinct matches or null" rule). Runs client-side so the required-color
// check below can know WHETHER a description satisfies the alt input path
// WITHOUT round-tripping through the python resolver. PURE + TOTAL.
// ---------------------------------------------------------------------------

/** Mirrors cex_ingest_registry.py::_COLOR_WORD_HEX exactly. */
export const COLOR_WORD_HEX: readonly (readonly [string, string])[] = [
  ["verde musgo", "#4A5D23"],
  ["verde escuro", "#1B4332"],
  ["verde agua", "#2FA6A0"],
  ["azul marinho", "#1B3A57"],
  ["azul claro", "#7EC8E3"],
  ["terracota", "#B5651D"],
  ["vermelho", "#B23A2F"],
  ["dourado", "#C9A227"],
  ["marrom", "#6F4E37"],
  ["bege", "#D8C9A3"],
  ["creme", "#F0E6D2"],
  ["preto", "#1A1A1A"],
  ["branco", "#FAFAFA"],
  ["cinza", "#6B7280"],
  ["rosa", "#D97A9B"],
  ["roxo", "#6B3FA0"],
  ["laranja", "#D9752B"],
  ["amarelo", "#E8B923"],
  ["vinho", "#6E1F2A"],
  ["turquesa", "#2FA6A0"],
  ["azul", "#1E5AA8"],
  ["verde", "#2E7D32"],
];

export interface DerivedColors {
  primary: string;
  secondary: string;
  accent: string;
}

/** Mirrors cex_ingest_registry.py::_derive_colors_from_description exactly
 *  (same masking algorithm). Returns null when fewer than 3 distinct color
 *  words are recognized -- degrade-never, no invented palette. */
export function deriveColorsFromDescription(text: string): DerivedColors | null {
  if (!text || !text.trim()) return null;
  let working = " " + text.trim().toLowerCase().replace(/\s+/g, " ") + " ";
  const matches: Array<{ idx: number; hex: string }> = [];
  const seenHex = new Set<string>();
  const byLengthDesc = [...COLOR_WORD_HEX].sort((a, b) => b[0].length - a[0].length);
  for (const [word, hex] of byLengthDesc) {
    const idx = working.indexOf(word);
    if (idx === -1) continue;
    if (!seenHex.has(hex)) {
      matches.push({ idx, hex });
      seenHex.add(hex);
    }
    // mask regardless (seen or not) so a shorter substring of an
    // already-matched phrase can never independently match later.
    working = working.slice(0, idx) + " ".repeat(word.length) + working.slice(idx + word.length);
  }
  if (matches.length < 3) return null;
  matches.sort((a, b) => a.idx - b.idx);
  const [primary, secondary, accent] = matches.slice(0, 3).map((m) => m.hex);
  return { primary, secondary, accent };
}

const MSG_REQUIRED = "obrigatorio (campo requerido pelo gate brand_validate)";

/** Validate the form state. PURE + TOTAL. */
export function validateIntake(state: IntakeState): IntakeValidation {
  const errors: Partial<Record<IntakeKey, string>> = {};
  const warnings: Partial<Record<IntakeKey, string>> = {};
  const v = (k: IntakeKey): string => (state[k] ?? "").trim();

  // E1 -- the 14 required fields (brand_validate.py:76-143 validate_section).
  // DP3 (v2): visual.colors_description can satisfy the 3 color slots via the
  // SAME derivation the python resolver runs (cex_ingest_registry.py step
  // "1b") -- an input path, never a gate relaxation: an UNDERIVABLE
  // description still leaves the 3 fields required, exactly like the server
  // (an unresolvable description leaves BRAND_COLORS unset there too).
  const derivedColors = deriveColorsFromDescription(v("visual.colors_description"));
  for (const k of REQUIRED_KEYS) {
    if (COLOR_KEYS.includes(k) && derivedColors) continue; // alt path satisfies it
    if (!v(k)) errors[k] = MSG_REQUIRED;
  }

  // E2 / W1 -- BRAND_VALUES >=3 items error, >7 warning (:80-85).
  const values = splitList(state["identity.brand_values"]);
  if (values.length > 0 && values.length < 3) {
    errors["identity.brand_values"] =
      "BRAND_VALUES precisa de 3+ itens (tem " + values.length + ")";
  } else if (values.length > 7) {
    warnings["identity.brand_values"] =
      values.length + " itens (recomendado 3-7)";
  }

  // E3 -- archetype enum-12, case-insensitive like arch.lower() (:88-92).
  const arch = v("archetype.brand_archetype");
  if (arch && !(ARCHETYPES as readonly string[]).includes(arch.toLowerCase())) {
    errors["archetype.brand_archetype"] =
      "arquetipo invalido -- um de: " + ARCHETYPES.join(", ");
  }

  // E4 -- formality integer 1-5 (:97-102).
  const formality = v("voice.formality");
  if (formality && !isFormalityValid(formality)) {
    errors["voice.formality"] = "deve ser um inteiro de 1 a 5";
  }

  // E5 -- each color ^#[0-9a-fA-F]{6}$ (:121-129).
  for (const k of COLOR_KEYS) {
    const c = v(k);
    if (c && !HEX_PATTERN.test(c)) {
      errors[k] = "HEX invalido -- use #RRGGBB (ex.: #3B2A20)";
    }
  }

  // E6 -- pricing model enum-6, EXACT match like the validator (:139-143).
  const pricing = v("monetization.pricing_model");
  if (pricing && !(PRICING_MODELS as readonly string[]).includes(pricing)) {
    errors["monetization.pricing_model"] =
      "modelo invalido -- um de: " + PRICING_MODELS.join(", ");
  }

  // W2 -- language xx-XX warning (:103-105).
  const lang = v("voice.language");
  if (lang && !LANG_PATTERN.test(lang)) {
    warnings["voice.language"] = "nao segue o padrao xx-XX (ex.: pt-BR)";
  }

  // W3 -- transformation 'From X to Y through Z' warning (:116-118).
  const transformation = v("audience.transformation");
  if (transformation && !TRANSFORM_PATTERN.test(transformation)) {
    warnings["audience.transformation"] =
      "nao segue o padrao 'From X to Y through Z'";
  }

  // W4 -- UVP < 20 chars warning (:134-136).
  const uvp = v("positioning.uvp");
  if (uvp && uvp.length < 20) {
    warnings["positioning.uvp"] =
      "curta (" + uvp.length + " chars; recomendado 20+)";
  }

  // --- resolver-side DROPS, pre-validated so the user never loses data ------
  // (cex_ingest_registry.py: slug :409-417, links :371-385, creds :433-444).
  // These block ONLY a non-empty malformed value -- clearing the field is
  // always a valid way to proceed (all three are optional in the contract).
  const slug = v("tenant.slug");
  if (slug && !isValidSlug(slug)) {
    errors["tenant.slug"] =
      "slug invalido -- padrao ^[a-z0-9][a-z0-9_-]{0,63}$ (o resolver ignora um slug fora do padrao)";
  }
  for (const k of LINK_STATE_KEYS) {
    const link = v(k);
    if (link && !isHttpsUrl(link)) {
      errors[k] =
        "apenas URL https:// absoluta (o sanitizador do resolver descarta http:/relativos)";
    }
  }
  const crmRef = v("credentials.crm_ref");
  if (crmRef && !ENV_REF_PATTERN.test(crmRef)) {
    errors["credentials.crm_ref"] =
      "apenas o NOME de uma env-var (^[A-Z][A-Z0-9_]{2,63}$, ex.: BOREALIS_CRM_KEY) -- " +
      "nunca um segredo literal (R-276); o resolver descarta e nunca emite outros valores";
  }

  // --- v2 (2026-07-07): the 17 new fields are ALL optional/soft-warn -- NONE
  // of the checks below ever populate `errors`, only `warnings` (manifest hard
  // constraint: "TODOS os 15 novos = OPCIONAIS/soft-warn"). Every check is
  // guarded on a non-empty value first, so an empty field never warns either.
  const wtpBand = v("audience.wtp_band");
  if (wtpBand) {
    const nums = wtpBand.match(/\d+(?:\.\d+)?/g) || [];
    if (nums.length < 2) {
      warnings["audience.wtp_band"] =
        "formato recomendado: R$ MIN-MAX (ex.: R$ 29-149) -- sem 2 numeros, o " +
        "pricing fastpath usa uma faixa padrao";
    }
  }
  const contactEmail = v("contact.email");
  if (contactEmail && !EMAIL_LOOSE_PATTERN.test(contactEmail)) {
    warnings["contact.email"] = "parece invalido -- confira o formato do e-mail";
  }
  const designStyle = v("visual.design_style");
  if (designStyle && !(DESIGN_STYLES as readonly string[]).includes(designStyle.toLowerCase())) {
    warnings["visual.design_style"] =
      "fora da lista sugerida -- nao bloqueia, e so uma dica para o preset de tema";
  }
  const logoStatus = v("visual.logo_status");
  if (logoStatus && !LOGO_STATUSES.some((o) => o.value === logoStatus.toLowerCase())) {
    warnings["visual.logo_status"] = "use 'primeiro' ou 'renovar' -- nao bloqueia";
  }
  const colorsDescription = v("visual.colors_description");
  if (colorsDescription && !derivedColors && !COLOR_KEYS.some((k) => v(k))) {
    warnings["visual.colors_description"] =
      "nao foi possivel reconhecer 3 cores distintas no texto -- preencha as 3 cores " +
      "HEX acima OU descreva com mais palavras de cor (ex.: verde musgo, marrom, dourado)";
  }

  return { errors, warnings };
}

// ---------------------------------------------------------------------------
// Emission -- form state -> the form_v1 answers object -> the answers YAML.
// ---------------------------------------------------------------------------

/** The form_v1 answers file shape (sections/keys = cex_ingest_registry.py
 *  KNOWN_SECTIONS :111-115 + FORM_FIELD_MAP :83-108; example:
 *  examples/10_intake_form_v1/form_answers_borealis_cafe.yaml). */
export interface IntakeAnswers {
  form_version: 1;
  tenant?: { slug: string };
  contact?: { name?: string; email?: string };
  identity?: {
    brand_name?: string;
    brand_tagline?: string;
    brand_mission?: string;
    brand_values?: string[];
    brand_story?: string;
    legal_name?: string;
    vision?: string;
  };
  archetype?: { brand_archetype?: string; brand_personality?: string[] };
  voice?: {
    tone?: string;
    formality?: number | string;
    language?: string;
    do?: string[];
    dont?: string[];
  };
  audience?: {
    icp?: string;
    transformation?: string;
    wtp_band?: string;
    demographics?: string;
  };
  visual?: {
    colors?: { primary?: string; secondary?: string; accent?: string };
    colors_description?: string;
    logo?: string;
    fonts?: { heading?: string; body?: string };
    colors_avoid?: string[];
    style_avoid?: string[];
    design_style?: string;
    logo_status?: string;
    references?: string[];
  };
  positioning?: {
    category?: string;
    uvp?: string;
    content_pillars?: string[];
    offerings?: string;
  };
  monetization?: {
    pricing_model?: string;
    currency?: string;
    tiers?: string[];
  };
  location?: { channels?: string[]; city_state?: string };
  market?: { competitors?: string[]; edge_notes?: string; trends?: string };
  applications?: { surfaces?: string[] };
  shape_confirm?: {
    vertical?: string;
    has_store?: boolean;
    has_blog?: boolean;
    has_b2b?: boolean;
    b2b_mode?: string;
  };
  links?: Partial<Record<(typeof LINK_KEYS)[number], string>>;
  sources?: { site_url?: string; snapshot?: string; brandbook?: string };
  catalog?: { source_ref?: string };
  credentials?: { crm_ref?: string };
}

/** Keep only entries with substance; return undefined when nothing survives. */
function prune<T extends Record<string, unknown>>(obj: T): T | undefined {
  const out: Record<string, unknown> = {};
  for (const [k, val] of Object.entries(obj)) {
    if (val === undefined || val === null) continue;
    if (typeof val === "string" && !val.trim()) continue;
    if (Array.isArray(val) && val.length === 0) continue;
    if (
      typeof val === "object" &&
      !Array.isArray(val) &&
      Object.keys(val as object).length === 0
    )
      continue;
    out[k] = val;
  }
  return Object.keys(out).length > 0 ? (out as T) : undefined;
}

/** "sim"/"nao" -> boolean; anything else -> undefined (unanswered = OMITTED,
 *  never fabricated -- the detector keeps its own verdict). */
function simNao(raw: string): boolean | undefined {
  const s = raw.trim().toLowerCase();
  if (s === "sim") return true;
  if (s === "nao") return false;
  return undefined;
}

/** Build the answers OBJECT from form state. Empty optional keys are omitted.
 *  Coercions mirror the resolver: archetype lowercased, currency uppercased,
 *  formality -> integer when integer-shaped (else the raw string is emitted and
 *  the Python side rejects it honestly). PURE + TOTAL. */
export function buildAnswers(state: IntakeState): IntakeAnswers {
  const t = (k: IntakeKey): string => (state[k] ?? "").trim();
  const list = (k: IntakeKey): string[] => splitList(state[k] ?? "");

  const answers: IntakeAnswers = { form_version: 1 };

  const slug = t("tenant.slug");
  if (slug) answers.tenant = { slug };

  // v2 (2026-07-07): contact.* -- respondent provenance, never a credential.
  const contact = prune({ name: t("contact.name"), email: t("contact.email") });
  if (contact) answers.contact = contact;

  const identity = prune({
    brand_name: t("identity.brand_name"),
    brand_tagline: t("identity.brand_tagline"),
    brand_mission: t("identity.brand_mission"),
    brand_values: list("identity.brand_values"),
    brand_story: t("identity.brand_story"),
    legal_name: t("identity.legal_name"),
    vision: t("identity.vision"),
  });
  if (identity) answers.identity = identity;

  const archetype = prune({
    brand_archetype: t("archetype.brand_archetype").toLowerCase(),
    brand_personality: list("archetype.brand_personality"),
  });
  if (archetype) answers.archetype = archetype;

  const formalityRaw = t("voice.formality");
  const voice = prune({
    tone: t("voice.tone"),
    formality: /^-?[0-9]+$/.test(formalityRaw)
      ? Number(formalityRaw)
      : formalityRaw || undefined,
    language: t("voice.language"),
    do: list("voice.do"),
    dont: list("voice.dont"),
  });
  if (voice) answers.voice = voice;

  const audience = prune({
    icp: t("audience.icp"),
    transformation: t("audience.transformation"),
    wtp_band: t("audience.wtp_band"),
    demographics: t("audience.demographics"),
  });
  if (audience) answers.audience = audience;

  const colors = prune({
    primary: t("visual.colors.primary"),
    secondary: t("visual.colors.secondary"),
    accent: t("visual.colors.accent"),
  });
  const fonts = prune({
    heading: t("visual.fonts.heading"),
    body: t("visual.fonts.body"),
  });
  const visual = prune({
    colors,
    logo: t("visual.logo"),
    fonts,
    colors_description: t("visual.colors_description"),
    colors_avoid: list("visual.colors_avoid"),
    style_avoid: list("visual.style_avoid"),
    design_style: t("visual.design_style").toLowerCase(),
    logo_status: t("visual.logo_status").toLowerCase(),
    references: list("visual.references"),
  });
  if (visual) answers.visual = visual;

  const positioning = prune({
    category: t("positioning.category"),
    uvp: t("positioning.uvp"),
    content_pillars: list("positioning.content_pillars"),
    offerings: t("positioning.offerings"),
  });
  if (positioning) answers.positioning = positioning;

  const monetization = prune({
    pricing_model: t("monetization.pricing_model"),
    currency: t("monetization.currency").toUpperCase(),
    tiers: list("monetization.tiers"),
  });
  if (monetization) answers.monetization = monetization;

  const location = prune({
    channels: list("location.channels"),
    city_state: t("location.city_state"),
  });
  if (location) answers.location = location;

  // v2 (2026-07-07): market.* + applications.* -- new sections, omitted
  // entirely when empty (same sparse-emit contract as every section above).
  const market = prune({
    competitors: list("market.competitors"),
    edge_notes: t("market.edge_notes"),
    trends: t("market.trends"),
  });
  if (market) answers.market = market;

  const applications = prune({ surfaces: list("applications.surfaces") });
  if (applications) answers.applications = applications;

  const shape = prune({
    vertical: t("shape_confirm.vertical").toLowerCase(),
    has_store: simNao(state["shape_confirm.has_store"] ?? ""),
    has_blog: simNao(state["shape_confirm.has_blog"] ?? ""),
    has_b2b: simNao(state["shape_confirm.has_b2b"] ?? ""),
    b2b_mode: t("shape_confirm.b2b_mode").toLowerCase(),
  });
  if (shape) answers.shape_confirm = shape;

  const linksEntries: Record<string, string> = {};
  for (const key of LINK_KEYS) {
    const val = t(("links." + key) as IntakeKey);
    if (val) linksEntries[key] = val;
  }
  const links = prune(linksEntries);
  if (links) answers.links = links;

  const sources = prune({
    site_url: t("sources.site_url"),
    snapshot: t("sources.snapshot"),
    brandbook: t("sources.brandbook"),
  });
  if (sources) answers.sources = sources;

  const catalog = prune({ source_ref: t("catalog.source_ref") });
  if (catalog) answers.catalog = catalog;

  const credentials = prune({ crm_ref: t("credentials.crm_ref") });
  if (credentials) answers.credentials = credentials;

  return answers;
}

/** Answers object -> the answers FILE text: '#' comment header + pretty JSON.
 *  JSON is a YAML subset, so PyYAML safe_load parses this file as-is -- the
 *  exact input `python _tools/cex_ingest_registry.py --resolve` expects. */
export function answersToYamlText(answers: IntakeAnswers): string {
  const header = [
    "R-149 form_v1 answers -- emitted by the /intake web form (apps/public_site).",
    "The JSON body below IS valid YAML (JSON is a YAML subset; PyYAML parses it).",
    "Template: N02_marketing/P01_knowledge/p01_dq_tenant_intake_form.md",
    "Resolve:",
    "  python _tools/cex_ingest_registry.py --resolve THIS_FILE \\",
    "    --out brand_init.yaml --provenance provenance.json --emit-shape shape.json",
    "Consume:",
    "  python _tools/cex_bootstrap.py [--tenant SLUG] --from-file brand_init.yaml",
  ];
  return (
    header.map((l) => "# " + l).join("\n") +
    "\n" +
    JSON.stringify(answers, null, 2) +
    "\n"
  );
}

/** Form state -> the downloadable answers YAML (the always-on, prod-honest
 *  path: pure client, zero backend). */
export function buildAnswersFile(state: IntakeState): string {
  return answersToYamlText(buildAnswers(state));
}

/** The consume command the resolver itself prints in its --out header
 *  (cex_ingest_registry.py:554-556). */
export function bootstrapCommand(
  slug: string | null | undefined,
  brandInitPath: string,
): string {
  const tenantArg = slug ? "--tenant " + slug + " " : "";
  return "python _tools/cex_bootstrap.py " + tenantArg + "--from-file " + brandInitPath;
}

// ---------------------------------------------------------------------------
// Resolver CLI output parsing (the dev-only route's read-back seam).
// ---------------------------------------------------------------------------

export interface ResolveOutput {
  ok: boolean;
  /** The '[OK] resolved form_v1: ...' summary line, when present. */
  summary: string | null;
  /** '[WARN] ...' lines (resolve warnings are indented '  [WARN] ...'). */
  warnings: string[];
  /** '[FAIL] ...' lines (fail-closed refusals). */
  failures: string[];
}

/** Parse the resolver CLI's stable ASCII stdout. The CLI has NO --json flag
 *  today (unlike cex_tenant_bootstrap), so exit code + these line shapes ARE
 *  the machine contract. PURE + TOTAL. */
export function parseResolveOutput(
  stdout: unknown,
  exitCode: number | null,
): ResolveOutput {
  const text = typeof stdout === "string" ? stdout : "";
  const warnings: string[] = [];
  const failures: string[] = [];
  let summary: string | null = null;
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;
    if (line.startsWith("[OK] resolved form_v1:")) summary = line;
    else if (line.startsWith("[WARN]")) warnings.push(line.slice(6).trim());
    else if (line.startsWith("[FAIL]")) failures.push(line.slice(6).trim());
  }
  return { ok: exitCode === 0, summary, warnings, failures };
}

/** The JSON the dev-only /api/intake route returns -- an HONEST projection of
 *  the resolver run (paths repo-relative; nothing fabricated). */
export interface IntakeApiResponse {
  ok: boolean;
  summary?: string | null;
  resolver_warnings?: string[];
  errors?: string[];
  answers_path?: string;
  brand_init_path?: string;
  provenance_path?: string;
  shape_path?: string;
  /** Displayed, NEVER auto-run: brand-state mutation stays operator-explicit. */
  bootstrap_cmd?: string;
}

// ---------------------------------------------------------------------------
// Draft persistence (DP5, v2 2026-07-07): localStorage save/restore/clear.
// The Google-Forms-style "your progress is saved" UX the old Briefing da
// Marca form had natively. PURE + TOTAL here -- the page (app/intake/page.tsx)
// owns the actual `window.localStorage` calls inside useEffect (browser-only);
// this module only serializes/parses/validates the payload SHAPE so the
// logic is unit-testable without a DOM.
// ---------------------------------------------------------------------------

/** The localStorage key. Versioned so a future incompatible shape change can
 *  detect + discard an old draft instead of corrupting state. */
export const INTAKE_DRAFT_STORAGE_KEY = "cexai_intake_draft_v1";

export interface IntakeDraftPayload {
  version: 1;
  savedAt: string;
  state: IntakeState;
}

/** Form state -> the JSON string persisted to localStorage. PURE + TOTAL. */
export function serializeDraft(
  state: IntakeState,
  now: () => string = () => new Date().toISOString(),
): string {
  const payload: IntakeDraftPayload = { version: 1, savedAt: now(), state };
  return JSON.stringify(payload);
}

/** localStorage's raw string -> a full IntakeState, or null. Degrade-never:
 *  missing/malformed JSON, a foreign shape, or a version mismatch all return
 *  null (never throws, never partially hydrates state with an unknown shape).
 *  Any key absent from the parsed state.state defaults to "" (an old draft
 *  saved before a new v2 key existed still restores cleanly). PURE + TOTAL. */
export function parseDraft(raw: string | null | undefined): IntakeState | null {
  if (!raw) return null;
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    return null;
  }
  if (
    !data ||
    typeof data !== "object" ||
    (data as Partial<IntakeDraftPayload>).version !== 1 ||
    typeof (data as Partial<IntakeDraftPayload>).state !== "object" ||
    (data as Partial<IntakeDraftPayload>).state === null
  ) {
    return null;
  }
  const savedState = (data as IntakeDraftPayload).state as Record<string, unknown>;
  const out = emptyIntakeState();
  for (const k of ALL_KEYS) {
    const v = savedState[k];
    if (typeof v === "string") out[k] = v;
  }
  return out;
}
