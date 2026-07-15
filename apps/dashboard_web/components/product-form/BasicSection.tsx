"use client";

import { LabeledField } from "./FieldHelpers";
import type { SectionProps } from "./types";

export function BasicSection({ draft, onChange }: SectionProps) {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <LabeledField label="Slug" help="URL-safe id, e.g. caneca-gato">
        <input
          className="field"
          value={draft.slug}
          onChange={(e) => onChange({ slug: e.target.value })}
          placeholder="meu-produto"
        />
      </LabeledField>
      <LabeledField label="Name">
        <input
          className="field"
          value={draft.name}
          onChange={(e) => onChange({ name: e.target.value })}
          placeholder="Nome do produto"
        />
      </LabeledField>
      <LabeledField label="Tagline" help="One-liner shown on cards">
        <input
          className="field"
          value={draft.tagline}
          onChange={(e) => onChange({ tagline: e.target.value })}
          placeholder="O produto certo para o momento certo."
        />
      </LabeledField>
      <LabeledField label="Price (R$)" help="Public consumer price">
        <input
          className="field"
          type="number"
          min={0}
          step={0.01}
          value={draft.price === 0 ? "" : draft.price}
          onChange={(e) => onChange({ price: parseFloat(e.target.value) || 0 })}
          placeholder="0.00"
        />
      </LabeledField>
    </div>
  );
}
