// ----------------------------------------------------------------------------
// /api/intake -- the DEV-ONLY resolve seam for the /intake form (R-283). The
// browser posts the form_v1 answers OBJECT; this handler writes the answers
// YAML under .cex/runtime/intake/ (a gitignored runtime surface) and runs the
// CLI resolver (_tools/cex_ingest_registry.py --resolve), returning an HONEST
// projection of its exit code + stable ASCII output. It NEVER runs
// cex_bootstrap: brand-state mutation stays operator-explicit -- the consume
// command is DISPLAYED by the page, not executed.
//
// runtime = "nodejs": needs child_process (spawn) -- can NOT run on the edge.
//
// HARD GATE (same family as /api/onboard, both checks SERVER-SIDE):
//   * isOnboardEnabled(process.env): NODE_ENV === "development" AND
//     CEXAI_ONBOARD_ENABLED === "1". In ANY prod/deployed build the gate is
//     false -> 403 BEFORE any filesystem write or spawn. The prod posture of
//     this app is PURE CLIENT (next.config.mjs) -- in prod the form's download
//     path is the only path, and this route refuses.
//
// SAFETY: the answers file NAME is server-generated (regex-guarded slug OR a
// timestamp -- user input never forms a path); args go to spawn as an argv
// ARRAY (shell:false) with a ~30s SIGKILL timeout; writes land ONLY under
// <repo>/.cex/runtime/intake/. The resolver itself is fail-closed (R-276
// credential drops, https-only links, unregistered-source refusal).
//
// WRINKLE (mined, honest): the resolver CLI has NO --json flag today -- this
// route parses exit code + its stable '[OK] resolved form_v1: ...' /
// '  [WARN] ...' / '[FAIL] ...' lines (lib/intake.parseResolveOutput, unit-
// tested). A cleaner follow-up adds --json to cex_ingest_registry.py main().
//
// The PURE logic (yaml text emission, output parsing, response types) lives in
// lib/intake.ts and is unit-tested; THIS file owns only the write + spawn
// orchestration (which N07 verifies LIVE). ASCII-only + diacritic-free.
// ----------------------------------------------------------------------------

import { spawn } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

import { isOnboardEnabled } from "@/lib/onboard";
import { isValidSlug } from "@/lib/slug";
import {
  answersToYamlText,
  bootstrapCommand,
  parseResolveOutput,
  type IntakeAnswers,
  type IntakeApiResponse,
} from "@/lib/intake";

// child_process spawn -> requires the Node runtime (never the edge).
export const runtime = "nodejs";
// This route mutates local dev state (writes a file + spawns) -- never cache it.
export const dynamic = "force-dynamic";

// The Python interpreter. Defaults to the contract's bare `python`; an operator
// may point at a specific interpreter via CEX_PYTHON_BIN (optional, degrade-safe).
const PYTHON_BIN = (process.env.CEX_PYTHON_BIN || "python").trim() || "python";
const RESOLVE_TIMEOUT_MS = 30_000; // the runaway-process guard (SIGKILL).

/** A small JSON Response helper (avoids any Response.json lib-target uncertainty). */
function json(body: IntakeApiResponse, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Resolve the repo ROOT by walking UP from the process cwd looking for the
 *  marker we are about to spawn (_tools/cex_ingest_registry.py). Independent of
 *  where Next sets cwd (mirrors /api/onboard's findRepoRoot). */
function findRepoRoot(): string | null {
  let dir = process.cwd();
  for (let i = 0; i < 12; i++) {
    if (existsSync(join(dir, "_tools", "cex_ingest_registry.py"))) return dir;
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

/** Spawn a process (shell:false), collect stdout/stderr, enforce a hard SIGKILL
 *  timeout. TOTAL: never rejects -- a spawn failure resolves with spawnError. */
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

/** Repo-relative display path with forward slashes (stable across OSes). */
function displayPath(parts: string[]): string {
  return parts.join("/");
}

export async function POST(request: Request): Promise<Response> {
  // --- 1. HARD DEV GATE (server-side). Refuse BEFORE reading the body. ------
  if (!isOnboardEnabled(process.env)) {
    return json(
      {
        ok: false,
        errors: [
          "/api/intake is DEV-ONLY. It is enabled only when NODE_ENV=development AND the " +
            "server-only CEXAI_ONBOARD_ENABLED=1 -- it can never run in a prod/deployed " +
            "build. Use 'Baixar answers YAML': the downloaded file feeds the SAME " +
            "resolver via the CLI (python _tools/cex_ingest_registry.py --resolve ...).",
        ],
      },
      403,
    );
  }

  // --- parse the JSON body (a malformed body is a 400, never a crash). ------
  let body: { answers?: unknown };
  try {
    body = (await request.json()) as { answers?: unknown };
  } catch {
    return json({ ok: false, errors: ["invalid JSON body"] }, 400);
  }
  const answers = body.answers;
  if (!answers || typeof answers !== "object" || Array.isArray(answers)) {
    return json(
      { ok: false, errors: ["'answers' must be the form_v1 answers object"] },
      400,
    );
  }
  // Mirror the resolver's own fail-closed version check early (it would refuse
  // anyway; refusing here saves the write + spawn).
  const formVersion = (answers as Record<string, unknown>).form_version;
  if (formVersion !== 1) {
    return json(
      { ok: false, errors: ["'answers.form_version' must be 1 (this resolver speaks 1)"] },
      400,
    );
  }

  // --- 2. server-generated file base name (user input NEVER forms a path). --
  const tenant = (answers as Record<string, unknown>).tenant;
  const rawSlug =
    tenant && typeof tenant === "object" && !Array.isArray(tenant)
      ? (tenant as Record<string, unknown>).slug
      : undefined;
  const slug = typeof rawSlug === "string" && isValidSlug(rawSlug.trim())
    ? rawSlug.trim()
    : "";
  const stamp = new Date()
    .toISOString()
    .replace(/[-:T]/g, "")
    .slice(0, 14); // YYYYMMDDHHMMSS
  const base = (slug || "intake") + "_" + stamp;

  // --- resolve the repo root (robustly, from wherever Next set the cwd). ----
  const repoRoot = findRepoRoot();
  if (!repoRoot) {
    return json(
      {
        ok: false,
        errors: ["could not resolve the repo root (_tools/cex_ingest_registry.py not found)"],
      },
      500,
    );
  }

  // --- 3. write the answers YAML under .cex/runtime/intake/ (gitignored). ---
  const relDir = [".cex", "runtime", "intake"];
  const relAnswers = displayPath([...relDir, base + "_answers.yaml"]);
  const relBrandInit = displayPath([...relDir, base + "_brand_init.yaml"]);
  const relProv = displayPath([...relDir, base + "_provenance.json"]);
  const relShape = displayPath([...relDir, base + "_shape.json"]);
  try {
    mkdirSync(join(repoRoot, ...relDir), { recursive: true });
    writeFileSync(
      join(repoRoot, ...relDir, base + "_answers.yaml"),
      answersToYamlText(answers as IntakeAnswers),
      "utf8",
    );
  } catch (err) {
    return json(
      {
        ok: false,
        errors: [
          "could not write the answers file: " +
            (err instanceof Error ? err.message : String(err)),
        ],
      },
      500,
    );
  }

  // --- 4. spawn the CLI resolver (argv array -> no shell; ~30s timeout). ----
  const proc = await runProcess(
    PYTHON_BIN,
    [
      "_tools/cex_ingest_registry.py",
      "--resolve",
      relAnswers,
      "--out",
      relBrandInit,
      "--provenance",
      relProv,
      "--emit-shape",
      relShape,
    ],
    { cwd: repoRoot, timeoutMs: RESOLVE_TIMEOUT_MS },
  );

  if (proc.timedOut) {
    return json(
      { ok: false, answers_path: relAnswers, errors: ["resolver timed out (~30s)"] },
      503,
    );
  }
  if (proc.spawnError) {
    const why =
      proc.spawnError.code === "ENOENT"
        ? "'" + PYTHON_BIN + "' was not found on PATH (set CEX_PYTHON_BIN)"
        : "resolver spawn failed: " + (proc.spawnError.code || proc.spawnError.message);
    return json({ ok: false, answers_path: relAnswers, errors: [why] }, 500);
  }

  // --- 5. honest projection: exit code + the CLI's stable ASCII lines. ------
  const parsed = parseResolveOutput(proc.stdout, proc.code);
  if (parsed.ok) {
    return json(
      {
        ok: true,
        summary: parsed.summary,
        resolver_warnings: parsed.warnings,
        answers_path: relAnswers,
        brand_init_path: relBrandInit,
        provenance_path: relProv,
        shape_path: relShape,
        // Displayed by the page, NEVER auto-run (operator-explicit consume).
        bootstrap_cmd: bootstrapCommand(slug || null, relBrandInit),
      },
      200,
    );
  }
  const errors = parsed.failures.length
    ? parsed.failures
    : ["resolver exited " + String(proc.code), (proc.stderr || "").trim().slice(0, 400)].filter(
        Boolean,
      );
  // An application-level refusal (fail-closed resolver) is surfaced HONESTLY at
  // 200 -- it is an outcome, not a transport failure (mirrors /api/onboard).
  return json(
    {
      ok: false,
      summary: parsed.summary,
      resolver_warnings: parsed.warnings,
      answers_path: relAnswers,
      errors,
    },
    200,
  );
}
