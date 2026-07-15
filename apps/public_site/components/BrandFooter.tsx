// ----------------------------------------------------------------------------
// BrandFooter -- the shared, branded site footer for a resolved tenant. SERVER-SAFE
// presentational (no hooks, no client state, no fetch).
//
// The SAME footer renders on every page (the "one site" chrome, bottom half). It themes
// from the injected brand tokens via the design-token utility classes. It carries the
// brand name + tagline + the full nav echo (catalog kinds + Blog + B2B + Sobre) + the
// monochrome PT-BR trust row + the HONEST provenance line (the public surface shows
// published-only content). DEGRADE-NEVER: an absent brand -> a neutral footer.
//
// SECURITY: name/tagline render as TEXT; nav links are built from the trusted
// PUBLIC_KINDS constant + static section labels + the URL-encoded validated slug only.
// The Admin link DEEP-LINKS this tenant (config.adminUrl + "?tenant=<slug>"; the ?tenant
// param drives the admin THEME only, never data access), rel-hardened. The
// nav "Loja" link + the external PRESENCE ROW derive from the tenant links contract
// (links.store / links.*); EVERY external href passes isSafeHref (absolute https only)
// at the render boundary, so a javascript:/data:/relative URL never becomes an href on
// this unauthenticated surface. rel="noopener noreferrer" + target="_blank" throughout.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import type { BrandTheme } from "@/lib/brandTheme";
import { adminUrlForTenant } from "@/lib/config";
import { publicKindsFor } from "@/lib/publicKinds";
import { tenantSectionsFor } from "@/lib/tenantSections";
import {
  tenantConfigFor,
  tenantStoreUrl,
  isSafeHref,
  safeLinkEntries,
  type TenantLinks,
} from "@/lib/tenantConfig";
import { TrustRow } from "@/components/TrustRow";

/** The external PRESENCE ROW -- the tenant's web + social links. This is the RENDER BOUNDARY
 *  for the links contract: it sanitizes EVERY href here (safeLinkEntries -> isSafeHref:
 *  absolute https only) so a hostile / relative / javascript: / data: URL never becomes an
 *  <a href> on this unauthenticated public surface. Renders ONLY the links that exist; when
 *  none are safe it returns null (graceful -- no empty row). ``hasContactWhatsapp`` reconciles
 *  the WhatsApp link (omitted when a WhatsApp control already exists elsewhere). */
export function TenantPresenceRow({
  links,
  hasContactWhatsapp = false,
}: {
  links?: TenantLinks | null;
  hasContactWhatsapp?: boolean;
}) {
  const entries = safeLinkEntries(links, { hasContactWhatsapp });
  if (entries.length === 0) return null;
  return (
    <nav
      aria-label="Redes e canais"
      className="mt-10 flex flex-wrap items-center gap-x-5 gap-y-2"
    >
      {entries.map((l) => (
        <a
          key={l.key}
          href={l.href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
        >
          {l.label}
        </a>
      ))}
    </nav>
  );
}

export function BrandFooter({ brand, slug }: { brand?: BrandTheme; slug: string }) {
  const name = (brand?.name ?? "").trim() || "Catalogo publico";
  const tagline = (brand?.tagline ?? "").trim();
  const base = `/t/${encodeURIComponent(slug)}`;
  const year = new Date().getFullYear();
  const kinds = publicKindsFor(slug);
  // the BR-commerce trust row (PIX / parcelamento / troca) only fits a product-retail
  // vertical -- suppress it for a services tenant (it would be a false claim there).
  // SHAPE-DRIVEN: read the AUTHORITATIVE shape.vertical (the declarative source of truth),
  // NOT a kinds.some(k==="service") heuristic off the catalog kinds -- so a GENERATED services
  // tenant whose published kinds are not literally "service" STILL suppresses the false retail
  // trust row. ZERO-REGRESSION: a services-vertical tenant + demo-acme/unknown (retail) resolve
  // the SAME vertical as before (the footer chrome matches the shape-driven HomeView hero).
  const isServiceVertical = tenantConfigFor(slug).shape.vertical === "services";

  // Blog/B2B are PER-TENANT (tenantSectionsFor): a retail tenant echoes them (default), a
  // services tenant drops them -- the footer nav mirrors the header so a non-retail vertical
  // never links to a content blog or a wholesale program it does not run.
  const sections = tenantSectionsFor(slug);
  const navLinks: { href: string; label: string }[] = [
    { href: base, label: "Inicio" },
    ...kinds.map((pk) => ({
      href: `${base}/${encodeURIComponent(pk.kind)}`,
      label: pk.label,
    })),
    ...(sections.blog ? [{ href: `${base}/blog`, label: sections.blogLabel }] : []),
    ...(sections.b2b ? [{ href: `${base}/b2b`, label: sections.b2bLabel }] : []),
    { href: `${base}/sobre`, label: "Sobre" },
  ];

  // an OPTIONAL external Loja link -- now DERIVED from the links contract (links.store),
  // sanitized https-only. Absent for demo-acme (zero-regression); present for a services-vertical
  // tenant with a separate webstore (its own loja.<domain> URL, byte-identical to the historic
  // hard-coded value for that tenant).
  const cfg = tenantConfigFor(slug);
  const lojaHref = tenantStoreUrl(slug);
  // the Admin link DEEP-LINKS the current tenant: config.adminUrl + "?tenant=<slug>" (slug
  // URL-encoded). ?tenant drives the admin THEME/preview only -- never data access. SAFE by
  // construction (config.adminUrl is normalized to https:/same-origin; the slug is encoded).
  const adminHref = adminUrlForTenant(slug);
  // reconcile flag for the presence row: a tenant already exposing a WhatsApp control via
  // content.contact.whatsapp must NOT get a duplicate WhatsApp link in the row.
  const hasContactWhatsapp = isSafeHref((cfg.content?.contact?.whatsapp ?? "").trim());

  return (
    <footer className="mt-24 border-t border-border bg-secondary/40">
      <div className="shell py-14">
        {/* trust row (monochrome, brand-themed) -- product-retail verticals only */}
        {!isServiceVertical && (
          <TrustRow className="mb-10 justify-center sm:justify-start" />
        )}

        <div className="flex flex-col gap-10 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-sm space-y-2">
            <p className="font-display text-h3 font-semibold tracking-tight text-foreground">
              {name}
            </p>
            {tagline && <p className="text-base text-muted-foreground">{tagline}</p>}
            <p className="pt-1 text-sm text-muted-foreground">
              Vitrine publica. Somente itens publicados sao visiveis aqui -- nenhum login
              e necessario.
            </p>
          </div>

          <nav
            aria-label="Rodape"
            className="grid grid-cols-2 gap-x-10 gap-y-2 sm:flex sm:flex-col"
          >
            {navLinks.map((l) => (
              <Link
                key={l.href + l.label}
                href={l.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                {l.label}
              </Link>
            ))}
            {lojaHref && (
              <a
                href={lojaHref}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Loja
              </a>
            )}
            <a
              href={adminHref}
              rel="noopener noreferrer"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Admin
            </a>
          </nav>
        </div>

        {/* external presence row (web + social) -- ADDITIVE: each link sanitized
            (isSafeHref: https only) + rel-hardened; renders ONLY present links, nothing for
            a tenant with none (demo-acme/unknown -> no empty row). The nav + copyright
            below stay byte-identical. */}
        <TenantPresenceRow links={cfg.links} hasContactWhatsapp={hasContactWhatsapp} />

        <div className="mt-10 border-t border-border pt-6">
          <p className="text-2xs uppercase tracking-wide text-muted-foreground">
            (c) {year} {name} -- catalogo publicado via CEXAI.
          </p>
        </div>
      </div>
    </footer>
  );
}
