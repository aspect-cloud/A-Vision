import asyncio
import logging
from collections import defaultdict
from typing import Dict, List

from aiogram import F, Router
from aiogram.types import Message

from config import RESPONSE_TEMPLATE, SUPPORTED_MEDIA_MESSAGE
from services.gemini import gemini_service
from handlers import is_chat_active

router = Router()
logger = logging.getLogger(__name__)

media_groups: Dict[str, List[Message]] = defaultdict(list)
media_group_timers: Dict[str, asyncio.TimerHandle] = {}

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
        logger.info(f"Got file URL for file_id {file_id}: {file_url}")
        return file_url
    except Exception as e:
        logger.error(f"Error getting file URL for {file_id}: {str(e)}")
        raise

async def process_description(message: Message, files: List[dict]):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        logger.info("Sending request to Gemini AI for description/transcription...")
        description = await gemini_service.describe_media(files)
        logger.info("Received response from Gemini AI")

        if not description:
            logger.warning("Received empty description from Gemini AI.")
            await message.reply("Не удалось получить описание для этого медиафайла.")
            return

        await send_long_message(message, RESPONSE_TEMPLATE.format(description))
        logger.info(f"Text description successfully sent to user {user_id} in chat {chat_id}")

    except Exception as e:
        logger.error(f"Error generating description: {str(e)}", exc_info=True)
        await message.reply(
            "Извините, произошла ошибка при обработке вашего запроса. "
            "Пожалуйста, попробуйте еще раз позже."
        )

async def process_media_group_wrapper(group_id: str, chat_id: int, user_id: int, bot):
    if not is_chat_active(chat_id):
        logger.info(f"Бот неактивен в чате {chat_id}, игнорируем обработку медиа-группы")
        if group_id in media_groups:
            media_groups.pop(group_id)
        if group_id in media_group_timers:
            media_group_timers.pop(group_id)
        return

    if group_id in media_groups:
        messages_to_process = media_groups.pop(group_id)
        messages_to_process.sort(key=lambda m: m.message_id)
        
        files_to_process = []
        for msg in messages_to_process:
            file_type, file_id = None, None
            if msg.photo:
                file_type, file_id = 'photo', max(msg.photo, key=lambda p: p.file_size).file_id
            elif msg.video:
                file_type, file_id = 'video', msg.video.file_id
            
            if file_type and file_id:
                file_url = await get_file_url(bot, file_id)
                files_to_process.append({'url': file_url, 'type': file_type})

        if files_to_process:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await process_description(messages_to_process[0], files_to_process)
        else:
            logger.warning("No files found to process in the media group.")

    if group_id in media_group_timers:
        media_group_timers.pop(group_id)

@router.message(F.media_group_id)
async def handle_media_group(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_chat_active(chat_id):
        logger.info(f"Бот неактивен в чате {chat_id}, игнорируем медиа-группу")
        return

    group_id = str(message.media_group_id)
    media_groups[group_id].append(message)

    if group_id in media_group_timers:
        media_group_timers[group_id].cancel()
    loop = asyncio.get_running_loop()
    media_group_timers[group_id] = loop.call_later(
        1.5, 
        lambda: asyncio.create_task(process_media_group_wrapper(group_id, message.chat.id, user_id, message.bot))
    )

@router.message(F.photo | F.video | F.voice)
async def handle_single_media(message: Message):
    if message.media_group_id:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_chat_active(chat_id):
        logger.info(f"Бот неактивен в чате {chat_id}, игнорируем медиа-сообщение")
        return

    file_type, file_id = None, None
    if message.photo:
        file_type, file_id = 'photo', max(message.photo, key=lambda p: p.file_size).file_id
    elif message.video:
        file_type, file_id = 'video', message.video.file_id
    elif message.voice:
        file_type, file_id = 'voice', message.voice.file_id


    if file_type and file_id:
        action = "upload_audio" if file_type == 'voice' else "typing"
        await message.bot.send_chat_action(chat_id=message.chat.id, action=action)
        file_url = await get_file_url(message.bot, file_id)
        await process_description(message, [{'url': file_url, 'type': file_type}])

@router.message(F.audio | F.document)
async def handle_unsupported_files(message: Message):
    await message.reply(SUPPORTED_MEDIA_MESSAGE)