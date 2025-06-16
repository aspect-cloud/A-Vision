import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не найдена переменная окружения BOT_TOKEN")

BOT_USERNAME = "A-Vision"

# The google-genai library automatically looks for the GOOGLE_API_KEY environment variable.
# Make sure it is set in your .env file or in your Vercel project settings.

VERCEL_URL = os.getenv("VERCEL_URL")
if not VERCEL_URL:
    raise ValueError("The VERCEL_URL environment variable was not found. This is set automatically by Vercel.")


GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 20))

START_MESSAGE = """
Привет, {full_name}!
Я A-Vision, предназначен для описания фото, видео и транскрипции голосовых сообщений.

Просто отправьте мне любое медиа, и я опишу его содержание.

---

[open-source](https://github.com/qzbx-cloud/a-vision)
"""

HELP_MESSAGE = """
Чтобы получить описание медиа, просто отправь его в этот чат или добавь меня в группу.
Чтобы я мог отвечать в группе - сделай меня администратором

/start - начну описывать медиа.
/stop - перестану описывать медиа в этом чатею
/help - этот текст.

Я не храню твои запросы
[open-source](https://github.com/qzbx-cloud/a-vision)
"""

GROUP_WELCOME_MESSAGE = """
Теперь я могу описывать медиа здесь!

Чтобы использовать меня, просто отправь медиа в этот чат.
"""

RESPONSE_TEMPLATE = "{}"

MEDIA_PROMPT = """Опиши это изображение/видео для человека с нарушением зрения. Будь максимально точен, простой и дружелюбный. Укажи:
- Кто или что изображено;
- Где это расположено;
- Какого цвета и формы предметы;
- Что написано на фото, если есть текст.
Твой ответ не должен содержать элементы форматирования текста.
Твой ответ - описание, никаких технических деталей
"""

VOICE_PROMPT = "Твоя задача — дословно транскрибировать это голосовое сообщение. Ответ должен содержать только текст из сообщения, без каких-либо дополнительных фраз или форматирования."

SUPPORTED_MEDIA_MESSAGE = "Я могу обрабатывать только фото, видео и голосовые сообщения. Пожалуйста, отправьте медиа поддерживаемого формата."