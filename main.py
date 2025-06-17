# main.py

import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Импорты теперь должны быть такими, так как main.py в корне
from handlers import commands, media
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

# Устанавливаем простой путь, который будет слушать наше приложение
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "a_vision_super_secret"

# Создаем главный объект приложения, который найдет Vercel
app = web.Application()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def process_update(request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=403)
    
    update = types.Update(**(await request.json()))
    await dp.feed_update(bot=bot, update=update)
    
    return web.Response()

async def on_startup(app_instance):
    dp.include_router(commands.router)
    dp.include_router(media.router)

    # VERCEL_URL - переменная окружения, которую предоставляет Vercel
    webhook_url = f"https://{os.environ.get('VERCEL_URL')}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url, secret_token=WEBHOOK_SECRET)

# Регистрируем наш простой путь /webhook
app.router.add_post(WEBHOOK_PATH, process_update)
app.on_startup.append(on_startup)