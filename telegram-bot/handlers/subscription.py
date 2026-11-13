from __future__ import annotations

import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from config import Settings
from db import Database
from keyboards import main_menu

logger = logging.getLogger(__name__)

router = Router(name="subscription")

_TITLES = {
    "pro": "Тариф Pro",
    "unlimited": "Тариф Безлимит",
}


def tariffs_text(settings: Settings) -> str:
    free = settings.tariffs["free"]
    pro = settings.tariffs["pro"]
    unlimited = settings.tariffs["unlimited"]
    return (
        "Тарифы\n\n"
        f"Бесплатный: {free.text_limit} текстов в день, только базовая модель. "
        "Картинки недоступны.\n"
        f"Pro — {pro.price_stars} Stars / 30 дней: {pro.text_limit} текстов, "
        f"{pro.image_limit} картинок, топовая модель.\n"
        f"Безлимит — {unlimited.price_stars} Stars / 30 дней: текст без лимита, "
        f"{unlimited.image_limit} картинок, все модели.\n\n"
        "Картинка списывает свой лимит, он заметно меньше текстового. "
        "Оплата через Telegram Stars."
    )


@router.callback_query(F.data.startswith("pay:"))
async def pay(callback: CallbackQuery, settings: Settings) -> None:
    await callback.answer()
    if callback.data is None or callback.message is None or callback.from_user is None:
        return
    code = callback.data.split(":", 1)[1]
    tariff = settings.tariffs.get(code)
    if tariff is None or tariff.price_stars <= 0:
        await callback.message.answer("Этот тариф нельзя оплатить.")
        return
    description = _invoice_description(code, settings)
    await callback.message.answer_invoice(
        title=_TITLES.get(code, tariff.title),
        description=description,
        payload=f"tariff:{code}",
        currency="XTR",
        prices=[LabeledPrice(label=tariff.title, amount=tariff.price_stars)],
        provider_token="",
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(
    message: Message,
    state: FSMContext,
    db: Database,
    settings: Settings,
) -> None:
    payment = message.successful_payment
    if payment is None or message.from_user is None:
        return
    payload = payment.invoice_payload or ""
    code = payload.removeprefix("tariff:")
    tariff = settings.tariffs.get(code)
    if tariff is None or code not in ("pro", "unlimited") or not payload.startswith("tariff:"):
        logger.error("unknown payment payload user=%s payload=%s", message.from_user.id, payload)
        await message.answer(
            "Платёж получен, но тариф не распознан. Напишите администратору.",
            reply_markup=main_menu(),
        )
        return
    if payment.currency != "XTR":
        logger.error(
            "payment currency mismatch user=%s currency=%s",
            message.from_user.id,
            payment.currency,
        )
        await message.answer(
            "Платёж пришёл в неожиданной валюте. Напишите администратору.",
            reply_markup=main_menu(),
        )
        return
    if payment.total_amount != tariff.price_stars:
        logger.warning(
            "payment amount differs user=%s amount=%s expected=%s",
            message.from_user.id,
            payment.total_amount,
            tariff.price_stars,
        )
    subscription = await db.grant_subscription(
        message.from_user.id,
        code,
        days=settings.subscription_days,
        stars_paid=payment.total_amount,
        charge_id=payment.telegram_payment_charge_id,
    )
    await state.clear()
    until = datetime.fromisoformat(subscription.ends_at).strftime("%d.%m.%Y %H:%M UTC")
    logger.info("payment stored user=%s tariff=%s", message.from_user.id, code)
    await message.answer(
        f"Оплата прошла. Тариф {tariff.title} активен до {until}.",
        reply_markup=main_menu(),
    )


def _invoice_description(code: str, settings: Settings) -> str:
    tariff = settings.tariffs[code]
    if code == "unlimited":
        return (
            f"Текст без лимита, {tariff.image_limit} картинок в день, все модели. "
            "Доступ на 30 дней."
        )
    return (
        f"{tariff.text_limit} текстов и {tariff.image_limit} картинок в день, "
        "топовая модель. Доступ на 30 дней."
    )
