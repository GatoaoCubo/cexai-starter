// ----------------------------------------------------------------------------
// /t/<slug>/<kind>/<id> -- the PRODUCT DETAIL route. A thin SERVER COMPONENT that
// extracts slug + kind + id and hands them to <DetailView/> (the client component).
// <DetailView/> RE-FETCHES /public/catalog for (slug, kind) and matches the row by
// id (degrade-to-list -- there is NO get-by-id endpoint; this mirrors the
// dashboard's results deep-link). A no match -> <NotFound/>. The client only ever
// sends slug + kind to the API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { DetailView } from "@/components/views/DetailView";

export default function DetailPage({
  params,
}: {
  params: { slug: string; kind: string; id: string };
}) {
  return <DetailView slug={params.slug} kind={params.kind} id={params.id} />;
}
