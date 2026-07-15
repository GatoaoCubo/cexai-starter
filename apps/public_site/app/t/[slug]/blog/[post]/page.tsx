// ----------------------------------------------------------------------------
// /t/<slug>/blog/<post> -- a single ARTICLE route. A thin SERVER COMPONENT that extracts
// slug + post and hands them to <BlogPostView/> (the client component). The client fetches
// /public/tenant-info for the brand + the no-leak gate, matches the post against the
// STATIC sample set, and renders <NotFound/> on either miss (an unknown slug OR an unknown
// post). It only ever sends the slug to the API.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { BlogPostView } from "@/components/views/BlogPostView";

export default function BlogPostPage({
  params,
}: {
  params: { slug: string; post: string };
}) {
  return <BlogPostView slug={params.slug} post={params.post} />;
}
