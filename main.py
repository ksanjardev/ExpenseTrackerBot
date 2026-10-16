"""Entry point.
  * No WEBHOOK_URL  -> long polling (PyCharm / any always-on machine). Reminders run via JobQueue.
  * WEBHOOK_URL set -> small ASGI server (free hosts such as Render): /telegram receives updates,
                       /tick (hit every 5 min by cron-job.org) sends due reminders/weekly reports.
"""
import asyncio
import contextlib
import hashlib
import hmac
import logging

from telegram import Update

import bot
import config
import db

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
log = logging.getLogger("expense-bot")


def run_polling():
    app = bot.build_app(config.BOT_TOKEN, webhook=False)

    async def post_init(a):
        await bot.setup_commands(a)

    app.post_init = post_init
    app.job_queue.run_repeating(bot.tick_job, interval=60, first=15, name="tick")
    log.info("polling mode, DB: %s", "Postgres" if config.DATABASE_URL else config.SQLITE_PATH)

    async def on_error(update, context):
        log.warning("telegram error: %s", context.error)

    app.add_error_handler(on_error)
    app.run_polling(drop_pending_updates=False)


def make_asgi():
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse, PlainTextResponse, Response
    from starlette.routing import Route

    secret = config.WEBHOOK_SECRET or hashlib.sha256(("wh" + config.BOT_TOKEN).encode()).hexdigest()[:40]
    app = bot.build_app(config.BOT_TOKEN, webhook=True)

    @contextlib.asynccontextmanager
    async def lifespan(_):
        async with app:
            await bot.setup_commands(app)
            await app.start()
            await app.bot.set_webhook(f"{config.WEBHOOK_URL}/telegram", secret_token=secret,
                                      allowed_updates=Update.ALL_TYPES)
            log.info("webhook set -> %s/telegram", config.WEBHOOK_URL)
            yield
            await app.stop()

    async def telegram(request: Request):
        if not hmac.compare_digest(request.headers.get("X-Telegram-Bot-Api-Secret-Token", ""), secret):
            return Response(status_code=403)
        await app.update_queue.put(Update.de_json(await request.json(), app.bot))
        return Response()                                   # answer fast; handlers run in the background

    state = {"task": None}

    async def tick(request: Request):
        if not config.TICK_KEY:
            return PlainTextResponse("TICK_KEY is not configured", status_code=503)
        if not hmac.compare_digest(request.query_params.get("key", ""), config.TICK_KEY):
            return Response(status_code=403)
        if request.query_params.get("wait") == "1":          # handy for manual testing in a browser
            return JSONResponse(await bot.run_due(app.bot))
        task = state["task"]
        if task is not None and not task.done():             # previous tick still sending -> don't overlap
            return JSONResponse({"status": "busy"})
        state["task"] = asyncio.create_task(bot.run_due(app.bot))
        return JSONResponse({"status": "started"})

    async def health(request: Request):
        return PlainTextResponse("ok")

    return Starlette(routes=[Route("/telegram", telegram, methods=["POST"]),
                             Route("/tick", tick, methods=["GET", "POST"]),
                             Route("/", health, methods=["GET", "HEAD"])], lifespan=lifespan)


def main():
    if not config.BOT_TOKEN:
        raise SystemExit("Set BOT_TOKEN (see .env.example)")
    db.init()
    if config.WEBHOOK_URL:
        import uvicorn
        if not config.TICK_KEY:
            log.warning("TICK_KEY not set: /tick is disabled, reminders and weekly reports will NOT be sent")
        uvicorn.run(make_asgi(), host="0.0.0.0", port=config.PORT, log_level="info")
    else:
        run_polling()


if __name__ == "__main__":
    main()
