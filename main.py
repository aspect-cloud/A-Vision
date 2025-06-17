import os
import traceback
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- Конфигурация ---
# Импортируем конфиг и хендлеры
try:
    from config import BOT_TOKEN
    from handlers import commands, media
except ImportError as e:
    raise ImportError(f"Не удалось импортировать модули. Проверь __init__.py и структуру проекта. Ошибка: {e}")

# --- Инициализация ---
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(commands.router)
dp.include_router(media.router)

WEBHOOK_PATH = f'/{BOT_TOKEN}'

# --- ГЛАВНАЯ ЛОГИКА С ОТЛОВЩИКОМ ОШИБОК ---
@app.route(WEBHOOK_PATH, methods=['POST'])
async def process_webhook():
    try:
        # Получаем и обрабатываем обновление от Telegram
        update_data = request.json
        update = types.Update(**update_data)
        await dp.feed_update(bot=bot, update=update)
        
        # Если все хорошо, отвечаем Telegram "ОК"
        return jsonify({'ok': True}), 200

    except Exception as e:
        # ЕСЛИ ЧТО-ТО СЛОМАЛОСЬ - ЛОВИМ ОШИБКУ
        
        # Получаем полный текст ошибки (Traceback)
        error_text = f"СЛУЧИЛАСЬ ОШИБКА:\n\n<pre>{traceback.format_exc()}</pre>"
        app.logger.error(error_text) # Логируем ошибку для Vercel

        # Пытаемся отправить сообщение с ошибкой пользователю, который ее вызвал
        try:
            chat_id = request.json['message']['chat']['id']
            await bot.send_message(chat_id, error_text)
        except Exception as send_error:
            app.logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

        # Отвечаем Telegram "ОК", чтобы он не пытался отправить обновление снова
        return jsonify({'ok': False, 'error': str(e)}), 200

@app.route('/')
def index():
    return 'A-Vision Bot is running!', 200