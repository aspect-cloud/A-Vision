# main.py

import os
import logging
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import commands, media
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

# Инициализируем Flask, Aiogram Bot и Dispatcher
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрируем роутеры из твоих файлов
dp.include_router(commands.router)
dp.include_router(media.router)

# Путь для вебхука
WEBHOOK_PATH = f"/webhook"

# Этот роут будет отвечать на GET запросы, чтобы Vercel не падал с ошибкой 500
@app.route("/")
def index():
    return "Bot is running!"

# Главный роут для приема апдейтов от Telegram
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    json_update = await request.get_json()
    update = types.Update(**json_update)
    await dp.feed_update(bot=bot, update=update)
    return jsonify(ok=True)

# Этот блок нужен для локального запуска, на Vercel он не выполняется,
# но позволяет один раз установить вебхук, если запустить локально.
if __name__ == "__main__":
    # ВАЖНО: Вебхук нужно будет установить вручную через браузер!
    # Этот код здесь для справки.
    pass