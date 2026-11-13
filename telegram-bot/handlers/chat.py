from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import Settings, allowed
from db import Database
from keyboards import chat_keyboard, models_keyboard, tariffs_keyboard
from middlewares.limits import LimitMiddleware
from middlewares.rate_limit import RateLimitMiddleware
from providers import ProviderError
from providers.anthropic import generate as anthropic_generate
from providers.openai import generate as openai_generate

logger = logging.getLogger(__name__)

router = Router(name="chat")


class ChatMode(StatesGroup):
    active = State()


@router.callback_query(F.data == "model:list")
async def list_models(
    callback: CallbackQuery,
    db: Database,
    settings: Settings,
) -> None:
    await callback.answer()
    if callback.from_user is None or callback.message is None:
        return
    code = await db.effective_tariff_code(callback.from_user.id)
    tariff = settings.tariffs[code]
    user = await db.get_user(callback.from_user.id)
    models = settings.text_models(tariff)
    if not models:
        await callback.message.answer("Сейчас нет доступных моделей.")
        return
    current = settings.resolve_model(tariff, user.selected_model if user else None)
    await callback.message.answer(
        "Выберите модель. Доступны только модели вашего тарифа.",
        reply_markup=models_keyboard(models, current.key if current else None),
    )


@router.callback_query(F.data.startswith("model:set:"))
async def set_model(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    settings: Settings,
) -> None:
    if callback.from_user is None or callback.data is None or callback.message is None:
        await callback.answer()
        return
    key = callback.data.split(":", 2)[2]
    code = await db.effective_tariff_code(callback.from_user.id)
    tariff = settings.tariffs[code]
    models = settings.text_models(tariff)
    choice = next((model for model in models if model.key == key), None)
    if choice is None:
        await callback.answer("Эта модель недоступна на вашем тарифе", show_alert=True)
        return
    await db.set_selected_model(callback.from_user.id, choice.key)
    await state.set_state(ChatMode.active)
    await callback.answer("Модель сохранена")
    await callback.message.answer(
        f"Модель: {choice.title} ({choice.model_id}). Напишите сообщение.",
        reply_markup=chat_keyboard(),
    )


@router.message(ChatMode.active, F.text, ~F.text.startswith("/"))
async def on_chat_message(message: Message, db: Database, settings: Settings) -> None:
    if message.from_user is None or not message.text:
        return
    prompt = message.text.strip()
    if not prompt:
        await message.answer("Напишите текст сообщения.")
        return
    if len(prompt) > settings.max_prompt_length:
        await message.answer(
            f"Слишком длинный запрос. Максимум {settings.max_prompt_length} символов."
        )
        return
    user = await db.get_user(message.from_user.id)
    code = await db.effective_tariff_code(message.from_user.id)
    tariff = settings.tariffs[code]
    if not allowed(tariff, "text", await db.usage_today(message.from_user.id, "text")):
        await message.answer("Лимит исчерпан, вот тарифы.", reply_markup=tariffs_keyboard())
        return
    model = settings.resolve_model(tariff, user.selected_model if user else None)
    if model is None:
        await message.answer("Текстовые модели сейчас недоступны.")
        return
    thinking = await message.answer("Думаю…")
    history = await db.recent_messages(message.from_user.id, settings.context_limit)
    try:
        if model.provider == "anthropic":
            reply = await anthropic_generate(prompt, model.model_id, history=history)
        else:
            reply = await openai_generate(prompt, model.model_id, history=history)
    except ProviderError:
        logger.warning("text provider failed user=%s model=%s", message.from_user.id, model.model_id)
        await db.log_request(message.from_user.id, model.model_id, "text", charged=False)
        await thinking.edit_text("Ошибка провайдера, попробуйте позже.")
        return
    try:
        await _send_reply(thinking, message, reply)
    except Exception:
        logger.exception("failed to deliver text reply")
        await db.log_request(message.from_user.id, model.model_id, "text", charged=False)
        await message.answer("Ошибка провайдера, попробуйте позже.")
        return
    await db.add_message(message.from_user.id, "user", prompt, keep=settings.context_limit)
    await db.add_message(message.from_user.id, "assistant", reply, keep=settings.context_limit)
    await db.log_request(message.from_user.id, model.model_id, "text", charged=True)


@router.message(ChatMode.active)
async def chat_needs_text(message: Message) -> None:
    await message.answer("Нужен текст сообщения.")


async def _send_reply(thinking: Message, source: Message, reply: str) -> None:
    parts = _split_text(reply)
    markup = chat_keyboard()
    try:
        await thinking.edit_text(parts[0], reply_markup=markup if len(parts) == 1 else None)
    except Exception:
        logger.exception("failed to edit thinking message")
        await source.answer(parts[0], reply_markup=markup if len(parts) == 1 else None)
    for part in parts[1:-1]:
        await source.answer(part)
    if len(parts) > 1:
        await source.answer(parts[-1], reply_markup=markup)


def _split_text(text: str, size: int = 4000) -> list[str]:
    remaining = text.strip()
    if len(remaining) <= size:
        return [remaining]
    parts: list[str] = []
    while remaining:
        if len(remaining) <= size:
            parts.append(remaining)
            break
        cut = remaining.rfind("\n", 0, size)
        if cut < size // 2:
            cut = size
        parts.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip("\n")
    return parts


router.message.middleware(RateLimitMiddleware(ChatMode.active.state))
router.message.middleware(LimitMiddleware("text", ChatMode.active.state))
