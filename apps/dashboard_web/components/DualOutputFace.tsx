"use client";

// ----------------------------------------------------------------------------
// DualOutputFace -- the HUMAN AUDIOVISUAL face of a dual-output asset (mission
// DASHBOARD_COMPOSITION W5; founder directive 2026-06-21).
//
// EVERY capability emits ONE asset with TWO coupled faces (cex_dual_output.py):
//   * MACHINE face -- the canonical .md + YAML frontmatter the tenant's AI reads.
//   * HUMAN face   -- this: the structured media rendered as a clickable preview
//                     (real <img>/<video>/<audio> when produced) PLUS an editable
//                     UPLOAD-FALLBACK dropzone where the pipeline produced nothing.
//
// The two faces share ONE id; a media slot is keyed by the SAME ``key`` on both
// (the human upload fills the machine ledger entry the AI reads -- the sync rule).
//
// This renders STRICTLY from the TYPED contract (media_slots), NOT
// dangerouslySetInnerHTML -- the backend's ``human_html`` is an export string, not
// the interactive surface. Safety + interactivity both demand the typed path.
//
// NEVER-FABRICATE: a slot renders a real media element ONLY when status ===
// "generated" AND a src is actually present; otherwise it is an editable upload
// dropzone (never a broken <img>). A human upload shows a CLIENT-SIDE preview
// (URL.createObjectURL) and is flagged "nao persistido ainda" -- writing back to
// the machine media[] ledger is a SEPARATE backend wire (W2 owns it), not faked here.
//
// DEGRADE-NEVER: a result without a dual_output asset never reaches this component
// (ResultView guards). A dual_output with no renderable surface -> renders nothing.
//
// ASCII-only + diacritic-free (the dashboard house style). Reuses the shared design
// tokens (border-line / bg-panel / chip / eyebrow / bg-ink-800) -- no new look.
// ----------------------------------------------------------------------------

import { useEffect, useRef, useState } from "react";
import type { MediaKind } from "@/lib/dual_output_contract";
import type { DualOutputResult, UploadedMedia } from "@/lib/types";
import { CheckIcon, PlusIcon } from "./icons";
import type { BrandTheme } from "@/lib/brandTheme";
import {
  buildCssVars,
  buildBrandHeaderHtml,
  buildProvenanceHtml,
  isSafeLogoSrc,
} from "@/lib/brandTheme";

/**
 * The client-side state of a slot the human just picked: a local preview + its PERSIST status.
 *   - "local"  -> no persist wire (read-only context): local preview, "nao persistido ainda".
 *   - "saving" -> the upload-persist wire (onUploadMedia) is in flight.
 *   - "saved"  -> the backend stored + persisted it (the slot is co-owned now).
 *   - "error"  -> the persist failed; the local preview is KEPT and the failure surfaced.
 */
interface SlotUpload {
  /** local object-URL preview (instant feedback, independent of persistence). */
  url: string;
  name: string;
  state: "local" | "saving" | "saved" | "error";
  /** the PERSISTED src returned by the wire (when state === "saved"). */
  src?: string;
  /** a human-readable failure (when state === "error"). */
  error?: string;
}

// --- normalize the raw emitter shape into the typed slots we render ----------
//
// The backend forwards the raw to_dual_output(...) dict (snake_case, flat):
// {id, capability, machine_md, human_html, media_slots, frontmatter, real}. We also
// accept an already-reshaped DualOutputContract ({machine:{md}, human:{mediaSlots}})
// so either projection round-trips. Both are read DEFENSIVELY (TOTAL, never throws).

const VALID_KINDS: readonly MediaKind[] = ["image", "video", "audio"];

function asKind(v: unknown): MediaKind {
  const k = String(v ?? "").toLowerCase();
  return (VALID_KINDS as readonly string[]).includes(k) ? (k as MediaKind) : "image";
}

/** Allowlist the scheme of a PRODUCED media src (anti-beacon / never-fabricate). A result src is
 *  attacker-influenceable, so permit only ``https:`` and ``data:image|video|audio`` -- an
 *  ``http:`` (mixed-content beacon), ``javascript:``, ``file:`` or any other scheme is dropped so
 *  the slot renders its empty/upload state instead of fetching a hostile URL. Total: never throws.
 *  (Client UPLOADS use blob: object URLs minted locally from a user-picked File -- that trusted
 *  path is separate from this and is not gated here.) */
function isSafeMediaSrc(src: string): boolean {
  const s = src.trim();
  if (/^https:\/\//i.test(s)) return true;
  if (/^data:(image|video|audio)\//i.test(s)) return true;
  return false;
}

// --- EXPORT-HTML helpers (mission DASHBOARD_COMPOSITION) ----------------
//
// The human face can be downloaded / opened as a standalone RENDERED html page (the
// founder wants to SEE the visual face, not the code). These are pure + total. The new
// tab is an origin-sandboxed separate document; no dangerouslySetInnerHTML is used here.

/** The affordance appears ONLY for a human_html long enough to be a real document. A thin
 *  placeholder (e.g. the fixtures stub for a data-only cap) yields no buttons -- degrade-never. */
const EXPORT_HTML_MIN_LEN = 200;

/** True when the string already opens a full HTML document (so we must NOT double-wrap it). */
function isFullHtmlDoc(html: string): boolean {
  const h = html.trimStart().toLowerCase();
  return h.startsWith("<!doctype") || h.startsWith("<html");
}

/** Wrap a bare human_html fragment in a standalone document, optionally injecting
 *  brand CSS vars into <head> and a brand header + provenance footer into <body>.
 *  A string that is ALREADY a full document (starts with <!doctype or <html) is
 *  returned UNTOUCHED -- no brand injection on pre-formed documents (degrade-never).
 *  Total: never throws. */
function wrapHtmlDocument(
  html: string,
  capability: string,
  theme?: BrandTheme,
  provenanceOpts?: { real: boolean; createdAt?: string },
): string {
  if (isFullHtmlDoc(html)) return html;
  const title = (capability || "asset").replace(/[<>&"]/g, " ").slice(0, 80);
  // Brand CSS vars: inject into <head> when tokens are present (cascades to the body).
  const cssVars = theme ? buildCssVars(theme) : "";
  const styleBlock = cssVars ? "<style>" + cssVars + "</style>" : "";
  // Brand header: prepended in <body> when the theme has a name or safe logo.
  const brandHeader = theme ? buildBrandHeaderHtml(theme) : "";
  // Provenance footer: always appended -- the HTML trust gap flagged in the audit.
  const provenance = buildProvenanceHtml({
    capability,
    real: provenanceOpts?.real ?? false,
    createdAt: provenanceOpts?.createdAt,
  });
  return (
    '<!doctype html><html lang="pt-br"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    "<title>" + title + "</title>" + styleBlock + "</head>" +
    "<body>" + brandHeader + html + provenance + "</body></html>"
  );
}

/** A safe download filename ``${capability}_${id}.html`` -- every unsafe character collapsed to
 *  "_", falling back to "asset.html" when both parts are empty. */
function safeFilename(capability: string, id?: string): string {
  const base = `${capability || ""}_${id || ""}`
    .replace(/[^A-Za-z0-9._-]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return `${base || "asset"}.html`;
}

/** A slot reduced to exactly what the renderer needs (never-fabricate enforced). */
interface NormalSlot {
  key: string;
  kind: MediaKind;
  /** true ONLY when the pipeline produced a real src (status generated + src present). */
  generated: boolean;
  src?: string;
  alt?: string;
  label: string;
}

/** Reduce the raw media_slots (unknown) into NormalSlot[], re-deriving the generated
 *  flag from an ACTUAL src so a mislabeled "generated" with no src degrades to empty. */
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
    const rawSrc =
      typeof o.src === "string" && o.src.trim() ? o.src.trim() : undefined;
    // Scheme allowlist: a produced src with an unsafe scheme (http:/javascript:/...) is dropped
    // -> the slot degrades to the empty/upload state, never beacons (anti-beacon, Fix 4).
    const src = rawSrc && isSafeMediaSrc(rawSrc) ? rawSrc : undefined;
    // NEVER-FABRICATE on the render side too: "generated" requires a real, safe-scheme src.
    const generated = String(o.status ?? "") === "generated" && !!src;
    const alt = typeof o.alt === "string" && o.alt.trim() ? o.alt.trim() : undefined;
    const label =
      (typeof o.label === "string" && o.label.trim() ? o.label.trim() : "") ||
      alt ||
      key;
    out.push({ key, kind, generated, src: generated ? src : undefined, alt, label });
  });
  return out;
}

/** The machine .md from either the flat emitter shape or a reshaped contract. */
function machineMd(dual: DualOutputResult): string {
  if (typeof dual.machine_md === "string") return dual.machine_md;
  const m = (dual as { machine?: { md?: unknown } }).machine;
  return m && typeof m.md === "string" ? m.md : "";
}

/** The raw media slots from either projection (flat media_slots | human.mediaSlots). */
function rawSlots(dual: DualOutputResult): unknown {
  if (Array.isArray(dual.media_slots)) return dual.media_slots;
  const h = (dual as { human?: { mediaSlots?: unknown } }).human;
  return h && Array.isArray(h.mediaSlots) ? h.mediaSlots : [];
}

/** The honest "resultado real vs amostra" determination behind the badge. Tied to the run's
 *  ``real`` flag (the backend sets it from the grounding verdict); an explicit frontmatter
 *  ``grounding.approved === false`` demotes it to "amostra" even if ``real`` slipped true, so
 *  the face never OVERCLAIMS a result that grounding did not approve. TOTAL: never throws. */
function isGroundedReal(dual: DualOutputResult): boolean {
  if (dual.real !== true) return false;
  const fm = dual.frontmatter as { grounding?: { approved?: unknown } } | undefined;
  if (fm && fm.grounding && fm.grounding.approved === false) return false;
  return true;
}

const ACCEPT: Record<MediaKind, string> = {
  image: "image/*",
  video: "video/*",
  audio: "audio/*",
};

const UPLOAD_PROMPT: Record<MediaKind, string> = {
  image: "Enviar imagem",
  video: "Enviar video",
  audio: "Enviar audio",
};

// --- one media element (a generated/uploaded asset) --------------------------

function MediaEl({
  kind,
  src,
  alt,
}: {
  kind: MediaKind;
  src: string;
  alt: string;
}) {
  if (kind === "video") {
    return (
      <video
        controls
        src={src}
        className="w-full rounded-card border border-line bg-ink-800"
      />
    );
  }
  if (kind === "audio") {
    return <audio controls src={src} className="w-full" />;
  }
  // image (default). next/image is intentionally NOT used: srcs here are data-URI
  // samples / object URLs / arbitrary tenant CDN refs, none of which fit the
  // next/image domain allowlist; a plain <img> is the correct, total surface.
  // The src reaching here is ALWAYS pre-validated: a produced src passed isSafeMediaSrc
  // (https:/data:) in normalizeSlots, or it is a locally-minted blob: upload URL.
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      className="w-full rounded-card border border-line bg-ink-800 object-contain"
    />
  );
}

// --- one slot card (generated/uploaded -> media + replace; empty -> dropzone) -

function SlotStatusBadge({ upload }: { upload?: SlotUpload }) {
  // No upload -> the asset came from the pipeline. Else reflect the persist lifecycle.
  if (!upload) {
    return (
      <span className="inline-flex items-center gap-1.5 font-mono text-2xs text-synapse">
        <CheckIcon width={13} height={13} /> gerado pelo pipeline
      </span>
    );
  }
  if (upload.state === "saving") {
    return (
      <span className="inline-flex items-center gap-1.5 font-mono text-2xs text-text-muted">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted" />
        enviando + persistindo...
      </span>
    );
  }
  if (upload.state === "saved") {
    return (
      <span className="inline-flex items-center gap-1.5 font-mono text-2xs text-synapse">
        <CheckIcon width={13} height={13} /> enviado e persistido
      </span>
    );
  }
  if (upload.state === "error") {
    return (
      <span
        className="inline-flex items-center gap-1.5 font-mono text-2xs text-danger"
        title={upload.error}
      >
        <span className="h-1.5 w-1.5 rounded-full bg-danger" />
        falha ao persistir -- previa local
      </span>
    );
  }
  // "local" -> no persist wire (read-only context): the original honest local-preview state.
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-2xs text-signal">
      <span className="h-1.5 w-1.5 rounded-full bg-signal" />
      previa local -- nao persistido ainda
    </span>
  );
}

function MediaSlotCard({
  slot,
  upload,
  onPick,
}: {
  slot: NormalSlot;
  upload?: SlotUpload;
  onPick: (key: string, file: File | null | undefined) => void;
}) {
  const [dragOver, setDragOver] = useState(false);
  // The effective media: a PERSISTED src wins, else the local preview, else the produced src.
  const shownSrc = upload?.src ?? upload?.url ?? slot.src;
  const isShown = !!shownSrc && (slot.generated || !!upload);

  return (
    <div className="space-y-2 rounded-card border border-line bg-panel p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="min-w-0 truncate font-mono text-2xs uppercase tracking-wider text-text-faint">
          {slot.label}
        </span>
        <span className="chip shrink-0">{slot.kind}</span>
      </div>

      {isShown && shownSrc ? (
        <div className="space-y-2">
          <MediaEl kind={slot.kind} src={shownSrc} alt={slot.alt ?? slot.label} />
          <div className="flex flex-wrap items-center justify-between gap-2">
            <SlotStatusBadge upload={upload} />
            {/* every slot is editable -- a generated/persisted asset also offers replace */}
            <label className="cursor-pointer font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse">
              <input
                type="file"
                accept={ACCEPT[slot.kind]}
                className="hidden"
                onChange={(e) => onPick(slot.key, e.target.files?.[0])}
              />
              trocar
            </label>
          </div>
        </div>
      ) : (
        // EMPTY -> editable upload-fallback dropzone (no src, no broken media tag).
        <label
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            onPick(slot.key, e.dataTransfer.files?.[0]);
          }}
          className={[
            "flex cursor-pointer flex-col items-center justify-center gap-1.5 rounded-card border-2 border-dashed px-4 py-7 text-center transition-colors",
            dragOver
              ? "border-synapse/60 bg-synapse/[0.06]"
              : "border-line bg-panel-sunken hover:border-synapse/40",
          ].join(" ")}
        >
          <input
            type="file"
            accept={ACCEPT[slot.kind]}
            className="hidden"
            onChange={(e) => onPick(slot.key, e.target.files?.[0])}
          />
          <span className="text-text-faint">
            <PlusIcon width={18} height={18} />
          </span>
          <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
            {UPLOAD_PROMPT[slot.kind]}
          </span>
          <span className="font-mono text-2xs text-text-faint">
            slot vazio -- arraste ou clique para enviar
          </span>
        </label>
      )}
    </div>
  );
}

// ----------------------------------------------------------------------------

export function DualOutputFace({
  dual,
  recordId,
  onUploadMedia,
  brandTheme,
}: {
  dual: DualOutputResult;
  /** the persisted record id (POST /capability/run record_id). With onUploadMedia present, a
   *  human upload PERSISTS through the wire; absent -> the upload is a local preview only. */
  recordId?: string;
  /** the upload-persist wire: store + persist a file into a slot, returning the filled slot.
   *  Omitted (read-only context) -> the face still accepts uploads but keeps them local (honest). */
  onUploadMedia?: (slotKey: string, file: File) => Promise<UploadedMedia>;
  /** Optional tenant brand theme. When provided, the component shows a brand header
   *  (logo + name + tagline) and the exported HTML is themed with brand CSS vars +
   *  brand header + provenance footer. Absent -> neutral look unchanged (degrade-never). */
  brandTheme?: BrandTheme;
}) {
  const slots = normalizeSlots(rawSlots(dual));
  const md = machineMd(dual);
  // The amostra-vs-real badge is tied to the grounding verdict (never the bare flag alone).
  const real = isGroundedReal(dual);
  const capability = String(dual.capability ?? "asset");
  // EXPORT-HTML: the human face is exportable when its human_html is a real document
  // (long enough). A missing/short string -> no export affordance (degrade-never).
  const humanHtml = typeof dual.human_html === "string" ? dual.human_html : "";
  const canExport = humanHtml.trim().length >= EXPORT_HTML_MIN_LEN;

  // Provenance opts for the export wrapper (extracted once from the dual frontmatter).
  const provenanceOpts = {
    real,
    createdAt:
      typeof dual.frontmatter?.created === "string"
        ? dual.frontmatter.created
        : typeof dual.frontmatter?.generated_at === "string"
          ? dual.frontmatter.generated_at
          : undefined,
  };

  const [uploads, setUploads] = useState<Record<string, SlotUpload>>({});
  const [showMachine, setShowMachine] = useState(false);
  const [copied, setCopied] = useState(false);
  // Track every object URL we mint so we can revoke them on unmount (no leak).
  const createdUrls = useRef<string[]>([]);

  useEffect(() => {
    return () => {
      for (const u of createdUrls.current) URL.revokeObjectURL(u);
      createdUrls.current = [];
    };
  }, []);

  // The persist wire is live only when BOTH a record id and the upload callback are present.
  const canPersist = !!recordId && !!onUploadMedia;

  async function onPick(key: string, file: File | null | undefined) {
    if (!file) return;
    const url = URL.createObjectURL(file);
    createdUrls.current.push(url);
    // 1) optimistic local preview (instant). state = saving (wire live) | local (read-only).
    setUploads((prev) => {
      const prevUrl = prev[key]?.url;
      if (prevUrl) {
        URL.revokeObjectURL(prevUrl);
        createdUrls.current = createdUrls.current.filter((u) => u !== prevUrl);
      }
      return {
        ...prev,
        [key]: { url, name: file.name, state: canPersist ? "saving" : "local" },
      };
    });
    if (!canPersist || !onUploadMedia) return;
    // 2) persist through the wire; on success flip to saved (carry the persisted src), else error.
    try {
      const res = await onUploadMedia(key, file);
      const persistedSrc =
        res.slot && typeof res.slot.src === "string" && res.slot.src
          ? res.slot.src
          : undefined;
      setUploads((prev) => ({
        ...prev,
        [key]: { ...prev[key], state: "saved", src: persistedSrc ?? prev[key]?.url },
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "falha ao persistir o upload";
      setUploads((prev) => ({
        ...prev,
        [key]: { ...prev[key], state: "error", error: message },
      }));
    }
  }

  async function copyMd() {
    try {
      await navigator.clipboard.writeText(md);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked -- ignore */
    }
  }

  // EXPORT-HTML: download the human face as a standalone .html file (client-side Blob).
  // Total + degrade-never: a failure is swallowed, the rest of the face is untouched.
  // Brand theming + provenance footer are injected when brandTheme is present.
  function exportHtml() {
    if (!canExport) return;
    try {
      const doc = wrapHtmlDocument(humanHtml, capability, brandTheme, provenanceOpts);
      const url = URL.createObjectURL(new Blob([doc], { type: "text/html" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = safeFilename(
        capability,
        typeof dual.id === "string" ? dual.id : undefined,
      );
      document.body.appendChild(a);
      a.click();
      a.remove();
      // revoke on the next tick -- after the download has been kicked off.
      setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch {
      /* export blocked -- ignore */
    }
  }

  // EXPORT-HTML: open the same page RENDERED in a new tab (blob: URL, text/html) so the
  // founder immediately SEES the visual face. The object URL is revoked on unmount (by then
  // the new tab has already loaded the document).
  function openHtml() {
    if (!canExport) return;
    try {
      const doc = wrapHtmlDocument(humanHtml, capability, brandTheme, provenanceOpts);
      const url = URL.createObjectURL(new Blob([doc], { type: "text/html" }));
      createdUrls.current.push(url);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch {
      /* popup blocked -- ignore */
    }
  }

  // Degrade-never: a dual_output with neither media slots nor a machine face -> render nothing.
  if (slots.length === 0 && !md) return null;

  return (
    <section className="animate-fade-in space-y-3 rounded-lg border border-line bg-panel-sunken/40 p-4">
      {/* BRAND HEADER: shown when a brandTheme with name/logo is provided. Uses inline
          styles (not Tailwind) since the values come from runtime token data. Degrade-never:
          absent or empty theme -> this block is not rendered (unchanged look). */}
      {brandTheme && (brandTheme.name || (brandTheme.logo && isSafeLogoSrc(brandTheme.logo))) && (
        <div
          style={{
            background: `hsl(${brandTheme.tokens?.primary ?? "220 90% 50%"})`,
            color: `hsl(${brandTheme.tokens?.primaryForeground ?? "0 0% 100%"})`,
            borderRadius: brandTheme.tokens?.radius ?? "0.5rem",
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            marginBottom: "2px",
          }}
        >
          {brandTheme.logo && isSafeLogoSrc(brandTheme.logo) && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={brandTheme.logo}
              alt={brandTheme.logoAlt ?? brandTheme.name ?? "logo"}
              style={{ height: "30px", objectFit: "contain", maxWidth: "140px" }}
            />
          )}
          {brandTheme.name && (
            <div>
              <span style={{ fontWeight: 700, fontSize: "15px", lineHeight: 1.2 }}>
                {brandTheme.name}
              </span>
              {brandTheme.tagline && (
                <span
                  style={{
                    display: "block",
                    fontSize: "11px",
                    opacity: 0.85,
                    marginTop: "2px",
                  }}
                >
                  {brandTheme.tagline}
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* header: this is the human, editable, audiovisual face */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="eyebrow normal-case text-text-muted">
          // face audiovisual (humana, editavel)
        </p>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {real ? (
            <span className="chip border-synapse/30 text-synapse">resultado real</span>
          ) : (
            <span className="chip border-danger/30 text-danger">dados simulados</span>
          )}
          <span className="chip">{capability}</span>
          {/* EXPORT-HTML: download / open the human face as a standalone rendered page.
              Shown ONLY when human_html is a real document (degrade-never). */}
          {canExport && (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={exportHtml}
                title="Baixar a face humana como um arquivo .html standalone"
                className="inline-flex items-center gap-1.5 rounded-card border border-line bg-panel px-2.5 py-1 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:border-synapse/40 hover:text-synapse"
              >
                Exportar HTML
              </button>
              <button
                type="button"
                onClick={openHtml}
                title="Abrir a face humana renderizada em uma nova aba"
                className="inline-flex items-center gap-1.5 rounded-card border border-line bg-panel px-2.5 py-1 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:border-synapse/40 hover:text-synapse"
              >
                Abrir
              </button>
            </div>
          )}
        </div>
      </div>

      <p className="font-mono text-2xs leading-relaxed text-text-faint">
        Um asset, duas faces co-editaveis com o MESMO id: esta face HUMANA (audiovisual,
        editavel{canExport ? " -- Exportar HTML / Abrir" : ""}) e a face MAQUINA (.md/YAML
        que a IA do tenant le e opera, abaixo). Slot gerado pelo pipeline aparece como midia
        real; slot vazio vira campo de upload -- voce edita o visual, a IA opera o .md.
      </p>

      {/* the media layer -- the human audiovisual face built from the typed slots */}
      {slots.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {slots.map((s) => (
            <MediaSlotCard
              key={s.key}
              slot={s}
              upload={uploads[s.key]}
              onPick={onPick}
            />
          ))}
        </div>
      )}

      {/* the coupled MACHINE face -- collapsible .md/YAML the tenant's AI reads */}
      {md && (
        <div className="overflow-hidden rounded-lg border border-line">
          <button
            onClick={() => setShowMachine((v) => !v)}
            className="flex w-full items-center justify-between bg-panel-sunken px-4 py-2 text-left transition-colors hover:bg-panel"
          >
            <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              face maquina -- .md/YAML (a IA do tenant opera)
            </span>
            <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
              {showMachine ? "ocultar" : "ver"}
            </span>
          </button>
          {showMachine && (
            <div>
              <div className="flex items-center justify-between border-t border-line bg-panel-sunken px-4 py-2">
                <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                  machine_md (face maquina)
                </span>
                <button
                  onClick={copyMd}
                  className="font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
                >
                  {copied ? "copied" : "copy"}
                </button>
              </div>
              <pre className="max-h-[36vh] overflow-auto bg-ink-800 px-4 py-3 font-mono text-xs leading-relaxed text-text-muted">
                {md}
              </pre>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
