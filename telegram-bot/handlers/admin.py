from __future__ import annotations

import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import Settings
from db import Database, utc_day_start
from keyboards import admin_cancel_keyboard, admin_keyboard

logger = logging.getLogger(__name__)

router = Router(name="admin")


class AdminGrant(StatesGroup):
    waiting_user_id = State()


def _is_admin(user_id: int, settings: Settings) -> bool:
    return settings.admin_id != 0 and user_id == settings.admin_id


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, db: Database, settings: Settings) -> None:
    if message.from_user is None:
        return
    if not _is_admin(message.from_user.id, settings):
        await message.answer("Недостаточно прав.")
        return
    await state.clear()
    await message.answer(await _admin_text(db), reply_markup=admin_keyboard())


@router.callback_query(F.data.startswith("admin:grant:"))
async def start_grant(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
) -> None:
    if callback.from_user is None or callback.data is None:
        await callback.answer()
        return
    if not _is_admin(callback.from_user.id, settings):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    code = callback.data.split(":")[2]
    if code not in ("pro", "unlimited"):
        await callback.answer("Неизвестный тариф", show_alert=True)
        return
    await state.set_state(AdminGrant.waiting_user_id)
    await state.update_data(tariff=code)
    await callback.answer()
    if callback.message is not None:
        title = settings.tariffs[code].title
        await callback.message.answer(
            f"Выдать тариф {title} на 30 дней.\nПришлите числовой user id.",
            reply_markup=admin_cancel_keyboard(),
        )


@router.callback_query(F.data == "admin:cancel")
async def cancel_grant(callback: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if callback.from_user is None:
        await callback.answer()
        return
    if not _is_admin(callback.from_user.id, settings):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    await state.clear()
    await callback.answer("Отменено")
    if callback.message is not None:
        await callback.message.answer("Выдача отменена. Снова открыть панель: /admin")


@router.message(AdminGrant.waiting_user_id, F.text)
async def grant_by_id(
    message: Message,
    state: FSMContext,
    db: Database,
    settings: Settings,
) -> None:
    if message.from_user is None or message.text is None:
        return
    if not _is_admin(message.from_user.id, settings):
        await state.clear()
        await message.answer("Недостаточно прав.")
        return
    raw = message.text.strip()
    if not raw.isdigit():
        await message.answer(
            "Нужен числовой user id, без @username.",
            reply_markup=admin_cancel_keyboard(),
        )
        return
    user_id = int(raw)
    if user_id <= 0:
        await message.answer("Некорректный user id.", reply_markup=admin_cancel_keyboard())
        return
    data = await state.get_data()
    code = data.get("tariff")
    if code not in settings.tariffs or code == "free":
        await state.clear()
        await message.answer("Тариф не выбран. Откройте /admin ещё раз.")
        return
    subscription = await db.grant_subscription(
        user_id,
        code,
        days=settings.subscription_days,
        stars_paid=0,
        charge_id=None,
    )
    await state.clear()
    until = datetime.fromisoformat(subscription.ends_at).strftime("%d.%m.%Y %H:%M UTC")
    title = settings.tariffs[code].title
    logger.info("admin grant admin=%s user=%s tariff=%s", message.from_user.id, user_id, code)
    await message.answer(
        f"Готово. Пользователю {user_id} выдан тариф {title} до {until}."
    )


async def _admin_text(db: Database) -> str:
    users = await db.count_users()
    today = await db.count_requests_since(utc_day_start())
    return (
        "Админ-панель\n\n"
        f"Пользователей: {users}\n"
        f"Запросов сегодня: {today}\n\n"
        "Выдать подписку на 30 дней:"
    )
