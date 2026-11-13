from __future__ import annotations

import logging

from openai import AsyncOpenAI

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
    """Return the full assistant reply. ``history`` is older chat turns, oldest first."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise ProviderError("OPENAI_API_KEY is empty")
    kwargs: dict[str, str] = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    messages: list[dict[str, str]] = [{"role": "system", "content": _SYSTEM}]
    for item in (history or [])[-10:]:
        role = item.get("role", "")
        content = item.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": prompt})
    client = AsyncOpenAI(**kwargs, timeout=60.0)
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1200,
        )
    except Exception as exc:
        logger.exception("OpenAI request failed")
        raise ProviderError("openai") from exc
    finally:
        try:
            await client.close()
        except Exception:
            logger.debug("openai client close failed", exc_info=True)
    choice = response.choices[0].message.content if response.choices else None
    if not choice or not choice.strip():
        raise ProviderError("empty openai reply")
    return choice.strip()
