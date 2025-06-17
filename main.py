import logging
import os
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, Response

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.fastapi import SimpleRequestHandler

from config import BOT_TOKEN, VERCEL_URL
from handlers.commands import router as commands_router
from handlers.media import router as media_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Bot and Dispatcher Setup ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_routers(commands_router, media_router)

# --- Web App Setup (using FastAPI) ---
app = FastAPI()

# Create a request handler for the bot
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
)

# Register the webhook handler to listen on the bot token path
webhook_requests_handler.register(app, path=f'/{BOT_TOKEN}')

@app.on_event("startup")
async def on_startup():
    """Sets the webhook on application startup."""
    webhook_url = f"https://{VERCEL_URL}/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logger.info(f"Webhook set to {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    """Deletes the webhook on application shutdown."""
    await bot.delete_webhook()
    logger.info("Webhook deleted")

# Add handlers for GET requests
@app.get("/")
async def root():
    return PlainTextResponse("A-Vision Bot is running!")

@app.get("/favicon.ico")
@app.get("/favicon.png")
async def favicon():
    return Response(status_code=204)

# Expose the application for Vercel
application = app