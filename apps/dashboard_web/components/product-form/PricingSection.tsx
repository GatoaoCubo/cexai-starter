"use client";

import { LabeledField } from "./FieldHelpers";
import type { SectionProps } from "./types";

function derivedPrice(custo: number, margem: number): string {
  if (custo <= 0 || margem <= 0 || margem >= 100) return "--";
  return "R$ " + (custo / (1 - margem / 100)).toFixed(2);
}

export function PricingSection({ draft, onChange }: SectionProps) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <LabeledField label="Custo (R$)" help="Product cost (COGS)">
          <input
            className="field"
            type="number"
            min={0}
            step={0.01}
            value={draft.custo === 0 ? "" : draft.custo}
            onChange={(e) =>
              onChange({ custo: parseFloat(e.target.value) || 0 })
            }
            placeholder="0.00"
          />
        </LabeledField>
        <LabeledField label="Margem B2C (%)" help="Retail margin target">
          <input
            className="field"
            type="number"
            min={0}
            max={99}
            step={1}
            value={draft.margem_b2c}
            onChange={(e) =>
              onChange({ margem_b2c: parseFloat(e.target.value) || 0 })
            }
          />
        </LabeledField>
        <LabeledField label="Margem B2B (%)" help="Wholesale margin target">
          <input
            className="field"
            type="number"
            min={0}
            max={99}
            step={1}
            value={draft.margem_b2b}
            onChange={(e) =>
              onChange({ margem_b2b: parseFloat(e.target.value) || 0 })
            }
          />
        </LabeledField>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel px-4 py-3">
          <p className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            Auto -- Preco B2C
          </p>
          <p className="mt-1.5 font-display text-2xl font-600 text-text">
            {derivedPrice(draft.custo, draft.margem_b2c)}
          </p>
          <p className="mt-0.5 font-mono text-2xs text-text-faint">
            custo / (1 - margem_b2c / 100)
          </p>
        </div>
        <div className="rounded-lg border border-line bg-panel px-4 py-3">
          <p className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            Auto -- Preco B2B
          </p>
          <p className="mt-1.5 font-display text-2xl font-600 text-text">
            {derivedPrice(draft.custo, draft.margem_b2b)}
          </p>
          <p className="mt-0.5 font-mono text-2xs text-text-faint">
            custo / (1 - margem_b2b / 100)
          </p>
        </div>
      </div>

      <p className="font-mono text-2xs text-text-faint">
        Auto-prices are derived; they do not override the public price field in
        Basic. Use them to validate margin before setting the price.
      </p>
    </div>
  );
}
