"""Settings. Locally put them in a .env file (PyCharm: Run > Edit Configurations > EnvFile, or just use .env)."""
import os
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:          # python-dotenv is optional
    pass

TZ = ZoneInfo("Asia/Tashkent")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Empty -> local SQLite file (great for PyCharm). Neon/Supabase/any Postgres URL -> shared cloud DB.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_PATH = os.getenv("SQLITE_PATH", "expenses.db")

# Webhook mode (free hosting). Render sets RENDER_EXTERNAL_URL automatically.
WEBHOOK_URL = (os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")      # Telegram echoes it in a header
TICK_KEY = os.getenv("TICK_KEY", "")                  # protects /tick (called by cron-job.org)
PORT = int(os.getenv("PORT", "10000"))

DEFAULT_REMIND = "18:00"          # daily reminder, Tashkent time
WEEKLY_HOUR = 20                  # weekly Excel report: Sunday 20:00 Tashkent
WEEKLY_WEEKDAY = 6                # Python weekday(): Monday=0 ... Sunday=6
LATE_GRACE_MIN = 180              # if the host was asleep, still send up to 3 h late, never later
