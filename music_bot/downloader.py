"""Поиск и скачивание полного публичного трека через yt-dlp.

Сначала YouTube, затем SoundCloud. Платный, приватный и защищённый DRM
контент не скачивается. Фрагменты и превью не отправляются.
"""

from __future__ import annotations

import ipaddress
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp
from dotenv import load_dotenv

logger = logging.getLogger("music_bot.downloader")

# Необязательный файл cookies для публичных роликов YouTube.
# Оставьте YT_COOKIES закомментированным в .env.
# Не используйте cookies для платного или закрытого контента.
# YT_COOKIES=

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
_FRAGMENT_REJECTION = "Это фрагмент, а не полный трек. Нужна полная публичная запись."
_TOO_BIG = "Трек слишком большой для Telegram. Попробуйте другой результат."
_PLAYLIST_SEGMENTS = {"playlist", "playlists", "album", "albums", "sets"}
_INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class DownloadError(Exception):
    """Ошибка, текст которой можно показать пользователю."""


def search_youtube(query: str, limit: int = 5) -> list[dict]:
    """Ищет до limit роликов на YouTube через ytsearch.

    Каждый результат: title, url, duration, uploader, source.
    """
    return _search(query, limit=limit, source="youtube")


def search_soundcloud(query: str, limit: int = 5) -> list[dict]:
    """Ищет до limit треков на SoundCloud. source всегда \"soundcloud\"."""
    return _search(query, limit=limit, source="soundcloud")


def download_audio(url: str, output_dir: str) -> tuple[str, dict]:
    """Скачивает один полный трек и конвертирует его в MP3 192 kbps.

    Формат yt-dlp: bestaudio/best, без привязки к кодеку.
    noplaylist=True, чтобы одиночное видео не тянуло весь плейлист.
    Метаданные: {title, performer, duration}.
    """
    checked = _supported_url(url)
    _require_ffmpeg()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    info = _extract(checked, _download_options(output, url=checked), download=True)
    entry = _primary_entry(info)
    rejection = _rejection_reason(entry)
    if rejection:
        raise DownloadError(rejection)
    if _is_fragment(entry):
        raise DownloadError(_FRAGMENT_REJECTION)

    path = _mp3_from_entry(entry, output) or _mp3_from_entry(info, output)
    if path is None:
        mp3s = sorted(item for item in output.glob("*.mp3") if item.is_file())
        path = mp3s[0] if mp3s else None
    if path is None or not path.is_file() or path.stat().st_size <= 0:
        raise DownloadError("Не удалось получить MP3. Попробуйте другую ссылку.")
    if not _inside(path, output):
        raise DownloadError("Не удалось сохранить файл.")
    if _file_is_fragment(path, entry):
        path.unlink(missing_ok=True)
        raise DownloadError(_FRAGMENT_REJECTION)

    meta = _metadata(entry, path)
    final_path = _rename_for_telegram(path, meta, output)
    logger.info("Готов MP3 %s (%s байт)", final_path.name, final_path.stat().st_size)
    return str(final_path), meta


def ensure_size_limit(path: str, max_mb: int = 45) -> str:
    """Возвращает путь к MP3 не больше max_mb.

    Если файл больше лимита, исходник удаляется и трек перекодируется
    в 128 кбит/с без обрезки. Если и после этого он больше лимита,
    новый файл удаляется и выбрасывается ValueError.
    """
    source = Path(path)
    if not source.is_file():
        raise ValueError("Не удалось подготовить файл для отправки.")
    limit = max(max_mb, 1) * 1024 * 1024
    if source.stat().st_size <= limit:
        return str(source)

    _require_ffmpeg()
    smaller = source.with_name(f"{source.stem}-128.mp3")
    if smaller.resolve() == source.resolve():
        smaller = source.with_name(f"{source.stem}-128k.mp3")
    completed = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "128k",
            str(smaller),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    source.unlink(missing_ok=True)
    if completed.returncode != 0 or not smaller.is_file() or smaller.stat().st_size <= 0:
        smaller.unlink(missing_ok=True)
        logger.info("ffmpeg не смог перекодировать трек в 128 кбит/с")
        raise ValueError("Не удалось ужать трек до размера, который принимает Telegram.")
    if smaller.stat().st_size > limit:
        smaller.unlink(missing_ok=True)
        raise ValueError(_TOO_BIG)
    logger.info("Трек перекодирован в 128 кбит/с (%s байт)", smaller.stat().st_size)
    return str(smaller)


def expand_targets(url: str) -> list[str]:
    """Одна ссылка или первые 5 треков плейлиста YouTube/SoundCloud."""
    checked = _supported_url(url)
    if not is_playlist_url(checked):
        return [checked]

    source = detect_source(checked) or "youtube"
    options = _base_options(youtube=source == "youtube")
    options.update(
        {
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": False,
            "playlistend": 5,
        }
    )
    info = _extract(checked, options, download=False)
    urls: list[str] = []
    for entry in _entries(info):
        link = _entry_url(entry, source)
        if not link or is_playlist_url(link) or detect_source(link) is None:
            continue
        try:
            link = _supported_url(link)
        except DownloadError:
            continue
        if link in urls:
            continue
        urls.append(link)
        if len(urls) >= 5:
            break
    if not urls:
        raise DownloadError("В плейлисте нет доступных публичных треков.")
    logger.info("Плейлист: беру %s треков", len(urls))
    return urls


def lookup_title(url: str) -> str | None:
    """Пытается узнать название без скачивания, чтобы повторить поиск."""
    try:
        checked = _supported_url(url)
    except DownloadError:
        return None
    source = detect_source(checked) or "youtube"
    options = _base_options(youtube=source == "youtube")
    options.update({"skip_download": True, "noplaylist": True})
    try:
        info = _extract(checked, options, download=False)
    except DownloadError:
        return None
    title = _optional_text(_primary_entry(info).get("track") or _primary_entry(info).get("title"))
    return title


def detect_source(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    if host == "youtu.be" or host.endswith("youtube.com"):
        return "youtube"
    if host.endswith("soundcloud.com"):
        return "soundcloud"
    return None


def is_playlist_url(url: str) -> bool:
    parsed = urlparse(url)
    segments = [part for part in parsed.path.lower().split("/") if part]
    if any(part in _PLAYLIST_SEGMENTS for part in segments):
        return True
    host = (parsed.hostname or "").lower().removeprefix("www.")
    query = parse_qs(parsed.query)
    if host.endswith(("youtube.com", "youtu.be")) and "list" in query and "v" not in query:
        return True
    return False


def explain_failure(exc: BaseException) -> str:
    raw = str(exc)
    for message in (*_BLOCKED_AVAILABILITY.values(), _LIVE_REJECTION, _FRAGMENT_REJECTION, _TOO_BIG):
        if message in raw:
            return message
    text = raw.lower()
    rules: tuple[tuple[tuple[str, ...], str], ...] = (
        (
            ("premium_only", "paid video", "purchase this", "requires payment", "premium"),
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
            ("confirm your age", "age-restricted", "sign in to confirm your age"),
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
            "Эта ссылка не поддерживается. Пришлите публичную ссылку YouTube или SoundCloud.",
        ),
        (
            ("preview", "snippet", "fragment"),
            _FRAGMENT_REJECTION,
        ),
        (
            ("drm", "protected content", "widevine"),
            "Этот материал защищён. Я не обхожу защиту.",
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


def _search(query: str, *, limit: int, source: str) -> list[dict]:
    cleaned = " ".join(query.split())
    if not cleaned:
        return []
    if len(cleaned) > 300:
        cleaned = cleaned[:300]
    bounded = _bounded_limit(limit)
    prefix = "ytsearch" if source == "youtube" else "scsearch"
    options = _base_options(youtube=source == "youtube")
    options.update(
        {
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": True,
            "playlistend": bounded,
        }
    )
    info = _extract(f"{prefix}{bounded}:{cleaned}", options, download=False)
    results: list[dict] = []
    for entry in _entries(info):
        if _rejection_reason(entry):
            continue
        url = _entry_url(entry, source)
        if not url or detect_source(url) != source:
            continue
        results.append(
            {
                "title": _clip_field(entry.get("title"), "Без названия", limit=200),
                "url": url,
                "duration": _duration_seconds(entry.get("duration")),
                "uploader": _optional_text(
                    entry.get("uploader") or entry.get("channel") or entry.get("artist")
                ),
                "source": source,
            }
        )
        if len(results) >= bounded:
            break
    logger.info("Поиск %s %r: %s результатов", source, cleaned, len(results))
    return results


def _download_options(output: Path, *, url: str) -> dict:
    options = _base_options(youtube=detect_source(url) == "youtube")
    options.update(
        {
            "format": "bestaudio/best",
            "outtmpl": str(output / "%(id)s.%(ext)s"),
            "noplaylist": True,
            "max_downloads": 1,
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


def _base_options(*, youtube: bool) -> dict:
    _load_env()
    options = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "restrictfilenames": True,
        "windowsfilenames": True,
        "geo_bypass": False,
        "socket_timeout": 30,
        "retries": 2,
        "fragment_retries": 2,
    }
    if youtube:
        options.update(_youtube_cookies())
    return options


def _youtube_cookies() -> dict:
    raw = os.getenv("YT_COOKIES", "").strip()
    if not raw or raw.startswith("#"):
        return {}
    path = Path(raw).expanduser()
    if not path.is_file():
        logger.warning("YT_COOKIES задан, но файл не найден")
        return {}
    logger.info("Используются cookies YouTube только для публичных роликов")
    return {"cookiefile": str(path)}


def _load_env() -> None:
    load_dotenv(Path(__file__).resolve().parent / ".env")


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise DownloadError(
            "Не найден ffmpeg. Установите его и добавьте в PATH, затем перезапустите бота."
        )


def _supported_url(url: str) -> str:
    raw = url.strip()
    if len(raw) > 2000:
        raise DownloadError("Слишком длинная ссылка.")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise DownloadError("Нужна публичная ссылка на YouTube или SoundCloud.")
    if parsed.username or parsed.password:
        raise DownloadError("Ссылка с логином или паролем не подходит. Пришлите публичную ссылку.")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal")):
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
    if detect_source(raw) is None:
        raise DownloadError("Нужна публичная ссылка на YouTube или SoundCloud.")
    return raw


def _rejection_reason(info: dict) -> str | None:
    availability = str(info.get("availability") or "").strip().lower()
    if availability in _BLOCKED_AVAILABILITY:
        return _BLOCKED_AVAILABILITY[availability]
    live_status = str(info.get("live_status") or "").strip().lower()
    if info.get("is_live") or live_status in {"is_live", "is_upcoming"}:
        return _LIVE_REJECTION
    return None


def _public_only(info: dict, incomplete: bool = False) -> str | None:
    """Убирает превью и платные форматы до выбора bestaudio/best."""
    reason = _rejection_reason(info)
    if reason:
        raise DownloadError(reason)
    # На раннем проходе yt-dlp передаёт incomplete=True, список форматов ещё не полный.
    if incomplete is True:
        return None
    formats = info.get("formats")
    if not isinstance(formats, list) or not formats:
        return None
    kept = [
        item
        for item in formats
        if isinstance(item, dict) and not _format_is_preview(item) and not _format_is_premium(item)
    ]
    if not kept:
        if any(isinstance(item, dict) and _format_is_premium(item) for item in formats):
            raise DownloadError(_BLOCKED_AVAILABILITY["premium_only"])
        raise DownloadError(_FRAGMENT_REJECTION)
    info["formats"] = kept
    return None


def _format_is_preview(item: dict) -> bool:
    format_id = str(item.get("format_id") or "").lower()
    url = str(item.get("url") or "")
    note = str(item.get("format_note") or "").lower()
    return "preview" in format_id or "/preview/" in url or note == "preview"


def _format_is_premium(item: dict) -> bool:
    return str(item.get("format_note") or "").lower() == "premium"


def _is_fragment(info: dict) -> bool:
    """True, если скачанный формат — превью, а не полный трек."""
    selected: list[dict] = []
    for key in ("requested_downloads", "requested_formats"):
        items = info.get(key)
        if isinstance(items, list):
            selected.extend(item for item in items if isinstance(item, dict))
    return any(_format_is_preview(item) for item in selected)


def _file_is_fragment(path: Path, entry: dict) -> bool:
    expected = _duration_seconds(entry.get("duration"))
    actual = _probe_duration(path)
    if expected is None or actual is None:
        return False
    # Превью SoundCloud обычно около 30 секунд при длинном полном треке.
    return expected >= 90 and actual <= 35


def _probe_duration(path: Path) -> int | None:
    if shutil.which("ffprobe") is None:
        return None
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return _duration_seconds(completed.stdout.strip())


def _extract(url: str, options: dict, *, download: bool) -> dict:
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=download)
    except DownloadError:
        raise
    except Exception as exc:
        logger.info("yt-dlp не смог обработать ссылку: %s", exc)
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


def _entry_url(entry: dict, source: str) -> str | None:
    for key in ("webpage_url", "url"):
        value = entry.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
    video_id = entry.get("id")
    if not isinstance(video_id, str) or not video_id:
        raw_url = entry.get("url")
        if isinstance(raw_url, str) and raw_url and not raw_url.startswith(("http://", "https://")):
            video_id = raw_url
    if source == "youtube" and isinstance(video_id, str) and video_id:
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


def _metadata(entry: dict, path: Path) -> dict:
    title = _clip_field(entry.get("track") or entry.get("title"), "Без названия")
    performer = _clip_field(
        entry.get("artist")
        or entry.get("album_artist")
        or entry.get("creator")
        or entry.get("uploader")
        or entry.get("channel"),
        "Неизвестный исполнитель",
    )
    duration = _duration_seconds(entry.get("duration")) or _probe_duration(path)
    return {"title": title, "performer": performer, "duration": duration}


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
    if isinstance(value, str):
        value = value.strip()
    try:
        seconds = int(float(value))
    except (TypeError, ValueError):
        return None
    if seconds < 0:
        return None
    return seconds


def _bounded_limit(limit: int) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return 5
    return min(max(value, 1), 10)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True
