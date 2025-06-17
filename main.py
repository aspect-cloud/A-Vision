import os
import traceback
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- Конфигурация и глобальная инициализация ---
try:
    from config import BOT_TOKEN
    from handlers import commands, media
except ImportError as e:
    raise ImportError(f"Не удалось импортировать модули. Проверь __init__.py и структуру проекта. Ошибка: {e}")

# Создаем Dispatcher и подключаем роутеры ОДИН РАЗ
dp = Dispatcher()
dp.include_router(commands.router)
dp.include_router(media.router)

# Создаем Flask приложение
app = Flask(__name__)

# Функция для настройки команд бота при запуске
async def setup_bot():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await commands.setup_bot_commands(bot)
        print("✅ Команды бота успешно настроены")
    except Exception as e:
        print(f"❌ Ошибка настройки команд бота: {e}")
    finally:
        await bot.session.close()

# Настраиваем команды при запуске приложения
@app.before_first_request
def before_first_request():
    import asyncio
    asyncio.run(setup_bot())

# --- Логика Вебхука ---
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def process_webhook():
    # Создаем объект Bot при каждом вызове, чтобы получить свежую сессию
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        # Передаем обновление в наш глобальный диспетчер
        update = types.Update(**request.json)
        await dp.feed_update(bot=bot, update=update)
        return jsonify({'ok': True}), 200
    except Exception as e:
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return 'Internal Server Error', 500
    finally:
        # ВАЖНО: Закрываем сессию бота после обработки запроса
        await bot.session.close()

# Этот роут для проверки, что сервер жив
@app.route('/')
def index():
    return 'A-Vision Bot is running!', 200