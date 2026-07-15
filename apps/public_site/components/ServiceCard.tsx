// ----------------------------------------------------------------------------
// ServiceCard -- one published SERVICE as a premium service card (the IT-services vertical
// analog of CatalogCard). SERVER-SAFE presentational (no hooks, no client state).
//
// A service card is NOT a product: it has NO price and NO fake checkout. It shows a brand-
// colored icon tile, the service title + an honest short description, and a single "Saiba
// mais" CTA that points at the tenant's REAL contact channel (WhatsApp/contact) when one is
// provided, else it degrades to a plain (no-CTA) card. TYPED render of the OPEN payload via
// the shared brandText pickers -- it NEVER assumes a field exists and NEVER injects payload
// HTML (strings render as text).
//
// SECURITY: the CTA href is a TRUSTED brand-published contact link, scheme-checked by the
// caller (isSafeContactHref) BEFORE being passed in -- this component only ever places an
// already-validated href into <a>. The icon is mapped by lookup (ServiceIcon), never
// rendered as markup.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { ServiceIcon } from "@/components/ServiceIcon";
import { ArrowRightIcon } from "@/components/icons";
import { summaryOf, titleOf } from "@/lib/brandText";
import type { PublicCatalogItem } from "@/lib/types";

export function ServiceCard({
  item,
  /** the tenant's REAL contact CTA href (already scheme-checked), or '' for no CTA. */
  ctaHref,
  /** the CTA label, e.g. "Saiba mais" / "Fale no WhatsApp". */
  ctaLabel = "Saiba mais",
}: {
  item: PublicCatalogItem;
  ctaHref?: string;
  ctaLabel?: string;
}) {
  const title = titleOf(item);
  const summary = summaryOf(item);
  const href = (ctaHref ?? "").trim();

  return (
    <div className="group flex h-full flex-col rounded-card border border-border bg-card p-7 shadow-sm transition-all duration-base ease-standard hover:-translate-y-1 hover:border-brand/40 hover:shadow-lg">
      <span className="mb-5 inline-grid h-12 w-12 place-items-center rounded-card bg-brand-muted text-brand transition-transform duration-base ease-emphasized group-hover:scale-110">
        <ServiceIcon icon={item.icon} width={24} height={24} />
      </span>
      <h3 className="font-display text-h3 font-semibold tracking-tight text-foreground">
        {title}
      </h3>
      {summary && (
        <p className="mt-2 flex-1 text-base leading-relaxed text-muted-foreground">{summary}</p>
      )}
      {href ? (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-brand transition-colors duration-fast hover:text-highlight"
        >
          {ctaLabel}
          <span className="transition-transform duration-base ease-emphasized group-hover:translate-x-0.5">
            <ArrowRightIcon />
          </span>
        </a>
      ) : null}
    </div>
  );
}
