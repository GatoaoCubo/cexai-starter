// ----------------------------------------------------------------------------
// BrandShell -- BACKWARD-COMPATIBLE thin wrapper over BrandLayout.
//
// The storefront chrome (header + nav + footer) and the re-skin mechanism now live in
// BrandLayout (see components/BrandLayout.tsx). BrandShell is retained so existing
// callers keep working; it simply delegates to BrandLayout with the catalog nav section
// active (its historical callers are the catalog + detail pages). New pages should use
// BrandLayout directly and pass the correct ``active`` / ``activeKind``.
//
// All theming + security semantics are unchanged -- they are implemented once in
// BrandLayout: buildCssVars -> a scoped <style> (data, never tenant HTML), a scheme-gated
// logo, text-only name/tagline, trusted-constant nav. DEGRADE-NEVER throughout.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import type { ReactNode } from "react";
import type { BrandTheme } from "@/lib/brandTheme";
import { BrandLayout } from "@/components/BrandLayout";
import type { NavSection } from "@/components/BrandHeader";

export function BrandShell({
  brand,
  slug,
  /** which nav section is active (defaults to "catalog" -- BrandShell's historical use). */
  active = "catalog",
  activeKind,
  children,
}: {
  brand?: BrandTheme;
  /** the tenant slug -- powers the nav links (URL-encoded) and the chrome. */
  slug?: string;
  active?: NavSection;
  activeKind?: string;
  children: ReactNode;
}) {
  return (
    <BrandLayout brand={brand} slug={slug ?? ""} active={active} activeKind={activeKind}>
      {children}
    </BrandLayout>
  );
}
