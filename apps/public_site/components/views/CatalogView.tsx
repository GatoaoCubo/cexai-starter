"use client";

// ----------------------------------------------------------------------------
// CatalogView -- the per-kind CATALOG page body (client component; fetch through
// PublicApiClient so fixtures mode works in tests).
//
// Flow: validate slug + kind -> fetch /public/catalog. A null result (unknown /
// non-public / malformed slug or kind -- the no-leak miss) renders <NotFound/>.
// A resolved tenant with an EMPTY items list renders a branded empty shell
// ("nada publicado ainda"). Else a grid of <CatalogCard/> linking to detail.
//
// To render the branded shell on the empty case it ALSO needs the brand -- so it
// fetches tenant-info alongside the catalog. A catalog hit but a tenant-info miss
// is treated as the no-leak NotFound (consistency).
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
import { publicApi, ApiClientError } from "@/lib/publicApi";
import { isValidKind, isValidSlug } from "@/lib/slug";
import { publicKindsFor } from "@/lib/publicKinds";
import { imageryFor } from "@/lib/tenantImagery";
import { tenantContentFor, isSafeContactHref } from "@/lib/tenantContent";
import type { PublicCatalogResponse, PublicTenantInfo } from "@/lib/types";

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo; catalog: PublicCatalogResponse }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

export function CatalogView({ slug, kind }: { slug: string; kind: string }) {
  const [state, setState] = useState<LoadState>({ phase: "loading" });

  useEffect(() => {
    let alive = true;
    if (!isValidSlug(slug) || !isValidKind(kind)) {
      setState({ phase: "notfound" });
      return;
    }
    setState({ phase: "loading" });
    Promise.all([publicApi.getTenantInfo(slug), publicApi.getCatalog(slug, kind)])
      .then(([info, catalog]) => {
        if (!alive) return;
        // Either miss (no-leak) -> NotFound, never a partial disclosure.
        if (!info || !catalog) {
          setState({ phase: "notfound" });
          return;
        }
        setState({ phase: "ready", info, catalog });
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
  }, [slug, kind]);

  if (state.phase === "loading") {
    // content-shaped skeleton (header band + card grid). The brand shell is not
    // known yet, so render inside a neutral shell with the standard page gutter.
    return (
      <div className="shell py-12">
        <Skeleton.CatalogGrid />
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

  const { info, catalog } = state;
  const items = catalog.items ?? [];
  const kinds = publicKindsFor(info.slug);
  const label = kinds.find((pk) => pk.kind === catalog.kind)?.label ?? catalog.kind;
  const blurb = kinds.find((pk) => pk.kind === catalog.kind)?.blurb ?? "";
  const isServiceVertical = catalog.kind === "service";
  const eyebrow = isServiceVertical ? "Servicos" : "Catalogo";
  // tenant-derived decorative fallback for product cards ('' -> brand-gradient tile).
  const imagery = imageryFor(info.slug);
  const cardFallback = imagery.mode === "photos" ? imagery.cardFallback : "";
  // the REAL contact CTA for service cards (WhatsApp/store), scheme-checked.
  const content = tenantContentFor(info.slug);
  const whatsappHref =
    content?.contact?.whatsapp && isSafeContactHref(content.contact.whatsapp)
      ? content.contact.whatsapp
      : "";
  const storeHref =
    content?.contact?.store && isSafeContactHref(content.contact.store)
      ? content.contact.store
      : "";
  const serviceCtaHref = whatsappHref || storeHref;
  const serviceCtaLabel = content?.ctaLabel || "Fale conosco";

  return (
    <BrandLayout brand={info.brand} slug={info.slug} active="catalog" activeKind={catalog.kind}>
      <header className="mb-10 flex flex-wrap items-end justify-between gap-4 border-b border-border pb-8">
        <div className="space-y-2">
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="font-display text-h1 text-foreground">{label}</h1>
          {blurb && <p className="text-base text-muted-foreground">{blurb}</p>}
          {items.length > 0 && (
            <p className="text-sm text-muted-foreground">
              {items.length}{" "}
              {isServiceVertical
                ? items.length === 1
                  ? "servico publicado"
                  : "servicos publicados"
                : items.length === 1
                  ? "item publicado"
                  : "itens publicados"}
            </p>
          )}
        </div>
        <Link href={`/t/${encodeURIComponent(info.slug)}`} className="btn-ghost">
          Voltar ao inicio
        </Link>
      </header>

      {items.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((it, i) => (
            <Reveal key={it.id} delay={(i % 3) * 70}>
              {isServiceVertical ? (
                <ServiceCard
                  item={it}
                  ctaHref={serviceCtaHref}
                  ctaLabel={serviceCtaHref ? serviceCtaLabel : ""}
                />
              ) : (
                <CatalogCard item={it} slug={info.slug} cardFallback={cardFallback} />
              )}
            </Reveal>
          ))}
        </div>
      ) : (
        <div className="rounded-card border border-dashed border-border bg-secondary/40 px-6 py-14 text-center">
          <p className="font-display text-h3 font-semibold text-foreground">Nada publicado ainda</p>
          <p className="mt-1 text-base text-muted-foreground">
            Esta categoria nao tem itens publicados no momento.
          </p>
        </div>
      )}
    </BrandLayout>
  );
}
