// ----------------------------------------------------------------------------
// exportAgent -- the PURE, testable core of the DEV-ONLY "Exportar agente" flow.
//
// The route (app/api/export-agent/route.ts) owns the spawn ORCHESTRATION
// (child_process -> _tools/cex_export_agent.py -> read the zip -> stream it back);
// everything that can be reasoned about WITHOUT spawning a process lives HERE so it
// is unit-tested in isolation. MIRRORS lib/onboard.ts (the /api/onboard pattern):
//
//   * isExportEnabled(env) -- the HARD DEV GATE. true ONLY when NODE_ENV=="development"
//     AND the server-only opt-in CEXAI_EXPORT_ENABLED=="1". In any prod/deployed build
//     NODE_ENV!=="development" so the gate is false and the route returns 403 BEFORE any
//     spawn. CEXAI_EXPORT_ENABLED is NOT a NEXT_PUBLIC_ var -> it can never be inlined into
//     the client bundle nor toggled from the browser.
//   * isValidExportTarget(t) -- the render target allowlist (customgpt | claude-md | mcp).
//   * validateExportRequest(body) -- tenant + capability MUST pass isValidSlug (the SAME
//     ^[a-z0-9][a-z0-9_-]{0,63}$ allowlist the backend enforces); target MUST be allowed.
//     PURE: returns { ok, tenant, capability, target, errors } -- never throws, never spawns.
//   * parseExportManifest(stdout) -- parse the tool's --json manifest off captured stdout.
//     TOTAL: a valid object (ok:true OR ok:false-with-errors) returns it; non-JSON -> error.
//
// PURE + TOTAL: none of these throw, touch the filesystem, or hit the network. ASCII-only
// + diacritic-free (house style).
// ----------------------------------------------------------------------------

// The strict slug allowlist -- IDENTICAL to apps/dashboard_api/public_reader._SLUG_RE and
// _tools/cex_export_agent._SLUG_RE (^[a-z0-9][a-z0-9_-]{0,63}$). Forbids a leading -/_/. and
// any "." (so ".." can never match) and caps length at 64. Inlined (no cross-app import) so
// this module is self-contained; the backend remains the authority.
const SLUG_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;

/** True iff ``value`` is a well-formed slug. Trims first so a stray space is rejected by
 *  shape, not silently accepted. PURE + TOTAL (never throws). */
function isValidSlug(value: unknown): boolean {
  return typeof value === "string" && SLUG_RE.test(value.trim());
}

/** The render targets the export tool supports (mirrors cex_export_agent.VALID_TARGETS). */
export const EXPORT_TARGETS = ["customgpt", "claude-md", "mcp"] as const;
export type ExportTarget = (typeof EXPORT_TARGETS)[number];

/** Human labels for the target picker (the runtime each target imports into). */
export const EXPORT_TARGET_LABELS: Record<ExportTarget, string> = {
  customgpt: "GPT Builder",
  "claude-md": "Claude Project",
  mcp: "MCP",
};

/** The env subset the dev gate reads (the route passes process.env). */
export interface ExportEnv {
  NODE_ENV?: string;
  CEXAI_EXPORT_ENABLED?: string;
}

/** The request body the route accepts + the UI sends. */
export interface ExportRequest {
  tenant: string;
  capability: string;
  target: ExportTarget;
}

/** The shape cex_export_agent.py emits with --json (loose-typed; the route never assumes a
 *  key is present). On success the zip lands at ``zip_path``; on a fail-closed refusal it
 *  carries ok:false + reason + errors. */
export interface ExportManifest {
  ok?: boolean;
  reason?: string;
  tenant?: string;
  capability?: string;
  target?: string;
  kind?: string;
  pillar?: string;
  nucleus?: string;
  bundle_dir?: string;
  zip_path?: string;
  files?: { file: string; bytes: number }[];
  target_file?: string;
  target_file_head?: string;
  notes?: string[];
  errors?: string[];
  [key: string]: unknown;
}

/** The JSON the route returns on the ERROR path (the success path streams the zip binary). */
export interface ExportApiError {
  ok: false;
  reason?: string;
  errors: string[];
}

/** The HARD DEV GATE. true ONLY in a local dev build that EXPLICITLY opted in. Both checks
 *  are server-side (the route passes process.env):
 *    1. NODE_ENV === "development"      -- never true in a prod/deployed build.
 *    2. CEXAI_EXPORT_ENABLED === "1"    -- a SERVER-ONLY env (NOT NEXT_PUBLIC_), so it can
 *       never be inlined into the client bundle / toggled from the browser.
 *  When false the route returns 403 BEFORE any spawn. TOTAL (never throws). */
export function isExportEnabled(env: ExportEnv | undefined | null): boolean {
  if (!env) return false;
  return env.NODE_ENV === "development" && env.CEXAI_EXPORT_ENABLED === "1";
}

/** True iff ``t`` is one of the supported render targets. */
export function isValidExportTarget(t: unknown): t is ExportTarget {
  return typeof t === "string" && (EXPORT_TARGETS as readonly string[]).includes(t);
}

/** Validate + normalize an export request. PURE + TOTAL: returns the normalized fields plus
 *  an ``ok`` flag and an ``errors`` list -- never throws. The route refuses (400) when
 *  ok is false, BEFORE resolving the repo root or spawning anything. */
export function validateExportRequest(body: {
  tenant?: unknown;
  capability?: unknown;
  target?: unknown;
}): {
  ok: boolean;
  tenant: string;
  capability: string;
  target: ExportTarget | "";
  errors: string[];
} {
  const errors: string[] = [];
  const tenant = typeof body.tenant === "string" ? body.tenant.trim() : "";
  const capability =
    typeof body.capability === "string" ? body.capability.trim() : "";
  const target = typeof body.target === "string" ? body.target.trim() : "";

  if (!isValidSlug(tenant)) {
    errors.push("'tenant' is invalid -- must match ^[a-z0-9][a-z0-9_-]{0,63}$");
  }
  if (!isValidSlug(capability)) {
    errors.push(
      "'capability' is invalid -- must match ^[a-z0-9][a-z0-9_-]{0,63}$ (an overlay " +
        "capability whose slug is a free-text phrase with spaces cannot be exported here)",
    );
  }
  if (!isValidExportTarget(target)) {
    errors.push(`'target' must be one of ${EXPORT_TARGETS.join(", ")}`);
  }

  return {
    ok: errors.length === 0,
    tenant,
    capability,
    target: isValidExportTarget(target) ? target : "",
    errors,
  };
}

/** A safe download filename for a bundle (slug-shaped inputs -> always filesystem-safe). */
export function exportZipFilename(
  tenant: string,
  capability: string,
  target: string,
): string {
  return `${tenant}_${capability}_${target}_agent.zip`;
}

/** Parse the tool's --json manifest off captured stdout. TOTAL -- never throws:
 *    * a valid JSON object (ok:true OR ok:false-with-errors) -> { manifest, error:null }
 *    * empty / non-JSON / a JSON non-object -> { manifest:null, error }
 *  Defensive: if the whole string is not valid JSON it retries on the outermost { ... }
 *  slice, so a stray log line on stdout still yields the manifest (mirrors parseManifest). */
export function parseExportManifest(
  stdout: unknown,
): { manifest: ExportManifest; error: null } | { manifest: null; error: string } {
  const text = typeof stdout === "string" ? stdout.trim() : "";
  if (!text) return { manifest: null, error: "empty export-tool output" };

  const direct = tryParseObject(text);
  if (direct) return { manifest: direct, error: null };

  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start >= 0 && end > start) {
    const sliced = tryParseObject(text.slice(start, end + 1));
    if (sliced) return { manifest: sliced, error: null };
  }
  return { manifest: null, error: "export-tool stdout was not a JSON object" };
}

/** JSON.parse that returns a plain object or null (never throws, rejects arrays/scalars). */
function tryParseObject(s: string): ExportManifest | null {
  try {
    const value = JSON.parse(s);
    if (value && typeof value === "object" && !Array.isArray(value)) {
      return value as ExportManifest;
    }
    return null;
  } catch {
    return null;
  }
}
