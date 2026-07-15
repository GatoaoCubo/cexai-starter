"use client";

// ----------------------------------------------------------------------------
// BlogPostView -- a single editorial article (client component; brand fetch via
// PublicApiClient so the no-leak gate + fixtures mode stay consistent).
//
// HONEST: the post is the curated SAMPLE content (lib/storeContent) -- clearly flagged
// "amostra". An unknown post slug -> <NotFound/> (the SAME no-leak view), so a guessed
// post path discloses nothing. The article body renders as TEXT paragraphs (never
// dangerouslySetInnerHTML). Re-skinned to the brand tokens.
//
// SECURITY: the brand fetch still runs (a null tenant-info -> NotFound). The post slug is
// matched against the STATIC sample set; the cat art is a FIRST-PARTY same-origin asset.
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
import { findBlogPostFor, blogCoverSrc, type SampleBlogPost } from "@/lib/storeContent";
import type { PublicTenantInfo } from "@/lib/types";

type LoadState =
  | { phase: "loading" }
  | { phase: "ready"; info: PublicTenantInfo; post: SampleBlogPost }
  | { phase: "notfound" }
  | { phase: "error"; message: string };

export function BlogPostView({ slug, post }: { slug: string; post: string }) {
  const [state, setState] = useState<LoadState>({ phase: "loading" });

  useEffect(() => {
    let alive = true;
    if (!isValidSlug(slug) || !post) {
      setState({ phase: "notfound" });
      return;
    }
    setState({ phase: "loading" });
    publicApi
      .getTenantInfo(slug)
      .then((info) => {
        if (!alive) return;
        // a tenant whose vertical does NOT offer a blog (e.g. a services tenant) renders
        // NotFound -- so a direct hit on /blog/<post> discloses NO sample cat article.
        if (!info || !tenantSectionsFor(info.slug).blog) {
          setState({ phase: "notfound" });
          return;
        }
        // match the post against the TENANT'S OWN sample set; an unknown slug -> NotFound.
        // A cat-post slug requested on a services tenant resolves undefined -> NotFound (no
        // gato leak); a tech-post slug on the cat tenant likewise -> NotFound.
        const found = findBlogPostFor(info.slug, post);
        setState(found ? { phase: "ready", info, post: found } : { phase: "notfound" });
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
  }, [slug, post]);

  if (state.phase === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          carregando...
        </p>
      </div>
    );
  }

  if (state.phase === "notfound") {
    return <NotFound message="Este artigo nao existe ou nao esta publicado." />;
  }

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

  const { info, post: article } = state;
  const base = `/t/${encodeURIComponent(info.slug)}`;
  const showPhotos = imageryFor(info.slug).mode === "photos";

  return (
    <BrandLayout brand={info.brand} slug={info.slug} active="blog">
      <article className="mx-auto max-w-3xl">
        {/* breadcrumb */}
        <nav aria-label="Trilha" className="mb-8 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <Link href={base} className="transition-colors hover:text-foreground">
            Inicio
          </Link>
          <span aria-hidden="true" className="text-border">/</span>
          <Link href={`${base}/blog`} className="transition-colors hover:text-foreground">
            Blog
          </Link>
        </nav>

        <header className="space-y-5 border-b border-border pb-10">
          <div className="flex flex-wrap items-center gap-3">
            <span className="chip border-brand/30 text-brand">{article.category}</span>
            <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
              <CalendarIcon width={15} height={15} />
              {article.date}
            </span>
            <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
              <ClockIcon width={15} height={15} />
              {article.readTime}
            </span>
          </div>
          <h1 className="font-display text-display text-foreground">{article.title}</h1>
          <p className="text-xl leading-relaxed text-muted-foreground">{article.excerpt}</p>
          <p className="inline-flex w-fit items-center gap-2 rounded-pill border border-border bg-secondary px-3 py-1 text-2xs font-medium uppercase tracking-wide text-muted-foreground">
            amostra -- dados simulados
          </p>
        </header>

        {/* lead art -- the post's cover photo (photo tenant) or a brand-gradient tile */}
        <div className="my-10 overflow-hidden rounded-card border border-border bg-foreground">
          {showPhotos && article.cover ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={blogCoverSrc(article.cover)}
              alt=""
              aria-hidden="true"
              className="aspect-[16/9] w-full object-cover"
            />
          ) : (
            <div
              aria-hidden="true"
              className="aspect-[16/9] w-full"
              style={{
                background:
                  "linear-gradient(135deg, hsl(var(--brand)) 0%, hsl(var(--foreground)) 100%)",
              }}
            />
          )}
        </div>

        {/* the article body -- paragraphs as TEXT (never markup) */}
        <div className="space-y-6">
          {article.body.map((p, i) => (
            <p key={i} className="text-lg leading-relaxed text-foreground/90">
              {p}
            </p>
          ))}
        </div>

        <footer className="mt-14 border-t border-border pt-8">
          <Link href={`${base}/blog`} className="btn-outline">
            Voltar ao blog
            <ArrowRightIcon />
          </Link>
        </footer>
      </article>
    </BrandLayout>
  );
}
