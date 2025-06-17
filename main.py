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

dp = Dispatcher()
dp.include_router(commands.router)
dp.include_router(media.router)

app = Flask(__name__)


@app.route("/")
def index():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    try:
        asyncio.run(process_update(request.get_json()))
        return jsonify(ok=True)
    except Exception as e:
        logging.error(f"Error in webhook handler: {e}", exc_info=True)
        return jsonify(ok=False, error=str(e)), 500

async def process_update(update_data: dict):
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    update = types.Update(**update_data)
    
    try:
        await dp.feed_update(bot=bot, update=update)
    finally:
        await bot.session.close() 