"use client";

import { LabeledField, TagField } from "./FieldHelpers";
import type { SectionProps } from "./types";

export function BenefitsSection({ draft, onChange }: SectionProps) {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <LabeledField
        label="Functional benefits"
        help="What it does -- tangible, measurable"
      >
        <TagField
          values={draft.benefits_functional}
          onChange={(v) => onChange({ benefits_functional: v })}
          placeholder="Reduz odor..."
        />
      </LabeledField>
      <LabeledField
        label="Emotional benefits"
        help="How it makes the customer feel"
      >
        <TagField
          values={draft.benefits_emotional}
          onChange={(v) => onChange({ benefits_emotional: v })}
          placeholder="Orgulho de ter..."
        />
      </LabeledField>
    </div>
  );
}
