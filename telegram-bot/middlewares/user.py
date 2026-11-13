from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware

from db import Database


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        db: Database | None = data.get("db")
        if user is not None and not user.is_bot and db is not None:
            await db.upsert_user(user.id, user.username, user.first_name)
        return await handler(event, data)
