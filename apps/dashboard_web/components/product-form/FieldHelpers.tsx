"use client";

import type { ReactNode } from "react";
import { useState } from "react";

export function LabeledField({
  label,
  help,
  children,
}: {
  label: string;
  help?: string;
  children: ReactNode;
}) {
  return (
    <div>
      <p className="mb-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted">
        {label}
      </p>
      {children}
      {help && (
        <p className="mt-1 font-mono text-2xs text-text-faint">{help}</p>
      )}
    </div>
  );
}

export function TagField({
  values,
  onChange,
  placeholder,
}: {
  values: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState("");

  const add = () => {
    const trimmed = input.trim();
    if (!trimmed || values.includes(trimmed)) return;
    onChange([...values, trimmed]);
    setInput("");
  };

  const remove = (i: number) => {
    onChange(values.filter((_, idx) => idx !== i));
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
          className="field flex-1"
          placeholder={placeholder ?? "Add..."}
        />
        <button
          type="button"
          onClick={add}
          className="btn-ghost px-3 text-lg leading-none"
          aria-label="Add item"
        >
          +
        </button>
      </div>
      {values.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {values.map((v, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1 rounded-pill border border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs text-text-muted"
            >
              {v}
              <button
                type="button"
                onClick={() => remove(i)}
                className="ml-0.5 text-text-faint hover:text-danger"
                aria-label={"Remove " + v}
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
