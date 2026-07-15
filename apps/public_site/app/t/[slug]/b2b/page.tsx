// ----------------------------------------------------------------------------
// /t/<slug>/b2b -- the WHOLESALE / PARTNER route. A thin SERVER COMPONENT that extracts
// the slug and hands it to <B2BView/> (the client component that fetches
// /public/tenant-info for the brand + the no-leak gate, and renders the curated SAMPLE
// B2B content -- value props, illustrative tiers, and a CONTACT CTA with NO fake
// checkout). The client validates the slug and renders <NotFound/> on the no-leak miss;
// it only ever sends the slug to the API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { B2BView } from "@/components/views/B2BView";

export default function B2BPage({ params }: { params: { slug: string } }) {
  return <B2BView slug={params.slug} />;
}
