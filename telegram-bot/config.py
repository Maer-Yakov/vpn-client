"""Runtime settings and tariff rules.

Tokens, prices, and model ids come from the environment. Handlers ask this
module which models a tariff may use; they do not read os.environ themselves.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent

TARIFF_RANK = {"free": 0, "pro": 1, "unlimited": 2}


@dataclass(frozen=True)
class Tariff:
    code: str
    title: str
    text_limit: int | None
    image_limit: int
    price_stars: int
    model_keys: tuple[str, ...]

    def limit_for(self, kind: str) -> int | None:
        if kind == "text":
            return self.text_limit
        if kind == "image":
            return self.image_limit
        raise ValueError(f"unknown request kind: {kind}")


@dataclass(frozen=True)
class ModelChoice:
    key: str
    model_id: str
    title: str
    provider: str


def allowed(tariff: Tariff, kind: str, used: int) -> bool:
    """True when another request of this kind still fits today's quota.

    ``text_limit is None`` means unlimited text. Image quotas are separate and
    smaller: a picture is not covered by the text counter.
    """
    limit = tariff.limit_for(kind)
    if limit is None:
        return True
    return used < limit


def build_tariffs(pro_price: int, unlimited_price: int) -> dict[str, Tariff]:
    return {
        "free": Tariff("free", "Бесплатный", 10, 0, 0, ("basic",)),
        "pro": Tariff("pro", "Pro", 500, 50, pro_price, ("basic", "top")),
        "unlimited": Tariff(
            "unlimited",
            "Безлимит",
            None,
            300,
            unlimited_price,
            ("basic", "top", "anthropic"),
        ),
    }


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_id: int
    openai_api_key: str
    openai_base_url: str | None
    anthropic_api_key: str
    anthropic_model: str
    image_api_key: str
    image_base_url: str | None
    image_model: str
    basic_model: str
    top_model: str
    pro_price_stars: int
    unlimited_price_stars: int
    db_path: Path
    tariffs: dict[str, Tariff]
    max_prompt_length: int = 4000
    context_limit: int = 10
    rate_limit_seconds: float = 3.0
    subscription_days: int = 30

    def text_models(self, tariff: Tariff) -> list[ModelChoice]:
        catalog = {
            "basic": ModelChoice("basic", self.basic_model, "Базовая", "openai"),
            "top": ModelChoice("top", self.top_model, "Топовая", "openai"),
            "anthropic": ModelChoice(
                "anthropic", self.anthropic_model, "Claude", "anthropic"
            ),
        }
        visible: list[ModelChoice] = []
        for key in tariff.model_keys:
            choice = catalog[key]
            if choice.provider == "openai" and not self.openai_api_key:
                continue
            if choice.provider == "anthropic" and not self.anthropic_api_key:
                continue
            visible.append(choice)
        return visible

    def image_enabled(self) -> bool:
        return bool(self.image_api_key)

    def resolve_model(self, tariff: Tariff, selected_key: str | None) -> ModelChoice | None:
        models = self.text_models(tariff)
        if not models:
            return None
        for model in models:
            if model.key == selected_key:
                return model
        return models[0]


_cached: Settings | None = None


def get_settings() -> Settings:
    global _cached
    if _cached is None:
        _cached = load_settings()
    return _cached


def load_settings() -> Settings:
    global _cached
    load_dotenv(ROOT / ".env")
    token = _env("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN не задан. Скопируйте .env.example в .env и укажите токен бота."
        )
    pro_price = _env_int("PRO_PRICE_STARS", 500)
    unlimited_price = _env_int("UNLIMITED_PRICE_STARS", 1500)
    if pro_price <= 0 or unlimited_price <= 0:
        raise RuntimeError("PRO_PRICE_STARS и UNLIMITED_PRICE_STARS должны быть больше нуля.")
    db_raw = _env("DB_PATH") or "bot.db"
    db_path = Path(db_raw)
    if not db_path.is_absolute():
        db_path = ROOT / db_path
    openai_base = _env("OPENAI_BASE_URL") or None
    image_base = _env("IMAGE_BASE_URL") or openai_base
    _cached = Settings(
        bot_token=token,
        admin_id=_env_int("ADMIN_ID", 0),
        openai_api_key=_env("OPENAI_API_KEY"),
        openai_base_url=openai_base,
        anthropic_api_key=_env("ANTHROPIC_API_KEY"),
        anthropic_model=_env("ANTHROPIC_MODEL") or "claude-3-5-haiku-latest",
        image_api_key=_env("IMAGE_API_KEY"),
        image_base_url=image_base,
        image_model=_env("IMAGE_MODEL") or "dall-e-3",
        basic_model=_env("BASIC_TEXT_MODEL") or "gpt-4o-mini",
        top_model=_env("TOP_TEXT_MODEL") or "gpt-4o",
        pro_price_stars=pro_price,
        unlimited_price_stars=unlimited_price,
        db_path=db_path,
        tariffs=build_tariffs(pro_price, unlimited_price),
    )
    return _cached


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default
    return int(raw)
