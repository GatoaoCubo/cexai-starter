import { describe, it, expect } from "vitest";
import { execFileSync } from "node:child_process";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// ----------------------------------------------------------------------------
// loadGeneratedTenants -- the CEX_PREVIEW_TENANTS opt-in gate PROOF (node-side; this
// exercises the REAL scripts/load-generated-tenants.mjs by spawning it, the way its two
// callers do: package.json `predev` spawns it BARE (ambient env -> invariant 1), and
// app/api/onboard/route.ts spawns it with CEX_PREVIEW_TENANTS=1 merged over process.env
// for its deliberate, sanctioned post-onboard refresh (child-only -- exactly the merge
// mechanic invariant 2 pins; no separate route-specific case is needed).
//
// TWO invariants pinned:
//   1. FLAG ABSENT (or set to anything other than the exact string "1") -> a NO-OP: the
//      REAL committed lib/generatedTenants.json is byte-untouched (no read, no write).
//      Run directly against the REAL repo paths -- safe because nothing is ever written
//      on this path, so there is zero risk to the tracked file or to any other test file
//      that may statically import it in parallel.
//   2. FLAG=1 -> the merge runs: a throwaway fixture tenant is picked up and written into
//      the registry (shape asserted). This case is proven against a FULLY ISOLATED temp
//      copy of the script + its {scripts,lib}/.cex/tenants layout (one of the two
//      mechanics the handoff itself sanctions: "create under a temp .cex/tenants sandbox
//      or point the script's source dir via its existing resolution") -- so the REAL
//      committed file is never touched by this case either, and there is no window where
//      a concurrently-running test file could observe a partially-written real registry.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_DIR = resolve(HERE, "..");
const REAL_SCRIPT_REL = "scripts/load-generated-tenants.mjs";
const REAL_OUT_FILE = join(APP_DIR, "lib", "generatedTenants.json");
const REAL_SCRIPT_ABS = join(APP_DIR, REAL_SCRIPT_REL);
const FLAG = "CEX_PREVIEW_TENANTS";

// Captured ONCE, before any test in this file runs -- the actual committed bytes (do NOT
// assume a specific newline style; the checked-out file may be CRLF-normalized on this
// platform). Every "byte-identical" assertion below compares against THIS, never a
// hardcoded literal. Safe to capture at module scope: none of the cases below ever write
// to REAL_OUT_FILE (case 1/2 only read it; case 3 uses a fully separate temp sandbox).
const COMMITTED_BASELINE = readFileSync(REAL_OUT_FILE, "utf8");

/** Run a script with node (mirrors process.execPath usage in app/api/onboard/route.ts).
 *  Throws on a non-zero exit -- an implicit proof of the ALWAYS-exit-0 contract when a
 *  test does NOT expect a throw. */
function runNode(scriptAbsPath: string, cwd: string, env: NodeJS.ProcessEnv): string {
  return execFileSync(process.execPath, [scriptAbsPath], {
    cwd,
    env,
    encoding: "utf8",
  });
}

describe("load-generated-tenants.mjs -- CEX_PREVIEW_TENANTS opt-in gate", () => {
  it("flag ABSENT -> no-op: the REAL tracked file is byte-untouched", () => {
    const env = { ...process.env };
    delete env[FLAG];
    const stdout = runNode(REAL_SCRIPT_ABS, APP_DIR, env);
    expect(readFileSync(REAL_OUT_FILE, "utf8")).toBe(COMMITTED_BASELINE);
    expect(stdout).toContain(FLAG);
  });

  it("flag set to a non-'1' value -> STILL a no-op (exact-match gate, mirrors isOnboardEnabled)", () => {
    for (const badValue of ["true", "0", "yes", "TRUE"]) {
      const stdout = runNode(REAL_SCRIPT_ABS, APP_DIR, {
        ...process.env,
        [FLAG]: badValue,
      });
      expect(stdout).toContain(FLAG);
    }
    expect(readFileSync(REAL_OUT_FILE, "utf8")).toBe(COMMITTED_BASELINE);
  });

  it("flag=1 + a throwaway fixture tenant -> the merge runs (shape asserted), fully isolated", () => {
    // A FRESH temp root, laid out to mirror the real relative resolution the script's own
    // HERE/REPO_ROOT math depends on: <root>/apps/public_site/scripts/<script>,
    // <root>/apps/public_site/lib/, <root>/.cex/tenants/<slug>/tenant_config.json.
    const tmpRoot = mkdtempSync(join(tmpdir(), "cex-predev-gate-"));
    try {
      const tmpScriptsDir = join(tmpRoot, "apps", "public_site", "scripts");
      const tmpLibDir = join(tmpRoot, "apps", "public_site", "lib");
      const tmpTenantsDir = join(tmpRoot, ".cex", "tenants");
      const fixtureSlug = "zz_test_predev_gate_fixture";
      const fixtureDir = join(tmpTenantsDir, fixtureSlug);

      mkdirSync(tmpScriptsDir, { recursive: true });
      mkdirSync(tmpLibDir, { recursive: true });
      mkdirSync(fixtureDir, { recursive: true });

      // Copy the REAL script verbatim (byte-identical) into the sandbox -- this is the
      // SAME code under test, just anchored at a throwaway root instead of the repo root.
      writeFileSync(
        join(tmpScriptsDir, "load-generated-tenants.mjs"),
        readFileSync(REAL_SCRIPT_ABS, "utf8"),
        "utf8",
      );
      // Seed the sandbox's committed default with the ACTUAL real committed bytes (not a
      // guessed literal) -- the sandbox starts from an authentic committed-default snapshot.
      writeFileSync(join(tmpLibDir, "generatedTenants.json"), COMMITTED_BASELINE, "utf8");
      // The throwaway fixture tenant_config.json.
      writeFileSync(
        join(fixtureDir, "tenant_config.json"),
        JSON.stringify({
          slug: fixtureSlug,
          brand: { name: "ZZ Test Fixture", tokens: { brand: "0 0% 0%" } },
          shape: { vertical: "retail" },
        }),
        "utf8",
      );

      const stdout = runNode(
        join(tmpScriptsDir, "load-generated-tenants.mjs"),
        join(tmpRoot, "apps", "public_site"),
        // The SAME child-env mechanic app/api/onboard/route.ts uses for its deliberate
        // post-onboard refresh: FLAG=1 merged over process.env, child-only.
        { ...process.env, [FLAG]: "1" },
      );
      expect(stdout).toContain(fixtureSlug);

      const merged = JSON.parse(
        readFileSync(join(tmpLibDir, "generatedTenants.json"), "utf8"),
      );
      expect(merged[fixtureSlug]).toBeTruthy();
      expect(merged[fixtureSlug].brand.name).toBe("ZZ Test Fixture");
      expect(merged[fixtureSlug].shape.vertical).toBe("retail");
      expect(Object.keys(merged)).toEqual([fixtureSlug]);
    } finally {
      rmSync(tmpRoot, { recursive: true, force: true });
    }

    // The REAL committed file was never touched by this test at all.
    expect(readFileSync(REAL_OUT_FILE, "utf8")).toBe(COMMITTED_BASELINE);
  });
});
