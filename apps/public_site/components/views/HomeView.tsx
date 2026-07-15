"use client";

// ----------------------------------------------------------------------------
// HomeView -- the tenant HOME / premium B2C storefront landing (client component so the
// fetch runs through PublicApiClient, keeping fixtures mode working in tests).
//
// A branded HERO (name / tagline / logo + decorative cat art) + FEATURED published items
// + a VALUE row + the monochrome PT-BR trust row + a closing CTA. It reads PUBLISHED-ONLY
// data via the public endpoints:
//   * /public/tenant-info (the brand shell), and
//   * /public/catalog for EACH configured PUBLIC_KIND with a small limit (the "featured"
//     strip) -- there is NO list-kinds / featured endpoint, so featured == the newest
//     published rows of the documented kinds (honest: a kind with nothing published
//     contributes no cards, never a fabricated item).
//
// SECURITY: the no-leak contract is preserved end-to-end. A null tenant-info (unknown /
// non-public / malformed slug) renders <NotFound/> -- the SAME view a private slug gets.
// The per-kind catalog fetches go through the SAME validated, auth-free client (slug +
// kind only; never a tenant_id, never an auth header). The hero logo is scheme-gated; all
// brand text renders as text; the cat art is a FIRST-PARTY same-origin asset.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import { useEffect, useState } from "react";
import { BrandLayout } from "@/components/BrandLayout";
import { CatalogCard } from "@/components/CatalogCard";
import { ServiceCard } from "@/components/ServiceCard";
import { NotFound } from "@/components/NotFound";
import { Reveal } from "@/components/Reveal";
import { Skeleton } from "@/components/Skeleton";
import { TrustRow } from "@/components/TrustRow";
import {
  ArrowRightIcon,
  SparkleIcon,
  ShieldIcon,
  HeartIcon,
  HeadsetIcon,
  CatIcon,
  StarIcon,
} from "@/components/icons";
import { isSafeLogoSrc } from "@/lib/brandTheme";
import { isSafeMediaSrc } from "@/lib/mediaSafety";
import { buildHomeCopy, galleryCandidates, priceOf, titleOf } from "@/lib/brandText";
import { publicApi, ApiClientError } from "@/lib/publicApi";
import { isValidSlug } from "@/lib/slug";
import { publicKindsFor } from "@/lib/publicKinds";
import { tenantConfigFor } from "@/lib/tenantConfig";
import { imageryFor } from "@/lib/tenantImagery";
import {
  tenantContentFor,
  isSafeContactHref,
  isPlainEmail,
  instagramUrl,
} from "@/lib/tenantContent";
import type { PublicCatalogItem, PublicTenantInfo } from "@/lib/types";

/** How many items per kind the featured strip pulls (newest first, published-only). */
const FEATURED_PER_KIND = 3;

interface FeaturedGroup {
  kind: string;
  label: string;
  blurb: string;
  items: PublicCatalogItem[];
}

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo; featured: FeaturedGroup[] }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

function PillarIcon({ icon }: { icon: "sparkle" | "shield" | "heart" | "headset" | "cat" }) {
  const cls = "text-brand";
  if (icon === "sparkle") return <SparkleIcon className={cls} width={22} height={22} />;
  if (icon === "shield") return <ShieldIcon className={cls} width={22} height={22} />;
  if (icon === "headset") return <HeadsetIcon className={cls} width={22} height={22} />;
  // "cat" -- the RETAIL vitrine default 3rd-pillar glyph (zero-regression for demo-acme +
  // unknown slug); a services tenant resolves to "heart" instead (no cat-face leak).
  if (icon === "cat") return <CatIcon className={cls} width={22} height={22} />;
  // "heart" -- the brand-NEUTRAL "feito com cuidado" glyph (the SERVICES-vertical default).
  return <HeartIcon className={cls} width={22} height={22} />;
}

export function HomeView({ slug }: { slug: string }) {
  const [state, setState] = useState<LoadState>({ phase: "loading" });

  useEffect(() => {
    let alive = true;
    if (!isValidSlug(slug)) {
      setState({ phase: "notfound" });
      return;
    }
    setState({ phase: "loading" });

    (async () => {
      try {
        const info = await publicApi.getTenantInfo(slug);
        if (!alive) return;
        if (!info) {
          setState({ phase: "notfound" });
          return;
        }
        const groups = await Promise.all(
          publicKindsFor(info.slug).map(async (pk): Promise<FeaturedGroup> => {
            let items: PublicCatalogItem[] = [];
            try {
              const cat = await publicApi.getCatalog(info.slug, pk.kind, FEATURED_PER_KIND, 0);
              items = (cat?.items ?? []).slice(0, FEATURED_PER_KIND);
            } catch {
              items = [];
            }
            return { kind: pk.kind, label: pk.label, blurb: pk.blurb, items };
          }),
        );
        if (!alive) return;
        setState({ phase: "ready", info, featured: groups });
      } catch (err: unknown) {
        if (!alive) return;
        const message =
          err instanceof ApiClientError ? err.message : "Nao foi possivel carregar.";
        setState({ phase: "error", message });
      }
    })();

    return () => {
      alive = false;
    };
  }, [slug]);

  if (state.phase === "loading") {
    // content-shaped skeleton (hero band + featured card grid) -- reads more
    // finished than a centered word; pulse auto-disabled by reduced-motion.
    return <Skeleton.HeroGrid />;
  }

  if (state.phase === "notfound") return <NotFound />;

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

  const { info, featured } = state;
  const brand = info.brand ?? {};
  const name = (brand.name ?? "").trim() || "Catalogo publico";
  const tagline = (brand.tagline ?? "").trim();
  const logo = typeof brand.logo === "string" && isSafeLogoSrc(brand.logo) ? brand.logo : "";
  const logoAlt = (brand.logoAlt ?? name ?? "logo").slice(0, 80);
  const base = `/t/${encodeURIComponent(info.slug)}`;
  const kinds = publicKindsFor(info.slug);
  const primaryKind = kinds[0]?.kind ?? "";
  const hasAnyFeatured = featured.some((g) => g.items.length > 0);
  // the SERVICES-vertical signal drives the WHOLE vertical-aware home (copy / CTAs / trust-row
  // / pillars / icons / product-inset): a services tenant must not show a PIX/parcelamento/
  // compra checkout claim. SHAPE-DRIVEN -- it reads the AUTHORITATIVE shape.vertical from the
  // tenant config (the declarative source of truth), NOT the fragile primaryKind==="service"
  // heuristic off the catalog kinds. So a GENERATED services tenant whose published kinds are
  // not literally "service" STILL gets the services home. ZERO-REGRESSION: a services-vertical
  // tenant + demo-acme/unknown (retail) resolve the SAME vertical as before -> byte-identical copy.
  const isServiceVertical = tenantConfigFor(info.slug).shape.vertical === "services";
  // white-label home copy: brand-agnostic pillars (neutral icons, no cat-face) + editorial,
  // derived from the brand. VERTICAL-AWARE via the SAME shape-driven signal above (passed
  // explicitly so the copy + the view can never disagree): a services tenant gets a support
  // pillar, not the PIX/compra claim. A non-retail tenant never shows cat copy; name woven in.
  const copy = buildHomeCopy(brand, { isService: isServiceVertical });

  // WHITE-LABEL IMAGERY: a tenant that ships first-party photos (demo-acme) paints them;
  // a tenant with none (e.g. a services-vertical tenant) gets the BRAND-GRADIENT treatment
  // (no cats, no fake stock). This is the content-layer half of the reskin.
  const imagery = imageryFor(info.slug);
  const heroPhoto = imagery.mode === "photos" ? imagery.hero : "";
  const sectionPhoto = imagery.mode === "photos" ? imagery.section : "";
  const cardFallback = imagery.mode === "photos" ? imagery.cardFallback : "";

  // EXTRA tenant content (partners / about-stats / social proof / testimonials / contact)
  // -- null for tenants (demo-acme) that ship none, so the home is unchanged for them.
  const content = tenantContentFor(info.slug);
  // the REAL contact CTA href (WhatsApp preferred, else the store, else null) -- scheme-
  // checked; only a safe href ever reaches an <a>.
  const whatsappHref =
    content?.contact?.whatsapp && isSafeContactHref(content.contact.whatsapp)
      ? content.contact.whatsapp
      : "";
  const storeHref =
    content?.contact?.store && isSafeContactHref(content.contact.store)
      ? content.contact.store
      : "";
  const primaryCtaHref = whatsappHref || storeHref;
  const primaryCtaLabel = content?.ctaLabel || "Fale conosco";

  // The hero PRODUCT INSET: the single newest published item across the featured groups
  // (honest -- only rendered when something is actually published). Its image is gated by
  // isSafeMediaSrc exactly like every tenant-payload media; the section photo is the
  // fallback. SERVICE items carry no image, so the inset is suppressed for the service
  // vertical (we never show a fabricated photo for a service) -- isServiceVertical is
  // computed above (it also drives the vertical-aware home copy).
  const firstItem: PublicCatalogItem | undefined = featured.find(
    (g) => g.items.length > 0,
  )?.items[0];
  const insetThumbRaw = firstItem
    ? galleryCandidates(firstItem).find((c) => isSafeMediaSrc(c)) ?? ""
    : "";
  const insetTitle = firstItem ? titleOf(firstItem) : "";
  const insetPrice = firstItem ? priceOf(firstItem) : "";
  const insetHref = firstItem
    ? `${base}/${encodeURIComponent(firstItem.kind)}/${encodeURIComponent(firstItem.id)}`
    : "";
  // the inset renders ONLY when the item has a SAFE photo (product vertical); a service
  // (no photo) never gets the photo inset.
  const showInset = !!firstItem && !!insetThumbRaw && !isServiceVertical;

  return (
    <BrandLayout brand={brand} slug={info.slug} active="home" fullBleed>
      {/* ============================================================================
          HERO -- editorial asymmetric split. Left: type + dual CTA + trust, sitting
          over a directional scrim so the photo reads premium (not washed-out grey).
          Right (lg+): a floating featured-product inset card OR a framed photo plate.
          ============================================================================ */}
      <section
        className="relative isolate overflow-hidden border-b border-border bg-foreground"
        aria-label="Destaque"
      >
        {heroPhoto ? (
          <>
            {/* premium photographic backdrop (first-party, same-origin /images/*) -- only
                for a tenant that ships photos (demo-acme). */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={heroPhoto}
              alt=""
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 h-full w-full object-cover object-center opacity-70"
            />
            {/* Directional scrim: dense at the lower-left where the copy lives, opening up
                to the right so the photo + inset breathe. Two layered gradients = a refined,
                non-flat dimming that keeps the headline at AAA contrast. */}
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-foreground via-foreground/85 to-foreground/25" />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-foreground via-foreground/35 to-transparent" />
          </>
        ) : (
          // WHITE-LABEL BRAND TREATMENT: no photo -> a brand-color gradient panel built
          // from the tenant's own --brand / --foreground tokens. This is the honest
          // default for a tenant that ships no decorative photography (no cats, no fake
          // stock). It reads as a premium brand panel, fully reskinned by the tokens.
          <>
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
              }}
              aria-hidden="true"
            />
            {/* a soft radial brand glow for depth (top-right) */}
            <div
              className="pointer-events-none absolute -right-32 -top-32 h-[28rem] w-[28rem] rounded-full opacity-30 blur-3xl"
              style={{ background: "hsl(var(--highlight))" }}
              aria-hidden="true"
            />
          </>
        )}
        {/* a faint brand-tinted glow anchored bottom-left -- the only color in the photo scrim */}
        {heroPhoto && (
          <div
            className="pointer-events-none absolute -bottom-24 -left-24 h-96 w-96 rounded-full opacity-25 blur-3xl"
            style={{ background: "hsl(var(--brand))" }}
            aria-hidden="true"
          />
        )}

        <div className="shell relative grid grid-cols-1 items-center gap-12 py-24 sm:py-28 lg:grid-cols-12 lg:gap-8 lg:py-36">
          {/* ---- LEFT: editorial copy column ---- */}
          <div className="lg:col-span-7 xl:col-span-6">
            {logo && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={logo}
                alt={logoAlt}
                className="mb-8 h-12 max-w-[200px] rounded-card bg-background/95 object-contain px-3 py-1.5 shadow-md"
              />
            )}
            <div className="animate-fade-in-up space-y-6">
              <p className="inline-flex items-center gap-2 rounded-pill border border-background/25 bg-background/10 px-3.5 py-1.5 text-eyebrow font-semibold uppercase tracking-eyebrow text-background/85 backdrop-blur-sm">
                <SparkleIcon width={14} height={14} className="text-brand" />
                {copy.eyebrow}
              </p>
              <h1 className="max-w-2xl font-display text-display leading-[1.04] tracking-tight text-background">
                {name}
              </h1>
              <p className="max-w-xl text-lg leading-relaxed text-background/85 sm:text-xl">
                {content?.heroSubline || tagline || copy.heroFallbackTagline}
              </p>
              <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center">
                {primaryKind && (
                  <Link
                    href={`${base}/${encodeURIComponent(primaryKind)}`}
                    className="btn-brand btn-lg w-full justify-center sm:w-auto"
                  >
                    {isServiceVertical ? "Ver servicos" : "Ver catalogo"}
                    <ArrowRightIcon />
                  </Link>
                )}
                {/* a REAL contact CTA (WhatsApp/store), only when the brand publishes one */}
                {primaryCtaHref ? (
                  <a
                    href={primaryCtaHref}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-lg inline-flex w-full items-center justify-center gap-2 rounded-pill border border-background/40 bg-background/5 px-6 font-semibold text-background backdrop-blur-sm transition-all duration-base ease-standard hover:-translate-y-0.5 hover:border-background/70 hover:bg-background/15 sm:w-auto"
                  >
                    {primaryCtaLabel}
                  </a>
                ) : (
                  <Link
                    href={`${base}/sobre`}
                    className="btn-lg inline-flex w-full items-center justify-center gap-2 rounded-pill border border-background/40 bg-background/5 px-6 font-semibold text-background backdrop-blur-sm transition-all duration-base ease-standard hover:-translate-y-0.5 hover:border-background/70 hover:bg-background/15 sm:w-auto"
                  >
                    Sobre a marca
                  </Link>
                )}
              </div>
              {/* the BR-commerce trust row only fits a product-retail vertical; suppress it
                  for a services tenant (it would be a false claim -- "12x sem juros" etc). */}
              {!isServiceVertical && (
                <div className="mt-2 inline-flex max-w-full flex-wrap items-center gap-x-6 gap-y-2 rounded-card bg-background/95 px-5 py-3 shadow-lg backdrop-blur-sm">
                  <TrustRow />
                </div>
              )}
            </div>
          </div>

          {/* ---- RIGHT: featured-product inset (lg+). Honest: only when a SAFE product
               photo exists. A services tenant (no photo) shows a brand LOGO PLATE instead
               -- never a fabricated product photo. ---- */}
          {showInset && (
            <div className="hidden lg:col-span-5 lg:block xl:col-span-6">
              <Link
                href={insetHref}
                aria-label={`Ver ${insetTitle}`}
                className="group relative ml-auto block w-full max-w-sm overflow-hidden rounded-card border border-background/15 bg-card shadow-lg ring-1 ring-background/10 transition-all duration-slow ease-emphasized hover:-translate-y-1 hover:shadow-xl animate-scale-in"
              >
                <span className="absolute left-4 top-4 z-10 inline-flex items-center gap-1.5 rounded-pill bg-background/90 px-3 py-1 text-2xs font-semibold uppercase tracking-wide text-foreground shadow-sm backdrop-blur-sm">
                  Em destaque
                </span>
                <div className="relative aspect-[4/5] overflow-hidden bg-secondary">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={insetThumbRaw}
                    alt={insetTitle}
                    className="h-full w-full object-cover transition-transform duration-slow ease-emphasized group-hover:scale-[1.05]"
                  />
                  <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-foreground/55 to-transparent" />
                </div>
                <div className="flex items-center justify-between gap-3 p-5">
                  <div className="min-w-0">
                    <p className="truncate font-display text-h3 font-semibold tracking-tight text-foreground">
                      {insetTitle}
                    </p>
                    {insetPrice && (
                      <p className="mt-0.5 font-display text-lg font-bold text-brand">
                        {insetPrice}
                      </p>
                    )}
                  </div>
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-secondary text-foreground transition-colors duration-base group-hover:bg-brand group-hover:text-brand-foreground">
                    <ArrowRightIcon />
                  </span>
                </div>
              </Link>
            </div>
          )}
          {/* brand LOGO PLATE -- the white-label hero anchor for a tenant with no product
              photo (services). A crisp card holding the logo on a brand-tinted surface. */}
          {!showInset && logo && (
            <div className="hidden lg:col-span-5 lg:block xl:col-span-6">
              <div className="ml-auto grid aspect-[4/3] w-full max-w-md place-items-center rounded-card border border-background/20 bg-background/95 p-10 shadow-lg ring-1 ring-background/10 animate-scale-in">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={logo}
                  alt={logoAlt}
                  className="max-h-28 w-full max-w-[280px] object-contain"
                />
              </div>
            </div>
          )}
        </div>
      </section>

      <div className="shell space-y-24 py-24 sm:space-y-28 sm:py-28">
        {/* ---- VALUE PILLARS (brand-agnostic; brand name woven in) --------------- */}
        <section className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {copy.pillars.map((p, i) => (
            <Reveal
              key={p.title}
              delay={i * 80}
              className="group rounded-card border border-border bg-card p-7 shadow-sm transition-all duration-base ease-standard hover:-translate-y-1 hover:border-brand/30 hover:shadow-lg"
            >
              <span className="mb-5 inline-grid h-12 w-12 place-items-center rounded-card bg-brand-muted transition-transform duration-base ease-emphasized group-hover:scale-110">
                <PillarIcon icon={p.icon} />
              </span>
              <h3 className="font-display text-h3 font-semibold tracking-tight text-foreground">
                {p.title}
              </h3>
              <p className="mt-2 text-base leading-relaxed text-muted-foreground">{p.body}</p>
            </Reveal>
          ))}
        </section>

        {/* ---- FEATURED: newest published items per kind ------------------------- */}
        {featured.map((group) =>
          group.items.length > 0 ? (
            <section key={group.kind} className="space-y-8">
              <Reveal className="flex flex-wrap items-end justify-between gap-4">
                <div className="space-y-2">
                  <p className="eyebrow">{group.kind === "service" ? "Servicos" : "Destaques"}</p>
                  <h2 className="font-display text-h2 text-foreground">{group.label}</h2>
                  <p className="max-w-xl text-base text-muted-foreground">{group.blurb}</p>
                </div>
                <Link
                  href={`${base}/${encodeURIComponent(group.kind)}`}
                  className="btn-ghost group/link"
                >
                  Ver tudo
                  <span className="transition-transform duration-base ease-emphasized group-hover/link:translate-x-1">
                    <ArrowRightIcon />
                  </span>
                </Link>
              </Reveal>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {group.items.map((it, i) => (
                  <Reveal key={it.id} delay={i * 70}>
                    {group.kind === "service" ? (
                      <ServiceCard
                        item={it}
                        ctaHref={primaryCtaHref}
                        ctaLabel={primaryCtaHref ? primaryCtaLabel : ""}
                      />
                    ) : (
                      <CatalogCard item={it} slug={info.slug} cardFallback={cardFallback} />
                    )}
                  </Reveal>
                ))}
              </div>
            </section>
          ) : null,
        )}

        {/* ---- EDITORIAL BAND: photographic for a photo tenant; a brand-gradient panel
             for a white-label tenant with no photo (no cats, no fake stock). ----------- */}
        <Reveal
          as="section"
          className="relative overflow-hidden rounded-card border border-border shadow-md"
        >
          {sectionPhoto ? (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={sectionPhoto}
                alt=""
                aria-hidden="true"
                className="absolute inset-0 h-full w-full object-cover"
              />
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-foreground via-foreground/75 to-foreground/15" />
            </>
          ) : (
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "linear-gradient(120deg, hsl(var(--foreground)) 0%, hsl(var(--brand)) 100%)",
              }}
              aria-hidden="true"
            />
          )}
          <div className="relative max-w-xl space-y-5 p-10 sm:p-14 lg:p-16">
            <p className="eyebrow text-background/70">A marca</p>
            <h2 className="font-display text-h2 leading-tight text-background">
              Uma vitrine que reflete {name}
            </h2>
            <p className="text-lg leading-relaxed text-background/85">
              Cores, tipografia e tom -- tudo nesta pagina vem da identidade publicada da
              marca. O que voce ve aqui e o que a marca escolheu mostrar.
            </p>
            <Link href={`${base}/sobre`} className="btn-brand mt-2">
              Conhecer a marca
              <ArrowRightIcon />
            </Link>
          </div>
        </Reveal>

        {/* ---- CATEGORY CARDS: always present, link into each catalog ------------ */}
        <section className="space-y-8">
          <Reveal className="space-y-2">
            <p className="eyebrow">Explorar</p>
            <h2 className="font-display text-h2 text-foreground">Categorias</h2>
          </Reveal>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {kinds.map((pk, i) => (
              <Reveal key={pk.kind} delay={i * 70}>
                <Link
                  href={`${base}/${encodeURIComponent(pk.kind)}`}
                  className="group flex h-full items-center justify-between gap-3 rounded-card border border-border bg-card p-6 shadow-sm transition-all duration-base ease-standard hover:-translate-y-1 hover:border-brand/40 hover:shadow-lg"
                >
                  <div className="min-w-0">
                    <p className="font-display text-h3 font-semibold tracking-tight text-foreground">
                      {pk.label}
                    </p>
                    <p className="mt-1 text-base text-muted-foreground">{pk.blurb}</p>
                  </div>
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-secondary text-muted-foreground transition-all duration-base ease-emphasized group-hover:translate-x-0.5 group-hover:bg-brand group-hover:text-brand-foreground">
                    <ArrowRightIcon />
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
        </section>

        {/* ---- ABOUT STATS (real brand stats; only when the tenant publishes them) --- */}
        {content?.aboutStats && content.aboutStats.length > 0 && (
          <Reveal as="section" className="space-y-8">
            <div className="space-y-2">
              <p className="eyebrow">A empresa</p>
              <h2 className="font-display text-h2 text-foreground">{name} em numeros</h2>
              {content.aboutBody && (
                <p className="max-w-2xl text-base leading-relaxed text-muted-foreground">
                  {content.aboutBody}
                </p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-5 sm:grid-cols-4">
              {content.aboutStats.map((s) => (
                <div
                  key={s.value + s.label}
                  className="rounded-card border border-border bg-card p-6 text-center shadow-sm"
                >
                  <p className="font-display text-h2 font-bold text-brand">{s.value}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{s.label}</p>
                </div>
              ))}
            </div>
          </Reveal>
        )}

        {/* ---- PARTNERS (committed same-origin logos; only when published) ---------- */}
        {content?.partners && content.partners.length > 0 && (
          <Reveal as="section" className="space-y-8">
            <div className="space-y-2">
              <p className="eyebrow">Parceiros</p>
              <h2 className="font-display text-h2 text-foreground">Tecnologia que confiamos</h2>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-8 rounded-card border border-border bg-card p-10 shadow-sm">
              {content.partners.map((p) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  key={p.src}
                  src={p.src}
                  alt={p.alt}
                  className="h-10 max-w-[160px] object-contain opacity-80 transition-opacity duration-base hover:opacity-100 sm:h-12"
                />
              ))}
            </div>
          </Reveal>
        )}

        {/* ---- SOCIAL PROOF + TESTIMONIALS (honest: flagged amostra) ----------------- */}
        {content?.testimonials && content.testimonials.length > 0 && (
          <Reveal as="section" className="space-y-8">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div className="space-y-2">
                <p className="eyebrow">Depoimentos</p>
                <h2 className="font-display text-h2 text-foreground">
                  O que dizem os clientes
                </h2>
              </div>
              {content.socialProof && (
                <div className="flex items-center gap-3 rounded-card border border-border bg-card px-5 py-3 shadow-sm">
                  <span className="inline-flex items-center gap-1 text-highlight">
                    <StarIcon width={18} height={18} className="text-highlight" />
                    <span className="font-display text-h3 font-bold text-foreground">
                      {content.socialProof.rating.toFixed(1)}
                    </span>
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {content.socialProof.count} avaliacoes ({content.socialProof.source})
                  </span>
                </div>
              )}
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
              {content.testimonials.map((t, i) => (
                <Reveal
                  key={t.author + i}
                  delay={i * 70}
                  className="flex h-full flex-col rounded-card border border-border bg-card p-7 shadow-sm"
                >
                  <p className="flex-1 text-base leading-relaxed text-foreground">
                    &ldquo;{t.body}&rdquo;
                  </p>
                  <div className="mt-5 flex items-center justify-between gap-2">
                    <span className="font-display text-sm font-semibold text-foreground">
                      {t.author}
                    </span>
                    {t.sample && (
                      <span className="chip text-2xs uppercase tracking-wide">amostra</span>
                    )}
                  </div>
                </Reveal>
              ))}
            </div>
          </Reveal>
        )}

        {/* ---- CONTACT (real published channels; scheme-checked hrefs) -------------- */}
        {content?.contact && (
          <Reveal
            as="section"
            className="rounded-card border border-border bg-secondary/40 p-10 shadow-sm sm:p-12"
          >
            <div className="space-y-2">
              <p className="eyebrow">Contato</p>
              <h2 className="font-display text-h2 text-foreground">Fale com {name}</h2>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-x-10 gap-y-4 sm:grid-cols-2">
              {content.contact.address && (
                <p className="text-base text-muted-foreground">{content.contact.address}</p>
              )}
              {content.contact.phone && (
                <p className="text-base text-muted-foreground">{content.contact.phone}</p>
              )}
              {content.contact.email && isPlainEmail(content.contact.email) && (
                <a
                  href={`mailto:${content.contact.email}`}
                  className="text-base font-medium text-brand transition-colors hover:text-highlight"
                >
                  {content.contact.email}
                </a>
              )}
              {instagramUrl(content.contact.instagram) && (
                <a
                  href={instagramUrl(content.contact.instagram)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base font-medium text-brand transition-colors hover:text-highlight"
                >
                  @{(content.contact.instagram ?? "").replace(/^@+/, "")}
                </a>
              )}
            </div>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              {whatsappHref && (
                <a
                  href={whatsappHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-brand btn-lg justify-center"
                >
                  {content.ctaLabel || "Fale no WhatsApp"}
                  <ArrowRightIcon />
                </a>
              )}
              {storeHref && (
                <a
                  href={storeHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-outline btn-lg justify-center"
                >
                  Loja online
                  <ArrowRightIcon />
                </a>
              )}
            </div>
          </Reveal>
        )}

        {!hasAnyFeatured && (
          <div className="rounded-card border border-dashed border-border bg-secondary/40 px-6 py-12 text-center">
            <p className="font-display text-h3 font-semibold text-foreground">
              {isServiceVertical ? "Servicos em preparacao" : "Catalogo em preparacao"}
            </p>
            <p className="mt-1 text-base text-muted-foreground">
              Ainda nao ha itens publicados nesta vitrine. Volte em breve.
            </p>
          </div>
        )}

        {/* ---- CLOSING CTA (primary fill section) -------------------------------- */}
        <Reveal
          as="section"
          className="relative overflow-hidden rounded-card bg-primary px-8 py-20 text-center text-primary-foreground shadow-lg sm:px-12"
        >
          {/* a quiet brand glow inside the dark CTA plate */}
          <div
            className="pointer-events-none absolute -right-20 -top-20 h-72 w-72 rounded-full opacity-20 blur-3xl"
            style={{ background: "hsl(var(--brand))" }}
            aria-hidden="true"
          />
          <div className="relative">
            <p className="eyebrow text-primary-foreground/60">Comecar</p>
            <h2 className="mx-auto mt-3 max-w-2xl font-display text-h2 leading-tight">
              {isServiceVertical
                ? `Conheca os servicos de ${name}`
                : `Conheca o catalogo completo de ${name}`}
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg leading-relaxed text-primary-foreground/80">
              {copy.ctaBody}
            </p>
            {primaryKind && (
              <Link
                href={`${base}/${encodeURIComponent(primaryKind)}`}
                className="btn-brand btn-lg mt-8"
              >
                Explorar agora
                <ArrowRightIcon />
              </Link>
            )}
          </div>
        </Reveal>
      </div>
    </BrandLayout>
  );
}
