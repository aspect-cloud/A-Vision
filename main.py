# main.py

import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import commands, media
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

# --- Настройки ---
# Путь, который будет слушать наше приложение
WEBHOOK_PATH = "/webhook"
# Секретный токен для проверки, что запросы приходят от Telegram
WEBHOOK_SECRET = "a_vision_super_secret"


# --- Основная логика ---

# Функция, которая будет вызвана при старте приложения
async def on_startup(bot: Bot):
    # Устанавливаем вебхук
    # VERCEL_URL - переменная, которую Vercel предоставляет автоматически
    webhook_url = f"https://{os.environ.get('VERCEL_URL')}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url, secret_token=WEBHOOK_SECRET)
    logging.info(f"Webhook has been set to {webhook_url}")

# Функция-обработчик для входящих апдейтов от Telegram
async def webhook_handler(request):
    # Проверяем секретный токен
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=403)
    
    # Получаем и обрабатываем апдейт
    update_data = await request.json()
    update = types.Update(**update_data)
    
    # Получаем объекты bot и dp из контекста приложения
    bot = request.app["bot"]
    dp = request.app["dp"]
    
    await dp.feed_update(bot=bot, update=update)
    
    return web.Response()

# Функция-обработчик для GET запросов (чтобы Vercel не падал с ошибкой 500)
async def health_check(request):
    return web.Response(text="Bot is running!")

# --- Инициализация приложения ---

# Создаем объекты Bot и Dispatcher один раз
bot_instance = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp_instance = Dispatcher()

# Регистрируем роутеры
dp_instance.include_router(commands.router)
dp_instance.include_router(media.router)

# Регистрируем функцию, которая выполнится при старте
dp_instance.startup.register(on_startup)

# Создаем веб-приложение
app = web.Application()
# Сохраняем bot и dp в контексте приложения, чтобы иметь к ним доступ в хендлерах
app["bot"] = bot_instance
app["dp"] = dp_instance

# Регистрируем наши обработчики для разных путей и методов
app.router.add_post(WEBHOOK_PATH, webhook_handler)
app.router.add_get("/", health_check) # Отвечает на запросы к корню сайта