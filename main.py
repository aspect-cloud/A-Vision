import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

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

# --- Web App Setup (using official aiogram helpers) ---
async def on_startup(bot: Bot):
    """Sets the webhook on application startup."""
    webhook_url = f"https://{VERCEL_URL}/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logger.info(f"Webhook set to {webhook_url}")

async def on_shutdown(bot: Bot):
    """Deletes the webhook on application shutdown."""
    await bot.delete_webhook()
    logger.info("Webhook deleted")

# Register startup and shutdown handlers
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# Create the aiohttp application
app = web.Application()

# Create a request handler for the bot
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
)

# Register the webhook handler to listen on the bot token path
webhook_requests_handler.register(app, path=f'/{BOT_TOKEN}')

# Mount the dispatcher to the application to handle startup and shutdown
setup_application(app, dp, bot=bot)

# Add a simple root handler for health checks
async def home(request: web.Request):
    return web.Response(text="A-Vision Bot is running!")

app.router.add_get('/', home)