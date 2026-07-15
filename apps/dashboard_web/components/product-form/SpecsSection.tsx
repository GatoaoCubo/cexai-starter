"use client";

import { LabeledField, TagField } from "./FieldHelpers";
import type { ProductDims, SectionProps } from "./types";

const DIM_KEYS: (keyof ProductDims)[] = ["largura", "altura", "profundidade"];
const UNITS = ["cm", "mm", "m", "in"] as const;

export function SpecsSection({ draft, onChange }: SectionProps) {
  const { dims } = draft;

  const setDim = (key: keyof ProductDims, val: string) =>
    onChange({ dims: { ...dims, [key]: val } });

  return (
    <div className="space-y-5">
      <div>
        <p className="mb-3 font-mono text-2xs uppercase tracking-wider text-text-muted">
          Dimensions
        </p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {DIM_KEYS.map((key) => (
            <LabeledField key={key} label={key}>
              <input
                className="field"
                value={dims[key] as string}
                onChange={(e) => setDim(key, e.target.value)}
                placeholder="0"
                aria-label={"Dimension " + key}
              />
            </LabeledField>
          ))}
          <LabeledField label="Unit">
            <select
              className="field"
              value={dims.unit}
              onChange={(e) =>
                setDim("unit", e.target.value as ProductDims["unit"])
              }
            >
              {UNITS.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </LabeledField>
        </div>
      </div>
      <LabeledField label="Weight" help="e.g. 350g or 1.2kg">
        <input
          className="field"
          value={draft.weight}
          onChange={(e) => onChange({ weight: e.target.value })}
          placeholder="0g"
        />
      </LabeledField>
      <LabeledField label="Materials" help="Press Enter to add each material">
        <TagField
          values={draft.materials}
          onChange={(v) => onChange({ materials: v })}
          placeholder="Ceramica..."
        />
      </LabeledField>
    </div>
  );
}
