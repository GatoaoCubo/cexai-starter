"use client";

// =============================================================================
// editor/MediaKitUploader.tsx -- MediaKitImage[] editor + upload HANDLER seam
// =============================================================================
//
// Controlled editor for the `mediaKit` field kind (the B2B media kit). Each entry
// is a {slot, url, type, alt} record (mediaKitImageSchema). Like ImageUploader,
// real upload is the HANDLER SEAM (tenant-bound); this component manages the typed
// records + a hasMediaKit toggle. With no handler bound the add-by-URL path keeps
// the control functional for the structural proof. Domain-neutral; ZERO tenant literals.

import { useState } from "react";
import type { MediaKitImage } from "./types";

const SLOT_TYPES: MediaKitImage["type"][] = [
  "hero",
  "angle",
  "usage",
  "detail1",
  "detail2",
  "lifestyle1",
  "lifestyle2",
  "packaging",
  "comparison",
];

export interface MediaKitUploaderProps {
  images: MediaKitImage[];
  onImagesChange: (next: MediaKitImage[]) => void;
  hasMediaKit?: boolean;
  onHasMediaKitChange?: (next: boolean) => void;
}

export function MediaKitUploader({
  images,
  onImagesChange,
  hasMediaKit,
  onHasMediaKitChange,
}: MediaKitUploaderProps) {
  const [urlInput, setUrlInput] = useState("");
  const items = images ?? [];
  const atMax = items.length >= SLOT_TYPES.length;

  const add = () => {
    const trimmed = urlInput.trim();
    if (!trimmed || atMax) return;
    const slot = items.length + 1;
    onImagesChange([
      ...items,
      { slot, url: trimmed, type: SLOT_TYPES[Math.min(slot - 1, SLOT_TYPES.length - 1)] },
    ]);
    setUrlInput("");
  };

  const update = (i: number, patch: Partial<MediaKitImage>) => {
    onImagesChange(items.map((it, idx) => (idx === i ? { ...it, ...patch } : it)));
  };

  const remove = (i: number) => onImagesChange(items.filter((_, idx) => idx !== i));

  return (
    <div>
      {onHasMediaKitChange && (
        <label className="mb-2 flex items-center gap-2 text-sm text-text-muted">
          <input
            type="checkbox"
            checked={!!hasMediaKit}
            onChange={(e) => onHasMediaKitChange(e.target.checked)}
          />
          Media kit ativo
        </label>
      )}
      <div className="flex gap-2">
        <input
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          disabled={atMax}
          className="field flex-1"
          placeholder={atMax ? "Todos os slots preenchidos" : "URL da imagem do kit"}
        />
        <button
          type="button"
          onClick={add}
          disabled={atMax}
          className="btn-ghost px-3 text-lg leading-none"
          aria-label="Adicionar imagem do kit"
        >
          +
        </button>
      </div>
      {items.length > 0 && (
        <ul className="mt-2 space-y-1.5">
          {items.map((it, i) => (
            <li
              key={i}
              className="flex items-center gap-2 rounded-md border border-line bg-panel-sunken px-2.5 py-1.5"
            >
              <span className="font-mono text-2xs text-text-faint">slot {it.slot}</span>
              <select
                value={it.type}
                onChange={(e) => update(i, { type: e.target.value as MediaKitImage["type"] })}
                className="field font-mono text-2xs"
              >
                {SLOT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <span className="flex-1 truncate font-mono text-2xs text-text-muted">{it.url}</span>
              <button
                type="button"
                onClick={() => remove(i)}
                className="text-text-faint hover:text-danger"
                aria-label={"Remover slot " + it.slot}
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
