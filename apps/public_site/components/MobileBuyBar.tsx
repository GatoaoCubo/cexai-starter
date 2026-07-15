"use client";

// ----------------------------------------------------------------------------
// MobileBuyBar -- a mobile-only (lg:hidden) fixed bottom buy CTA for the PDP.
//
// On mobile the in-page buy-box CTA scrolls out of view; this fixed bar keeps the
// primary action reachable. It MIRRORS the in-page CTA exactly: the SAME external
// https-only buy_url, opened in a new tab, rel-hardened (noopener noreferrer
// nofollow). It is NOT a fake cart -- it is the same external link, pinned.
//
// NO DOUBLE CTA: an IntersectionObserver watches the in-page buy-box CTA (passed by
// id). While that CTA is on screen the bar is HIDDEN; it appears only once the real
// CTA has scrolled away. Degrade-never: if IntersectionObserver is unavailable (or no
// anchor is found) the bar simply stays visible (the safe default -- the CTA is always
// reachable). Visible only below lg (the desktop buy-box is sticky already).
//
// SECURITY: renders ONLY when ``buyUrl`` is a non-empty (already https-validated by
// the caller's buyUrlOf) string. It builds no other URL. Safe-area-inset padding keeps
// the CTA clear of the home indicator on notched devices.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { useEffect, useRef, useState } from "react";
import { ArrowRightIcon } from "./icons";

export function MobileBuyBar({
  buyUrl,
  label = "Ver / comprar",
  /** id of the in-page CTA element to watch -- the bar hides while it is on screen. */
  watchId,
}: {
  buyUrl: string;
  label?: string;
  watchId?: string;
}) {
  // Start hidden, then reveal once we know the in-page CTA is NOT on screen. If there
  // is no anchor / no IntersectionObserver, we fall back to visible (safe default).
  const [visible, setVisible] = useState(false);
  const observedRef = useRef(false);

  useEffect(() => {
    if (!buyUrl) return;
    const target = watchId ? document.getElementById(watchId) : null;
    if (!target || typeof IntersectionObserver === "undefined") {
      // no anchor to watch (or no IO) -> keep the CTA reachable: show the bar.
      setVisible(true);
      return;
    }
    observedRef.current = true;
    const io = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        // hide the bar while the in-page CTA is on screen; show it once it leaves.
        setVisible(!entry.isIntersecting);
      },
      { threshold: 0 },
    );
    io.observe(target);
    return () => io.disconnect();
  }, [buyUrl, watchId]);

  if (!buyUrl) return null;

  return (
    <div
      data-testid="mobile-buy-bar"
      aria-hidden={visible ? undefined : "true"}
      className={[
        "fixed inset-x-0 bottom-0 z-[1030] border-t border-border bg-background/95 backdrop-blur-sm lg:hidden",
        "transition-transform duration-base ease-standard",
        visible ? "translate-y-0" : "translate-y-full",
      ].join(" ")}
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="shell flex h-14 items-center">
        <a
          href={buyUrl}
          target="_blank"
          rel="noopener noreferrer nofollow"
          tabIndex={visible ? undefined : -1}
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-pill bg-brand px-5 text-sm font-semibold text-brand-foreground shadow-sm transition-all duration-base ease-standard active:scale-[0.98]"
        >
          {label}
          <ArrowRightIcon />
        </a>
      </div>
    </div>
  );
}
