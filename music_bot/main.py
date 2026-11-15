"""Telegram-бот: ищет публичное аудио и присылает MP3."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import sys
import tempfile
import uuid
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from downloader import (
    DownloadError,
    download_audio,
    resolve_audio_urls,
    search_youtube,
)

logger = logging.getLogger("music_bot")

# Лимит Telegram Bot API для обычного бота.
TELEGRAM_AUDIO_LIMIT = 50 * 1024 * 1024
_URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)
_SEARCHES: OrderedDict[str, list[dict]] = OrderedDict()
_SEARCH_LIMIT = 200
_LOCKS: dict[int, asyncio.Lock] = {}

START_TEXT = (
    "Привет! Я помогу найти песню и прислать её в MP3.\n\n"
    "Отправьте название — покажу до 5 вариантов.\n"
    "Или пришлите публичную ссылку на YouTube, SoundCloud или другой открытый источник — "
    "сразу скачаю аудио.\n\n"
    "Из плейлиста беру только первые 5 треков.\n"
    "Платный и закрытый контент не скачиваю.\n\n"
    "Команда /help — подробнее о возможностях."
)

HELP_TEXT = (
    "Что я умею:\n\n"
    "• искать трек по названию и показывать до 5 вариантов кнопками;\n"
    "• скачивать аудио по публичной ссылке;\n"
    "• присылать MP3 с названием и исполнителем;\n"
    "• из плейлиста или альбома брать только первые 5 треков.\n\n"
    "Ограничения:\n\n"
    "• только публичные источники;\n"
    "• без обхода DRM и без платного или закрытого контента;\n"
    "• файл больше 50 МБ не отправляю — выберите другой вариант.\n\n"
    "Напишите название песни или пришлите ссылку."
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # httpx пишет полный URL запроса, а в нём есть токен бота.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def build_application(token: str) -> Application:
    application = (
        Application.builder()
        .token(token)
        .connect_timeout(30)
        .read_timeout(60)
        .write_timeout(60)
        .concurrent_updates(True)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(on_pick, pattern=r"^pick:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    return application


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message is None:
        return
    await update.message.reply_text(START_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message is None:
        return
    await update.message.reply_text(HELP_TEXT)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if message is None or not message.text:
        return
    text = message.text.strip()
    if not text:
        await message.reply_text("Напишите название песни или пришлите публичную ссылку.")
        return

    lock = _lock_for(update)
    if lock.locked():
        await message.reply_text("Подождите, я ещё обрабатываю предыдущий запрос.")
        return

    async with lock:
        url = extract_url(text)
        if url:
            logger.info("Прямая ссылка от пользователя")
            await deliver(message, url)
            return
        if len(text) > 300:
            await message.reply_text("Слишком длинный запрос. Напишите название короче.")
            return
        await offer_choices(message, text)


async def on_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    query = update.callback_query
    if query is None:
        return
    parsed = _parse_pick(query.data)
    if parsed is None:
        await query.answer("Эта кнопка больше не работает. Повторите поиск.", show_alert=True)
        return
    token, index = parsed
    results = _SEARCHES.get(token)
    if results is None or index >= len(results):
        await query.answer("Результат устарел. Повторите поиск.", show_alert=True)
        return

    message = query.message
    if message is None or not hasattr(message, "reply_audio"):
        await query.answer("Не могу отправить ответ на это сообщение.", show_alert=True)
        return

    lock = _lock_for(update)
    if lock.locked():
        await query.answer("Подождите, я ещё скачиваю предыдущий запрос.", show_alert=True)
        return

    await query.answer()
    async with lock:
        logger.info("Выбран результат %s", index + 1)
        await deliver(message, results[index]["url"])


async def offer_choices(message, query: str) -> None:
    status = await message.reply_text("Ищу…")
    try:
        results = await asyncio.to_thread(search_youtube, query)
    except DownloadError as exc:
        await status.edit_text(str(exc))
        return
    except Exception:
        logger.info("Сбой поиска", exc_info=True)
        await status.edit_text("Не удалось выполнить поиск. Попробуйте ещё раз чуть позже.")
        return

    if not results:
        await status.edit_text("Ничего не нашёл. Попробуйте другое название.")
        return

    token = _remember(results)
    keyboard = [
        [
            InlineKeyboardButton(
                _button_title(item.get("title") or "Без названия"),
                callback_data=f"pick:{token}:{index}",
            )
        ]
        for index, item in enumerate(results)
    ]
    await status.edit_text(
        "Нашёл варианты. Выберите трек:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def deliver(message, url: str) -> None:
    status = await message.reply_text("Проверяю ссылку…")
    tmp = tempfile.mkdtemp(prefix="music-bot-")
    try:
        try:
            targets = await asyncio.to_thread(resolve_audio_urls, url)
        except DownloadError as exc:
            await status.edit_text(str(exc))
            return
        except Exception:
            logger.info("Сбой разбора ссылки", exc_info=True)
            await status.edit_text("Не удалось разобрать ссылку. Попробуйте другую.")
            return

        total = len(targets)
        sent = 0
        for index, target in enumerate(targets, start=1):
            progress = f"Скачиваю {index} из {total}…" if total > 1 else "Скачиваю…"
            await _safe_edit(status, progress)
            track_dir = os.path.join(tmp, str(index))
            os.makedirs(track_dir, exist_ok=True)
            try:
                path, meta = await asyncio.to_thread(download_audio, target, track_dir)
            except DownloadError as exc:
                await message.reply_text(str(exc))
                continue
            except Exception:
                logger.info("Сбой скачивания", exc_info=True)
                await message.reply_text(
                    "Не удалось получить аудио. Попробуйте другую ссылку или другой результат."
                )
                continue

            size = os.path.getsize(path)
            title = meta.get("title") or "Без названия"
            if size > TELEGRAM_AUDIO_LIMIT:
                await message.reply_text(
                    f"Файл «{title}» больше 50 МБ, поэтому я не могу его отправить. "
                    "Выберите другой результат или пришлите другую ссылку."
                )
                continue

            try:
                with open(path, "rb") as audio:
                    await message.reply_audio(
                        audio=audio,
                        title=meta.get("title") or "Без названия",
                        performer=meta.get("performer") or "Неизвестный исполнитель",
                        read_timeout=120,
                        write_timeout=300,
                    )
            except TelegramError:
                logger.info("Telegram не принял аудио", exc_info=True)
                await message.reply_text(
                    f"Не удалось отправить «{title}». Попробуйте другой результат."
                )
                continue
            sent += 1

        if sent:
            done = "Готово." if total == 1 else f"Готово: {sent} из {total}."
            await _safe_edit(status, done)
        elif total > 1:
            await _safe_edit(status, "Не удалось отправить треки из плейлиста.")
        else:
            await _safe_edit(status, "Не удалось отправить аудио.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def extract_url(text: str) -> str | None:
    match = _URL_RE.search(text)
    if match is None:
        return None
    return match.group(0).rstrip(".,!?;:)]}>\"'")


def _remember(results: list[dict]) -> str:
    token = uuid.uuid4().hex[:8]
    while token in _SEARCHES:
        token = uuid.uuid4().hex[:8]
    _SEARCHES[token] = results
    _SEARCHES.move_to_end(token)
    while len(_SEARCHES) > _SEARCH_LIMIT:
        _SEARCHES.popitem(last=False)
    return token


def _parse_pick(data: str | None) -> tuple[str, int] | None:
    if not data:
        return None
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "pick" or not parts[2].isdigit():
        return None
    return parts[1], int(parts[2])


def _button_title(title: str) -> str:
    cleaned = " ".join(title.split()) or "Без названия"
    if len(cleaned) <= 60:
        return cleaned
    return cleaned[:59].rstrip() + "…"


def _lock_for(update: Update) -> asyncio.Lock:
    if update.effective_user is not None:
        actor = update.effective_user.id
    elif update.effective_chat is not None:
        actor = update.effective_chat.id
    else:
        actor = 0
    lock = _LOCKS.get(actor)
    if lock is None:
        lock = asyncio.Lock()
        _LOCKS[actor] = lock
    return lock


async def _safe_edit(status, text: str) -> None:
    try:
        await status.edit_text(text)
    except TelegramError:
        logger.info("Не удалось обновить служебное сообщение")


def main() -> None:
    configure_logging()
    load_dotenv(Path(__file__).resolve().parent / ".env")
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        logger.error("Задайте BOT_TOKEN в файле .env (см. .env.example).")
        sys.exit(1)
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        logger.error("ffmpeg не найден в PATH. Конвертация в MP3 не сработает.")

    logger.info("Запускаю бота")
    application = build_application(token)
    application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    logger.info("Бот остановлен")


if __name__ == "__main__":
    main()
