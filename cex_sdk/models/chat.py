# cex_sdk.models.chat -- thin synchronous LLM convenience API
# kind: model_provider / pillar: P02 / 8F: F5 CALL
# -*- coding: ascii -*-
from __future__ import annotations

import os
import sys
from typing import Any

# Resolve default model from nucleus_models.yaml (graceful fallback)
try:
    _tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_tools")
    if _tools_dir not in sys.path:
        sys.path.insert(0, os.path.normpath(_tools_dir))
    from cex_model_resolver import resolve_model_for_tool
    _CHAT_DEFAULT_MODEL = resolve_model_for_tool("chat", "standard")["model"]
except Exception:
    _CHAT_DEFAULT_MODEL = "claude-sonnet-4-6"


def chat(
    prompt: str,
    *,
    model: str = _CHAT_DEFAULT_MODEL,
    provider: str = "auto",
    max_tokens: int = 4096,
    system: str = "",
    **kwargs: Any,
) -> str:
    """
    Thin synchronous LLM call. Returns response text.
    provider: "auto" (detect from model name), "anthropic", "openai", "ollama", "openwebui"
    """
    resolved = _resolve_provider(provider, model)
    if resolved == "anthropic":
        return _call_anthropic(prompt, model=model, max_tokens=max_tokens, system=system, **kwargs)
    if resolved == "openai":
        return _call_openai(prompt, model=model, max_tokens=max_tokens, system=system, **kwargs)
    if resolved == "openwebui":
        return _call_openwebui(prompt, model=model, max_tokens=max_tokens, system=system, **kwargs)
    return _call_ollama(prompt, model=model, max_tokens=max_tokens, system=system, **kwargs)


def _resolve_provider(provider: str, model: str) -> str:
    if provider != "auto":
        return provider
    if model.startswith("claude-"):
        return "anthropic"
    if model.startswith(("gpt-", "o1-", "o3-")):
        return "openai"
    if model.startswith("glm-"):
        return "openwebui"
    return "ollama"


def _call_anthropic(
    prompt: str,
    *,
    model: str,
    max_tokens: int,
    system: str,
    **kwargs: Any,
) -> str:
    import anthropic  # type: ignore[import]

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    msgs: list[dict[str, str]] = [{"role": "user", "content": prompt}]
    create_kwargs: dict[str, Any] = dict(model=model, max_tokens=max_tokens, messages=msgs)
    if system:
        create_kwargs["system"] = system
    create_kwargs.update(kwargs)
    resp = client.messages.create(**create_kwargs)
    return resp.content[0].text


def _call_openai(
    prompt: str,
    *,
    model: str,
    max_tokens: int,
    system: str,
    **kwargs: Any,
) -> str:
    from openai import OpenAI  # type: ignore[import]

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    create_kwargs: dict[str, Any] = dict(model=model, max_tokens=max_tokens, messages=msgs)
    create_kwargs.update(kwargs)
    resp = client.chat.completions.create(**create_kwargs)
    return resp.choices[0].message.content or ""


def _call_ollama(
    prompt: str,
    *,
    model: str,
    max_tokens: int,
    system: str,
    **kwargs: Any,
) -> str:
    import requests  # type: ignore[import]

    try:  # shared R-056/R-141 resolver: canonical OLLAMA_HOST + legacy aliases
        from _tools.cex_ollama_env import resolve_ollama_host
        base_url = resolve_ollama_host()
    except Exception:  # degrade-never: inline canonical-first chain
        base_url = (os.environ.get("OLLAMA_HOST")
                    or os.environ.get("OLLAMA_URL")  # legacy alias
                    or "http://localhost:11434").rstrip("/")
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    payload: dict[str, Any] = {"model": model, "messages": msgs, "stream": False}
    resp = requests.post(f"{base_url}/api/chat", json=payload, timeout=60)
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()
    return data["message"]["content"]


def _call_openwebui(
    prompt: str,
    *,
    model: str,
    max_tokens: int,
    system: str,
    **kwargs: Any,
) -> str:
    """Open WebUI (OpenAI-compatible gateway) provider branch. Same requests-based
    shape as _call_ollama, but -- unlike ollama -- this provider has NO hardcoded
    default endpoint: OPENWEBUI_API_BASE is a required env, and an absent env raises
    an honest error instead of silently pointing at some guessed address."""
    import requests  # type: ignore[import]

    base_url = os.environ.get("OPENWEBUI_API_BASE", "").strip()
    if not base_url:
        raise RuntimeError(
            "OPENWEBUI_API_BASE is not set. This provider has no hardcoded default "
            "endpoint -- set OPENWEBUI_API_BASE to the Open WebUI OpenAI-compatible "
            "base URL (e.g. http://localhost:3000/api) before calling chat() with a "
            "glm-* model or provider='openwebui'."
        )
    api_key = os.environ.get("OPENWEBUI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENWEBUI_API_KEY is not set. This provider requires a bearer key -- "
            "set OPENWEBUI_API_KEY before calling chat() with a glm-* model or "
            "provider='openwebui'."
        )
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    payload: dict[str, Any] = {
        "model": model,
        "messages": msgs,
        "max_tokens": max_tokens,
        "stream": False,
    }
    headers = {"Authorization": "Bearer %s" % api_key}
    resp = requests.post(
        f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=60
    )
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()
    return data["choices"][0]["message"]["content"] or ""
