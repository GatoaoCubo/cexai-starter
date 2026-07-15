"use client";

import { LabeledField, TagField } from "./FieldHelpers";
import type { SectionProps } from "./types";

const MAX_TITLE = 60;
const MAX_DESC = 155;

function charCounter(val: string, max: number): string {
  return val.length + " / " + max;
}

function counterClass(val: string, max: number): string {
  if (val.length > max) return "text-danger";
  if (val.length > max * 0.9) return "text-signal";
  return "text-text-faint";
}

export function SeoSection({ draft, onChange }: SectionProps) {
  return (
    <div className="space-y-5">
      <LabeledField
        label={"SEO Title -- " + charCounter(draft.seo_title, MAX_TITLE)}
        help="Google shows ~60 chars. Best: Product name | Brand."
      >
        <input
          className="field"
          value={draft.seo_title}
          maxLength={MAX_TITLE + 20}
          onChange={(e) => onChange({ seo_title: e.target.value })}
          placeholder="Product Name | Brand"
        />
        <span
          className={"mt-1 block font-mono text-2xs " + counterClass(draft.seo_title, MAX_TITLE)}
        >
          {charCounter(draft.seo_title, MAX_TITLE)}
        </span>
      </LabeledField>

      <LabeledField
        label={"Meta description -- " + charCounter(draft.seo_description, MAX_DESC)}
        help="Google shows ~155 chars. Lead with the benefit."
      >
        <textarea
          className="field min-h-[72px] resize-y"
          value={draft.seo_description}
          maxLength={MAX_DESC + 20}
          onChange={(e) => onChange({ seo_description: e.target.value })}
          placeholder="Compelling summary for search result snippet..."
        />
        <span
          className={"mt-1 block font-mono text-2xs " + counterClass(draft.seo_description, MAX_DESC)}
        >
          {charCounter(draft.seo_description, MAX_DESC)}
        </span>
      </LabeledField>

      <LabeledField label="Keywords" help="Press Enter to add each keyword">
        <TagField
          values={draft.seo_keywords}
          onChange={(v) => onChange({ seo_keywords: v })}
          placeholder="caneca gato..."
        />
      </LabeledField>

      <LabeledField
        label="Image alt texts"
        help="One alt text per product image (same order)"
      >
        <TagField
          values={draft.seo_alt_texts}
          onChange={(v) => onChange({ seo_alt_texts: v })}
          placeholder="Foto da frente da caneca..."
        />
      </LabeledField>
    </div>
  );
}
