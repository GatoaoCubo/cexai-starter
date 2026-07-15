import path from "node:path";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Repo-relative root (forward slashes so the alias regex replacement is clean on
// every platform, Windows included).
const root = path.dirname(fileURLToPath(import.meta.url)).replace(/\\/g, "/");

// ----------------------------------------------------------------------------
// Vitest -- the dashboard's test runner (HARDEN mission). jsdom + React plugin so
// component smoke tests render in a DOM; the ``@/`` alias mirrors tsconfig paths.
// We do NOT use globals -- each test imports { describe, it, expect } from
// "vitest" so tsconfig needs no extra ``types`` entry (which would otherwise
// suppress the auto-included @types/*). The setup file wires jest-dom matchers.
// ----------------------------------------------------------------------------

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [{ find: /^@\//, replacement: root + "/" }],
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    include: ["__tests__/**/*.{test,spec}.{ts,tsx}"],
    css: false,
  },
});
