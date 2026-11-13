from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from config import Settings, allowed, build_tariffs
from db import Database


@pytest.fixture
async def db(tmp_path: Path):
    database = Database(tmp_path / "bot.db")
    await database.connect()
    try:
        yield database
    finally:
        await database.close()


def test_tariff_allowance() -> None:
    tariffs = build_tariffs(500, 1500)
    free = tariffs["free"]
    pro = tariffs["pro"]
    unlimited = tariffs["unlimited"]

    assert allowed(free, "text", 9)
    assert not allowed(free, "text", 10)
    assert not allowed(free, "image", 0)

    assert allowed(pro, "text", 499)
    assert not allowed(pro, "text", 500)
    assert allowed(pro, "image", 49)
    assert not allowed(pro, "image", 50)
    assert pro.image_limit < pro.text_limit

    assert allowed(unlimited, "text", 100_000)
    assert allowed(unlimited, "image", 299)
    assert not allowed(unlimited, "image", 300)

    assert free.model_keys == ("basic",)
    assert pro.model_keys == ("basic", "top")
    assert unlimited.model_keys == ("basic", "top", "anthropic")
    assert pro.price_stars == 500
    assert unlimited.price_stars == 1500


def test_missing_keys_hide_models(tmp_path: Path) -> None:
    tariffs = build_tariffs(500, 1500)
    settings = Settings(
        bot_token="test",
        admin_id=1,
        openai_api_key="",
        openai_base_url=None,
        anthropic_api_key="",
        anthropic_model="claude-3-5-haiku-latest",
        image_api_key="",
        image_base_url=None,
        image_model="dall-e-3",
        basic_model="gpt-4o-mini",
        top_model="gpt-4o",
        pro_price_stars=500,
        unlimited_price_stars=1500,
        db_path=tmp_path / "bot.db",
        tariffs=tariffs,
    )
    assert settings.text_models(tariffs["unlimited"]) == []
    assert settings.image_enabled() is False
    assert settings.resolve_model(tariffs["free"], "basic") is None

    with_openai = Settings(
        bot_token="test",
        admin_id=1,
        openai_api_key="sk-test",
        openai_base_url=None,
        anthropic_api_key="",
        anthropic_model="claude-3-5-haiku-latest",
        image_api_key="img",
        image_base_url=None,
        image_model="dall-e-3",
        basic_model="gpt-4o-mini",
        top_model="gpt-4o",
        pro_price_stars=500,
        unlimited_price_stars=1500,
        db_path=tmp_path / "bot.db",
        tariffs=tariffs,
    )
    visible = [model.key for model in with_openai.text_models(tariffs["unlimited"])]
    assert visible == ["basic", "top"]
    assert with_openai.image_enabled() is True
    assert with_openai.resolve_model(tariffs["free"], "top").key == "basic"


async def test_usage_resets_at_utc_midnight(db: Database) -> None:
    await db.ensure_user(1)
    just_before = datetime(2026, 11, 12, 23, 59, 59, tzinfo=timezone.utc)
    midnight = datetime(2026, 11, 13, 0, 0, 0, tzinfo=timezone.utc)
    morning = datetime(2026, 11, 13, 0, 30, tzinfo=timezone.utc)

    await db.log_request(1, "gpt-4o-mini", "text", charged=True, at=just_before)
    await db.log_request(1, "gpt-4o-mini", "text", charged=False, at=morning)
    await db.log_request(1, "dall-e-3", "image", charged=True, at=midnight)

    assert await db.usage_today(1, "text", now=morning) == 0
    assert await db.usage_today(1, "text", now=just_before) == 1
    assert await db.usage_today(1, "image", now=morning) == 1
    assert await db.count_requests_since(midnight) == 2


async def test_expired_subscription_falls_back_to_free(db: Database) -> None:
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    await db.grant_subscription(5, "pro", now=start, stars_paid=500, charge_id="pay-1")

    assert await db.effective_tariff_code(5, now=datetime(2026, 10, 15, tzinfo=timezone.utc)) == "pro"
    assert await db.effective_tariff_code(5, now=datetime(2026, 11, 13, tzinfo=timezone.utc)) == "free"


async def test_duplicate_payment_does_not_extend_twice(db: Database) -> None:
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    first = await db.grant_subscription(7, "pro", now=start, stars_paid=500, charge_id="chg-1")
    second = await db.grant_subscription(
        7,
        "pro",
        now=start + timedelta(days=1),
        stars_paid=500,
        charge_id="chg-1",
    )
    assert first.id == second.id
    assert second.ends_at == (start + timedelta(days=30)).isoformat()


async def test_higher_active_tariff_wins(db: Database) -> None:
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    await db.grant_subscription(4, "pro", now=start, charge_id="pro-1")
    await db.grant_subscription(4, "unlimited", now=start, charge_id="unl-1")
    assert await db.effective_tariff_code(4, now=start + timedelta(days=1)) == "unlimited"
