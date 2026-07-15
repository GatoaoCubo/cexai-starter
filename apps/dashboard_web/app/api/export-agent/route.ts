// ----------------------------------------------------------------------------
// /api/export-agent -- the DEV-ONLY "Exportar agente" route. The dashboard sends
// { tenant, capability, target }; this handler runs the Python tool
// (_tools/cex_export_agent.py), which assembles a portable, single-capability agent
// package (manifest.yaml + system_instruction.md + agent_card.json + the target file
// + README) and zips it. On success the route STREAMS the zip back as a download; on
// any refusal it returns the tool's honest JSON error.
//
// runtime = "nodejs": this needs child_process (spawn) -- it can NOT run on the edge.
//
// SECURITY MODEL -- MIRRORS app/api/onboard/route.ts (apps/public_site) exactly:
//   * HARD DEV GATE (server-side, BEFORE any spawn): NODE_ENV==="development" AND the
//     server-only CEXAI_EXPORT_ENABLED==="1". In any prod/deployed build the gate is false
//     -> 403. CEXAI_EXPORT_ENABLED is NOT a NEXT_PUBLIC_ var (cannot be toggled from the
//     browser). (lib/exportAgent.isExportEnabled.)
//   * INPUT VALIDATION (BEFORE spawn): tenant + capability MUST pass isValidSlug
//     (^[a-z0-9][a-z0-9_-]{0,63}$); target MUST be one of customgpt|claude-md|mcp.
//     (lib/exportAgent.validateExportRequest.)
//   * shell:false ARGV ARRAY: the tool is spawned with an argv array, never a shell string
//     -- the slug/target can never be interpreted as a shell command. Plus a spawn TIMEOUT.
//   * WRITES: only what the tool writes, into a FRESH per-request TEMP dir (os.tmpdir()),
//     cleaned up after the zip is read. NEVER the DB / Supabase / prod. The tool itself
//     also fail-closes its out-dir to the repo root or the system temp dir.
//
// The PURE logic (the gate, slug/target validation, manifest parse) lives in
// lib/exportAgent.ts and is unit-tested; THIS file owns only the spawn orchestration.
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";

import {
  exportZipFilename,
  isExportEnabled,
  parseExportManifest,
  validateExportRequest,
  type ExportApiError,
} from "@/lib/exportAgent";

// child_process spawn -> requires the Node runtime (never the edge).
export const runtime = "nodejs";
// This route runs a process + reads a file -- never cache it.
export const dynamic = "force-dynamic";

// The Python interpreter (mirrors onboard): bare `python`, overridable via CEX_PYTHON_BIN.
const PYTHON_BIN = (process.env.CEX_PYTHON_BIN || "python").trim() || "python";
const EXPORT_TIMEOUT_MS = 30_000; // ~30s -- the runaway-process guard.
// A zip larger than this is refused (a sane upper bound; a scoped agent package is tiny).
const MAX_ZIP_BYTES = 8 * 1024 * 1024;

/** A small JSON Response helper for the error path (the success path streams the zip). */
function json(body: ExportApiError, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Resolve the repo ROOT by walking UP from cwd looking for the tool we are about to spawn
 *  (_tools/cex_export_agent.py). Independent of where Next set cwd. Null if never found. */
function findRepoRoot(): string | null {
  let dir = process.cwd();
  for (let i = 0; i < 12; i++) {
    if (existsSync(join(dir, "_tools", "cex_export_agent.py"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) break;
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

/** Spawn a process (shell:false), collect stdout/stderr, enforce a hard kill timeout.
 *  TOTAL: never rejects -- a spawn failure resolves with spawnError set. */
function runProcess(
  cmd: string,
  args: string[],
  opts: { cwd: string; timeoutMs: number },
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
      child = spawn(cmd, args, { cwd: opts.cwd, shell: false, windowsHide: true });
    } catch (err) {
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
  if (!isExportEnabled(process.env)) {
    return json(
      {
        ok: false,
        reason: "disabled",
        errors: [
          "/api/export-agent is DEV-ONLY. It is enabled only when NODE_ENV=development AND " +
            "the server-only CEXAI_EXPORT_ENABLED=1. It can never run in a prod/deployed build.",
        ],
      },
      403,
    );
  }

  // --- parse the JSON body (a malformed body is a 400, never a crash). ---
  let body: { tenant?: unknown; capability?: unknown; target?: unknown };
  try {
    body = (await request.json()) as {
      tenant?: unknown;
      capability?: unknown;
      target?: unknown;
    };
  } catch {
    return json({ ok: false, reason: "bad_body", errors: ["invalid JSON body"] }, 400);
  }

  // --- 2. INPUT VALIDATION (slug + target allowlist) BEFORE any spawn. ---
  const v = validateExportRequest(body);
  if (!v.ok) {
    return json({ ok: false, reason: "invalid_request", errors: v.errors }, 400);
  }

  // --- resolve the repo-root cwd (robustly, from wherever Next set the process cwd). ---
  const repoRoot = findRepoRoot();
  if (!repoRoot) {
    return json(
      {
        ok: false,
        reason: "repo_root_not_found",
        errors: ["could not resolve the repo root (_tools/cex_export_agent.py not found)"],
      },
      500,
    );
  }

  // --- 3. a FRESH per-request temp dir for the bundle (the tool's --out). ---
  let tmpDir: string;
  try {
    tmpDir = mkdtempSync(join(tmpdir(), "cex-export-"));
  } catch (err) {
    return json(
      {
        ok: false,
        reason: "tmp_failed",
        errors: [`could not create a temp dir: ${(err as Error).message}`],
      },
      500,
    );
  }

  try {
    // --- 4. spawn the Python tool (argv array -> no shell injection; ~30s timeout). ---
    const proc = await runProcess(
      PYTHON_BIN,
      [
        "_tools/cex_export_agent.py",
        "--tenant",
        v.tenant,
        "--capability",
        v.capability,
        "--target",
        v.target,
        "--out",
        tmpDir,
        "--json",
      ],
      { cwd: repoRoot, timeoutMs: EXPORT_TIMEOUT_MS },
    );

    if (proc.timedOut) {
      return json({ ok: false, reason: "timeout", errors: ["export timed out (~30s)"] }, 503);
    }
    if (proc.spawnError) {
      const why =
        proc.spawnError.code === "ENOENT"
          ? `'${PYTHON_BIN}' was not found on PATH (set CEX_PYTHON_BIN)`
          : `export spawn failed: ${proc.spawnError.code || proc.spawnError.message}`;
      return json({ ok: false, reason: "spawn_failed", errors: [why] }, 500);
    }

    // The tool is TOTAL with --json: it ALWAYS prints a manifest (ok:true) or an honest
    // error object (ok:false). Parse stdout regardless of exit code; only NON-parseable
    // stdout is a transport failure (500).
    const parsed = parseExportManifest(proc.stdout);
    if (!parsed.manifest) {
      return json(
        {
          ok: false,
          reason: "unparseable",
          errors: [
            "could not parse the export manifest",
            parsed.error,
            (proc.stderr || "").trim().slice(0, 400),
          ].filter(Boolean) as string[],
        },
        500,
      );
    }

    const m = parsed.manifest;
    if (m.ok !== true) {
      // An honest, fail-closed refusal from the tool (invalid/frozen/unresolved capability).
      return json(
        {
          ok: false,
          reason: typeof m.reason === "string" ? m.reason : "export_failed",
          errors: Array.isArray(m.errors) && m.errors.length ? m.errors : ["export refused"],
        },
        422,
      );
    }

    // --- 5. read the produced zip + stream it back as a download. ---
    const zipPath = typeof m.zip_path === "string" ? m.zip_path : "";
    if (!zipPath || !existsSync(zipPath)) {
      return json(
        { ok: false, reason: "zip_missing", errors: ["the export produced no zip"] },
        500,
      );
    }
    let zipBytes: Buffer;
    try {
      zipBytes = readFileSync(zipPath);
    } catch (err) {
      return json(
        {
          ok: false,
          reason: "zip_read_failed",
          errors: [`could not read the zip: ${(err as Error).message}`],
        },
        500,
      );
    }
    if (zipBytes.byteLength > MAX_ZIP_BYTES) {
      return json(
        { ok: false, reason: "zip_too_large", errors: ["the export zip exceeds the size cap"] },
        500,
      );
    }

    const filename = exportZipFilename(v.tenant, v.capability, v.target);
    // Copy into a fresh Uint8Array so the response body does not alias the Buffer we free.
    const out = new Uint8Array(zipBytes);
    return new Response(out, {
      status: 200,
      headers: {
        "content-type": "application/zip",
        "content-disposition": `attachment; filename="${filename}"`,
        "content-length": String(out.byteLength),
        "cache-control": "no-store",
        // Honest provenance the UI can surface (which fields were placeholder vs real).
        "x-export-notes": String((m.notes || []).length),
      },
    });
  } finally {
    // --- 6. clean up the temp bundle (best-effort; never fails the response). ---
    try {
      rmSync(tmpDir, { recursive: true, force: true });
    } catch {
      /* best-effort cleanup */
    }
  }
}
