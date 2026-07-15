// Global test setup. Imported once per test file (vitest.config setupFiles).
//
//   * jest-dom/vitest extends vitest's expect with DOM matchers and augments the
//     Assertion types globally (this file is in the tsconfig program, so the
//     augmentation is visible to tsc everywhere).
//   * afterEach(cleanup) unmounts React trees between tests so renders do not leak.

import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
});
