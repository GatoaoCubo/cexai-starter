// ----------------------------------------------------------------------------
// /t/<slug> -- the tenant HOME route. A thin SERVER COMPONENT that extracts the slug
// param and hands it to <HomeView/> (the client component that fetches
// /public/tenant-info + the featured per-kind catalogs through PublicApiClient). The
// client view validates the slug and renders <NotFound/> on the no-leak miss. The client
// only ever sends slug (+ kind) to the API -- no auth header, no tenant_id.
//
// (The previous thin <LandingView/> is superseded by <HomeView/>, the full branded
// storefront home: hero + featured items + section cards.)
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { HomeView } from "@/components/views/HomeView";

export default function TenantHomePage({
  params,
}: {
  params: { slug: string };
}) {
  return <HomeView slug={params.slug} />;
}
