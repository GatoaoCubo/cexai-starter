"""Ollama (local) provider adapter -- the multi-runtime keystone.

Maps the frozen contracts to the ``ollama`` SDK chat API. Ollama runs locally
and needs NO API key, so it is the provider every credential-free test routes
through (Article XIV). LAZY client init: the SDK is imported and the client
built on first call. Tests inject a mock ``client=`` exposing ``chat(...)``.

CEX kind remains ``model_provider`` (P02); this is a CODE adapter.

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator, Mapping
from typing import Any

from cexai.foundation._shared.errors import ProviderCallError, ProviderConfigError
from cexai.foundation._shared.types import (
    LlmRequest,
    LlmResponse,
    LlmStreamChunk,
    ToolCallDelta,
    Usage,
)
from cexai.foundation.llm.normalizer import from_provider_tool_calls, to_provider_tools

_logger = logging.getLogger("cexai.foundation.llm.providers.ollama_provider")


def _get(obj: object, key: str, default: Any = None) -> Any:
    """Read ``key`` from a mapping OR an attribute object. The ollama SDK returns
    a ``ChatResponse`` (attribute access) while tests pass plain dicts."""
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


class OllamaProvider:
    """``LlmProvider`` adapter over a local ollama server (no API key)."""

    name = "ollama"

    def __init__(self, *, client: object | None = None, host: str | None = None) -> None:
        self._client = client
        self._host = host

    def _get_client(self) -> object:
        if self._client is not None:
            return self._client
        try:
            import ollama
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ProviderConfigError(self.name, f"ollama SDK not installed: {exc}") from exc
        host = self._host or os.environ.get("OLLAMA_HOST")
        self._client = ollama.Client(host=host) if host else ollama.Client()
        return self._client

    def _messages(self, request: LlmRequest) -> list[dict]:
        messages: list[dict] = []
        for message in request.messages:
            if isinstance(message.content, str):
                content = message.content
            else:
                # The ollama chat API takes a plain string ``content`` field --
                # it has no equivalent of the provider-agnostic multimodal
                # content-block tuple (Article VIII types.Message.content).
                # Silently coercing to "" used to drop the message body with
                # no trace; flag it loudly instead so callers can see their
                # multimodal content never reached the model (R-225).
                _logger.warning(
                    "ollama provider: message role=%r has non-text content (%d block(s)); "
                    "ollama has no multimodal content-block support, so this message is being "
                    "sent with EMPTY content -- the original content is dropped, not translated",
                    message.role,
                    len(message.content),
                )
                content = ""
            messages.append({"role": message.role, "content": content})
        return messages

    def _options(self, request: LlmRequest) -> dict:
        options: dict = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        return options

    def _build_kwargs(self, request: LlmRequest, *, stream: bool) -> dict:
        kwargs: dict = {
            "model": request.model,
            "messages": self._messages(request),
            "stream": stream,
            "options": self._options(request),
        }
        if request.tools:
            kwargs["tools"] = to_provider_tools(self.name, request.tools)
        kwargs.update(dict(request.provider_options))
        return kwargs

    def call(self, request: LlmRequest) -> LlmResponse:
        client = self._get_client()
        try:
            native = client.chat(**self._build_kwargs(request, stream=False))
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"ollama call failed: {exc}") from exc
        return self._to_response(native, request)

    def _to_response(self, native: object, request: LlmRequest) -> LlmResponse:
        message = _get(native, "message", {}) or {}
        text = _get(message, "content", "") or ""
        raw_calls: list[dict] = []
        for tool_call in _get(message, "tool_calls", None) or []:
            function = _get(tool_call, "function", {}) or {}
            raw_calls.append(
                {
                    "function": {
                        "name": _get(function, "name", ""),
                        "arguments": _get(function, "arguments", {}) or {},
                    }
                }
            )
        tool_calls = from_provider_tool_calls(self.name, raw_calls) if raw_calls else ()
        prompt = _get(native, "prompt_eval_count", 0) or 0
        completion = _get(native, "eval_count", 0) or 0
        return LlmResponse(
            text=text,
            finish_reason=_get(native, "done_reason", None),
            usage=Usage(prompt, completion, prompt + completion),
            model=_get(native, "model", request.model),
            provider=self.name,
            tool_calls=tool_calls,
            raw=native,
        )

    def call_stream(self, request: LlmRequest) -> Iterator[LlmStreamChunk]:
        client = self._get_client()
        try:
            native_stream = client.chat(**self._build_kwargs(request, stream=True))
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"ollama stream failed: {exc}") from exc
        return self._iter_stream(native_stream)

    def _iter_stream(self, native_stream: object) -> Iterator[LlmStreamChunk]:
        index = 0
        for chunk in native_stream:
            message = _get(chunk, "message", {}) or {}
            text = _get(message, "content", "") or ""
            if text:
                yield LlmStreamChunk(delta_text=text, index=index)
                index += 1
            for tool_call in _get(message, "tool_calls", None) or []:
                function = _get(tool_call, "function", {}) or {}
                arguments = _get(function, "arguments", None)
                yield LlmStreamChunk(
                    tool_call_delta=ToolCallDelta(
                        id=None,
                        name=_get(function, "name", None),
                        arguments_delta=_encode_args(arguments),
                    ),
                    index=index,
                )
                index += 1
            if _get(chunk, "done", False):
                yield LlmStreamChunk(finish_reason=_get(chunk, "done_reason", "stop") or "stop", index=index)
                index += 1


def _encode_args(arguments: Any) -> str | None:
    """Ollama emits tool-call arguments as a mapping; serialize to a JSON
    fragment so it round-trips through ``streaming.merge_tool_call_deltas``."""
    if arguments is None:
        return None
    if isinstance(arguments, str):
        return arguments
    import json

    return json.dumps(arguments)
