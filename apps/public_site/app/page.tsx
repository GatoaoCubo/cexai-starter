// Single-tenant sovereign build: the canonical entry "/" renders the self tenant
// storefront (cex_distill apps-collapse rewrote the multi-tenant neutral root).
import { redirect } from "next/navigation";

export default function RootPage() {
  redirect("/t/starter");
}
