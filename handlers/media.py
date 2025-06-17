import asyncio
import logging
from typing import List
from aiogram import F, Router
from aiogram.types import Message
from config import RESPONSE_TEMPLATE, SUPPORTED_MEDIA_MESSAGE
from services.gemini import gemini_service

router = Router()
logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

async def send_long_message(message: Message, text: str):
    if len(text) <= TELEGRAM_MAX_MESSAGE_LENGTH:
        await message.reply(text)
        return

    parts = []
    while len(text) > 0:
        if len(text) > TELEGRAM_MAX_MESSAGE_LENGTH:
            split_pos = text.rfind('\n', 0, TELEGRAM_MAX_MESSAGE_LENGTH)
            if split_pos == -1:
                split_pos = text.rfind(' ', 0, TELEGRAM_MAX_MESSAGE_LENGTH)
            if split_pos == -1:
                split_pos = TELEGRAM_MAX_MESSAGE_LENGTH
            
            parts.append(text[:split_pos])
            text = text[split_pos:].lstrip()
        else:
            parts.append(text)
            break
    
    for part in parts:
        await message.reply(part)
        await asyncio.sleep(0.5)

async def get_file_url(bot, file_id: str) -> str:
    try:
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
        return file_url
    except Exception as e:
        logger.error(f"Error getting file URL for {file_id}: {str(e)}")
        raise

async def process_description(message: Message, files: List[dict]):
    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        description = await gemini_service.describe_media(files)

        if not description:
            await message.reply("Не удалось получить описание для этого медиафайла.")
            return

        await send_long_message(message, RESPONSE_TEMPLATE.format(description))

    except Exception as e:
        logger.error(f"Error generating description: {str(e)}", exc_info=True)
        await message.reply("Извините, произошла ошибка при обработке вашего запроса.")

@router.message(F.photo | F.video | F.voice)
async def handle_any_media(message: Message):
    file_type, file_id = None, None
    if message.photo:
        file_type, file_id = 'photo', max(message.photo, key=lambda p: p.file_size).file_id
    elif message.video:
        file_type, file_id = 'video', message.video.file_id
    elif message.voice:
        file_type, file_id = 'voice', message.voice.file_id

    if file_type and file_id:
        file_url = await get_file_url(message.bot, file_id)
        await process_description(message, [{'url': file_url, 'type': file_type}])

@router.message(F.audio | F.document)
async def handle_unsupported_files(message: Message):
    await message.reply(SUPPORTED_MEDIA_MESSAGE)