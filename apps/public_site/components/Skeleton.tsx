// ----------------------------------------------------------------------------
// Skeleton -- a lightweight content-shaped loading placeholder primitive.
//
// SERVER-SAFE presentational (no hooks, no client state). It is a single pulsing
// block in bg-secondary; the global `prefers-reduced-motion: reduce` rule in
// globals.css forces the pulse animation to 0.01ms, so it auto-disables for users
// who ask for reduced motion (no per-component opt-in -- s5 motion baseline).
//
// Composed (Skeleton.Card / Skeleton.HeroGrid / Skeleton.Pdp) into content-shaped
// loading states that REPLACE the plain "carregando..." text loaders: the page's
// final layout is implied while data loads, which reads far more finished than a
// centered word. Purely decorative -> aria-hidden so screen readers skip the
// scaffold (the surrounding region carries aria-busy / a status label).
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import type { ReactNode } from "react";

/** One pulsing placeholder block. `className` sets its size/shape (the caller owns
 *  the dimensions). Decorative -> aria-hidden. The pulse is the built-in Tailwind
 *  `animate-pulse`, neutralized by the global reduced-motion rule. */
export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={["animate-pulse rounded-md bg-secondary", className].join(" ")}
    />
  );
}

/** A small wrapper that announces a region as busy to assistive tech while the
 *  decorative skeleton blocks render inside it. */
function Loading({
  label,
  children,
  className = "",
}: {
  label: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div role="status" aria-busy="true" aria-live="polite" className={className}>
      <span className="sr-only">{label}</span>
      {children}
    </div>
  );
}

/** A product-card shaped skeleton (1:1 image area + title/price lines) -- mirrors
 *  CatalogCard so the grid keeps its shape while items load. */
function Card() {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-card border border-border bg-card shadow-sm">
      <Skeleton className="aspect-square w-full rounded-none" />
      <div className="flex flex-1 flex-col gap-3 p-5">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <div className="mt-auto flex items-center justify-between gap-3 pt-3">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-4 w-12" />
        </div>
      </div>
    </div>
  );
}

/** A grid of N card skeletons (the catalog / featured loading shape). */
function CardGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: Math.max(1, count) }).map((_, i) => (
        <Card key={i} />
      ))}
    </div>
  );
}

/** The HOME loading shape: a hero band skeleton + a featured card grid. */
function HeroGrid() {
  return (
    <Loading label="Carregando vitrine" className="min-h-screen">
      {/* hero band */}
      <div className="border-b border-border bg-secondary/40">
        <div className="shell grid grid-cols-1 items-center gap-12 py-24 lg:grid-cols-12 lg:py-32">
          <div className="space-y-6 lg:col-span-7">
            <Skeleton className="h-6 w-40 rounded-pill" />
            <Skeleton className="h-14 w-3/4" />
            <Skeleton className="h-6 w-full max-w-xl" />
            <div className="flex flex-col gap-3 pt-2 sm:flex-row">
              <Skeleton className="h-12 w-full rounded-pill sm:w-44" />
              <Skeleton className="h-12 w-full rounded-pill sm:w-40" />
            </div>
          </div>
          <div className="hidden lg:col-span-5 lg:block">
            <Skeleton className="ml-auto aspect-[4/5] w-full max-w-sm rounded-card" />
          </div>
        </div>
      </div>
      {/* featured card grid */}
      <div className="shell space-y-8 py-24">
        <div className="space-y-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-9 w-64" />
        </div>
        <CardGrid count={3} />
      </div>
    </Loading>
  );
}

/** The CATALOG loading shape: a header band + a card grid. */
function CatalogGrid() {
  return (
    <Loading label="Carregando catalogo" className="space-y-10">
      <div className="space-y-3 border-b border-border pb-8">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-72" />
        <Skeleton className="h-5 w-full max-w-md" />
      </div>
      <CardGrid count={6} />
    </Loading>
  );
}

/** The PDP loading shape: a gallery plate + a buy-box (title/price/CTA/specs). */
function Pdp() {
  return (
    <Loading label="Carregando produto" className="space-y-10">
      {/* breadcrumb */}
      <div className="flex items-center gap-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-28" />
      </div>
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-12">
        {/* gallery */}
        <div className="space-y-3">
          <Skeleton className="aspect-square w-full rounded-card" />
          <div className="flex gap-2.5">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-16 rounded-md" />
            ))}
          </div>
        </div>
        {/* buy-box */}
        <div className="space-y-6 lg:rounded-card lg:border lg:border-border lg:bg-card lg:p-7">
          <div className="space-y-3">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-10 w-3/4" />
          </div>
          <Skeleton className="h-9 w-32" />
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-5/6" />
          <Skeleton className="h-12 w-full rounded-pill" />
          <div className="space-y-3 rounded-card border border-border p-5">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-5 w-full" />
            ))}
          </div>
        </div>
      </div>
    </Loading>
  );
}

Skeleton.Card = Card;
Skeleton.CardGrid = CardGrid;
Skeleton.HeroGrid = HeroGrid;
Skeleton.CatalogGrid = CatalogGrid;
Skeleton.Pdp = Pdp;
