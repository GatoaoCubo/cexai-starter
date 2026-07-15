// ----------------------------------------------------------------------------
// tenantContent -- per-tenant STOREFRONT CONTENT the public API contract does NOT carry.
//
// The public /tenant-info + /public/catalog contract carries the BRAND + the published
// CATALOG only. A real tenant storefront also has PARTNERS, SOCIAL PROOF, TESTIMONIALS,
// an ABOUT-stats block, and CONTACT affordances -- none of which the wire contract models.
// So this module curates that extra content PER SLUG, clearly flagged where it is a demo
// render of a real brand's public marketing ("amostra").
//
// HONEST BY CONSTRUCTION: every block here is real public marketing copy a services-vertical
// brand itself publishes, rendered as a DEMO of the storefront -- testimonials carry
// an explicit "amostra" flag, no price is invented, and contact links use ONLY the brand's
// own published channels. A slug ABSENT here -> null (the home renders without these extra
// sections, exactly as demo-acme does today) -> ZERO regression for existing tenants.
//
// SECURITY: this returns plain strings + same-origin "/images/..." partner-logo paths +
// SCHEME-CHECKED external links (https:/whatsapp shapes only -- see safeContactHref). It
// emits NO markup and NO tenant-typed media. Partner logos are first-party committed
// same-origin assets (the same trust class as the decorative photos).
//
// PURE DATA + PURE FUNCTIONS. ASCII-only + diacritic-free (house style).
//
// The per-tenant content clusters + the per-slug registry moved to the single source-of-truth
// (lib/tenantConfig); tenantContentFor now DERIVES from tenantConfigFor(slug).content.
// ----------------------------------------------------------------------------

import { tenantConfigFor } from "@/lib/tenantConfig";

/** One partner / certification logo (a same-origin committed image + an alt label). */
export interface PartnerLogo {
  /** same-origin "/images/..." path to the committed partner logo. */
  src: string;
  /** alt / caption text for the logo. */
  alt: string;
}

/** One social-proof rating summary (e.g. a Google rating). HONEST: surfaced only when the
 *  tenant actually publishes it -- never fabricated. */
export interface SocialProof {
  /** the average rating, 0..5 (display as a 1-decimal). */
  rating: number;
  /** the number of ratings/reviews the source reports. */
  count: number;
  /** the source label, e.g. "Google". */
  source: string;
}

/** One testimonial. ``sample: true`` flags it as a DEMO render of the brand's real
 *  public review (shown with an "amostra" badge), never a fabricated endorsement. */
export interface Testimonial {
  author: string;
  body: string;
  /** true -> render an "amostra" flag (honest: a demo render of public content). */
  sample: boolean;
}

/** One about-stat (a headline number + a short label), e.g. "+20 anos". */
export interface AboutStat {
  value: string;
  label: string;
}

/** The tenant CONTACT affordances. Every link is scheme-checked at the render boundary
 *  (safeContactHref) so only https:/whatsapp(api)/mailto/tel shapes ever become an href. */
export interface TenantContact {
  /** display phone, e.g. "(11) 0000-0000". */
  phone?: string;
  /** contact email (becomes a mailto: only when it is a plain email shape). */
  email?: string;
  /** display address. */
  address?: string;
  /** WhatsApp deep link (https://api.whatsapp.com/... or https://wa.me/...). */
  whatsapp?: string;
  /** Instagram handle (rendered as @handle; linked to https://instagram.com/<handle>). */
  instagram?: string;
  /** the tenant's external store URL (https only). */
  store?: string;
}

/** The full extra storefront content for a tenant. ALL sections optional -- a tenant may
 *  ship only some of them; an absent section simply does not render. */
export interface TenantContent {
  /** the hero sub-headline shown under the brand tagline (brand-specific support line). */
  heroSubline?: string;
  /** the primary hero CTA label (e.g. "Fale no WhatsApp"). */
  ctaLabel?: string;
  /** the partner / certification logos row. */
  partners?: PartnerLogo[];
  /** the about-stats row (e.g. "+20 anos", "+10 mil atendimentos"). */
  aboutStats?: AboutStat[];
  /** a short, factual about paragraph (real brand copy). */
  aboutBody?: string;
  /** the social-proof rating (e.g. Google 4.6 / 68). */
  socialProof?: SocialProof;
  /** the testimonials (flagged amostra). */
  testimonials?: Testimonial[];
  /** the contact affordances. */
  contact?: TenantContact;
}

/** Resolve a tenant SLUG to its extra storefront content, or null -- DERIVED from the single
 *  source-of-truth (tenantConfig). A tenant that ships extra content (a services-vertical
 *  tenant) -> its TenantContent; a tenant that ships none (demo-acme + any unknown slug) ->
 *  null (the home renders without these extra sections -> zero-regression). TOTAL. ASCII-only. */
export function tenantContentFor(slug: string): TenantContent | null {
  return tenantConfigFor(slug).content;
}

// ---------------------------------------------------------------------------
// CONTACT-HREF SCHEME GUARD (render-boundary, defense-in-depth)
// ---------------------------------------------------------------------------

/** True iff a contact href is a SAFE scheme to place in an <a href>. Permits ONLY:
 *  https:, mailto:, tel:, and the whatsapp deep-link shapes (which are https already).
 *  Rejects javascript:, data:, http: and anything else. Mirrors the no-leak posture of
 *  the rest of the surface. TOTAL. */
export function isSafeContactHref(href: unknown): boolean {
  if (typeof href !== "string") return false;
  const s = href.trim();
  if (/^https:\/\//i.test(s)) return true;
  if (/^mailto:[^\s]+@[^\s]+$/i.test(s)) return true;
  if (/^tel:\+?[0-9()\-\s]+$/i.test(s)) return true;
  return false;
}

/** True iff a string is a plain email shape (so it can become a SAFE mailto:). TOTAL. */
export function isPlainEmail(value: unknown): boolean {
  return typeof value === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

/** Build a SAFE Instagram URL from a handle (strips a leading @; https only). '' if blank. */
export function instagramUrl(handle: unknown): string {
  if (typeof handle !== "string") return "";
  const h = handle.trim().replace(/^@+/, "");
  if (!h || !/^[a-z0-9._]{1,40}$/i.test(h)) return "";
  return "https://instagram.com/" + h;
}
