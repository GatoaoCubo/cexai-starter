"use client";

// ----------------------------------------------------------------------------
// MediaGallery -- a READ-ONLY product image gallery for the PDP (main image +
// thumbnail strip). CLIENT component (it tracks the selected thumbnail).
//
// SECURITY (the load-bearing line): the gallery receives URL CANDIDATES from the open
// published payload (brandText.galleryCandidates) -- those are tenant-controlled and
// forwarded VERBATIM by the backend. EVERY candidate is gated by isSafeMediaSrc (https:
// | data:image|video|audio) HERE before it ever becomes an <img src>. An unsafe scheme
// (javascript:, http:, data:text/html, file:, ...) is DROPPED -- it never renders a tag
// and never fetches a hostile URL. A plain <img> is correct: the src is always
// pre-validated (next/image is not used -- arbitrary tenant CDN refs / data: URIs do not
// fit its domain allowlist; same rationale as DualOutputFacePublic.MediaEl).
//
// DEGRADE-NEVER + TOTAL: zero safe candidates -> renders nothing (the PDP falls back to
// its other surfaces). Never throws.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { useState } from "react";
import type { SyntheticEvent } from "react";
import { isSafeMediaSrc } from "@/lib/mediaSafety";

export function MediaGallery({
  candidates,
  alt,
}: {
  /** raw URL candidates from the payload (UNVALIDATED -- gated here). */
  candidates: readonly string[];
  /** accessible alt text for the images (the product title). */
  alt: string;
}) {
  // The scheme allowlist: keep ONLY safe-src candidates. Tenant-controlled input, so this
  // is the security boundary for the gallery.
  const safe = (candidates ?? []).filter((c) => isSafeMediaSrc(c));
  const [active, setActive] = useState(0);
  // Per-candidate object-fit: default "contain" (letterbox, the safe choice for an
  // unknown ratio); switch to "cover" ONLY for a near-square photo (within ~10% of
  // 1:1) so square product shots fill the plate edge-to-edge instead of being framed
  // by grey bars, while extreme ratios (banners / tall posters) stay un-cropped.
  const [fits, setFits] = useState<Record<number, "cover" | "contain">>({});

  // Degrade-never: nothing safe to show -> render nothing.
  if (safe.length === 0) return null;

  const activeIdx = Math.min(active, safe.length - 1);
  const current = safe[activeIdx];
  const label = (alt || "Imagem do produto").slice(0, 120);
  const currentFit = fits[activeIdx] ?? "contain";

  // On load, read the image's NATURAL dimensions and decide cover vs contain. A
  // ratio within 10% of square gets object-cover (fills the 1:1 plate); anything
  // more extreme keeps the safe object-contain default. PURE: only sets local state.
  const onImgLoad = (idx: number) => (e: SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    const w = img.naturalWidth;
    const h = img.naturalHeight;
    if (!w || !h) return; // unknown (e.g. some data: SVGs) -> keep contain default.
    const ratio = w / h;
    const nearSquare = ratio >= 0.9 && ratio <= 1.1;
    setFits((prev) =>
      prev[idx] === (nearSquare ? "cover" : "contain")
        ? prev
        : { ...prev, [idx]: nearSquare ? "cover" : "contain" },
    );
  };

  return (
    <div className="space-y-3">
      <div className="group relative aspect-square overflow-hidden rounded-card border border-border bg-secondary shadow-sm">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={current}
          alt={label}
          onLoad={onImgLoad(activeIdx)}
          className={[
            "h-full w-full bg-secondary transition-transform duration-slow ease-emphasized group-hover:scale-[1.04]",
            currentFit === "cover" ? "object-cover" : "object-contain",
          ].join(" ")}
        />
        {/* a hairline inner ring for a premium "framed" plate (purely decorative). */}
        <span
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 rounded-card ring-1 ring-inset ring-foreground/5"
        />
      </div>

      {safe.length > 1 && (
        <div className="flex flex-wrap gap-2.5" role="list" aria-label="Miniaturas">
          {safe.map((src, i) => {
            const isActive = i === Math.min(active, safe.length - 1);
            return (
              <button
                key={src + i}
                type="button"
                role="listitem"
                aria-label={`Imagem ${i + 1}`}
                aria-current={isActive ? "true" : undefined}
                aria-pressed={isActive}
                onClick={() => setActive(i)}
                className={[
                  "h-16 w-16 shrink-0 overflow-hidden rounded-md border bg-secondary transition-all duration-base ease-standard",
                  isActive
                    ? "border-brand ring-2 ring-brand/40 ring-offset-1 ring-offset-background"
                    : "border-border opacity-70 hover:-translate-y-0.5 hover:border-foreground/30 hover:opacity-100",
                ].join(" ")}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt="" className="h-full w-full object-cover" />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
