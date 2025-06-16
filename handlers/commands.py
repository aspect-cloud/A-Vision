import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, Message
from aiogram.enums import ChatMemberStatus
from config import BOT_USERNAME, GROUP_WELCOME_MESSAGE
from utils.logger import logger

router = Router()

@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота в чате {message.chat.id}")
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я - A-Vision, бот для описания медиа. Просто отправьте мне фото, видео или голосовое сообщение."
    )

@router.message(Command(commands=["stop"]))
async def send_goodbye(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь - {user_id} остановил бота в чате {message.chat.id}")
    await message.answer(
        "Бот будет остановлен в этом чате. Чтобы запустить снова, используйте /start."
    )

@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    try:
        help_text = [
            f"🤖 {BOT_USERNAME} - бот для помощи людям с нарушениями зрения",
            "\nДоступные команды:",
            "/start - активировать бота",
            "/stop - деактивировать бота",
            "/help - показать это сообщение",
            "\nКак использовать:",
            "1. Активируйте бота с помощью команды /start",
            "2. Отправьте любой медиа-файл (фото, видео)",
            "3. Бот опишет содержимое файла"
        ]
        
        await message.answer("\n".join(help_text))
        
        logger.info(f"Помощь запрошена в чате {message.chat.id} пользователем {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения помощи в чате {message.chat.id}: {e}")
        await message.answer("Произошла ошибка при отправке помощи. Пожалуйста, попробуйте снова позже.")

@router.my_chat_member()
async def on_bot_promote(event: ChatMemberUpdated, bot: Bot):
    logger.info(
        f"Статус бота изменен в чате {event.chat.id}. "
        f"Старый статус: {event.old_chat_member.status.value}, "
        f"Новый статус: {event.new_chat_member.status.value}"
    )

    if event.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR and event.new_chat_member.user.id == bot.id:
        try:
            await bot.send_message(event.chat.id, GROUP_WELCOME_MESSAGE, parse_mode="Markdown")
            logger.info(f"Бот повышен до администратора в чате {event.chat.id}")
        except Exception as e:
            logger.error(f"Ошибка при повышении бота до администратора в чате {event.chat.id}: {e}")