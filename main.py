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

# Этот роут для проверки "здоровья"
@app.route("/")
def index():
    return "Bot is running!"

# Главный роут для вебхука
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    # Эта функция синхронная, как любит Flask
    try:
        # Получаем данные из запроса
        update_data = request.get_json()
        
        # Создаем и запускаем асинхронную задачу для aiogram
        # Это самый надежный способ подружить Flask и asyncio
        asyncio.run(process_update(update_data))
        
        return jsonify(ok=True)
    except Exception as e:
        logging.error(f"Error in webhook: {e}")
        return jsonify(ok=False, error=str(e)), 500

async def process_update(data):
    """Асинхронная функция, которая делает всю работу с aiogram."""
    update = types.Update(**data)
    await dp.feed_update(bot=bot, update=update)