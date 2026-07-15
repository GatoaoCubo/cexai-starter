// ----------------------------------------------------------------------------
// /t/<slug>/blog -- the BLOG landing route. A thin SERVER COMPONENT that extracts the
// slug and hands it to <BlogView/> (the client component that fetches /public/tenant-info
// through PublicApiClient for the brand shell + the no-leak gate, and renders the curated
// SAMPLE editorial content -- clearly flagged amostra). The client validates the slug and
// renders <NotFound/> on the no-leak miss; it only ever sends the slug to the API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { BlogView } from "@/components/views/BlogView";

export default function BlogPage({ params }: { params: { slug: string } }) {
  return <BlogView slug={params.slug} />;
}
