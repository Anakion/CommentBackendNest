import secrets
import string
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from src.models.captcha import Captcha
from src.repositories.captcha import CaptchaRepository


@dataclass
class CaptchaService:
    captcha_repo: CaptchaRepository

    async def generate_captcha(self) -> Captcha:
        """Генерирует новую CAPTCHA с текстом"""
        from src.services.captcha_generator import captcha_generator

        # Генерируем текст
        captcha_text = captcha_generator.generate_text(6)

        # Создаем запись в БД
        captcha = Captcha(text=captcha_text)
        return await self.captcha_repo.create(captcha)

    async def get_captcha_image(self, captcha_id: int) -> Optional[BytesIO]:
        """Генерирует изображение CAPTCHA по ID"""
        from src.services.captcha_generator import captcha_generator

        # Получаем CAPTCHA из БД
        captcha = await self.captcha_repo.get_by_id(captcha_id)
        if not captcha:
            return None

        # Генерируем изображение
        return captcha_generator.generate_captcha_image(captcha.text)

    async def validate_captcha(self, captcha_id: int, text: str) -> bool:
        captcha = await self.captcha_repo.get_valid_captcha(captcha_id, text)
        if captcha:
            await self.captcha_repo.mark_as_used(captcha_id)
            return True
        return False