// =============================================================================
// run.mjs -- zero-new-dependency runner for the field-manifest parity gate.
// =============================================================================
//
// The dashboard's test runner (vitest) is jsdom-oriented; this parity gate is a
// pure-node behavior pin that the spec asks to run as a standalone exit-0/1 gate
// (the reference __parity__ pattern). esbuild IS present transitively (vitest ->
// @vitejs/plugin-react -> esbuild), so this runner uses esbuild's build API to
// bundle parity.ts (resolving the "@/..." alias to the dashboard root and inlining
// zod + the manifest + buildSchema) into a temp ESM module, then dynamically
// imports it. The parity script itself sets process.exit(0|1).
//
// Usage (from apps/dashboard_web):  node lib/field-manifest/__parity__/run.mjs

import { build } from "esbuild";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, resolve, join } from "node:path";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
// .../apps/dashboard_web/lib/field-manifest/__parity__ -> .../apps/dashboard_web
const dashboardRoot = resolve(__dirname, "../../..");
const entry = join(__dirname, "parity.ts");

const outDir = mkdtempSync(join(tmpdir(), "fm-parity-"));
const outFile = join(outDir, "parity.mjs");

try {
  await build({
    entryPoints: [entry],
    bundle: true,
    platform: "node",
    format: "esm",
    target: "node18",
    outfile: outFile,
    logLevel: "warning",
    // Resolve the dashboard's "@/..." path alias (tsconfig "@/*": ["./*"]) to the
    // dashboard root directory.
    alias: {
      "@": dashboardRoot,
    },
    // Keep node builtins external; bundle zod + the manifest + buildSchema in.
    external: ["node:*"],
  });

  // Dynamically import the bundled module. It calls process.exit() itself.
  await import(pathToFileURL(outFile).href);
} catch (err) {
  // Build/exec error => treat as a parity failure.
  console.error("[run.mjs] parity runner error:");
  console.error(err && err.stack ? err.stack : err);
  process.exitCode = 1;
} finally {
  try {
    rmSync(outDir, { recursive: true, force: true });
  } catch {
    /* best-effort temp cleanup */
  }
}
