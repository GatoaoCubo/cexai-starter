"use client";

// ----------------------------------------------------------------------------
// B2BView -- the per-tenant B2B / CORPORATE area (client component; brand fetch via
// PublicApiClient so the no-leak gate + fixtures mode stay consistent).
//
// PER-TENANT CONTENT (b2bContentFor): the area renders the shape that fits the tenant's
// business --
//   * mode "wholesale" (the built-in retail default): the WHOLESALE / PARTNER landing -- value
//     pillars, illustrative atacado tiers + pricing bands, onboarding, FAQ. UNCHANGED.
//   * mode "corporate" (a services-vertical tenant): the "Para Empresas" area --
//     corporate offers + who-we-serve + partners + a real WhatsApp contact CTA. NO fake
//     checkout, NO atacado/wholesale-pet language.
//
// SCOPE BOUNDARY (both modes): NO fake checkout and NO binding price. The CTA is a contact
// affordance only. Cart / payments / accounts are the separate commerce repo's concern.
//
// HONEST: the content is curated SAMPLE copy (lib/storeContent) -- never claimed to be a
// real offer. Flagged "amostra" in the UI. Re-skinned to the brand tokens.
//
// SECURITY: the SAME no-leak gate -- the brand fetch runs and a null tenant-info ->
// <NotFound/>. The corporate CTA href is scheme-checked (isSafeContactHref: https only) and
// rel-hardened; covers are brand-gradient for a non-photo tenant (no cat leak). Partner
// logos are first-party committed same-origin assets. All text renders as text.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import { useEffect, useState } from "react";
import { BrandLayout } from "@/components/BrandLayout";
import { NotFound } from "@/components/NotFound";
import { ArrowRightIcon, CheckIcon, SparkleIcon } from "@/components/icons";
import { publicApi, ApiClientError } from "@/lib/publicApi";
import { isValidSlug } from "@/lib/slug";
import { imageryFor } from "@/lib/tenantImagery";
import { tenantSectionsFor } from "@/lib/tenantSections";
import { tenantContentFor, isSafeContactHref } from "@/lib/tenantContent";
import {
  B2B_BENEFITS,
  B2B_TIERS,
  B2B_PRICING_BANDS,
  B2B_STEPS,
  B2B_FAQ,
  B2B_TRUST,
  b2bContentFor,
  type CorporateB2BContent,
} from "@/lib/storeContent";
import type { PublicTenantInfo } from "@/lib/types";

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

export function B2BView({ slug }: { slug: string }) {
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
        // a tenant whose vertical offers NO B2B/corporate area renders NotFound -- so a
        // direct hit on /b2b discloses nothing.
        if (!info || !tenantSectionsFor(info.slug).b2b) {
          setState({ phase: "notfound" });
          return;
        }
        setState({ phase: "ready", info });
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

  const { info } = state;
  const content = b2bContentFor(info.slug);
  const label = tenantSectionsFor(info.slug).b2bLabel;

  // branch on the per-tenant B2B content shape: a services tenant's corporate "Para
  // Empresas" area, OR the built-in retail wholesale area (default -> demo-acme UNCHANGED).
  if (content.mode === "corporate") {
    return <CorporateB2B info={info} content={content} label={label} />;
  }
  return <WholesaleB2B info={info} />;
}

// ---------------------------------------------------------------------------
// CORPORATE ("Para Empresas") -- a services tenant. Corporate offers + who-we-serve +
// partners + a REAL WhatsApp contact CTA. NO atacado, NO fake checkout.
// ---------------------------------------------------------------------------

function CorporateB2B({
  info,
  content,
  label,
}: {
  info: PublicTenantInfo;
  content: CorporateB2BContent;
  label: string;
}) {
  const extra = tenantContentFor(info.slug);
  const partners = extra?.partners ?? [];
  // the CTA href: ONLY an https-scheme-checked WhatsApp deep link reaches the href.
  const ctaHref = isSafeContactHref(content.ctaWhatsapp) ? content.ctaWhatsapp : "";

  return (
    <BrandLayout brand={info.brand} slug={info.slug} active="b2b" fullBleed>
      {/* ---- HERO (brand-gradient -- no photo, no cat) -------------------------- */}
      <section className="relative overflow-hidden border-b border-border bg-foreground">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
          }}
          aria-hidden="true"
        />
        <div className="shell relative py-24 text-center sm:py-32">
          <span className="mb-6 inline-flex items-center gap-2 rounded-pill border border-brand/40 bg-brand/15 px-4 py-1.5 text-sm font-medium text-background">
            <SparkleIcon width={16} height={16} />
            {content.eyebrow}
          </span>
          <h1 className="mx-auto max-w-3xl font-display text-display text-background">
            {content.heroTitle}
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-background/80">
            {content.heroSubline}
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            {ctaHref && (
              <a
                href={ctaHref}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="btn-brand btn-lg"
              >
                {content.ctaLabel}
                <ArrowRightIcon />
              </a>
            )}
            <Link
              href={`/t/${encodeURIComponent(info.slug)}/service`}
              className="btn-lg inline-flex items-center gap-2 rounded-pill border border-background/40 bg-background/10 px-6 font-semibold text-background backdrop-blur-sm transition-colors hover:bg-background/20"
            >
              Ver servicos
            </Link>
          </div>
          <p className="mt-8 text-2xs uppercase tracking-wide text-background/60">
            amostra -- dados simulados
          </p>
        </div>
      </section>

      <div className="shell space-y-24 py-24">
        {/* ---- CORPORATE OFFERS (6) --------------------------------------------- */}
        <section className="space-y-10">
          <div className="space-y-2 text-center">
            <p className="eyebrow">{label}</p>
            <h2 className="font-display text-h2 text-foreground">
              O que a {info.brand.name} faz pela sua operacao
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {content.offers.map((o, i) => (
              <div
                key={o.title}
                className="group rounded-card border border-border bg-card p-7 shadow-sm transition-all duration-base hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-md"
              >
                <span className="mb-4 inline-grid h-10 w-10 place-items-center rounded-card bg-brand-muted font-display text-lg font-bold text-brand">
                  {i + 1}
                </span>
                <h3 className="font-display text-h3 font-semibold tracking-tight text-foreground">
                  {o.title}
                </h3>
                <p className="mt-2 text-base text-muted-foreground">{o.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ---- WHO WE SERVE ------------------------------------------------------ */}
        <section className="mx-auto max-w-3xl rounded-card border border-border bg-card p-10 text-center shadow-sm">
          <p className="eyebrow">Quem atendemos</p>
          <p className="mt-3 font-display text-h2 text-foreground">{content.whoWeServe}</p>
        </section>

        {/* ---- PARTNERS (committed first-party logos) --------------------------- */}
        {partners.length > 0 && (
          <section className="space-y-8">
            <div className="space-y-2 text-center">
              <p className="eyebrow">Parceiros oficiais</p>
              <h2 className="font-display text-h2 text-foreground">
                Tecnologia que confiamos
              </h2>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-8 rounded-card border border-border bg-card p-10 shadow-sm">
              {partners.map((p) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  key={p.src}
                  src={p.src}
                  alt={p.alt}
                  className="h-10 max-w-[160px] object-contain opacity-80 transition-opacity duration-base hover:opacity-100 sm:h-12"
                />
              ))}
            </div>
          </section>
        )}

        {/* ---- CONTACT CTA (WhatsApp -- no fake checkout) ------------------------ */}
        <section
          id="contato"
          className="overflow-hidden rounded-card bg-primary px-8 py-16 text-center text-primary-foreground sm:px-12"
        >
          <h2 className="mx-auto max-w-2xl font-display text-h2">
            Pronto para tirar a TI da sua empresa do improviso?
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-base text-primary-foreground/80">
            Conte sobre a sua operacao e um especialista da {info.brand.name} retorna. Sem
            compromisso -- e sem cadastro nesta vitrine.
          </p>
          {ctaHref && (
            <div className="mt-8 flex justify-center">
              <a
                href={ctaHref}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="btn-lg inline-flex items-center gap-2 rounded-pill bg-background px-6 font-semibold text-foreground transition-colors hover:bg-background/90"
              >
                {content.ctaLabel}
                <ArrowRightIcon />
              </a>
            </div>
          )}
          <p className="mx-auto mt-6 max-w-md text-2xs uppercase tracking-wide text-primary-foreground/60">
            amostra -- dados simulados
          </p>
        </section>
      </div>
    </BrandLayout>
  );
}

// ---------------------------------------------------------------------------
// WHOLESALE -- the built-in retail vertical (UNCHANGED). Value pillars + illustrative atacado
// tiers + pricing bands + onboarding + FAQ + a contact note (no fake checkout).
// ---------------------------------------------------------------------------

function WholesaleB2B({ info }: { info: PublicTenantInfo }) {
  const name = (info.brand?.name ?? "").trim() || "a marca";
  // tenant-derived hero photo ('' -> brand-gradient, no cat leak for a non-photo tenant).
  const imagery = imageryFor(info.slug);
  const heroPhoto = imagery.mode === "photos" ? imagery.section : "";

  return (
    <BrandLayout brand={info.brand} slug={info.slug} active="b2b" fullBleed>
      {/* ---- HERO (photographic for a photo tenant; brand-gradient otherwise) ------ */}
      <section className="relative overflow-hidden border-b border-border bg-foreground">
        {heroPhoto ? (
          <>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={heroPhoto}
              alt=""
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-50"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-foreground/85 via-foreground/80 to-foreground" />
          </>
        ) : (
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
            }}
            aria-hidden="true"
          />
        )}
        <div className="shell relative py-24 text-center sm:py-32">
          <span className="mb-6 inline-flex items-center gap-2 rounded-pill border border-brand/40 bg-brand/15 px-4 py-1.5 text-sm font-medium text-background">
            <SparkleIcon width={16} height={16} />
            Programa de parceiros
          </span>
          <h1 className="mx-auto max-w-3xl font-display text-display text-background">
            Revenda os produtos de {name}
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-background/80">
            Curadoria premium, margem para o lojista e suporte de marca -- para lojistas e
            e-commerces parceiros.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href="#contato" className="btn-brand btn-lg">
              Quero ser parceiro
              <ArrowRightIcon />
            </a>
            <Link
              href={`/t/${encodeURIComponent(info.slug)}`}
              className="btn-lg inline-flex items-center gap-2 rounded-pill border border-background/40 bg-background/10 px-6 font-semibold text-background backdrop-blur-sm transition-colors hover:bg-background/20"
            >
              Ver catalogo
            </Link>
          </div>
          {/* trust signals (no-cart, no-checkout -- honest scope) */}
          <ul className="mx-auto mt-8 flex max-w-2xl flex-wrap justify-center gap-x-6 gap-y-2">
            {B2B_TRUST.map((t) => (
              <li
                key={t}
                className="inline-flex items-center gap-1.5 text-sm font-medium text-background/80"
              >
                <span className="text-brand">
                  <CheckIcon width={16} height={16} />
                </span>
                {t}
              </li>
            ))}
          </ul>
          <p className="mt-6 text-2xs uppercase tracking-wide text-background/60">
            amostra -- dados simulados
          </p>
        </div>
      </section>

      <div className="shell space-y-24 py-24">
        {/* ---- VALUE PILLARS (6) ------------------------------------------------- */}
        <section className="space-y-10">
          <div className="space-y-2 text-center">
            <p className="eyebrow">Por que parceria</p>
            <h2 className="font-display text-h2 text-foreground">O que voce ganha</h2>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {B2B_BENEFITS.map((b, i) => (
              <div
                key={b.title}
                className="group rounded-card border border-border bg-card p-7 shadow-sm transition-all duration-base hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-md"
              >
                <span className="mb-4 inline-grid h-10 w-10 place-items-center rounded-card bg-brand-muted font-display text-lg font-bold text-brand">
                  {i + 1}
                </span>
                <h3 className="font-display text-h3 font-semibold tracking-tight text-foreground">
                  {b.title}
                </h3>
                <p className="mt-2 text-base text-muted-foreground">{b.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ---- PRICING BANDS (illustrative table) ------------------------------- */}
        <section className="space-y-8">
          <div className="space-y-2 text-center">
            <p className="eyebrow">Faixas de atacado</p>
            <h2 className="font-display text-h2 text-foreground">Quanto mais volume, melhor a faixa</h2>
            <p className="mx-auto max-w-2xl text-base text-muted-foreground">
              Faixas ilustrativas (amostra). Os percentuais e regras finais sao definidos no
              contato, conforme volume e recorrencia.
            </p>
          </div>
          <div className="overflow-hidden rounded-card border border-border">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="bg-secondary text-foreground">
                  <th className="px-5 py-4 text-sm font-semibold uppercase tracking-wide">Volume</th>
                  <th className="px-5 py-4 text-sm font-semibold uppercase tracking-wide">Faixa de desconto</th>
                  <th className="px-5 py-4 text-sm font-semibold uppercase tracking-wide">Nivel</th>
                </tr>
              </thead>
              <tbody>
                {B2B_PRICING_BANDS.map((row) => (
                  <tr key={row.volume} className="border-t border-border">
                    <td className="px-5 py-4 text-base text-foreground">{row.volume}</td>
                    <td className="px-5 py-4 text-base font-semibold text-brand">{row.band}</td>
                    <td className="px-5 py-4 text-base text-muted-foreground">{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ---- TIERS (3 bands, discount-flagged) -------------------------------- */}
        <section className="space-y-10">
          <div className="space-y-2 text-center">
            <p className="eyebrow">Niveis</p>
            <h2 className="font-display text-h2 text-foreground">Tiers de parceria</h2>
            <p className="text-base text-muted-foreground">
              Condicoes ilustrativas (amostra) -- os valores e regras finais sao tratados no
              contato.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {B2B_TIERS.map((t) => (
              <div
                key={t.name}
                className={[
                  "flex flex-col gap-5 rounded-card border bg-card p-8 shadow-sm",
                  t.featured
                    ? "border-brand/50 ring-2 ring-brand/20"
                    : "border-border",
                ].join(" ")}
              >
                <div className="space-y-1">
                  {t.featured && (
                    <span className="mb-2 inline-block rounded-pill bg-brand px-3 py-0.5 text-2xs font-semibold uppercase tracking-wide text-brand-foreground">
                      Recomendado
                    </span>
                  )}
                  <h3 className="font-display text-h2 text-foreground">{t.name}</h3>
                  <p className="text-sm text-muted-foreground">{t.qualifier}</p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="font-display text-display text-brand">{t.discountBand}</span>
                  <span className="text-sm text-muted-foreground">de desconto</span>
                </div>
                <p className="text-base font-medium text-foreground">{t.highlight}</p>
                <ul className="space-y-3">
                  {t.perks.map((perk) => (
                    <li key={perk} className="flex items-start gap-2.5 text-base text-foreground">
                      <span className="mt-0.5 shrink-0 text-brand">
                        <CheckIcon width={18} height={18} />
                      </span>
                      {perk}
                    </li>
                  ))}
                </ul>
                <a
                  href="#contato"
                  className={[
                    "mt-auto w-full text-center",
                    t.featured ? "btn-brand" : "btn-outline",
                  ].join(" ")}
                >
                  Falar sobre este nivel
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* ---- ONBOARDING (how it works) ---------------------------------------- */}
        <section className="space-y-10">
          <div className="space-y-2 text-center">
            <p className="eyebrow">Como funciona</p>
            <h2 className="font-display text-h2 text-foreground">Tres passos para comecar</h2>
          </div>
          <ol className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {B2B_STEPS.map((s) => (
              <li
                key={s.step}
                className="rounded-card border border-border bg-card p-7 shadow-sm"
              >
                <span className="mb-4 inline-grid h-11 w-11 place-items-center rounded-full border-2 border-brand font-display text-lg font-bold text-brand">
                  {s.step}
                </span>
                <h3 className="font-display text-h3 font-semibold tracking-tight text-foreground">
                  {s.title}
                </h3>
                <p className="mt-2 text-base text-muted-foreground">{s.body}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* ---- FAQ -------------------------------------------------------------- */}
        <section className="mx-auto max-w-3xl space-y-8">
          <div className="space-y-2 text-center">
            <p className="eyebrow">Duvidas</p>
            <h2 className="font-display text-h2 text-foreground">Perguntas frequentes</h2>
          </div>
          <dl className="space-y-4">
            {B2B_FAQ.map((f) => (
              <div
                key={f.question}
                className="rounded-card border border-border bg-card p-6 shadow-sm"
              >
                <dt className="font-display text-h3 font-semibold tracking-tight text-foreground">
                  {f.question}
                </dt>
                <dd className="mt-2 text-base leading-relaxed text-muted-foreground">
                  {f.answer}
                </dd>
              </div>
            ))}
          </dl>
        </section>

        {/* ---- CONTACT CTA (no fake checkout -- a contact affordance only) -------- */}
        <section
          id="contato"
          className="overflow-hidden rounded-card bg-primary px-8 py-16 text-center text-primary-foreground sm:px-12"
        >
          <h2 className="mx-auto max-w-2xl font-display text-h2">
            Pronto para vender {name}?
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-base text-primary-foreground/80">
            Conte um pouco sobre a sua loja e a equipe de {name} entra em contato. Sem
            compromisso -- e sem cadastro nesta vitrine.
          </p>
          <p className="mx-auto mt-6 max-w-md text-sm text-primary-foreground/70">
            Esta e uma vitrine publica de demonstracao: o formulario real de parceria vive
            no painel da marca. Use o link Admin no topo para acessar o ambiente de gestao.
          </p>
        </section>
      </div>
    </BrandLayout>
  );
}
