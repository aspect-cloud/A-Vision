import asyncio
import logging
from typing import List

import aiohttp
from google import genai
from google.genai import types

from config import GEMINI_MODEL, MEDIA_PROMPT, VOICE_PROMPT, MAX_RETRIES

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.client = genai.Client()
        self.retry_delay = 1

    async def _download_file(self, file_url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(file_url) as response:
                    response.raise_for_status()
                    return await response.read()
            except Exception as e:
                logger.error(f"Error downloading file {file_url}: {e}")
                raise

    async def describe_media(self, files: List[dict]) -> str:
        for attempt in range(MAX_RETRIES):
            try:
                file_type = files[0]['type'] if files else None
                if file_type == 'voice':
                    prompt = VOICE_PROMPT
                elif len(files) > 1:
                    prompt = f"{MEDIA_PROMPT}\n\nНиже {len(files)} медиафайлов. Опиши их все вместе в одном ответе."
                else:
                    prompt = MEDIA_PROMPT

                download_tasks = [self._download_file(file_info['url']) for file_info in files]
                file_datas = await asyncio.gather(*download_tasks)

                media_parts = []
                for i, file_info in enumerate(files):
                    mime_type = {
                        'photo': 'image/jpeg',
                        'video': 'video/mp4',
                        'voice': 'audio/ogg',
                    }.get(file_info['type'], 'application/octet-stream')
                    media_parts.append(types.Part(inline_data=types.Blob(data=file_datas[i], mime_type=mime_type)))

                contents = [prompt] + media_parts

                config = types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    safety_settings=[
                        types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_NONE'),
                        types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_NONE'),
                        types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_NONE'),
                        types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_NONE'),
                    ]
                )

                response = await self.client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=config
                )

                return response.text

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Failed to get description after {MAX_RETRIES} attempts: {e}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        return ""

gemini_service = GeminiService()