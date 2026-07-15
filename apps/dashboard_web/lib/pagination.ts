// ----------------------------------------------------------------------------
// Pagination -- a reusable limit/offset helper for the dashboard's list views
// (HARDEN mission, central-dashboard-hardening).
//
// Two layers, both pure-ish and mode-transparent:
//
//   paginate(items, page, pageSize)  -- a PURE windowing function. Clamps page
//       into [1, pageCount], slices the array, and reports the window (start/end
//       1-based, inclusive). Empty input -> page 1 of 1, no rows. Never throws.
//
//   usePagination(items, pageSize)   -- the React hook the list views use. Holds
//       the current page, re-clamps when the source list shrinks (a reload /
//       filter must never strand you on a now-empty page), and exposes next/prev
//       + the current window. Resets to page 1 when the list identity changes.
//
// SCOPE NOTE (honest): this windows what is RENDERED on the client. The backend
// already CAPS each fetch server-side (GET /results default 50 / max 200; GET
// /entity max 200) -- see apps/dashboard_api/main.py -- but exposes no `offset`,
// so true server-side paging is not available without a backend change (out of
// this mission's scope). The data hooks additionally pass an explicit `limit`
// (lib/api.ts) so the fetch ceiling is caller-controlled, not implicit. Until an
// `offset`/cursor lands, this client-side window bounds the DOM + scan cost of a
// large list; the limit/offset shape here is ready to drive server paging then.
// ----------------------------------------------------------------------------

import { useEffect, useMemo, useState } from "react";

export interface Page<T> {
  /** The rows for the current page (a slice; never the whole list). */
  items: T[];
  /** 1-based current page, clamped into [1, pageCount]. */
  page: number;
  /** Total number of pages (>= 1, even when empty). */
  pageCount: number;
  /** The page size used to compute the window. */
  pageSize: number;
  /** Total number of items across all pages. */
  total: number;
  /** 1-based index of the first visible row (0 when empty). */
  start: number;
  /** 1-based index of the last visible row (0 when empty). */
  end: number;
}

/** Coerce to a positive integer page size; falls back to ``fallback``. */
function safePageSize(pageSize: number, fallback = 25): number {
  if (!Number.isFinite(pageSize) || pageSize < 1) return fallback;
  return Math.floor(pageSize);
}

/**
 * Pure windowing. Returns the slice of ``items`` for ``page`` at ``pageSize``,
 * with the page clamped into range and the 1-based window reported. Safe on
 * empty / non-finite inputs.
 */
export function paginate<T>(items: T[], page: number, pageSize: number): Page<T> {
  const size = safePageSize(pageSize);
  const list = Array.isArray(items) ? items : [];
  const total = list.length;
  const pageCount = Math.max(1, Math.ceil(total / size));
  const clamped = Math.min(Math.max(1, Math.floor(page) || 1), pageCount);
  const offset = (clamped - 1) * size;
  const slice = list.slice(offset, offset + size);
  return {
    items: slice,
    page: clamped,
    pageCount,
    pageSize: size,
    total,
    start: total === 0 ? 0 : offset + 1,
    end: total === 0 ? 0 : offset + slice.length,
  };
}

export interface UsePaginationResult<T> extends Page<T> {
  setPage: (page: number) => void;
  next: () => void;
  prev: () => void;
  canPrev: boolean;
  canNext: boolean;
}

/**
 * Stateful pagination for a list view. The window is derived from ``items`` +
 * the current page; the page re-clamps whenever the list shrinks below it. When
 * the list IDENTITY changes (a fresh fetch / a filter switch), the page resets
 * to 1 so the user always lands at the top of the new result set.
 */
export function usePagination<T>(
  items: T[],
  pageSize = 25,
): UsePaginationResult<T> {
  const [page, setPageRaw] = useState(1);

  // A fresh list (new identity) starts at page 1.
  useEffect(() => {
    setPageRaw(1);
  }, [items]);

  const view = useMemo(
    () => paginate(items, page, pageSize),
    [items, page, pageSize],
  );

  // If the source shrank under us (e.g. rows deleted), snap the state back into
  // range so a later interaction does not act on a stale page number.
  useEffect(() => {
    if (page !== view.page) setPageRaw(view.page);
  }, [page, view.page]);

  return {
    ...view,
    setPage: (p: number) => setPageRaw(p),
    next: () => setPageRaw((p) => p + 1),
    prev: () => setPageRaw((p) => p - 1),
    canPrev: view.page > 1,
    canNext: view.page < view.pageCount,
  };
}
