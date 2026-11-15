"""Поиск и скачивание публичного аудио через yt-dlp.

Платный, приватный и защищённый DRM контент не скачивается.
Обход геоограничений и DRM выключен.
"""

from __future__ import annotations

import ipaddress
import logging
import os
import re
import shutil
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp
from dotenv import load_dotenv

logger = logging.getLogger("music_bot.downloader")

# Опциональный файл cookies. Оставьте переменную закомментированной в .env.
# Раскомментируйте COOKIES_FILE только для публичных страниц, которые просят
# подтвердить браузер. Не используйте cookies для платного или закрытого контента.
# COOKIES_FILE=

_MAX_TRACKS = 5
_FIELD_LIMIT = 64
_FILENAME_LIMIT = 80
_BLOCKED_AVAILABILITY = {
    "private": "Это закрытая запись. Я скачиваю только публичные материалы.",
    "needs_auth": "Эта запись требует входа. Я скачиваю только публичные материалы.",
    "premium_only": "Это платный материал. Я не скачиваю платный контент.",
    "subscriber_only": "Эта запись только для подписчиков. Нужна публичная ссылка.",
}
_LIVE_REJECTION = (
    "Это прямой эфир или премьера, а не готовая запись. "
    "Пришлите уже опубликованный трек."
)
_PLAYLIST_SEGMENTS = {"playlist", "playlists", "album", "albums", "sets"}
_INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class DownloadError(Exception):
    """Ошибка, текст которой можно показать пользователю."""


def search_youtube(query: str) -> list[dict]:
    """Ищет до 5 роликов на YouTube через ytsearch5.

    Каждый результат: title, url, duration, uploader.
    """
    cleaned = " ".join(query.split())
    if not cleaned:
        return []
    if len(cleaned) > 300:
        cleaned = cleaned[:300]

    options = _common_options()
    options.update(
        {
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": True,
            "playlistend": _MAX_TRACKS,
        }
    )
    info = _extract(f"ytsearch5:{cleaned}", options, download=False)
    results: list[dict] = []
    for entry in _entries(info):
        url = _entry_url(entry, source="https://www.youtube.com/watch")
        if not url:
            continue
        results.append(
            {
                "title": _clip_field(entry.get("title"), "Без названия", limit=200),
                "url": url,
                "duration": _duration_seconds(entry.get("duration")),
                "uploader": _optional_text(
                    entry.get("uploader") or entry.get("channel") or entry.get("artist")
                ),
            }
        )
        if len(results) >= _MAX_TRACKS:
            break
    logger.info("Поиск %r: %s результатов", cleaned, len(results))
    return results


def download_audio(url: str, output_dir: str) -> tuple[str, dict]:
    """Скачивает один публичный ролик и конвертирует его в MP3 192 kbps.

    Возвращает путь к файлу и метаданные ``{title, performer}``.
    В параметрах yt-dlp стоит ``playlistend: 5``, чтобы плейлист не разрастался,
    но сама функция сохраняет один трек. Список ссылок плейлиста собирает
    :func:`resolve_audio_urls`.
    """
    checked = validate_url(url)
    _require_ffmpeg()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    options = _download_options(output)
    info = _extract(checked, options, download=True)
    entry = _primary_entry(info)
    rejection = _rejection_reason(entry)
    if rejection:
        raise DownloadError(rejection)
    path = _mp3_from_entry(entry, output) or _mp3_from_entry(info, output)
    if path is None:
        mp3s = sorted(item for item in output.glob("*.mp3") if item.is_file())
        path = mp3s[0] if mp3s else None
    if path is None or not path.is_file() or path.stat().st_size <= 0:
        raise DownloadError("Не удалось получить MP3. Попробуйте другую ссылку.")
    if not _inside(path, output):
        raise DownloadError("Не удалось сохранить файл.")

    meta = _metadata(entry)
    final_path = _rename_for_telegram(path, meta, output)
    logger.info(
        "Готов MP3 %s (%s байт)",
        final_path.name,
        final_path.stat().st_size,
    )
    return str(final_path), meta


def resolve_audio_urls(url: str) -> list[str]:
    """Возвращает одну ссылку или первые 5 треков плейлиста либо альбома."""
    checked = validate_url(url)
    if not is_playlist_url(checked):
        return [checked]

    options = _common_options()
    options.update(
        {
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": False,
            "playlistend": _MAX_TRACKS,
        }
    )
    info = _extract(checked, options, download=False)
    urls: list[str] = []
    for entry in _entries(info):
        entry_link = _entry_url(entry, source=checked)
        if not entry_link or is_playlist_url(entry_link):
            continue
        try:
            entry_link = validate_url(entry_link)
        except DownloadError:
            logger.info("Пропускаю непубличную ссылку из плейлиста")
            continue
        if entry_link in urls:
            continue
        urls.append(entry_link)
        if len(urls) >= _MAX_TRACKS:
            break
    if not urls:
        raise DownloadError("В плейлисте нет доступных публичных треков.")
    logger.info("Плейлист: беру %s треков", len(urls))
    return urls


def validate_url(url: str) -> str:
    raw = url.strip()
    if len(raw) > 2000:
        raise DownloadError("Слишком длинная ссылка.")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise DownloadError(
            "Нужна публичная ссылка, которая начинается с http:// или https://."
        )
    if parsed.username or parsed.password:
        raise DownloadError(
            "Ссылка с логином или паролем не подходит. Пришлите публичную ссылку."
        )
    host = parsed.hostname.lower().rstrip(".")
    if (
        host in {"localhost", "localhost.localdomain"}
        or host.endswith(".local")
        or host.endswith(".internal")
    ):
        raise DownloadError("Эта ссылка не ведёт на публичный источник.")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        raise DownloadError("Эта ссылка не ведёт на публичный источник.")
    return raw


def is_playlist_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()
    segments = [part for part in path.split("/") if part]
    if any(part in _PLAYLIST_SEGMENTS for part in segments):
        return True
    host = (parsed.hostname or "").lower().removeprefix("www.")
    query = parse_qs(parsed.query)
    if host.endswith(("youtube.com", "youtu.be")) and "list" in query and "v" not in query:
        return True
    return False


def explain_failure(exc: BaseException) -> str:
    raw = str(exc)
    for message in (
        *_BLOCKED_AVAILABILITY.values(),
        _LIVE_REJECTION,
    ):
        if message in raw:
            return message

    text = raw.lower()
    rules: tuple[tuple[tuple[str, ...], str], ...] = (
        (
            ("premium_only", "paid video", "purchase this", "requires payment"),
            _BLOCKED_AVAILABILITY["premium_only"],
        ),
        (
            ("subscriber_only", "members-only", "join this channel", "channel members"),
            _BLOCKED_AVAILABILITY["subscriber_only"],
        ),
        (
            ("private video", "video is private", "this video is private"),
            _BLOCKED_AVAILABILITY["private"],
        ),
        (
            (
                "sign in to confirm you’re not a bot",
                "sign in to confirm you're not a bot",
            ),
            "Источник временно не отдаёт эту запись без подтверждения браузера. Попробуйте другую ссылку.",
        ),
        (
            (
                "confirm your age",
                "age-restricted",
                "sign in to confirm your age",
            ),
            "Это видео с ограничением по возрасту или требует входа. Доступны только открытые записи.",
        ),
        (
            (
                "not available in your country",
                "blocked it in your country",
                "geo restricted",
                "geo-restricted",
            ),
            "Это видео недоступно в вашем регионе. Попробуйте другую ссылку.",
        ),
        (
            (
                "removed by the uploader",
                "has been removed",
                "video unavailable",
                "this video is unavailable",
                "account associated with this video has been terminated",
            ),
            "Запись недоступна или была удалена.",
        ),
        (
            ("ffmpeg", "ffprobe"),
            "Не найден ffmpeg. Установите его и добавьте в PATH, затем перезапустите бота.",
        ),
        (
            ("unsupported url",),
            "Эта ссылка не поддерживается. Пришлите публичную ссылку на ролик или трек.",
        ),
        (
            ("is not a valid url", "invalid url"),
            "Ссылка выглядит некорректно. Пришлите публичный адрес ролика.",
        ),
        (
            ("drm", "protected content", "widevine"),
            "Этот материал защищён. Я не обхожу защиту.",
        ),
        (
            ("copyright claim", "copyright"),
            "Правообладатель закрыл доступ к этой записи.",
        ),
        (
            ("http error 404", "404: not found"),
            "Запись не найдена. Проверьте ссылку.",
        ),
        (
            ("http error 403", "403: forbidden"),
            "Источник отклонил запрос. Попробуйте другую ссылку.",
        ),
        (
            ("failed to load cookies", "cookie file"),
            "Не удалось прочитать файл cookies. Проверьте COOKIES_FILE или уберите эту настройку.",
        ),
        (
            ("timed out", "timeout", "unable to download webpage", "network is unreachable"),
            "Не получилось связаться с источником. Попробуйте ещё раз чуть позже.",
        ),
    )
    for keys, message in rules:
        if any(key in text for key in keys):
            return message
    return "Не удалось получить аудио. Попробуйте другую ссылку или другой результат."


def _download_options(output: Path) -> dict:
    options = _common_options()
    options.update(
        {
            "format": "bestaudio/best",
            "outtmpl": str(output / "%(id)s.%(ext)s"),
            "noplaylist": True,
            "playlistend": _MAX_TRACKS,
            "max_downloads": _MAX_TRACKS,
            "keepvideo": False,
            "overwrites": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "match_filter": _public_only,
        }
    )
    return options


def _common_options() -> dict:
    _load_env()
    options = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "restrictfilenames": True,
        "windowsfilenames": True,
        # Региональные ограничения не обходим: пользователь получит понятную ошибку.
        "geo_bypass": False,
        "socket_timeout": 30,
        "retries": 2,
        "fragment_retries": 2,
        "playlistend": _MAX_TRACKS,
    }
    options.update(_cookies_options())
    return options


def _cookies_options() -> dict:
    raw = os.getenv("COOKIES_FILE", "").strip()
    if not raw or raw.startswith("#"):
        return {}
    path = Path(raw).expanduser()
    if not path.is_file():
        logger.warning("COOKIES_FILE задан, но файл не найден")
        return {}
    logger.info("Используется файл cookies только для публичных страниц")
    return {"cookiefile": str(path)}


def _load_env() -> None:
    load_dotenv(Path(__file__).resolve().parent / ".env")


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise DownloadError(
            "Не найден ffmpeg. Установите его и добавьте в PATH, затем перезапустите бота."
        )


def _rejection_reason(info: dict) -> str | None:
    availability = str(info.get("availability") or "").strip().lower()
    if availability in _BLOCKED_AVAILABILITY:
        return _BLOCKED_AVAILABILITY[availability]
    live_status = str(info.get("live_status") or "").strip().lower()
    if info.get("is_live") or live_status in {"is_live", "is_upcoming"}:
        return _LIVE_REJECTION
    return None


def _public_only(info: dict, incomplete: bool = False) -> str | None:
    """Останавливает yt-dlp до записи файла, если источник не публичный."""
    del incomplete
    reason = _rejection_reason(info)
    if reason:
        raise DownloadError(reason)
    return None


def _extract(url: str, options: dict, *, download: bool) -> dict:
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=download)
    except DownloadError:
        raise
    except Exception as exc:
        logger.info("yt-dlp не смог обработать %s: %s", url, exc)
        raise DownloadError(explain_failure(exc)) from exc
    if not isinstance(info, dict):
        raise DownloadError("Не удалось получить аудио. Попробуйте другую ссылку.")
    return info


def _entries(info: dict) -> list[dict]:
    entries = info.get("entries")
    if isinstance(entries, list):
        return [entry for entry in entries if isinstance(entry, dict)]
    return [info]


def _primary_entry(info: dict) -> dict:
    entries = _entries(info)
    return entries[0] if entries else info


def _entry_url(entry: dict, *, source: str) -> str | None:
    for key in ("webpage_url", "url"):
        value = entry.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value

    video_id = entry.get("id")
    if not isinstance(video_id, str) or not video_id:
        raw_url = entry.get("url")
        if isinstance(raw_url, str) and raw_url and not raw_url.startswith(("http://", "https://")):
            video_id = raw_url
    if not isinstance(video_id, str) or not video_id:
        return None

    extractor = " ".join(
        str(entry.get(key) or "")
        for key in ("ie_key", "extractor_key", "extractor")
    ).lower()
    source_host = (urlparse(source).hostname or "").lower()
    if "youtube" in extractor or "youtu" in source_host:
        return f"https://www.youtube.com/watch?v={video_id}"
    return None


def _mp3_from_entry(entry: dict, output: Path) -> Path | None:
    candidates: list[Path] = []
    downloads = entry.get("requested_downloads")
    if isinstance(downloads, list):
        for item in downloads:
            if not isinstance(item, dict):
                continue
            for key in ("filepath", "filename"):
                raw = item.get(key)
                if isinstance(raw, str) and raw:
                    candidates.append(Path(raw))
    for key in ("filepath", "filename"):
        raw = entry.get(key)
        if isinstance(raw, str) and raw:
            candidates.append(Path(raw))

    video_id = entry.get("id")
    if isinstance(video_id, str) and video_id:
        candidates.extend(output.glob(f"*{video_id}*.mp3"))

    seen: set[Path] = set()
    for candidate in candidates:
        mp3 = candidate if candidate.suffix.lower() == ".mp3" else candidate.with_suffix(".mp3")
        resolved = mp3 if mp3.is_absolute() else output / mp3.name
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file() and _inside(resolved, output):
            return resolved
    return None


def _metadata(entry: dict) -> dict:
    title = _clip_field(entry.get("track") or entry.get("title"), "Без названия")
    performer = _clip_field(
        entry.get("artist")
        or entry.get("album_artist")
        or entry.get("creator")
        or entry.get("uploader")
        or entry.get("channel"),
        "Неизвестный исполнитель",
    )
    return {"title": title, "performer": performer}


def _rename_for_telegram(path: Path, meta: dict, output: Path) -> Path:
    stem = _sanitize_filename(f"{meta['performer']} - {meta['title']}") or "audio"
    dest = output / f"{stem}.mp3"
    counter = 2
    while dest.exists() and dest.resolve() != path.resolve():
        dest = output / f"{stem} ({counter}).mp3"
        counter += 1
    if dest.resolve() != path.resolve():
        path.replace(dest)
    return dest


def _sanitize_filename(name: str) -> str:
    cleaned = _INVALID_FILENAME.sub(" ", name)
    cleaned = " ".join(cleaned.split()).strip(" .")
    if len(cleaned) > _FILENAME_LIMIT:
        cleaned = cleaned[:_FILENAME_LIMIT].rstrip(" .")
    return cleaned


def _clip_field(value: object, fallback: str, limit: int = _FIELD_LIMIT) -> str:
    if isinstance(value, str):
        text = " ".join(value.replace("\x00", "").split()).strip()
    else:
        text = ""
    if not text:
        text = fallback
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.replace("\x00", "").split()).strip()
    return text or None


def _duration_seconds(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return None
    if seconds < 0:
        return None
    return seconds


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True
