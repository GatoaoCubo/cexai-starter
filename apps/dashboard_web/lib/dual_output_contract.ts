// ----------------------------------------------------------------------------
// DUAL-OUTPUT CONTRACT -- the universal output contract every capability inherits
// (founder directive 2026-06-21; mission DUALMINT, Wave 1).
//
// EVERY dashboard capability emits ONE asset with TWO coupled faces:
//   * MACHINE face -- the canonical `.md` + YAML frontmatter: typed/governed, persisted
//     tenant-scoped to the tenant's OWN Supabase and readable by THAT tenant's AI.
//   * HUMAN face   -- an HTML AUDIOVISUAL render: the structured sections as readable
//     widgets PLUS a media layer of editable slots (real <img>/<video>/<audio> when the
//     pipeline produced it, an upload-fallback dropzone when it did not).
//
// The two faces share ONE `id` (the coupling): the human edits the visual/media side, the
// tenant's AI reads + operates the structured `.md`+YAML side -- they CO-OWN the asset. A
// media slot is referenced by the SAME `key` on both faces (the human face's data-slot-key
// <-> the machine frontmatter `media[].key`), so a human upload updates the machine ledger
// entry the AI reads. That key-equality IS the sync rule.
//
// THESE ARE PURE TYPES -- no React, no runtime, no UI. They mirror the Python emitter
// (_tools/cex_dual_output.to_dual_output) field-for-field and reuse the FROZEN MoldSection
// shape (lib/molds) for the structured body, so the same object round-trips Python -> wire
// -> TS. ADDITIVE + backward-compatible: this sits ALONGSIDE MoldedStructuredResult
// (lib/types) -- the structured payload a generator already emits -- and wraps it with the
// dual faces; it does not replace it.
//
// ASCII-only + diacritic-free (the dashboard's house style): "--" for em-dash, "->" for
// arrows, no accents. Spec: _docs/specs/spec_dual_output_contract.md.
// ----------------------------------------------------------------------------

// MoldSection is the frozen output-section shape (lib/molds): one of layout
// "fields" | "table" | "list". The MACHINE face's structured body IS a list of these (the
// SAME shape the mock mold and the real generator already use -- see MoldedStructuredResult).
import type { MoldSection } from "@/lib/molds";

/** The media kinds a slot may carry. Mirrors cex_dual_output.VALID_MEDIA_KINDS. */
export type MediaKind = "image" | "video" | "audio";

/**
 * A slot's fill state:
 *   - "generated" -> the media pipeline already produced it; `src` is present.
 *   - "empty"     -> NOT produced; `src` is ABSENT (NEVER a fabricated/blank URL). The human
 *                    face renders an upload-fallback dropzone; a human upload flips it to
 *                    "generated" and fills `src` (the sync rule).
 */
export type MediaSlotStatus = "generated" | "empty";

/**
 * ONE editable media slot -- the unit of the human/AI media coupling. Identified by `key`
 * (unique within an asset); the SAME `key` keys the machine frontmatter `media[]` ledger.
 *
 * NEVER-FABRICATE invariant: a slot with status "empty" carries NO `src`. The renderer shows
 * an upload dropzone for it, never a broken <img>/<video>/<audio>. `editable` + `uploadFallback`
 * are ALWAYS true (a human may swap a generated asset too, and any slot accepts an upload).
 */
export interface MediaSlot {
  /** the coupling key (unique per asset); matches the machine frontmatter media[].key. */
  key: string;
  /** image | video | audio. */
  kind: MediaKind;
  /** generated (has src) | empty (upload-fallback, no src). */
  status: MediaSlotStatus;
  /** the produced media URL -- present ONLY when status === "generated". Never fabricated. */
  src?: string;
  /** human caption / accessibility text (alt). */
  alt?: string;
  /** the structured section title this slot decorates (renders under it); unbound -> gallery. */
  section?: string;
  /** optional human label for the slot / its upload prompt. */
  label?: string;
  /** a human can always swap/edit this slot -- ALWAYS true. */
  editable: true;
  /** an empty slot offers upload (and a generated one offers replace) -- ALWAYS true. */
  uploadFallback: true;
}

/**
 * The MACHINE face -- the canonical, AI-readable projection. `md` is the full `.md` string
 * (YAML frontmatter + a body of the structured sections + a media ledger). `frontmatter` is
 * that frontmatter parsed: the coupling identity + the media ledger the tenant's AI reads.
 */
export interface DualOutputMachineFace {
  /** the canonical `.md`: YAML frontmatter + structured body + media ledger. Source of truth. */
  md: string;
  /**
   * the parsed frontmatter. Carries at least: id, capability, tenant, created, kind, real,
   * passed, score, schema_version, and media[] (the slot ledger -- {key, kind, status, src?}).
   * Typed loosely (Record) because it is tenant/capability-extensible; the structured BODY
   * (the MoldSection list) travels in `md` and on the human face below.
   */
  frontmatter: Record<string, unknown>;
}

/**
 * The HUMAN face -- the audiovisual projection. `html` is the self-contained report (the
 * structured sections + the media layer). `mediaSlots` is the resolved slot ledger (the SAME
 * objects keyed into the machine frontmatter media[]), so the UI can wire upload/edit handlers
 * by `key` without re-parsing the HTML.
 */
export interface DualOutputHumanFace {
  /** the HTML audiovisual render (structured widgets + media slots). Always derivative. */
  html: string;
  /** the editable media slots (coupling ledger). An empty slot has no src (upload-fallback). */
  mediaSlots: MediaSlot[];
}

/**
 * The whole DUAL-OUTPUT asset: ONE shared `id` + the two coupled faces. This is what the
 * Python emitter returns (cex_dual_output.to_dual_output -> {id, capability, machine_md,
 * human_html, media_slots, frontmatter}) reshaped into the two-face object the UI consumes.
 *
 * Coupling: `id` is identical across both faces; a `mediaSlots[i].key` equals a machine
 * `frontmatter.media[j].key`. Editing a slot on the human side updates the machine ledger
 * entry the AI reads -- the asset is co-owned, not a one-way handoff.
 */
export interface DualOutputContract {
  /** the shared id coupling the two faces (the persisted tenant record id at runtime). */
  id: string;
  /** the capability that produced the asset (e.g. "research", "marketplace_listing"). */
  capability: string;
  /** the canonical machine face (.md + frontmatter), AI-readable + persisted tenant-scoped. */
  machine: DualOutputMachineFace;
  /** the human audiovisual face (HTML + media slots), human-editable + publishable. */
  human: DualOutputHumanFace;
  /** the structured sections (the FROZEN MoldSection list) -- the shared body both faces render. */
  sections?: MoldSection[];
  /** true => a real run (renderer shows "resultado real"); false => molded/simulated. */
  real?: boolean;
  /** the generator's F7 self-score (0..1), when present. */
  score?: number;
  /** the generator's F7 gate verdict, when present. */
  passed?: boolean;
  /** any extra emitter keys not named here (never silently dropped). */
  [key: string]: unknown;
}

/**
 * One media slot the capability DECLARES it wants, BEFORE the pipeline runs. The emitter
 * turns each request into a MediaSlot: produced -> "generated" (src filled), else -> "empty"
 * (upload-fallback). A capability that declares none gets one empty hero image slot by default
 * (the editable affordance the directive requires). Mirrors the Python `media_requests` arg.
 */
export interface MediaRequest {
  /** the coupling key the produced media / the human upload will fill. */
  key: string;
  /** image | video | audio. */
  kind: MediaKind;
  /** the structured section title to bind the slot under (optional; unbound -> gallery). */
  section?: string;
  /** optional human label / upload prompt for the slot. */
  label?: string;
}
