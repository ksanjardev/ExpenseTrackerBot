"""Storage via SQLAlchemy: SQLite locally, any Postgres (Neon free tier) in production.

Every row carries user_id -> fully multi-user. Timestamps are stored as naive Tashkent local time
strings 'YYYY-MM-DDTHH:MM:SS' (sortable and portable across SQLite/Postgres).
All functions are synchronous; the bot calls them through `acall` (thread) so the event loop never blocks.
"""
import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import (BigInteger, Column, Integer, MetaData, String, Table, Text, create_engine,
                        delete, insert, select, update, and_, or_)

import config

TZ = config.TZ
FMT = "%Y-%m-%dT%H:%M:%S"

metadata = MetaData()
users = Table(
    "users", metadata,
    Column("user_id", BigInteger, primary_key=True, autoincrement=False),
    Column("chat_id", BigInteger, nullable=False),
    Column("name", String(200)),
    Column("lang", String(5), nullable=False, default="uz"),
    Column("lang_chosen", Integer, nullable=False, default=0),
    Column("remind_time", String(5), default=config.DEFAULT_REMIND),   # 'HH:MM', NULL = off
    Column("active", Integer, nullable=False, default=1),
    Column("last_reminded", String(10)),                               # 'YYYY-MM-DD'
    Column("last_weekly", String(10)),
)
expenses = Table(
    "expenses", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, nullable=False, index=True),
    Column("item", Text, nullable=False),
    Column("amount", BigInteger, nullable=False),
    Column("cat", String(40)),                                         # 'daily.clothing' or NULL = unknown
    Column("ts", String(19), nullable=False, index=True),
)
rules = Table(
    "user_rules", metadata,
    Column("user_id", BigInteger, primary_key=True, autoincrement=False),
    Column("key", String(120), primary_key=True),
    Column("cat", String(40), nullable=False),
)

_engine = None


def engine():
    global _engine
    if _engine is None:
        url = config.DATABASE_URL
        if not url:
            _engine = create_engine(f"sqlite:///{config.SQLITE_PATH}")
        else:
            if url.startswith("postgres://"):
                url = "postgresql://" + url[len("postgres://"):]
            if url.startswith("postgresql://"):
                url = "postgresql+psycopg://" + url[len("postgresql://"):]
            # pre_ping/recycle: serverless Postgres (Neon) suspends idle compute and drops connections
            _engine = create_engine(url, pool_pre_ping=True, pool_recycle=240, pool_size=3, max_overflow=2)
    return _engine


async def acall(fn, *a, **kw):
    return await asyncio.to_thread(fn, *a, **kw)


def now() -> datetime:
    return datetime.now(TZ)


def stamp(dt: datetime) -> str:
    return dt.astimezone(TZ).strftime(FMT)


def init() -> None:
    metadata.create_all(engine())


def _row(r):
    return dict(r._mapping) if r is not None else None


# ----------------------------------------------------------------------------- users
def upsert_user(user_id: int, chat_id: int, name: str) -> dict:
    with engine().begin() as c:
        row = c.execute(select(users).where(users.c.user_id == user_id)).first()
        if row is None:
            c.execute(insert(users).values(user_id=user_id, chat_id=chat_id, name=name, lang="uz",
                                           lang_chosen=0, remind_time=config.DEFAULT_REMIND, active=1))
        else:
            c.execute(update(users).where(users.c.user_id == user_id)
                      .values(chat_id=chat_id, name=name, active=1))
        return _row(c.execute(select(users).where(users.c.user_id == user_id)).first())


def get_user(user_id: int) -> Optional[dict]:
    with engine().connect() as c:
        return _row(c.execute(select(users).where(users.c.user_id == user_id)).first())


def active_users() -> list:
    with engine().connect() as c:
        return [_row(r) for r in c.execute(select(users).where(users.c.active == 1))]


def set_lang(user_id: int, lang: str) -> None:
    with engine().begin() as c:
        c.execute(update(users).where(users.c.user_id == user_id).values(lang=lang, lang_chosen=1))


def set_remind(user_id: int, hhmm: Optional[str]) -> None:
    with engine().begin() as c:
        c.execute(update(users).where(users.c.user_id == user_id).values(remind_time=hhmm))


def deactivate(user_id: int) -> None:
    with engine().begin() as c:
        c.execute(update(users).where(users.c.user_id == user_id).values(active=0))


def claim_reminder(user_id: int, today: str) -> bool:
    """Atomically mark today's reminder as sent. True only for the one caller that wins (no double sends)."""
    with engine().begin() as c:
        r = c.execute(update(users).where(and_(
            users.c.user_id == user_id,
            or_(users.c.last_reminded.is_(None), users.c.last_reminded != today)
        )).values(last_reminded=today))
        return r.rowcount == 1


def claim_weekly(user_id: int, today: str) -> bool:
    with engine().begin() as c:
        r = c.execute(update(users).where(and_(
            users.c.user_id == user_id,
            or_(users.c.last_weekly.is_(None), users.c.last_weekly != today)
        )).values(last_weekly=today))
        return r.rowcount == 1


# ----------------------------------------------------------------------------- expenses
def add_expense(user_id: int, item: str, amount: int, cat: Optional[str]) -> int:
    with engine().begin() as c:
        r = c.execute(insert(expenses).values(user_id=user_id, item=item[:500], amount=int(amount),
                                              cat=cat, ts=stamp(now())))
        return int(r.inserted_primary_key[0])


def get_expenses(user_id: int, start: Optional[datetime] = None, end: Optional[datetime] = None) -> list:
    q = select(expenses).where(expenses.c.user_id == user_id)
    if start is not None:
        q = q.where(expenses.c.ts >= stamp(start))
    if end is not None:
        q = q.where(expenses.c.ts < stamp(end))
    with engine().connect() as c:
        return [_row(r) for r in c.execute(q.order_by(expenses.c.ts, expenses.c.id))]


def get_expense(user_id: int, expense_id: int) -> Optional[dict]:
    with engine().connect() as c:
        return _row(c.execute(select(expenses).where(and_(expenses.c.id == expense_id,
                                                          expenses.c.user_id == user_id))).first())


def set_category(user_id: int, expense_id: int, cat: str) -> Optional[dict]:
    """Only touches the caller's own row (user_id check) - callback data can't be abused across users."""
    with engine().begin() as c:
        r = c.execute(update(expenses).where(and_(expenses.c.id == expense_id, expenses.c.user_id == user_id))
                      .values(cat=cat))
        if r.rowcount != 1:
            return None
    return get_expense(user_id, expense_id)


def delete_last(user_id: int) -> Optional[dict]:
    with engine().begin() as c:
        row = c.execute(select(expenses).where(expenses.c.user_id == user_id)
                        .order_by(expenses.c.id.desc()).limit(1)).first()
        if row:
            c.execute(delete(expenses).where(expenses.c.id == row.id))
        return _row(row)


# ----------------------------------------------------------------------------- learned rules
def get_rules(user_id: int) -> dict:
    with engine().connect() as c:
        return {r.key: r.cat for r in c.execute(select(rules).where(rules.c.user_id == user_id))}


def save_rule(user_id: int, key: str, cat: str) -> None:
    if not key:
        return
    key = key[:120]
    with engine().begin() as c:
        r = c.execute(update(rules).where(and_(rules.c.user_id == user_id, rules.c.key == key)).values(cat=cat))
        if r.rowcount == 0:
            c.execute(insert(rules).values(user_id=user_id, key=key, cat=cat))
