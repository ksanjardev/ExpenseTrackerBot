"""Telegram handlers + due-job runner (daily reminders, Sunday weekly Excel). Multi-user, DB driven."""
import asyncio
import html
import logging
import re
from datetime import datetime, timedelta

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Forbidden, TelegramError
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

import categories as C
import config
import db
import reports
from expense_parser import fmt_money, parse_message
from i18n import DEFAULT_LANG, LANGS, t

log = logging.getLogger("expense-bot")
PERIODS = ("today", "week", "month", "year")
FORMATS = ("img", "xlsx", "pdf", "txt")


# ----------------------------------------------------------------------------- helpers
def period_range(period: str):
    n = db.now()
    midnight = n.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "today":
        return midnight, None
    if period == "week":
        return n - timedelta(days=7), None
    if period == "month":
        return midnight.replace(day=1), None
    return midnight.replace(month=1, day=1), None          # year


def period_text(start: datetime, end=None) -> str:
    end = end or db.now()
    return f"{start:%d.%m.%Y} – {end:%d.%m.%Y}"


def _money(lang, n):
    return f"{fmt_money(n)} {t(lang, 'currency')}"


def _short(s: str, n=24) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


async def _user(update: Update):
    u = update.effective_user
    return await db.acall(db.upsert_user, u.id, update.effective_chat.id, u.full_name)


def lang_keyboard(prefix="lg", suffix="", mark=None):
    rows = [[InlineKeyboardButton(("✅ " if code == mark else "") + label, callback_data=f"{prefix}:{code}{suffix}")]
            for code, label in LANGS.items()]
    return InlineKeyboardMarkup(rows)


def cat_keyboard_groups(lang, exp_id):
    btns = [InlineKeyboardButton(g[C.LANG_IDX[lang]].capitalize()[:30], callback_data=f"cg:{exp_id}:{i}")
            for i, g in enumerate(C.GROUPS)]
    return InlineKeyboardMarkup([btns[i:i + 2] for i in range(0, len(btns), 2)])


def cat_keyboard_subs(lang, exp_id, gi):
    subs = C.GROUPS[gi][4]
    btns = [InlineKeyboardButton(s[C.LANG_IDX[lang]][:30], callback_data=f"cs:{exp_id}:{gi}:{si}")
            for si, s in enumerate(subs) if s[0] != "other2"]
    rows = [btns[i:i + 2] for i in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton(t(lang, "back"), callback_data=f"e:{exp_id}")])
    return InlineKeyboardMarkup(rows)


# ----------------------------------------------------------------------------- commands
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    if not u["lang_chosen"]:
        await update.effective_chat.send_message(t(DEFAULT_LANG, "choose_lang"), reply_markup=lang_keyboard(suffix=":w"))
        return
    await _welcome(update.effective_chat, u, update.effective_user.first_name)


async def _welcome(chat, u, first_name):
    await chat.send_message(t(u["lang"], "welcome", name=first_name, remind=u["remind_time"] or "—"), parse_mode="HTML")


async def lang_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    await update.effective_chat.send_message(t(u["lang"], "choose_lang"), reply_markup=lang_keyboard(mark=u["lang"]))


async def today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    rows = await db.acall(db.get_expenses, u["user_id"], period_range("today")[0])
    lang = u["lang"]
    if not rows:
        await update.message.reply_text(t(lang, "today_empty"))
        return
    lines = [f"{r['ts'][11:16]}  {r['item'] or t(lang, 'unnamed')} — {fmt_money(r['amount'])}" for r in rows]
    lines.append(f"\n{t(lang, 'today_total')}: {_money(lang, sum(r['amount'] for r in rows))}")
    await update.message.reply_text("\n".join(lines)[:4000])


async def undo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    row = await db.acall(db.delete_last, u["user_id"])
    lang = u["lang"]
    await update.message.reply_text(
        t(lang, "undo_done", item=row["item"] or t(lang, "unnamed"), amount=_money(lang, row["amount"]))
        if row else t(lang, "undo_none"))


async def remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    lang, arg = u["lang"], (ctx.args[0] if ctx.args else "").lower()
    if arg == "off":
        await db.acall(db.set_remind, u["user_id"], None)
        await update.message.reply_text(t(lang, "remind_off"))
    elif re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", arg):
        hhmm = f"{int(arg.split(':')[0]):02d}:{arg.split(':')[1]}"
        await db.acall(db.set_remind, u["user_id"], hhmm)
        await update.message.reply_text(t(lang, "remind_on", time=hhmm))
    else:
        await update.message.reply_text(t(lang, "remind_usage"))


async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    lang = u["lang"]
    kb = [[InlineKeyboardButton(t(lang, "periods")[k], callback_data=f"p:{k}")] for k in PERIODS]
    await update.message.reply_text(t(lang, "ask_period"), reply_markup=InlineKeyboardMarkup(kb))


# ----------------------------------------------------------------------------- expense messages
async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = await _user(update)
    if not u["lang_chosen"]:
        await start(update, ctx)
        return
    lang, uid = u["lang"], u["user_id"]
    parsed, failed = parse_message(update.message.text)
    if parsed:
        rules = await db.acall(db.get_rules, uid)
        lines, buttons, unknown = [], [], False
        for item, amount in parsed:
            cat = C.classify(item, rules)
            eid = await db.acall(db.add_expense, uid, item, amount, cat)
            name = html.escape(item or t(lang, "unnamed"))
            if cat:
                lines.append(f"✅ {name} — <b>{fmt_money(amount)}</b>\n      <i>{C.cat_label(lang, cat)}</i>")
            else:
                lines.append(f"❓ {name} — <b>{fmt_money(amount)}</b>")
                unknown = True
            if len(buttons) < 5:
                buttons.append([InlineKeyboardButton(f"{'🏷' if not cat else '✏️'} {_short(html.unescape(name))}",
                                                     callback_data=f"e:{eid}")])
        today_rows = await db.acall(db.get_expenses, uid, period_range("today")[0])
        lines.append(f"\n{t(lang, 'today_total')}: <b>{_money(lang, sum(r['amount'] for r in today_rows))}</b>")
        if unknown:
            lines.append(t(lang, "need_category"))
        await update.message.reply_html("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))
    for line in failed:
        await update.message.reply_html(t(lang, "no_price", line=html.escape(line[:80])))


# ----------------------------------------------------------------------------- callbacks
async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kind, *a = q.data.split(":")
    u = await db.acall(db.upsert_user, q.from_user.id, q.message.chat.id, q.from_user.full_name)
    lang = u["lang"]

    if kind == "lg":                                         # UI language chosen
        new = a[0] if a[0] in LANGS else DEFAULT_LANG
        await db.acall(db.set_lang, u["user_id"], new)
        u["lang"] = new
        await q.edit_message_text(t(new, "lang_set"))
        if len(a) > 1 and a[1] == "w":
            await _welcome(q.message.chat, u, q.from_user.first_name)

    elif kind == "p":                                        # period -> ask format
        period = a[0]
        kb = [[InlineKeyboardButton(t(lang, "formats")[k], callback_data=f"f:{k}:{period}") for k in FORMATS[:2]],
              [InlineKeyboardButton(t(lang, "formats")[k], callback_data=f"f:{k}:{period}") for k in FORMATS[2:]]]
        await q.edit_message_text(t(lang, "ask_format", period=t(lang, "periods")[period]),
                                  reply_markup=InlineKeyboardMarkup(kb))

    elif kind == "f":  # format chosen -> build & send in the user's language

        fmt, period = a

        await send_report(q, u, fmt, period, lang)

    elif kind == "x":                                        # language chosen -> build & send
        out_lang, fmt, period = a
        await send_report(q, u, fmt, period, out_lang if out_lang in LANGS else lang)

    elif kind == "e":                                        # (re)categorize expense: pick group
        exp = await db.acall(db.get_expense, u["user_id"], int(a[0]))
        if exp:
            await q.edit_message_text(
                f"{t(lang, 'ask_cat', item=exp['item'] or t(lang, 'unnamed'))}\n{t(lang, 'pick_group')}",
                reply_markup=cat_keyboard_groups(lang, exp["id"]))

    elif kind == "cg":                                       # group picked -> subcategories
        eid, gi = int(a[0]), int(a[1])
        await q.edit_message_text(t(lang, "pick_sub", group=C.GROUPS[gi][C.LANG_IDX[lang]].capitalize()),
                                  reply_markup=cat_keyboard_subs(lang, eid, gi))

    elif kind == "cs":                                       # sub picked -> save + learn
        eid, gi, si = int(a[0]), int(a[1]), int(a[2])
        cat = f"{C.GROUPS[gi][0]}.{C.GROUPS[gi][4][si][0]}"
        exp = await db.acall(db.set_category, u["user_id"], eid, cat)
        if exp:
            await db.acall(db.save_rule, u["user_id"], C.rule_key(exp["item"]), cat)
            await q.edit_message_text(t(lang, "cat_saved", item=exp["item"] or t(lang, "unnamed"),
                                        cat=C.cat_label(lang, cat)))


async def send_report(q, u, fmt, period, lang):
    start_dt, end_dt = period_range(period)
    rows = await db.acall(db.get_expenses, u["user_id"], start_dt, end_dt)
    if not rows:
        await q.edit_message_text(t(lang, "no_data"))
        return
    await q.edit_message_text(t(lang, "generating"))
    ptext = period_text(start_dt, end_dt)
    title = f"{t(lang, 'title')}: {t(lang, 'periods')[period]} ({ptext})"
    stamp = f"{db.now():%Y-%m-%d}"
    msg, prefix = q.message, t(lang, "file_prefix")
    if fmt == "txt":
        await msg.reply_text(reports.build_text(rows, title, lang))
    elif fmt == "img":
        await msg.reply_photo(await asyncio.to_thread(reports.build_image, rows, title, lang))
    elif fmt == "xlsx":
        buf = await asyncio.to_thread(reports.build_excel, rows, title, lang, ptext, db.now().year)
        await msg.reply_document(buf, filename=f"{prefix}_{stamp}.xlsx")
    elif fmt == "pdf":
        await msg.reply_document(await asyncio.to_thread(reports.build_pdf, rows, title, lang),
                                 filename=f"{prefix}_{stamp}.pdf")
    await q.delete_message()


# ----------------------------------------------------------------------------- scheduled work
def _due(now: datetime, hhmm: str) -> bool:
    """True from hh:mm until LATE_GRACE_MIN later (covers a host that was asleep at the exact minute)."""
    h, m = map(int, hhmm.split(":"))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    return 0 <= (now - target).total_seconds() / 60 <= config.LATE_GRACE_MIN


async def run_due(bot) -> dict:
    """Idempotent: safe to call every minute from JobQueue (polling) or from the /tick URL (webhook).
    The claim_* DB updates guarantee each user gets each message at most once per day."""
    n = db.now()
    today_s = n.strftime("%Y-%m-%d")
    sent = {"reminders": 0, "weekly": 0}
    is_weekly_time = n.weekday() == config.WEEKLY_WEEKDAY and _due(n, f"{config.WEEKLY_HOUR:02d}:00")

    for u in await db.acall(db.active_users):
        uid, chat, lang = u["user_id"], u["chat_id"], u["lang"]
        try:
            if u["remind_time"] and u["last_reminded"] != today_s and _due(n, u["remind_time"]):
                if await db.acall(db.claim_reminder, uid, today_s):
                    await bot.send_message(chat, t(lang, "reminder"), parse_mode="HTML")
                    sent["reminders"] += 1
            if is_weekly_time and u["last_weekly"] != today_s:
                if await db.acall(db.claim_weekly, uid, today_s):
                    rows = await db.acall(db.get_expenses, uid, n - timedelta(days=7))
                    if rows:
                        start_dt = n - timedelta(days=7)
                        title = f"{t(lang, 'title')}: {t(lang, 'periods')['week']} ({period_text(start_dt, n)})"
                        buf = await asyncio.to_thread(reports.build_excel, rows, title, lang,
                                                      period_text(start_dt, n), n.year)
                        await bot.send_document(
                            chat, buf, filename=f"{t(lang, 'weekly_prefix')}_{today_s}.xlsx",
                            caption=t(lang, "weekly_caption", total=_money(lang, sum(r['amount'] for r in rows))))
                        sent["weekly"] += 1
        except Forbidden:                                   # user blocked the bot
            await db.acall(db.deactivate, uid)
        except TelegramError:
            log.exception("send failed for %s", uid)
        except Exception:
            log.exception("scheduled job failed for %s", uid)
        await asyncio.sleep(0.05)                           # far below Telegram's ~30 msg/s limit
    return sent


async def tick_job(ctx: ContextTypes.DEFAULT_TYPE):
    await run_due(ctx.bot)


# ----------------------------------------------------------------------------- app factory
async def setup_commands(app: Application):
    for code in LANGS:
        cmds = [BotCommand(k, t(code, "cmds")[k]) for k in ("stats", "today", "undo", "remind", "lang", "start")]
        await app.bot.set_my_commands(cmds, language_code=None if code == DEFAULT_LANG else code)


def build_app(token: str, webhook: bool) -> Application:
    b = Application.builder().token(token).concurrent_updates(True)
    if webhook:
        b = b.updater(None)                                 # updates arrive through our own HTTP endpoint
    app = b.build()
    private = filters.ChatType.PRIVATE
    app.add_handler(CommandHandler("start", start, filters=private))
    app.add_handler(CommandHandler("lang", lang_cmd, filters=private))
    app.add_handler(CommandHandler("stats", stats, filters=private))
    app.add_handler(CommandHandler("today", today, filters=private))
    app.add_handler(CommandHandler("undo", undo, filters=private))
    app.add_handler(CommandHandler("remind", remind, filters=private))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & private, on_text))
    return app

