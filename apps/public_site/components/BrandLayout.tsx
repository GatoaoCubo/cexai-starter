// ----------------------------------------------------------------------------
// BrandLayout -- THE re-skin keystone + the shared site chrome for a resolved tenant.
// SERVER-SAFE presentational (no hooks, no client state, no fetch).
//
// THE RESKIN MECHANISM (mirrors the reference storefront's applyBrandTheme):
//   buildCssVars(brand) -> a ":root{ --primary: ...; --brand: ...; ... }" string
//   -> injected ONCE here, at the layout, into a scoped <style> element.
// Every descendant component (header, hero, cards, footer, PDP) then reads those CSS
// vars through the design-token utility classes (text-text / border-line / bg-brand /
// text-primary, ...). So the WHOLE multi-page site re-themes from ONE brand object with
// ZERO per-component edits -- add a page and it is branded for free.
//
// WHY <style> TEXT, NOT dangerouslySetInnerHTML: buildCssVars output is a CSS string
// built ONLY from the tenant's own token VALUES (HSL triplets / a CSS length) -- it is
// DATA, never tenant HTML. It is injected as a <style> element's text content (React
// escapes it; it is not a markup-injection sink). DEGRADE-NEVER: an absent/partial brand
// yields an empty vars string -> the neutral look (unchanged), never a broken page.
//
// All three SECURITY invariants are preserved here and downstream: the header logo is
// scheme-gated (isSafeLogoSrc), name/tagline render as text, and nav is built from
// trusted constants + the encoded slug. This component never fetches and never touches
// auth -- it only paints a brand the caller already resolved from the public API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import type { ReactNode } from "react";
import type { BrandTheme } from "@/lib/brandTheme";
import { buildCssVars } from "@/lib/brandTheme";
import { BrandHeader, type NavSection } from "@/components/BrandHeader";
import { BrandFooter } from "@/components/BrandFooter";

export function BrandLayout({
  brand,
  slug,
  active,
  activeKind,
  /** when true, the page renders its own full-bleed hero -> drop the centered main
   *  max-width + top padding so the hero can span edge-to-edge. */
  fullBleed = false,
  children,
}: {
  brand?: BrandTheme;
  slug: string;
  /** which primary nav entry is the current page. */
  active: NavSection;
  /** the active kind when ``active === "catalog"`` (highlights its nav pill). */
  activeKind?: string;
  fullBleed?: boolean;
  children: ReactNode;
}) {
  const theme = brand ?? {};
  // THE re-skin line: tenant tokens -> CSS vars, injected once at the layout root.
  const cssVars = buildCssVars(theme);

  return (
    <div className="flex min-h-screen flex-col">
      {/* Brand CSS vars: data (HSL triplets), not tenant HTML. Empty -> neutral look. */}
      {cssVars && <style>{cssVars}</style>}

      <BrandHeader brand={theme} slug={slug} active={active} activeKind={activeKind} />

      {fullBleed ? (
        <main id="main-content" className="flex-1">
          {children}
        </main>
      ) : (
        <main id="main-content" className="shell flex-1 py-12">
          {children}
        </main>
      )}

      <BrandFooter brand={theme} slug={slug} />
    </div>
  );
}
