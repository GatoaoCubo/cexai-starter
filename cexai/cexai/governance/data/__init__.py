"""CEXAI governance data lane -- the centralized multi-tenant Supabase data plane
(mission MULTITENANT_DATA_PLANE, task T1; spec_multitenant_data_plane_v1).

The data lane is the THIRD tenant-boundary enforcement point, alongside the file
tier (``_tools.cex_tenant_paths.deny_cross_tenant``) and the inference tier
(``governance.rbac.inference_gate.authorize_inference``). ``SupabaseDataAdapter``
takes ``tenant_id`` as an EXPLICIT argument and MUST NOT import repo-root
``_tools`` (the package is extraction-bound, cexai/pyproject.toml); it MIRRORS the
fail-closed cross-tenant equality invariant rather than importing it -- the same
seam, for the same reason, as ``inference_gate.py`` (spec A.3).

Import is light (Article VIII): only stdlib + intra-package names at import time;
NO concrete DB driver is imported here or in ``adapter`` (the ``DbSession``
Protocol is the injected seam). The two public names below are re-exported for
caller ergonomics, mirroring ``governance.rbac``.

absorbs: convergence/multitenant-data-plane (T1 -- data plane)
"""

from cexai.governance.data.adapter import SupabaseDataAdapter
from cexai.governance.data.errors import TenantDataDenied
from cexai.governance.data.marketplace_observation import (
    MarketplaceObservationStore,
    Observation,
)

__all__ = [
    "SupabaseDataAdapter",
    "TenantDataDenied",
    "MarketplaceObservationStore",
    "Observation",
]
