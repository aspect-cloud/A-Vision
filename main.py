import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.media import router as media_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Dispatcher setup
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(commands_router)
dp.include_router(media_router)

# This is the webhook path that Telegram will send updates to.
# It's important to use the bot token in the path to ensure it's secret.
WEBHOOK_PATH = f'/{BOT_TOKEN}'

async def webhook(request: web.Request):
    """
    This endpoint processes incoming updates from Telegram.
    """
    logger.info("Webhook received a request.")
    if request.content_type == 'application/json':
        try:
            json_string = await request.text()
            logger.info(f"Update from Telegram: {json_string}")
            update = types.Update.model_validate_json(json_string)
            await dp.feed_update(bot, update)
            logger.info("Update processed successfully by dispatcher.")
            return web.Response(status=200)
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return web.Response(status=500)
    else:
        logger.warning(f"Request aborted. Content-Type: {request.content_type}")
        return web.Response(status=403)

async def index(request: web.Request):
    """
    A simple endpoint to confirm the app is running.
    """
    return web.Response(text='A-Vision is alive!')

# aiohttp app setup
app = web.Application()
app.router.add_post(WEBHOOK_PATH, webhook)
app.router.add_get('/', index)