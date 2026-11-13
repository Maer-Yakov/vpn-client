from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import Settings, allowed
from db import Database
from keyboards import tariffs_keyboard


class LimitMiddleware(BaseMiddleware):
    """Stop a prompt before the provider call when the daily quota is spent.

    A provider failure is logged later with ``charged=0``, so this check only
    looks at requests that were actually delivered.
    """

    def __init__(self, kind: str, state_name: str) -> None:
        self.kind = kind
        self.state_name = state_name

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        state: FSMContext | None = data.get("state")
        if state is None or await state.get_state() != self.state_name:
            return await handler(event, data)
        text = event.text or ""
        if not text or text.startswith("/"):
            return await handler(event, data)
        settings: Settings = data["settings"]
        db: Database = data["db"]
        if len(text) > settings.max_prompt_length:
            await event.answer(
                f"Слишком длинный запрос. Максимум {settings.max_prompt_length} символов."
            )
            return None
        user = event.from_user
        if user is None:
            return await handler(event, data)
        code = await db.effective_tariff_code(user.id)
        tariff = settings.tariffs[code]
        if self.kind == "text" and not settings.text_models(tariff):
            await event.answer("Текстовые модели сейчас недоступны.")
            return None
        if self.kind == "image" and not settings.image_enabled():
            await event.answer("Генерация картинок сейчас недоступна.")
            return None
        used = await db.usage_today(user.id, self.kind)
        if not allowed(tariff, self.kind, used):
            await event.answer(
                "Лимит исчерпан, вот тарифы.",
                reply_markup=tariffs_keyboard(),
            )
            return None
        return await handler(event, data)
