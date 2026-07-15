// ----------------------------------------------------------------------------
// load-generated-tenants.mjs -- the DEV-ONLY half of the close-the-loop bridge.
//
// THE LOOP: a bootstrap GENERATES a tenant OFFLINE -> it writes the full manifest's
// tenant_config to `.cex/tenants/<slug>/tenant_config.json` (gitignored, the same
// per-tenant convention cex_tenant_onboard already uses). This script reads EVERY
// such file and writes the merged map into lib/generatedTenants.json -- the COMMITTED
// (default {}) registry that lib/tenantConfig statically imports. The preview then
// renders /t/<slug> for the generated tenant with NO hand-seeding.
//
// WIRING: package.json `predev` runs this before `next dev`, on EVERY `npm run dev` --
// but see OPT-IN GATE right below: by default this run is a NO-OP.
//
// OPT-IN GATE (env CEX_PREVIEW_TENANTS): by default -- the var unset, or set to anything
// other than the exact string "1" -- this script is a NO-OP: it prints one line and
// leaves lib/generatedTenants.json byte-untouched (no read of .cex/tenants, no write at
// all). Set CEX_PREVIEW_TENANTS=1 to opt in; the merge then runs exactly as described in
// THE LOOP above. This exists because the ambient predev run used to silently merge
// whatever LOCAL tenants exist on THIS machine (e.g. real client slugs under
// .cex/tenants/) into the TRACKED registry file on every `npm run dev` -- 2 real
// incidents, 2026-07-11, both hand-reverted. app/api/onboard/route.ts's own runtime
// refresh invokes this SAME script but distinguishes itself: it merges
// CEX_PREVIEW_TENANTS=1 into THAT CHILD's env only (deliberate, user-initiated refresh =
// sanctioned), so the ambient predev run stays a no-op while onboarding keeps working.
//
// CLIENT-SAFE BY DESIGN: this script only PRE-COMPUTES a JSON file at dev time. The app
// itself does a STATIC `import ... from "@/lib/generatedTenants.json"` (which bundles into
// BOTH the server and the CLIENT) -- it never reads .cex/tenants at runtime. So the
// generated tenant resolves client-side (HomeView is a client component) without any
// server-only fs read.
//
// PROD-SAFE: this never runs in prod (no `next dev`), the committed registry default is {},
// and prod resolves tenants from the backend (NEXT_PUBLIC_API_URL) -- never from .cex.
// This NEVER writes the DB.
//
// DEGRADE-NEVER: every failure path writes (or keeps) an EMPTY registry and exits 0, so a
// missing/garbled .cex/tenants can NEVER block `next dev`. The TYPED validation +
// normalization (the brand.tokens + shape gate, the safe-empty defaults) lives in
// lib/tenantConfig -- this collector stays minimal: parse JSON, key by slug, write.
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
// scripts/ -> public_site/ -> apps/ -> repo root
const REPO_ROOT = resolve(HERE, "..", "..", "..");
const TENANTS_DIR = join(REPO_ROOT, ".cex", "tenants");
const OUT_FILE = resolve(HERE, "..", "lib", "generatedTenants.json");
const TAG = "[load-generated-tenants]";
const PREVIEW_ENV_VAR = "CEX_PREVIEW_TENANTS";

/** True only when the opt-in flag is the EXACT string "1" (mirrors the isOnboardEnabled
 *  exact-match convention elsewhere in this app -- "true"/"yes"/"0" do NOT enable it). */
function isPreviewEnabled() {
  return process.env[PREVIEW_ENV_VAR] === "1";
}

// Mirror lib/slug.ts SLUG_RE (the backend's _SLUG_RE): a leading [a-z0-9], then up to 63
// more [a-z0-9_-]. Keeps a bad path segment out of the registry keys.
const SLUG_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;

function isValidSlug(s) {
  return typeof s === "string" && SLUG_RE.test(s.trim());
}

/** Collect every `.cex/tenants/<slug>/tenant_config.json` into a { slug: config } map.
 *  Degrade-never: any error on a single tenant skips THAT tenant, never the whole run. */
function collect() {
  const registry = {};
  if (!existsSync(TENANTS_DIR) || !statSync(TENANTS_DIR).isDirectory()) {
    console.warn(TAG + " no .cex/tenants dir -> empty registry");
    return registry;
  }
  let entries = [];
  try {
    entries = readdirSync(TENANTS_DIR);
  } catch (e) {
    console.warn(TAG + " cannot read .cex/tenants -> empty registry: " + msg(e));
    return registry;
  }
  for (const entry of entries) {
    const cfgPath = join(TENANTS_DIR, entry, "tenant_config.json");
    if (!existsSync(cfgPath)) continue;
    let parsed;
    try {
      parsed = JSON.parse(readFileSync(cfgPath, "utf8"));
    } catch (e) {
      console.warn(TAG + " skip '" + entry + "' (parse error): " + msg(e));
      continue;
    }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      console.warn(TAG + " skip '" + entry + "' (not a JSON object)");
      continue;
    }
    // Key by the config's own slug when valid, else the directory name (both must pass the
    // slug allowlist; a malformed slug is dropped so it can never become a registry key).
    const slug = isValidSlug(parsed.slug) ? parsed.slug.trim() : String(entry).trim();
    if (!isValidSlug(slug)) {
      console.warn(TAG + " skip '" + entry + "' (no valid slug)");
      continue;
    }
    registry[slug] = parsed;
  }
  return registry;
}

function msg(e) {
  return e && e.message ? e.message : String(e);
}

function main() {
  if (!isPreviewEnabled()) {
    // NO-OP: do not even read .cex/tenants, and do not touch OUT_FILE at all -- the
    // tracked file must stay byte-untouched (see OPT-IN GATE in the header comment).
    console.log(
      TAG + " preview tenant merge is OFF (default) -- lib/generatedTenants.json left " +
        "untouched. Set " + PREVIEW_ENV_VAR + "=1 to opt in and merge " +
        ".cex/tenants/*/tenant_config.json into the preview registry.",
    );
    return; // ALWAYS exit 0 -- a predev step must never block `next dev`.
  }
  let registry = {};
  try {
    registry = collect();
  } catch (e) {
    // Belt-and-braces: any unexpected error still yields an empty registry (never throws).
    console.warn(TAG + " unexpected error -> empty registry: " + msg(e));
    registry = {};
  }
  try {
    writeFileSync(OUT_FILE, JSON.stringify(registry, null, 2) + "\n", "utf8");
    const n = Object.keys(registry).length;
    console.log(
      TAG + " wrote " + n + " generated tenant(s) -> lib/generatedTenants.json" +
        (n > 0 ? " [" + Object.keys(registry).join(", ") + "]" : ""),
    );
  } catch (e) {
    // A write failure leaves the committed default in place -- still non-fatal for dev.
    console.error(TAG + " FAILED to write registry (keeping committed default): " + msg(e));
  }
  // ALWAYS exit 0 -- a predev step must never block `next dev`.
}

main();
