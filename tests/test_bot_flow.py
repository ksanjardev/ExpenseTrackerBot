"""Drives the real handlers with fake Telegram objects (no network)."""
import asyncio
from datetime import datetime
from types import SimpleNamespace as NS

import pytest
from starlette.testclient import TestClient

import bot
import config
import db as dbmod


class Chat:
    id = 7

    def __init__(self): self.sent = []
    async def send_message(self, text, **kw): self.sent.append((text, kw))


class Msg:
    def __init__(self, text=""):
        self.text, self.sent, self.chat = text, [], Chat()

    async def reply_html(self, text, **kw): self.sent.append(("html", text, kw))
    async def reply_text(self, text, **kw): self.sent.append(("text", text, kw))
    async def reply_document(self, doc, filename=None, **kw): self.sent.append(("doc", filename, doc))
    async def reply_photo(self, p, **kw): self.sent.append(("photo", p, kw))
    async def delete(self): pass


class Query:
    def __init__(self, data, user, msg):
        self.data, self.from_user, self.message, self.edits = data, user, msg, []

    async def answer(self): pass
    async def edit_message_text(self, text, **kw): self.edits.append((text, kw))
    async def delete_message(self): pass


USER = NS(id=555, full_name="Sanjar", first_name="Sanjar")


def upd(text=None):
    chat, m = Chat(), Msg(text or "")
    return NS(effective_user=USER, effective_chat=chat, message=m), chat, m


def cb(data):
    m = Msg()
    q = Query(data, USER, m)
    return NS(callback_query=q), q, m


def run(c):
    return asyncio.run(c)


def test_full_user_journey(fresh_db):
    ctx = NS(args=[], application=None)
    # new user: language picker first
    u, chat, _ = upd(); run(bot.start(u, ctx))
    assert "Tilni tanlang" in chat.sent[0][0]
    u, q, m = cb("lg:ru:w"); run(bot.on_callback(u, ctx))
    assert "Русский" in q.edits[0][0]
    # expense messages (Russian UI)
    u, chat, m = upd("10 пар носков 13k\nqwerty zxcv 5000\nпросто текст"); run(bot.on_text(u, ctx))
    kinds = [s[0] for s in m.sent]
    assert kinds.count("html") == 2                                     # confirmation + "no price" notice
    confirm = m.sent[0][1]
    assert "13 000" in confirm and "Одежда" in confirm and "❓ qwerty zxcv" in confirm
    rows = fresh_db.get_expenses(555)
    assert [(r["item"], r["amount"], r["cat"]) for r in rows] == \
           [("10 пар носков", 13000, "daily.clothing"), ("qwerty zxcv", 5000, None)]
    # categorize the unknown one: group -> sub -> saved and learned
    eid = rows[1]["id"]
    u, q, _ = cb(f"e:{eid}"); run(bot.on_callback(u, ctx)); assert "qwerty zxcv" in q.edits[0][0]
    gi = [g[0] for g in bot.C.GROUPS].index("fun")
    u, q, _ = cb(f"cg:{eid}:{gi}"); run(bot.on_callback(u, ctx))
    u, q, _ = cb(f"cs:{eid}:{gi}:4"); run(bot.on_callback(u, ctx))
    assert fresh_db.get_expense(555, eid)["cat"] == "fun.hobbies"
    u, chat, m = upd("3 qwerty zxcv 9k"); run(bot.on_text(u, ctx))
    assert fresh_db.get_expenses(555)[-1]["cat"] == "fun.hobbies"       # learned
    # stats flow: period -> format -> language -> file
    u, q, _ = cb("p:year"); run(bot.on_callback(u, ctx)); assert len(q.edits[0][1]["reply_markup"].inline_keyboard) == 2
    u, q, _ = cb("f:xlsx:year"); run(bot.on_callback(u, ctx))
    assert [b.callback_data for r in q.edits[0][1]["reply_markup"].inline_keyboard for b in r] == \
           ["x:uz:xlsx:year", "x:ru:xlsx:year", "x:en:xlsx:year"]
    for fmt in ("xlsx", "pdf", "img", "txt"):
        u, q, m = cb(f"x:uz:{fmt}:year"); run(bot.on_callback(u, ctx))
        assert m.sent and m.sent[0][0] in ("doc", "photo", "text"), fmt
    u, q, m = cb("x:uz:xlsx:today"); run(bot.on_callback(u, ctx))
    # /today /undo /remind
    u, chat, m = upd(); run(bot.today(u, ctx)); assert "13 000" in m.sent[0][1]
    ctx.args = ["19:30"]; u, chat, m = upd(); run(bot.remind(u, ctx)); assert "19:30" in m.sent[0][1]
    assert fresh_db.get_user(555)["remind_time"] == "19:30"
    ctx.args = ["off"]; u, chat, m = upd(); run(bot.remind(u, ctx)); assert fresh_db.get_user(555)["remind_time"] is None
    u, chat, m = upd(); run(bot.undo(u, ctx)); assert "Удалено" in m.sent[0][1]


class FakeBot:
    def __init__(self): self.msgs, self.docs = [], []
    async def send_message(self, chat, text, **kw): self.msgs.append((chat, text))
    async def send_document(self, chat, buf, filename=None, caption=None, **kw): self.docs.append((chat, filename, caption))


def _at(monkeypatch, y, mo, d, h, mi):
    monkeypatch.setattr(dbmod, "now", lambda: datetime(y, mo, d, h, mi, tzinfo=config.TZ))


def test_scheduler_daily_and_weekly(fresh_db, monkeypatch):
    for uid, lang in ((1, "uz"), (2, "ru")):
        fresh_db.upsert_user(uid, uid, f"U{uid}"); fresh_db.set_lang(uid, lang)
    fresh_db.upsert_user(3, 3, "Off"); fresh_db.set_remind(3, None)
    fresh_db.upsert_user(4, 4, "Late"); fresh_db.set_remind(4, "21:00")
    fresh_db.add_expense(1, "taksi", 25000, "transport.fare")
    fb = FakeBot()

    _at(monkeypatch, 2026, 10, 16, 17, 59)                                  # Friday before 18:00
    assert run(bot.run_due(fb)) == {"reminders": 0, "weekly": 0}
    _at(monkeypatch, 2026, 10, 16, 18, 2)                                   # 18:02 tick
    assert run(bot.run_due(fb)) == {"reminders": 2, "weekly": 0}
    assert {c for c, _ in fb.msgs} == {1, 2} and "Bugun nimalarga" in dict(fb.msgs)[1]
    _at(monkeypatch, 2026, 10, 16, 18, 7)                                   # next tick: no duplicates
    assert run(bot.run_due(fb)) == {"reminders": 0, "weekly": 0}
    _at(monkeypatch, 2026, 10, 16, 21, 1)                                   # user 4 asked for 21:00
    assert run(bot.run_due(fb)) == {"reminders": 1, "weekly": 0}

    fb2 = FakeBot()                                                          # Sunday 2026-10-18
    _at(monkeypatch, 2026, 10, 18, 19, 55); assert run(bot.run_due(fb2))["weekly"] == 0
    _at(monkeypatch, 2026, 10, 18, 20, 3)
    res = run(bot.run_due(fb2))
    assert res["weekly"] == 1 and fb2.docs[0][0] == 1 and fb2.docs[0][1].startswith("haftalik_")   # only users with data
    _at(monkeypatch, 2026, 10, 18, 20, 8); assert run(bot.run_due(fb2))["weekly"] == 0
    _at(monkeypatch, 2026, 10, 19, 20, 3); assert run(bot.run_due(FakeBot()))["weekly"] == 0       # Monday: no
    # host was asleep until 23:30 -> too late for the 18:00 reminder (grace is 3 h), never spams at night
    fresh_db.upsert_user(9, 9, "Z"); fb3 = FakeBot(); _at(monkeypatch, 2026, 10, 20, 23, 30)
    run(bot.run_due(fb3))
    assert {c for c, _ in fb3.msgs} == {4}          # only the 21:00 user (inside its grace window)


def test_blocked_user_is_deactivated(fresh_db, monkeypatch):
    from telegram.error import Forbidden
    fresh_db.upsert_user(1, 1, "B")

    class Blocked(FakeBot):
        async def send_message(self, *a, **k): raise Forbidden("blocked")
    _at(monkeypatch, 2026, 10, 16, 18, 5)
    run(bot.run_due(Blocked()))
    assert fresh_db.active_users() == []


def test_http_endpoints(fresh_db, monkeypatch):
    import main
    monkeypatch.setattr(config, "BOT_TOKEN", "123:ABC"); monkeypatch.setattr(config, "TICK_KEY", "k3y")
    monkeypatch.setattr(config, "WEBHOOK_URL", "https://x.example")
    app = main.make_asgi()
    c = TestClient(app)                                                       # no `with` -> lifespan/Telegram not touched
    assert c.get("/").text == "ok"
    assert c.get("/tick").status_code == 403 and c.get("/tick?key=nope").status_code == 403
    assert c.get("/tick?key=k3y&wait=1").json() == {"reminders": 0, "weekly": 0}
    assert c.get("/tick?key=k3y").json()["status"] in ("started", "busy")      # returns at once
    assert c.post("/telegram", json={"update_id": 1}).status_code == 403
    import hashlib
    secret = hashlib.sha256(("wh" + "123:ABC").encode()).hexdigest()[:40]
    r = c.post("/telegram", json={"update_id": 1}, headers={"X-Telegram-Bot-Api-Secret-Token": secret})
    assert r.status_code == 200
