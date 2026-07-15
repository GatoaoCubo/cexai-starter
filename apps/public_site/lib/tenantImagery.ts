// ----------------------------------------------------------------------------
// tenantImagery -- the WHITE-LABEL decorative-imagery layer, DERIVED from the single
// source-of-truth (lib/tenantConfig).
//
// THE PROBLEM this fixes: the storefront's decorative HERO + section + card-fallback art
// used to be HARD-CODED built-in-sample CAT photos ("/images/cat-hero.jpg", ...). On a white-label
// storefront that is a brand LEAK: a non-cat tenant (e.g. an IT-services company) must
// NEVER show cat photos. The published payload + brand contract carry NO decorative
// photography, so the tenant's ``shape.imagery_mode`` + ``imagery`` paths in tenantConfig
// decide the treatment:
//
//   * a tenant that SHIPS first-party photos (demo-acme keeps its /images/cat-*.jpg) ->
//     a ``photos`` treatment: the components paint those same-origin photos exactly as
//     before (ZERO regression for demo-acme);
//   * a tenant with NO photos (the default -- e.g. a services-vertical tenant) -> a
//     ``brand`` treatment: the components paint a BRAND-COLOR GRADIENT panel (the tenant's
//     own --brand / --foreground tokens) + the logo + crisp service cards. NO cats, NO
//     fake stock photos.
//
// The per-slug map is GONE; the photo paths live in tenantConfig.imagery (null = brand
// treatment). This is the content-layer half of the reskin: brandTheme reskins the COLORS;
// this reskins the IMAGERY.
//
// SECURITY: this returns ONLY same-origin root-relative "/images/..." paths (first-party
// committed assets -- the SAME trust class as the existing cat photos, painted directly,
// never gated by isSafeMediaSrc -- that gate is for tenant-PAYLOAD media). It returns NO
// tenant-controlled URL and NO markup.
//
// PURE DATA + PURE FUNCTIONS. ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { tenantConfigFor } from "@/lib/tenantConfig";

/** A decorative imagery treatment for a resolved tenant.
 *
 *  ``mode: "photos"`` -- the tenant ships first-party same-origin decorative photos; the
 *  components paint them (hero backdrop, editorial section, card fallback tile).
 *
 *  ``mode: "brand"``  -- the tenant ships NO photos; the components paint a brand-color
 *  gradient treatment (driven by the tenant CSS tokens) instead of any photo. This is the
 *  honest white-label default: no fabricated stock imagery, just the brand's own palette +
 *  logo + service-icon cards. */
export type TenantImagery =
  | {
      mode: "photos";
      /** full-bleed hero backdrop photo (same-origin /images path). */
      hero: string;
      /** the editorial "A marca" band photo (same-origin /images path). */
      section: string;
      /** the catalog-card decorative fallback tile (same-origin /images path). */
      cardFallback: string;
    }
  | {
      mode: "brand";
    };

/** The honest default when a tenant ships no photos: the brand-gradient treatment. */
const BRAND_TREATMENT: TenantImagery = { mode: "brand" };

/**
 * Resolve a tenant SLUG to its decorative imagery treatment, DERIVED from its config. A
 * photo-shipping tenant (demo-acme) -> its first-party photos; a tenant with no photos
 * (e.g. a services-vertical tenant) AND any unknown slug -> the brand-gradient treatment
 * (the white-label default -- no cat-leak, no fabricated stock photos). TOTAL. ASCII-only.
 */
export function imageryFor(slug: string): TenantImagery {
  const im = tenantConfigFor(slug).imagery;
  if (!im) return BRAND_TREATMENT;
  return { mode: "photos", hero: im.hero, section: im.section, cardFallback: im.cardFallback };
}
