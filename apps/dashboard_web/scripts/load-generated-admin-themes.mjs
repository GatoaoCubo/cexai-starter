// ----------------------------------------------------------------------------
// load-generated-admin-themes.mjs -- the DEV-ONLY half of the R-006 Admin Theming
// Bridge (mirrors apps/public_site/scripts/load-generated-tenants.mjs).
//
// THE LOOP: cex_tenant_bootstrap (--execute / --persist-config) derives a tenant's
// admin theme via _tools/cex_admin_theme.py and persists the RAW mechanic output to
// `.cex/tenants/<slug>/admin_theme.json` (gitignored). This script reads EVERY such
// file, PROJECTS it into a registry entry (the projection MIRRORS -- keep in sync --
// cex_distill._admin_theme_registry_entry), and writes the merged map into
// lib/generatedAdminThemes.json -- the COMMITTED (default {}) registry that
// lib/adminTheme.ts statically imports. `npm run dev` then themes the admin for the
// generated tenant with NO hand-seeding. A manual ADMIN_TENANTS row still WINS
// (precedence lives in lib/adminTheme.ts: manual > generated > default).
//
// DISTILLED-REPO SAFETY (deliberate divergence from the public_site loader): when
// `.cex/tenants/` does NOT exist we SKIP the write entirely instead of writing {}.
// A distilled sovereign repo carries its own single-entry registry committed by
// cex_distill._carry_admin_theme and usually has NO .cex/tenants dir -- writing {}
// here would erase the carried theme on the first `npm run dev`. When the dir DOES
// exist, the collected map is authoritative (an empty collection honestly writes {}).
//
// PROD-SAFE: never runs in prod (no `next dev`); resolves nothing from the network;
// NEVER writes the DB. DEGRADE-NEVER: every failure path keeps a usable registry and
// exits 0, so a garbled .cex/tenants can NEVER block `next dev`.
//
// ASCII-only + diacritic-free (house style). No external deps (node builtins only).
// ----------------------------------------------------------------------------

import {
  existsSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
// scripts/ -> dashboard_web/ -> apps/ -> repo root
const REPO_ROOT = resolve(HERE, "..", "..", "..");
const TENANTS_DIR = join(REPO_ROOT, ".cex", "tenants");
const APP_ROOT = resolve(HERE, "..");
const OUT_FILE = join(APP_ROOT, "lib", "generatedAdminThemes.json");
const TAG = "[load-generated-admin-themes]";

// Mirror lib/adminTheme.ts TENANT_SLUG_RE (the backend's _SLUG_RE): a leading [a-z0-9],
// then up to 63 more [a-z0-9_-]. Keeps a bad path segment out of the registry keys.
const SLUG_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;

function isValidSlug(s) {
  return typeof s === "string" && SLUG_RE.test(s.trim());
}

function msg(e) {
  return e && e.message ? e.message : String(e);
}

/** RAW cex_admin_theme output -> ONE registry entry. MIRRORS (keep in sync) the Python
 *  projection cex_distill._admin_theme_registry_entry: {brand:{name, logoAlt, tokens},
 *  logoPath, monogramSvg, title, source}. Returns null on a shape that is not the
 *  mechanic's output (that tenant is skipped, never the whole run). */
function projectEntry(theme, slug) {
  if (!theme || typeof theme !== "object" || Array.isArray(theme)) return null;
  const meta = theme.meta && typeof theme.meta === "object" ? theme.meta : {};
  const tokens = theme.tokens && typeof theme.tokens === "object" ? theme.tokens : null;
  const mono = theme.monogram && typeof theme.monogram === "object" ? theme.monogram : {};
  if (!tokens) return null;
  const brandName =
    typeof meta.brand_name === "string" && meta.brand_name.trim()
      ? meta.brand_name.trim()
      : slug;
  const source = meta.source === "brand" ? "brand" : "default";
  const svg = typeof mono.svg === "string" ? mono.svg : "";
  // honest logoPath: point at the same-origin admin logo ONLY when the file actually exists.
  const logoFs = join(APP_ROOT, "public", "tenants", slug, "logo.png");
  const logoPath = existsSync(logoFs) ? "/tenants/" + slug + "/logo.png" : null;
  return {
    brand: { name: brandName, logoAlt: brandName, tokens },
    logoPath,
    monogramSvg: svg,
    title: brandName + " -- Capability Console",
    source,
  };
}

/** Collect every `.cex/tenants/<slug>/admin_theme.json` into a { slug: entry } map.
 *  Degrade-never: any error on a single tenant skips THAT tenant, never the whole run. */
function collect() {
  const registry = {};
  let entries = [];
  try {
    entries = readdirSync(TENANTS_DIR);
  } catch (e) {
    console.warn(TAG + " cannot read .cex/tenants -> empty registry: " + msg(e));
    return registry;
  }
  for (const entry of entries) {
    const themePath = join(TENANTS_DIR, entry, "admin_theme.json");
    if (!existsSync(themePath)) continue;
    const slug = String(entry).trim();
    if (!isValidSlug(slug)) {
      console.warn(TAG + " skip '" + entry + "' (no valid slug)");
      continue;
    }
    let parsed;
    try {
      parsed = JSON.parse(readFileSync(themePath, "utf8"));
    } catch (e) {
      console.warn(TAG + " skip '" + entry + "' (parse error): " + msg(e));
      continue;
    }
    const projected = projectEntry(parsed, slug);
    if (!projected) {
      console.warn(TAG + " skip '" + entry + "' (not a cex_admin_theme output shape)");
      continue;
    }
    registry[slug] = projected;
  }
  return registry;
}

function main() {
  // DISTILLED-REPO SAFETY: no .cex/tenants dir -> DO NOT touch the committed registry
  // (a distilled repo's own carried entry must survive `npm run dev`).
  let tenantsDirExists = false;
  try {
    tenantsDirExists = existsSync(TENANTS_DIR) && statSync(TENANTS_DIR).isDirectory();
  } catch (e) {
    tenantsDirExists = false;
  }
  if (!tenantsDirExists) {
    console.log(TAG + " no .cex/tenants dir -> keeping the committed registry untouched");
    return;
  }
  let registry = {};
  try {
    registry = collect();
  } catch (e) {
    console.warn(TAG + " unexpected error -> empty registry: " + msg(e));
    registry = {};
  }
  try {
    writeFileSync(OUT_FILE, JSON.stringify(registry, null, 2) + "\n", "utf8");
    const n = Object.keys(registry).length;
    console.log(
      TAG + " wrote " + n + " generated admin theme(s) -> lib/generatedAdminThemes.json" +
        (n > 0 ? " [" + Object.keys(registry).join(", ") + "]" : ""),
    );
  } catch (e) {
    // A write failure leaves the previous registry in place -- still non-fatal for dev.
    console.error(TAG + " FAILED to write registry (keeping previous): " + msg(e));
  }
  // ALWAYS exit 0 -- a predev step must never block `next dev`.
}

main();
