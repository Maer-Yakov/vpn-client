"""Telegram-бот: ищет полный трек на YouTube, затем на SoundCloud."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import sys
import tempfile
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
    MetadataError,
    catalog_service,
    detect_source,
    download_audio,
    ensure_size_limit,
    expand_targets,
    explain_failure,
    lookup_title,
    read_share_metadata,
    search_soundcloud,
    search_youtube,
)

logger = logging.getLogger("music_bot")

_URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)
_PICK_RE = re.compile(r"^(yt|sc)_(\d+)$")
# chat_id -> {"query": str, "yt": list[dict], "sc": list[dict]}
_RESULTS: dict[int, dict] = {}
_LOCKS: dict[int, asyncio.Lock] = {}
_TOO_BIG = "Трек слишком большой для Telegram. Попробуйте другой результат."

START_TEXT = (
    "Привет! Я найду песню и пришлю полный трек в MP3.\n\n"
    "Напишите название — покажу до 5 вариантов с YouTube: "
    "название, длительность и источник.\n"
    "Если YouTube ничего не дал, ролик закрыт или файл слишком большой, "
    "попробую тот же запрос на SoundCloud.\n\n"
    "Можно сразу прислать ссылку на YouTube или SoundCloud.\n"
    "Ссылку Spotify или Apple Music я не скачиваю: читаю только название и исполнителя, "
    "а сам трек ищу на YouTube.\n"
    "Из плейлиста беру только первые 5 треков.\n\n"
    "Команда /help — подробнее."
)

HELP_TEXT = (
    "Что я умею:\n\n"
    "• искать трек на YouTube и показывать 5 кнопок с названием, длительностью и источником;\n"
    "• если YouTube пуст, недоступен или файл больше 45 МБ — искать тот же запрос на SoundCloud;\n"
    "• скачивать полный трек по ссылке YouTube или SoundCloud;\n"
    "• по ссылке Spotify или Apple Music читать только название и исполнителя, "
    "а аудио искать на YouTube;\n"
    "• присылать MP3 с названием, исполнителем и длительностью;\n"
    "• из плейлиста брать только первые 5 треков.\n\n"
    "Файл больше 45 МБ я перекодирую в 128 кбит/с. Обрезанный фрагмент не отправляю.\n\n"
    "Ограничения:\n\n"
    "• только публичные записи;\n"
    "• без обхода DRM и без платных подписок;\n"
    "• закрытые ролики не скачиваю."
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
    application.add_handler(CallbackQueryHandler(on_pick, pattern=r"^(yt|sc)_\d+$"))
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
    del context
    message = update.message
    if message is None or not message.text:
        return
    text = message.text.strip()
    if not text:
        await message.reply_text(
            "Напишите название песни или пришлите ссылку YouTube, SoundCloud, Spotify или Apple Music."
        )
        return
    chat_id = _chat_id(update)
    if chat_id is None:
        return
    lock = _lock_for(chat_id)
    if lock.locked():
        await message.reply_text("Подождите, я ещё обрабатываю предыдущий запрос.")
        return

    async with lock:
        url = extract_url(text)
        if url:
            if catalog_service(url):
                logger.info("Ссылка каталога, только метаданные")
                await deliver_catalog(message, url)
                return
            if detect_source(url) is None:
                await message.reply_text(
                    "Нужна ссылка на YouTube, SoundCloud, Spotify или Apple Music, либо название песни."
                )
                return
            logger.info("Прямая ссылка от пользователя")
            await deliver_url(message, url, fallback_query=None)
            return
        if len(text) > 300:
            await message.reply_text("Слишком длинный запрос. Напишите название короче.")
            return
        await offer_youtube(message, chat_id, text)


async def on_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    query = update.callback_query
    if query is None:
        return
    match = _PICK_RE.fullmatch(query.data or "")
    if match is None:
        await query.answer("Эта кнопка больше не работает. Повторите поиск.", show_alert=True)
        return
    kind, index_text = match.group(1), match.group(2)
    index = int(index_text)
    chat_id = _chat_id(update)
    bucket = _RESULTS.get(chat_id) if chat_id is not None else None
    results = (bucket or {}).get(kind) or []
    if index >= len(results) or chat_id is None:
        await query.answer("Результат устарел. Повторите поиск.", show_alert=True)
        return
    message = query.message
    if message is None or not hasattr(message, "reply_audio"):
        await query.answer("Не могу отправить ответ на это сообщение.", show_alert=True)
        return
    lock = _lock_for(chat_id)
    if lock.locked():
        await query.answer("Подождите, я ещё скачиваю предыдущий запрос.", show_alert=True)
        return

    await query.answer()
    item = results[index]
    text_query = str((bucket or {}).get("query") or item.get("title") or "")
    async with lock:
        logger.info("Выбран результат %s_%s", kind, index)
        await deliver_url(
            message,
            item["url"],
            fallback_query=text_query if kind == "yt" else None,
        )


async def offer_youtube(message, chat_id: int, query: str) -> None:
    status = await message.reply_text("Ищу на YouTube…")
    try:
        results = await asyncio.to_thread(search_youtube, query)
    except DownloadError as exc:
        logger.info("Поиск YouTube не удался: %s", exc)
        results = []
    except Exception:
        logger.info("Сбой поиска YouTube", exc_info=True)
        results = []

    if results:
        _remember(chat_id, query, "yt", results)
        await status.edit_text(
            "Нашёл на YouTube. Выберите трек:",
            reply_markup=_keyboard(results, "yt"),
        )
        return

    await status.edit_text("На YouTube ничего нет. Ищу на SoundCloud…")
    await _offer_soundcloud(message, chat_id, query, status)


async def _offer_soundcloud(message, chat_id: int, query: str, status) -> None:
    try:
        results = await asyncio.to_thread(search_soundcloud, query)
    except DownloadError as exc:
        await status.edit_text(str(exc))
        return
    except Exception:
        logger.info("Сбой поиска SoundCloud", exc_info=True)
        await status.edit_text("Не удалось выполнить поиск. Попробуйте ещё раз чуть позже.")
        return
    if not results:
        await status.edit_text("Ничего не нашёл ни на YouTube, ни на SoundCloud. Попробуйте другое название.")
        return
    _remember(chat_id, query, "sc", results)
    await status.edit_text(
        "Нашёл на SoundCloud. Выберите трек:",
        reply_markup=_keyboard(results, "sc"),
    )


async def deliver_url(message, url: str, fallback_query: str | None) -> None:
    source = detect_source(url)
    status = await message.reply_text("Проверяю ссылку…")
    tmp = tempfile.mkdtemp(prefix="music-bot-")
    try:
        try:
            targets = await asyncio.to_thread(expand_targets, url)
        except DownloadError as exc:
            await _fail_or_fallback(message, status, exc, source, fallback_query, tmp, url)
            return
        except Exception:
            logger.info("Сбой разбора ссылки", exc_info=True)
            await _safe_edit(status, "Не удалось разобрать ссылку. Попробуйте другую.")
            return

        total = len(targets)
        sent = 0
        for index, target in enumerate(targets, start=1):
            progress = f"Скачиваю {index} из {total}…" if total > 1 else "Скачиваю…"
            await _safe_edit(status, progress)
            track_dir = os.path.join(tmp, str(index))
            os.makedirs(track_dir, exist_ok=True)
            query = fallback_query
            if total == 1 and not query and detect_source(target) == "youtube":
                query = await asyncio.to_thread(lookup_title, target)
            try:
                await _send_file(message, target, track_dir)
            except (DownloadError, ValueError) as exc:
                logger.info("Не удалось скачать трек: %s", exc)
                if total == 1 and detect_source(target) == "youtube" and query:
                    if isinstance(exc, ValueError) and "слишком большой" in str(exc):
                        notice = "Файл больше 45 МБ даже после сжатия. Ищу тот же запрос на SoundCloud…"
                    else:
                        notice = "На YouTube не получилось. Ищу тот же запрос на SoundCloud…"
                    await message.reply_text(notice)
                    try:
                        if await _send_soundcloud_query(message, query, os.path.join(tmp, f"sc-{index}")):
                            sent += 1
                            continue
                    except (DownloadError, ValueError) as fallback_exc:
                        await message.reply_text(_user_text(fallback_exc))
                        continue
                await message.reply_text(_user_text(exc))
                continue
            except Exception:
                logger.info("Сбой скачивания", exc_info=True)
                await message.reply_text(
                    "Не удалось получить аудио. Попробуйте другую ссылку или другой результат."
                )
                continue
            sent += 1

        if sent:
            done = "Готово." if sent == 1 else f"Готово: {sent}."
            await _safe_edit(status, done)
        else:
            await _safe_edit(status, "Не удалось отправить аудио.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


async def _fail_or_fallback(
    message,
    status,
    exc: DownloadError,
    source: str | None,
    query: str | None,
    tmp: str,
    url: str,
) -> None:
    fallback = query
    if source == "youtube" and not fallback:
        fallback = await asyncio.to_thread(lookup_title, url)
    if source == "youtube" and fallback:
        await _safe_edit(status, "На YouTube не получилось. Ищу тот же запрос на SoundCloud…")
        try:
            found = await _send_soundcloud_query(message, fallback, os.path.join(tmp, "fallback"))
        except (DownloadError, ValueError) as fallback_exc:
            await _safe_edit(status, _user_text(fallback_exc))
            return
        if found:
            await _safe_edit(status, "Готово.")
            return
    await _safe_edit(status, str(exc))


async def _send_soundcloud_query(message, query: str, output_dir: str) -> bool:
    try:
        results = await asyncio.to_thread(search_soundcloud, query)
    except DownloadError:
        raise
    except Exception:
        logger.info("Сбой запасного поиска SoundCloud", exc_info=True)
        return False
    if not results:
        return False
    os.makedirs(output_dir, exist_ok=True)
    last_error: Exception | None = None
    for index, item in enumerate(results):
        track_dir = os.path.join(output_dir, str(index))
        os.makedirs(track_dir, exist_ok=True)
        try:
            await _send_file(message, item["url"], track_dir)
            return True
        except (DownloadError, ValueError) as exc:
            last_error = exc
            logger.info("SoundCloud вариант не подошёл: %s", exc)
            continue
    if last_error is not None:
        raise last_error
    return False


async def deliver_catalog(message, url: str) -> None:
    status = await message.reply_text("Читаю название и исполнителя…")
    try:
        meta = await asyncio.to_thread(read_share_metadata, url)
    except MetadataError as exc:
        await _safe_edit(status, str(exc))
        return
    service = "Spotify" if meta["service"] == "spotify" else "Apple Music"
    query = str(meta["query"])
    await _safe_edit(
        status,
        f"Название и исполнитель взяты из {service}: {meta['artist']} — {meta['title']}. Ищу на YouTube…",
    )
    try:
        results = await asyncio.to_thread(search_youtube, query)
    except DownloadError as exc:
        logger.info("Поиск YouTube по каталогу не удался: %s", exc)
        results = []
    except Exception:
        logger.info("Сбой поиска YouTube по каталогу", exc_info=True)
        results = []

    tmp = tempfile.mkdtemp(prefix="music-bot-")
    try:
        if not results:
            await message.reply_text("На YouTube ничего не нашлось. Ищу на SoundCloud…")
            await _finish_catalog_on_soundcloud(message, status, service, query, tmp)
            return
        for index, item in enumerate(results):
            track_dir = os.path.join(tmp, f"yt-{index}")
            os.makedirs(track_dir, exist_ok=True)
            try:
                await _send_file(message, item["url"], track_dir)
            except ValueError as exc:
                if "слишком большой" in str(exc):
                    await message.reply_text(
                        "На YouTube трек больше 45 МБ даже после сжатия. Ищу на SoundCloud…"
                    )
                    await _finish_catalog_on_soundcloud(message, status, service, query, tmp)
                    return
            except DownloadError:
                continue
            else:
                await _safe_edit(status, f"Готово. Название и исполнитель взяты из {service}.")
                return
        await message.reply_text("На YouTube не получилось скачать. Ищу на SoundCloud…")
        await _finish_catalog_on_soundcloud(message, status, service, query, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


async def _finish_catalog_on_soundcloud(message, status, service: str, query: str, tmp: str) -> None:
    try:
        found = await _send_soundcloud_query(message, query, os.path.join(tmp, "sc"))
    except (DownloadError, ValueError) as exc:
        await _safe_edit(status, _user_text(exc))
        return
    if found:
        await _safe_edit(status, f"Готово. Название взято из {service}, трек с SoundCloud.")
        return
    await _safe_edit(status, "Не нашёл этот трек ни на YouTube, ни на SoundCloud.")


async def _send_file(message, url: str, output_dir: str) -> None:
    path, meta = await asyncio.to_thread(download_audio, url, output_dir)
    path = await asyncio.to_thread(ensure_size_limit, path, 45)
    if detect_source(url) == "soundcloud":
        await message.reply_text("Этот трек с SoundCloud.")
    duration = meta.get("duration")
    with open(path, "rb") as audio:
        await message.reply_audio(
            audio=audio,
            title=meta.get("title") or "Без названия",
            performer=meta.get("performer") or "Неизвестный исполнитель",
            duration=duration if isinstance(duration, int) and duration > 0 else None,
            read_timeout=120,
            write_timeout=300,
        )


def extract_url(text: str) -> str | None:
    match = _URL_RE.search(text)
    if match is None:
        return None
    return match.group(0).rstrip(".,!?;:)]}>\"'")


def _remember(chat_id: int, query: str, kind: str, results: list[dict]) -> None:
    bucket = _RESULTS.setdefault(chat_id, {"query": query, "yt": [], "sc": []})
    bucket["query"] = query
    bucket[kind] = results
    while len(_RESULTS) > 200:
        _RESULTS.pop(next(iter(_RESULTS)))


def _keyboard(results: list[dict], kind: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                _button_label(item),
                callback_data=f"{kind}_{index}",
            )
        ]
        for index, item in enumerate(results)
    ]
    return InlineKeyboardMarkup(rows)


def _button_label(item: dict) -> str:
    source = "YouTube" if item.get("source") == "youtube" else "SoundCloud"
    duration = _format_duration(item.get("duration"))
    suffix = f" · {duration} · {source}" if duration else f" · {source}"
    title = " ".join(str(item.get("title") or "Без названия").split())
    room = 60 - len(suffix)
    if room < 8:
        suffix = f" · {source}"
        room = 60 - len(suffix)
    if len(title) > room:
        title = title[: max(room - 1, 1)].rstrip() + "…"
    return (title + suffix)[:60]


def _format_duration(value: object) -> str:
    if not isinstance(value, int) or value < 0:
        return ""
    minutes, seconds = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _user_text(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        text = str(exc)
        if "слишком большой" in text:
            return _TOO_BIG
        return text or _TOO_BIG
    if isinstance(exc, DownloadError):
        return str(exc)
    return explain_failure(exc)


def _chat_id(update: Update) -> int | None:
    if update.effective_chat is not None:
        return update.effective_chat.id
    return None


def _lock_for(chat_id: int) -> asyncio.Lock:
    lock = _LOCKS.get(chat_id)
    if lock is None:
        lock = asyncio.Lock()
        _LOCKS[chat_id] = lock
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
