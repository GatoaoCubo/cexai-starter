// ----------------------------------------------------------------------------
// CAPABILITY MOLD TYPES + pure render helpers -- a LIFTED SUBSET of
// apps/dashboard_web/lib/molds.ts (keep the TYPES in sync with the dashboard).
//
// The public site only needs:
//   1. the FROZEN structured-output shape (MoldField / MoldSection / CapabilityMold)
//      that DualOutputContract.sections and a published payload's output_sections use;
//   2. the PURE + TOTAL pending-copy helpers (PENDING_COPY_MARKER / stripPendingMarker
//      / sectionHasPendingCopy) so a published asset whose copy was still scaffold
//      never leaks the internal marker to a public visitor.
//
// DROPPED (dashboard-only): the inline mold instances (MOLD_ADS, ...), the MOLDS
// registry, moldFor(), inputExampleFor(), the bespoke-vertical input contracts.
// The public site renders a PUBLISHED payload's own sections -- it never resolves a
// capability mock mold.
//
// ASCII-only + diacritic-free (house style): "--" for em-dash, "->" for arrows.
// PURE DATA + PURE FUNCTIONS -- no React, no runtime.
// ----------------------------------------------------------------------------

/**
 * One field of a capability's INPUT CONTRACT. ``example`` is a realistic sample
 * value. Kept so a published payload that echoes its input contract round-trips.
 */
export interface MoldField {
  /** the input key the capability reads (snake_case, e.g. "num_variants"). */
  key: string;
  /** human label for the field. */
  label: string;
  /** the declared type ("string" | "number" | "enum" | "string[]" | ...). */
  type: string;
  /** whether the capability requires this field. */
  required: boolean;
  /** a realistic example value (string | number | boolean | list). */
  example: string | number | boolean | (string | number | boolean)[];
  /** optional one-line note (allowed values, units, gotchas). */
  note?: string;
  /** validation rigor (all optional). */
  enum_values?: (string | number)[];
  min_len?: number;
  max_len?: number;
  min?: number;
  max?: number;
  pattern?: string;
  default?: string | number | boolean;
}

/**
 * One section of a capability's OUTPUT MOLD. Rendered per ``layout``:
 *   - "fields" -> ``rows`` as label/value pairs
 *   - "table"  -> ``columns`` header + ``table`` rows (a grid)
 *   - "list"   -> ``items`` as chips
 * This is the FROZEN shape both dual-output faces render (mirrors the dashboard).
 */
export interface MoldSection {
  /** section heading (e.g. "Variantes"). */
  title: string;
  /** how the section renders. */
  layout: "fields" | "table" | "list";
  /** optional one-line note under the heading. */
  note?: string;
  /** layout="fields": label/value rows. */
  rows?: { label: string; value: string | number | boolean }[];
  /** layout="table": column headers. */
  columns?: string[];
  /** layout="table": optional per-column type hints. */
  column_types?: string[];
  /** layout="table": which column holds the row key. */
  key_col_index?: number;
  /** layout="table": row cells (each row aligns to ``columns``). */
  table?: (string | number | boolean)[][];
  /** layout="list": chip items. */
  items?: string[];
  /** optional contract version stamp. */
  contract_version?: string;
}

/**
 * The whole mold for ONE capability: its identity + the input contract + the
 * output sections. Kept as a type for parity with the dashboard; the public site
 * does not author or resolve mold instances.
 */
export interface CapabilityMold {
  /** the capability id this mold shapes. */
  capability: string;
  /** the artifact kind the real generator produces (provenance chip). */
  kind: string;
  /** one-line "what this capability molds". */
  summary: string;
  /** the typed input fields (with example values). */
  input_contract: MoldField[];
  /** the structured output mold. */
  output_sections: MoldSection[];
  /** optional contract version stamp (e.g. "1.0"). */
  contract_version?: string;
}

// ----------------------------------------------------------------------------
// PENDING-COPY (scaffold) DETECTION -- the HONEST empty-state rule.
//
// A capability whose creative lane could not produce REAL copy returns a
// deterministic SCAFFOLD: its copy cells carry an INTERNAL placeholder marker. That
// marker is an internal signal -- a public visitor must NEVER see it. These are PURE
// + TOTAL (no React). Lifted verbatim from the dashboard's molds.ts so a published
// asset is sanitized identically on the public surface.
// ----------------------------------------------------------------------------

/** The internal scaffold marker a generator embeds in a copy cell when it had no
 *  real copy to emit. Kept in ONE place; it is never shown to a visitor. */
export const PENDING_COPY_MARKER = "(generation_pending)";

/** True when a value carries the scaffold marker -- i.e. it is placeholder, not real copy. */
function carriesPendingMarker(value: unknown): boolean {
  return typeof value === "string" && value.indexOf(PENDING_COPY_MARKER) !== -1;
}

/**
 * Remove the internal scaffold marker from a DISPLAY string (defense-in-depth: even a
 * cell a section's empty-state did not replace must never leak the raw marker). Collapses
 * the whitespace the removal leaves behind. A string without the marker is returned as-is.
 */
export function stripPendingMarker(text: string): string {
  if (text.indexOf(PENDING_COPY_MARKER) === -1) return text;
  return text.split(PENDING_COPY_MARKER).join("").replace(/\s{2,}/g, " ").trim();
}

/**
 * True when a section still carries SCAFFOLD placeholder copy (any of its cells /
 * values / items holds the marker). GENERIC -- it does NOT hardcode section titles:
 * a section is "pending" iff its OWN data still holds the marker, so it flips to
 * "real" automatically the moment real copy lands.
 */
export function sectionHasPendingCopy(section: MoldSection): boolean {
  if (Array.isArray(section.table)) {
    for (const row of section.table) {
      if (Array.isArray(row) && row.some(carriesPendingMarker)) return true;
    }
  }
  if (Array.isArray(section.rows)) {
    if (section.rows.some((r) => r && carriesPendingMarker(r.value))) return true;
  }
  if (Array.isArray(section.items)) {
    if (section.items.some(carriesPendingMarker)) return true;
  }
  return false;
}
