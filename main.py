import logging
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.executor import start_webhook

# Configure logging
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

# Bot and Dispatcher Setup
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_routers(commands_router, media_router)

# Webhook Setup
webhook_path = f'/webhook/{BOT_TOKEN}'
webhook_url = f"https://{VERCEL_URL}{webhook_path}"

# Set webhook on startup
async def on_startup():
    try:
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        logger.info(f"Webhook set successfully to {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {str(e)}", exc_info=True)
        raise

async def on_shutdown():
    await bot.delete_webhook()
    logger.info("Webhook deleted")

# Register startup and shutdown handlers
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        try:
            parsed_path = urlparse(self.path)
            if parsed_path.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"A-Vision Bot is running!")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Not Found")
        except Exception as e:
            logger.error(f"Error handling GET request {self.path}: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

    def do_POST(self):
        """Handle POST requests for webhook."""
        try:
            if self.path == webhook_path:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                dp.feed_webhook_update(bot, post_data)
                self.send_response(200)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"Error handling POST request {self.path}: {str(e)}", exc_info=True)
            self.send_response(500)
            self.end_headers()

def handler(event, context):
    """Vercel handler."""
    # Create a new instance of the handler for each request
    handler = RequestHandler()
    handler.setup(event, context)
    return handler

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=webhook_path,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=8080,
    )