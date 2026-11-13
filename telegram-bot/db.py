"""SQLite access. All SQL lives here so Postgres can replace this module later.

Timestamps are UTC ISO-8601 strings (``2026-11-13T00:00:00+00:00``). Lexical
order matches chronological order, which is what the daily limit query relies on.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite

from config import TARIFF_RANK

_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        selected_model TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        tariff TEXT NOT NULL,
        starts_at TEXT NOT NULL,
        ends_at TEXT NOT NULL,
        stars_paid INTEGER NOT NULL DEFAULT 0,
        charge_id TEXT UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        model TEXT NOT NULL,
        type TEXT NOT NULL,
        charged INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_requests_usage
        ON requests(user_id, type, charged, created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_subscriptions_user
        ON subscriptions(user_id, ends_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_messages_user
        ON messages(user_id, id)
    """,
)


@dataclass(frozen=True)
class UserRecord:
    user_id: int
    username: str | None
    first_name: str | None
    selected_model: str | None
    created_at: str


@dataclass(frozen=True)
class Subscription:
    id: int
    user_id: int
    tariff: str
    starts_at: str
    ends_at: str
    stars_paid: int
    charge_id: str | None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_day_start(now: datetime | None = None) -> datetime:
    current = now or utc_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    return current.replace(hour=0, minute=0, second=0, microsecond=0)


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


class Database:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        for statement in _SCHEMA:
            await self._conn.execute(statement)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database.connect() was not called")
        return self._conn

    async def upsert_user(
        self,
        user_id: int,
        username: str | None,
        first_name: str | None,
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO users (user_id, username, first_name, selected_model, created_at)
            VALUES (?, ?, ?, NULL, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username, first_name, _iso(utc_now())),
        )
        await self.conn.commit()

    async def ensure_user(self, user_id: int) -> None:
        await self.conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
            VALUES (?, NULL, NULL, ?)
            """,
            (user_id, _iso(utc_now())),
        )
        await self.conn.commit()

    async def get_user(self, user_id: int) -> UserRecord | None:
        cursor = await self.conn.execute(
            """
            SELECT user_id, username, first_name, selected_model, created_at
            FROM users WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return UserRecord(
            user_id=row["user_id"],
            username=row["username"],
            first_name=row["first_name"],
            selected_model=row["selected_model"],
            created_at=row["created_at"],
        )

    async def set_selected_model(self, user_id: int, model_key: str) -> None:
        await self.ensure_user(user_id)
        await self.conn.execute(
            "UPDATE users SET selected_model = ? WHERE user_id = ?",
            (model_key, user_id),
        )
        await self.conn.commit()

    async def count_users(self) -> int:
        cursor = await self.conn.execute("SELECT COUNT(*) AS n FROM users")
        row = await cursor.fetchone()
        return int(row["n"])

    async def effective_tariff_code(self, user_id: int, now: datetime | None = None) -> str:
        current = now or utc_now()
        cursor = await self.conn.execute(
            """
            SELECT tariff FROM subscriptions
            WHERE user_id = ? AND ends_at > ?
            """,
            (user_id, _iso(current)),
        )
        rows = await cursor.fetchall()
        if not rows:
            return "free"
        return max((row["tariff"] for row in rows), key=lambda code: TARIFF_RANK.get(code, 0))

    async def subscription_end(
        self,
        user_id: int,
        tariff: str,
        now: datetime | None = None,
    ) -> str | None:
        current = now or utc_now()
        cursor = await self.conn.execute(
            """
            SELECT MAX(ends_at) AS ends_at FROM subscriptions
            WHERE user_id = ? AND tariff = ? AND ends_at > ?
            """,
            (user_id, tariff, _iso(current)),
        )
        row = await cursor.fetchone()
        if row is None or row["ends_at"] is None:
            return None
        return str(row["ends_at"])

    async def grant_subscription(
        self,
        user_id: int,
        tariff: str,
        *,
        days: int = 30,
        stars_paid: int = 0,
        charge_id: str | None = None,
        now: datetime | None = None,
    ) -> Subscription:
        """Activate a tariff for ``days`` days.

        The same Telegram charge id is applied once. A repeat purchase of a
        tariff that is still active adds ``days`` to its current end, so the
        paid time already on the account is kept.
        """
        if charge_id:
            existing = await self._subscription_by_charge(charge_id)
            if existing is not None:
                return existing
        await self.ensure_user(user_id)
        current = now or utc_now()
        active_end = await self.subscription_end(user_id, tariff, current)
        start = current
        if active_end is not None:
            end = datetime.fromisoformat(active_end) + timedelta(days=days)
        else:
            end = current + timedelta(days=days)
        try:
            cursor = await self.conn.execute(
                """
                INSERT INTO subscriptions
                    (user_id, tariff, starts_at, ends_at, stars_paid, charge_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, tariff, _iso(start), _iso(end), stars_paid, charge_id),
            )
            await self.conn.commit()
        except sqlite3.IntegrityError:
            await self.conn.rollback()
            if charge_id:
                raced = await self._subscription_by_charge(charge_id)
                if raced is not None:
                    return raced
            raise
        created = await self._subscription_by_id(int(cursor.lastrowid))
        if created is None:
            raise RuntimeError("subscription insert was not readable")
        return created

    async def usage_today(self, user_id: int, kind: str, now: datetime | None = None) -> int:
        """Charged requests since 00:00 UTC. Yesterday does not count."""
        return await self.count_usage(user_id, kind, utc_day_start(now))

    async def count_usage(self, user_id: int, kind: str, since: datetime) -> int:
        cursor = await self.conn.execute(
            """
            SELECT COUNT(*) AS n FROM requests
            WHERE user_id = ? AND type = ? AND charged = 1 AND created_at >= ?
            """,
            (user_id, kind, _iso(since)),
        )
        row = await cursor.fetchone()
        return int(row["n"])

    async def count_requests_since(self, since: datetime) -> int:
        cursor = await self.conn.execute(
            "SELECT COUNT(*) AS n FROM requests WHERE created_at >= ?",
            (_iso(since),),
        )
        row = await cursor.fetchone()
        return int(row["n"])

    async def log_request(
        self,
        user_id: int,
        model: str,
        kind: str,
        *,
        charged: bool,
        at: datetime | None = None,
    ) -> None:
        await self.ensure_user(user_id)
        moment = at or utc_now()
        await self.conn.execute(
            """
            INSERT INTO requests (user_id, model, type, charged, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, model, kind, 1 if charged else 0, _iso(moment)),
        )
        await self.conn.commit()

    async def add_message(self, user_id: int, role: str, content: str, *, keep: int = 10) -> None:
        await self.ensure_user(user_id)
        await self.conn.execute(
            """
            INSERT INTO messages (user_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, role, content[:16000], _iso(utc_now())),
        )
        await self.conn.execute(
            """
            DELETE FROM messages
            WHERE user_id = ?
              AND id NOT IN (
                  SELECT id FROM (
                      SELECT id FROM messages
                      WHERE user_id = ?
                      ORDER BY id DESC
                      LIMIT ?
                  )
              )
            """,
            (user_id, user_id, keep),
        )
        await self.conn.commit()

    async def recent_messages(self, user_id: int, limit: int = 10) -> list[dict[str, str]]:
        cursor = await self.conn.execute(
            """
            SELECT role, content FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    async def _subscription_by_charge(self, charge_id: str) -> Subscription | None:
        cursor = await self.conn.execute(
            """
            SELECT id, user_id, tariff, starts_at, ends_at, stars_paid, charge_id
            FROM subscriptions WHERE charge_id = ?
            """,
            (charge_id,),
        )
        row = await cursor.fetchone()
        return _subscription_from_row(row) if row is not None else None

    async def _subscription_by_id(self, subscription_id: int) -> Subscription | None:
        cursor = await self.conn.execute(
            """
            SELECT id, user_id, tariff, starts_at, ends_at, stars_paid, charge_id
            FROM subscriptions WHERE id = ?
            """,
            (subscription_id,),
        )
        row = await cursor.fetchone()
        return _subscription_from_row(row) if row is not None else None


def _subscription_from_row(row: aiosqlite.Row) -> Subscription:
    return Subscription(
        id=row["id"],
        user_id=row["user_id"],
        tariff=row["tariff"],
        starts_at=row["starts_at"],
        ends_at=row["ends_at"],
        stars_paid=row["stars_paid"],
        charge_id=row["charge_id"],
    )
