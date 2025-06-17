import logging
import os
from typing import Optional
from aiohttp import web
from aiohttp.web import Request, Response

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A-Vision")

try:
    from config import BOT_TOKEN, VERCEL_URL
    logger.info(f"Config loaded: BOT_TOKEN={bool(BOT_TOKEN)}, VERCEL_URL={VERCEL_URL}")
except Exception as e:
    logger.error(f"Failed to load config: {str(e)}", exc_info=True)
    raise

from handlers.commands import router as commands_router
from handlers.media import router as media_router

# --- Bot and Dispatcher Setup ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_routers(commands_router, media_router)

# --- Web App Setup (using aiohttp) ---
app = web.Application()

# Create a request handler for the bot
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
)

# Register the webhook handler to listen on the bot token path
webhook_path = f'/webhook/{BOT_TOKEN}'
webhook_requests_handler.register(app, path=webhook_path)

# Add static file handling for favicon
app.router.add_static('/static/', path=os.path.join(os.path.dirname(__file__), 'static'))

# Add handlers for GET requests
async def on_startup():
    """Sets the webhook on application startup."""
    webhook_path = f'/webhook/{BOT_TOKEN}'
    webhook_url = f"https://{VERCEL_URL}{webhook_path}"
    try:
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        logger.info(f"Webhook set successfully to {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {str(e)}", exc_info=True)
        raise

async def on_shutdown():
    """Deletes the webhook on application shutdown."""
    await bot.delete_webhook()
    logger.info("Webhook deleted")

# Register startup and shutdown handlers
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# Add handlers for GET requests
async def handle_get(request: Request) -> Response:
    """Handle GET requests to the root."""
    try:
        path = request.path
        
        if path == '/':
            return web.Response(text="A-Vision Bot is running!", content_type="text/plain")
        else:
            return web.Response(status=404, text="Not Found")
    except Exception as e:
        logger.error(f"Error handling GET request {path}: {str(e)}", exc_info=True)
        raise

# Add routes for GET requests
app.router.add_get('/', handle_get)
app.router.add_get('/favicon.ico', handle_get)
app.router.add_get('/favicon.png', handle_get)

# Expose the application for Vercel
app = app