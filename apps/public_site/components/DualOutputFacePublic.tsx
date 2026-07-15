"use client";

// ----------------------------------------------------------------------------
// DualOutputFacePublic -- the READ-ONLY public human face of a published
// dual-output asset (spec 10 W1-frontend).
//
// ADAPTED from apps/dashboard_web/components/DualOutputFace.tsx, stripped to a
// public, read-only surface. It renders STRICTLY from the TYPED contract:
//   * the structured sections (StructuredSections, typed -- never raw HTML);
//   * the media slots, and ONLY a slot whose src passes isSafeMediaSrc (https: or
//     data:image|video|audio) -- an empty/unsafe slot is a static placeholder,
//     never a broken tag and never a beacon.
//
// REMOVED vs the dashboard (this is the security keystone -- an UNAUTHENTICATED
// public page):
//   * ALL upload / edit / replace / dropzone handlers + the File picker + the
//     object-URL machinery. A visitor cannot mutate anything.
//   * the live-DOM treatment of human_html. human_html is TENANT-AUTHORED -- it is
//     an EXPORT STRING, NOT an interactive surface. We NEVER dangerouslySetInnerHTML
//     it on the live page. If shown at all, it is isolated in a SANDBOXED <iframe>
//     via srcDoc with the sandbox attribute and NO allow-scripts (so no script,
//     form, popup, or same-origin access from the tenant markup can run). Mirrors
//     DualOutputFace's "human_html is an export string" principle.
//
// DEGRADE-NEVER + TOTAL: every field is optional; an asset with neither sections
// nor media nor a machine face renders nothing. Never throws.
//
// ASCII-only + diacritic-free (house style). Reuses the shared design tokens.
// ----------------------------------------------------------------------------

import { useState } from "react";
import type { MediaKind } from "@/lib/dual_output_contract";
import type { MoldSection } from "@/lib/molds";
import { isSafeMediaSrc } from "@/lib/mediaSafety";
import { StructuredSections } from "./StructuredSections";

/** The loose shape a published dual_output asset can arrive in. We accept BOTH the
 *  flat emitter shape (snake_case) AND an already-reshaped contract, read DEFENSIVELY. */
export interface PublicDualOutput {
  id?: unknown;
  capability?: unknown;
  real?: unknown;
  /** flat emitter shape */
  machine_md?: unknown;
  human_html?: unknown;
  media_slots?: unknown;
  frontmatter?: unknown;
  sections?: unknown;
  /** reshaped-contract shape */
  machine?: { md?: unknown };
  human?: { html?: unknown; mediaSlots?: unknown };
  [key: string]: unknown;
}

const VALID_KINDS: readonly MediaKind[] = ["image", "video", "audio"];

function asKind(v: unknown): MediaKind {
  const k = String(v ?? "").toLowerCase();
  return (VALID_KINDS as readonly string[]).includes(k) ? (k as MediaKind) : "image";
}

/** A slot reduced to exactly what the read-only renderer needs. */
interface NormalSlot {
  key: string;
  kind: MediaKind;
  /** true ONLY when the pipeline produced a real, SAFE-scheme src. */
  shown: boolean;
  src?: string;
  alt?: string;
  label: string;
}

/**
 * Reduce the raw media_slots (unknown) into NormalSlot[]. NEVER-FABRICATE + the
 * scheme allowlist are BOTH enforced here: a slot is "shown" ONLY when status ===
 * "generated" AND it carries a src that passes isSafeMediaSrc. A mislabeled
 * "generated" with no/unsafe src degrades to a static placeholder (no upload here).
 */
function normalizeSlots(raw: unknown): NormalSlot[] {
  if (!Array.isArray(raw)) return [];
  const out: NormalSlot[] = [];
  const seen = new Set<string>();
  raw.forEach((s, i) => {
    if (!s || typeof s !== "object") return;
    const o = s as Record<string, unknown>;
    const key = String(o.key ?? "").trim() || `slot_${i}`;
    if (seen.has(key)) return;
    seen.add(key);
    const kind = asKind(o.kind);
    const rawSrc = typeof o.src === "string" && o.src.trim() ? o.src.trim() : undefined;
    // Scheme allowlist: a produced src with an unsafe scheme is DROPPED.
    const src = rawSrc && isSafeMediaSrc(rawSrc) ? rawSrc : undefined;
    const shown = String(o.status ?? "") === "generated" && !!src;
    const alt = typeof o.alt === "string" && o.alt.trim() ? o.alt.trim() : undefined;
    const label =
      (typeof o.label === "string" && o.label.trim() ? o.label.trim() : "") || alt || key;
    out.push({ key, kind, shown, src: shown ? src : undefined, alt, label });
  });
  return out;
}

/** The structured sections from either projection. */
function dualSections(dual: PublicDualOutput): MoldSection[] {
  if (Array.isArray(dual.sections)) return dual.sections as MoldSection[];
  return [];
}

/** The raw media slots from either projection (flat media_slots | human.mediaSlots). */
function rawSlots(dual: PublicDualOutput): unknown {
  if (Array.isArray(dual.media_slots)) return dual.media_slots;
  const h = dual.human;
  return h && Array.isArray(h.mediaSlots) ? h.mediaSlots : [];
}

/** The human_html export string from either projection (flat | human.html). */
function humanHtml(dual: PublicDualOutput): string {
  if (typeof dual.human_html === "string") return dual.human_html;
  const h = dual.human;
  return h && typeof h.html === "string" ? h.html : "";
}

/** The honest "resultado real vs amostra" determination. Tied to the run's ``real``
 *  flag; an explicit frontmatter grounding.approved === false demotes it to amostra
 *  even if real slipped true (never OVERCLAIM). TOTAL. */
function isGroundedReal(dual: PublicDualOutput): boolean {
  if (dual.real !== true) return false;
  const fm = dual.frontmatter as { grounding?: { approved?: unknown } } | undefined;
  if (fm && fm.grounding && fm.grounding.approved === false) return false;
  return true;
}

/** A human_html long enough to be a real document earns the "ver versao publicada"
 *  affordance; a short/empty string -> no iframe (degrade-never). */
const HUMAN_HTML_MIN_LEN = 200;

// --- one media element (read-only; src is ALWAYS pre-validated) --------------

function MediaEl({ kind, src, alt }: { kind: MediaKind; src: string; alt: string }) {
  if (kind === "video") {
    return (
      <video
        controls
        src={src}
        className="w-full rounded-card border border-border bg-secondary"
      />
    );
  }
  if (kind === "audio") {
    return <audio controls src={src} className="w-full" />;
  }
  // image (default). A plain <img> is correct here: the src is ALWAYS pre-validated
  // by isSafeMediaSrc (https:/data:) in normalizeSlots. next/image is not used
  // (arbitrary tenant CDN refs / data: URIs do not fit its domain allowlist).
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      className="w-full rounded-card border border-border bg-secondary object-contain"
    />
  );
}

/** One read-only slot card: shown media, or a static "midia indisponivel"
 *  placeholder (NO upload affordance -- this is the public read surface). */
function MediaSlotCard({ slot }: { slot: NormalSlot }) {
  return (
    <div className="space-y-2 rounded-card border border-border bg-card p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="min-w-0 truncate text-2xs font-medium uppercase tracking-wide text-muted-foreground">
          {slot.label}
        </span>
        <span className="chip shrink-0">{slot.kind}</span>
      </div>
      {slot.shown && slot.src ? (
        <MediaEl kind={slot.kind} src={slot.src} alt={slot.alt ?? slot.label} />
      ) : (
        <div className="flex flex-col items-center justify-center gap-1.5 rounded-card border border-dashed border-border bg-secondary px-4 py-7 text-center">
          <span className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
            midia indisponivel
          </span>
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------------------------------

export function DualOutputFacePublic({ dual }: { dual: PublicDualOutput }) {
  const [showHtml, setShowHtml] = useState(false);

  const slots = normalizeSlots(rawSlots(dual));
  const sections = dualSections(dual);
  const real = isGroundedReal(dual);
  const capability = String(dual.capability ?? "asset");
  const html = humanHtml(dual);
  const canShowHtml = html.trim().length >= HUMAN_HTML_MIN_LEN;

  // Degrade-never: an asset with nothing renderable -> render nothing.
  if (slots.length === 0 && sections.length === 0 && !canShowHtml) return null;

  return (
    <section className="animate-fade-in space-y-3 rounded-lg border border-border bg-secondary/40 p-4">
      {/* header: this is the published human face (read-only) */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="eyebrow">Face publicada</p>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {real ? (
            <span className="chip border-success/30 text-success">resultado real</span>
          ) : (
            <span className="chip border-destructive/30 text-destructive">amostra</span>
          )}
          <span className="chip">{capability}</span>
        </div>
      </div>

      {/* the typed structured body -- rendered from the contract, never raw HTML */}
      {sections.length > 0 && <StructuredSections sections={sections} />}

      {/* the media layer -- only safe-src slots render media; others are placeholders */}
      {slots.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {slots.map((s) => (
            <MediaSlotCard key={s.key} slot={s} />
          ))}
        </div>
      )}

      {/* human_html: TENANT-AUTHORED export string. Shown ONLY inside a SANDBOXED
          iframe (no allow-scripts) -- NEVER dangerouslySetInnerHTML on the live page.
          The sandbox with no allow-scripts blocks script, form submission, popups,
          and same-origin access from the tenant markup. */}
      {canShowHtml && (
        <div className="overflow-hidden rounded-lg border border-border">
          <button
            type="button"
            onClick={() => setShowHtml((v) => !v)}
            className="flex w-full items-center justify-between bg-secondary px-4 py-2 text-left transition-colors hover:bg-secondary"
          >
            <span className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
              versao publicada (HTML) -- isolada em sandbox
            </span>
            <span className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
              {showHtml ? "ocultar" : "ver"}
            </span>
          </button>
          {showHtml && (
            <iframe
              title="Versao publicada (sandbox)"
              srcDoc={html}
              sandbox=""
              className="h-[60vh] w-full border-0 bg-white"
            />
          )}
        </div>
      )}
    </section>
  );
}
