import asyncio
import logging
import sys
import threading
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from flask import Flask

from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.media import router as media_router

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(commands_router)
dp.include_router(media_router)

app = Flask(__name__)

@app.route('/')
def index():
    return "A-Vision is alive!"

async def run_bot_polling():
    logger.info("Starting bot polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, timeout_seconds=30)

def run_bot_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot_polling())
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        loop.close()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot_in_thread)
    bot_thread.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)