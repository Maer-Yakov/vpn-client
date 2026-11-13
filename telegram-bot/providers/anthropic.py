from __future__ import annotations

import logging

import httpx

from config import get_settings
from providers import ProviderError

logger = logging.getLogger(__name__)

_SYSTEM = (
    "Ты полезный ассистент. Отвечай на языке пользователя, обычно по-русски. "
    "Пиши ясно и по делу."
)


async def generate(
    prompt: str,
    model: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """Return the full assistant reply. ``history`` is optional and may be omitted."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise ProviderError("ANTHROPIC_API_KEY is empty")
    payload = {
        "model": model,
        "max_tokens": 1200,
        "system": _SYSTEM,
        "messages": _messages(history, prompt),
    }
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
    except Exception as exc:
        logger.exception("Anthropic request failed")
        raise ProviderError("anthropic") from exc
    parts = body.get("content") or []
    text = "".join(
        part.get("text", "")
        for part in parts
        if isinstance(part, dict) and part.get("type") == "text"
    ).strip()
    if not text:
        raise ProviderError("empty anthropic reply")
    return text


def _messages(history: list[dict[str, str]] | None, prompt: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for item in (history or [])[-10:]:
        role = item.get("role", "")
        content = (item.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        if items and items[-1]["role"] == role:
            items[-1]["content"] += "\n" + content
        else:
            items.append({"role": role, "content": content})
    if items and items[-1]["role"] == "user":
        items[-1]["content"] += "\n" + prompt
    else:
        items.append({"role": "user", "content": prompt})
    if items and items[0]["role"] != "user":
        items = items[1:]
    return items or [{"role": "user", "content": prompt}]
