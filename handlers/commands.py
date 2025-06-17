import logging
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ChatMemberUpdated
from aiogram.enums import ChatMemberStatus, ParseMode
from config import BOT_USERNAME, GROUP_WELCOME_MESSAGE
from utils.logger import logger

router = Router()

kb = [
    [KeyboardButton(text="❓ Помощь")],
]
main_keyboard = ReplyKeyboardMarkup(
    keyboard=kb, 
    resize_keyboard=True, 
    input_field_placeholder="Отправьте медиа или выберите команду..."
)

@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота в чате {message.chat.id}")
    
    welcome_text = [
        f"Привет, {message.from_user.full_name}! 👋",
        f"Я - {BOT_USERNAME}, бот для описания медиа.",
        "",
        "📸 Просто отправьте мне фото, видео или голосовое сообщение, и я его обработаю.",
    ]
    
    await message.answer("\n".join(welcome_text), reply_markup=main_keyboard)

@router.message(Command(commands=["stop"]))
async def send_goodbye(message: Message):
    logger.info(f"Пользователь {message.from_user.id} деактивировал бота в чате {message.chat.id}")
    goodbye_text = "Клавиатура убрана. Бот всегда готов к работе, просто отправьте медиа."
    await message.answer(goodbye_text, reply_markup=types.ReplyKeyboardRemove())

@router.message(F.text == "❓ Помощь")
async def show_help_from_button(message: types.Message):
    await cmd_help(message)

@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    help_text = [
        f"🤖 **{BOT_USERNAME}** - бот для помощи незрячим.",
        "",
        "**Как использовать:**",
        "1. Отправьте любой медиа-файл (фото, видео, голосовое).",
        "2. Я опишу содержимое или сделаю транскрипцию.",
        "",
        "**Команды:**",
        "/start - Показать приветствие и клавиатуру.",
        "/stop - Скрыть клавиатуру и перестать отвечать.",
        "/help - Показать это сообщение.",
        "",
        "Для работы в группе, добавьте меня и дайте права администратора.",
        "",
        "[Исходный код на GitHub](https://github.com/aspect-cloud/a_vision)"
    ]
        
    await message.answer("\n".join(help_text), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    logger.info(f"Помощь запрошена в чате {message.chat.id} пользователем {message.from_user.id}")

@router.my_chat_member()
async def on_bot_promote(event: ChatMemberUpdated, bot: types.Bot):
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