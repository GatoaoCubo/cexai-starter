"use client";

import type { SectionProps } from "./types";

const MAX_IMAGES = 9;

export function ImagesSection({ draft, onChange }: SectionProps) {
  const { images } = draft;

  const add = () => {
    if (images.length >= MAX_IMAGES) return;
    onChange({ images: [...images, ""] });
  };

  const update = (i: number, url: string) => {
    const next = [...images];
    next[i] = url;
    onChange({ images: next });
  };

  const remove = (i: number) => {
    onChange({ images: images.filter((_, idx) => idx !== i) });
  };

  const move = (from: number, dir: -1 | 1) => {
    const to = from + dir;
    if (to < 0 || to >= images.length) return;
    const next = [...images];
    [next[from], next[to]] = [next[to], next[from]];
    onChange({ images: next });
  };

  return (
    <div className="space-y-3">
      <p className="font-mono text-2xs text-text-faint">
        {images.length} / {MAX_IMAGES} images. First image = cover.
      </p>
      {images.map((url, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-5 shrink-0 text-right font-mono text-2xs text-text-faint">
            {i + 1}
          </span>
          <input
            className="field flex-1"
            value={url}
            onChange={(e) => update(i, e.target.value)}
            placeholder="https://... or /assets/..."
            aria-label={"Image " + (i + 1) + " URL"}
          />
          <button
            type="button"
            onClick={() => move(i, -1)}
            disabled={i === 0}
            className="btn-ghost px-2 text-xs disabled:opacity-30"
            aria-label="Move up"
          >
            ^
          </button>
          <button
            type="button"
            onClick={() => move(i, 1)}
            disabled={i === images.length - 1}
            className="btn-ghost px-2 text-xs disabled:opacity-30"
            aria-label="Move down"
          >
            v
          </button>
          <button
            type="button"
            onClick={() => remove(i)}
            className="btn-ghost px-2 text-xs text-danger"
            aria-label="Remove image"
          >
            x
          </button>
        </div>
      ))}
      {images.length < MAX_IMAGES && (
        <button type="button" onClick={add} className="btn-ghost mt-1">
          + Add image
        </button>
      )}
    </div>
  );
}
