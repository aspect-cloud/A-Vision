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
    # Эта ошибка поможет при отладке, если структура папок неверна
    raise ImportError(f"Не удалось импортировать модули. Проверь __init__.py и структуру проекта. Ошибка: {e}")

# --- Инициализация ---
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(commands.router)
dp.include_router(media.router)

WEBHOOK_PATH = f'/{BOT_TOKEN}'

# --- Финальная, правильная логика вебхука ---
@app.route(WEBHOOK_PATH, methods=['POST'])
async def process_webhook():
    try:
        update = types.Update(**request.json)
        await dp.feed_update(bot=bot, update=update)
        # Если все хорошо, отвечаем Telegram "ОК"
        return jsonify({'ok': True}), 200
    except Exception as e:
        # Если что-то сломалось, логируем и возвращаем честную ошибку 500
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return 'Internal Server Error', 500

@app.route('/')
def index():
    return 'A-Vision Bot is running!', 200