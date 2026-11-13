from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ModelChoice


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Чат с ИИ", callback_data="menu:chat")
    builder.button(text="Сгенерировать картинку", callback_data="menu:image")
    builder.button(text="Тарифы", callback_data="menu:tariffs")
    builder.button(text="Мой профиль", callback_data="menu:profile")
    builder.adjust(1)
    return builder.as_markup()


def tariffs_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Оплатить Pro", callback_data="pay:pro")
    builder.button(text="Оплатить Безлимит", callback_data="pay:unlimited")
    builder.button(text="В меню", callback_data="menu:home")
    builder.adjust(1)
    return builder.as_markup()


def chat_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Сменить модель", callback_data="model:list")
    builder.button(text="В меню", callback_data="menu:home")
    builder.adjust(1)
    return builder.as_markup()


def models_keyboard(models: list[ModelChoice], current_key: str | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for model in models:
        mark = "✓ " if model.key == current_key else ""
        label = f"{mark}{model.title} ({model.model_id})"
        if len(label) > 60:
            label = label[:57] + "..."
        builder.button(text=label, callback_data=f"model:set:{model.key}")
    builder.button(text="В меню", callback_data="menu:home")
    builder.adjust(1)
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Тарифы", callback_data="menu:tariffs")
    builder.button(text="В меню", callback_data="menu:home")
    builder.adjust(2)
    return builder.as_markup()


def admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Выдать Pro", callback_data="admin:grant:pro")
    builder.button(text="Выдать Безлимит", callback_data="admin:grant:unlimited")
    builder.adjust(1)
    return builder.as_markup()


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отмена", callback_data="admin:cancel")
    return builder.as_markup()
