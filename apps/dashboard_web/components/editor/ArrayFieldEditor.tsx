"use client";

// =============================================================================
// editor/ArrayFieldEditor.tsx -- ordered string[] editor (domain-neutral)
// =============================================================================
//
// Controlled value/onChange editor for the `orderedArray` field kind: an ordered
// list of free-text lines with add / remove / move-up / move-down, optionally
// rendered with a 1. 2. 3. number gutter (the `numbered` flag). Domain-neutral;
// ZERO tenant literals. Built on the dashboard's CSS atoms.

import { useState } from "react";

export interface ArrayFieldEditorProps {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
  numbered?: boolean;
  maxItems?: number;
}

export function ArrayFieldEditor({
  value,
  onChange,
  placeholder,
  numbered = false,
  maxItems = 20,
}: ArrayFieldEditorProps) {
  const [input, setInput] = useState("");
  const items = value ?? [];
  const atMax = items.length >= maxItems;

  const add = () => {
    const trimmed = input.trim();
    if (!trimmed || atMax) return;
    onChange([...items, trimmed]);
    setInput("");
  };

  const remove = (i: number) => onChange(items.filter((_, idx) => idx !== i));

  const move = (i: number, dir: -1 | 1) => {
    const j = i + dir;
    if (j < 0 || j >= items.length) return;
    const next = [...items];
    [next[i], next[j]] = [next[j], next[i]];
    onChange(next);
  };

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
          placeholder={atMax ? `Limite de ${maxItems} atingido` : placeholder ?? "Adicionar passo..."}
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
        <ol className="mt-2 space-y-1.5">
          {items.map((v, i) => (
            <li
              key={i}
              className="flex items-center gap-2 rounded-md border border-line bg-panel-sunken px-2.5 py-1.5"
            >
              {numbered && (
                <span className="font-mono text-2xs text-text-faint">{i + 1}.</span>
              )}
              <span className="flex-1 text-sm text-text-muted">{v}</span>
              <button
                type="button"
                onClick={() => move(i, -1)}
                disabled={i === 0}
                className="text-text-faint hover:text-text disabled:opacity-30"
                aria-label="Mover para cima"
              >
                ^
              </button>
              <button
                type="button"
                onClick={() => move(i, 1)}
                disabled={i === items.length - 1}
                className="text-text-faint hover:text-text disabled:opacity-30"
                aria-label="Mover para baixo"
              >
                v
              </button>
              <button
                type="button"
                onClick={() => remove(i)}
                className="text-text-faint hover:text-danger"
                aria-label={"Remover item " + (i + 1)}
              >
                x
              </button>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
