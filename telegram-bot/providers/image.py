"""Image generation via the OpenAI images API (or any compatible base URL).

``generate`` returns a string the handler can turn into a photo:

- ``http://...`` or ``https://...`` — send this URL as the photo
- anything else — a local PNG path; send the file, then delete it
"""

from __future__ import annotations

import base64
import logging
import os
import tempfile

from openai import AsyncOpenAI

from config import get_settings
from providers import ProviderError

logger = logging.getLogger(__name__)


def is_image_url(result: str) -> bool:
    return result.startswith("http://") or result.startswith("https://")


def is_managed_file(path: str) -> bool:
    """True for a PNG this process created under the system temp directory."""
    if not path or is_image_url(path):
        return False
    root = os.path.realpath(tempfile.gettempdir())
    try:
        candidate = os.path.realpath(path)
    except OSError:
        return False
    return candidate.startswith(root + os.sep) and os.path.isfile(candidate)


async def generate(
    prompt: str,
    model: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """Return an image URL or a local PNG path. ``history`` is ignored."""
    del history
    settings = get_settings()
    if not settings.image_api_key:
        raise ProviderError("IMAGE_API_KEY is empty")
    kwargs: dict[str, str] = {"api_key": settings.image_api_key}
    if settings.image_base_url:
        kwargs["base_url"] = settings.image_base_url
    client = AsyncOpenAI(**kwargs, timeout=90.0)
    try:
        response = await client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size="1024x1024",
        )
    except Exception as exc:
        logger.exception("Image request failed")
        raise ProviderError("image") from exc
    finally:
        try:
            await client.close()
        except Exception:
            logger.debug("image client close failed", exc_info=True)
    if not response.data:
        raise ProviderError("empty image response")
    item = response.data[0]
    url = getattr(item, "url", None)
    if url:
        if not is_image_url(str(url)):
            raise ProviderError("image url rejected")
        return str(url)
    encoded = getattr(item, "b64_json", None)
    if not encoded:
        raise ProviderError("image had no url or bytes")
    try:
        raw = base64.b64decode(encoded)
    except Exception as exc:
        logger.exception("Image payload was not base64")
        raise ProviderError("bad image payload") from exc
    handle, path = tempfile.mkstemp(suffix=".png")
    try:
        os.write(handle, raw)
    finally:
        os.close(handle)
    return path
