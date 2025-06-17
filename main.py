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

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """Синхронный обработчик, который запускает асинхронную логику."""
    try:
        asyncio.run(process_webhook(request.get_json()))
        return jsonify(ok=True)
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify(ok=False, error=str(e)), 500

async def process_webhook(update_data: dict):
    """
    Асинхронная функция, которая создает все объекты с нуля
    для каждого запроса, обеспечивая полную изоляцию.
    """
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Роутеры регистрируются здесь же
    dp.include_router(commands.router)
    dp.include_router(media.router)

    # Обработка апдейта
    update = types.Update(**update_data)
    await dp.feed_update(bot=bot, update=update)

    # ВАЖНО: Закрываем сессию бота после обработки, чтобы не было утечек
    await bot.session.close()