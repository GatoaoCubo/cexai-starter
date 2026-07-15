// ----------------------------------------------------------------------------
// CatalogCard -- one published catalog item as a premium product card linking to its
// detail (PDP). SERVER-SAFE presentational (no hooks, no client state).
//
// Mirrors the reference retail ProductCard pattern (design_system.md): a 1:1 image area with a
// subtle zoom on hover, the brand accent reserved for the price + the hover ring, a
// kind badge, and the title/summary. TYPED render of the OPEN payload via the shared
// brandText pickers -- it NEVER assumes a field exists (an absent field simply does not
// render) and NEVER injects payload HTML (no dangerouslySetInnerHTML; strings render as
// text).
//
// SECURITY: a thumbnail renders ONLY when the payload carries a SAFE image URL
// (isSafeMediaSrc) -- a tenant-controlled, verbatim-forwarded field, scheme-gated here.
// The decorative cat tile fallback is a FIRST-PARTY same-origin asset (not tenant media).
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import type { PublicCatalogItem } from "@/lib/types";
import { galleryCandidates, priceOf, summaryOf, titleOf } from "@/lib/brandText";
import { isSafeMediaSrc } from "@/lib/mediaSafety";
import { ArrowRightIcon } from "./icons";

export function CatalogCard({
  item,
  slug,
  /** the tenant's decorative card-fallback photo (a same-origin "/images/..." path), or ''
   *  when the tenant ships NO photos -> a brand-gradient tile is painted instead (no cat
   *  leak, no fabricated stock). Defaults to '' (the white-label brand treatment). */
  cardFallback = "",
}: {
  item: PublicCatalogItem;
  slug: string;
  cardFallback?: string;
}) {
  const title = titleOf(item);
  const summary = summaryOf(item);
  const price = priceOf(item);
  // SAFE image candidates -> the product images (scheme-gated; unsafe/absent dropped).
  // EVERY candidate (incl the 2nd hover-swap image) passes isSafeMediaSrc HERE before
  // it can become an <img src> -- the same security boundary as the gallery.
  const safeImgs = galleryCandidates(item).filter((c) => isSafeMediaSrc(c));
  const thumb = safeImgs[0] ?? "";
  // a 2nd safe image enables the hover-swap overlay (fades in on group-hover).
  const hoverThumb = safeImgs.length >= 2 ? safeImgs[1] : "";
  const href = `/t/${encodeURIComponent(slug)}/${encodeURIComponent(item.kind)}/${encodeURIComponent(item.id)}`;

  return (
    <Link
      href={href}
      className="group flex h-full flex-col overflow-hidden rounded-card border border-border bg-card shadow-sm transition-all duration-base ease-standard hover:-translate-y-1 hover:border-brand/40 hover:shadow-lg"
    >
      {/* 1:1 image area (design_system.md s11.8) */}
      <div className="relative aspect-square overflow-hidden bg-secondary">
        {thumb ? (
          <>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={thumb}
              alt={title}
              className="h-full w-full object-cover transition-transform duration-slow ease-emphasized group-hover:scale-[1.05]"
            />
            {/* 2nd-image hover swap: a second SAFE image (isSafeMediaSrc-gated above)
                fades in over the first on group-hover. prefers-reduced-motion keeps
                it from animating (global rule clamps the transition); object-cover
                preserved. Decorative -> aria-hidden (the primary img carries alt). */}
            {hoverThumb && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={hoverThumb}
                alt=""
                aria-hidden="true"
                className="absolute inset-0 h-full w-full object-cover opacity-0 transition-opacity duration-base ease-standard group-hover:opacity-100"
              />
            )}
          </>
        ) : cardFallback ? (
          // first-party decorative fallback (same-origin /images photo -- NOT tenant
          // media, so not subject to isSafeMediaSrc which gates tenant-PAYLOAD media).
          // Provided per-tenant: demo-acme passes its cat tile; a tenant with no photos
          // passes '' and gets the brand-gradient tile below (no cat leak).
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={cardFallback}
            alt=""
            aria-hidden="true"
            className="h-full w-full object-cover opacity-95 transition-transform duration-slow ease-emphasized group-hover:scale-[1.05]"
          />
        ) : (
          // WHITE-LABEL brand-gradient tile: no tenant photo -> a brand-color panel built
          // from the tenant's own --brand / --foreground tokens. No cats, no fake stock.
          <div
            aria-hidden="true"
            className="h-full w-full transition-transform duration-slow ease-emphasized group-hover:scale-[1.05]"
            style={{
              background:
                "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
            }}
          />
        )}
        {/* a soft veil that deepens on hover -- lifts the image from flat to premium. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-foreground/10 to-transparent opacity-0 transition-opacity duration-base group-hover:opacity-100"
        />
        <span
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-foreground/5"
        />
      </div>

      <div className="flex flex-1 flex-col gap-2 p-5">
        <p className="min-w-0 break-words font-display text-h3 font-semibold leading-tight tracking-tight text-foreground transition-colors duration-fast group-hover:text-brand">
          {title}
        </p>

        {summary && (
          <p className="line-clamp-2 text-sm leading-relaxed text-muted-foreground">{summary}</p>
        )}

        <div className="mt-auto flex items-center justify-between gap-3 pt-3">
          {price ? (
            <span className="font-display text-lg font-bold text-brand">{price}</span>
          ) : (
            <span className="chip">{item.kind}</span>
          )}
          <span className="inline-flex items-center gap-1 text-sm font-medium text-muted-foreground transition-colors duration-fast group-hover:text-brand">
            Ver
            <span className="transition-transform duration-base ease-emphasized group-hover:translate-x-0.5">
              <ArrowRightIcon />
            </span>
          </span>
        </div>
      </div>
    </Link>
  );
}
