import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request, abort

from config import BOT_TOKEN
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

# This is the webhook path that Telegram will send updates to.
# It's important to use the bot token in the path to ensure it's secret.
WEBHOOK_PATH = f'/{BOT_TOKEN}'

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """
    This endpoint processes incoming updates from Telegram.
    """
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.model_validate_json(json_string)
        asyncio.run(dp.feed_update(bot, update))
        return '', 200
    else:
        # Block requests that are not from Telegram
        abort(403)

@app.route('/')
def index():
    """
    A simple endpoint to confirm the app is running.
    """
    return 'A-Vision is alive!'