// ----------------------------------------------------------------------------
// slug -- client-side slug + kind validation for the L2 public site.
//
// MIRRORS apps/dashboard_api/public_reader._SLUG_RE / _KIND_RE
// (^[a-z0-9][a-z0-9_-]{0,63}$). This is DEFENCE-IN-DEPTH: the backend is the
// authority (it rejects the same shapes), but the public pages validate BEFORE
// any fetch so a malformed path segment (a "..", a space, UPPERCASE, a SQL
// fragment, an over-long string) renders <NotFound/> and never reaches the API.
//
// A slug is the public URL segment AND a tenant_slugs lookup key; a kind is the
// tenant_data.kind the catalog filters on -- both pinned to the SAME strict
// allowlist so a path can never carry SQL or a surprise.
//
// PURE + TOTAL: never throws. ASCII-only.
// ----------------------------------------------------------------------------

// The strict allowlist (identical to the backend's _SLUG_RE / _KIND_RE). The
// leading class forbids a leading "-" / "_" / "."; the bounded {0,63} caps length
// at 64 chars total. No "." anywhere -> ".." can never match.
const SLUG_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;
const KIND_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;

/** True iff ``slug`` is a well-formed public slug. A malformed slug renders
 *  <NotFound/> and never reaches the DB (the caller treats false as "no such
 *  public tenant"). Trims first so a stray surrounding space is rejected by shape,
 *  not silently accepted. */
export function isValidSlug(slug: unknown): boolean {
  return typeof slug === "string" && SLUG_RE.test(slug.trim());
}

/** True iff ``kind`` is a well-formed tenant_data kind. A malformed kind renders
 *  <NotFound/> and never reaches the DB (the caller treats false as "no such
 *  catalog"). */
export function isValidKind(kind: unknown): boolean {
  return typeof kind === "string" && KIND_RE.test(kind.trim());
}
