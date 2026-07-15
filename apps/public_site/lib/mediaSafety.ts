// ----------------------------------------------------------------------------
// mediaSafety -- the produced-media scheme allowlist for the L2 public site.
//
// LIFTED from apps/dashboard_web/components/DualOutputFace.isSafeMediaSrc. On the
// PUBLIC surface this is load-bearing: a published payload's media field is
// whatever the tenant stored and the backend forwards it VERBATIM (it does NOT
// fetch / inline / validate it -- see public_reader._row_to_item's media-URL
// caveat). So the client MUST gate it before rendering an <img>/<video>/<audio>.
//
// A result src is attacker-influenceable, so permit ONLY ``https:`` and
// ``data:image|video|audio`` -- an ``http:`` (mixed-content beacon),
// ``javascript:``, ``data:text/html``, ``file:`` or any other scheme is dropped so
// the slot renders its empty/placeholder state instead of fetching a hostile URL.
//
// TOTAL: never throws. ASCII-only.
// ----------------------------------------------------------------------------

/** True iff ``src`` is a safe produced-media URL (https: or data:image|video|audio). */
export function isSafeMediaSrc(src: unknown): boolean {
  if (typeof src !== "string") return false;
  const s = src.trim();
  if (/^https:\/\//i.test(s)) return true;
  if (/^data:(image|video|audio)\//i.test(s)) return true;
  return false;
}
