import asyncio
import os
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- Конфигурация ---
# Импортируем конфиг и хендлеры
# Убедись, что config.py теперь лежит в корне проекта!
try:
    from config import BOT_TOKEN
    from handlers import commands, media
except ImportError as e:
    # Эта ошибка поможет при отладке, если структура папок неверна
    raise ImportError(f"Не удалось импортировать модули. Проверь структуру проекта. Ошибка: {e}")

# --- Инициализация ---
# Создаем Flask-приложение, которое ищет Vercel
app = Flask(__name__)

# Инициализация бота и диспетчера Aiogram
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключаем роутеры из папки handlers
dp.include_router(commands.router)
dp.include_router(media.router)

# Секретный путь для вебхука, чтобы его не нашли случайные люди
WEBHOOK_PATH = f'/{BOT_TOKEN}'

# --- Логика Вебхука ---
# Этот роут будет принимать обновления от Telegram
@app.route(WEBHOOK_PATH, methods=['POST'])
async def process_webhook():
    if request.method == 'POST':
        try:
            # Получаем обновление от Telegram
            update_data = request.json
            update = types.Update(**update_data)
            
            # Передаем обновление в диспетчер Aiogram для обработки
            await dp.feed_update(bot=bot, update=update)
            
            return jsonify({'ok': True}), 200
        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            app.logger.error(f"Error processing update: {e}")
            return jsonify({'ok': False, 'error': str(e)}), 500
    else:
        return 'Method Not Allowed', 405

# Этот роут нужен для проверки, что бот жив
@app.route('/')
def index():
    return 'A-Vision Bot is running!', 200

# Важно! Код ниже НЕ нужен для Vercel. 
# Webhook устанавливается ОДИН РАЗ вручную.
# async def on_startup(bot: Bot):
#     await bot.set_webhook(f"https://{VERCEL_URL}{WEBHOOK_PATH}")
#
# dp.startup.register(on_startup)