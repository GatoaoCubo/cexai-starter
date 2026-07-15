import path from "node:path";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Repo-relative root (forward slashes so the alias regex replacement is clean on
// every platform, Windows included).
const root = path.dirname(fileURLToPath(import.meta.url)).replace(/\\/g, "/");

// ----------------------------------------------------------------------------
// Vitest -- the public site's test runner. MIRRORS apps/dashboard_web/vitest.
// config.ts: jsdom + React plugin so component smoke tests render in a DOM; the
// ``@/`` alias mirrors tsconfig paths. No globals -- each test imports
// { describe, it, expect } from "vitest". The setup file wires jest-dom matchers.
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
