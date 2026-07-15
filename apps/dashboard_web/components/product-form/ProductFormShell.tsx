"use client";

import type { ReactNode } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { BasicSection } from "./BasicSection";
import { BenefitsSection } from "./BenefitsSection";
import { DescriptionSection } from "./DescriptionSection";
import { ImagesSection } from "./ImagesSection";
import { PricingSection } from "./PricingSection";
import { SeoSection } from "./SeoSection";
import { SpecsSection } from "./SpecsSection";
import { StockSection } from "./StockSection";
import type { ProductDraft } from "./types";
import { Spinner } from "@/components/ui";

// Section nav anchors
const NAV_ITEMS = [
  { id: "basic", label: "Basic" },
  { id: "images", label: "Images" },
  { id: "description", label: "Description" },
  { id: "benefits", label: "Benefits" },
  { id: "specs", label: "Specs" },
  { id: "pricing", label: "Pricing" },
  { id: "seo", label: "SEO" },
  { id: "stock", label: "Stock" },
] as const;

type NavId = (typeof NAV_ITEMS)[number]["id"];

interface SectionItem {
  id: NavId;
  label: string;
  node: ReactNode;
}

export interface ProductFormShellProps {
  initialDraft: ProductDraft;
  onSave?: (draft: ProductDraft) => Promise<void> | void;
  readOnly?: boolean;
}

export function ProductFormShell({
  initialDraft,
  onSave,
  readOnly = false,
}: ProductFormShellProps) {
  const [draft, setDraft] = useState<ProductDraft>(initialDraft);
  const [savedDraft, setSavedDraft] = useState<ProductDraft>(initialDraft);
  const [saving, setSaving] = useState(false);
  const [saveOk, setSaveOk] = useState(false);
  const [showDiscard, setShowDiscard] = useState(false);
  const sectionRefs = useRef<Record<string, HTMLElement | null>>({});

  const isDirty = JSON.stringify(draft) !== JSON.stringify(savedDraft);

  // Warn before unload when dirty
  useEffect(() => {
    if (!isDirty) return;
    const guard = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, [isDirty]);

  const handleChange = useCallback((patch: Partial<ProductDraft>) => {
    setDraft((prev) => ({ ...prev, ...patch }));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (onSave) await onSave(draft);
      setSavedDraft(draft);
      setSaveOk(true);
      setTimeout(() => setSaveOk(false), 2500);
    } finally {
      setSaving(false);
    }
  };

  const scrollTo = (id: string) => {
    const el = sectionRefs.current[id];
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const sections: SectionItem[] = [
    {
      id: "basic",
      label: "Basic info",
      node: <BasicSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "images",
      label: "Images",
      node: <ImagesSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "description",
      label: "Description",
      node: <DescriptionSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "benefits",
      label: "Benefits",
      node: <BenefitsSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "specs",
      label: "Dims / Specs",
      node: <SpecsSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "pricing",
      label: "Pricing",
      node: <PricingSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "seo",
      label: "SEO",
      node: <SeoSection draft={draft} onChange={handleChange} />,
    },
    {
      id: "stock",
      label: "Stock",
      node: <StockSection draft={draft} onChange={handleChange} />,
    },
  ];

  const noVariant = draft.shopify_variant_id.trim() === "";

  return (
    <>
      {/* Page header */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div className="min-w-0">
          <p className="eyebrow mb-2">Product form</p>
          <h1 className="truncate font-display text-2xl font-600 tracking-tight text-text">
            {draft.name || "Untitled product"}
          </h1>
          {draft.slug && (
            <p className="mt-1 font-mono text-2xs text-text-faint">
              /{draft.slug}
            </p>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {isDirty && (
            <span className="chip border-signal/40 text-signal">unsaved</span>
          )}
          {saveOk && (
            <span className="chip border-synapse/40 text-synapse">saved</span>
          )}
          {noVariant && (
            <span className="chip border-signal/30 text-signal/80">
              nao vendavel
            </span>
          )}
        </div>
      </header>

      {/* Section quick-nav */}
      <nav
        aria-label="Form sections"
        className="mt-5 flex gap-1 overflow-x-auto border-b border-line pb-2"
      >
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => scrollTo(item.id)}
            className="shrink-0 rounded-pill px-3 py-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:bg-panel hover:text-text"
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Form sections */}
      <div className="mt-8 space-y-10 pb-32">
        {sections.map(({ id, label, node }) => (
          <article
            key={id}
            ref={(el) => {
              sectionRefs.current[id] = el;
            }}
            className="scroll-mt-6"
          >
            <p className="eyebrow mb-4">// {label}</p>
            <div className="panel p-5">{node}</div>
          </article>
        ))}
      </div>

      {/* Sticky save footer */}
      {!readOnly && (
        <footer className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-ink-800/90 px-5 py-4 backdrop-blur sm:px-8 lg:px-12">
          <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
            <p className="font-mono text-2xs text-text-faint">
              {isDirty ? "You have unsaved changes." : "No unsaved changes."}
            </p>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => isDirty && setShowDiscard(true)}
                disabled={!isDirty || saving}
                className="btn-ghost disabled:opacity-40"
              >
                Discard
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={!isDirty || saving}
                className="btn-primary disabled:opacity-40"
              >
                {saving ? (
                  <>
                    <Spinner className="h-3.5 w-3.5" />
                    Saving...
                  </>
                ) : (
                  "Salvar"
                )}
              </button>
            </div>
          </div>
        </footer>
      )}

      {/* Discard confirmation modal */}
      {showDiscard && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Confirm discard"
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/80 backdrop-blur-sm"
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowDiscard(false);
          }}
        >
          <div className="panel mx-4 w-full max-w-sm p-6">
            <h2 className="font-display text-lg font-600 text-text">
              Discard changes?
            </h2>
            <p className="mt-2 text-sm text-text-muted">
              All unsaved changes to this product will be lost. This cannot be
              undone.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowDiscard(false)}
                className="btn-ghost"
              >
                Keep editing
              </button>
              <button
                type="button"
                onClick={() => {
                  setDraft(savedDraft);
                  setShowDiscard(false);
                }}
                className="inline-flex items-center justify-center gap-2 rounded-pill bg-danger px-5 py-2.5 font-medium text-white transition-all duration-200 hover:bg-danger-deep active:translate-y-px"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
