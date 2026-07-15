"use client";

// ----------------------------------------------------------------------------
// Reveal -- a tasteful reveal-on-scroll wrapper (fade-in-up) for the storefront.
// CLIENT component (it observes its own visibility).
//
// CRAFT + ACCESSIBILITY: the element starts slightly translated + transparent and
// transitions to its resting state the first time it scrolls into view (one-time,
// never loops -- mirrors design_system.md s5 "one-time reveals"). It RESPECTS
// prefers-reduced-motion: when the user asks for reduced motion, the element is
// rendered in its final state immediately with NO transform and NO transition (the
// global index.css rule also clamps any residual transition to ~0ms, belt + braces).
//
// DEGRADE-NEVER + SSR/TEST-SAFE: when IntersectionObserver is unavailable (server
// render, jsdom tests, very old browsers) the content is shown immediately in its
// resting state. The wrapped content is ALWAYS in the DOM (it is never unmounted or
// hidden from assistive tech / crawlers) -- only its opacity + transform animate.
// This keeps every existing test (which asserts text is present) green.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { useEffect, useRef, useState, type ReactNode } from "react";

/** True when the environment asks for reduced motion (total; false when unknown). */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }
  try {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch {
    return false;
  }
}

export function Reveal({
  children,
  /** stagger delay in ms (for sequenced grids); clamped to a tasteful ceiling. */
  delay = 0,
  /** semantic wrapper element (defaults to a div). */
  as: Tag = "div",
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  as?: "div" | "section" | "li" | "article";
  className?: string;
}) {
  const ref = useRef<HTMLElement | null>(null);
  // Start visible when motion is reduced OR IntersectionObserver is unavailable (SSR /
  // jsdom): the content must never depend on JS to be present.
  const [shown, setShown] = useState(false);
  const [armed, setArmed] = useState(true);

  useEffect(() => {
    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") {
      setArmed(false);
      setShown(true);
      return;
    }
    const el = ref.current;
    if (!el) {
      setShown(true);
      return;
    }
    // Reveal as soon as ANY part of the element enters the viewport. A positive bottom
    // rootMargin pre-arms content just below the fold so it is already settling by the
    // time it scrolls into view (no jarring "empty then pop"). Anything already on
    // screen at mount reveals on the first observer callback.
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setShown(true);
            obs.disconnect();
            break;
          }
        }
      },
      { rootMargin: "0px 0px 12% 0px", threshold: 0 },
    );
    obs.observe(el);
    // Safety net: if for any reason the observer never fires (edge layouts, instant
    // print), reveal shortly after mount so content is never stuck transparent.
    const fallback = window.setTimeout(() => setShown(true), 1200);
    return () => {
      obs.disconnect();
      window.clearTimeout(fallback);
    };
  }, []);

  const cappedDelay = Math.max(0, Math.min(delay, 240));

  const motionClass = armed
    ? [
        "transition-[opacity,transform] duration-slow ease-emphasized will-change-transform",
        shown ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4",
      ].join(" ")
    : "opacity-100";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Comp = Tag as any;
  return (
    <Comp
      ref={ref}
      className={[motionClass, className].join(" ").trim()}
      style={armed && cappedDelay ? { transitionDelay: `${cappedDelay}ms` } : undefined}
    >
      {children}
    </Comp>
  );
}
