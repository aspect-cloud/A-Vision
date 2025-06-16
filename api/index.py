import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request, abort

from config import BOT_TOKEN, BOT_USERNAME
from handlers.commands import router as commands_router
from handlers.media import router as media_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Dispatcher setup
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(commands_router)
dp.include_router(media_router)

# Flask app setup
app = Flask(__name__)

# Vercel environment variables
VERCEL_URL = os.getenv('VERCEL_URL')
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'https://{VERCEL_URL}{WEBHOOK_PATH}'

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.model_validate_json(json_string)
        asyncio.run(dp.feed_update(bot, update))
        return '', 200
    else:
        abort(403)

@app.route('/')
def index():
    return 'A-Vision is alive!'

# Set webhook on startup
async def on_startup():
    logger.info(f'Setting webhook to {WEBHOOK_URL}')
    await bot.set_webhook(WEBHOOK_URL)

# Run on startup
if os.getenv('VERCEL_ENV') == 'production':
    asyncio.run(on_startup())
