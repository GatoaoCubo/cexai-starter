"use client";

// =============================================================================
// editor/TagInput.tsx -- string[] chips editor (domain-neutral)
// =============================================================================
//
// Controlled value/onChange chip editor used by the `tags` / `stringArray`
// field kinds. Lifted near-verbatim from the dashboard's existing TagField
// (components/product-form/FieldHelpers.tsx) + a maxItems cap to match the reference
// TagInput contract the renderer registry expects. ZERO tenant literals.

import { useState } from "react";

export interface TagInputProps {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
  maxItems?: number;
}

export function TagInput({ value, onChange, placeholder, maxItems = 50 }: TagInputProps) {
  const [input, setInput] = useState("");
  const items = value ?? [];
  const atMax = items.length >= maxItems;

  const add = () => {
    const trimmed = input.trim();
    if (!trimmed || items.includes(trimmed) || atMax) return;
    onChange([...items, trimmed]);
    setInput("");
  };

  const remove = (i: number) => onChange(items.filter((_, idx) => idx !== i));

  return (
    <div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          disabled={atMax}
          className="field flex-1"
          placeholder={atMax ? `Limite de ${maxItems} atingido` : placeholder ?? "Adicionar..."}
        />
        <button
          type="button"
          onClick={add}
          disabled={atMax}
          className="btn-ghost px-3 text-lg leading-none"
          aria-label="Adicionar item"
        >
          +
        </button>
      </div>
      {items.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {items.map((v, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1 rounded-pill border border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs text-text-muted"
            >
              {v}
              <button
                type="button"
                onClick={() => remove(i)}
                className="ml-0.5 text-text-faint hover:text-danger"
                aria-label={"Remover " + v}
              >
                x
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
