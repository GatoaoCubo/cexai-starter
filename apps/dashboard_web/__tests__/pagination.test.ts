import { describe, it, expect } from "vitest";
import { paginate } from "@/lib/pagination";

// Pure-function unit tests for the pagination core (HARDEN mission).

const seq = (n: number) => Array.from({ length: n }, (_, i) => i + 1);

describe("paginate", () => {
  it("returns an empty, single page for an empty list", () => {
    const p = paginate<number>([], 1, 25);
    expect(p.items).toEqual([]);
    expect(p.page).toBe(1);
    expect(p.pageCount).toBe(1);
    expect(p.total).toBe(0);
    expect(p.start).toBe(0);
    expect(p.end).toBe(0);
  });

  it("keeps a list shorter than the page size on one page", () => {
    const p = paginate(seq(10), 1, 25);
    expect(p.items).toHaveLength(10);
    expect(p.pageCount).toBe(1);
    expect(p.start).toBe(1);
    expect(p.end).toBe(10);
  });

  it("windows a multi-page list (first page)", () => {
    const p = paginate(seq(60), 1, 25);
    expect(p.items[0]).toBe(1);
    expect(p.items).toHaveLength(25);
    expect(p.pageCount).toBe(3);
    expect(p.start).toBe(1);
    expect(p.end).toBe(25);
  });

  it("windows the partial last page", () => {
    const p = paginate(seq(60), 3, 25);
    expect(p.items).toEqual([51, 52, 53, 54, 55, 56, 57, 58, 59, 60]);
    expect(p.page).toBe(3);
    expect(p.start).toBe(51);
    expect(p.end).toBe(60);
  });

  it("clamps a page above the range down to the last page", () => {
    const p = paginate(seq(60), 99, 25);
    expect(p.page).toBe(3);
    expect(p.items[0]).toBe(51);
  });

  it("clamps a page below 1 up to the first page", () => {
    const p = paginate(seq(60), 0, 25);
    expect(p.page).toBe(1);
    expect(p.items[0]).toBe(1);
  });

  it("falls back to a sane page size when given a bad one", () => {
    const p = paginate(seq(60), 1, 0);
    expect(p.pageSize).toBe(25);
    expect(p.items).toHaveLength(25);
  });

  it("tolerates non-array input without throwing", () => {
    const p = paginate(undefined as unknown as number[], 1, 25);
    expect(p.items).toEqual([]);
    expect(p.total).toBe(0);
  });
});
