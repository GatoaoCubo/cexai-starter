"use client";

// ----------------------------------------------------------------------------
// BrandHeader -- the shared, branded site header + primary nav for a resolved tenant.
// CLIENT component (it tracks the mobile-nav open state) but otherwise presentational
// (no fetch, no auth).
//
// This is the "one site" chrome: the SAME header renders on home, every catalog, the
// PDP, the blog, the B2B area, and the about page, so the multi-page storefront reads as
// a single branded site. It themes purely from the brand tokens already injected by
// BrandLayout (design-token utility classes -- text-foreground / border-border / bg-brand
// -- which resolve to the tenant's CSS vars), so it re-skins with ZERO per-component edits.
//
// SECURITY: the logo renders ONLY when its src passes isSafeLogoSrc (https: | data:image
// -- a more restrictive subset of the media allowlist). The name/tagline render as TEXT.
// The nav links are built from the trusted PUBLIC_KINDS constant + STATIC sections + the
// validated slug -- never from tenant-controlled strings -- and the slug is URL-encoded.
// The "Admin" link DEEP-LINKS the current tenant: config.adminUrl (a trusted build-time
// constant, default "/admin") + "?tenant=<slug>" (the encoded, in-scope slug) -- so the
// dashboard opens in THIS tenant's admin theme. The ?tenant param drives the admin THEME +
// preview label ONLY, never data access (that stays bound to the auth/RLS session). It is a
// trusted constant, never a tenant value beyond the slug already in the URL. DEGRADE-NEVER.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import { useState } from "react";
import type { BrandTheme } from "@/lib/brandTheme";
import { isSafeLogoSrc } from "@/lib/brandTheme";
import { adminUrlForTenant } from "@/lib/config";
import { publicKindsFor } from "@/lib/publicKinds";
import { tenantSectionsFor } from "@/lib/tenantSections";
import { tenantStoreUrl } from "@/lib/tenantConfig";

/** Which primary nav entry is the active page (for aria-current + the active style). */
export type NavSection = "home" | "catalog" | "blog" | "b2b" | "about";

interface NavLink {
  href: string;
  label: string;
  isActive: boolean;
  /** when true, the link leaves the site (the Admin link) -> rel-hardened. */
  external?: boolean;
}

export function BrandHeader({
  brand,
  slug,
  active,
  /** when active === "catalog", the currently-viewed kind (so its nav pill highlights). */
  activeKind,
}: {
  brand?: BrandTheme;
  slug: string;
  active: NavSection;
  activeKind?: string;
}) {
  const [open, setOpen] = useState(false);
  const theme = brand ?? {};
  const name = (theme.name ?? "").trim();
  const tagline = (theme.tagline ?? "").trim();
  const logo =
    typeof theme.logo === "string" && isSafeLogoSrc(theme.logo) ? theme.logo : "";
  const logoAlt = (theme.logoAlt ?? name ?? "logo").slice(0, 80);
  const base = `/t/${encodeURIComponent(slug)}`;

  // The nav model: Home + the catalog kinds + (Blog + B2B, per-tenant) + Sobre. Built from
  // trusted constants only (PUBLIC_KINDS + static section labels + the encoded slug). The
  // Blog/B2B links are PER-TENANT (tenantSectionsFor): a retail tenant shows them (default),
  // a services tenant drops them -- so a non-retail vertical never links to a content blog
  // or a wholesale program it does not run.
  const sections = tenantSectionsFor(slug);
  const navLinks: NavLink[] = [
    { href: base, label: "Inicio", isActive: active === "home" },
    ...publicKindsFor(slug).map((pk) => ({
      href: `${base}/${encodeURIComponent(pk.kind)}`,
      label: pk.label,
      isActive: active === "catalog" && activeKind === pk.kind,
    })),
    ...(sections.blog
      ? [{ href: `${base}/blog`, label: sections.blogLabel, isActive: active === "blog" }]
      : []),
    ...(sections.b2b
      ? [{ href: `${base}/b2b`, label: sections.b2bLabel, isActive: active === "b2b" }]
      : []),
    { href: `${base}/sobre`, label: "Sobre", isActive: active === "about" },
  ];

  // an OPTIONAL external "Loja" link (a tenant whose published vertical is NOT product-retail
  // but still runs a separate webstore). Now DERIVED from the links contract (links.store),
  // sanitized https-only; a slug without one -> no Loja link (zero-regression for demo-acme --
  // byte-identical value for a services-vertical tenant with its own store URL). rel-hardened.
  const lojaHref = tenantStoreUrl(slug);

  // the Admin link DEEP-LINKS the current tenant: config.adminUrl + "?tenant=<slug>" (slug
  // URL-encoded). ?tenant drives the admin THEME/preview only -- never data access. SAFE by
  // construction (config.adminUrl is normalized to https:/same-origin; the slug is encoded).
  const adminHref = adminUrlForTenant(slug);

  return (
    <header
      className="sticky top-0 z-[1020] border-b border-border bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70"
    >
      <div className="shell flex items-center justify-between gap-4 py-3">
        {/* brand mark -> always links home */}
        <Link href={base} className="group flex min-w-0 items-center gap-3" aria-label="Inicio">
          {logo ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={logo}
              alt={logoAlt}
              className="h-9 max-w-[150px] rounded-md object-contain"
            />
          ) : (
            <span
              aria-hidden="true"
              className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-brand text-brand-foreground font-display text-base font-bold"
            >
              {(name || "C").slice(0, 1).toUpperCase()}
            </span>
          )}
          <span className="min-w-0">
            <span className="block truncate font-display text-lg font-bold leading-tight tracking-tight text-foreground">
              {name || "Catalogo publico"}
            </span>
            {tagline && (
              <span className="hidden truncate text-2xs text-muted-foreground sm:block">
                {tagline}
              </span>
            )}
          </span>
        </Link>

        {/* primary nav (desktop) -- the SAME on every page (the "one site" chrome) */}
        <nav
          aria-label="Navegacao principal"
          className="hidden items-center gap-1 lg:flex"
        >
          {navLinks.map((l) => (
            <Link
              key={l.href + l.label}
              href={l.href}
              aria-current={l.isActive ? "page" : undefined}
              className={[
                "rounded-pill px-3 py-2 text-sm font-medium transition-colors duration-fast",
                l.isActive
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground",
              ].join(" ")}
            >
              {l.label}
            </Link>
          ))}
          {/* OPTIONAL external Loja link (https-only, rel-hardened) -- a services-vertical tenant
              with a separate webstore; absent for demo-acme. */}
          {lojaHref && (
            <a
              href={lojaHref}
              target="_blank"
              rel="noopener noreferrer nofollow"
              className="rounded-pill px-3 py-2 text-sm font-medium text-muted-foreground transition-colors duration-fast hover:bg-secondary hover:text-foreground"
            >
              Loja
            </a>
          )}
          {/* Admin link -> the dashboard, deep-linked to THIS tenant (?tenant=<slug>); rel-hardened. */}
          <a
            href={adminHref}
            rel="noopener noreferrer"
            className="ml-1 rounded-pill border border-border px-3 py-2 text-sm font-medium text-muted-foreground transition-colors duration-fast hover:border-foreground/30 hover:text-foreground"
          >
            Admin
          </a>
        </nav>

        {/* mobile toggle */}
        <button
          type="button"
          aria-label={open ? "Fechar menu" : "Abrir menu"}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
          className="touch-target rounded-md text-foreground lg:hidden"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            {open ? (
              <path d="M6 6l12 12M18 6 6 18" />
            ) : (
              <path d="M4 7h16M4 12h16M4 17h16" />
            )}
          </svg>
        </button>
      </div>

      {/* mobile nav drawer */}
      {open && (
        <nav
          aria-label="Navegacao principal (mobile)"
          className="border-t border-border bg-background lg:hidden"
        >
          <div className="shell flex flex-col gap-1 py-3">
            {navLinks.map((l) => (
              <Link
                key={l.href + l.label}
                href={l.href}
                aria-current={l.isActive ? "page" : undefined}
                onClick={() => setOpen(false)}
                className={[
                  "rounded-md px-3 py-2.5 text-base font-medium transition-colors",
                  l.isActive
                    ? "bg-secondary text-foreground"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                ].join(" ")}
              >
                {l.label}
              </Link>
            ))}
            {lojaHref && (
              <a
                href={lojaHref}
                target="_blank"
                rel="noopener noreferrer nofollow"
                onClick={() => setOpen(false)}
                className="rounded-md px-3 py-2.5 text-base font-medium text-muted-foreground hover:bg-secondary hover:text-foreground"
              >
                Loja
              </a>
            )}
            <a
              href={adminHref}
              rel="noopener noreferrer"
              className="rounded-md px-3 py-2.5 text-base font-medium text-muted-foreground hover:bg-secondary hover:text-foreground"
            >
              Admin
            </a>
          </div>
        </nav>
      )}
    </header>
  );
}
