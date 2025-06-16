import asyncio
import logging
from typing import List

import aiohttp
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, SafetySetting, Part, Blob

from config import GEMINI_API_KEY, GEMINI_MODEL, MEDIA_PROMPT, VOICE_PROMPT, MAX_RETRIES

class GeminiService:
    _is_configured = False

    def __init__(self):
        self.retry_delay = 1
        self.max_retries = MAX_RETRIES
        self._model = None

    def _ensure_configured(self):
        # Use a class-level flag to ensure configure is only called once.
        if not GeminiService._is_configured:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured.")
            genai.configure(api_key=GEMINI_API_KEY)
            GeminiService._is_configured = True
    
    @property
    def model(self):
        """Lazily initializes and returns the GenerativeModel instance."""
        self._ensure_configured()
        if self._model is None:
            safety_settings = [
                SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_NONE'),
                SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_NONE'),
                SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_NONE'),
                SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_NONE'),
            ]
            self._model = genai.GenerativeModel(GEMINI_MODEL, safety_settings=safety_settings)
        return self._model

    async def _download_file(self, file_url: str) -> bytes:
        """Downloads a file from a URL."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(file_url) as response:
                    response.raise_for_status()
                    return await response.read()
            except Exception as e:
                logging.error(f"Error downloading file {file_url}: {e}")
                raise

    async def describe_media(self, files: List[dict]) -> str:
        """Generates a description for a list of media files using the Gemini model."""
        for attempt in range(self.max_retries):
            try:
                # Determine the correct prompt based on the file type and count
                file_type = files[0]['type'] if files else None
                if file_type == 'voice':
                    prompt = VOICE_PROMPT
                elif len(files) > 1:
                    prompt = f"{MEDIA_PROMPT}\n\nНиже {len(files)} медиафайлов. Опиши их все вместе в одном ответе."
                else:
                    prompt = MEDIA_PROMPT
                
                # Download all files concurrently
                download_tasks = [self._download_file(file_info['url']) for file_info in files]
                file_datas = await asyncio.gather(*download_tasks)
                
                # Prepare parts for the model
                media_parts = []
                for i, file_info in enumerate(files):
                    mime_type = {
                        'photo': 'image/jpeg',
                        'video': 'video/mp4',
                        'voice': 'audio/ogg',
                    }.get(file_info['type'], 'application/octet-stream')
                    media_parts.append(Part(inline_data=Blob(data=file_datas[i], mime_type=mime_type)))
                
                contents = [prompt] + media_parts

                generation_config = GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                )
                
                # Generate content using the modern async API
                response = await self.model.generate_content_async(
                    contents=contents,
                    generation_config=generation_config
                )
                
                return response.text or ""

            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to get description after {self.max_retries} attempts: {e}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        return ""

# Global service instance
gemini_service = GeminiService()