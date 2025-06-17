import os
import traceback
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- Конфигурация ---
try:
    from config import BOT_TOKEN
    from handlers import commands, media
except ImportError as e:
    raise ImportError(f"Не удалось импортировать модули. Проверь __init__.py и структуру проекта. Ошибка: {e}")

# --- Главное приложение Flask ---
app = Flask(__name__)

# --- Финальная, правильная логика вебхука ---
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def process_webhook():
    # --- СОЗДАЕМ ОБЪЕКТЫ ЗАНОВО ПРИ КАЖДОМ ВЫЗОВЕ ---
    # Это гарантирует, что у нас всегда свежая HTTP-сессия.
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(commands.router)
    dp.include_router(media.router)

    try:
        # Обрабатываем обновление
        update = types.Update(**request.json)
        await dp.feed_update(bot=bot, update=update)
        return jsonify({'ok': True}), 200
    except Exception as e:
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return 'Internal Server Error', 500

# Этот роут для проверки, что сервер жив
@app.route('/')
def index():
    return 'A-Vision Bot is running!', 200