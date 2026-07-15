// ----------------------------------------------------------------------------
// /api/onboard -- the DEV-ONLY URL-first onboarding loader (inc3). An operator pastes a
// tenant SITE URL; this handler runs the Python bootstrap (_tools/cex_tenant_bootstrap.py),
// which generates + PERSISTS a tenant_config under .cex/tenants/<slug>/ (gitignored, NO DB),
// then refreshes lib/generatedTenants.json so the preview at /t/<slug> updates. The human
// front-door for "1 input -> tenant".
//
// runtime = "nodejs": this needs child_process (spawn) -- it can NOT run on the edge.
//
// HARD GATE (the safety bar, both checks SERVER-SIDE in the handler):
//   * NODE_ENV === "development"  AND  CEXAI_ONBOARD_ENABLED === "1".
//   * In ANY prod/deployed build NODE_ENV !== "development" -> the gate is false -> 403 is
//     returned BEFORE any spawn. This route can NEVER spawn a process in prod.
//   * CEXAI_ONBOARD_ENABLED is a SERVER-ONLY env (NOT NEXT_PUBLIC_) -- it cannot be inlined
//     into the client bundle nor toggled from the browser.
//
// SSRF: the operator is dev-trusted, so we validate the URL SCHEME (http(s) only -- reject
// file:/ftp:/data:/javascript:) and pass a SPAWN TIMEOUT (~30s); we do NOT add a host
// allowlist (this is a dev tool). The slug is regex-validated (isValidSlug) BEFORE the
// spawn, and args are passed as an argv ARRAY to spawn (shell:false) -- so neither the URL
// nor the slug can ever be interpreted as a shell command.
//
// WRITES: only what the bootstrap writes -- under .cex/tenants/<slug>/ (gitignored). NEVER
// the DB / Supabase / prod (cex_prod_activate stays founder-gated).
//
// The PURE logic (the gate, scheme validation, slug derivation, manifest parse) lives in
// lib/onboard.ts and is unit-tested; THIS file owns only the spawn orchestration (which N07
// verifies LIVE). ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";

import { isValidSlug } from "@/lib/slug";
import {
  deriveSlugFromUrl,
  isOnboardEnabled,
  parseManifest,
  validateUrlScheme,
  type OnboardApiResponse,
} from "@/lib/onboard";

// child_process spawn -> requires the Node runtime (never the edge).
export const runtime = "nodejs";
// This route mutates local dev state (spawns + refreshes a file) -- never cache it.
export const dynamic = "force-dynamic";

// The Python interpreter. Defaults to the contract's bare `python`; an operator may point
// it at a specific interpreter via CEX_PYTHON_BIN for local dev (optional, degrade-safe).
const PYTHON_BIN = (process.env.CEX_PYTHON_BIN || "python").trim() || "python";
const BOOTSTRAP_TIMEOUT_MS = 30_000; // ~30s -- the SSRF/runaway-process guard.
const LOADER_TIMEOUT_MS = 5_000;

/** A small JSON Response helper (avoids any Response.json lib-target uncertainty). */
function json(body: OnboardApiResponse, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Resolve the repo ROOT robustly by walking UP from the process cwd looking for the marker
 *  file we are about to spawn (_tools/cex_tenant_bootstrap.py). This is independent of where
 *  Next sets cwd. Returns null if the marker is never found. */
function findRepoRoot(): string | null {
  let dir = process.cwd();
  for (let i = 0; i < 12; i++) {
    if (existsSync(join(dir, "_tools", "cex_tenant_bootstrap.py"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) break; // reached the filesystem root
    dir = parent;
  }
  return null;
}

interface ProcResult {
  code: number | null;
  stdout: string;
  stderr: string;
  timedOut: boolean;
  spawnError: NodeJS.ErrnoException | null;
}

/** Spawn a process (shell:false), collect stdout/stderr, and enforce a hard timeout that
 *  kills it. TOTAL: never rejects -- a spawn failure resolves with spawnError set.
 *  `env` (optional) REPLACES the child env when given -- callers merge over process.env
 *  themselves ({ ...process.env, KEY: "v" }); when absent, the child inherits process.env
 *  unchanged (spawn's own default), so env-less callers are byte-identical in behavior. */
function runProcess(
  cmd: string,
  args: string[],
  opts: { cwd: string; timeoutMs: number; env?: NodeJS.ProcessEnv },
): Promise<ProcResult> {
  return new Promise((resolveResult) => {
    let stdout = "";
    let stderr = "";
    let timedOut = false;
    let settled = false;

    const finish = (r: ProcResult) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolveResult(r);
    };

    let child;
    try {
      child = spawn(cmd, args, {
        cwd: opts.cwd,
        shell: false,
        windowsHide: true,
        env: opts.env, // undefined -> inherit process.env (spawn's own default)
      });
    } catch (err) {
      // Synchronous spawn failure (rare) -- resolve with the error rather than throw.
      resolveResult({
        code: null,
        stdout: "",
        stderr: "",
        timedOut: false,
        spawnError: err as NodeJS.ErrnoException,
      });
      return;
    }

    const timer = setTimeout(() => {
      timedOut = true;
      try {
        child.kill("SIGKILL");
      } catch {
        /* already gone */
      }
    }, opts.timeoutMs);

    child.stdout?.on("data", (d: Buffer) => {
      stdout += d.toString();
    });
    child.stderr?.on("data", (d: Buffer) => {
      stderr += d.toString();
    });
    child.on("error", (err: NodeJS.ErrnoException) => {
      finish({ code: null, stdout, stderr, timedOut, spawnError: err });
    });
    child.on("close", (code: number | null) => {
      finish({ code, stdout, stderr, timedOut, spawnError: null });
    });
  });
}

export async function POST(request: Request): Promise<Response> {
  // --- 1. HARD DEV GATE (server-side). Refuse BEFORE reading the body or spawning. ---
  if (!isOnboardEnabled(process.env)) {
    return json(
      {
        ok: false,
        previewPath: null,
        errors: [
          "/onboard is DEV-ONLY. It is enabled only when NODE_ENV=development AND the " +
            "server-only CEXAI_ONBOARD_ENABLED=1. It can never run in a prod/deployed build.",
        ],
      },
      403,
    );
  }

  // --- parse the JSON body (a malformed body is a 400, never a crash). ---
  let body: { url?: unknown; slug?: unknown };
  try {
    body = (await request.json()) as { url?: unknown; slug?: unknown };
  } catch {
    return json({ ok: false, previewPath: null, errors: ["invalid JSON body"] }, 400);
  }

  const url = typeof body.url === "string" ? body.url.trim() : "";
  if (!url) {
    return json({ ok: false, previewPath: null, errors: ["'url' is required"] }, 400);
  }

  // --- 2. URL scheme validation (http(s) only -- the SSRF scheme guard). ---
  if (!validateUrlScheme(url)) {
    return json(
      {
        ok: false,
        previewPath: null,
        errors: ["'url' must be an http(s) URL (file:/ftp:/data:/javascript: are rejected)"],
      },
      400,
    );
  }

  // --- 3. slug: explicit body.slug OR derived from the host; MUST pass isValidSlug. ---
  const requestedSlug = typeof body.slug === "string" ? body.slug.trim() : "";
  const slug = requestedSlug || deriveSlugFromUrl(url) || "";
  if (!slug || !isValidSlug(slug)) {
    return json(
      {
        ok: false,
        previewPath: null,
        errors: [
          requestedSlug
            ? "'slug' is invalid -- must match ^[a-z0-9][a-z0-9_-]{0,63}$"
            : "could not derive a valid slug from the URL host -- pass an explicit 'slug'",
        ],
      },
      400,
    );
  }

  // --- resolve the repo-root cwd (robustly, from wherever Next set the process cwd). ---
  const repoRoot = findRepoRoot();
  if (!repoRoot) {
    return json(
      {
        ok: false,
        previewPath: null,
        errors: ["could not resolve the repo root (_tools/cex_tenant_bootstrap.py not found)"],
      },
      500,
    );
  }
  const appDir = join(repoRoot, "apps", "public_site");

  // --- 4. spawn the Python bootstrap (argv array -> no shell injection; ~30s timeout). ---
  const boot = await runProcess(
    PYTHON_BIN,
    [
      "_tools/cex_tenant_bootstrap.py",
      "--source",
      url,
      "--tenant",
      slug,
      "--persist-config",
      "--json",
    ],
    { cwd: repoRoot, timeoutMs: BOOTSTRAP_TIMEOUT_MS },
  );

  if (boot.timedOut) {
    return json(
      { ok: false, previewPath: null, errors: ["bootstrap timed out (~30s)"] },
      503,
    );
  }
  if (boot.spawnError) {
    const why =
      boot.spawnError.code === "ENOENT"
        ? `'${PYTHON_BIN}' was not found on PATH (set CEX_PYTHON_BIN)`
        : `bootstrap spawn failed: ${boot.spawnError.code || boot.spawnError.message}`;
    return json({ ok: false, previewPath: null, errors: [why] }, 500);
  }

  // The bootstrap is TOTAL: with --json it ALWAYS prints the manifest (and exits 1 on a soft
  // ok:false). So we parse stdout regardless of exit code; only a NON-parseable stdout is a
  // transport failure (500). A parsed ok:false is surfaced HONESTLY at 200 (the page renders
  // manifest.errors) -- it is an application outcome, not a spawn failure.
  const parsed = parseManifest(boot.stdout);
  if (!parsed.manifest) {
    return json(
      {
        ok: false,
        previewPath: null,
        errors: [
          "could not parse the bootstrap manifest",
          parsed.error,
          (boot.stderr || "").trim().slice(0, 400),
        ].filter(Boolean) as string[],
      },
      500,
    );
  }

  const m = parsed.manifest;
  const tenantId = typeof m.tenant_id === "string" && m.tenant_id ? m.tenant_id : slug;

  // --- 5. on ok && persisted: refresh lib/generatedTenants.json so the preview updates. ---
  //         A loader failure must NOT fail the response (degrade-never).
  if (m.ok === true && m.tenant_config_persisted === true) {
    // process.execPath = the running Node binary (robust; no reliance on "node" in PATH).
    // CEX_PREVIEW_TENANTS=1 goes to THIS CHILD ONLY (merged over process.env -- never set
    // process-wide): this refresh is a deliberate, user-initiated post-onboard action, so
    // it is sanctioned to open the loader's opt-in gate; the ambient `predev` run of the
    // SAME script stays gated (see scripts/load-generated-tenants.mjs OPT-IN GATE).
    await runProcess(process.execPath, ["scripts/load-generated-tenants.mjs"], {
      cwd: appDir,
      timeoutMs: LOADER_TIMEOUT_MS,
      env: { ...process.env, CEX_PREVIEW_TENANTS: "1" },
    });
  }

  // --- 6. return the honest manifest projection + the preview path. ---
  const previewPath = `/t/${tenantId}`;
  return json(
    {
      ok: m.ok === true,
      tenant_id: tenantId,
      tenant_config_path: typeof m.tenant_config_path === "string" ? m.tenant_config_path : "",
      tenant_config_persisted: m.tenant_config_persisted === true,
      brand: m.brand ?? null,
      business_shape: (m.business_shape as Record<string, unknown> | null) ?? null,
      errors: Array.isArray(m.errors) ? (m.errors as string[]) : [],
      next_steps: Array.isArray(m.next_steps) ? (m.next_steps as string[]) : [],
      previewPath,
    },
    200,
  );
}
