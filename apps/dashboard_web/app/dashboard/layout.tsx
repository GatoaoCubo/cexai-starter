"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ApiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { getEntitySchemas } from "@/lib/entities";
import { Wordmark } from "@/components/ui";
import {
  AgentIcon,
  CatalogIcon,
  CheckIcon,
  CrewIcon,
  GridIcon,
  HistoryIcon,
  HomeIcon,
  ResearchIcon,
  SettingsIcon,
  SignOutIcon,
  TableIcon,
} from "@/components/icons";

/**
 * Authenticated shell. A fixed left "spine" carries tenant context + nav; the
 * main column renders the active view. Guards the route: no session -> /login.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { session, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const token = session && session.access_token ? session.access_token : "";
  const client = useMemo(() => (token ? new ApiClient(token) : null), [token]);

  // The management half is OVERLAY-DRIVEN: "Data" shows only when management is
  // enabled AND the tenant's overlay declares >= 1 manageable entity. We load
  // the schema count from the same overlay source (ApiClient.listEntitySchemas:
  // GET /entities-config live, fixtures offline). A tenant with no entities (or
  // a failed/empty load) never sees the nav item -- nothing is hardcoded on.
  const [hasEntities, setHasEntities] = useState(false);

  // The Review nav (SPEC 10 W5 -- the content-review HITL gate) shows only when the
  // tenant has >= 1 PUBLISHABLE entity (an entity with a draft/published gate to
  // review). Computed from the SAME overlay schema load as Data -- no extra request,
  // same degrade-closed posture (a failed/empty load hides the nav).
  const [hasPublishable, setHasPublishable] = useState(false);

  // The Agents nav is OVERLAY-GATED too (ADR Phase A): "Agents" shows only when
  // the tenant's catalog+overlay yields >= 1 agent (the SAME degrade-closed
  // posture as Data -- a tenant with no agents never sees the nav item). Loaded
  // from the same mode-transparent ApiClient (GET /agents live, fixtures offline).
  const [hasAgents, setHasAgents] = useState(false);

  // The Crews nav is OVERLAY-GATED too (ADR Phase D -- the layer above agents):
  // "Crews" shows only when the tenant's catalog+overlay yields >= 1 crew (the SAME
  // degrade-closed posture as Agents). Loaded from the same mode-transparent
  // ApiClient (GET /crews live, fixtures offline).
  const [hasCrews, setHasCrews] = useState(false);

  useEffect(() => {
    if (session === null) router.replace("/login");
  }, [session, router]);

  useEffect(() => {
    let active = true;
    if (!config.enableManagement || !client) {
      setHasEntities(false);
      setHasPublishable(false);
      return;
    }
    getEntitySchemas(client)
      .then((schemas) => {
        if (!active) return;
        setHasEntities(schemas.length > 0);
        // SPEC 10 W5: the Review nav gates on a publishable entity existing.
        setHasPublishable(schemas.some((s) => s.publishable === true));
      })
      .catch(() => {
        // Degrade closed: a failed overlay load hides the management nav rather
        // than surfacing a broken "Data" link.
        if (active) {
          setHasEntities(false);
          setHasPublishable(false);
        }
      });
    return () => {
      active = false;
    };
  }, [client]);

  useEffect(() => {
    let active = true;
    if (!client) {
      setHasAgents(false);
      return;
    }
    client
      .listAgents()
      .then((list) => {
        if (active) setHasAgents(list.length > 0);
      })
      .catch(() => {
        // Degrade closed: a failed load hides the Agents nav rather than
        // surfacing a broken link.
        if (active) setHasAgents(false);
      });
    return () => {
      active = false;
    };
  }, [client]);

  useEffect(() => {
    let active = true;
    if (!client) {
      setHasCrews(false);
      return;
    }
    client
      .listCrews()
      .then((list) => {
        if (active) setHasCrews(list.length > 0);
      })
      .catch(() => {
        // Degrade closed: a failed load hides the Crews nav rather than
        // surfacing a broken link.
        if (active) setHasCrews(false);
      });
    return () => {
      active = false;
    };
  }, [client]);

  // While resolving or redirecting, hold a quiet frame.
  if (!session) {
    return (
      <main className="grid min-h-screen place-items-center">
        <div className="animate-filament-pulse">
          <Wordmark />
        </div>
      </main>
    );
  }

  const hasManagement = config.enableManagement && hasEntities;

  const nav = [
    { href: "/dashboard/home", label: "Home", icon: HomeIcon, exact: true },
    { href: "/dashboard", label: "Capabilities", icon: GridIcon, exact: true },
    // The Research Universe hero flow (spec_dashboard_roadmap W4). Always visible --
    // a core capability surface (like Capabilities), not overlay-gated.
    { href: "/dashboard/research", label: "Research", icon: ResearchIcon, exact: false },
    // Spec Catalog: navigable quality map of all capabilities + agents + crews.
    // Always visible -- a read-only reference, not an action surface.
    { href: "/dashboard/catalog", label: "Catalog", icon: CatalogIcon, exact: false },
    ...(hasAgents
      ? [{ href: "/dashboard/agents", label: "Agents", icon: AgentIcon, exact: false }]
      : []),
    ...(hasCrews
      ? [{ href: "/dashboard/crews", label: "Crews", icon: CrewIcon, exact: false }]
      : []),
    ...(hasManagement
      ? [{ href: "/dashboard/data", label: "Data", icon: TableIcon, exact: false }]
      : []),
    // Review (SPEC 10 W5): the content-review HITL gate. Shown only when a
    // publishable entity exists (there is a draft/published gate to review).
    ...(hasManagement && hasPublishable
      ? [{ href: "/dashboard/review", label: "Review", icon: CheckIcon, exact: false }]
      : []),
    { href: "/dashboard/results", label: "Results", icon: HistoryIcon, exact: false },
    // GO_ONLINE A2 (spec 23 FR-003): the /intake waitlist lead queue. Visible
    // to all authenticated sessions, NOT tenant-scoped (DECISIONS -- pre-launch
    // there is effectively one tenant on this dashboard; revisit if/when real
    // paying tenants share it). Unlike Agents/Crews/Data above, this is a
    // STATIC entry (not overlay-gated) -- it always appears, mirroring Results.
    { href: "/dashboard/waitlist", label: "Waitlist", icon: TableIcon, exact: false },
    { href: "/dashboard/settings", label: "Settings", icon: SettingsIcon, exact: false },
  ];

  const isActive = (item: { href: string; exact: boolean }) =>
    item.exact ? pathname === item.href : pathname.startsWith(item.href);

  const tenantLabel = session.tenant_label || "Tenant";
  const tenantShort = session.tenant_id
    ? `${session.tenant_id.slice(0, 8)}`
    : "unbound";

  return (
    <div className="flex min-h-screen">
      {/* ---- the spine -------------------------------------------------- */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-line bg-ink-800/60 px-4 py-6 backdrop-blur md:flex">
        <div className="px-2">
          <Wordmark />
        </div>

        {/* tenant context card -- always visible, never editable */}
        <div className="mt-7 panel px-3.5 py-3.5">
          <p className="eyebrow mb-2">Tenant context</p>
          <p className="font-display text-base font-600 text-text">
            {tenantLabel}
          </p>
          <p className="mt-1 font-mono text-2xs text-text-faint" title={session.tenant_id}>
            {tenantShort}
          </p>
          <div className="mt-3 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-synapse" />
            <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              {config.fixtures ? "fixtures" : "live"}
            </span>
          </div>
        </div>

        <nav className="mt-7 flex flex-1 flex-col gap-1">
          {nav.map((item) => {
            const active = isActive(item);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                  active
                    ? "bg-synapse/10 text-synapse"
                    : "text-text-muted hover:bg-panel hover:text-text",
                ].join(" ")}
                aria-current={active ? "page" : undefined}
              >
                <Icon />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto border-t border-line pt-4">
          <p className="px-3 font-mono text-2xs text-text-faint" title={session.email}>
            {session.email}
          </p>
          <button
            onClick={() => signOut()}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-text-muted transition-colors hover:bg-panel hover:text-danger"
          >
            <SignOutIcon />
            Sign out
          </button>
        </div>
      </aside>

      {/* ---- mobile top bar -------------------------------------------- */}
      <div className="flex w-full flex-col">
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-line bg-ink-800/80 px-4 py-3 backdrop-blur md:hidden">
          <Wordmark compact />
          <div className="flex items-center gap-3">
            <span className="chip">{tenantLabel}</span>
            <button
              onClick={() => signOut()}
              className="text-text-muted hover:text-danger"
              aria-label="Sign out"
            >
              <SignOutIcon />
            </button>
          </div>
        </header>

        {/* mobile nav */}
        <nav className="flex gap-1 overflow-x-auto border-b border-line px-3 py-2 md:hidden">
          {nav.map((item) => {
            const active = isActive(item);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "flex shrink-0 items-center gap-2 rounded-pill px-3 py-1.5 text-sm transition-colors",
                  active
                    ? "bg-synapse/10 text-synapse"
                    : "text-text-muted hover:text-text",
                ].join(" ")}
              >
                <Icon />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <main className="flex-1 px-5 py-8 sm:px-8 lg:px-12">{children}</main>
      </div>
    </div>
  );
}
