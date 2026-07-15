// MIRRORS apps/dashboard_web/lib/dual_output_contract.ts -- keep in sync.
//
// ----------------------------------------------------------------------------
// DUAL-OUTPUT CONTRACT -- the universal output contract every capability inherits
// (founder directive 2026-06-21; mission DUALMINT, Wave 1). Lifted verbatim for the
// L2 public site: a published catalog item that carries a dual_output asset is
// rendered by DualOutputFacePublic from THESE typed faces.
//
// EVERY dashboard capability emits ONE asset with TWO coupled faces:
//   * MACHINE face -- the canonical `.md` + YAML frontmatter: typed/governed.
//   * HUMAN face   -- an HTML AUDIOVISUAL render: the structured sections as readable
//     widgets PLUS a media layer of slots (real <img>/<video>/<audio> when produced).
//
// The two faces share ONE `id` (the coupling). A media slot is referenced by the
// SAME `key` on both faces. THESE ARE PURE TYPES -- no React, no runtime.
//
// ASCII-only + diacritic-free (house style): "--" for em-dash, "->" for arrows.
// ----------------------------------------------------------------------------

// MoldSection is the frozen output-section shape (lib/molds): one of layout
// "fields" | "table" | "list". The MACHINE face's structured body IS a list of these.
import type { MoldSection } from "@/lib/molds";

/** The media kinds a slot may carry. Mirrors cex_dual_output.VALID_MEDIA_KINDS. */
export type MediaKind = "image" | "video" | "audio";

/**
 * A slot's fill state:
 *   - "generated" -> the media pipeline already produced it; `src` is present.
 *   - "empty"     -> NOT produced; `src` is ABSENT (NEVER a fabricated/blank URL).
 */
export type MediaSlotStatus = "generated" | "empty";

/**
 * ONE media slot -- the unit of the human/AI media coupling. Identified by `key`.
 * NEVER-FABRICATE invariant: a slot with status "empty" carries NO `src`.
 *
 * NOTE (public site): on the read-only public surface the upload affordances
 * (editable / uploadFallback) are IGNORED -- DualOutputFacePublic strips all edit
 * handlers and renders an empty slot as a static "midia indisponivel" placeholder.
 */
export interface MediaSlot {
  /** the coupling key (unique per asset); matches the machine frontmatter media[].key. */
  key: string;
  /** image | video | audio. */
  kind: MediaKind;
  /** generated (has src) | empty (no src). */
  status: MediaSlotStatus;
  /** the produced media URL -- present ONLY when status === "generated". Never fabricated. */
  src?: string;
  /** human caption / accessibility text (alt). */
  alt?: string;
  /** the structured section title this slot decorates (renders under it); unbound -> gallery. */
  section?: string;
  /** optional human label for the slot. */
  label?: string;
  /** a human can always swap/edit this slot -- ALWAYS true (ignored on the public read surface). */
  editable: true;
  /** an empty slot offers upload -- ALWAYS true (ignored on the public read surface). */
  uploadFallback: true;
}

/**
 * The MACHINE face -- the canonical, AI-readable projection. `md` is the full `.md`
 * string. `frontmatter` is that frontmatter parsed.
 */
export interface DualOutputMachineFace {
  /** the canonical `.md`: YAML frontmatter + structured body + media ledger. Source of truth. */
  md: string;
  /** the parsed frontmatter. Typed loosely (Record) because it is extensible. */
  frontmatter: Record<string, unknown>;
}

/**
 * The HUMAN face -- the audiovisual projection. `html` is the self-contained report.
 * `mediaSlots` is the resolved slot ledger.
 */
export interface DualOutputHumanFace {
  /** the HTML audiovisual render (structured widgets + media slots). Always derivative. */
  html: string;
  /** the media slots (coupling ledger). An empty slot has no src. */
  mediaSlots: MediaSlot[];
}

/**
 * The whole DUAL-OUTPUT asset: ONE shared `id` + the two coupled faces.
 */
export interface DualOutputContract {
  /** the shared id coupling the two faces (the persisted tenant record id at runtime). */
  id: string;
  /** the capability that produced the asset (e.g. "research", "marketplace_listing"). */
  capability: string;
  /** the canonical machine face (.md + frontmatter). */
  machine: DualOutputMachineFace;
  /** the human audiovisual face (HTML + media slots). */
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
 * One media slot the capability DECLARES it wants, BEFORE the pipeline runs.
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
