# Expense bot (Telegram) — multi-user, uz / ru / en

Users write `10 ta paypoq oldim 13k` → the bot splits **what** (`10 ta paypoq oldim`) and **how much** (`13 000`),
files it under one of the template's categories (Clothing), and:

* reminds every user daily at **18:00 Tashkent time** (`/remind 19:30` or `/remind off` to change it),
* sends a **weekly Excel** every **Sunday 20:00**,
* `/stats` → period → format (**image / Excel / PDF / text**) → **language of the file** (uz / ru / en).

## Where things are

| File | Purpose |
|---|---|
| `assets/personal-budget-template.xlsx` | **Your Vertex42 template.** Keep it here, in the project. The code opens a fresh copy for every report, localizes it and fills the month columns. The original file is never modified. |
| `categories.py` | The 10 template categories (+ their rows) in uz/ru/en and the keyword rules that pick a category |
| `expense_parser.py` | "text + price" splitter (13k, 13 000, 1.5 mln, 45 ming …) |
| `reports.py` | text / PNG / PDF / Excel builders |
| `db.py` | SQLite locally, Postgres (Neon) in production — same code |
| `bot.py`, `main.py` | handlers, scheduler, webhook server |
| `tests/` | `python -m pytest` |

Your list had `OBLIGATIONS` twice; the template really has **10** category tables, so the bot uses 10.

## Run in PyCharm (5 minutes, no database setup)

1. Create the bot with @BotFather and copy the token.
2. `pip install -r requirements.txt` (Python 3.11+).
3. Copy `.env.example` to `.env`, set `BOT_TOKEN`.
4. Run `main.py`. Data goes to `expenses.db` (SQLite). Reminders run while the program is running.

## Deploy for free: Neon (database) + Render (host) + cron-job.org (clock)

1. **Neon** → new project → copy the connection string (`postgresql://…?sslmode=require`).
   Free plan: 1 GB per project, no credit card. Compute suspends after 5 min idle and wakes on the next query.
   (Don't use Render's free Postgres — it expires after 30 days.)
2. Push this folder to a GitHub repo. **Render** → New → Blueprint → pick the repo (`render.yaml` is included).
   Set `BOT_TOKEN` and `DATABASE_URL`. After the first deploy open the service's **Environment** tab and copy `TICK_KEY`.
3. **cron-job.org** (free) → new cron job, every **5 minutes**, URL
   `https://<your-service>.onrender.com/tick?key=<TICK_KEY>`.
   Why: a free Render service sleeps after 15 min without traffic, and a sleeping bot cannot send the 18:00
   reminder. The 5-minute ping keeps it awake and triggers due reminders / weekly reports. Each user gets each
   message at most once per day (it is recorded in the DB), and if the host was asleep, a reminder is still sent
   up to 3 hours late but never later.
4. Message your bot. Done.

One always-on free web service uses ~744 of Render's 750 free hours per month, so keep it to this one service.

## Categories

Unknown items: the bot saves the expense, shows buttons (group → sub-category), and **remembers the choice per
user**, so the same item is filed automatically next time. Wrong auto-pick? Tap the ✏️ button under the confirmation.
To teach the built-in rules a new word, add it to the matching `_r("group.sub", W(...))` line in `categories.py`.

## Excel details

* `Budget` sheet = your template: same tables, formulas, print setup; texts localized; the totals row formulas were
  re-pointed at the renamed table columns. Column widths were enlarged because amounts are in so'm (the original
  columns fit ~4 digits).
* Added after it: `Dashboard` (KPIs + 2 charts) and `Expenses` (raw rows, filterable). `Help` is translated
  (uz/ru); `©` is left as is.
* Month columns show the period's expenses (e.g. "last 7 days" fills only the current month's column).

## Notes

* Times are Tashkent (`config.TZ`). Currency label is so'm.
* The template carries a Vertex42 © sheet and a personal-use license note — check that licence before distributing
  the bot widely, or swap in your own template (same code works if the table/row order stays the same).
* Passwords/tokens live only in environment variables. The DB stores Telegram user id, first+last name, expenses.
