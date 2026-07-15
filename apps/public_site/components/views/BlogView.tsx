"use client";

// ----------------------------------------------------------------------------
// BlogView -- the editorial CONTENT BLOG landing (client component so the brand fetch
// runs through PublicApiClient, keeping fixtures mode + the no-leak gate consistent).
//
// HONEST BY CONSTRUCTION: the public API carries NO blog endpoint, so the posts are the
// curated SAMPLE editorial content (lib/storeContent.SAMPLE_BLOG_POSTS) -- every card +
// the page banner are clearly flagged "amostra / dados simulados" and NEVER claimed to be
// a tenant's real article. The page is re-skinned to the BRAND tokens (NOT amber -- the
// design_system.md flags amber as debt).
//
// SECURITY: the SAME no-leak gate as every page -- the brand fetch still runs, and a null
// tenant-info (unknown / non-public / malformed slug) renders <NotFound/> (no disclosure).
// Post slugs are STATIC constants; the cat art is a FIRST-PARTY same-origin asset; all
// text renders as text (never dangerouslySetInnerHTML).
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";
import { useEffect, useState } from "react";
import { BrandLayout } from "@/components/BrandLayout";
import { NotFound } from "@/components/NotFound";
import { ArrowRightIcon, CalendarIcon, ClockIcon } from "@/components/icons";
import { publicApi, ApiClientError } from "@/lib/publicApi";
import { isValidSlug } from "@/lib/slug";
import { imageryFor } from "@/lib/tenantImagery";
import { tenantSectionsFor } from "@/lib/tenantSections";
import { blogPostsFor, blogCategoriesFor, blogSubtitleFor, blogCoverSrc, type BlogCover } from "@/lib/storeContent";
import type { PublicTenantInfo } from "@/lib/types";

/** A blog cover surface: the first-party photo for a photo tenant, else a brand-gradient
 *  tile (no cat leak for a non-photo tenant -- the sample posts stay, just not cat art). */
function BlogCoverArt({
  cover,
  showPhotos,
  className,
}: {
  cover?: BlogCover;
  showPhotos: boolean;
  className: string;
}) {
  if (showPhotos && cover) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={blogCoverSrc(cover)} alt="" aria-hidden="true" className={className} />;
  }
  return (
    <div
      aria-hidden="true"
      className={className}
      style={{
        background: "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
      }}
    />
  );
}

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

export function BlogView({ slug }: { slug: string }) {
  const [state, setState] = useState<LoadState>({ phase: "loading" });

  useEffect(() => {
    let alive = true;
    if (!isValidSlug(slug)) {
      setState({ phase: "notfound" });
      return;
    }
    setState({ phase: "loading" });
    publicApi
      .getTenantInfo(slug)
      .then((info) => {
        if (!alive) return;
        // a tenant whose vertical does NOT offer a blog (e.g. a services tenant) renders
        // the neutral NotFound -- so a direct hit on /blog discloses NO sample cat content.
        if (!info || !tenantSectionsFor(info.slug).blog) {
          setState({ phase: "notfound" });
          return;
        }
        setState({ phase: "ready", info });
      })
      .catch((err: unknown) => {
        if (!alive) return;
        const message =
          err instanceof ApiClientError ? err.message : "Nao foi possivel carregar.";
        setState({ phase: "error", message });
      });
    return () => {
      alive = false;
    };
  }, [slug]);

  if (state.phase === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          carregando...
        </p>
      </div>
    );
  }

  if (state.phase === "notfound") return <NotFound />;

  if (state.phase === "error") {
    return (
      <div className="flex min-h-screen items-center justify-center px-5">
        <div className="w-full max-w-md space-y-3 rounded-card border border-border bg-card p-8 text-center shadow-sm">
          <p className="eyebrow">erro</p>
          <p className="text-sm text-muted-foreground">{state.message}</p>
        </div>
      </div>
    );
  }

  const { info } = state;
  const base = `/t/${encodeURIComponent(info.slug)}`;
  // PER-TENANT posts + category chips: a services-vertical tenant renders ITS OWN tech
  // posts + tech categories; demo-acme keeps the cat posts (default) -> no cat-content leak on a
  // services blog, no services content on the cat blog.
  const posts = blogPostsFor(info.slug);
  const categories = blogCategoriesFor(info.slug);
  const featured = posts.find((p) => p.featured) ?? posts[0];
  const rest = posts.filter((p) => p.slug !== featured?.slug);
  // only a photo-shipping tenant (demo-acme) paints the cat cover art; others get a
  // brand-gradient tile (no cat leak into a non-cat tenant's blog).
  const showPhotos = imageryFor(info.slug).mode === "photos";

  return (
    <BrandLayout brand={info.brand} slug={info.slug} active="blog">
      <header className="mb-10 space-y-3 border-b border-border pb-10">
        <p className="eyebrow">Conteudo</p>
        <h1 className="font-display text-display text-foreground">Blog</h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          {blogSubtitleFor(info.slug)}
        </p>
        <p className="inline-flex items-center gap-2 rounded-pill border border-border bg-secondary px-3 py-1 text-2xs font-medium uppercase tracking-wide text-muted-foreground">
          amostra -- dados simulados
        </p>
      </header>

      {/* category chips (static -- a presentational taxonomy of the sample set) */}
      <nav aria-label="Categorias" className="mb-10 flex flex-wrap gap-2">
        <span className="chip border-brand/30 bg-brand-muted text-brand">Todos</span>
        {categories.map((cat) => (
          <span key={cat} className="chip">
            {cat}
          </span>
        ))}
      </nav>

      {/* featured post -- editorial hero card with a real cover photo */}
      {featured && (
        <Link
          href={`${base}/blog/${encodeURIComponent(featured.slug)}`}
          className="group mb-14 grid grid-cols-1 overflow-hidden rounded-card border border-border bg-card shadow-sm transition-all duration-base hover:-translate-y-1 hover:border-brand/40 hover:shadow-lg lg:grid-cols-2"
        >
          <div className="relative aspect-[16/10] overflow-hidden bg-foreground lg:aspect-auto">
            {/* first-party decorative cover photo (photo tenant) or brand-gradient tile */}
            <BlogCoverArt
              cover={featured.cover}
              showPhotos={showPhotos}
              className="h-full w-full object-cover transition-transform duration-slow ease-emphasized group-hover:scale-[1.03]"
            />
            <span className="absolute left-4 top-4 inline-flex items-center gap-1.5 rounded-pill bg-background/90 px-3 py-1 text-2xs font-semibold uppercase tracking-wide text-foreground shadow-sm backdrop-blur-sm">
              Destaque
            </span>
          </div>
          <div className="flex flex-col justify-center gap-4 p-8 lg:p-12">
            <span className="chip w-fit border-brand/30 text-brand">{featured.category}</span>
            <h2 className="font-display text-h2 text-foreground">{featured.title}</h2>
            <p className="text-lg text-muted-foreground">{featured.excerpt}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <CalendarIcon width={15} height={15} />
                {featured.date}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <ClockIcon width={15} height={15} />
                {featured.readTime}
              </span>
            </div>
            <span className="inline-flex items-center gap-1.5 font-semibold text-brand">
              Ler artigo
              <ArrowRightIcon />
            </span>
          </div>
        </Link>
      )}

      {/* the rest of the posts -- multi-post grid with cover art + excerpts */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {rest.map((post) => (
          <Link
            key={post.slug}
            href={`${base}/blog/${encodeURIComponent(post.slug)}`}
            className="group flex flex-col overflow-hidden rounded-card border border-border bg-card shadow-sm transition-all duration-base hover:-translate-y-1 hover:border-brand/40 hover:shadow-md"
          >
            <div className="relative aspect-[16/10] overflow-hidden bg-foreground">
              <BlogCoverArt
                cover={post.cover}
                showPhotos={showPhotos}
                className="h-full w-full object-cover transition-transform duration-slow ease-emphasized group-hover:scale-[1.03]"
              />
            </div>
            <div className="flex flex-1 flex-col gap-3 p-6">
              <span className="chip w-fit">{post.category}</span>
              <h3 className="font-display text-h3 font-semibold tracking-tight text-foreground">
                {post.title}
              </h3>
              <p className="line-clamp-3 text-sm text-muted-foreground">{post.excerpt}</p>
              <div className="mt-auto flex items-center gap-3 pt-2 text-2xs uppercase tracking-wide text-muted-foreground">
                <span>{post.date}</span>
                <span aria-hidden="true">-</span>
                <span>{post.readTime}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </BrandLayout>
  );
}
