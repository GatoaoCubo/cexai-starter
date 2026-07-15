"use client";

// ----------------------------------------------------------------------------
// DetailView -- the PRODUCT PDP page body (client component; fetch through
// PublicApiClient so fixtures mode works in tests).
//
// THE DEGRADE-TO-LIST PATTERN (unchanged): the public API has NO get-by-id endpoint
// (only /public/catalog). So the PDP RE-FETCHES /public/catalog for (slug, kind) and
// matches the row by id -- the SAME pattern the dashboard uses for its results deep-link.
// It is NOT an invented route.
//
// The PDP is now a real storefront product page built from the OPEN published payload:
//   * a media GALLERY (MediaGallery -- EVERY image URL gated by isSafeMediaSrc);
//   * the title + price + description (brandText pickers, rendered as TEXT);
//   * a SPECS / attributes block (scalar rows from the payload);
//   * the dual-output FACE (DualOutputFacePublic -- typed sections + sandboxed iframe).
// A "ver/comprar" CTA links OUT to an external buy URL when the payload carries a safe
// one -- it NEVER builds a fake cart/checkout (that is the separate commerce concern).
//
// SECURITY: the no-leak gate (a miss -> NotFound), the media scheme allowlist (gallery +
// dual face), the sandboxed iframe (no allow-scripts), and the auth-free client are ALL
// preserved. Payload strings are rendered as text only (never dangerouslySetInnerHTML).
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import { useEffect, useState } from "react";
import { BrandLayout } from "@/components/BrandLayout";
import { NotFound } from "@/components/NotFound";
import { MediaGallery } from "@/components/MediaGallery";
import { MobileBuyBar } from "@/components/MobileBuyBar";
import { RatingRow, ReviewsBand } from "@/components/Rating";
import { Skeleton } from "@/components/Skeleton";
import { TrustRow } from "@/components/TrustRow";
import {
  DualOutputFacePublic,
  type PublicDualOutput,
} from "@/components/DualOutputFacePublic";
import { ArrowRightIcon } from "@/components/icons";
import { isSafeMediaSrc } from "@/lib/mediaSafety";
import {
  descriptionOf,
  galleryCandidates,
  priceOf,
  publishedDate,
  ratingOf,
  reviewsOf,
  specRows,
  titleOf,
} from "@/lib/brandText";
import { publicApi, ApiClientError } from "@/lib/publicApi";
import { isValidKind, isValidSlug } from "@/lib/slug";
import { imageryFor } from "@/lib/tenantImagery";
import type { PublicCatalogItem, PublicTenantInfo } from "@/lib/types";

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo; item: PublicCatalogItem }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

/**
 * Build the PublicDualOutput the read-only face renders from a published item. Prefers
 * the item's own ``dual_output`` asset; otherwise synthesizes one from the item's typed
 * ``sections`` + ``human_html`` so a plain published payload still gets a structured +
 * (sandboxed) HTML render. TOTAL.
 */
function toDualOutput(item: PublicCatalogItem): PublicDualOutput {
  const asset = item.dual_output;
  if (asset && typeof asset === "object") return asset as PublicDualOutput;
  const dual: PublicDualOutput = {
    id: item.id,
    capability: item.kind,
    real: item.real === true,
  };
  if (Array.isArray(item.sections)) dual.sections = item.sections;
  if (typeof item.human_html === "string") dual.human_html = item.human_html;
  return dual;
}

/** Pick a SAFE external buy/CTA URL from the payload, or '' (never a fake checkout). */
function buyUrlOf(item: PublicCatalogItem): string {
  for (const k of ["buy_url", "url", "link", "permalink", "product_url", "comprar_url"]) {
    const v = item[k];
    // Only an https: link leaves the site; anything else is dropped (no unsafe scheme).
    if (typeof v === "string" && /^https:\/\//i.test(v.trim())) return v.trim();
  }
  return "";
}

export function DetailView({
  slug,
  kind,
  id,
}: {
  slug: string;
  kind: string;
  id: string;
}) {
  const [state, setState] = useState<LoadState>({ phase: "loading" });

  useEffect(() => {
    let alive = true;
    if (!isValidSlug(slug) || !isValidKind(kind) || !id) {
      setState({ phase: "notfound" });
      return;
    }
    setState({ phase: "loading" });
    Promise.all([publicApi.getTenantInfo(slug), publicApi.getCatalog(slug, kind)])
      .then(([info, catalog]) => {
        if (!alive) return;
        if (!info || !catalog) {
          setState({ phase: "notfound" });
          return;
        }
        // degrade-to-list: match the row by id (no get-by-id endpoint exists).
        const item = (catalog.items ?? []).find((it) => it.id === id);
        setState(item ? { phase: "ready", info, item } : { phase: "notfound" });
      })
      .catch((err: unknown) => {
        if (!alive) return;
        const message =
          err instanceof ApiClientError ? err.message : "Nao foi possivel carregar.";
        setState({ phase: "error", message });
      });
    return () => {
      alive = false;
    };
  }, [slug, kind, id]);

  if (state.phase === "loading") {
    // content-shaped skeleton (gallery plate + buy-box) -- mirrors the PDP layout
    // while the catalog re-fetch resolves; pulse auto-disabled by reduced-motion.
    return (
      <div className="shell py-12">
        <Skeleton.Pdp />
      </div>
    );
  }

  if (state.phase === "notfound") {
    return <NotFound message="Este item nao existe ou nao esta publicado." />;
  }

  if (state.phase === "error") {
    return (
      <div className="flex min-h-screen items-center justify-center px-5">
        <div className="w-full max-w-md space-y-3 rounded-card border border-border bg-card p-8 text-center shadow-sm">
          <p className="eyebrow">erro</p>
          <p className="text-sm text-muted-foreground">{state.message}</p>
        </div>
      </div>
    );
  }

  const { info, item } = state;
  const title = titleOf(item);
  const price = priceOf(item);
  const description = descriptionOf(item);
  const specs = specRows(item);
  const gallery = galleryCandidates(item);
  const hasSafeGallery = gallery.some((c) => isSafeMediaSrc(c));
  // WHITE-LABEL decorative fallback for the no-safe-image gallery placeholder. A photo
  // tenant (demo-acme) keeps its first-party /images/cat-product.jpg tile (zero-regression);
  // ANY other tenant paints a brand-gradient tile -- no cat-leak. Mirrors the HomeView/
  // BlogView/B2BView treatment so the PDP never leaks the built-in sample's cat photo.
  const imagery = imageryFor(info.slug);
  const cardFallback = imagery.mode === "photos" ? imagery.cardFallback : "";
  // services tenant (kind=service) has NO checkout -> suppress the BR-commerce trust row
  // (PIX/parcelamento/12x/troca), the same guard HomeView + BrandFooter already apply.
  // Avoids a false commerce claim on a non-retail tenant; demo-acme (retail) keeps it.
  const isServiceVertical = item.kind === "service";
  const buyUrl = buyUrlOf(item);
  const dual = toDualOutput(item);
  const published = publishedDate(item);
  // HONEST-EMPTY: a rating row + reviews band ONLY when the payload actually carries
  // them (ratingOf -> null when absent -> render nothing; reviewsOf -> [] when absent).
  const rating = ratingOf(item);
  const reviews = reviewsOf(item);
  const catalogHref = `/t/${encodeURIComponent(info.slug)}/${encodeURIComponent(item.kind)}`;
  // the in-page CTA id the mobile sticky bar watches (hides the bar while on screen).
  const BUY_CTA_ID = "pdp-buy-cta";

  return (
    <BrandLayout brand={info.brand} slug={info.slug} active="catalog" activeKind={item.kind}>
      {/* breadcrumb */}
      <nav aria-label="Trilha" className="mb-8 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <Link href={`/t/${encodeURIComponent(info.slug)}`} className="transition-colors duration-fast hover:text-foreground">
          Inicio
        </Link>
        <span aria-hidden="true" className="text-border">/</span>
        <Link href={catalogHref} className="transition-colors duration-fast hover:text-foreground">
          {item.kind}
        </Link>
        <span aria-hidden="true" className="text-border">/</span>
        <span className="truncate font-medium text-foreground">{title}</span>
      </nav>

      {/* ---- PRODUCT HEAD: gallery + buy-box (48px gap, design_system.md s4) -------- */}
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-12">
        <div>
          {hasSafeGallery ? (
            <MediaGallery candidates={gallery} alt={title} />
          ) : cardFallback ? (
            // photo tenant (demo-acme): honest first-party fallback photo (same-origin
            // /images -- NOT tenant-payload media, so not gated by isSafeMediaSrc).
            <div className="group relative aspect-square overflow-hidden rounded-card border border-border bg-secondary shadow-sm">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={cardFallback}
                alt=""
                aria-hidden="true"
                className="h-full w-full object-cover opacity-95 transition-transform duration-slow ease-emphasized group-hover:scale-[1.04]"
              />
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-card ring-1 ring-inset ring-foreground/5"
              />
            </div>
          ) : (
            // WHITE-LABEL brand-gradient tile: a non-photo tenant paints a
            // brand-color panel from its own --brand/--foreground tokens (no cat-leak),
            // the SAME treatment HomeView/BlogView/B2BView use for their decorative art.
            <div
              aria-hidden="true"
              className="aspect-square rounded-card border border-border shadow-sm"
              style={{
                background:
                  "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
              }}
            />
          )}
        </div>

        {/* the buy-box: a framed panel, sticky on desktop so it stays in view on scroll */}
        <div className="lg:sticky lg:top-24 lg:self-start">
          <div className="space-y-6 lg:rounded-card lg:border lg:border-border lg:bg-card lg:p-7 lg:shadow-md">
            <div className="space-y-3">
              <p className="eyebrow">{item.kind}</p>
              <h1 className="break-words font-display text-h1 leading-tight text-foreground">
                {title}
              </h1>
              {/* HONEST-EMPTY rating row (renders nothing when the payload has no rating). */}
              <RatingRow rating={rating} />
              {published && (
                <p className="text-sm text-muted-foreground">publicado {published}</p>
              )}
            </div>

            {price && (
              <div className="flex items-baseline gap-2">
                <span className="font-display text-display font-bold leading-none text-brand">
                  {price}
                </span>
              </div>
            )}

            {description && (
              <p className="text-lg leading-relaxed text-muted-foreground">{description}</p>
            )}

            {/* CTA: links OUT to an external buy URL when present. NEVER a fake checkout
                -- cart/payments are the separate commerce concern. Opens in a new tab,
                rel-hardened (noopener noreferrer nofollow). */}
            {buyUrl ? (
              <a
                id={BUY_CTA_ID}
                href={buyUrl}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="btn-brand btn-lg w-full justify-center"
              >
                Ver / comprar
                <ArrowRightIcon />
              </a>
            ) : (
              <Link href={catalogHref} className="btn-outline btn-lg w-full justify-center">
                Voltar ao catalogo
              </Link>
            )}

            {/* PT-BR trust row (monochrome) -- NOT for a services tenant (no checkout) */}
            {!isServiceVertical && <TrustRow className="border-t border-border pt-6" />}

            {/* specs / attributes */}
            {specs.length > 0 && (
              <div className="space-y-3 rounded-card border border-border bg-background/60 p-5">
                <p className="eyebrow">Especificacoes</p>
                <dl className="divide-y divide-border">
                  {specs.map((s) => (
                    <div key={s.label} className="flex items-baseline justify-between gap-4 py-2.5">
                      <dt className="text-sm font-medium text-muted-foreground">{s.label}</dt>
                      <dd className="text-right text-sm font-medium text-foreground">{s.value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ---- the dual-output published face (typed sections + sandboxed iframe) ---- */}
      <div className="mt-16">
        <DualOutputFacePublic dual={dual} />
      </div>

      {/* ---- optional REVIEWS band (renders NOTHING when the payload has no reviews) - */}
      <ReviewsBand reviews={reviews} />

      {/* ---- back-to-catalog tail (quiet, always present) ------------------------- */}
      <div className="mt-12 border-t border-border pt-8">
        <Link
          href={catalogHref}
          className="group inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors duration-fast hover:text-foreground"
        >
          <span className="transition-transform duration-base ease-emphasized group-hover:-translate-x-1">
            <ArrowRightIcon className="rotate-180" />
          </span>
          Voltar para {item.kind}
        </Link>
      </div>

      {/* ---- MOBILE sticky buy CTA (lg:hidden). Mirrors the external buy_url; hides
           while the in-page CTA is on screen (IntersectionObserver). Only when buyUrl. */}
      {buyUrl && <MobileBuyBar buyUrl={buyUrl} watchId={BUY_CTA_ID} />}
    </BrandLayout>
  );
}
