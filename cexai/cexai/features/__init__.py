"""Shipped CEXAI features built on the foundation.

The canonical sentiment_classifier (the cross-provider parity probe for SC-001 /
SC-003) lands here in W5. Each feature is invocable via both CLI and library API
per Article II.

Importing this package imports each feature module, whose import-time
``register_feature`` side effect makes it discoverable to both invocation
interfaces. ``import cexai.features`` is therefore the one line an application
runs to make every shipped feature available on the ``cexai`` CLI.

The activation wave adds three more features built on existing subsystems:
``content_factory_feature`` (content-factory), ``planning_feature`` (plan), and
``providers_feature`` (providers) -- each a thin wrapper registered the same way.
"""

from cexai.features import (
    content_factory_feature,
    planning_feature,
    providers_feature,
    sentiment_classifier,
)
from cexai.features.content_factory_feature import make_video
from cexai.features.planning_feature import plan
from cexai.features.providers_feature import list_providers
from cexai.features.sentiment_classifier import classify

__all__ = [
    "sentiment_classifier",
    "classify",
    "content_factory_feature",
    "make_video",
    "planning_feature",
    "plan",
    "providers_feature",
    "list_providers",
]
