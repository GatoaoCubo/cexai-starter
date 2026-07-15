"use client";

// =============================================================================
// editor/ImageUploader.tsx -- media URL[] editor + the upload HANDLER seam
// =============================================================================
//
// Controlled images value/onChange editor for the `images` field kind. The list
// of URLs is the field VALUE (declarative). File selection is the HANDLER SEAM:
// `onFilesSelected` is wired by the renderer to the tenant's upload handler
// (HandlerRegistry.upload) -- with NO handler bound it is an INERT no-op (the
// control still renders + the URL list still validates). A URL can also be added
// by hand (the structural-proof path that needs no storage). Domain-neutral;
// ZERO tenant literals.

import { useRef, useState } from "react";

export interface ImageUploaderProps {
  images: string[];
  onImagesChange: (next: string[]) => void;
  /** The upload HANDLER seam. Inert no-op when no tenant handler is bound. */
  onFilesSelected?: (files: File[]) => void;
  maxFiles?: number;
}

export function ImageUploader({
  images,
  onImagesChange,
  onFilesSelected,
  maxFiles = 9,
}: ImageUploaderProps) {
  const [urlInput, setUrlInput] = useState("");
  const fileRef = useRef<HTMLInputElement | null>(null);
  const items = images ?? [];
  const atMax = items.length >= maxFiles;

  const addUrl = () => {
    const trimmed = urlInput.trim();
    if (!trimmed || items.includes(trimmed) || atMax) return;
    onImagesChange([...items, trimmed]);
    setUrlInput("");
  };

  const remove = (i: number) => onImagesChange(items.filter((_, idx) => idx !== i));

  const onPick = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    // The upload SEAM. A bound tenant handler turns these Files into URLs and
    // appends them; with no handler this is a no-op (inert by design).
    onFilesSelected?.(Array.from(files));
  };

  return (
    <div>
      <div className="flex gap-2">
        <input
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addUrl();
            }
          }}
          disabled={atMax}
          className="field flex-1"
          placeholder={atMax ? `Limite de ${maxFiles} atingido` : "URL da imagem/vídeo"}
        />
        <button
          type="button"
          onClick={addUrl}
          disabled={atMax}
          className="btn-ghost px-3 text-lg leading-none"
          aria-label="Adicionar URL"
        >
          +
        </button>
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={atMax}
          className="btn-ghost px-3 py-1.5 text-sm"
        >
          Enviar
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*,video/*"
          multiple
          className="hidden"
          onChange={(e) => onPick(e.target.files)}
        />
      </div>
      {items.length > 0 && (
        <ul className="mt-2 space-y-1.5">
          {items.map((url, i) => (
            <li
              key={i}
              className="flex items-center gap-2 rounded-md border border-line bg-panel-sunken px-2.5 py-1.5"
            >
              {i === 0 && (
                <span className="rounded-pill border border-line px-1.5 py-0.5 font-mono text-2xs text-text-faint">
                  capa
                </span>
              )}
              <span className="flex-1 truncate font-mono text-2xs text-text-muted">{url}</span>
              <button
                type="button"
                onClick={() => remove(i)}
                className="text-text-faint hover:text-danger"
                aria-label={"Remover imagem " + (i + 1)}
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
