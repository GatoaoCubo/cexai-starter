"use client";

// ----------------------------------------------------------------------------
// RenderBoundary -- a minimal client-side React error boundary (degrade-never).
//
// If a child subtree throws DURING RENDER, React unmounts up to the nearest error
// boundary. Without one, a throw inside (say) DualOutputFace would erase the WHOLE
// ResultView -- the silent-drop failure mode the W5-FIX guards against. This boundary
// catches that throw and shows ``fallback`` instead, so the rest of the result view
// keeps rendering and the user sees an honest "[previa indisponivel]" note rather
// than a blank screen.
//
// Class component on purpose: getDerivedStateFromError is the only React API that can
// turn a render throw into fallback UI (hooks cannot). ASCII-only house style.
// ----------------------------------------------------------------------------

import { Component, type ReactNode } from "react";

interface RenderBoundaryProps {
  children: ReactNode;
  /** shown when a child render throws; defaults to nothing (renders null). */
  fallback?: ReactNode;
}

interface RenderBoundaryState {
  failed: boolean;
}

export class RenderBoundary extends Component<
  RenderBoundaryProps,
  RenderBoundaryState
> {
  state: RenderBoundaryState = { failed: false };

  static getDerivedStateFromError(): RenderBoundaryState {
    return { failed: true };
  }

  render() {
    if (this.state.failed) return this.props.fallback ?? null;
    return this.props.children;
  }
}
