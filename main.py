import asyncio
import logging
import os
import sys

from aiogram import Bot

from config import BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_webhook(bot: Bot, webhook_url: str):
    await bot.set_webhook(webhook_url)
    logger.info(f'Webhook set to {webhook_url}')

async def delete_webhook(bot: Bot):
    await bot.delete_webhook()
    logger.info('Webhook deleted')

async def main():
    bot = Bot(token=BOT_TOKEN)

    if len(sys.argv) < 2:
        print('Usage: python main.py <set|delete> [webhook_url]')
        return

    command = sys.argv[1]

    if command == 'set':
        if len(sys.argv) < 3:
            print('Usage: python main.py set <webhook_url>')
            return
        webhook_url = sys.argv[2]
        await set_webhook(bot, webhook_url)
    elif command == 'delete':
        await delete_webhook(bot)
    else:
        print(f'Unknown command: {command}')

    await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())