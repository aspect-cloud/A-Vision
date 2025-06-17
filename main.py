# main.py

import os
import logging
import asyncio
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import commands, media
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(commands.router)
dp.include_router(media.router)

WEBHOOK_PATH = f"/webhook"

@app.route("/")
def index():
    return "Bot is running!"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update_data = request.get_json()
    
    # Более надежный способ управления циклом событий
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Запускаем нашу асинхронную задачу в существующем или новом цикле
    loop.run_until_complete(process_update(update_data))
    
    return jsonify(ok=True)

async def process_update(data):
    update = types.Update(**data)
    await dp.feed_update(bot=bot, update=update)