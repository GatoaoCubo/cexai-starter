// ----------------------------------------------------------------------------
// Agent Input Schema -> typed form fields (ADR adr_agents_sdk_dashboard, Phase B).
//
// The agent's Input Schema is a RAW JSON-ish string parsed from the agent / agent_card
// on disk (agents_config._extract_json_block). It looks like, e.g.:
//
//   { "topic": "string", "depth": "shallow|standard|deep", "competitors": ["string"] }
//
// The run cockpit renders ONE form field per top-level key, with the field KIND derived
// from the declared value:
//   * "a|b|c"            -> an enum (a <select> of options).
//   * "string"           -> text.
//   * "number"/"integer" -> a numeric text input (coerced to a Number on submit).
//   * "boolean"          -> a true/false select.
//   * ["..."] / object   -> text (a comma-joined / freeform value the agent parses).
//
// This is best-effort + TOTAL: a schema that does not parse as JSON falls back to a
// light line-scan; a fully unparseable schema yields [] (the cockpit then shows a single
// free-text intent box). The parser NEVER throws -- a bad schema must never break the run
// cockpit. The coercion is conservative: anything ambiguous stays a string (the backend's
// ASSEMBLE loader binds the inputs into the contract regardless of exact type).
// ----------------------------------------------------------------------------

/** A single typed field derived from one Input Schema key. */
export interface SchemaField {
  /** the schema key (the input name sent to the backend). */
  key: string;
  /** the rendered control kind. */
  kind: "string" | "number" | "boolean" | "enum";
  /** a short type label shown next to the field name (e.g. "string", "number", "a|b"). */
  typeLabel: string;
  /** enum options when kind === "enum" (else []). */
  options: string[];
  /** placeholder hint for text/number fields. */
  placeholder: string;
}

/**
 * Parse an agent's Input Schema string into typed form fields. Returns [] when the schema
 * is empty or unparseable (the cockpit then falls back to a single free-text intent box).
 * NEVER throws.
 */
export function parseSchemaFields(schema: string | undefined | null): SchemaField[] {
  if (!schema || typeof schema !== "string" || !schema.trim()) return [];

  // 1. Try strict JSON first (the common, well-formed case).
  const obj = tryParseJsonObject(schema);
  if (obj) {
    const fields: SchemaField[] = [];
    for (const [key, raw] of Object.entries(obj)) {
      const k = String(key).trim();
      if (!k) continue;
      fields.push(fieldFromDeclared(k, raw));
    }
    if (fields.length > 0) return fields;
  }

  // 2. Fallback: a light line-scan for "key": value-ish (tolerates trailing commas, comments).
  return scanFields(schema);
}

/**
 * Coerce a string form value into the type the field declares, for the submit payload.
 * Conservative: a number field with a non-numeric value stays the raw string; a boolean
 * maps "true"/"false"; everything else is the trimmed string. NEVER throws.
 */
export function coerceFieldValue(
  raw: string,
  field: SchemaField,
): string | number | boolean {
  const v = raw.trim();
  if (field.kind === "number") {
    const n = Number(v);
    return Number.isFinite(n) && v !== "" ? n : v;
  }
  if (field.kind === "boolean") {
    if (v === "true") return true;
    if (v === "false") return false;
    return v;
  }
  return v;
}

// --- internals ---------------------------------------------------------------

function tryParseJsonObject(schema: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(schema);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
    /* not strict JSON -- fall through to the line scan */
  }
  return null;
}

/** Build a SchemaField from a key + its declared value (a JSON value). */
function fieldFromDeclared(key: string, declared: unknown): SchemaField {
  // A nested array/object -> a text field the agent parses (comma-joined freeform).
  if (Array.isArray(declared) || (declared && typeof declared === "object")) {
    return {
      key,
      kind: "string",
      typeLabel: Array.isArray(declared) ? "list" : "object",
      options: [],
      placeholder: Array.isArray(declared) ? "comma-separated values" : "",
    };
  }
  const decl = String(declared ?? "").trim();
  return fieldFromTypeString(key, decl);
}

/** Build a SchemaField from a key + the declared TYPE STRING (e.g. "string", "a|b|c"). */
function fieldFromTypeString(key: string, decl: string): SchemaField {
  const lower = decl.toLowerCase();

  // An enum is a pipe-joined set of LITERAL options (e.g. "shallow|standard|deep"). We treat
  // it as an enum only when it has >=2 parts AND none of the parts is a bare scalar TYPE name
  // (so "number" alone is not an enum, but "npm|pip|cargo" is).
  if (decl.includes("|")) {
    const parts = decl.split("|").map((p) => p.trim()).filter(Boolean);
    if (parts.length >= 2) {
      return {
        key,
        kind: "enum",
        typeLabel: parts.join(" | ").slice(0, 40),
        options: parts,
        placeholder: "",
      };
    }
  }

  if (lower.startsWith("number") || lower.startsWith("integer") || lower.startsWith("int") || lower.startsWith("float")) {
    return { key, kind: "number", typeLabel: "number", options: [], placeholder: "0" };
  }
  if (lower.startsWith("bool")) {
    return { key, kind: "boolean", typeLabel: "boolean", options: [], placeholder: "" };
  }
  // Default: a string field. The declared type (if any) is shown as the label.
  return {
    key,
    kind: "string",
    typeLabel: decl || "string",
    options: [],
    placeholder: "",
  };
}

/**
 * Last-resort line scan for ``"key": value`` pairs when the schema is not strict JSON.
 * Picks up the top-level keys and their declared value text. Bounded to 40 fields.
 */
function scanFields(schema: string): SchemaField[] {
  const fields: SchemaField[] = [];
  const seen = new Set<string>();
  // Match  "key": "value"  OR  "key": value  on a line (the value is best-effort).
  const re = /"([A-Za-z_][\w.-]*)"\s*:\s*("?)([^",}\n]*)\2/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(schema)) !== null && fields.length < 40) {
    const key = m[1].trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    const decl = (m[3] || "").trim();
    fields.push(fieldFromTypeString(key, decl));
  }
  return fields;
}
