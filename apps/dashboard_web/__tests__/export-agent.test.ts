// Unit tests for lib/exportAgent -- the PURE core of the DEV-ONLY "Exportar agente" flow.
// Mirrors the onboard pure-core tests: the dev gate, the slug/target validation, the manifest
// parse. No spawn, no network, no filesystem (the route owns orchestration; this is pure).

import { describe, it, expect } from "vitest";
import {
  EXPORT_TARGETS,
  exportZipFilename,
  isExportEnabled,
  isValidExportTarget,
  parseExportManifest,
  validateExportRequest,
} from "@/lib/exportAgent";

describe("isExportEnabled (the hard dev gate)", () => {
  it("is true ONLY in development AND with the server-only flag set", () => {
    expect(isExportEnabled({ NODE_ENV: "development", CEXAI_EXPORT_ENABLED: "1" })).toBe(true);
  });

  it("is false in any prod/deployed build, even with the flag", () => {
    expect(isExportEnabled({ NODE_ENV: "production", CEXAI_EXPORT_ENABLED: "1" })).toBe(false);
  });

  it("is false in development WITHOUT the explicit opt-in flag", () => {
    expect(isExportEnabled({ NODE_ENV: "development" })).toBe(false);
    expect(isExportEnabled({ NODE_ENV: "development", CEXAI_EXPORT_ENABLED: "0" })).toBe(false);
  });

  it("is false for null/undefined env (total, never throws)", () => {
    expect(isExportEnabled(undefined)).toBe(false);
    expect(isExportEnabled(null)).toBe(false);
  });
});

describe("isValidExportTarget", () => {
  it("accepts exactly the supported targets", () => {
    for (const t of EXPORT_TARGETS) expect(isValidExportTarget(t)).toBe(true);
  });
  it("rejects anything else", () => {
    expect(isValidExportTarget("cursorrules")).toBe(false);
    expect(isValidExportTarget("")).toBe(false);
    expect(isValidExportTarget(42)).toBe(false);
    expect(isValidExportTarget(undefined)).toBe(false);
  });
});

describe("validateExportRequest (slug + target allowlist)", () => {
  it("accepts a well-formed request", () => {
    const v = validateExportRequest({
      tenant: "demo-orbit",
      capability: "ads",
      target: "customgpt",
    });
    expect(v.ok).toBe(true);
    expect(v.tenant).toBe("demo-orbit");
    expect(v.capability).toBe("ads");
    expect(v.target).toBe("customgpt");
    expect(v.errors).toEqual([]);
  });

  it("trims surrounding whitespace before validating", () => {
    const v = validateExportRequest({
      tenant: "  acme3 ",
      capability: " brandbook ",
      target: " claude-md ",
    });
    expect(v.ok).toBe(true);
    expect(v.tenant).toBe("acme3");
    expect(v.capability).toBe("brandbook");
    expect(v.target).toBe("claude-md");
  });

  it("rejects a bad tenant slug (uppercase / spaces / leading dash)", () => {
    expect(validateExportRequest({ tenant: "Bad", capability: "ads", target: "mcp" }).ok).toBe(
      false,
    );
    expect(
      validateExportRequest({ tenant: "has space", capability: "ads", target: "mcp" }).ok,
    ).toBe(false);
    expect(validateExportRequest({ tenant: "-x", capability: "ads", target: "mcp" }).ok).toBe(
      false,
    );
  });

  it("rejects a path-traversal attempt in either slug", () => {
    const v = validateExportRequest({
      tenant: "../etc",
      capability: "../../secret",
      target: "mcp",
    });
    expect(v.ok).toBe(false);
    expect(v.errors.length).toBeGreaterThanOrEqual(1);
  });

  it("rejects an unknown target and reports it", () => {
    const v = validateExportRequest({ tenant: "t", capability: "ads", target: "wat" });
    expect(v.ok).toBe(false);
    expect(v.target).toBe("");
    expect(v.errors.some((e) => e.includes("target"))).toBe(true);
  });

  it("collects all errors for an all-bad request", () => {
    const v = validateExportRequest({ tenant: "", capability: "", target: "" });
    expect(v.ok).toBe(false);
    expect(v.errors.length).toBe(3);
  });
});

describe("exportZipFilename", () => {
  it("composes a slug-safe download filename", () => {
    expect(exportZipFilename("demo-orbit", "ads", "customgpt")).toBe(
      "demo-orbit_ads_customgpt_agent.zip",
    );
  });
});

describe("parseExportManifest (total stdout parse)", () => {
  it("parses a clean ok:true manifest", () => {
    const out = JSON.stringify({ ok: true, zip_path: "/tmp/x.zip", target: "mcp" });
    const r = parseExportManifest(out);
    expect(r.manifest).not.toBeNull();
    expect(r.manifest?.ok).toBe(true);
    expect(r.manifest?.zip_path).toBe("/tmp/x.zip");
  });

  it("parses an ok:false refusal manifest", () => {
    const out = JSON.stringify({ ok: false, reason: "frozen_kind", errors: ["nope"] });
    const r = parseExportManifest(out);
    expect(r.manifest?.ok).toBe(false);
    expect(r.manifest?.reason).toBe("frozen_kind");
  });

  it("recovers a manifest embedded among stray log lines", () => {
    const out = 'WARN: something\n{"ok":true,"zip_path":"/t/a.zip"}\ntrailing';
    const r = parseExportManifest(out);
    expect(r.manifest?.ok).toBe(true);
    expect(r.manifest?.zip_path).toBe("/t/a.zip");
  });

  it("returns an error for empty / non-JSON / a JSON non-object", () => {
    expect(parseExportManifest("").manifest).toBeNull();
    expect(parseExportManifest("not json at all").manifest).toBeNull();
    expect(parseExportManifest("[1,2,3]").manifest).toBeNull();
    expect(parseExportManifest(undefined).manifest).toBeNull();
  });
});
