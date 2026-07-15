"""OpenAI provider adapter.

Maps the frozen contracts to the ``openai`` SDK Chat Completions API. LAZY
client init (SDK imported + client built on first call). Tests inject a mock
``client=`` so no real key is required (Article XIV).

CEX kind remains ``model_provider`` (P02); this is a CODE adapter.

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

_ENV_KEY = "OPENAI_API_KEY"


class OpenAIProvider:
    """``LlmProvider`` adapter over the OpenAI Chat Completions API."""

    name = "openai"

    def __init__(self, *, client: object | None = None, api_key: str | None = None) -> None:
        self._client = client
        self._api_key = api_key

    def _get_client(self) -> object:
        if self._client is not None:
            return self._client
        key = self._api_key or os.environ.get(_ENV_KEY)
        if not key:
            raise ProviderConfigError(self.name, f"missing API key (set {_ENV_KEY} or pass client=)")
        try:
            import openai
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ProviderConfigError(self.name, f"openai SDK not installed: {exc}") from exc
        self._client = openai.OpenAI(api_key=key)
        return self._client

    def _build_kwargs(self, request: LlmRequest) -> dict:
        messages = [{"role": message.role, "content": message.content} for message in request.messages]
        kwargs: dict = {"model": request.model, "messages": messages}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.tools:
            kwargs["tools"] = to_provider_tools(self.name, request.tools)
        kwargs.update(dict(request.provider_options))
        return kwargs

    def call(self, request: LlmRequest) -> LlmResponse:
        client = self._get_client()
        try:
            native = client.chat.completions.create(**self._build_kwargs(request))
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"openai call failed: {exc}") from exc
        return self._to_response(native, request)

    def _to_response(self, native: object, request: LlmRequest) -> LlmResponse:
        choices = getattr(native, "choices", None) or []
        choice = choices[0] if choices else None
        message = getattr(choice, "message", None)
        text = getattr(message, "content", None) or ""
        raw_calls: list[dict] = []
        for tool_call in getattr(message, "tool_calls", None) or []:
            function = getattr(tool_call, "function", None)
            raw_calls.append(
                {
                    "id": getattr(tool_call, "id", ""),
                    "type": "function",
                    "function": {
                        "name": getattr(function, "name", ""),
                        "arguments": getattr(function, "arguments", "") or "",
                    },
                }
            )
        tool_calls = from_provider_tool_calls(self.name, raw_calls) if raw_calls else ()
        usage_obj = getattr(native, "usage", None)
        prompt = getattr(usage_obj, "prompt_tokens", 0) or 0
        completion = getattr(usage_obj, "completion_tokens", 0) or 0
        total = getattr(usage_obj, "total_tokens", 0) or (prompt + completion)
        return LlmResponse(
            text=text,
            finish_reason=getattr(choice, "finish_reason", None),
            usage=Usage(prompt, completion, total),
            model=getattr(native, "model", request.model),
            provider=self.name,
            tool_calls=tool_calls,
            raw=native,
        )

    def call_stream(self, request: LlmRequest) -> Iterator[LlmStreamChunk]:
        client = self._get_client()
        kwargs = {**self._build_kwargs(request), "stream": True}
        try:
            native_stream = client.chat.completions.create(**kwargs)
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"openai stream failed: {exc}") from exc
        return self._iter_stream(native_stream)

    def _iter_stream(self, native_stream: object) -> Iterator[LlmStreamChunk]:
        index = 0
        for chunk in native_stream:
            choices = getattr(chunk, "choices", None) or []
            if not choices:
                continue
            choice = choices[0]
            delta = getattr(choice, "delta", None)
            text = getattr(delta, "content", None)
            if text:
                yield LlmStreamChunk(delta_text=text, index=index)
                index += 1
            for tool_delta in getattr(delta, "tool_calls", None) or []:
                function = getattr(tool_delta, "function", None)
                yield LlmStreamChunk(
                    tool_call_delta=ToolCallDelta(
                        id=getattr(tool_delta, "id", None),
                        name=getattr(function, "name", None),
                        arguments_delta=getattr(function, "arguments", None),
                    ),
                    index=index,
                )
                index += 1
            finish_reason = getattr(choice, "finish_reason", None)
            if finish_reason is not None:
                yield LlmStreamChunk(finish_reason=finish_reason, index=index)
                index += 1
