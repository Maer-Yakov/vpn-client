from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.enums import ChatType


class PrivateChatMiddleware(BaseMiddleware):
    """Drop group, supergroup, and channel updates. The bot is private-chat only."""

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        chat = getattr(event, "chat", None)
        if chat is None:
            message = getattr(event, "message", None)
            chat = getattr(message, "chat", None)
        if chat is not None and chat.type != ChatType.PRIVATE:
            return None
        return await handler(event, data)
