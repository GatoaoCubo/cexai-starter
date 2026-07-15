// ----------------------------------------------------------------------------
// /t/<slug>/sobre -- the BRAND / ABOUT route. A thin SERVER COMPONENT that extracts the
// slug param and hands it to <AboutView/> (the client component that fetches
// /public/tenant-info through PublicApiClient and renders the brand identity honestly --
// name / tagline / palette, never an invented story). The client validates the slug and
// renders <NotFound/> on the no-leak miss; it only ever sends the slug to the API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { AboutView } from "@/components/views/AboutView";

export default function TenantAboutPage({
  params,
}: {
  params: { slug: string };
}) {
  return <AboutView slug={params.slug} />;
}
