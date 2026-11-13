from __future__ import annotations

import logging
import os

from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from config import Settings, allowed
from db import Database
from keyboards import tariffs_keyboard
from middlewares.limits import LimitMiddleware
from middlewares.rate_limit import RateLimitMiddleware
from providers import ProviderError
from providers.image import generate as image_generate
from providers.image import is_image_url, is_managed_file

logger = logging.getLogger(__name__)

router = Router(name="image")


class ImageMode(StatesGroup):
    active = State()


@router.message(ImageMode.active, F.text, ~F.text.startswith("/"))
async def on_image_prompt(message: Message, db: Database, settings: Settings) -> None:
    if message.from_user is None or not message.text:
        return
    prompt = message.text.strip()
    if not prompt:
        await message.answer("Напишите, что нарисовать.")
        return
    if len(prompt) > settings.max_prompt_length:
        await message.answer(
            f"Слишком длинный запрос. Максимум {settings.max_prompt_length} символов."
        )
        return
    code = await db.effective_tariff_code(message.from_user.id)
    tariff = settings.tariffs[code]
    if not allowed(tariff, "image", await db.usage_today(message.from_user.id, "image")):
        await message.answer("Лимит исчерпан, вот тарифы.", reply_markup=tariffs_keyboard())
        return
    if not settings.image_enabled():
        await message.answer("Генерация картинок сейчас недоступна.")
        return
    thinking = await message.answer("Думаю…")
    local_path: str | None = None
    try:
        result = await image_generate(prompt, settings.image_model)
        try:
            await thinking.delete()
        except Exception:
            logger.info("thinking message was already gone")
        if is_image_url(result):
            await message.answer_photo(result)
        elif is_managed_file(result):
            local_path = result
            await message.answer_photo(FSInputFile(local_path))
        else:
            raise ProviderError("unexpected image result")
    except ProviderError:
        logger.warning("image provider failed user=%s", message.from_user.id)
        await _edit_or_answer(thinking, message, "Ошибка провайдера, попробуйте позже.")
        await db.log_request(
            message.from_user.id,
            settings.image_model,
            "image",
            charged=False,
        )
        return
    except Exception:
        logger.exception("failed to send image")
        await _edit_or_answer(thinking, message, "Не удалось отправить картинку. Попробуйте позже.")
        await db.log_request(
            message.from_user.id,
            settings.image_model,
            "image",
            charged=False,
        )
        return
    finally:
        if local_path and is_managed_file(local_path):
            try:
                os.remove(local_path)
            except OSError:
                logger.warning("temp image was not removed: %s", local_path)
    await db.log_request(message.from_user.id, settings.image_model, "image", charged=True)
    await message.answer("Готово. Можно описать следующую картинку.")


async def _edit_or_answer(thinking: Message, source: Message, text: str) -> None:
    try:
        await thinking.edit_text(text)
    except Exception:
        await source.answer(text)


@router.message(ImageMode.active)
async def image_needs_text(message: Message) -> None:
    await message.answer("Нужно текстовое описание картинки.")


router.message.middleware(RateLimitMiddleware(ImageMode.active.state))
router.message.middleware(LimitMiddleware("image", ImageMode.active.state))
