"use client";

// ----------------------------------------------------------------------------
// TenantThemeProvider -- RUNTIME admin theme + preview-tenant from the ?tenant
// query param (admin runtime-tenant, inc2). ONE admin build serves every tenant
// by URL: the public site's "Admin" link is <adminUrl>?tenant=<slug>, and this
// provider resolves THAT slug into the admin accent (--accent) + the preview brand
// (the Wordmark logo/name) at RUNTIME, replacing build-time NEXT_PUBLIC_TENANT for
// theming. Absent / invalid / unknown ?tenant -> EXACT current behaviour
// (NEXT_PUBLIC_TENANT if set, else the default CEXAI cyan) -- byte-identical.
//
// SECURITY (LOAD-BEARING): ?tenant drives THEME + PREVIEW ONLY. It NEVER selects,
// widens, or overrides DATA access. The data tenant_id stays bound to auth/RLS --
// the Supabase session JWT app_metadata.tenant_id claim (lib/auth.tsx ->
// lib/supabase.tenantFromSession); dev-mode uses the static FIXTURE_TENANT. This
// module imports NOTHING from the data layer (no ApiClient, no supabase, no auth),
// and the ONLY effect of ?tenant here is a CSS custom property (--accent) + the
// Wordmark brand label. A URL param physically cannot reach a data query from here.
//
// DEGRADE-NEVER: total; ASCII-only source.
// ----------------------------------------------------------------------------

import { createContext, useContext, useEffect, type ReactNode } from "react";
import { useSearchParams } from "next/navigation";
import {
  resolveAdminTheme,
  resolveAdminThemeParamOverride,
  monogramDataUri,
  type AdminTenantTheme,
} from "@/lib/adminTheme";

// undefined = "no provider mounted" -> a consumer (e.g. Wordmark, or a unit test that
// renders the atom alone) falls back to the build-time env theme, preserving byte-
// identical standalone behaviour. null = "provider mounted, default theme". An
// AdminTenantTheme = the active (env or ?tenant) tenant's theme.
const TenantThemeCtx = createContext<AdminTenantTheme | null | undefined>(undefined);

export function TenantThemeProvider({ children }: { children: ReactNode }) {
  const params = useSearchParams();
  const rawTenant = params ? params.get("tenant") : null;

  // The ?tenant runtime OVERRIDE -- null unless the param resolves to a KNOWN tenant.
  const override = resolveAdminThemeParamOverride(rawTenant);
  // The EFFECTIVE preview theme handed to consumers: the override, else the build-time
  // env theme (resolveAdminTheme reads config.activeTenant = NEXT_PUBLIC_TENANT).
  const effective = override ?? resolveAdminTheme();

  const overrideAccent = override ? override.accentHsl : null;

  useEffect(() => {
    // Apply --accent at RUNTIME *only* when ?tenant actually OVERRIDES to a known tenant.
    // With no override we touch NOTHING -- the server-injected env <style> (build-time
    // NEXT_PUBLIC_TENANT) + the tailwind cyan fallback stand exactly as rendered, so the
    // absent/invalid/unknown ?tenant case is byte-identical. The inline property (set on
    // <html>) outranks the :root stylesheet rule, so a known-tenant ?tenant cleanly wins.
    if (!overrideAccent) return;
    const root = document.documentElement;
    const prev = root.style.getPropertyValue("--accent");
    root.style.setProperty("--accent", overrideAccent);
    return () => {
      // Restore on unmount / param change so we never leave a stale inline accent.
      if (prev) root.style.setProperty("--accent", prev);
      else root.style.removeProperty("--accent");
    };
  }, [overrideAccent]);

  // R-006 D3 (per-tenant <title> + favicon) for the EFFECTIVE theme (?tenant override OR the
  // build-time env tenant). Both are OPT-IN per field: a theme without `title` leaves the
  // document title untouched, one without `monogramSvg` leaves the favicon untouched -- so the
  // default admin AND the existing manual rows (which carry neither field) are byte-identical
  // to the pre-R-006 behaviour. Cleanup restores on unmount/param change (preview-safe).
  const effectiveTitle = effective && effective.title ? effective.title : null;
  const effectiveFavicon =
    effective && effective.monogramSvg ? monogramDataUri(effective.monogramSvg) : null;

  useEffect(() => {
    if (!effectiveTitle) return;
    const prev = document.title;
    document.title = effectiveTitle;
    return () => {
      document.title = prev;
    };
  }, [effectiveTitle]);

  useEffect(() => {
    if (!effectiveFavicon) return;
    // An APPENDED <link rel="icon"> outranks the build-time app/icon.svg convention link;
    // removing it on cleanup restores the built-in icon. THEME/PREVIEW ONLY -- never auth/data.
    const link = document.createElement("link");
    link.id = "cexai-tenant-favicon";
    link.rel = "icon";
    link.type = "image/svg+xml";
    link.href = effectiveFavicon;
    document.head.appendChild(link);
    return () => {
      link.remove();
    };
  }, [effectiveFavicon]);

  return (
    <TenantThemeCtx.Provider value={effective}>{children}</TenantThemeCtx.Provider>
  );
}

/** The effective admin theme from context. Returns ``undefined`` when no provider is
 *  mounted, so a standalone consumer (or a unit test) can fall back to the build-time
 *  env theme -- preserving byte-identical behaviour outside the provider. */
export function useAdminThemeContext(): AdminTenantTheme | null | undefined {
  return useContext(TenantThemeCtx);
}
