from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import Settings


class RateLimitMiddleware(BaseMiddleware):
    """At most one generation prompt per user per few seconds.

    The clock is shared by every instance, so chat and image prompts share one limit.
    Navigation buttons and commands are not counted.
    """

    _last: dict[int, float] = {}

    def __init__(self, state_name: str) -> None:
        self.state_name = state_name

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not _is_prompt(event):
            return await handler(event, data)
        state: FSMContext | None = data.get("state")
        if state is None or await state.get_state() != self.state_name:
            return await handler(event, data)
        user = event.from_user
        if user is None:
            return await handler(event, data)
        settings: Settings = data["settings"]
        now = time.monotonic()
        previous = self._last.get(user.id)
        if previous is not None and now - previous < settings.rate_limit_seconds:
            await event.answer("Слишком часто. Подождите несколько секунд.")
            return None
        self._last[user.id] = now
        return await handler(event, data)


def _is_prompt(message: Message) -> bool:
    text = message.text or ""
    return bool(text) and not text.startswith("/")
