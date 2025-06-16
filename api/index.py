import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request, Response

# Assuming your config and handlers are in the parent directory
# Add the parent directory to the Python path
sys.path.append('..')

from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.media import router as media_router

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Bot setup
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(commands_router)
dp.include_router(media_router)

# Flask app setup
app = Flask(__name__)

# Webhook setup
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
VERCEL_URL = getenv('VERCEL_URL')
WEBHOOK_URL = f"https://{VERCEL_URL}{WEBHOOK_PATH}" if VERCEL_URL else ''

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    async def process_update():
        try:
            update_data = request.json
            update = Update.model_validate(update_data, context={"bot": bot})
            await dp.feed_update(bot=bot, update=update)
            return Response(status=200)
        except Exception as e:
            logger.error(f"Error in webhook: {e}")
            return Response(status=500)
    return asyncio.run(process_update())

@app.route('/')
def index():
    return "A-Vision is alive!"

# A one-time function to set the webhook
async def set_webhook():
    if not VERCEL_URL:
        logger.error('VERCEL_URL is not set. Cannot set webhook.')
        return
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f'Webhook set to {WEBHOOK_URL}')

# Vercel will call this app
# On the first deployment, you might need to manually call set_webhook
# or browse to a temporary endpoint that calls it.

# Example of a one-time setup endpoint (use with caution)
@app.route('/set_webhook')
def setup_webhook():
    async def _setup():
        await set_webhook()
        return 'Webhook has been set.'
    return asyncio.run(_setup())

@app.route('/delete_webhook')
def remove_webhook():
    async def _remove():
        await bot.delete_webhook()
        return 'Webhook has been deleted.'
    return asyncio.run(_remove())
