"use client";

import { LabeledField } from "./FieldHelpers";
import type { SectionProps } from "./types";

export function DescriptionSection({ draft, onChange }: SectionProps) {
  return (
    <div className="space-y-5">
      <LabeledField label="Short description" help="One paragraph; shown on product cards">
        <textarea
          className="field min-h-[72px] resize-y"
          value={draft.description}
          onChange={(e) => onChange({ description: e.target.value })}
          placeholder="What this product is, in one paragraph."
        />
      </LabeledField>
      <LabeledField label="Long description" help="Full story; shown on product detail page">
        <textarea
          className="field min-h-[120px] resize-y"
          value={draft.long_description}
          onChange={(e) => onChange({ long_description: e.target.value })}
          placeholder="The full story behind the product."
        />
      </LabeledField>
      <LabeledField label="Why it works" help="The mechanism / proof">
        <textarea
          className="field min-h-[72px] resize-y"
          value={draft.why_it_works}
          onChange={(e) => onChange({ why_it_works: e.target.value })}
          placeholder="Explain the mechanism that makes this product effective."
        />
      </LabeledField>
    </div>
  );
}
