// ----------------------------------------------------------------------------
// Rating -- the PDP rating ROW + the optional REVIEWS band. SERVER-SAFE
// presentational (no hooks, no client state).
//
// HONEST-EMPTY BY CONSTRUCTION: these render ONLY from data the published payload
// actually carries (brandText.ratingOf / reviewsOf). The DetailView gates them on a
// non-null RatingSummary -- with no rating field the PDP shows NOTHING here. This
// component NEVER fabricates a star count, a review total, or a review entry.
//
// MONOCHROME by design (design_system.md roadmap #9): the stars are foreground/muted,
// NOT brand teal -- teal stays reserved for the primary action. The "verificado" badge
// uses --success (status green), also NOT brand teal.
//
// SECURITY: any per-review media URL is gated by isSafeMediaSrc HERE before it can
// become an <img src> -- the same tenant-payload media boundary as the gallery. An
// unsafe/absent media url simply does not render an image.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import type { RatingSummary, ReviewEntry } from "@/lib/brandText";
import { isSafeMediaSrc } from "@/lib/mediaSafety";
import { StarIcon, CheckIcon } from "./icons";

/** A 5-star monochrome row with a fractional fill clip for the partial star.
 *  Decorative -> aria-hidden; the parent RatingRow carries the accessible label. */
function Stars({ value, size = 16 }: { value: number; size?: number }) {
  // fraction of 5 filled, as a percentage width over the 5-glyph track.
  const pct = Math.max(0, Math.min(100, (value / 5) * 100));
  return (
    <span aria-hidden="true" className="relative inline-flex align-middle">
      {/* empty track (muted outline tone) */}
      <span className="inline-flex text-border">
        {[0, 1, 2, 3, 4].map((i) => (
          <StarIcon key={i} width={size} height={size} />
        ))}
      </span>
      {/* filled overlay clipped to the value fraction (foreground tone) */}
      <span
        className="absolute inset-y-0 left-0 inline-flex overflow-hidden text-foreground"
        style={{ width: pct + "%" }}
      >
        {[0, 1, 2, 3, 4].map((i) => (
          <StarIcon key={i} width={size} height={size} />
        ))}
      </span>
    </span>
  );
}

/** The compact rating row shown under the PDP title (stars + value + count +
 *  optional verified badge). Render NOTHING when ``rating`` is null (honest-empty). */
export function RatingRow({ rating }: { rating: RatingSummary | null }) {
  if (!rating) return null;
  const countLabel =
    rating.count === null
      ? ""
      : `${rating.count} ${rating.count === 1 ? "avaliacao" : "avaliacoes"}`;
  return (
    <div
      className="flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-sm text-muted-foreground"
      aria-label={`Nota ${rating.display} de 5`}
    >
      <Stars value={rating.value} />
      <span className="font-semibold text-foreground">{rating.display}</span>
      {countLabel && <span>{countLabel}</span>}
      {rating.verified && (
        // status-green verified badge -- NOT brand teal (roadmap #9 discipline).
        <span className="inline-flex items-center gap-1 text-success">
          <CheckIcon width={14} height={14} />
          verificado
        </span>
      )}
    </div>
  );
}

/** The optional reviews band below the dual-face. Render NOTHING when there are no
 *  review entries (honest-empty). Each entry renders verbatim text; any media url is
 *  isSafeMediaSrc-gated before it becomes an <img>. */
export function ReviewsBand({ reviews }: { reviews: ReviewEntry[] }) {
  if (!reviews || reviews.length === 0) return null;
  return (
    <section className="mt-16 space-y-6" aria-label="Avaliacoes">
      <div className="space-y-2 border-b border-border pb-4">
        <p className="eyebrow">Avaliacoes</p>
        <h2 className="font-display text-h2 text-foreground">O que dizem</h2>
      </div>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        {reviews.map((r, i) => {
          const safeMedia = r.media && isSafeMediaSrc(r.media) ? r.media : "";
          return (
            <article
              key={i}
              className="space-y-3 rounded-card border border-border bg-card p-5 shadow-sm"
            >
              <div className="flex items-center justify-between gap-3">
                {r.author ? (
                  <p className="text-sm font-semibold text-foreground">{r.author}</p>
                ) : (
                  <span aria-hidden="true" />
                )}
                {r.rating !== null && <Stars value={r.rating} size={14} />}
              </div>
              {r.body && (
                <p className="text-sm leading-relaxed text-muted-foreground">{r.body}</p>
              )}
              {safeMedia && (
                // review media -- tenant payload, isSafeMediaSrc-gated above.
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={safeMedia}
                  alt=""
                  aria-hidden="true"
                  className="mt-1 h-24 w-full rounded-md border border-border object-cover"
                />
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
