"use client";

// =============================================================================
// editor/AttributesEditor.tsx -- key/value jsonb bag editor (domain-neutral)
// =============================================================================
//
// Controlled editor for the `keyValue` field kind: an arbitrary string->unknown
// record (e.g. category-specific marketplace attributes). Renders as a list of
// key/value rows with add / remove; the value is held as a string in the UI (the
// schema is z.record(z.string(), z.unknown()), so a string value is valid).
// Domain-neutral; ZERO tenant literals.

import { useState } from "react";

export interface AttributesEditorProps {
  value?: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
  maxItems?: number;
}

export function AttributesEditor({ value, onChange, maxItems = 50 }: AttributesEditorProps) {
  const [k, setK] = useState("");
  const [v, setV] = useState("");
  const entries = Object.entries(value ?? {});
  const atMax = entries.length >= maxItems;

  const add = () => {
    const key = k.trim();
    if (!key || atMax) return;
    onChange({ ...(value ?? {}), [key]: v });
    setK("");
    setV("");
  };

  const remove = (key: string) => {
    const next = { ...(value ?? {}) };
    delete next[key];
    onChange(next);
  };

  return (
    <div>
      <div className="flex gap-2">
        <input
          value={k}
          onChange={(e) => setK(e.target.value)}
          disabled={atMax}
          className="field flex-1"
          placeholder="Chave"
        />
        <input
          value={v}
          onChange={(e) => setV(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          disabled={atMax}
          className="field flex-1"
          placeholder="Valor"
        />
        <button
          type="button"
          onClick={add}
          disabled={atMax}
          className="btn-ghost px-3 text-lg leading-none"
          aria-label="Adicionar atributo"
        >
          +
        </button>
      </div>
      {entries.length > 0 && (
        <ul className="mt-2 space-y-1.5">
          {entries.map(([key, val]) => (
            <li
              key={key}
              className="flex items-center gap-2 rounded-md border border-line bg-panel-sunken px-2.5 py-1.5"
            >
              <span className="font-mono text-2xs text-text">{key}</span>
              <span className="font-mono text-2xs text-text-faint">=</span>
              <span className="flex-1 truncate font-mono text-2xs text-text-muted">
                {String(val)}
              </span>
              <button
                type="button"
                onClick={() => remove(key)}
                className="text-text-faint hover:text-danger"
                aria-label={"Remover " + key}
              >
                x
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
