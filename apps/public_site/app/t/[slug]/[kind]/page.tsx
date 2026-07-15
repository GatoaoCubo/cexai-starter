// ----------------------------------------------------------------------------
// /t/<slug>/<kind> -- the per-kind CATALOG route. A thin SERVER COMPONENT that
// extracts slug + kind and hands them to <CatalogView/> (the client component that
// fetches /public/catalog through PublicApiClient). The client view validates both
// segments and renders <NotFound/> on the no-leak miss / the branded empty shell on
// no items. The client only ever sends slug + kind to the API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { CatalogView } from "@/components/views/CatalogView";

export default function CatalogPage({
  params,
}: {
  params: { slug: string; kind: string };
}) {
  return <CatalogView slug={params.slug} kind={params.kind} />;
}
