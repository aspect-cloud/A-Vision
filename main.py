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

# --- Глобальные объекты, которые создаются ОДИН РАЗ ---
# Создаем и настраиваем Dispatcher один раз при старте.
# Это решает ошибку "Router is already attached".
dp = Dispatcher()
dp.include_router(commands.router)
dp.include_router(media.router)

# Создаем Flask приложение
app = Flask(__name__)


# --- Логика обработки запросов ---

@app.route("/")
def index():
    # Роут для проверки, что сервер жив
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """Синхронный обработчик, который запускает асинхронную задачу."""
    try:
        # Запускаем нашу асинхронную логику для каждого запроса
        asyncio.run(process_update(request.get_json()))
        return jsonify(ok=True)
    except Exception as e:
        logging.error(f"Error in webhook handler: {e}", exc_info=True)
        return jsonify(ok=False, error=str(e)), 500

async def process_update(update_data: dict):
    """
    Асинхронная функция, которая делает всю работу.
    Она создает временный объект Bot для каждого запроса,
    чтобы избежать проблем с event loop.
    """
    # Создаем НОВЫЙ объект Bot для каждого апдейта
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    update = types.Update(**update_data)
    
    try:
        # Используем наш ГЛОБАЛЬНЫЙ, уже настроенный Dispatcher
        await dp.feed_update(bot=bot, update=update)
    finally:
        # ВАЖНО: Закрываем сессию временного бота, чтобы не было утечек
        await bot.session.close()