from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import Settings, Tariff, allowed
from db import Database, utc_day_start
from handlers.chat import ChatMode
from handlers.image import ImageMode
from handlers.subscription import tariffs_text
from keyboards import chat_keyboard, main_menu, profile_keyboard, tariffs_keyboard

router = Router(name="start")
fallback_router = Router(name="fallback")

START_TEXT = (
    "Привет! 👋 Я открываю доступ к нескольким ИИ: можно поговорить "
    "и сгенерировать картинку без VPN и иностранной карты.\n\n"
    "Бесплатно доступна базовая модель с дневным лимитом. "
    "Платные тарифы снимают ограничения и открывают топовые модели.\n\n"
    "Выберите, что сделать:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(START_TEXT, reply_markup=main_menu())


@router.message(Command("profile"))
async def cmd_profile(message: Message, db: Database, settings: Settings) -> None:
    if message.from_user is None:
        return
    await message.answer(
        await profile_text(message.from_user.id, db, settings),
        reply_markup=profile_keyboard(),
    )


@router.callback_query(F.data == "menu:home")
async def menu_home(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    if callback.message is not None:
        await callback.message.answer("Главное меню. Выберите действие:", reply_markup=main_menu())


@router.callback_query(F.data == "menu:chat")
async def menu_chat(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    settings: Settings,
) -> None:
    await callback.answer()
    if callback.from_user is None or callback.message is None:
        return
    code = await db.effective_tariff_code(callback.from_user.id)
    tariff = settings.tariffs[code]
    user = await db.get_user(callback.from_user.id)
    model = settings.resolve_model(tariff, user.selected_model if user else None)
    if model is None:
        await callback.message.answer("Текстовые модели сейчас недоступны.")
        return
    used = await db.usage_today(callback.from_user.id, "text")
    if not allowed(tariff, "text", used):
        await callback.message.answer(
            "Лимит исчерпан, вот тарифы.",
            reply_markup=tariffs_keyboard(),
        )
        return
    await state.set_state(ChatMode.active)
    await callback.message.answer(
        f"Режим чата. Модель: {model.title} ({model.model_id}).\nНапишите сообщение.",
        reply_markup=chat_keyboard(),
    )


@router.callback_query(F.data == "menu:image")
async def menu_image(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    settings: Settings,
) -> None:
    await callback.answer()
    if callback.from_user is None or callback.message is None:
        return
    if not settings.image_enabled():
        await callback.message.answer("Генерация картинок сейчас недоступна.")
        return
    code = await db.effective_tariff_code(callback.from_user.id)
    tariff = settings.tariffs[code]
    used = await db.usage_today(callback.from_user.id, "image")
    if not allowed(tariff, "image", used):
        await callback.message.answer(
            "Лимит исчерпан, вот тарифы.",
            reply_markup=tariffs_keyboard(),
        )
        return
    await state.set_state(ImageMode.active)
    await callback.message.answer(
        "Режим картинки. Опишите, что нарисовать, одним сообщением.\n"
        "Картинка тратит отдельный лимит, он меньше текстового."
    )


@router.callback_query(F.data == "menu:tariffs")
async def menu_tariffs(callback: CallbackQuery, settings: Settings) -> None:
    await callback.answer()
    if callback.message is not None:
        await callback.message.answer(tariffs_text(settings), reply_markup=tariffs_keyboard())


@router.callback_query(F.data == "menu:profile")
async def menu_profile(callback: CallbackQuery, db: Database, settings: Settings) -> None:
    await callback.answer()
    if callback.from_user is None or callback.message is None:
        return
    await callback.message.answer(
        await profile_text(callback.from_user.id, db, settings),
        reply_markup=profile_keyboard(),
    )


@fallback_router.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def fallback(message: Message) -> None:
    await message.answer("Выберите действие в меню.", reply_markup=main_menu())


async def profile_text(user_id: int, db: Database, settings: Settings) -> str:
    code = await db.effective_tariff_code(user_id)
    tariff = settings.tariffs[code]
    since = utc_day_start()
    text_used = await db.count_usage(user_id, "text", since)
    image_used = await db.count_usage(user_id, "image", since)
    user = await db.get_user(user_id)
    model = settings.resolve_model(tariff, user.selected_model if user else None)
    if model is None:
        model_line = "нет доступных"
    else:
        model_line = f"{model.title} ({model.model_id})"
    if code == "free":
        until = "—"
    else:
        end = await db.subscription_end(user_id, code)
        until = _format_dt(end) if end else "—"
    return (
        "Ваш профиль\n\n"
        f"Тариф: {tariff.title}\n"
        f"{_quota('Текст', tariff, 'text', text_used)}\n"
        f"{_quota('Картинки', tariff, 'image', image_used)}\n"
        f"Подписка до: {until}\n"
        f"Модель: {model_line}"
    )


def _quota(label: str, tariff: Tariff, kind: str, used: int) -> str:
    limit = tariff.limit_for(kind)
    if limit is None:
        return f"{label}: без лимита (сегодня {used})"
    if limit == 0:
        return f"{label}: недоступно"
    left = max(0, limit - used)
    return f"{label}: осталось {left} из {limit}"


def _format_dt(value: str) -> str:
    moment = datetime.fromisoformat(value)
    return moment.strftime("%d.%m.%Y %H:%M UTC")
