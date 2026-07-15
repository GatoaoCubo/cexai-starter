// ----------------------------------------------------------------------------
// Capability input_contract -> typed form fields (mission BRANDBOOK, Cell A).
//
// A capability can declare an INPUT CONTRACT (MoldField[] -- the SAME shape lib/molds
// already pins per capability). The run cockpit (components/RunModal) renders ONE form
// control per field, deriving the control KIND from the field's declared ``type``:
//
//   * "file" (any media) -> an <input type=file>. The pick is read to a data: URI and
//        sent as the field value. The BACKEND resolves it: an IMAGE -> a dominant-color
//        palette at ``inputs[<key>_palette]``; a DOC -> extracted text at ``inputs[<key>_text]``.
//   * "url"              -> a URL text input. The backend FETCHES it -> ``inputs[<key>_text]``.
//   * "text"             -> a multi-line textarea (the guided free description).
//   * "enum"             -> a <select> of ``enum_values`` (falls back to text when none).
//   * "number"/"integer" -> a numeric text input (coerced to a Number on submit).
//   * "boolean"          -> a true/false select.
//   * "string" / "x[]"   -> text (an array type is a comma-joined freeform value).
//
// This MIRRORS the agent Input Schema renderer (lib/agentSchema) but consumes the ALREADY
// TYPED MoldField shape (no raw-string parsing) and adds the file/url/text ingest controls.
// It is a SEPARATE module -- agentSchema is untouched. TOTAL: an absent/empty contract
// yields [] and the cockpit falls back to the single free-text intent box (degrade-never).
//
// ASCII-only + diacritic-free (the dashboard house style). PURE DATA -- no React.
// ----------------------------------------------------------------------------

import type { MoldField } from "@/lib/molds";

/** The rendered control a contract field maps to. */
export type ContractControl =
  | "text"
  | "textarea"
  | "number"
  | "enum"
  | "boolean"
  | "file"
  | "url";

/** One typed field derived from a capability's input_contract entry. */
export interface ContractField {
  /** the input key sent to the backend (snake_case, e.g. "brand_logo"). */
  key: string;
  /** human label for the field (falls back to the key). */
  label: string;
  /** the rendered control kind. */
  control: ContractControl;
  /** whether the capability requires this field. */
  required: boolean;
  /** enum options when control === "enum" (else []). */
  options: string[];
  /** placeholder hint for text/number/url fields (from the field's example). */
  placeholder: string;
  /** optional one-line note (allowed values, units, gotchas). */
  note?: string;
  /** the file input ``accept`` attribute when control === "file" ("" = any media). */
  accept?: string;
  /** short type label shown next to the field name (e.g. "file", "url", "number"). */
  typeLabel: string;
}

/**
 * Map a capability's input_contract (MoldField[]) into renderable form fields. Returns []
 * when the contract is absent/empty (the cockpit then shows a single free-text intent box).
 * NEVER throws.
 */
export function contractFields(
  contract: MoldField[] | undefined | null,
): ContractField[] {
  if (!Array.isArray(contract)) return [];
  const out: ContractField[] = [];
  const seen = new Set<string>();
  for (const f of contract) {
    if (!f || typeof f.key !== "string" || !f.key.trim()) continue;
    const key = f.key.trim();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(fieldFromMold(f, key));
  }
  return out;
}

/**
 * Coerce a string form value into the type the field declares, for the submit payload.
 * Conservative: a number field with a non-numeric value stays the raw string; a boolean
 * maps "true"/"false"; file (a data: URI) / url / text / enum stay strings. NEVER throws.
 */
export function coerceContractValue(
  raw: string,
  field: ContractField,
): string | number | boolean {
  const v = raw.trim();
  if (field.control === "number") {
    const n = Number(v);
    return Number.isFinite(n) && v !== "" ? n : v;
  }
  if (field.control === "boolean") {
    if (v === "true") return true;
    if (v === "false") return false;
    return v;
  }
  // file values are data: URIs (NOT trimmed away) -- keep the raw, untrimmed string.
  if (field.control === "file") return raw;
  return v;
}

// --- internals ---------------------------------------------------------------

function fieldFromMold(f: MoldField, key: string): ContractField {
  const type = String(f.type ?? "string").trim().toLowerCase();
  const base = {
    key,
    label: f.label || key,
    required: Boolean(f.required),
    options: [] as string[],
    placeholder: exampleToPlaceholder(f.example),
    note: f.note,
    typeLabel: String(f.type ?? "string"),
  };

  // file / any-media upload
  if (type === "file" || type === "upload" || type === "media" || type === "image") {
    return { ...base, control: "file", accept: type === "image" ? "image/*" : "" };
  }
  // url -> fetched server-side
  if (type === "url") {
    return { ...base, control: "url", placeholder: base.placeholder || "https://..." };
  }
  // enum -> a select of enum_values (degrade to text when none declared)
  if (type === "enum") {
    const options = enumOptions(f);
    if (options.length >= 2) return { ...base, control: "enum", options };
    return { ...base, control: "text" };
  }
  // an array type ("string[]", "number[]") -> a comma-joined freeform textarea
  if (type.endsWith("[]")) {
    return {
      ...base,
      control: "textarea",
      placeholder: base.placeholder || "valores separados por virgula",
    };
  }
  // explicit multi-line text
  if (type === "text" || type === "textarea" || type === "longtext") {
    return { ...base, control: "textarea" };
  }
  if (
    type.startsWith("number") ||
    type.startsWith("integer") ||
    type.startsWith("int") ||
    type.startsWith("float")
  ) {
    return { ...base, control: "number", placeholder: base.placeholder || "0" };
  }
  if (type.startsWith("bool")) {
    return { ...base, control: "boolean" };
  }
  // default: a single-line text input.
  return { ...base, control: "text" };
}

/** enum_values -> string options (the structured enum declaration); [] when absent. */
function enumOptions(f: MoldField): string[] {
  if (Array.isArray(f.enum_values) && f.enum_values.length > 0) {
    return f.enum_values.map((v) => String(v));
  }
  return [];
}

/** Render a field's example value into a placeholder string. NEVER throws. */
function exampleToPlaceholder(example: MoldField["example"]): string {
  if (example === undefined || example === null) return "";
  if (Array.isArray(example)) return example.map((e) => String(e)).join(", ");
  return String(example);
}
