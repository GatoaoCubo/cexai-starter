"""The ``@traced`` decorator -- wrap any callable in a span.

Opens a span named ``name`` (default: the wrapped function's ``__qualname__``)
as the current span for the duration of the call, so a ``@traced`` function
invoked inside another span nests under it (standard OTel context). On a raised
exception the span status is set to ERROR, the exception is recorded as a span
event, and the original exception re-raises unchanged. Arguments are NOT
captured (no PII by default).

Usage (all equivalent for the no-name case)::

    @traced
    def f(): ...

    @traced()
    def g(): ...

    @traced("custom-span-name")
    def h(): ...

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from opentelemetry.trace.status import Status, StatusCode

from cexai.foundation.tracing.spans import get_tracer

__all__ = ["traced"]

_F = TypeVar("_F", bound=Callable[..., Any])
_DEFAULT_TRACER = "cexai"


def traced(name: str | Callable[..., Any] | None = None) -> Any:
    """Decorate a callable so each invocation is wrapped in a span. Accepts a
    span name, or is applied bare (``@traced``) to use the function qualname."""
    if callable(name):
        # Bare usage: @traced (name is actually the decorated function).
        return _wrap(name, None)

    def decorator(func: _F) -> _F:
        return _wrap(func, name)

    return decorator


def _wrap(func: _F, span_name: str | None) -> _F:
    resolved = span_name or func.__qualname__

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tracer = get_tracer(func.__module__ or _DEFAULT_TRACER)
        with tracer.start_as_current_span(resolved) as span:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.record_exception(exc)
                raise

    return wrapper  # type: ignore[return-value]
