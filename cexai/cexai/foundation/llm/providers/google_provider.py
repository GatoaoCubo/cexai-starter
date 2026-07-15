"""Google (Gemini) provider adapter.

Maps the frozen contracts to ``google-generativeai``. LAZY client init: the SDK
is imported and configured on first call. Tests inject a mock ``client=`` that
exposes ``generate_content(...)`` so no real key is required (Article XIV).

v0.1 simplification (FLAGGED): the real SDK builds a per-model
``genai.GenerativeModel(model)``; an injected client is used directly when it
already exposes ``generate_content``. This dual path keeps the adapter thin
(Article VIII) while remaining mockable. CEX kind remains ``model_provider``.

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

import json
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

_ENV_KEYS = ("GOOGLE_API_KEY", "GEMINI_API_KEY")


class GoogleProvider:
    """``LlmProvider`` adapter over the google-generativeai SDK."""

    name = "google"

    def __init__(self, *, client: object | None = None, api_key: str | None = None) -> None:
        self._client = client
        self._api_key = api_key

    def _get_client(self) -> object:
        if self._client is not None:
            return self._client
        key = self._api_key or next((os.environ[k] for k in _ENV_KEYS if os.environ.get(k)), None)
        if not key:
            raise ProviderConfigError(self.name, "missing API key (set GOOGLE_API_KEY or pass client=)")
        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ProviderConfigError(self.name, f"google-generativeai SDK not installed: {exc}") from exc
        genai.configure(api_key=key)
        self._client = genai
        return self._client

    def _build_contents(self, request: LlmRequest) -> list[dict]:
        # Gemini uses role "model" for assistant turns; system text is folded in.
        contents: list[dict] = []
        for message in request.messages:
            role = "model" if message.role == "assistant" else "user"
            text = message.content if isinstance(message.content, str) else ""
            contents.append({"role": role, "parts": [{"text": text}]})
        return contents

    def _gen_config(self, request: LlmRequest) -> dict:
        config: dict = {}
        if request.temperature is not None:
            config["temperature"] = request.temperature
        if request.max_tokens is not None:
            config["max_output_tokens"] = request.max_tokens
        return config

    def _tools(self, request: LlmRequest):
        if not request.tools:
            return None
        return [{"function_declarations": to_provider_tools(self.name, request.tools)}]

    def call(self, request: LlmRequest) -> LlmResponse:
        client = self._get_client()
        try:
            native = self._generate(client, request)
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"google call failed: {exc}") from exc
        return self._to_response(native, request)

    def _generate(self, client: object, request: LlmRequest, *, stream: bool = False) -> object:
        kwargs = {
            "contents": self._build_contents(request),
            "generation_config": self._gen_config(request),
            "tools": self._tools(request),
        }
        direct = getattr(client, "generate_content", None)
        if direct is not None:  # injected mock or model-like object
            return direct(stream=stream, **kwargs)
        model_obj = client.GenerativeModel(request.model)  # real SDK path
        return model_obj.generate_content(stream=stream, **kwargs)

    def _to_response(self, native: object, request: LlmRequest) -> LlmResponse:
        text_parts: list[str] = []
        raw_calls: list[dict] = []
        candidates = getattr(native, "candidates", None) or []
        if candidates:
            content = getattr(candidates[0], "content", None)
            for part in getattr(content, "parts", None) or []:
                part_text = getattr(part, "text", None)
                if part_text:
                    text_parts.append(part_text)
                function_call = getattr(part, "function_call", None)
                if function_call is not None:
                    raw_calls.append(
                        {
                            "name": getattr(function_call, "name", ""),
                            "args": dict(getattr(function_call, "args", {}) or {}),
                        }
                    )
        text = "".join(text_parts) or (getattr(native, "text", "") or "")
        tool_calls = from_provider_tool_calls(self.name, raw_calls) if raw_calls else ()
        usage_obj = getattr(native, "usage_metadata", None)
        prompt = getattr(usage_obj, "prompt_token_count", 0) or 0
        completion = getattr(usage_obj, "candidates_token_count", 0) or 0
        total = getattr(usage_obj, "total_token_count", 0) or (prompt + completion)
        finish_reason = None
        if candidates:
            raw_finish = getattr(candidates[0], "finish_reason", None)
            finish_reason = str(raw_finish) if raw_finish is not None else None
        return LlmResponse(
            text=text,
            finish_reason=finish_reason,
            usage=Usage(prompt, completion, total),
            model=request.model,
            provider=self.name,
            tool_calls=tool_calls,
            raw=native,
        )

    def call_stream(self, request: LlmRequest) -> Iterator[LlmStreamChunk]:
        client = self._get_client()
        try:
            native_stream = self._generate(client, request, stream=True)
        except ProviderConfigError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"google stream failed: {exc}") from exc
        return self._iter_stream(native_stream)

    def _iter_stream(self, native_stream: object) -> Iterator[LlmStreamChunk]:
        # Mirrors _to_response's part-walk: each streamed chunk carries the same
        # candidates[0].content.parts shape as the non-stream response, so a
        # part's function_call must be extracted here too (R-224) -- text alone
        # silently dropped every streamed Gemini tool-call.
        index = 0
        for chunk in native_stream:
            text = getattr(chunk, "text", None)
            if text:
                yield LlmStreamChunk(delta_text=text, index=index)
                index += 1
            candidates = getattr(chunk, "candidates", None) or []
            content = getattr(candidates[0], "content", None) if candidates else None
            for part in getattr(content, "parts", None) or []:
                function_call = getattr(part, "function_call", None)
                if function_call is None:
                    continue
                args = dict(getattr(function_call, "args", {}) or {})
                yield LlmStreamChunk(
                    tool_call_delta=ToolCallDelta(
                        id=None,
                        name=getattr(function_call, "name", None),
                        arguments_delta=json.dumps(args),
                    ),
                    index=index,
                )
                index += 1
