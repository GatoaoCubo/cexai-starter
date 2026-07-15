"use client";

import { AlertIcon } from "@/components/icons";
import { LabeledField } from "./FieldHelpers";
import type { ProductStatus, SectionProps } from "./types";

const STATUSES: { value: ProductStatus; label: string }[] = [
  { value: "draft", label: "Draft" },
  { value: "active", label: "Active" },
  { value: "archived", label: "Archived" },
];

export function StockSection({ draft, onChange }: SectionProps) {
  const noVariant = draft.shopify_variant_id.trim() === "";

  return (
    <div className="space-y-5">
      {noVariant && (
        <div
          role="alert"
          className="flex items-start gap-2 rounded-lg border border-signal/30 bg-signal/5 px-4 py-3 text-sm text-signal"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>
            <strong className="font-600">Produto nao e vendavel.</strong>{" "}
            Adicione um{" "}
            <code className="rounded bg-signal/10 px-1 font-mono text-xs">
              shopify_variant_id
            </code>{" "}
            para ativar a venda neste produto.
          </span>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <LabeledField label="Status">
          <select
            className="field"
            value={draft.status}
            onChange={(e) =>
              onChange({ status: e.target.value as ProductStatus })
            }
          >
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </LabeledField>

        <LabeledField label="Quantity" help="Units in stock">
          <input
            className="field"
            type="number"
            min={0}
            step={1}
            value={draft.quantity === 0 ? "" : draft.quantity}
            onChange={(e) =>
              onChange({ quantity: parseInt(e.target.value, 10) || 0 })
            }
            placeholder="0"
          />
        </LabeledField>

        <LabeledField label="SKU" help="Internal stock identifier">
          <input
            className="field"
            value={draft.sku}
            onChange={(e) => onChange({ sku: e.target.value })}
            placeholder="SKU-001"
          />
        </LabeledField>

        <LabeledField
          label="Shopify Variant ID"
          help="Required to enable sales"
        >
          <input
            className={[
              "field",
              noVariant ? "border-signal/50 focus:ring-signal/40" : "",
            ].join(" ")}
            value={draft.shopify_variant_id}
            onChange={(e) =>
              onChange({ shopify_variant_id: e.target.value })
            }
            placeholder="gid://shopify/ProductVariant/..."
          />
        </LabeledField>
      </div>
    </div>
  );
}
