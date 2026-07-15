"use client";

// =============================================================================
// editor/FAQEditor.tsx -- {question, answer}[] editor (domain-neutral)
// =============================================================================
//
// Controlled value/onChange editor for the `faq` field kind: a list of
// question/answer pairs with add / edit / remove. The publish-gate counts only
// PAIRS that have both a question AND an answer (countFaq in product.atoms.ts) --
// this editor lets a pair be partially filled; the gate decides if it counts.
// Domain-neutral; ZERO tenant literals.

import type { FAQItem } from "./types";

export interface FAQEditorProps {
  value: FAQItem[];
  onChange: (next: FAQItem[]) => void;
  maxItems?: number;
}

export function FAQEditor({ value, onChange, maxItems = 20 }: FAQEditorProps) {
  const items = value ?? [];
  const atMax = items.length >= maxItems;

  const add = () => {
    if (atMax) return;
    onChange([...items, { question: "", answer: "" }]);
  };

  const update = (i: number, patch: Partial<FAQItem>) => {
    onChange(items.map((it, idx) => (idx === i ? { ...it, ...patch } : it)));
  };

  const remove = (i: number) => onChange(items.filter((_, idx) => idx !== i));

  return (
    <div className="space-y-3">
      {items.map((it, i) => (
        <div key={i} className="rounded-md border border-line bg-panel-sunken p-2.5">
          <div className="mb-1.5 flex items-center justify-between">
            <span className="font-mono text-2xs text-text-faint">#{i + 1}</span>
            <button
              type="button"
              onClick={() => remove(i)}
              className="text-text-faint hover:text-danger"
              aria-label={"Remover pergunta " + (i + 1)}
            >
              x
            </button>
          </div>
          <input
            value={it.question}
            onChange={(e) => update(i, { question: e.target.value })}
            className="field mb-2 w-full"
            placeholder="Pergunta"
          />
          <textarea
            value={it.answer}
            onChange={(e) => update(i, { answer: e.target.value })}
            className="field min-h-[64px] w-full"
            placeholder="Resposta"
          />
        </div>
      ))}
      <button
        type="button"
        onClick={add}
        disabled={atMax}
        className="btn-ghost px-3 py-1.5 text-sm"
      >
        {atMax ? `Limite de ${maxItems} atingido` : "+ Adicionar pergunta"}
      </button>
    </div>
  );
}
