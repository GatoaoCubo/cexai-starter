// ----------------------------------------------------------------------------
// tenantSections -- the per-tenant SECTIONS / NAV config (which non-catalog pages a
// tenant offers), DERIVED from the single source-of-truth (lib/tenantConfig).
//
// THE PROBLEM this fixes: the built-in retail storefront ships a content BLOG (cat articles)
// and a B2B / wholesale area (Revenda / Distribuidor tiers). Those pages + their nav links
// used to render for EVERY tenant. On a white-label storefront that is a LEAK: a SERVICES
// tenant must NOT show a cat-articles blog or a wholesale program it does not
// run -- and must NOT link to them in the nav/footer.
//
// So this layer resolves a tenant SLUG to the set of non-catalog sections it offers. The
// per-slug map is GONE -- the on/off booleans + labels now derive from the tenant's
// ``shape`` (has_blog / has_b2b / b2b_label) in tenantConfig. A services tenant turns those
// sections to its own flavour; an unknown slug + demo-acme resolve to the retail DEFAULT.
//
// REFERENCE-STABLE: the derived TenantSections are INTERNED by structural value, so equal
// shapes share ONE object -- preserving the historic ``toBe(DEFAULT_SECTIONS)`` identity
// (demo-acme + any unknown slug return the SAME DEFAULT_SECTIONS instance).
//
// PURE DATA + PURE FUNCTIONS. ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { tenantConfigFor, type TenantConfig } from "@/lib/tenantConfig";

/** Which non-catalog SECTIONS a tenant offers (drives the nav links + page reachability)
 *  PLUS the per-tenant section LABELS (a services tenant's B2B area is "Para Empresas",
 *  not the retail "B2B"). */
export interface TenantSections {
  /** the content BLOG (sample editorial). retail = cat content; services = tech content. */
  blog: boolean;
  /** the B2B / corporate area. retail = wholesale; services = "Para Empresas". */
  b2b: boolean;
  /** the nav/page label for the b2b section. retail "B2B"; services "Para Empresas". */
  b2bLabel: string;
  /** the nav/page label for the blog section ("Blog" everywhere today). */
  blogLabel: string;
}

/** Build the sections view from a config's shape (the source of truth). The blog label is
 *  "Blog" everywhere today; the b2b label + the on/off flags come from the shape. */
function buildSections(cfg: TenantConfig): TenantSections {
  return {
    blog: cfg.shape.has_blog,
    b2b: cfg.shape.has_b2b,
    b2bLabel: cfg.shape.b2b_label,
    blogLabel: "Blog",
  };
}

// Intern by structural value so two configs with the SAME sections share ONE instance.
// This preserves the historic reference-stable contract: an unknown slug AND demo-acme both
// resolve to the SAME DEFAULT_SECTIONS object (tests assert `toBe(DEFAULT_SECTIONS)`).
const _interned = new Map<string, TenantSections>();
function internSections(cfg: TenantConfig): TenantSections {
  const s = buildSections(cfg);
  const key = s.blog + "|" + s.b2b + "|" + s.b2bLabel + "|" + s.blogLabel;
  const hit = _interned.get(key);
  if (hit) return hit;
  _interned.set(key, s);
  return s;
}

/** The DEFAULT sections -- the built-in product-retail vertical (blog + b2b ON, "B2B" label),
 *  derived from the retail-default config. An unknown slug + demo-acme resolve to THIS by
 *  reference (zero-regression). */
export const DEFAULT_SECTIONS: TenantSections = internSections(tenantConfigFor(""));

/** Resolve the sections a tenant SLUG offers, derived from its ``shape``. A registered tenant
 *  -> its sections; any other slug -> the DEFAULT retail sections (zero-regression). The
 *  result is reference-stable per distinct shape. TOTAL. ASCII-only. */
export function tenantSectionsFor(slug: string): TenantSections {
  return internSections(tenantConfigFor(slug));
}
