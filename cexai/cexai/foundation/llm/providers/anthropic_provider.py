"""Anthropic (Claude) provider adapter.

Maps the frozen ``LlmRequest`` / ``LlmResponse`` / ``LlmStreamChunk`` contracts
to the ``anthropic`` SDK. LAZY client init: the SDK is imported and the client
constructed on FIRST call, never at import or ``__init__`` -- so the module loads
with zero cloud credentials and tests inject a mock ``client=`` (Article XIV).

The CEX artifact kind for this provider remains ``model_provider`` (P02);
``AnthropicProvider`` is a CODE adapter, not a new CEX kind.

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from cexai.foundation._shared.errors import ProviderCallError, ProviderConfigError
from cexai.foundation._shared.types import (
    LlmRequest,
    LlmResponse,
    LlmStreamChunk,
    ToolCallDelta,
    Usage,
)
from cexai.foundation.llm.normalizer import from_provider_tool_calls, to_provider_tools

_ENV_KEY = "ANTHROPIC_API_KEY"
_DEFAULT_MAX_TOKENS = 1024


class AnthropicProvider:
    """``LlmProvider`` adapter over the anthropic Messages API."""

    name = "anthropic"

    def __init__(self, *, client: object | None = None, api_key: str | None = None) -> None:
        self._client = client
        self._api_key = api_key

    # -- lazy client ------------------------------------------------------- #
    def _get_client(self) -> object:
        if self._client is not None:
            return self._client
        key = self._api_key or os.environ.get(_ENV_KEY)
        if not key:
            raise ProviderConfigError(self.name, f"missing API key (set {_ENV_KEY} or pass client=)")
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ProviderConfigError(self.name, f"anthropic SDK not installed: {exc}") from exc
        self._client = anthropic.Anthropic(api_key=key)
        return self._client

    # -- request mapping --------------------------------------------------- #
    def _build_kwargs(self, request: LlmRequest) -> dict:
        system_parts: list[str] = []
        messages: list[dict] = []
        for message in request.messages:
            if message.role == "system" and isinstance(message.content, str):
                system_parts.append(message.content)
            else:
                messages.append({"role": message.role, "content": message.content})
        kwargs: dict = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or _DEFAULT_MAX_TOKENS,
        }
        if system_parts:
            kwargs["system"] = "\n".join(system_parts)
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.tools:
            kwargs["tools"] = to_provider_tools(self.name, request.tools)
        kwargs.update(dict(request.provider_options))
        return kwargs

    # -- non-streaming call ------------------------------------------------ #
    def call(self, request: LlmRequest) -> LlmResponse:
        client = self._get_client()
        try:
            native = client.messages.create(**self._build_kwargs(request))
        except ProviderConfigError:
            raise
        except Exception as exc:  # transport / API error
            raise ProviderCallError(f"anthropic call failed: {exc}") from exc
        return self._to_response(native, request)

    def _to_response(self, native: object, request: LlmRequest) -> LlmResponse:
        text_parts: list[str] = []
        raw_tool_uses: list[dict] = []
        for block in getattr(native, "content", None) or []:
            block_type = getattr(block, "type", None)
            if block_type == "text":
                text_parts.append(getattr(block, "text", "") or "")
            elif block_type == "tool_use":
                raw_tool_uses.append(
                    {
                        "type": "tool_use",
                        "id": getattr(block, "id", ""),
                        "name": getattr(block, "name", ""),
                        "input": getattr(block, "input", {}) or {},
                    }
                )
        tool_calls = from_provider_tool_calls(self.name, raw_tool_uses) if raw_tool_uses else ()
        usage_obj = getattr(native, "usage", None)
        prompt = getattr(usage_obj, "input_tokens", 0) or 0
        completion = getattr(usage_obj, "output_tokens", 0) or 0
        return LlmResponse(
            text="".join(text_parts),
            finish_reason=getattr(native, "stop_reason", None),
            usage=Usage(prompt, completion, prompt + completion),
            model=getattr(native, "model", request.model),
            provider=self.name,
            tool_calls=tool_calls,
            raw=native,
        )

    # -- streaming call ---------------------------------------------------- #
    def call_stream(self, request: LlmRequest) -> Iterator[LlmStreamChunk]:
        client = self._get_client()
        kwargs = {**self._build_kwargs(request), "stream": True}
        try:
            native_stream = client.messages.create(**kwargs)
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"anthropic stream failed: {exc}") from exc
        return self._iter_stream(native_stream)

    def _iter_stream(self, native_stream: object) -> Iterator[LlmStreamChunk]:
        index = 0
        for event in native_stream:
            event_type = getattr(event, "type", None)
            if event_type == "content_block_start":
                block = getattr(event, "content_block", None)
                if getattr(block, "type", None) == "tool_use":
                    yield LlmStreamChunk(
                        tool_call_delta=ToolCallDelta(
                            id=getattr(block, "id", None),
                            name=getattr(block, "name", None),
                            arguments_delta=None,
                        ),
                        index=index,
                    )
                    index += 1
            elif event_type == "content_block_delta":
                delta = getattr(event, "delta", None)
                delta_type = getattr(delta, "type", None)
                if delta_type == "text_delta":
                    yield LlmStreamChunk(delta_text=getattr(delta, "text", "") or "", index=index)
                    index += 1
                elif delta_type == "input_json_delta":
                    yield LlmStreamChunk(
                        tool_call_delta=ToolCallDelta(
                            id=None, name=None, arguments_delta=getattr(delta, "partial_json", "") or ""
                        ),
                        index=index,
                    )
                    index += 1
            elif event_type == "message_delta":
                stop_reason = getattr(getattr(event, "delta", None), "stop_reason", None)
                if stop_reason is not None:
                    yield LlmStreamChunk(finish_reason=stop_reason, index=index)
                    index += 1
