import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, Message, BotCommand
from aiogram.enums import ChatMemberStatus, ParseMode
from config import BOT_USERNAME, GROUP_WELCOME_MESSAGE
from utils.logger import logger

router = Router()

active_chats = set()

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Активировать бота"),
        BotCommand(command="help", description="Показать справку"),
        BotCommand(command="stop", description="Деактивировать бота")
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота настроены")

@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    active_chats.add(chat_id)
    
    logger.info(f"Пользователь {user_id} активировал бота в чате {chat_id}")
    
    welcome_text = [
        f"Привет, {message.from_user.full_name}! 👋",
        f"Я - {BOT_USERNAME}, бот для описания медиа.",
        "",
        "📋 **Доступные команды:**",
        "/start - активировать бота в этом чате",
        "/help - показать подробную справку", 
        "/stop - деактивировать бота в этом чате",
        "",
        "📸 **Как использовать:**",
        "1. Отправьте мне фото, видео или голосовое сообщение",
        "2. Я опишу содержимое файла или сделаю транскрипцию",
        "",
        "💡 Используйте /help для получения подробной информации!"
    ]
    
    await message.answer("\n".join(welcome_text), parse_mode=ParseMode.MARKDOWN)

@router.message(Command(commands=["stop"]))
async def send_goodbye(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    active_chats.discard(chat_id)
    
    logger.info(f"Пользователь {user_id} деактивировал бота в чате {chat_id}")
    
    goodbye_text = [
        "🛑 **A-Vision деактивирован**",
        "",
        "Бот больше не будет обрабатывать медиа в этом чате.",
        "",
        "💡 Чтобы активировать снова, используйте команду /start"
    ]
    
    await message.answer("\n".join(goodbye_text), parse_mode=ParseMode.MARKDOWN)

@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    try:
        help_text = [
            f"🤖 {BOT_USERNAME} - бот для описания медиа",
            "\nДоступные команды:",
            "/start - активировать бота в этом чате",
            "/stop - деактивировать бота в этом чате",
            "/help - показать это сообщение",
            "Для использования в группе нужно добавить бота и **выдать права администратора.**"
            "\nКак использовать:",
            "1. Активируй бота с помощью команды /start",
            "2. Отправь любой медиа-файл (фото, видео, голосовое сообщение)",
            "3. Бот опишет содержимое файла, либо сделает транскрипцию, если голосовое сообщение.\n\n",
            "[Its mine, but it can be yours](https://github.com/aspect-cloud/a_vision)"
        ]
        
        await message.answer("\n".join(help_text), parse_mode=ParseMode.MARKDOWN)
        
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

def is_chat_active(chat_id: int) -> bool:
    return chat_id in active_chats