"use client";

// ----------------------------------------------------------------------------
// AboutView -- the BRAND / SOBRE page body (client component so the fetch runs through
// PublicApiClient, keeping fixtures mode working in tests).
//
// It renders the tenant's brand IDENTITY from /public/tenant-info: the name, the
// tagline, the published palette, and HONEST narrative blocks. Crucially, the public
// tenant-info contract carries NO "story"/"voice" field (see apps/dashboard_api/
// public_reader.py -- brand maps 1:1 to BrandTheme: name/tagline/logo/tokens). So the
// about copy is built from what the brand ACTUALLY published (brandText.buildBrandAbout)
// -- it NEVER fabricates a narrative the tenant did not provide.
//
// SECURITY: same no-leak gate as every page -- a null tenant-info (unknown / non-public /
// malformed slug) renders <NotFound/>. The logo is scheme-gated (isSafeLogoSrc); all
// brand text renders as text; the palette swatches are inline background colors built
// from the brand's own HSL token triplets (data, not markup).
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import { useEffect, useState } from "react";
import { BrandLayout } from "@/components/BrandLayout";
import { NotFound } from "@/components/NotFound";
import { Reveal } from "@/components/Reveal";
import { ArrowRightIcon } from "@/components/icons";
import { isSafeLogoSrc } from "@/lib/brandTheme";
import { buildBrandAbout } from "@/lib/brandText";
import { publicApi, ApiClientError } from "@/lib/publicApi";
import { isValidSlug } from "@/lib/slug";
import { publicKindsFor } from "@/lib/publicKinds";
import type { PublicTenantInfo } from "@/lib/types";

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

export function AboutView({ slug }: { slug: string }) {
  const [state, setState] = useState<LoadState>({ phase: "loading" });

  useEffect(() => {
    let alive = true;
    if (!isValidSlug(slug)) {
      setState({ phase: "notfound" });
      return;
    }
    setState({ phase: "loading" });
    publicApi
      .getTenantInfo(slug)
      .then((info) => {
        if (!alive) return;
        setState(info ? { phase: "ready", info } : { phase: "notfound" });
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
  }, [slug]);

  if (state.phase === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          carregando...
        </p>
      </div>
    );
  }

  if (state.phase === "notfound") {
    return <NotFound />;
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

  const { info } = state;
  const brand = info.brand ?? {};
  const about = buildBrandAbout(brand);
  const logo = typeof brand.logo === "string" && isSafeLogoSrc(brand.logo) ? brand.logo : "";
  const logoAlt = (brand.logoAlt ?? about.name ?? "logo").slice(0, 80);
  const base = `/t/${encodeURIComponent(info.slug)}`;

  return (
    <BrandLayout brand={brand} slug={info.slug} active="about">
      <article className="mx-auto max-w-3xl space-y-14">
        <header className="space-y-5">
          {logo && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={logo}
              alt={logoAlt}
              className="h-16 max-w-[240px] rounded-card object-contain"
            />
          )}
          <div className="space-y-3">
            <p className="eyebrow">Sobre a marca</p>
            <h1 className="font-display text-display text-foreground">{about.name}</h1>
            {about.tagline && (
              <p className="text-lg text-muted-foreground">{about.tagline}</p>
            )}
          </div>
        </header>

        {/* the honest narrative blocks (built from the published identity, never invented) */}
        <div className="space-y-8">
          {about.paragraphs.map((p, i) => (
            <Reveal
              as="section"
              key={`${p.heading}-${i}`}
              delay={i * 60}
              className="space-y-2 border-l-2 border-brand/30 pl-5"
            >
              <h2 className="font-display text-h3 font-semibold tracking-tight text-foreground">
                {p.heading}
              </h2>
              <p className="text-lg leading-relaxed text-muted-foreground">{p.body}</p>
            </Reveal>
          ))}
        </div>

        {/* the published palette -- the brand's own tokens, shown as swatches */}
        {about.swatches.length > 0 && (
          <section className="space-y-4">
            <h2 className="font-display text-h3 font-semibold tracking-tight text-foreground">
              Identidade visual
            </h2>
            <div className="flex flex-wrap gap-4">
              {about.swatches.map((s) => (
                <div key={s.label} className="flex items-center gap-2.5">
                  <span
                    aria-hidden="true"
                    className="h-10 w-10 rounded-card border border-border shadow-sm"
                    style={{ background: `hsl(${s.hsl})` }}
                  />
                  <span className="text-sm font-medium text-muted-foreground">{s.label}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* a quiet CTA back into the catalog (the storefront purpose) */}
        <section className="flex flex-wrap gap-3 border-t border-border pt-10">
          {publicKindsFor(info.slug).map((pk) => (
            <Link
              key={pk.kind}
              href={`${base}/${encodeURIComponent(pk.kind)}`}
              className="btn-outline"
            >
              {pk.label}
              <ArrowRightIcon />
            </Link>
          ))}
        </section>
      </article>
    </BrandLayout>
  );
}
