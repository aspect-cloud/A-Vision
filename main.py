import os
import traceback
import asyncio
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

try:
    from config import BOT_TOKEN
    from handlers import commands, media
except ImportError as e:
    raise ImportError(f"Не удалось импортировать модули. Проверь __init__.py и структуру проекта. Ошибка: {e}")

dp = Dispatcher()
dp.include_router(commands.router)
dp.include_router(media.router)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
async def process_webhook():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        update = types.Update(**request.json)
        await dp.feed_update(bot=bot, update=update)
        return jsonify({'ok': True}), 200
    except Exception as e:
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return 'Internal Server Error', 500
    finally:
        await bot.session.close()

@app.route('/')
def index():
    return 'A-Vision Bot is running!', 200

async def set_bot_commands():
    bot = Bot(token=BOT_TOKEN)
    bot_commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="❓ Помощь по использованию"),
        BotCommand(command="stop", description="⛔ Остановить бота в чате"),
    ]
    try:
        await bot.set_my_commands(bot_commands)
    finally:
        await bot.session.close()

if os.environ.get('VERCEL'):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_bot_commands())
        loop.close()
    except Exception as e:
        print(f"An error occurred during command setup: {e}")